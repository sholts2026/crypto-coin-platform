// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title PepeJunior (PEPEJI) — Example ERC-20 Token
 * @dev Community meme token. Fixed supply. No minting after deployment.
 *
 * DRAFT — DO NOT deploy without:
 *   1. Independent security audit (minimum: Slither static analysis)
 *   2. Human founder review and sign-off
 *   3. Legal review in your jurisdiction
 *   4. All wallet addresses replaced with real multisigs
 *
 * Tokenomics:
 *   Total Supply: 1,000,000,000 PEPEJI
 *   Liquidity:    40% → lock on TeamFinance/UniCrypt after deployment
 *   Community:    30%
 *   Treasury:     10%
 *   Team:         10% → vesting recommended (separate vesting contract or trust)
 *   Marketing:    10%
 */
contract PepeJunior is ERC20, Ownable {

    uint256 public constant TOTAL_SUPPLY = 1_000_000_000 * 10 ** 18;

    uint256 public constant LIQUIDITY_PCT  = 40;
    uint256 public constant COMMUNITY_PCT  = 30;
    uint256 public constant TREASURY_PCT   = 10;
    uint256 public constant TEAM_PCT       = 10;
    uint256 public constant MARKETING_PCT  = 10;

    address public immutable liquidityWallet;
    address public immutable communityWallet;
    address public immutable treasuryWallet;
    address public immutable teamWallet;
    address public immutable marketingWallet;

    event AllocationMinted(address indexed wallet, string allocation, uint256 amount);

    constructor(
        address _liquidityWallet,
        address _communityWallet,
        address _treasuryWallet,
        address _teamWallet,
        address _marketingWallet
    )
        ERC20("Pepe Junior", "PEPEJI")
        Ownable(msg.sender)
    {
        require(_liquidityWallet  != address(0), "liquidity: zero address");
        require(_communityWallet  != address(0), "community: zero address");
        require(_treasuryWallet   != address(0), "treasury: zero address");
        require(_teamWallet       != address(0), "team: zero address");
        require(_marketingWallet  != address(0), "marketing: zero address");

        liquidityWallet  = _liquidityWallet;
        communityWallet  = _communityWallet;
        treasuryWallet   = _treasuryWallet;
        teamWallet       = _teamWallet;
        marketingWallet  = _marketingWallet;

        uint256 liq  = TOTAL_SUPPLY * LIQUIDITY_PCT  / 100;
        uint256 comm = TOTAL_SUPPLY * COMMUNITY_PCT  / 100;
        uint256 tres = TOTAL_SUPPLY * TREASURY_PCT   / 100;
        uint256 team = TOTAL_SUPPLY * TEAM_PCT       / 100;
        uint256 mktg = TOTAL_SUPPLY * MARKETING_PCT  / 100;

        // Dust from integer division goes to liquidity
        uint256 remainder = TOTAL_SUPPLY - liq - comm - tres - team - mktg;

        _mint(_liquidityWallet,  liq + remainder);
        _mint(_communityWallet,  comm);
        _mint(_treasuryWallet,   tres);
        _mint(_teamWallet,       team);
        _mint(_marketingWallet,  mktg);

        emit AllocationMinted(_liquidityWallet,  "liquidity",  liq + remainder);
        emit AllocationMinted(_communityWallet,  "community",  comm);
        emit AllocationMinted(_treasuryWallet,   "treasury",   tres);
        emit AllocationMinted(_teamWallet,       "team",       team);
        emit AllocationMinted(_marketingWallet,  "marketing",  mktg);

        // After verifying all wallets, call renounceOwnership() to make this
        // contract fully community-owned with no admin privileges.
    }

    // ── View helpers ──────────────────────────────────────────────────────────

    function getAllocations() external pure returns (
        uint256 liquidity, uint256 community, uint256 treasury,
        uint256 team, uint256 marketing
    ) {
        liquidity  = TOTAL_SUPPLY * LIQUIDITY_PCT  / 100;
        community  = TOTAL_SUPPLY * COMMUNITY_PCT  / 100;
        treasury   = TOTAL_SUPPLY * TREASURY_PCT   / 100;
        team       = TOTAL_SUPPLY * TEAM_PCT       / 100;
        marketing  = TOTAL_SUPPLY * MARKETING_PCT  / 100;
    }
}
