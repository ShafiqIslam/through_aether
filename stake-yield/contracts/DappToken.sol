// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract DappToken is ERC20 {
    constructor(uint256 initialSupplyInWei) ERC20("DAPP TOKEN", "DAPP") {
        _mint(msg.sender, initialSupplyInWei);
    }
}
