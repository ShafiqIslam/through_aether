// SPDX-License-Identifier: UNLICENSED

pragma solidity ^0.6.0;

import './SimpleStorage.sol';

contract InheritedStorage is SimpleStorage {

    function retrieve() public view override(SimpleStorage) returns(uint256) {
        return multiplyByTwo(someValue);
    }
}