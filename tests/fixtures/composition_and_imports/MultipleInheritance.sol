// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./interfaces/ILayerZeroReceiver.sol";
import { SafeMath } from "./libraries/SafeMath.sol";

contract BaseToken {
    string public name;
    uint256 public totalSupply;

    constructor(string memory _name) {
        name = _name;
    }

    function getInfo() public virtual returns (string memory) {
        return name;
    }
}

abstract contract Mintable {
    using SafeMath for uint256;

    uint256 public maxSupply;
    address public minter;

    modifier onlyMinter() {
        require(msg.sender == minter, "Not authorized");
        _;
    }

    function mint(address to, uint256 amount) public virtual onlyMinter {
        // Override in implementing contracts
    }
}

contract Ownable {
    address public owner;

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function transferOwnership(address newOwner) public onlyOwner {
        owner = newOwner;
    }
}

// Contract with multiple inheritance for testing
contract MultiInheritanceToken is BaseToken, Mintable, Ownable, ILayerZeroReceiver {
    using SafeMath for uint256;

    mapping(address => uint256) public balances;
    uint256 public crossChainMessages;

    constructor(string memory _name, uint256 _maxSupply)
        BaseToken(_name)
        Ownable()
    {
        maxSupply = _maxSupply;
        minter = msg.sender;
    }

    // Override from BaseToken
    function getInfo() public override returns (string memory) {
        return string(abi.encodePacked(name, " - Max: ", toString(maxSupply)));
    }

    // Override from Mintable
    function mint(address to, uint256 amount) public override onlyMinter {
        require(totalSupply.add(amount) <= maxSupply, "Exceeds max supply");

        totalSupply = totalSupply.add(amount);
        balances[to] = balances[to].add(amount);
    }

    // LayerZero implementation
    function lzReceive(
        uint16 _srcChainId,
        bytes calldata _srcAddress,
        uint64 _nonce,
        bytes calldata _payload
    ) external override {
        crossChainMessages = crossChainMessages.add(1);

        (address recipient, uint256 amount) = abi.decode(_payload, (address, uint256));
        mint(recipient, amount);
    }

    // Functions for testing different compositions
    function publicFunction() public pure returns (string memory) {
        return "public";
    }

    function externalFunction() external pure returns (string memory) {
        return "external";
    }

    function internalFunction() internal pure returns (string memory) {
        return "internal";
    }

    function privateFunction() private pure returns (string memory) {
        return "private";
    }

    // Function with external calls for testing
    function transferWithCall(address to, uint256 amount) external {
        require(balances[msg.sender] >= amount, "Insufficient balance");

        balances[msg.sender] = balances[msg.sender].sub(amount);
        balances[to] = balances[to].add(amount);

        // External call
        if (to.code.length > 0) {
            (bool success,) = to.call(abi.encodeWithSignature("onTokenReceived(address,uint256)", msg.sender, amount));
            require(success, "Transfer callback failed");
        }
    }

    // Helper function
    function toString(uint256 value) internal pure returns (string memory) {
        if (value == 0) return "0";

        uint256 temp = value;
        uint256 digits;
        while (temp != 0) {
            digits++;
            temp /= 10;
        }

        bytes memory buffer = new bytes(digits);
        while (value != 0) {
            digits -= 1;
            buffer[digits] = bytes1(uint8(48 + uint256(value % 10)));
            value /= 10;
        }

        return string(buffer);
    }
}
