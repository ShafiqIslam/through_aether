// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./MockV3Aggregator.sol";

contract MockV3AggregatorETHUSD is MockV3Aggregator {
    constructor(uint8 _decimals, int256 _initialAnswer) MockV3Aggregator(_decimals, _initialAnswer) {
    }
}