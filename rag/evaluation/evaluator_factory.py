from rag.config.config import EvaluationConfig
from rag.config.enums import EvaluationType
from rag.evaluation.trace_evaluation import TRACeEvaluationStrategy

class EvaluatorFactory:
    
    @staticmethod
    def create_evaluator(
        config: EvaluationConfig,
        *,
        provider,
    ):
        strategies = {
            EvaluationType.TRACE: lambda: TRACeEvaluationStrategy(
                config=config.config,
                provider=provider
            )
        }
        return strategies[config.type]()