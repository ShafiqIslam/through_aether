// SPDX-License-Identifier: UNLICENSED

pragma solidity ^0.6.0;

contract SimpleStorage {
    uint256 someValue;

    struct Person {
        string name;
        uint256 someValue;
    }

    Person[] public people;
    mapping(string => uint256) public peopleMap;

    function store(uint256 v) public {
        someValue = v;
    }

    function retrieve() public view returns(uint256) {
        return someValue;
    }
    
    function multiplyByTwo(uint256 v) public pure returns(uint256) {
        return v * 2;
    }

    function addPerson(string memory _name, uint256 _v) public {
        people.push(Person({name: _name, someValue: _v}));
        peopleMap[_name] = _v;
    }
}
