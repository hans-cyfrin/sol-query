
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface ILayerZeroEndpoint {
    function send(uint16 _dstChainId, bytes calldata _destination, bytes calldata _payload, address payable _refundAddress, address _zroPaymentAddress, bytes calldata _adapterParams) external payable;
}

interface ILayerZeroReceiver {
    function lzReceive(uint16 _srcChainId, bytes calldata _srcAddress, uint64 _nonce, bytes calldata _payload) external;
}

contract LayerZeroApp is ILayerZeroReceiver {
    ILayerZeroEndpoint public endpoint;
    mapping(uint16 => bytes) public remoteAddresses;
    mapping(bytes32 => bool) public processedMessages;
    
    uint256 public messageTimeout = 3600; // 1 hour timeout
    bool public circuitBreakerEnabled = false;
    
    modifier onlyEndpoint() {
        require(msg.sender == address(endpoint), "Only endpoint");
        _;
    }
    
    modifier circuitBreaker() {
        require(!circuitBreakerEnabled, "Circuit breaker active");
        _;
    }
    
    constructor(address _endpoint) {
        endpoint = ILayerZeroEndpoint(_endpoint);
    }
    
    function lzReceive(uint16 _srcChainId, bytes calldata _srcAddress, uint64 _nonce, bytes calldata _payload) 
        external override onlyEndpoint circuitBreaker {
        
        bytes32 messageId = keccak256(abi.encodePacked(_srcChainId, _srcAddress, _nonce));
        
        // Check for replay
        require(!processedMessages[messageId], "Message already processed");
        
        // Process message - this could fail and block subsequent messages
        require(processMessage(_payload), "Message processing failed");
        
        processedMessages[messageId] = true;
    }
    
    function processMessage(bytes calldata _payload) internal returns (bool) {
        // Decode and process message
        // This might call external contracts or modify state
        (address recipient, uint256 amount) = abi.decode(_payload, (address, uint256));
        
        // External call that could fail
        return IERC20(recipient).transfer(msg.sender, amount);
    }
    
    function retryMessage(bytes32 messageId, bytes calldata _payload) external {
        require(!processedMessages[messageId], "Already processed");
        require(processMessage(_payload), "Retry failed");
        processedMessages[messageId] = true;
    }
    
    function emergencyStop() external {
        circuitBreakerEnabled = true;
    }
}
