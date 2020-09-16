# Expense Pool

## Overview

This example models a shared expense pool where participants submit group expenses which are to be distributed fairly between parties. Each submitted expense is split between participants and the resulting Ious are merged and netted. A final split choice then creates the respective Iou contracts on the ledger.

## Workflow
1. A party creates a `Pool` to manage group expenses.
2. Participants in the pool can invite new participants via invite/accept, collecting their signatures on the `Pool` contract.
3. Participants can then `Declare` `Expense`s against the pool, which distributes the amount pro-rata by creating `Iou` records.
4. Each new `Iou` is merged with existing ones that have the same issuer and owner, and is netted with existing ones that have the opposite issuer and owner.
5. Finally, participants can exercise the `Split` choice on the pool, which creates the corresponding `Iou` contracts on the ledger.

## Building
To compile the project:
```
daml build
```

## Testing
To test all scripts:
```
daml test --color
```

## Running
To load the project into the sandbox and start navigator:
```
daml start
```
