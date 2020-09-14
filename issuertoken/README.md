# Token Issuance

## Overview
This is an example of token issuance. Unlike other blockchains, the DAML ledger model has strict access controls built-in. For instance, when issuing an Ethereum contract, it is by default visible to anybody; by contrast in DAML read/write access is specified in the contract itself, and the ledger guarantees the integrity of transactions.

This is meant to be an example of asset tokenization, where a central party, the issuer, is the only one able to create/transfer/destroy tokens. Other parties can inspect (only their own) holdings, but may not transfer tokens; to do this they need to request the issuer to perform the action using a `RequestTokens` contract.

## Building
To compile the project:
```
daml build
```

## Testing
To test all scripts:
```
daml test --color Scripts.daml
```

## Running
To load the project into the sandbox and start navigator:
```
daml start
```
