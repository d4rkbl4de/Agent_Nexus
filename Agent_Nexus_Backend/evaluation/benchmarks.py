import asyncio
import time
from typing import List, Dict, Any, Optional
from uuid import uuid4
from pydantic import BaseModel, Field
from datetime import datetime
from common.config.logging import logger
from common.schemas.errors import AppError, ErrorCategory

class BenchmarkCase(BaseModel):
    case_id: str = Field(default_factory=lambda: str(uuid4()))
    input_data: Dict[str, Any]
    expected_output: Dict[str, Any]
    metrics_thresholds: Dict[str, float] = Field(
        default_factory=lambda: {"min_confidence": 0.8, "max_latency_ms": 2000.0}
    )

class BenchmarkResult(BaseModel):
    case_id: str
    status: str
    actual_output: Optional[Dict[str, Any]]
    latency_ms: float
    confidence_score: float
    violations: List[str] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class AgentBenchmarker:
    def __init__(self, agent_instance: Any):
        self.agent = agent_instance
        self.results: List[BenchmarkResult] = []

    async def run_suite(self, cases: List[BenchmarkCase]) -> List[BenchmarkResult]:
        tasks = [self._run_case(case) for case in cases]
        self.results = await asyncio.gather(*tasks)
        self._generate_report()
        return self.results

    async def _run_case(self, case: BenchmarkCase) -> BenchmarkResult:
        start_time = time.perf_counter()
        violations = []
        
        try:
            response = await self.agent.process(
                input_data=case.input_data,
                trace_id=f"bench_{case.case_id}"
            )
            
            latency = (time.perf_counter() - start_time) * 1000
            confidence = response.get("confidence", 0.0)

            if latency > case.metrics_thresholds.get("max_latency_ms", 5000):
                violations.append("LATENCY_EXCEEDED")
            
            if confidence < case.metrics_thresholds.get("min_confidence", 0.0):
                violations.append("CONFIDENCE_INSUFFICIENT")

            status = "PASSED" if not violations else "FAILED"
            
            return BenchmarkResult(
                case_id=case.case_id,
                status=status,
                actual_output=response,
                latency_ms=latency,
                confidence_score=confidence,
                violations=violations
            )

        except Exception as e:
            return BenchmarkResult(
                case_id=case.case_id,
                status="ERROR",
                actual_output={"error": str(e)},
                latency_ms=(time.perf_counter() - start_time) * 1000,
                confidence_score=0.0,
                violations=["EXECUTION_CRASH"]
            )

    def _generate_report(self) -> None:
        total = len(self.results)
        passed = len([r for r in self.results if r.status == "PASSED"])
        logger.info(f"BENCHMARK_REPORT | Total: {total} | Passed: {passed} | Success Rate: {(passed/total)*100:.2f}%")

class BenchmarkRegistry:
    _benchmarks: Dict[str, List[BenchmarkCase]] = {}

    @classmethod
    def register_case(cls, lobe: str, case: BenchmarkCase):
        if lobe not in cls._benchmarks:
            cls._benchmarks[lobe] = []
        cls._benchmarks[lobe].append(case)

    @classmethod
    def get_cases(cls, lobe: str) -> List[BenchmarkCase]:
        return cls._benchmarks.get(lobe, [])