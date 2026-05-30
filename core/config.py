from __future__ import annotations
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

    # AI / LLM
    gemini_api_key: str = ""
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    # Social APIs
    twitter_api_key: str = ""
    twitter_api_secret: str = ""
    twitter_access_token: str = ""
    twitter_access_secret: str = ""
    reddit_client_id: str = ""
    reddit_client_secret: str = ""
    reddit_username: str = ""
    reddit_password: str = ""
    youtube_api_key: str = ""
    tiktok_session_id: str = ""
    google_trends_enabled: bool = False

    # Crypto / Chain
    coingecko_api_key: str = ""
    etherscan_api_key: str = ""
    rpc_url_ethereum: str = "https://mainnet.infura.io/v3/YOUR_KEY"
    rpc_url_base: str = "https://mainnet.base.org"
    rpc_url_solana: str = "https://api.mainnet-beta.solana.com"
    deployer_private_key: str = ""
    default_chain: str = "ethereum"

    # App
    database_url: str = f"sqlite:///{BASE_DIR}/data/crypto_coin.db"
    secret_key: str = "change-me"
    debug: bool = True
    log_level: str = "INFO"

    # Dashboard
    frontend_url: str = "http://localhost:5173"
    backend_url: str = "http://localhost:8000"

    # Data paths
    data_dir: Path = BASE_DIR / "data"
    contracts_dir: Path = BASE_DIR / "contracts"
    logs_dir: Path = BASE_DIR / "logs"


settings = Settings()
