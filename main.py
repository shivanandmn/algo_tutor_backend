from app.agents.base.agent import entrypoint
from livekit import agents

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))