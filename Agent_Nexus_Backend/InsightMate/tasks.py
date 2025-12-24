import dramatiq
import asyncio
from InsightMate.summary_agent import InsightMateAgent

@dramatiq.actor
def process_meeting_summary(app_id: str, user_id: str, transcript: str):
    try:
        agent = InsightMateAgent(app_id=app_id, user_id=user_id)
        
       
        final_result = asyncio.run(agent.execute_task(raw_transcript=transcript))
        
        print("--- Agent Analysis Complete ---")
        print(f"Run ID: {final_result['audit']['run_id']}")
        print(f"Attempts: {final_result['audit']['correction_attempts']}")
        
    except Exception as e:
        print(f"FATAL WORKER ERROR: Failed to execute agent task: {e}")
        # In Phase 6, this would queue a retry or send to a Dead Letter Queue