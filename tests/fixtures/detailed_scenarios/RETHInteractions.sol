
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

interface IRocketTokenRETH {
    function getExchangeRate() external view returns (uint256);
    function getRethValue(uint256 _ethAmount) external view returns (uint256);
    function getEthValue(uint256 _rethAmount) external view returns (uint256);
}

interface IRocketStorageInterface {
    function getAddress(bytes32 _key) external view returns (address);
}

contract RETHVault {
    IERC20 public rethToken;
    IRocketTokenRETH public rocketRETH;
    IRocketStorageInterface public rocketStorage;
    
    uint256 public cachedExchangeRate;
    uint256 public lastUpdateTimestamp;
    uint256 public updateInterval = 3600; // 1 hour
    
    mapping(address => uint256) public userShares;
    mapping(address => uint256) public userLastRewardSnapshot;
    uint256 public totalShares;
    uint256 public accumulatedRewards;
    
    event RewardDistributed(uint256 amount, uint256 newRate);
    event ExchangeRateUpdated(uint256 oldRate, uint256 newRate);
    
    constructor(address _rethToken, address _rocketRETH, address _rocketStorage) {
        rethToken = IERC20(_rethToken);
        rocketRETH = IRocketTokenRETH(_rocketRETH);
        rocketStorage = IRocketStorageInterface(_rocketStorage);
        updateExchangeRate();
    }
    
    function deposit(uint256 rethAmount) external {
        require(rethToken.transfer(address(this), rethAmount), "Transfer failed");
        
        // Calculate shares based on current rate
        uint256 shares = calculateShares(rethAmount);
        
        // Update user rewards before changing shares
        updateUserRewards(msg.sender);
        
        userShares[msg.sender] += shares;
        totalShares += shares;
        
        userLastRewardSnapshot[msg.sender] = accumulatedRewards;
    }
    
    function withdraw(uint256 shares) external {
        require(userShares[msg.sender] >= shares, "Insufficient shares");
        
        // Update rewards first
        updateUserRewards(msg.sender);
        
        // Calculate rETH amount
        uint256 rethAmount = calculateRETHFromShares(shares);
        
        userShares[msg.sender] -= shares;
        totalShares -= shares;
        
        require(rethToken.transfer(msg.sender, rethAmount), "Transfer failed");
    }
    
    function calculateShares(uint256 rethAmount) public view returns (uint256) {
        // Use cached rate for efficiency
        if (shouldUpdateRate()) {
            return rethAmount * 1e18 / getCurrentExchangeRate();
        }
        return rethAmount * 1e18 / cachedExchangeRate;
    }
    
    function calculateRETHFromShares(uint256 shares) public view returns (uint256) {
        if (totalShares == 0) return 0;
        
        uint256 totalRETH = rethToken.balanceOf(address(this));
        return shares * totalRETH / totalShares;
    }
    
    function getCurrentExchangeRate() public view returns (uint256) {
        return rocketRETH.getExchangeRate();
    }
    
    function updateExchangeRate() public {
        uint256 oldRate = cachedExchangeRate;
        uint256 newRate = getCurrentExchangeRate();
        
        cachedExchangeRate = newRate;
        lastUpdateTimestamp = block.timestamp;
        
        emit ExchangeRateUpdated(oldRate, newRate);
        
        // Distribute rewards based on rate increase
        if (newRate > oldRate && totalShares > 0) {
            distributeRewards(newRate, oldRate);
        }
    }
    
    function shouldUpdateRate() public view returns (bool) {
        return block.timestamp >= lastUpdateTimestamp + updateInterval;
    }
    
    function distributeRewards(uint256 newRate, uint256 oldRate) internal {
        uint256 rateIncrease = newRate - oldRate;
        uint256 totalRETH = rethToken.balanceOf(address(this));
        
        // Calculate additional value from staking rewards
        uint256 rewardValue = totalRETH * rateIncrease / oldRate;
        accumulatedRewards += rewardValue;
        
        emit RewardDistributed(rewardValue, newRate);
    }
    
    function updateUserRewards(address user) internal {
        if (userShares[user] == 0) return;
        
        uint256 userRewardDebt = userLastRewardSnapshot[user];
        uint256 userShare = userShares[user] * 1e18 / totalShares;
        
        uint256 userReward = (accumulatedRewards - userRewardDebt) * userShare / 1e18;
        
        // This is a simplified reward distribution
        // In practice, you'd need more sophisticated accounting
        userLastRewardSnapshot[user] = accumulatedRewards;
    }
    
    function getUserFairShare(address user) external view returns (uint256 rethValue, uint256 ethValue) {
        if (totalShares == 0) return (0, 0);
        
        uint256 userRETH = calculateRETHFromShares(userShares[user]);
        rethValue = userRETH;
        ethValue = rocketRETH.getEthValue(userRETH);
    }
}
