// SPDX-License-Identifier: UNLICENSED

pragma solidity ^0.6.0;

import './InheritedStorage.sol';

contract StorageFactory {

    InheritedStorage[] stores;

    function createSimpleStorage() public {
        stores.push(new InheritedStorage());
    }

    function store(uint256 index, uint256 value) public {
        stores[index].store(value);
    }

    function retrieve(uint256 index) view public returns (uint256) {
        return InheritedStorage(address(stores[index])).retrieve();
    }
}