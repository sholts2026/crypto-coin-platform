"""
start.py — Launch both backend and a setup reminder for frontend.
Run: python start.py
"""
import subprocess
import sys
import os

def main():
    print("\n🚀 Crypto Coin Launch Command Center")
    print("="*50)

    # Ensure data dir exists
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # Seed mock data if missing
    from pathlib import Path
    for f in ["trends.json", "token_ideas.json", "decisions.json", "risk_reviews.json", "social_drafts.json"]:
        if not Path(f"data/{f}").exists():
            print(f"Seeding mock data: {f}")
            Path(f"data/{f}").write_text("[]", encoding="utf-8")

    print("\n📡 Starting FastAPI backend on http://localhost:8000 ...")
    print("   API docs: http://localhost:8000/docs")
    print("\n💡 To start the dashboard frontend:")
    print("   cd frontend && npm install && npm run dev")
    print("   Dashboard: http://localhost:5173\n")
    print("📟 CLI usage:")
    print("   python cli/main.py run-all\n")

    # Start backend
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "backend.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload",
    ])

if __name__ == "__main__":
    main()
