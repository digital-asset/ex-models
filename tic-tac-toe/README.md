# Tic Tac Toe

## Overview

This example models the tic tac toe game between two players. It demonstrates primarily various way of testing `Either`-based state transitions. The `Play` choice returns either a new `Game` contract, or a `Result` contract if the game is decided. The first script uses a naive testing approach, which results in a highly nested chain of `case` statements. Subsequent scripts demonstrate how to simplify such kind of tests and make them more readable using binding functions.

## Workflow
1. A player invites another player by creating a `GameInvite`.
2. Upon acceptance of the invite a `Game` contract is created.
3. Player 1 starts the game by exercising the `Play` choice, which recreates the `Game` contract with the move added.
4. The players now take turns until the `Play` choice detects a final state (win or tie).
5. When the game is finished a `Result` contract is created containing the state and outcome of the game.

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
