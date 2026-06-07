import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

from workflow import OCRWorkflow
from activity import ocr_output

async def main():
    client = await Client.connect("localhost:7233")

    async with Worker(
        client,
        task_queue="ocr_queue",
        workflows=[OCRWorkflow],
        activities=[ocr_output],):
        print("[Worker] Running Forever - waiting for jobs...")
        await asyncio.Future()


if __name__=="__main__":
    asyncio.run(main())
