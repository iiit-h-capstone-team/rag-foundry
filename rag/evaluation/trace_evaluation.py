import json
import re
from rag.evaluation.base import EvaluationStrategy


class TRACeEvaluationStrategy(EvaluationStrategy):

    def __init__(
        self,
        judge_client,
        model: str = "llama-3.3-70b-versatile"
    ):
        self.judge_client = judge_client
        self.model = model

    def split_into_sentences(self, text: str) -> list[str]:
        import nltk
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)

        from nltk.tokenize import sent_tokenize
        sentences = sent_tokenize(text.strip())
        return [s.strip() for s in sentences if len(s.strip()) >= 10]

    def build_doc_sentences(self, retrieved_docs) -> list[list]:
        doc_sentences = []
        for doc_idx, doc in enumerate(retrieved_docs):
            text = doc.get("text") or doc.get("chunk").text
            sentences = self.split_into_sentences(text)
            doc_sent_pairs = []

            for sent_idx, sentence in enumerate(sentences):
                key = f"d{doc_idx}s{sent_idx}"
                doc_sent_pairs.append([key, sentence])

            doc_sentences.append(doc_sent_pairs)
        return doc_sentences

    def build_response_sentences(self, response: str) -> list[list]:
        sentences = self.split_into_sentences(response)
        response_sentences = []
        for idx, sentence in enumerate(sentences):
            letter = chr(ord('a') + idx % 26)
            response_sentences.append([letter, sentence])
        return response_sentences

    def format_doc_sentences(self, doc_sentences) -> str:
        formatted = ""
        for doc in doc_sentences:
            for key, sentence in doc:
                formatted += f"{key}. {sentence}\n"
        return formatted.strip()

    def format_response_sentences(self, resp_sentences) -> str:
        formatted = ""
        for key, sentence in resp_sentences:
            formatted += f"{key}. {sentence}\n"
        return formatted.strip()

    def evaluate(
        self,
        query: str,
        retrieved_docs,
        response: str
    ) -> dict:

        doc_sentences = self.build_doc_sentences(retrieved_docs)
        resp_sentences = self.build_response_sentences(response)

        doc_fmt = self.format_doc_sentences(doc_sentences)
        resp_fmt = self.format_response_sentences(resp_sentences)

        prompt = f"""I asked someone to answer a question based on one or more documents.
Your task is to review their response and assess whether or not each sentence in that response is supported by text in the documents. And if so, which sentences in the documents provide that support. You will also tell me which of the documents contain useful information for answering the question, and which of the documents the answer was sourced from.

Here are the documents, each of which is split into sentences. Alongside each sentence is associated key, such as '0a.' or '0b.' that you can use to refer to it:

'''
{doc_fmt}
'''

The question was:

'''
{query}
'''

Here is their response, split into sentences. Alongside each sentence is associated key, such as 'a.' or 'b.' that you can use to refer to it. Note that these keys are unique to the response, and are not related to the keys in the documents:

'''
{resp_fmt}
'''

You must respond with a JSON object matching this schema:
'''
{{
  "relevance_explanation": "string",
  "all_relevant_sentence_keys": ["string"],
  "overall_supported_explanation": "string",
  "overall_supported": boolean,
  "sentence_support_information": [
    {{
      "response_sentence_key": "string",
      "explanation": "string",
      "supporting_sentence_keys": ["string"],
      "fully_supported": boolean
    }}
  ],
  "all_utilized_sentence_keys": ["string"]
}}
'''

The all_relevant_sentence_keys field: list all document sentence keys relevant to the question (even if unused in the response).
The all_utilized_sentence_keys field: list all document sentence keys actually used to construct the answer.
The overall_supported field: true only if ALL response sentences are fully supported by the documents.

Respond with valid JSON only. No text before or after the JSON."""

        result = self.judge_client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.0
        )

        raw = result.choices[0].message.content.strip()
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        judge_output = json.loads(match.group())

        total_doc_sentences = sum(len(doc) for doc in doc_sentences)
        relevant_keys = set(judge_output.get('all_relevant_sentence_keys', []))
        utilized_keys = set(judge_output.get('all_utilized_sentence_keys', []))
        relevant_utilized = relevant_keys & utilized_keys

        relevance_score = len(relevant_keys) / total_doc_sentences if total_doc_sentences > 0 else 0.0
        utilization_score = len(utilized_keys) / total_doc_sentences if total_doc_sentences > 0 else 0.0
        completeness_score = len(relevant_utilized) / len(relevant_keys) if relevant_keys else 0.0
        adherence_score = bool(judge_output.get('overall_supported', False))

        return {
            'relevance_score': round(relevance_score, 4),
            'utilization_score': round(utilization_score, 4),
            'completeness_score': round(completeness_score, 4),
            'adherence_score': adherence_score,
            'judge_output': judge_output
        }
