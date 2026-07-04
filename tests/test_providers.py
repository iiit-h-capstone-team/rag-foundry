import pytest
from unittest.mock import Mock, patch, MagicMock
from rag.config.config import (
    OllamaEmbeddingConfig,
    CohereEmbeddingConfig,
    VoyageEmbeddingConfig,
    HuggingFaceEmbeddingConfig,
    MedCPTEmbeddingConfig,
    CohereRerankerConfig,
    VoyageRerankerConfig,
    JinaRerankerConfig,
    MixedBreadRerankerConfig,
)
from embedding.strategies.ollama.strategy import OllamaEmbeddingStrategy
from embedding.strategies.cohere.strategy import CohereEmbeddingStrategy
from embedding.strategies.voyage.strategy import VoyageEmbeddingStrategy
from embedding.strategies.huggingface.strategy import HuggingFaceEmbeddingStrategy
from embedding.strategies.medcpt.strategy import MedCPTEmbeddingStrategy
from rag.modules.reranking.strategies.cohere.strategy import CohereRerankerStrategy
from rag.modules.reranking.strategies.voyage.strategy import VoyageRerankerStrategy
from rag.modules.reranking.strategies.jina.strategy import JinaRerankerStrategy
from rag.modules.reranking.strategies.mixedbread.strategy import MixedBreadRerankerStrategy


# =============================================================================
# Ollama Embedding Tests
# =============================================================================

class TestOllamaEmbeddingStrategy:
    
    @patch('embedding.strategies.ollama.strategy.Client')
    def test_initialization(self, mock_client):
        config = OllamaEmbeddingConfig(
            model_name="nomic-embed-text",
            base_url="http://localhost:11434"
        )
        strategy = OllamaEmbeddingStrategy(config)
        assert strategy.config == config
        assert strategy.model == "nomic-embed-text"
    
    @patch('embedding.strategies.ollama.strategy.Client')
    def test_default_model(self, mock_client):
        config = OllamaEmbeddingConfig()
        strategy = OllamaEmbeddingStrategy(config)
        assert strategy.model == "nomic-embed-text"
    
    @patch('embedding.strategies.ollama.strategy.Client')
    def test_embed_single_text(self, mock_client_class):
        mock_client = Mock()
        mock_client.embed.return_value = {"embeddings": [[0.1, 0.2, 0.3]]}
        mock_client_class.return_value = mock_client
        
        config = OllamaEmbeddingConfig(model_name="nomic-embed-text")
        strategy = OllamaEmbeddingStrategy(config)
        result = strategy.embed("test text")
        
        mock_client.embed.assert_called_once_with(
            model="nomic-embed-text",
            input=["test text"]
        )
        assert result == [[0.1, 0.2, 0.3]]
    
    @patch('embedding.strategies.ollama.strategy.Client')
    def test_embed_multiple_texts(self, mock_client_class):
        mock_client = Mock()
        mock_client.embed.return_value = {"embeddings": [[0.1, 0.2], [0.3, 0.4]]}
        mock_client_class.return_value = mock_client
        
        config = OllamaEmbeddingConfig(model_name="nomic-embed-text")
        strategy = OllamaEmbeddingStrategy(config)
        result = strategy.embed(["text1", "text2"])
        
        mock_client.embed.assert_called_once_with(
            model="nomic-embed-text",
            input=["text1", "text2"]
        )
        assert result == [[0.1, 0.2], [0.3, 0.4]]


# =============================================================================
# Cohere Embedding Tests
# =============================================================================

class TestCohereEmbeddingStrategy:
    
    @patch.dict('os.environ', {'COHERE_API_KEY': 'test_key'})
    @patch('embedding.strategies.cohere.strategy.cohere')
    def test_initialization(self, mock_cohere):
        config = CohereEmbeddingConfig(
            model_name="embed-english-v3",
            input_type="search_document"
        )
        strategy = CohereEmbeddingStrategy(config)
        assert strategy.config == config
        assert strategy.model == "embed-english-v3"
    
    @patch.dict('os.environ', {}, clear=True)
    @patch('embedding.strategies.cohere.strategy.cohere')
    def test_missing_api_key(self, mock_cohere):
        config = CohereEmbeddingConfig()
        with pytest.raises(ValueError, match="COHERE_API_KEY"):
            CohereEmbeddingStrategy(config)
    
    @patch.dict('os.environ', {'COHERE_API_KEY': 'test_key'})
    @patch('embedding.strategies.cohere.strategy.cohere')
    def test_default_model(self, mock_cohere):
        config = CohereEmbeddingConfig()
        strategy = CohereEmbeddingStrategy(config)
        assert strategy.model == "embed-english-v3"
    
    @patch.dict('os.environ', {'COHERE_API_KEY': 'test_key'})
    @patch('embedding.strategies.cohere.strategy.cohere')
    def test_embed(self, mock_cohere):
        mock_client = Mock()
        mock_client.embed.return_value = Mock(embeddings=[[0.1, 0.2, 0.3]])
        mock_cohere.Client.return_value = mock_client
        
        config = CohereEmbeddingConfig(model_name="embed-english-v3")
        strategy = CohereEmbeddingStrategy(config)
        result = strategy.embed("test text")
        
        mock_client.embed.assert_called_once_with(
            texts=["test text"],
            model="embed-english-v3",
            input_type="search_document"
        )
        assert result == [[0.1, 0.2, 0.3]]


# =============================================================================
# Voyage Embedding Tests
# =============================================================================

class TestVoyageEmbeddingStrategy:
    
    @patch.dict('os.environ', {'VOYAGE_API_KEY': 'test_key'})
    @patch('embedding.strategies.voyage.strategy.voyageai')
    def test_initialization(self, mock_voyageai):
        config = VoyageEmbeddingConfig(
            model_name="voyage-large-2",
            input_type="document"
        )
        strategy = VoyageEmbeddingStrategy(config)
        assert strategy.config == config
        assert strategy.model == "voyage-large-2"
    
    @patch.dict('os.environ', {}, clear=True)
    @patch('embedding.strategies.voyage.strategy.voyageai')
    def test_missing_api_key(self, mock_voyageai):
        config = VoyageEmbeddingConfig()
        with pytest.raises(ValueError, match="VOYAGE_API_KEY"):
            VoyageEmbeddingStrategy(config)
    
    @patch.dict('os.environ', {'VOYAGE_API_KEY': 'test_key'})
    @patch('embedding.strategies.voyage.strategy.voyageai')
    def test_embed_with_input_type(self, mock_voyageai):
        mock_client = Mock()
        mock_client.embed.return_value = Mock(embeddings=[[0.1, 0.2, 0.3]])
        mock_voyageai.Client.return_value = mock_client
        
        config = VoyageEmbeddingConfig(
            model_name="voyage-large-2",
            input_type="document"
        )
        strategy = VoyageEmbeddingStrategy(config)
        result = strategy.embed("test text")
        
        mock_client.embed.assert_called_once()
        assert result == [[0.1, 0.2, 0.3]]


# =============================================================================
# HuggingFace Embedding Tests
# =============================================================================

class TestHuggingFaceEmbeddingStrategy:
    
    @patch('embedding.strategies.huggingface.strategy.requests')
    def test_initialization(self, mock_requests):
        config = HuggingFaceEmbeddingConfig(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        strategy = HuggingFaceEmbeddingStrategy(config)
        assert strategy.config == config
        assert strategy.model == "sentence-transformers/all-MiniLM-L6-v2"
    
    @patch('embedding.strategies.huggingface.strategy.requests')
    def test_default_model(self, mock_requests):
        config = HuggingFaceEmbeddingConfig()
        strategy = HuggingFaceEmbeddingStrategy(config)
        assert strategy.model == "sentence-transformers/all-MiniLM-L6-v2"
    
    @patch('embedding.strategies.huggingface.strategy.requests')
    def test_embed(self, mock_requests):
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = [
            {"embedding": [0.1, 0.2, 0.3]},
            {"embedding": [0.4, 0.5, 0.6]}
        ]
        mock_session.post.return_value = mock_response
        mock_requests.Session.return_value = mock_session
        
        config = HuggingFaceEmbeddingConfig(model_name="test-model")
        strategy = HuggingFaceEmbeddingStrategy(config)
        result = strategy.embed(["text1", "text2"])
        
        assert result == [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
    
    @patch('embedding.strategies.huggingface.strategy.requests')
    def test_embed_with_api_key(self, mock_requests):
        mock_session = Mock()
        mock_session.headers = {}
        mock_response = Mock()
        mock_response.json.return_value = [{"embedding": [0.1, 0.2, 0.3]}]
        mock_session.post.return_value = mock_response
        mock_requests.Session.return_value = mock_session
        
        with patch.dict('os.environ', {'HUGGINGFACE_API_KEY': 'test_key'}):
            config = HuggingFaceEmbeddingConfig(model_name="test-model")
            strategy = HuggingFaceEmbeddingStrategy(config)
            strategy.embed("test")
            
            assert "Authorization" in mock_session.headers


# =============================================================================
# MedCPT Embedding Tests
# =============================================================================

class TestMedCPTEmbeddingStrategy:
    
    @patch('embedding.strategies.medcpt.strategy.get_sentence_transformer')
    def test_initialization(self, mock_get_model):
        mock_query_model = Mock()
        mock_article_model = Mock()
        mock_get_model.side_effect = [mock_query_model, mock_article_model]
        
        config = MedCPTEmbeddingConfig(
            query_model_name="ncbi/MedCPT-Query-Encoder",
            article_model_name="ncbi/MedCPT-Article-Encoder"
        )
        strategy = MedCPTEmbeddingStrategy(config)
        
        assert strategy.config == config
        assert strategy.query_model == mock_query_model
        assert strategy.article_model == mock_article_model
    
    @patch('embedding.strategies.medcpt.strategy.get_sentence_transformer')
    def test_embed_query(self, mock_get_model):
        mock_query_model = Mock()
        mock_query_model.encode.return_value = [[0.1, 0.2, 0.3]]
        mock_article_model = Mock()
        mock_get_model.side_effect = [mock_query_model, mock_article_model]
        
        config = MedCPTEmbeddingConfig()
        strategy = MedCPTEmbeddingStrategy(config)
        result = strategy.embed("test query", is_query=True)
        
        mock_query_model.encode.assert_called_once_with(
            ["test query"],
            normalize_embeddings=True
        )
        assert result == [[0.1, 0.2, 0.3]]
    
    @patch('embedding.strategies.medcpt.strategy.get_sentence_transformer')
    def test_embed_documents(self, mock_get_model):
        mock_query_model = Mock()
        mock_article_model = Mock()
        mock_article_model.encode.return_value = [[0.1, 0.2], [0.3, 0.4]]
        mock_get_model.side_effect = [mock_query_model, mock_article_model]
        
        config = MedCPTEmbeddingConfig()
        strategy = MedCPTEmbeddingStrategy(config)
        result = strategy.embed(["doc1", "doc2"], is_query=False)
        
        mock_article_model.encode.assert_called_once_with(
            ["doc1", "doc2"],
            normalize_embeddings=True
        )
        assert result == [[0.1, 0.2], [0.3, 0.4]]
    
    @patch('embedding.strategies.medcpt.strategy.get_sentence_transformer')
    def test_embed_query_method(self, mock_get_model):
        mock_query_model = Mock()
        mock_query_model.encode.return_value = [[0.1, 0.2, 0.3]]
        mock_article_model = Mock()
        mock_get_model.side_effect = [mock_query_model, mock_article_model]
        
        config = MedCPTEmbeddingConfig()
        strategy = MedCPTEmbeddingStrategy(config)
        result = strategy.embed_query("test query")
        
        assert result == [[0.1, 0.2, 0.3]]
    
    @patch('embedding.strategies.medcpt.strategy.get_sentence_transformer')
    def test_embed_documents_method(self, mock_get_model):
        mock_query_model = Mock()
        mock_article_model = Mock()
        mock_article_model.encode.return_value = [[0.1, 0.2], [0.3, 0.4]]
        mock_get_model.side_effect = [mock_query_model, mock_article_model]
        
        config = MedCPTEmbeddingConfig()
        strategy = MedCPTEmbeddingStrategy(config)
        result = strategy.embed_documents(["doc1", "doc2"])
        
        assert result == [[0.1, 0.2], [0.3, 0.4]]


# =============================================================================
# Cohere Reranker Tests
# =============================================================================

class TestCohereRerankerStrategy:
    
    @patch.dict('os.environ', {'COHERE_API_KEY': 'test_key'})
    @patch('rag.modules.reranking.strategies.cohere.strategy.cohere')
    def test_initialization(self, mock_cohere):
        config = CohereRerankerConfig(
            model_name="rerank-v3.5",
            top_n=10
        )
        strategy = CohereRerankerStrategy(config)
        assert strategy.config == config
        assert strategy.model == "rerank-v3.5"
    
    @patch.dict('os.environ', {}, clear=True)
    @patch('rag.modules.reranking.strategies.cohere.strategy.cohere')
    def test_missing_api_key(self, mock_cohere):
        config = CohereRerankerConfig()
        with pytest.raises(ValueError, match="COHERE_API_KEY"):
            CohereRerankerStrategy(config)
    
    @patch.dict('os.environ', {'COHERE_API_KEY': 'test_key'})
    @patch('rag.modules.reranking.strategies.cohere.strategy.cohere')
    def test_rerank(self, mock_cohere):
        mock_client = Mock()
        mock_result = Mock()
        mock_result.index = 0
        mock_result.relevance_score = 0.95
        mock_client.rerank.return_value = Mock(results=[mock_result])
        mock_cohere.Client.return_value = mock_client
        
        config = CohereRerankerConfig(model_name="rerank-v3.5", top_n=5)
        strategy = CohereRerankerStrategy(config)
        result = strategy.rerank("query", ["doc1", "doc2"])
        
        mock_client.rerank.assert_called_once_with(
            model="rerank-v3.5",
            query="query",
            documents=[{"text": "doc1"}, {"text": "doc2"}],
            top_n=5
        )
        assert result[0] == 0.95


# =============================================================================
# Voyage Reranker Tests
# =============================================================================

class TestVoyageRerankerStrategy:
    
    @patch.dict('os.environ', {'VOYAGE_API_KEY': 'test_key'})
    @patch('rag.modules.reranking.strategies.voyage.strategy.voyageai')
    def test_initialization(self, mock_voyageai):
        config = VoyageRerankerConfig(
            model_name="rerank-2",
            top_k=10
        )
        strategy = VoyageRerankerStrategy(config)
        assert strategy.config == config
        assert strategy.model == "rerank-2"
    
    @patch.dict('os.environ', {}, clear=True)
    @patch('rag.modules.reranking.strategies.voyage.strategy.voyageai')
    def test_missing_api_key(self, mock_voyageai):
        config = VoyageRerankerConfig()
        with pytest.raises(ValueError, match="VOYAGE_API_KEY"):
            VoyageRerankerStrategy(config)
    
    @patch.dict('os.environ', {'VOYAGE_API_KEY': 'test_key'})
    @patch('rag.modules.reranking.strategies.voyage.strategy.voyageai')
    def test_rerank(self, mock_voyageai):
        mock_client = Mock()
        mock_result = Mock()
        mock_result.index = 0
        mock_result.relevance_score = 0.95
        mock_client.rerank.return_value = Mock(results=[mock_result])
        mock_voyageai.Client.return_value = mock_client
        
        config = VoyageRerankerConfig(model_name="rerank-2", top_k=5)
        strategy = VoyageRerankerStrategy(config)
        result = strategy.rerank("query", ["doc1", "doc2"])
        
        mock_client.rerank.assert_called_once()
        assert result[0] == 0.95


# =============================================================================
# Jina Reranker Tests
# =============================================================================

class TestJinaRerankerStrategy:
    
    @patch.dict('os.environ', {'JINA_API_KEY': 'test_key'})
    @patch('rag.modules.reranking.strategies.jina.strategy.requests')
    def test_initialization(self, mock_requests):
        config = JinaRerankerConfig(
            model_name="jina-reranker-v2-base",
            top_n=10
        )
        strategy = JinaRerankerStrategy(config)
        assert strategy.config == config
        assert strategy.model == "jina-reranker-v2-base"
    
    @patch.dict('os.environ', {}, clear=True)
    @patch('rag.modules.reranking.strategies.jina.strategy.requests')
    def test_missing_api_key(self, mock_requests):
        config = JinaRerankerConfig()
        with pytest.raises(ValueError, match="JINA_API_KEY"):
            JinaRerankerStrategy(config)
    
    @patch.dict('os.environ', {'JINA_API_KEY': 'test_key'})
    @patch('rag.modules.reranking.strategies.jina.strategy.requests')
    def test_rerank(self, mock_requests):
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [{"index": 0, "relevance_score": 0.95}]
        }
        mock_session.post.return_value = mock_response
        mock_requests.Session.return_value = mock_session
        
        config = JinaRerankerConfig(model_name="jina-reranker-v2-base", top_n=5)
        strategy = JinaRerankerStrategy(config)
        result = strategy.rerank("query", ["doc1", "doc2"])
        
        mock_session.post.assert_called_once()
        assert result[0] == 0.95


# =============================================================================
# MixedBread Reranker Tests
# =============================================================================

class TestMixedBreadRerankerStrategy:
    
    @patch.dict('os.environ', {'MIXEDBREAD_API_KEY': 'test_key'})
    @patch('rag.modules.reranking.strategies.mixedbread.strategy.requests')
    def test_initialization(self, mock_requests):
        config = MixedBreadRerankerConfig(
            model_name="mxbai-rerank-large-v1",
            top_n=10
        )
        strategy = MixedBreadRerankerStrategy(config)
        assert strategy.config == config
        assert strategy.model == "mxbai-rerank-large-v1"
    
    @patch.dict('os.environ', {}, clear=True)
    @patch('rag.modules.reranking.strategies.mixedbread.strategy.requests')
    def test_missing_api_key(self, mock_requests):
        config = MixedBreadRerankerConfig()
        with pytest.raises(ValueError, match="MIXEDBREAD_API_KEY"):
            MixedBreadRerankerStrategy(config)
    
    @patch.dict('os.environ', {'MIXEDBREAD_API_KEY': 'test_key'})
    @patch('rag.modules.reranking.strategies.mixedbread.strategy.requests')
    def test_rerank(self, mock_requests):
        mock_session = Mock()
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [{"index": 0, "relevance_score": 0.95}]
        }
        mock_session.post.return_value = mock_response
        mock_requests.Session.return_value = mock_session
        
        config = MixedBreadRerankerConfig(model_name="mxbai-rerank-large-v1", top_n=5)
        strategy = MixedBreadRerankerStrategy(config)
        result = strategy.rerank("query", ["doc1", "doc2"])
        
        mock_session.post.assert_called_once()
        assert result[0] == 0.95
