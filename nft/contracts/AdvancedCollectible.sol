// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@chainlink/contracts/src/v0.8/interfaces/VRFCoordinatorV2Interface.sol";
import "@chainlink/contracts/src/v0.8/VRFConsumerBaseV2.sol";

contract AdvancedCollectible is ERC721URIStorage, VRFConsumerBaseV2 {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIds;

    enum Breed {
        PUG,
        SHIBA_INU,
        ST_BERNARD
    }
    mapping(uint256 => Breed) internal tokens;
    mapping(uint256 => address) internal requestSenders;

    VRFCoordinatorV2Interface internal vrf;
    bytes32 internal vrfKey;
    uint64 internal sId;

    event RequestedCollectible(uint256 requestId, address sender);
    event BreedAssigned(uint256 tokenId, Breed breed);

    constructor(
        address _vrfCoordinatorAddress,
        bytes32 _keyHash,
        uint64 _chainlinkSubscriptionId
    ) VRFConsumerBaseV2(_vrfCoordinatorAddress) ERC721("Dog", "DOG") {
        vrf = VRFCoordinatorV2Interface(_vrfCoordinatorAddress);
        vrfKey = _keyHash;
        sId = _chainlinkSubscriptionId;
    }

    function create() public returns (uint256) {
        uint256 requestId = vrf.requestRandomWords(vrfKey, sId, 3, 100000, 1);
        requestSenders[requestId] = msg.sender;
        emit RequestedCollectible(requestId, msg.sender);
    }

    function fulfillRandomWords(uint256 requestId, uint256[] memory randomWords)
        internal
        override
    {
        uint256 newItemId = _tokenIds.current();

        Breed breed = Breed(randomWords[0] % 3);
        tokens[newItemId] = breed;
        emit BreedAssigned(newItemId, breed);

        _mint(requestSenders[requestId], newItemId);

        _tokenIds.increment();
    }

    function setTokenURI(uint256 tokenId, string memory _tokenURI) public {
        require(
            _isApprovedOrOwner(_msgSender(), tokenId),
            "ERC721: transfer caller is not owner nor approved"
        );
        _setTokenURI(tokenId, _tokenURI);
    }

    function getTokenCount() public view returns (uint256) {
        return _tokenIds.current();
    }

    function getBreedNameOf(uint256 _tokenId)
        public
        view
        returns (string memory)
    {
        Breed breed = tokens[_tokenId];
        if (breed == Breed.PUG) return "PUG";
        else if (breed == Breed.SHIBA_INU) return "SHIBA_INU";
        else return "ST_BERNARD";
    }
}
