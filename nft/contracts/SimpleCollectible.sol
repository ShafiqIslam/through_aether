// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";

contract SimpleCollectible is ERC721URIStorage {
    uint256 tokenCounter;

    constructor() ERC721("Dog", "DOG") {
        tokenCounter = 0;
    }

    function create(string memory tokenURI) public returns (uint256) {
        _mint(msg.sender, tokenCounter);
        _setTokenURI(tokenCounter, tokenURI);
        tokenCounter++;
        return tokenCounter - 1;
    }
}
