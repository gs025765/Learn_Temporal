import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from workflow import HelloWorkflow
from activity import say_hello


async def main():
    client = await Client.connect("localhost:7233")

    async with Worker(
        client,
        task_queue="poc",
        workflows=[HelloWorkflow],
        activities=[say_hello]
    ):
        print("[Worker] Started, Polling ocr-task-queue ...")
        result = await client.execute_workflow(
            HelloWorkflow.run,
            "Gaurav",
            id="poc1",
            task_queue="poc"
        )
        print(f"[Client] Workflow result: {result}")

if __name__ == "__main__":
    asyncio.run(main())