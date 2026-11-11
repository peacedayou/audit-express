// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

// Contrat volontairement vulnérable, utilisé seulement par les tests
contract Vulnerable {
    address owner = msg.sender;

    function withdraw(address payable to) external {
        require(tx.origin == owner); // tx.origin
        to.send(address(this).balance);
    }

    function proxy(address impl, bytes calldata data) external {
        impl.delegatecall(data);
    }

    function recover(bytes32 h, uint8 v, bytes32 r, bytes32 s) external pure returns (address) {
        return ecrecover(h, v, r, s);
    }

    // tx.origin dans un commentaire ne doit pas compter
}
