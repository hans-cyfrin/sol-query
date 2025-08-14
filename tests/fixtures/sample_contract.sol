// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IERC20 {
    function totalSupply() external view returns (uint256);
    function balanceOf(address account) external view returns (uint256);
    function transfer(address to, uint256 amount) external returns (bool);
    function allowance(address owner, address spender) external view returns (uint256);
    function approve(address spender, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
}

contract Token is IERC20 {
    mapping(address => uint256) private _balances;
    mapping(address => mapping(address => uint256)) private _allowances;

    uint256 private _totalSupply;
    string private _name;
    string private _symbol;
    uint8 private _decimals;

    address public owner;

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);

    error InsufficientBalance(uint256 available, uint256 required);
    error InsufficientAllowance(uint256 available, uint256 required);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not the owner");
        _;
    }

    modifier validAddress(address addr) {
        require(addr != address(0), "Invalid address");
        _;
    }

    constructor(
        string memory name_,
        string memory symbol_,
        uint8 decimals_,
        uint256 totalSupply_
    ) {
        _name = name_;
        _symbol = symbol_;
        _decimals = decimals_;
        _totalSupply = totalSupply_;
        _balances[msg.sender] = totalSupply_;
        owner = msg.sender;
        emit Transfer(address(0), msg.sender, totalSupply_);
    }

    function name() public view returns (string memory) {
        return _name;
    }

    function symbol() public view returns (string memory) {
        return _symbol;
    }

    function decimals() public view returns (uint8) {
        return _decimals;
    }

    function totalSupply() public view override returns (uint256) {
        return _totalSupply;
    }

    function balanceOf(address account) public view override returns (uint256) {
        return _balances[account];
    }

    function transfer(address to, uint256 amount) public override validAddress(to) returns (bool) {
        address owner = msg.sender;
        _transfer(owner, to, amount);
        return true;
    }

    function allowance(address owner, address spender) public view override returns (uint256) {
        return _allowances[owner][spender];
    }

    function approve(address spender, uint256 amount) public override validAddress(spender) returns (bool) {
        address owner = msg.sender;
        _approve(owner, spender, amount);
        return true;
    }

    function transferFrom(address from, address to, uint256 amount) public override validAddress(to) returns (bool) {
        address spender = msg.sender;
        _spendAllowance(from, spender, amount);
        _transfer(from, to, amount);
        return true;
    }

    function mint(address to, uint256 amount) public onlyOwner validAddress(to) {
        _totalSupply += amount;
        _balances[to] += amount;
        emit Transfer(address(0), to, amount);
    }

    function burn(uint256 amount) public {
        address owner = msg.sender;
        uint256 accountBalance = _balances[owner];
        if (accountBalance < amount) {
            revert InsufficientBalance(accountBalance, amount);
        }
        _balances[owner] = accountBalance - amount;
        _totalSupply -= amount;
        emit Transfer(owner, address(0), amount);
    }

    function transferOwnership(address newOwner) public onlyOwner validAddress(newOwner) {
        address oldOwner = owner;
        owner = newOwner;
        emit OwnershipTransferred(oldOwner, newOwner);
    }

    function _transfer(address from, address to, uint256 amount) internal {
        uint256 fromBalance = _balances[from];
        if (fromBalance < amount) {
            revert InsufficientBalance(fromBalance, amount);
        }
        _balances[from] = fromBalance - amount;
        _balances[to] += amount;
        emit Transfer(from, to, amount);
    }

    function _approve(address owner, address spender, uint256 amount) internal {
        _allowances[owner][spender] = amount;
        emit Approval(owner, spender, amount);
    }

    function _spendAllowance(address owner, address spender, uint256 amount) internal {
        uint256 currentAllowance = allowance(owner, spender);
        if (currentAllowance != type(uint256).max) {
            if (currentAllowance < amount) {
                revert InsufficientAllowance(currentAllowance, amount);
            }
            _approve(owner, spender, currentAllowance - amount);
        }
    }
}

contract ComplexLogic {
    uint256[] public numbers;
    mapping(address => uint256[]) public userNumbers;
    mapping(address => bool) public isActive;

    struct UserData {
        uint256 balance;
        uint256 lastUpdate;
        bool isVip;
    }

    mapping(address => UserData) public userData;

    event NumberAdded(uint256 number);
    event BatchProcessed(uint256 count);
    event UserStatusChanged(address user, bool status);

    // Function with for loop and conditionals
    function processNumbers(uint256[] memory inputNumbers) public {
        require(inputNumbers.length > 0, "Empty array");

        uint256 sum = 0;
        uint256 evenCount = 0;

        // For loop with conditional logic
        for (uint256 i = 0; i < inputNumbers.length; i++) {
            uint256 num = inputNumbers[i];

            // Conditional statements
            if (num > 0) {
                sum += num;
                numbers.push(num);
                emit NumberAdded(num);

                // Nested conditional
                if (num % 2 == 0) {
                    evenCount++;
                }
            } else {
                // Handle zero or negative numbers
                continue;
            }
        }

        // Assignment statements
        userData[msg.sender].balance = sum;
        userData[msg.sender].lastUpdate = block.timestamp;

        emit BatchProcessed(inputNumbers.length);
    }

    // Function with while loop and complex conditionals
    function findFirstLargeNumber(uint256 threshold) public view returns (uint256, bool) {
        uint256 index = 0;

        // While loop
        while (index < numbers.length) {
            uint256 current = numbers[index];

            // Complex conditional with logical operators
            if (current > threshold && current < threshold * 10) {
                return (current, true);
            } else if (current == threshold) {
                // Exact match handling
                return (current, true);
            }

            index++;
        }

        return (0, false);
    }

    // Function with do-while loop (simulated with while)
    function calculateFactorial(uint256 n) public pure returns (uint256) {
        require(n <= 20, "Number too large");

        if (n == 0 || n == 1) {
            return 1;
        }

        uint256 result = 1;
        uint256 counter = n;

        // Simulated do-while loop
        while (counter > 0) {
            result *= counter;
            counter--;
        }

        return result;
    }

    // Function with multiple assignment types
    function updateUserData(address user, uint256 newBalance, bool vipStatus) public {
        require(user != address(0), "Invalid address");

        // Direct assignment
        userData[user].balance = newBalance;

        // Compound assignment operators
        userData[user].balance += 100; // Bonus
        userData[user].lastUpdate = block.timestamp;

        // Conditional assignment
        userData[user].isVip = vipStatus ? true : false;

        // Array assignment
        userNumbers[user].push(newBalance);

        // Boolean assignment with complex logic
        isActive[user] = (newBalance > 1000 && vipStatus) || userData[user].balance > 5000;

        emit UserStatusChanged(user, isActive[user]);
    }

    // Function with nested loops and conditionals
    function analyzeUserPatterns() public view returns (uint256, uint256) {
        uint256 totalActiveUsers = 0;
        uint256 totalVipUsers = 0;

        // Iterate through numbers array to simulate user analysis
        for (uint256 i = 0; i < numbers.length; i++) {
            uint256 userId = numbers[i] % 1000; // Simulate user ID

            // Nested loop simulation
            for (uint256 j = 0; j < 3; j++) {
                uint256 checkValue = userId + j;

                // Complex nested conditionals
                if (checkValue > 100) {
                    if (checkValue % 2 == 0) {
                        totalActiveUsers++;
                    } else if (checkValue % 3 == 0) {
                        totalVipUsers++;
                    }
                }
            }
        }

        return (totalActiveUsers, totalVipUsers);
    }

    // Function with try-catch and error handling
    function safeDivision(uint256 a, uint256 b) public pure returns (uint256, bool) {
        // Manual error handling (Solidity doesn't have traditional try-catch for pure functions)
        if (b == 0) {
            return (0, false);
        }

        uint256 result = a / b;
        return (result, true);
    }

    // Function with switch-like behavior using if-else chain
    function getStatusMessage(uint256 code) public pure returns (string memory) {
        // Switch-like conditional chain
        if (code == 1) {
            return "Active";
        } else if (code == 2) {
            return "Pending";
        } else if (code == 3) {
            return "Suspended";
        } else if (code == 4) {
            return "Terminated";
        } else {
            return "Unknown";
        }
    }

    // Function with early returns and multiple exit points
    function validateAndProcess(uint256 value, bool shouldProcess) public returns (bool) {
        // Early return conditions
        if (value == 0) {
            return false;
        }

        if (!shouldProcess) {
            return false;
        }

        if (value > 1000000) {
            // Value too large
            return false;
        }

        // Process the value
        numbers.push(value);
        userData[msg.sender].balance += value;

        // Conditional processing
        if (value > 10000) {
            userData[msg.sender].isVip = true;
            emit UserStatusChanged(msg.sender, true);
        }

        return true;
    }

    // Function with assembly block (low-level operations)
    function getCodeSize(address addr) public view returns (uint256 size) {
        assembly {
            size := extcodesize(addr)
        }
    }

    // Function demonstrating various expression types
    function complexCalculations(uint256 x, uint256 y) public pure returns (uint256) {
        // Arithmetic expressions
        uint256 sum = x + y;
        uint256 product = x * y;
        uint256 difference = x > y ? x - y : y - x;

        // Bitwise operations
        uint256 bitwiseAnd = x & y;
        uint256 bitwiseOr = x | y;
        uint256 bitwiseXor = x ^ y;

        // Shift operations
        uint256 leftShift = x << 1;
        uint256 rightShift = x >> 1;

        // Complex expression combining multiple operations
        uint256 result = (sum * product) / (difference + 1) + bitwiseAnd - bitwiseOr + bitwiseXor;
        result = result + leftShift - rightShift;

        return result;
    }
}

library SafeMath {
    function add(uint256 a, uint256 b) internal pure returns (uint256) {
        return a + b;
    }

    function sub(uint256 a, uint256 b) internal pure returns (uint256) {
        require(b <= a, "SafeMath: subtraction overflow");
        return a - b;
    }

    function mul(uint256 a, uint256 b) internal pure returns (uint256) {
        return a * b;
    }

    function div(uint256 a, uint256 b) internal pure returns (uint256) {
        require(b > 0, "SafeMath: division by zero");
        return a / b;
    }

    // Function with loop for demonstration
    function sumArray(uint256[] memory arr) internal pure returns (uint256) {
        uint256 total = 0;

        // For loop in library function
        for (uint256 i = 0; i < arr.length; i++) {
            total += arr[i];
        }

        return total;
    }

    // Function with conditional logic
    function max(uint256 a, uint256 b) internal pure returns (uint256) {
        return a >= b ? a : b;
    }
}