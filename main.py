from app.agents.base.agent import entrypoint
from livekit import agents
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint,
        ws_url=os.getenv("LIVEKIT_URL"),
        api_key=os.getenv("LIVEKIT_API_KEY"),
        api_secret=os.getenv("LIVEKIT_API_SECRET"),
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8081")),))