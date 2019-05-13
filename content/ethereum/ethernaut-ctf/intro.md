Title: Solving Zeppelin's Ethernaut CTF - Intro
Date: 2018-05-19 18:30
Tags: ethereum, solidity, ctf, smart contracts
Category: Ethereum
Slug: solving-zeppelin-ethernaut-ctf-intro
Summary: First post of a series in which we will tackle the challenges in the [Ethernaut CTF by Zeppelin](https://ethernaut.zeppelin.solutions/){:target="_blank",:rel="noopener"}. In this first article, we prepare the environment with Truffle and Ganache-cli.

## Introduction
In this series of posts, I will cover the challenges included in the [Ethernaut CTF by Zeppelin](https://ethernaut.zeppelin.solutions/){:target="_blank",:rel="noopener"}. In the process,
I'll be explaining the Ethereum and Solidity fundamentals that are needed to solve each challenge, along with the code necessary to exploit the vulnerabilities found in the smart contracts.

I assume that you have some basic knowledge of what Ethereum and Smart Contracts are. If you don't, well, Zeppelin happens to have [a series of posts explaining the basics and not-so-basics of the Ethereum platform](https://blog.zeppelin.solutions/a-gentle-introduction-to-ethereum-programming-part-1-783cc7796094).

Although the use of external tools is not strictly mandatory in all challenges, I found it easier and better to use Truffle and Ganache-cli (formerly known as TestRPC) in my local computer instead of using the platform provided by Zeppelin to solve the challenges through the browser's console.

## Truffle & Ganache-cli
In a nutshell, Ganache-cli simulates a local Ethereum blockchain (including 10 fake externally owned accounts (EOA), each with 100 ETH in their balance), while Truffle takes care (among other things) of compiling your Solidity contracts to EVM bytecode and deploy them to the any blockchain you configure (more on this later).

So, before we dive into the challenges, let's first install Truffle and Ganache-cli as npm dependencies. Inside a new folder, initialize npm with `npm init -y` and then install Truffle and Ganache-Cli. A simple `npm i -g truffle@4 ganache-cli@6` should suffice, but if you have trouble doing so, please refer to either the [Truffle docs](http://truffleframework.com/) or [Ganache-cli docs](https://github.com/trufflesuite/ganache-cli).

_**DECEMBER 2018 UPDATE:** Note that we're installing Truffle 4 and not Truffle 5. While the tutorials might also work with Truffle 5, I haven't had the time to properly test it, so for now let's keep using Truffle 4._

### Quick side note on Ethereum accounts
I mentioned the term **externally owned accounts** before, so just to shed some light on that, this is how the [Ethereum docs](https://github.com/ethereum/wiki/wiki/Ethereum-Development-Tutorial#introduction) define them:
There are two types of accounts:
> 
> - **Externally owned account (EOAs)**: an account controlled by a private key, and if you own the private key associated with the EOA you have the ability to send ether and messages from it.
> - **Contract**: an account that has its own code, and is controlled by code.

### Running Ganache-cli
Brace yourself, this part is the toughest one.

1. Open a terminal
2. Run `npx ganache-cli`

### Truffle init
Create a new folder and inside it, run `truffle init`. Truffle will then create several folders and files. In the base dir, you'll find `truffle.js` and `truffle-config.js`. These are the configuration files for Truffle. On Windows, just delete `truffle.js`.

Inside `truffle-config.js`, you can tell Truffle where is/are the blockchain(s) you want to use. As ours we'll be a local blockchain (the one ganache-cli runs), the truffle-config.js looks like this:

~~~javascript
/* truffle-config.js */
module.exports = {
    networks: {
        development: {
            host: "127.0.0.1",
            port: 8545, // Where ganache-cli listens (8545 is default)
            network_id: "*" // Matches any network id
        }
    }
};
~~~

In `port`, write the local port in which you'll run the blockchain service. Ganache-cli listens on *8545* by default when you run `npx ganache-cli` on your terminal, but you can easily change that by running `npx ganache-cli --port <port-number>` instead.

For more advanced Truffle configurations and deeper explanations, refer to [Truffle Configuration page](http://truffleframework.com/docs/advanced/configuration).

## Summing up
1. Create a folder to keep all our contracts and exploits: `mkdir ethernaut-ctf` and `cd ethernaut-ctf`
2. Inside that folder, `npm init -y` and then `npm i truffle@4 ganache-cli@6`. This will initialize NPM with a `package.json` file and then install latest Truffle 4 and Ganache-cli 6
3. Now init a Truffle project with `npx truffle init`
4. Start Ganache with `npx ganache-cli` or `npx ganache-cli --port <port-number>` if you want it to listen in a port other than 8545. If you do this, remember to change the port number in the `truffle-config.js` file as well.
5. In a new terminal, `cd ethernaut-ctf` if not already in that dir and `npx truffle console`
6. If everything went well, a `truffle(development)>` prompt should appear.
    - There, you could do `web3.eth.accounts` and hit enter. A JSON-formatted list of 10 public addresses should appear. Those are the 10 EOAs (the public addresses) that Ganache created for you.

Okey, we are all set. In the [next article](https://www.notonlyowner.com/ethereum/solving-zeppelin-ethernaut-ctf-fallback/), we will get our hands dirty and solve the first challenge: [Fallback](https://ethernaut.zeppelin.solutions/level/0x234094aac85628444a82dae0396c680974260be7){:target="_blank",:rel="noopener"}.

To do so, we will first walk through **the very basics of Solidity**, so we can then cover how to deploy the vulnerable smart contract to the local blockchain to start interacting with it. Finally, we will understand **why the Fallback contract is vulnerable** and how you can **exploit it** to pass the challenge.
