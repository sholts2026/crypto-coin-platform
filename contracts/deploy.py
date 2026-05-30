"""
deploy.py — PepeJunior (PEPEJI) deployment script

IMPORTANT SAFETY RULES:
  - DO NOT run against mainnet without human approval
  - Set DEPLOY_TO_MAINNET=false in .env (default) to stay on testnet
  - All wallet addresses below are PLACEHOLDERS — replace with real multisigs
  - Keep DEPLOYER_PRIVATE_KEY out of git (it's in .gitignore)

Usage:
  # Testnet (safe):
  python contracts/deploy.py

  # Mainnet (requires explicit confirmation):
  DEPLOY_TO_MAINNET=true python contracts/deploy.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

# ── Safety gate ────────────────────────────────────────────────────────────────
DEPLOY_TO_MAINNET = os.getenv("DEPLOY_TO_MAINNET", "false").lower() == "true"
if DEPLOY_TO_MAINNET:
    print("\n" + "="*60)
    print("⚠️  MAINNET DEPLOYMENT REQUESTED")
    print("This will spend real ETH and create a permanent on-chain record.")
    print("="*60)
    confirm = input("Type CONFIRM-MAINNET to proceed (anything else aborts): ")
    if confirm.strip() != "CONFIRM-MAINNET":
        print("Aborted by user.")
        sys.exit(0)
else:
    print("Mode: TESTNET (safe). Set DEPLOY_TO_MAINNET=true for mainnet.")

# ── Config ─────────────────────────────────────────────────────────────────────
PRIVATE_KEY = os.getenv("DEPLOYER_PRIVATE_KEY", "")
if not PRIVATE_KEY or PRIVATE_KEY in ("NEVER_PUT_REAL_KEY_HERE", ""):
    print("ERROR: Set DEPLOYER_PRIVATE_KEY in .env")
    print("       Never commit real private keys to git.")
    sys.exit(1)

CHAIN    = os.getenv("DEFAULT_CHAIN", "ethereum")
RPC_URL  = os.getenv(f"RPC_URL_{CHAIN.upper()}", "http://localhost:8545")

# ── Wallet addresses ── REPLACE THESE WITH REAL MULTISIG WALLETS ───────────────
LIQUIDITY_WALLET  = os.getenv("LIQUIDITY_WALLET",  "0x0000000000000000000000000000000000000001")
COMMUNITY_WALLET  = os.getenv("COMMUNITY_WALLET",  "0x0000000000000000000000000000000000000002")
TREASURY_WALLET   = os.getenv("TREASURY_WALLET",   "0x0000000000000000000000000000000000000003")
TEAM_WALLET       = os.getenv("TEAM_WALLET",        "0x0000000000000000000000000000000000000004")
MARKETING_WALLET  = os.getenv("MARKETING_WALLET",  "0x0000000000000000000000000000000000000005")

PLACEHOLDER_WALLETS = {"0x" + "0" * 39 + "1", "0x" + "0" * 39 + "2",
                       "0x" + "0" * 39 + "3", "0x" + "0" * 39 + "4",
                       "0x" + "0" * 39 + "5"}

for name, addr in [("LIQUIDITY_WALLET", LIQUIDITY_WALLET), ("COMMUNITY_WALLET", COMMUNITY_WALLET),
                   ("TREASURY_WALLET", TREASURY_WALLET), ("TEAM_WALLET", TEAM_WALLET),
                   ("MARKETING_WALLET", MARKETING_WALLET)]:
    if addr in PLACEHOLDER_WALLETS:
        print(f"WARNING: {name} is still a placeholder address.")
        print("         Replace all wallet addresses before deploying.")
        if DEPLOY_TO_MAINNET:
            print("ERROR: Cannot deploy to mainnet with placeholder wallets.")
            sys.exit(1)

# ── Web3 connection ────────────────────────────────────────────────────────────
try:
    from web3 import Web3
    from eth_account import Account
except ImportError:
    print("ERROR: Missing dependencies. Run: pip install web3 eth-account")
    sys.exit(1)

w3 = Web3(Web3.HTTPProvider(RPC_URL))
if not w3.is_connected():
    print(f"ERROR: Cannot connect to RPC: {RPC_URL}")
    sys.exit(1)

account = Account.from_key(PRIVATE_KEY)
balance = w3.eth.get_balance(account.address)

print(f"\nDeployer:  {account.address}")
print(f"Balance:   {balance / 1e18:.4f} ETH")
print(f"Chain ID:  {w3.eth.chain_id}")
print(f"RPC:       {RPC_URL}")

# ── Load compiled artifact ─────────────────────────────────────────────────────
# Compile with Hardhat: npx hardhat compile
# Then load from artifacts/contracts/Token.sol/PepeJunior.json
print("\nTODO: Load compiled ABI and bytecode from Hardhat artifacts.")
print("      Run: npx hardhat compile")
print("      Then uncomment the deployment transaction below.")

# import json
# from pathlib import Path
# artifact_path = Path("artifacts/contracts/Token.sol/PepeJunior.json")
# artifact = json.loads(artifact_path.read_text())
# contract = w3.eth.contract(abi=artifact["abi"], bytecode=artifact["bytecode"])
#
# nonce = w3.eth.get_transaction_count(account.address)
# tx = contract.constructor(
#     LIQUIDITY_WALLET, COMMUNITY_WALLET, TREASURY_WALLET,
#     TEAM_WALLET, MARKETING_WALLET
# ).build_transaction({
#     "from": account.address,
#     "nonce": nonce,
#     "gas": 3_000_000,
#     "gasPrice": w3.eth.gas_price,
# })
# signed = account.sign_transaction(tx)
# tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
# print(f"Tx Hash: {tx_hash.hex()}")
# receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
# print(f"Contract deployed at: {receipt.contractAddress}")

print("\nDeployment script ready. Compile contract and uncomment transaction.")
