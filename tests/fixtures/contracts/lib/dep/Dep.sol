// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract Dep { function f() external { require(tx.origin != address(0)); } }
