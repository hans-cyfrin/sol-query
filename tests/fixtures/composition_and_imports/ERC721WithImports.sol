// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "./interfaces/ILayerZeroReceiver.sol";
import { SafeMath } from "./libraries/SafeMath.sol";

/**
 * @title ERC721 contract with various imports for testing composition and import analysis
 */
contract ERC721WithImports is ERC721, Ownable, ReentrancyGuard, ILayerZeroReceiver {
    using SafeMath for uint256;

    uint256 public nextTokenId = 1;
    uint256 public maxSupply = 10000;
    uint256 public price = 0.1 ether;

    mapping(address => uint256) public balances;
    mapping(uint256 => bool) public lockedTokens;

    event TokenMinted(address indexed to, uint256 indexed tokenId);
    event PriceUpdated(uint256 newPrice);

    modifier onlyValidTokenId(uint256 tokenId) {
        require(_exists(tokenId), "Token does not exist");
        _;
    }

    constructor() ERC721("TestNFT", "TNFT") Ownable() {}

    // External payable function with external calls and asset transfers
    function mint(address to) external payable nonReentrant {
        require(msg.value >= price, "Insufficient payment");
        require(nextTokenId <= maxSupply, "Max supply reached");

        uint256 tokenId = nextTokenId;
        nextTokenId = nextTokenId.add(1);

        _safeMint(to, tokenId);
        balances[to] = balances[to].add(1);

        emit TokenMinted(to, tokenId);

        // Asset transfer - refund excess
        if (msg.value > price) {
            uint256 refund = msg.value.sub(price);
            payable(msg.sender).transfer(refund);
        }
    }

    // Function with multiple parameter types for boundary testing
    function complexCalculation(uint256 a, int256 b, uint8 c) external pure returns (uint256) {
        require(a <= type(uint256).max / 2, "Overflow risk");
        require(b >= type(int256).min / 2, "Underflow risk");

        uint256 result = a.mul(uint256(b > 0 ? b : 1));
        return result.add(uint256(c));
    }

    // Function without external calls for comparison
    function internalOnlyFunction() public view returns (uint256) {
        return balances[msg.sender];
    }

    // Function with external calls but no reentrancy guard (vulnerable)
    function vulnerableTransfer(address to, uint256 tokenId) external {
        require(ownerOf(tokenId) == msg.sender, "Not owner");

        // External call before state update - vulnerable!
        IERC721(address(this)).safeTransferFrom(msg.sender, to, tokenId);

        // State update after external call
        balances[msg.sender] = balances[msg.sender].sub(1);
        balances[to] = balances[to].add(1);
    }

    // SafeMath usage for overflow testing
    function safeArithmetic(uint256 x, uint256 y) external pure returns (uint256) {
        return x.add(y).mul(2).sub(1);
    }

    // Unsafe arithmetic for comparison
    function unsafeArithmetic(uint256 x, uint256 y) external pure returns (uint256) {
        return (x + y) * 2 - 1; // No SafeMath
    }

    // LayerZero receiver implementation
    function lzReceive(
        uint16 _srcChainId,
        bytes calldata _srcAddress,
        uint64 _nonce,
        bytes calldata _payload
    ) external override {
        // Cross-chain message processing
        (address recipient, uint256 tokenId) = abi.decode(_payload, (address, uint256));

        // This could fail and block subsequent messages
        require(recipient != address(0), "Invalid recipient");
        require(!lockedTokens[tokenId], "Token is locked");

        // Mint NFT from cross-chain message
        _safeMint(recipient, tokenId);
        lockedTokens[tokenId] = true;
    }

    // Function with time operations for timeout analysis
    function timeBasedOperation() external view returns (bool) {
        uint256 timestamp = block.timestamp;
        uint256 deadline = timestamp + 3600; // 1 hour

        return deadline > timestamp;
    }

    // Access control function
    function updatePrice(uint256 newPrice) external onlyOwner {
        price = newPrice;
        emit PriceUpdated(newPrice);
    }

    // Override function for inheritance testing
    function supportsInterface(bytes4 interfaceId) public view virtual override returns (bool) {
        return super.supportsInterface(interfaceId);
    }
}
