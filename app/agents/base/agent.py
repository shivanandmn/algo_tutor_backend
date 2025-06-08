from dotenv import load_dotenv
import asyncio

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import openai, noise_cancellation
from livekit.agents import AutoSubscribe
load_dotenv()

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions="You are a helpful voice AI assistant.")

async def entrypoint(ctx: agents.JobContext):
    # 1. Connect to the LiveKit room (only audio)
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # 2. Create and start the AgentSession
    session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            model = "gpt-4o-mini-realtime-preview",voice="alloy")
    )
    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    try:
        # 3. Initial greeting to user
        await session.generate_reply(
            instructions="Greet the user and offer your assistance."
        )

        # 4. Keep generating replies as long as user is in room
        while ctx.room.remote_participants:
            await session.generate_reply()
    finally:
        # 5. Cleanly stop the session pipelines
        pass  # No stop() method on AgentSession; cleanup not needed or handled elsewhere.

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
