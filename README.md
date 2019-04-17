# DAML Examples

## Overview

This repository contains examples for several use cases modeled in DAML. They showcase useful patterns and practices when writing DAML applications. Refer to the readme files for more information.

## Prerequisites

- [DAML SDK](https://docs.daml.com/getting-started/installation.html)

## Examples

### Approval Chain
A simple three-step, sequential approval process, collecting signatures from approvers along the way.

[Project Readme](approval-chain/README.md)

### Task Tracking
A Jira-like work tracking model implementing a linear task workflow. Tasks can be created, assigned, reassigned, started and completed.

[Project Readme](task-tracking/README.md)

### Voting
A simple voting model where ballots are organized around proposals, and decision being taken are represented as contracts on the ledger.

[Project Readme](voting/README.md)

### Tic-Tac-Toe
A model for the Tic-Tac-Toe game for two players playing against each other.

[Project Readme](tic-tac-toe/README.md)

### Expense Pool
A shared expense pool where expenses are added in form of Ious, which then get split fairly between the partcipants.

[Project Readme](expense-pool/README.md)

### Crowd Funding
A model for a crowd funding campaign where backers commit Ious to a project. The originator can claim the funds if they surpass a threshold, and funds can be reclaimed if the threshold isn't reached.

[Project Readme](crowd-funding/README.md)

### Governance
A model demonstrating how on-chain governance can be modeled in DAML. Citizens can vote for the creation of a consititution contract, for the update of the constitution text, or for the upgrade of the constitution contract to a newer version.

[Project Readme](governance/README.md)

