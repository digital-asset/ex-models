# Voting

## Overview

This example models a voting process controlled by a government entity. The government puts text-based proposals to a vote by creating a ballot. When the vote is decided a contract evidences the outcome on the ledger.

## Workflow
1. The government creates a `Ballot` for a given `Proposal`.
2. It invites voters via invite/accept, creating mutually signed `VotingRight`s for each.
3. Voters can cast a vote using their `VotingRight` contract for a given `Ballot`.
4. Once all voters have voted the government can `Decide` the vote.
5. The outcome of the ballot is recorded in a `Decision` contract on the ledger.

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
