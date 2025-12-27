from typing import Dict, Any, List, Optional
from evaluation.metrics import metrics_registry, ExecutionMetrics
from evaluation.scoring import quality_scorer, FinalValidation
from evaluation.feedback import feedback_engine, FeedbackEntry
from evaluation.benchmarks import AgentBenchmarker, BenchmarkCase

class EvaluationFacade:
    def __init__(self):
        self.metrics = metrics_registry
        self.scorer = quality_scorer
        self.feedback = feedback_engine

    async def evaluate_agent_turn(
        self,
        trace_id: str,
        agent_id: str,
        lobe: str,
        output: Dict[str, Any],
        cost: float,
        tokens: Dict[str, int],
        criteria: Optional[Dict[str, float]] = None
    ) -> FinalValidation:
        self.metrics.stop_segment(
            trace_id=trace_id,
            status="SUCCESS",
            tokens=tokens,
            cost=cost
        )
        
        validation = await self.scorer.compute_score(
            trace_id=trace_id,
            raw_output=output,
            criteria=criteria or {"logic": 0.5, "alignment": 0.5}
        )
        
        return validation

    async def run_benchmark(self, agent: Any, cases: List[BenchmarkCase]):
        benchmarker = AgentBenchmarker(agent)
        return await benchmarker.run_suite(cases)

    async def process_feedback(self, entry: FeedbackEntry):
        return await self.feedback.submit_feedback(entry)

evaluation_service = EvaluationFacade()

__all__ = [
    "evaluation_service",
    "metrics_registry",
    "quality_scorer",
    "feedback_engine",
    "AgentBenchmarker",
    "BenchmarkCase"
]