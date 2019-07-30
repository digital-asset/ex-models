# Lottery

## Overview

This example models the concept of lottery where ...

## Workflow
1. The `Organizer` party creates a `Lottery` contract.
2. The `Organizer` party invites `Players` via invite/accept, collecting the fee on the `Lottery` contract.
3. Players can `Play` `Iou`s to the Lottery draw, which get locked up in the process.
4. Once the `deadline` has passed the `winner` can `Claim` the raised funds, which subsequently get transferred to him using the collected authorization on the `Lottery` contract.
5. If there are no winners, then the prize is carried over to the next `Lottery` draw.

## Building
To compile the project:
```
daml build
```

## Testing
To test all scenarios:
```
daml test --color
```

## Running
To load the project into the sandbox and start navigator:
```
daml start
```