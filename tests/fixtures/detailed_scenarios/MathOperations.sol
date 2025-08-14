
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./SafeMath.sol";

contract MathOperations {
    using SafeMath for uint256;
    
    uint256 public constant MAX_UINT = type(uint256).max;
    uint256 public totalSupply;
    mapping(address => uint256) public balances;
    
    function unsafeAdd(uint256 a, uint256 b) public pure returns (uint256) {
        return a + b; // Vulnerable to overflow
    }
    
    function safeAdd(uint256 a, uint256 b) public pure returns (uint256) {
        return a.add(b); // Uses SafeMath
    }
    
    function complexCalculation(uint256 principal, uint256 rate, uint256 time) 
        public pure returns (uint256) {
        // Complex calculation that could overflow
        uint256 interest = principal * rate * time / 10000;
        return principal + interest;
    }
    
    function safeComplexCalculation(uint256 principal, uint256 rate, uint256 time) 
        public pure returns (uint256) {
        // Safe version with proper checks
        require(principal <= MAX_UINT / rate, "Overflow risk");
        require(rate <= MAX_UINT / time, "Overflow risk");
        
        uint256 interest = principal.mul(rate).mul(time).div(10000);
        return principal.add(interest);
    }
    
    function transferWithMath(address to, uint256 amount, uint256 fee) external {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        
        // Vulnerable: no check for underflow
        uint256 netAmount = amount - fee;
        balances[msg.sender] -= amount;
        balances[to] += netAmount;
        
        // Fee goes to contract
        totalSupply += fee;
    }
    
    function boundaryValueTest(uint256 value) public pure returns (uint256) {
        // Test with boundary values
        if (value == 0) return 1;
        if (value == MAX_UINT) return MAX_UINT - 1;
        return value * 2;
    }
}
