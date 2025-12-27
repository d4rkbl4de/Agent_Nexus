from typing import Any, Dict, Optional
from decisions.proposal import ActionProposal, ProposalManager
from decisions.verdict import DecisionVerdict, PolicyEngine
from decisions.record import decision_recorder

class DecisionOrchestrator:
    def __init__(self):
        self.manager = ProposalManager()
        self.engine = PolicyEngine()
        self.recorder = decision_recorder

    async def process_action(
        self, 
        proposal: ActionProposal
    ) -> DecisionVerdict:
        await self.manager.submit(proposal)
        
        verdict = await self.engine.evaluate_proposal(proposal)
        
        await self.recorder.record_event(proposal, verdict)
        
        return verdict

decision_service = DecisionOrchestrator()

__all__ = [
    "decision_service",
    "ActionProposal",
    "DecisionVerdict",
    "ProposalManager",
    "PolicyEngine",
    "decision_recorder"
]