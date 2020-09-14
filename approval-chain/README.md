# Approval Chain

## Overview

This example models a simple chain of approval. The originator creates proposed content, which then goes through three sequential approval steps. Each step of the approval process is represented by a separate contract and collects the signature of the approver on the subsequent contract. The final contract is fully approved and contains signatures from the originator as well as all approvers.

By itself such a process is only useful to evidence approvals. To make use of the gathered signatures one can add a choice controlled by the originator to the final contract, within which he/she can perform actions using the authorization of all approvers. This makes this pattern useful whenever multiple signatures are required to exercise a given choice in another workflow.

## Workflow
1. The originator creates a `Proposed` contract providing some `Content`.
2. The level 1 approver exercises the `Level1Approve` choice on this contract to provide his approval. This creates a `Level1Approved` contract with two signatories.
3. Then, the level 2 approver exercises the `Level2Approve` choice on this contract to provide his approval. This creates a `Level2Approved` contract with three signatories.
4. Finally, the level 3 approver exercises the `Level3Approve` choice, which creates the final `FullyApproved` contract. This contract now has signatories from all involved parties.

## Building
To compile the project:
```
daml build
```

## Testing
To test all DAML scripts:
```
daml test --color
```

## Running
To load the project into the sandbox and start navigator:
```
daml start
```
