# Lottery

## Overview

This example models the concept of lottery where ...

## Workflow
1. The `Organizer` party creates a lottery `Draw` contract.
2. The `Organizer` party invites `Players` via invite/accept, collecting the fee on the lottery `Draw` contract.
3. Players can `Play` `Iou`s to the Lottery draw, they receive a lottery `Ticket` iou in return.
4. Once the `deadline` has passed the `winner` can `Claim` the cash prize, which subsequently get transferred to him using the collected authorization on the `Draw` contract.
5. If there are no winners, then the prize is carried over to the next lottery `Draw`.

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