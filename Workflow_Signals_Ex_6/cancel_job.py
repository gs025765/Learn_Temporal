import asyncio
from temporalio.client import Client


async def main():
    client = await Client.connect("localhost:7233")

    # Get handle to the already-running workflow by its id
    handle = client.get_workflow_handle("ocr-workflow-ex7")

    # Send cancel signal — fire and forget
    await handle.signal("cancel_job")

    print(f"[Client] Cancel signal sent to ocr-workflow-ex7")
    print(f"[Client] Workflow will stop after current page completes")


if __name__ == "__main__":
    asyncio.run(main())