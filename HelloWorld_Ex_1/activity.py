import asyncio
from temporalio import activity

#Single unit of work one function
# In OCR library, each OCR inference call will be an activity
@activity.defn
async def say_hello(name:str)-> str:
    print(f"[Activity] processing: {name}")
    return f"hello from activity, {name}!"


