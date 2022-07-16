// SPDX-License-Identifier: MIT
pragma solidity ^0.8.7;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract FundMe {
    AggregatorV3Interface internal priceFeed;

    mapping(address => uint256) public funded;
    address[] participants;

    address owner;

    constructor(address priceFeedAddress) {
        priceFeed = AggregatorV3Interface(priceFeedAddress);
        owner = msg.sender;
    }

    function fund() public payable {
        require(isEnoughFund(msg.value), "You have to give more!");
        if (funded[msg.sender] == 0) {
            participants.push(msg.sender);
        }

        funded[msg.sender] += msg.value;
    }

    modifier ownerOnly() {
        require(msg.sender == owner, "You are not owner!");
        _;
    }

    function withdraw() public payable ownerOnly {
        payable(msg.sender).transfer(address(this).balance);

        for (uint256 i = 0; i < participants.length; i++) {
            funded[participants[i]] = 0;
        }

        participants = new address[](0);
    }

    function getMinimumUsdWRTWei() internal view returns (uint256) {
        return 1 * (10**18);
    }

    function getEntranceFee() public view returns (uint256) {
        return (getMinimumUsdWRTWei() * (10**18)) / getCurrentRateWRTWei();
    }

    function isEnoughFund(uint256 _wei) internal view returns (bool) {
        return getUsdWRTWei(_wei) >= getMinimumUsdWRTWei();
    }

    function getUsdWRTWei(uint256 _wei) internal view returns (uint256) {
        return (getCurrentRateWRTWei() * _wei) / (10**18);
    }

    /**
     * 18 decimal
     * If 1 ETH = 1224.10309161 USD
     * This function returns 1224103091610000000000
     */
    function getCurrentRateWRTWei() internal view returns (uint256) {
        return getCurrentRateWRTGwei() * (10**10);
    }

    /**
     * 8 decimal
     * If 1 ETH = 1224.10309161 USD
     * This function returns 122410309161
     */
    function getCurrentRateWRTGwei() internal view returns (uint256) {
        (, int256 price, , , ) = priceFeed.latestRoundData();
        return uint256(price);
    }
}
