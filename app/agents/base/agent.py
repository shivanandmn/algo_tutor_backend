from dotenv import load_dotenv
import asyncio
import livekit
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import deepgram, elevenlabs, openai, silero, noise_cancellation
from livekit.agents import AutoSubscribe
import os
import logging
import json
from livekit.agents import JobProcess
from livekit.plugins.turn_detector.english import EnglishModel

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()
    
load_dotenv()
logger = logging.getLogger(__name__)


class Assistant(Agent):
    def __init__(self, **kwargs) -> None:
        # Create the OpenAI LLM
        openai_llm = openai.LLM(
            model="gpt-4o-mini",    # or "gpt-4o", "o1", etc.
            temperature=0.7,
        )
        # Initialize the Agent with the LLM
        super().__init__(
            instructions="You are a helpful voice assistant.",
            llm=openai_llm,
            **kwargs,
        )
        # Store participant information
        self.user_names = {}
        
    async def edit_instructions(self, instructions: str):
        await self.update_instructions(instructions)
    
    async def on_enter(self):
        self.session.generate_reply()
        

async def entrypoint(ctx: agents.JobContext):
    logger.info("Starting voice assistant")
    # 1. Connect to the LiveKit room (only audio)
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    participant = await ctx.wait_for_participant()
    print(f"starting voice assistant for participant {participant.identity}")

    # Create the agent instance
    agent = Assistant()
    # print("After agent")
    @ctx.room.on("data_received")
    def on_data_received(data_packet):
        # Log metadata
        sender = data_packet.participant.identity if data_packet.participant else "server"
        logger.info(f"Data received from {sender}: kind={data_packet.kind}, topic={data_packet.topic}")
        
        # Decode payload
        try:
            text = data_packet.data.decode("utf-8")
            problem_context = json.loads(text)
            logger.info(f"Prompt received: {problem_context}")
            question = problem_context.get("content", "")
            title = problem_context.get("title", "")
            instructions=f"You are a Expert tutor in Data Structures and Algorithms. You are speaking with a student who is learning Data Structures and Algorithms. By Solving the questions you will help the student to understand the concepts better. \nQuestion Title: {title}\nQuestion: {question}.\n Your task is provide as many hits as possible around this question to teach him and help him to understand the concepts better."
            asyncio.create_task(agent.edit_instructions(instructions))
            # process the text    
            
        except Exception as e:
            logger.error(f"Error decoding payload: {e}")

    # 2. Create and start the AgentSession

    
    # session = AgentSession(
    #     # vad=ctx.userdata["vad"],
    #     llm=openai.realtime.RealtimeModel(
    #         model = "gpt-4o-mini-realtime-preview",voice="alloy",
    #         )
    # )
    
    tts_params = {
            "model":"eleven_turbo_v2_5",
            "voice_id": "EXAVITQu4vr4xnSDxMaL",
            "voice_settings": elevenlabs.tts.VoiceSettings(
                stability=0.71,
                similarity_boost=0.5,
                style=0.0,
                use_speaker_boost=True,
            ),
            "streaming_latency": 3,
            "enable_ssml_parsing": False,
            "chunk_length_schedule": [80, 120, 200, 260],
        }
    session = AgentSession(
        vad=ctx.proc.userdata["vad"],
        stt=deepgram.STT(
            model="nova-3",
            interim_results=True,
            smart_format=True,
            punctuate=True,
            filler_words=True,
            profanity_filter=False,
            language="en",
        ),
        tts=elevenlabs.tts.TTS(**tts_params),
        turn_detection=EnglishModel(),
    )

    logger.info("Starting AgentSession...")
    await session.start(
        room=ctx.room,
        agent=agent,  # Use our agent instance with user_names
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )
    
    


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(
        entrypoint_fnc=entrypoint,
        ws_url=os.getenv("LIVEKIT_URL"),
        api_key=os.getenv("LIVEKIT_API_KEY"),
        api_secret=os.getenv("LIVEKIT_API_SECRET"),
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8080")),
        prewarm_fnc=prewarm
    ),
    
    )
