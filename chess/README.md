# Chess

## Overview

This example models a chess game between two players. It's similar in spirit to the tic tac toe examples, but demonstrates more complex rule data.

## Workflow
1. A player invites another player by creating a `GameProposal`.
2. Upon acceptance of the invite a `Game` contract is created.
3. The players take turns through the `Move` choice until a `Result` is returned.

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

## Known Issues / Weaknesses
 - No automatic check / checkmate detection
