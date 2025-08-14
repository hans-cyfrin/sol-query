// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title Simple contract with no imports for comparison testing
 */
contract SimpleContract {
    uint256 public value;
    address public owner;

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    constructor(uint256 _value) {
        value = _value;
        owner = msg.sender;
    }

    // Pure function for testing
    function pureFunction(uint256 a, uint256 b) public pure returns (uint256) {
        return a + b;
    }

    // View function for testing
    function viewFunction() public view returns (uint256) {
        return value;
    }

    // State-changing function for testing
    function setValue(uint256 _value) public onlyOwner {
        value = _value;
    }

    // Payable function for testing
    function deposit() public payable {
        // Simple deposit function
    }

    // Internal function for testing
    function internalHelper() internal pure returns (bool) {
        return true;
    }

    // Private function for testing
    function privateHelper() private pure returns (bool) {
        return false;
    }
}
