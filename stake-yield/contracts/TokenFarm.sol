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

    function stake(address _token, uint256 _amount) public {
        require(_amount > 0, "Amount must be greater than 0.");
        require(isTokenAllowed(_token), "Token is not allowed.");

        IERC20(_token).transferFrom(msg.sender, address(this), _amount);

        stakesByToken[_token][msg.sender] += _amount;

        uint256 _tokenBalance = getStakeholderTokenBalance(msg.sender, _token);
        stakesByHolder[msg.sender].set(_token, _tokenBalance + _amount);
        stakeholders.add(msg.sender);
    }

    function unstake(address _token) public {
        uint256 _tokenBalance = getStakeholderTokenBalance(msg.sender, _token);
        require(_tokenBalance > 0, "Balance must be greater than 0.");

        IERC20(_token).transfer(msg.sender, _tokenBalance);

        stakesByToken[_token][msg.sender] = 0;
        stakesByHolder[msg.sender].remove(_token);
        if (!doesStakeholderHaveAnyToken(msg.sender)) {
            stakeholders.remove(msg.sender);
        }
    }

    function getStakeholderTokenBalance(address _stakeholder, address _token)
        public
        view
        returns (uint256)
    {
        return
            stakesByHolder[_stakeholder].contains(_token)
                ? stakesByHolder[_stakeholder].get(_token)
                : 0;
    }

    function reward() public onlyOwner {
        for (uint256 i = 0; i < stakeholders.length(); i++) {
            dappToken.transfer(stakeholders.at(i), 0);
        }
    }

    function getStakeholderTotalBalance(address _holder)
        public
        view
        returns (uint256)
    {
        require(doesStakeholderHaveAnyToken(_holder), "Unknown stakeholder.");

        uint256 balance = 0;
        address _tokenAddress;
        uint256 _tokenBalance;
        for (uint256 i = 0; i < stakesByHolder[_holder].length(); i++) {
            (_tokenAddress, _tokenBalance) = stakesByHolder[_holder].at(i);
            balance +=
                (getTokenValueWRTWei(_tokenAddress) * _tokenBalance) /
                (10**18);
        }
        return balance;
    }

    function doesStakeholderHaveAnyToken(address _stakeholder)
        public
        view
        returns (bool)
    {
        return stakesByHolder[_stakeholder].length() > 0;
    }

    function getTokenValueWRTWei(address _token) public view returns (uint256) {
        AggregatorV3Interface _priceFeed = AggregatorV3Interface(
            tokenPriceFeeds[_token]
        );
        (, int256 price, , , ) = _priceFeed.latestRoundData();
        return uint256(price) * (10**(18 - _priceFeed.decimals()));
    }
}
