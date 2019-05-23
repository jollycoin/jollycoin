# JollyCoin Whitepaper

## Introduction

Mathematics secures the network and empowers individuals to control their own finances. JollyCoin features the same transaction confirmation times as the leading math-based currencies. New block is on average mined in 10 minutes. Mining is based on Proof-of-Work (PoW) algorithm that hashes using SHA-256 function, and finds corresponding nonce, similar to hashcash PoW.


## Technology

All network transport is done using standard HTTP protocol. Client requests are plane POST requests. All communication is and should be asynchronous for maximum usage of IO resources.


## Transaction

Every transaction, regardless of the type, must be signed by the sender prior to being accepted by the network. The process of signing the transaction is identical for every transaction.

A transaction is a transfer of JollyCoin value that is broadcast to the network and collected into blocks. Transactions are not encrypted, so it is possible to browse and view every transaction ever collected into a block. Once transactions are buried under enough confirmations they can be considered irreversible.

All transactions are visible in the blockchain, and can be viewed with a block explorer also called block browser. This is useful for seeing the technical details of transactions in action and for verifying payments.

After each transaction is signed, it is hashed using the SHA-256 algorithm to ensure that no data cannot be changed. If transaction is altered, hash will not match, and transaction will be invalid.


## Block

Transaction data is permanently recorded in files called blocks. Blocks are organized into a linear sequence over time, also known as the Blockchain. New transactions are constantly being processed by miners into new blocks which are added to the end of the chain. As blocks are buried deeper and deeper into the blockchain they become harder and harder to change or remove.

Each block contains, among other things, a record of some or all recent transactions, and a reference to the block that came immediately before it. It also contains an answer to a difficult-to-solve mathematical puzzle - nonce. New blocks cannot be submitted to the network without the correct answer - the process of "mining" is essentially the process of competing to be the next to find the answer that "solves" the current block. The mathematical problem in each block is extremely difficult to solve, but once a valid solution is found, it is very easy for the rest of the network to confirm that the solution is correct. There are multiple valid solutions for any given block - only one of the solutions needs to be found for the block to be solved.

After each Block is generated, it is hashed using the SHA-256 algorithm to ensure that no data cannot be changed. If block is altered, hash will not match, and block with all its transactions will be invalid.


## Blockchain

Blocks in the main chain are the longest series of blocks that go from the genesis block to the current block.

A blockchain is a transaction database shared by all nodes participating in a system based on the JollyCoin protocol. A full copy of a currency's block chain contains every transaction ever executed in the currency. With this information, one can find out how much value belonged to each address at any point in history.

Every block contains a hash of the previous block. This has the effect of creating a chain of blocks from the genesis block to the current block. Each block is guaranteed to come after the previous block chronologically because the previous block's hash would otherwise not be known. Each block is also computationally impractical to modify once it has been in the chain for a while because every block after it would also have to be regenerated. These properties are what make JollyCoin transactions irreversible.

A chain is valid if all of the blocks and transactions within it are valid, and only if it starts with the genesis block. For any block on the chain, there is only one path to the genesis block.

Coordinator guarantees that there is always one and only one chain of blocks coming from genesis. It is impossible to form smaller chains which compete which one will be accepted as final in blockchain. However, technically forks are possible of main chain.

Because a block can only reference one previous block, it is impossible for two forked chains to merge.

It's possible to use the block chain algorithm for non-financial purposes. JollyCoin is extensible, and will in future support creating Tokens on top of JollyCoin blockchain.

The blockchain is broadcast to all nodes on the networking using a long-poll requests from other nodes.


## Mining

Miners are currently awarded with 1 JLC (JollyCoin) per block, plus all fees associated with sent transactions, serving as incentive for miners. JollyCoin network is scheduled to produce 21 million JollyCoins. Every block is mined in average every 10 minutes. Initially, every two weeks, mining difficulty will be readjusted to keep average block mining time to about 10 minutes. This is mater of change, reward and difficulty might change in future depending on direction of development of JollyCoin.

The JollyCoin blockchain is capable of handling high transaction volume. Due to frequent block generation, the network supports more transactions. As a result, merchants get faster confirmation times.

Generated blocks' first transaction has no sender, but it has receiver address of miner and reward amount for miner. Generated block has unique nonce. Other miners cannot still work of any other miner, because reward will go to original miner address.


## Majority Attack

A majority attack (usually labeled 51% attack or >50% attack) is an attack on the network. This attack has a chance to work even if the merchant waits for some confirmations, but requires extremely high relative hashrate.

Due to use of Coordinator, Majority Attack is mitigated. However, network will depend on Coordinator availability for some time, until network stabilizes and reaches mature status.


## Characteristics

There will be maximum of 21,000,000 JLC every mined. Each JLC consists of 1,000 mJLC, or 1,000,000 uJLC. This means that 1 JLC consists of 1 million inseparable units called micro-JLC, or uJLC.

Unlike Bitcoin, but similar to Ethereum, JollyCoin operates using accounts and balances in a manner called state transitions. This does not rely upon unspent transaction outputs (UTXOs). Unlike Ethereum, state transitions are stored in main blockchain. Coordinator ensures validness of state transitions.