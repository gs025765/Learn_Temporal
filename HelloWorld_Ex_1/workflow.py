import asyncio
from datetime import timedelta
from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from activity import say_hello

#Workflow is an Orchestrator it call activities in order
#In OCR workflow will call preproces,infer, postprocess

@workflow.defn
class HelloWorkflow:
    @workflow.run
    async def run(self, name: str)->str:
        print(f"[Workflow] Starting for: {name}")

        # This is how a workflow calls an activity
        result = await workflow.execute_activity(
            say_hello,
            name,
            start_to_close_timeout=timedelta(seconds=10),
        )
        return result

