// SPDX-License-Identifier: MIT
pragma solidity ^0.8.12;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@chainlink/contracts/src/v0.8/interfaces/VRFCoordinatorV2Interface.sol";
import "@chainlink/contracts/src/v0.8/VRFConsumerBaseV2.sol";

contract Lottery is Ownable, VRFConsumerBaseV2 {
    AggregatorV3Interface internal priceFeed;
    VRFCoordinatorV2Interface internal vrfCoordinator;

    uint256 internal constant entryFeeInUSD = 10;
    enum STATUS {
        OPEN,
        CLOSED,
        CALCULATING
    }
    STATUS internal status;
    address payable[] public players;
    address payable public winner;
    bytes32 internal vrfKeyHash;
    uint64 internal chainlinkSubscriptionId;

    event RandomNumberRequested(uint256 requestId);

    constructor(
        address priceFeedAddress,
        address _vrfCoordinatorAddress,
        bytes32 _keyHash,
        uint64 _chainlinkSubscriptionId
    ) VRFConsumerBaseV2(_vrfCoordinatorAddress) {
        priceFeed = AggregatorV3Interface(priceFeedAddress);
        vrfCoordinator = VRFCoordinatorV2Interface(_vrfCoordinatorAddress);
        vrfKeyHash = _keyHash;
        chainlinkSubscriptionId = _chainlinkSubscriptionId;

        status = STATUS.CLOSED;
    }

    function start() public onlyOwner {
        require(isLotteryClosed(), "Lottery is not closed.");
        status = STATUS.OPEN;
    }

    function end() public onlyOwner {
        require(isLotteryOpen(), "Lottery is not open.");
        status = STATUS.CALCULATING;
        uint256 requestId = startRandomWinnerFinding();
        emit RandomNumberRequested(requestId);
    }

    function join() public payable {
        require(isLotteryOpen(), "Lottery is not open yet!");
        require(isEntryFeeCorrect(msg.value), getEntryFeeErrorMessage());
        players.push(payable(msg.sender));
    }

    /**
     * This may not be a good idea,
     * as every resource usage is charged in smart contract.
     * Maybe this sort of work should always happen in the front end.
     */
    function getEntryFeeErrorMessage() internal view returns (string memory) {
        string memory m = "You have to pay exactly ";
        m = string.concat(m, uint2str(entryFeeInUSD));
        m = string.concat(m, " USD or ");
        m = string.concat(m, uint2str(getEntryFeeInWei()));
        m = string.concat(m, " WEI.");
        return m;
    }

    function getStatus() public view returns (string memory) {
        if (isLotteryOpen()) return "Open";
        if (isLotteryClosed()) return "Closed";
        return "Calculating Winner";
    }

    function isLotteryClosed() internal view returns (bool) {
        return status == STATUS.CLOSED;
    }

    function isLotteryOpen() internal view returns (bool) {
        return status == STATUS.OPEN;
    }

    function isLotteryCalculating() internal view returns (bool) {
        return status == STATUS.CALCULATING;
    }

    function isEntryFeeCorrect(uint256 _wei) internal view returns (bool) {
        return _wei == getEntryFeeInWei();
    }

    function getEntryFeeInWei() public view returns (uint256) {
        /**
         * current_rate USD = 10^18 wei
         * entry_fee    USD = (10^18 * entry_fee) / current_rate wei
         *                  = (10^18 * entry_fee * 10^18) / (current_rate * 10^18) wei
         */
        return (entryFeeInUSD * (10**18) * (10**18)) / getCurrentRateWRTWei();
    }

    /**
     * This function returns current_rate_of_1_eth * (10^18)
     */
    function getCurrentRateWRTWei() internal view returns (uint256) {
        (, int256 price, , , ) = priceFeed.latestRoundData();
        return uint256(price) * (10**10);
    }

    /**
     * This is not secured,
     * as every param can be controlled by miners.
     */
    function getRandomWinner() internal view returns (uint256) {
        uint256 nonce = 0;
        uint256(
            keccak256(
                abi.encodePacked(
                    nonce,
                    msg.sender,
                    block.difficulty,
                    block.timestamp
                )
            )
        ) % players.length;
    }

    function startRandomWinnerFinding() internal returns (uint256) {
        // Depends on the number of requested values that you want sent to the
        // fulfillRandomWords() function. Storing each word costs about 20,000 gas,
        // so 100,000 is a safe default for this example contract. Test and adjust
        // this limit based on the network that you select, the size of the request,
        // and the processing of the callback request in the fulfillRandomWords()
        // function.
        uint32 callbackGasLimit = 100000;

        // The default is 3, but you can set this higher.
        uint16 requestConfirmations = 3;

        return
            vrfCoordinator.requestRandomWords(
                vrfKeyHash,
                chainlinkSubscriptionId,
                requestConfirmations,
                callbackGasLimit,
                1
            );
    }

    function fulfillRandomWords(uint256 requestId, uint256[] memory randomWords)
        internal
        override
    {
        require(isLotteryCalculating(), "Not calculating.");

        uint256 random = randomWords[0];
        require(random > 0, "random not found");

        winner = players[random % players.length];
        winner.transfer(address(this).balance);
        players = new address payable[](0);
        status = STATUS.CLOSED;
    }

    function uint2str(uint256 _i) internal pure returns (string memory) {
        if (_i == 0) {
            return "0";
        }
        uint256 j = _i;
        uint256 len;
        while (j != 0) {
            len++;
            j /= 10;
        }
        bytes memory bstr = new bytes(len);
        uint256 k = len;
        while (_i != 0) {
            k = k - 1;
            uint8 temp = (48 + uint8(_i - (_i / 10) * 10));
            bytes1 b1 = bytes1(temp);
            bstr[k] = b1;
            _i /= 10;
        }
        return string(bstr);
    }
}
