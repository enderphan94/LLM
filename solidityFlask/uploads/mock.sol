// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract mock {
    uint public value;
    bool private locked;

    constructor(uint _initialValue) {
        value = _initialValue;
        locked = false;
    }

    
    function setValue(uint _value) public {
        value += _value; // Unsafe addition (vulnerable to overflow)
    }

    function withdraw(address payable _recipient, uint _amount) public {
        require(_amount <= value, "Not enough balance");
        require(!locked, "Reentrancy detected");

        locked = true;
        (bool success, ) = _recipient.call{value: _amount}(""); // External call
        require(success, "Transfer failed");

        value -= _amount;
        locked = false;
    }

    function getValue() public view returns (uint) {
        return value;
    }

    // Function to receive Ether
    receive() external payable {
        value += msg.value;
    }
}