import asyncio
import json
import random
from aiohttp import web

import aiohttp

# Simulates what Triton returns after OCR inference

async def handle_infer(request):
    try:
        body = await request.json()
        file_path = body.get("file_path","")
        page_number = body.get("page_number",1)

        print(f"[MockTriton] Received inference request for: {file_path}")
        if random.random()<0.3:
            print(f"[MockTriton] Simulating server overload -returning 503")
            return web.Response(
                status=503,
                text=json.dumps({"error":"Server Temporarily overloaded"}),
                content_type="application/json"
            )

        await asyncio.sleep(0.5)

        try:
            with open(file_path,"r") as f:
                content = f.read().strip()
            confidence =0.95
        except FileNotFoundError:
            return web.response(
                status=404,
                text=json.dumps({"error": f"File not found: {file_path}"}),
                content_type="application/json"
            )

                # Return Triton-style response
        response_body = {
            "page_number": page_number,
            "text": content,
            "confidence": confidence,
            "model": "paddleocr-v3",
            "inference_time_ms": 487
        }
        print(f"[MockTriton] Inference complete for page {page_number}")
        return web.Response(
            status=200,
            text=json.dumps(response_body),
            content_type="application/json"
        )
    except Exception as e:
        return web.Response(
            status=500,
            text=json.dumps({"error": str(e)}),
            content_type="application/json"
        )

async def main():
    app = web.Application()
    app.router.add_post("/v2/models/paddleocr/infer", handle_infer)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, "localhost", 8080)
    await site.start()

    print("[MockTriton] Server running at http://localhost:8080")
    print("[MockTriton] Endpoint: POST /v2/models/paddleocr/infer")
    print("[MockTriton] 30% chance of returning 503 to simulate load")

    # Run forever
    await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())

            

