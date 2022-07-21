// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract MockFAU is ERC20 {
    constructor(uint256 initialSupplyInWei) ERC20("Mock FAU", "FAU") {
        _mint(msg.sender, initialSupplyInWei);
    }
}
