// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./mock.sol";

contract ChildContract is mock {

    constructor(uint _initialValue) mock(_initialValue) {}

    function incrementValue() public {
        value += 1; // This uses inherited "value" variable from ParentContract
    }
}