// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./SimpleStorage.sol";

contract SimpleStorageV2 is SimpleStorage {
    function increment() public {
        value = value + 1;
        emit ValueChanged(value);
    }
}
