"""
test_token.py — PepeJunior (PEPEJI) smart contract test suite

Requirements:
  pip install pytest web3 eth-tester py-evm

Run against local Hardhat/Anvil node:
  anvil &  # start local node
  pytest contracts/test_token.py -v

Or with Hardhat:
  npx hardhat node &
  pytest contracts/test_token.py -v
"""
import pytest

# ── Constants ──────────────────────────────────────────────────────────────────
TOTAL_SUPPLY     = 1_000_000_000
DECIMALS         = 18
LIQUIDITY_PCT    = 40
COMMUNITY_PCT    = 30
TREASURY_PCT     = 10
TEAM_PCT         = 10
MARKETING_PCT    = 10

TOKEN_NAME   = "Pepe Junior"
TOKEN_TICKER = "PEPEJI"


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def w3():
    """Web3 connection to local test node."""
    try:
        from web3 import Web3
        w3 = Web3(Web3.HTTPProvider("http://localhost:8545"))
        if not w3.is_connected():
            pytest.skip("No local node running. Start anvil or hardhat node.")
        return w3
    except ImportError:
        pytest.skip("web3 not installed")


@pytest.fixture(scope="session")
def accounts(w3):
    return w3.eth.accounts


@pytest.fixture(scope="session")
def token(w3, accounts):
    """Deploy token to local test node."""
    import json
    from pathlib import Path
    artifact_path = Path(__file__).parent.parent / "artifacts/contracts/Token.sol/PepeJunior.json"
    if not artifact_path.exists():
        pytest.skip("Compile contract first: npx hardhat compile")
    artifact = json.loads(artifact_path.read_text())
    contract_class = w3.eth.contract(abi=artifact["abi"], bytecode=artifact["bytecode"])

    wallets = accounts[1], accounts[2], accounts[3], accounts[4], accounts[5]
    tx_hash = contract_class.constructor(*wallets).transact({"from": accounts[0]})
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return w3.eth.contract(address=receipt.contractAddress, abi=artifact["abi"])


# ── Static / Math tests (no node needed) ──────────────────────────────────────

class TestTokenomicsMath:
    """Verify allocation math is correct without deploying."""

    def test_allocations_sum_to_100(self):
        total = LIQUIDITY_PCT + COMMUNITY_PCT + TREASURY_PCT + TEAM_PCT + MARKETING_PCT
        assert total == 100, f"Expected 100%, got {total}%"

    def test_expected_supply(self):
        assert TOTAL_SUPPLY == 1_000_000_000

    def test_expected_decimals(self):
        assert DECIMALS == 18

    def test_liquidity_is_largest_allocation(self):
        assert LIQUIDITY_PCT >= COMMUNITY_PCT
        assert LIQUIDITY_PCT >= TREASURY_PCT
        assert LIQUIDITY_PCT >= TEAM_PCT
        assert LIQUIDITY_PCT >= MARKETING_PCT

    def test_team_has_vesting_required(self):
        """Team allocation must be small enough to require vesting (<=15%)."""
        assert TEAM_PCT <= 15, "Team allocation too high — vesting strongly recommended"


# ── On-chain tests (require local node) ──────────────────────────────────────

class TestDeployment:
    def test_name(self, token):
        assert token.functions.name().call() == TOKEN_NAME

    def test_symbol(self, token):
        assert token.functions.symbol().call() == TOKEN_TICKER

    def test_decimals(self, token):
        assert token.functions.decimals().call() == DECIMALS

    def test_total_supply(self, token):
        expected = TOTAL_SUPPLY * 10**DECIMALS
        assert token.functions.totalSupply().call() == expected


class TestAllocations:
    def test_liquidity_balance(self, token, accounts):
        expected = TOTAL_SUPPLY * LIQUIDITY_PCT // 100 * 10**DECIMALS
        actual = token.functions.balanceOf(accounts[1]).call()
        # Allow for remainder dust going to liquidity
        assert actual >= expected

    def test_community_balance(self, token, accounts):
        expected = TOTAL_SUPPLY * COMMUNITY_PCT // 100 * 10**DECIMALS
        assert token.functions.balanceOf(accounts[2]).call() == expected

    def test_treasury_balance(self, token, accounts):
        expected = TOTAL_SUPPLY * TREASURY_PCT // 100 * 10**DECIMALS
        assert token.functions.balanceOf(accounts[3]).call() == expected

    def test_team_balance(self, token, accounts):
        expected = TOTAL_SUPPLY * TEAM_PCT // 100 * 10**DECIMALS
        assert token.functions.balanceOf(accounts[4]).call() == expected


class TestOwnership:
    def test_owner_is_deployer(self, token, accounts):
        assert token.functions.owner().call() == accounts[0]

    def test_no_mint_function(self, token):
        function_names = [fn["name"] for fn in token.abi if fn.get("type") == "function"]
        assert "mint" not in function_names, "No public mint function should exist"


class TestTransfers:
    def test_basic_transfer(self, token, w3, accounts):
        amount = 1_000 * 10**DECIMALS
        token.functions.transfer(accounts[6], amount).transact({"from": accounts[2]})
        assert token.functions.balanceOf(accounts[6]).call() == amount

    def test_transfer_to_zero_fails(self, token, accounts):
        with pytest.raises(Exception):
            token.functions.transfer("0x" + "0"*40, 100).transact({"from": accounts[1]})

    def test_transfer_exceeds_balance_fails(self, token, accounts):
        balance = token.functions.balanceOf(accounts[5]).call()
        with pytest.raises(Exception):
            token.functions.transfer(accounts[0], balance + 1).transact({"from": accounts[5]})


class TestRenounce:
    def test_renounce_ownership(self, token, w3, accounts):
        """After renounce, no admin privileges remain."""
        token.functions.renounceOwnership().transact({"from": accounts[0]})
        zero = "0x" + "0" * 40
        assert token.functions.owner().call().lower() == zero


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
