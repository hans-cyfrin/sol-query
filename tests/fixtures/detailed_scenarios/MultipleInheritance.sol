
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./IERC20.sol";
import "./Ownable.sol";

contract BaseA {
    uint256 public valueA;
    address public ownerA;
    
    constructor(uint256 _value) {
        valueA = _value;
        ownerA = msg.sender;
    }
    
    function functionA() public virtual returns (uint256) {
        return valueA * 2;
    }
}

contract BaseB {
    uint256 public valueB;
    mapping(address => uint256) public balances;
    
    constructor(uint256 _value) {
        valueB = _value;
    }
    
    function functionB() public virtual returns (uint256) {
        return valueB + 100;
    }
}

contract MultiInheritChild is BaseA, BaseB, Ownable {
    uint256 public childValue;
    
    constructor(uint256 _a, uint256 _b) BaseA(_a) BaseB(_b) Ownable() {
        childValue = _a + _b;
    }
    
    function functionA() public override returns (uint256) {
        return valueA * 3; // Different implementation
    }
    
    function functionB() public override returns (uint256) {
        return valueB + 200; // Different implementation  
    }
    
    function complexCalculation() public view returns (uint256) {
        return functionA() + functionB() + childValue;
    }
}
