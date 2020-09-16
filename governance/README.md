# Governance

## Overview
The governance model extends the [Voting](../Voting/README.md) example with functionality to vote on specific changes to the ledger. This is a simple form of on-ledger governance where users decide how a given model evolves. In the example the citizens can vote to create a constitution with a given text, to change the text of an existing constitution, or to upgrade the constitution contract itself. The newer version of the constitution contract gives the government the option to create ballots directly, as opposed to going through the invite/accept inbreeding process of voters.

## Workflow
1. The `government` creates a `Ballot` for one of three available `Proposal`s.
2. It invites voters via invite/accept, creating mutually signed `VotingRight`s for the given `Proposal`.
3. Each voter can cast a boolean `accept` vote via the `CastVote` choice.
4. Once all voters have cast their votes the government can `Decide` the `Ballot`.
5. If the `Proposal` received more `True` than `False` votes the decision is `execute`d.
6. The resulting `DecisionOutCome` is:
   - `None` if the proposal got rejected
   - `ContractId Consitiution` if a proposal to create or update the text of a constitution was accepted
   - `ContractId ConsititutionV2` if a proposal to upgrade the constitution contract was executed.
7. If the constitution contract was upgraded the government now has a new option to directly create `Ballot`s off the new constitution contract.

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
