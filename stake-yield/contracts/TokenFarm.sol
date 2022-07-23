// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/structs/EnumerableSet.sol";
import "@openzeppelin/contracts/utils/structs/EnumerableMap.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract TokenFarm is Ownable {
    using EnumerableSet for EnumerableSet.AddressSet;
    using EnumerableMap for EnumerableMap.AddressToUintMap;

    EnumerableSet.AddressSet internal allowedTokens;
    mapping(address => address) internal tokenPriceFeeds;
    mapping(address => mapping(address => uint256)) internal stakesByToken;
    mapping(address => EnumerableMap.AddressToUintMap) internal stakesByHolder;
    EnumerableSet.AddressSet internal stakeholders;
    IERC20 internal dappToken;

    constructor(address _dappTokenAddress, address _dappTokenPriceFeed) {
        dappToken = IERC20(_dappTokenAddress);
        addAllowedToken(_dappTokenAddress, _dappTokenPriceFeed);
    }

    function addAllowedToken(address _token, address _priceFeed)
        public
        onlyOwner
    {
        allowedTokens.add(_token);
        tokenPriceFeeds[_token] = _priceFeed;
    }

    function isTokenAllowed(address _token) public view returns (bool) {
        return allowedTokens.contains(_token);
    }

    function getTokenUnitValue(address _token) public view returns (uint256) {
        AggregatorV3Interface _priceFeed = AggregatorV3Interface(
            tokenPriceFeeds[_token]
        );
        (, int256 price, , , ) = _priceFeed.latestRoundData();
        return uint256(price) * (10**(18 - _priceFeed.decimals()));
    }

    function stake(address _token, uint256 _amount) public {
        require(_amount > 0, "Amount must be greater than 0.");
        require(isTokenAllowed(_token), "Token is not allowed.");

        IERC20(_token).transferFrom(msg.sender, address(this), _amount);

        stakesByToken[_token][msg.sender] += _amount;

        uint256 _tokenBalance = isStakeholder(msg.sender) ? getStakeholderTokenBalance(msg.sender, _token) : 0;
        stakesByHolder[msg.sender].set(_token, _tokenBalance + _amount);
        stakeholders.add(msg.sender);
    }

    function getTotalStakedToken(address _token) public view returns (uint256) {
        uint256 result = 0;
        for (uint256 i = 0; i < stakeholders.length(); i++) {
            result += stakesByToken[_token][stakeholders.at(i)];
        }
        return result;
    }

    function isStakeholder(address _user) public view returns (bool) {
        return stakeholders.contains(_user);
    }

    function unstake(address _token) public {
        require(isStakeholder(msg.sender), "Unknown stakeholder.");

        uint256 _tokenBalance = getStakeholderTokenBalance(msg.sender, _token);
        require(_tokenBalance > 0, "Balance must be greater than 0.");

        IERC20(_token).transfer(msg.sender, _tokenBalance);

        stakesByToken[_token][msg.sender] = 0;
        stakesByHolder[msg.sender].remove(_token);
        if (stakesByHolder[msg.sender].length() == 0) {
            stakeholders.remove(msg.sender);
        }
    }

    function getStakeholderTokenBalance(address _holder, address _token)
        public
        view
        returns (uint256)
    {
        require(isStakeholder(_holder), "Unknown stakeholder.");

        return stakesByHolder[_holder].contains(_token) 
            ? stakesByHolder[_holder].get(_token) 
            : 0;
    }

    function getStakeholderTokenValue(address _stakeholder, address _token)
        public
        view
        returns (uint256)
    {
        uint256 _tokenBalance = getStakeholderTokenBalance(_stakeholder, _token);
        return (getTokenUnitValue(_token) * _tokenBalance) / (10**18);
    }

    function reward() public onlyOwner {
        for (uint256 i = 0; i < stakeholders.length(); i++) {
            rewardStakeholder(stakeholders.at(i));
        }
    }

    function rewardStakeholder(address _stakeholder) public onlyOwner {
        dappToken.transferFrom(msg.sender, _stakeholder, getStakeholderTotalValue(_stakeholder) / 10);
    }

    function getStakeholderTotalValue(address _holder)
        public
        view
        returns (uint256)
    {
        require(isStakeholder(_holder), "Unknown stakeholder.");

        uint256 balance = 0;
        address _token;
        for (uint256 i = 0; i < stakesByHolder[_holder].length(); i++) {
            (_token, ) = stakesByHolder[_holder].at(i);
            balance += getStakeholderTokenValue(_holder, _token);
        }
        return balance;
    }
}
