# Chess

## Overview

This example models a chess game between two players. It's similar in spirit to the tic tac toe examples, but demonstrates more comples rule data.

## Workflow
1. A player invites another player by creating a `GameProposal`.
2. Upon acceptance of the invite a `Game` contract is created.
3. The players take turns through the `Move` choice until a `Result` is returned.

## Building
To compile the project:
```
da compile
```

## Testing
To test scenarios:
```
da run damlc -- test daml/Tests/All.daml
```

## Running
To load the project into the sandbox and start navigator:
```
da start
```

## Known Issues / Weaknesses

 - No automatic check / checkmate detection

## Contributing
We welcome suggestions for improvements via issues, or direct contributions via pull requests.
