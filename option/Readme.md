# Option

## Overview

This example models a simple European style option.

## Core Workflow
1. An `issuer` creates a `Quote` for an option.
2. A `client` accepts the `Quote` to create an `Option`
3. The `issuer` expires the `Option` using a `Fixing`, resulting in a `CashEntry` for the `client`.

### Side Workflows
1. An `agent` and `trader` can create indicative and firm quotes on the `issuer` side, respectively.
2. A `supervisor` and `clerk` can engage in a two-step process to accept `Quotes` on the `client` side.

## Running
To load the project into the sandbox and start navigator:
```
da start
```
