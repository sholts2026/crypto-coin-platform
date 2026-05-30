from __future__ import annotations
import uuid
from datetime import datetime
from typing import Dict

from core import memory
from core.schemas import AgentOutput


ERC20_TEMPLATE = '''// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title {token_name}
 * @dev ERC-20 meme token. Community-driven. No minting after deployment.
 *
 * Tokenomics:
 *   Total Supply : {total_supply} {ticker}
 *   Liquidity    : {liquidity_pct}%  (to be locked on-chain)
 *   Community    : {community_pct}%
 *   Treasury     : {treasury_pct}%
 *   Team         : {team_pct}%  (vesting recommended off-chain or via vesting contract)
 *   Marketing    : {marketing_pct}%
 *
 * IMPORTANT: This contract is a DRAFT. DO NOT deploy to mainnet without:
 *   1. Independent security audit
 *   2. Human founder review and approval
 *   3. Legal review in your jurisdiction
 */
contract {token_name_clean} is ERC20, Ownable {{

    uint256 public constant MAX_SUPPLY = {total_supply} * 10 ** 18;

    address public liquidityWallet;
    address public communityWallet;
    address public treasuryWallet;
    address public teamWallet;
    address public marketingWallet;

    constructor(
        address _liquidityWallet,
        address _communityWallet,
        address _treasuryWallet,
        address _teamWallet,
        address _marketingWallet
    ) ERC20("{token_name}", "{ticker}") Ownable(msg.sender) {{

        require(_liquidityWallet  != address(0), "Zero address: liquidity");
        require(_communityWallet  != address(0), "Zero address: community");
        require(_treasuryWallet   != address(0), "Zero address: treasury");
        require(_teamWallet       != address(0), "Zero address: team");
        require(_marketingWallet  != address(0), "Zero address: marketing");

        liquidityWallet  = _liquidityWallet;
        communityWallet  = _communityWallet;
        treasuryWallet   = _treasuryWallet;
        teamWallet       = _teamWallet;
        marketingWallet  = _marketingWallet;

        uint256 total = MAX_SUPPLY;

        _mint(_liquidityWallet,  total * {liquidity_pct_int}  / 100);
        _mint(_communityWallet,  total * {community_pct_int}  / 100);
        _mint(_treasuryWallet,   total * {treasury_pct_int}   / 100);
        _mint(_teamWallet,       total * {team_pct_int}       / 100);
        _mint(_marketingWallet,  total * {marketing_pct_int}  / 100);
    }}

    // ── Owner can renounce after verifying allocations are correct ──
    // Call renounceOwnership() after confirming wallets are correct.
    // Once renounced, no admin functions remain. Truly community-owned.
}}
'''


DEPLOY_TEMPLATE = '''"""
deploy.py — {token_name} ({ticker}) deployment script
Chain: {chain}

WARNING: DO NOT run against mainnet without human approval.
Set DEPLOY_TO_MAINNET=false in .env to prevent accidental mainnet deployment.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── Safety gate ────────────────────────────────────────────────────────────────
DEPLOY_TO_MAINNET = os.getenv("DEPLOY_TO_MAINNET", "false").lower() == "true"
if DEPLOY_TO_MAINNET:
    confirm = input(
        "\\n⚠️  MAINNET DEPLOYMENT REQUESTED.\\n"
        "Type CONFIRM-MAINNET to proceed: "
    )
    if confirm != "CONFIRM-MAINNET":
        print("Aborted.")
        exit(0)

PRIVATE_KEY = os.getenv("DEPLOYER_PRIVATE_KEY", "")
RPC_URL = os.getenv("RPC_URL_{chain_upper}", "http://localhost:8545")

if not PRIVATE_KEY or PRIVATE_KEY == "NEVER_PUT_REAL_KEY_HERE":
    print("ERROR: Set DEPLOYER_PRIVATE_KEY in .env — never commit real keys.")
    exit(1)

# ── Wallet addresses — FILL THESE IN ──────────────────────────────────────────
LIQUIDITY_WALLET  = os.getenv("LIQUIDITY_WALLET",  "0x0000000000000000000000000000000000000001")
COMMUNITY_WALLET  = os.getenv("COMMUNITY_WALLET",  "0x0000000000000000000000000000000000000002")
TREASURY_WALLET   = os.getenv("TREASURY_WALLET",   "0x0000000000000000000000000000000000000003")
TEAM_WALLET       = os.getenv("TEAM_WALLET",        "0x0000000000000000000000000000000000000004")
MARKETING_WALLET  = os.getenv("MARKETING_WALLET",  "0x0000000000000000000000000000000000000005")

try:
    from web3 import Web3
    from eth_account import Account
except ImportError:
    print("Install: pip install web3 eth-account")
    exit(1)

w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = Account.from_key(PRIVATE_KEY)
print(f"Deployer: {{account.address}}")
print(f"Balance:  {{w3.eth.get_balance(account.address) / 1e18:.4f}} ETH")
print(f"Chain ID: {{w3.eth.chain_id}}")

# TODO: Load ABI and bytecode from compiled contract artifacts
# from pathlib import Path
# import json
# artifact = json.loads(Path("artifacts/{token_name_clean}.json").read_text())
# contract = w3.eth.contract(abi=artifact["abi"], bytecode=artifact["bytecode"])
# ...

print("\\nDeployment script ready. Compile contract first with Hardhat or Foundry.")
print("Then uncomment the deployment transaction above.")
'''


TEST_TEMPLATE = '''"""
test_token.py — {token_name} ({ticker}) test suite
Framework: pytest + web3.py (local Hardhat/Anvil node)

Run: pytest contracts/test_token.py -v
"""
import pytest

# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture
def accounts():
    """Return test accounts. Replace with web3.py / brownie fixtures."""
    return [
        "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        "0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
        "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC",
        "0x90F79bf6EB2c4f870365E785982E1f101E93b906",
        "0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65",
    ]


@pytest.fixture
def token_contract(accounts):
    """Deploy the token. Replace with actual web3/brownie deployment."""
    # TODO: Deploy contract using accounts[0] as deployer
    # Return contract instance
    return None  # placeholder


# ── Unit tests ──────────────────────────────────────────────────────────────────

class TestTokenomics:
    def test_total_supply(self, token_contract):
        """Total supply must equal {total_supply} * 10^18."""
        if token_contract is None:
            pytest.skip("Contract not deployed — run against local node")
        expected = {total_supply} * 10**18
        assert token_contract.functions.totalSupply().call() == expected

    def test_no_additional_minting(self, token_contract):
        """No mint function should exist after deployment."""
        if token_contract is None:
            pytest.skip("Contract not deployed")
        # Verify no mint ABI exposed
        abi_names = [fn["name"] for fn in token_contract.abi if fn.get("type") == "function"]
        assert "mint" not in abi_names, "mint function should not be public"

    def test_allocation_sums_to_100(self):
        """Tokenomics percentages must sum to 100."""
        liquidity  = {liquidity_pct}
        community  = {community_pct}
        treasury   = {treasury_pct}
        team       = {team_pct}
        marketing  = {marketing_pct}
        assert liquidity + community + treasury + team + marketing == 100


class TestOwnership:
    def test_owner_is_deployer(self, token_contract, accounts):
        if token_contract is None:
            pytest.skip("Contract not deployed")
        assert token_contract.functions.owner().call() == accounts[0]

    def test_renounce_ownership(self, token_contract, accounts):
        """After renounce, owner should be zero address."""
        if token_contract is None:
            pytest.skip("Contract not deployed")
        # token_contract.functions.renounceOwnership().transact({{\'from\': accounts[0]}})
        # assert token_contract.functions.owner().call() == "0x0000000000000000000000000000000000000000"
        pytest.skip("Enable after local deployment")


class TestTransfers:
    def test_standard_transfer(self, token_contract, accounts):
        if token_contract is None:
            pytest.skip("Contract not deployed")
        # Test basic ERC-20 transfer
        pytest.skip("Enable after local deployment")

    def test_zero_address_transfer_fails(self, token_contract, accounts):
        if token_contract is None:
            pytest.skip("Contract not deployed")
        pytest.skip("Enable after local deployment")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''


class TokenBuilderAgent:
    NAME = "token_builder_agent"

    def run(self, concept: Dict, chain: str = "ethereum") -> AgentOutput:
        name = concept.get("token_name", "MyToken")
        ticker = concept.get("ticker", "MTK")
        name_clean = name.replace(" ", "").replace("-", "")

        tokenomics = {
            "total_supply": 1_000_000_000,
            "liquidity_pct": 40,
            "community_pct": 30,
            "treasury_pct": 10,
            "team_pct": 10,
            "marketing_pct": 10,
        }

        contract_code = ERC20_TEMPLATE.format(
            token_name=name,
            ticker=ticker,
            token_name_clean=name_clean,
            total_supply=tokenomics["total_supply"],
            liquidity_pct=tokenomics["liquidity_pct"],
            community_pct=tokenomics["community_pct"],
            treasury_pct=tokenomics["treasury_pct"],
            team_pct=tokenomics["team_pct"],
            marketing_pct=tokenomics["marketing_pct"],
            liquidity_pct_int=int(tokenomics["liquidity_pct"]),
            community_pct_int=int(tokenomics["community_pct"]),
            treasury_pct_int=int(tokenomics["treasury_pct"]),
            team_pct_int=int(tokenomics["team_pct"]),
            marketing_pct_int=int(tokenomics["marketing_pct"]),
        )

        deploy_script = DEPLOY_TEMPLATE.format(
            token_name=name,
            ticker=ticker,
            token_name_clean=name_clean,
            chain=chain,
            chain_upper=chain.upper(),
        )

        test_script = TEST_TEMPLATE.format(
            token_name=name,
            ticker=ticker,
            total_supply=tokenomics["total_supply"],
            liquidity_pct=tokenomics["liquidity_pct"],
            community_pct=tokenomics["community_pct"],
            treasury_pct=tokenomics["treasury_pct"],
            team_pct=tokenomics["team_pct"],
            marketing_pct=tokenomics["marketing_pct"],
        )

        audit_checklist = [
            "[ ] No overflow/underflow — using Solidity 0.8+ built-in checks",
            "[ ] No reentrancy vulnerability — no external calls in state-changing functions",
            "[ ] No centralization risk — owner renounced after deployment",
            "[ ] Liquidity locked — use Team.Finance or UniCrypt AFTER deployment",
            "[ ] Contract verified on Etherscan",
            "[ ] No hidden mint function",
            "[ ] No backdoor or pause function",
            "[ ] All wallets are multisig (Gnosis Safe recommended for team/treasury)",
            "[ ] Independent audit completed (at minimum: automated Slither scan)",
            "[ ] Tokenomics sum to exactly 100%",
        ]

        contract_spec = {
            "id": f"contract_{str(uuid.uuid4())[:8]}",
            "token_idea_id": concept.get("id"),
            "chain": chain,
            "standard": "ERC-20",
            "token_name": name,
            "ticker": ticker,
            "tokenomics": tokenomics,
            "contract_code": contract_code,
            "deploy_script": deploy_script,
            "test_script": test_script,
            "audit_checklist": audit_checklist,
            "deployment_status": "not_deployed",
            "mainnet_blocked": True,
            "created_at": datetime.utcnow().isoformat(),
            "warnings": [
                "DRAFT ONLY — do not deploy without audit and human approval",
                "All wallet addresses are placeholders — replace before deployment",
                f"Chain: {chain} — confirm correct RPC and chain ID",
            ],
        }

        existing = memory.load_contracts()
        existing.append(contract_spec)
        memory.save_contracts(existing)

        # Write .sol file
        sol_path = memory._path("").parent / "contracts" / f"{name_clean}.sol"
        sol_path.parent.mkdir(parents=True, exist_ok=True)
        sol_path.write_text(contract_code, encoding="utf-8")

        return AgentOutput(
            timestamp=datetime.utcnow(),
            agent_name=self.NAME,
            input_summary=f"Generated ERC-20 contract for {name} ({ticker}) on {chain}",
            output=contract_spec,
            score=None,
            next_recommended_action="Review contract code, run audit checklist, pass through security review before any deployment",
        )
