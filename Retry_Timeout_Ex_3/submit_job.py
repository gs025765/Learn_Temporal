import asyncio
from temporalio.client import Client
from data_model import ImageInput
from workflow import OCRWorkflow


async def main():
    client = await Client.connect("localhost:7233")
    handle = await client.start_workflow(
        OCRWorkflow,
        ImageInput(file_path="../Structured_Data/sample_doc.txt",page_number=1),
        id="ocr2",
        task_queue="ocr_queue",
    )
    print(f"[Client] Job Submitted: {handle.id}")
    result = await handle.result()

    print(f"\n[Result]")
    print(f"  Page      : {result.page_number}")
    print(f"  Text      : {result.text}")
    print(f"  Confidence: {result.confidence}")
    print(f"  Status    : {result.status}")

if __name__ == "__main__":
    asyncio.run(main())