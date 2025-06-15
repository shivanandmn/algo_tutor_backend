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
        # Store participant information
        self.user_names = {}

async def entrypoint(ctx: agents.JobContext):
    # 1. Connect to the LiveKit room (only audio)
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    participant = await ctx.wait_for_participant()
    print(f"starting voice assistant for participant {participant.identity}")

    # Create the agent instance
    agent = Assistant()
    
    # Set up participant tracking
    @ctx.room.on("participant_connected")
    def on_participant_connected(participant):
        # Store participant name when they join
        agent.user_names[participant.identity] = participant.name
        print(f"Participant connected: {participant.name} (identity: {participant.identity})")
    
    @ctx.room.on("participant_disconnected")
    def on_participant_disconnected(participant):
        # Remove participant when they leave
        if participant.identity in agent.user_names:
            del agent.user_names[participant.identity]
            print(f"Participant disconnected: {participant.identity}")

    # 2. Create and start the AgentSession
    session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            model = "gpt-4o-mini-realtime-preview",voice="alloy")
    )
    await session.start(
        room=ctx.room,
        agent=agent,  # Use our agent instance with user_names
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    try:
        # Populate initial participants that were already in the room
        for remote_participant in ctx.room.remote_participants.values():
            agent.user_names[remote_participant.identity] = remote_participant.name
            print(f"Initial participant found: {remote_participant.name} (identity: {remote_participant.identity})")
            
        # Format user names for personalized greeting
        user_list = list(agent.user_names.values())
        greeting_names = ""  
        greeting_names = user_list[0]
        
        # 3. Initial greeting to user with their name
        greeting_instruction = f"Greet {greeting_names} by name and offer your assistance."
        await session.generate_reply(instructions=greeting_instruction)

        # 4. Keep generating replies as long as user is in room
        while ctx.room.remote_participants:
            # Include user names in the context for the agent
            user_context = ""
            if agent.user_names:
                names_list = list(agent.user_names.values())
                user_context = f"You're speaking with {', '.join(names_list)}. "
            
            # Generate reply with access to user names
            await session.generate_reply(
                instructions=f"{user_context}Respond conversationally and helpfully."
            )
    finally:
        # 5. Cleanly stop the session pipelines
        pass  # No stop() method on AgentSession; cleanup not needed or handled elsewhere.

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
