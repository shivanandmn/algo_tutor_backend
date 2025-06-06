import os
import asyncio
from app.agents.base.agent import entrypoint
from livekit.agents import Worker, WorkerOptions
from dotenv import load_dotenv

load_dotenv()

async def main():
    opts = WorkerOptions(
        entrypoint_fnc=entrypoint,
        ws_url=os.getenv("LIVEKIT_URL"),
        api_key=os.getenv("LIVEKIT_API_KEY"),
        api_secret=os.getenv("LIVEKIT_API_SECRET"),
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8081")),
    )
    worker = Worker(opts)
    # Directly call run(), which runs drain() internally.
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
