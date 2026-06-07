import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

from workflow import OCRWorkflow
from activity import run_ocr_activity


async def main():
    client = await Client.connect("localhost:7233")

    async with Worker(
        client,
        task_queue="ocr-task-queue",
        workflows=[OCRWorkflow],
        activities=[run_ocr_activity],
    ):
        print("[Worker] Running — waiting for jobs...")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())