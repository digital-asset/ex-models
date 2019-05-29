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

### Option
A simple European style cash settled option.

[Project Readme](option/README.md)

### MongoDB ODS
A simplified demo covering the use of MongoDB as an ODS to capture streamed events from the DA ledger, and run analytics using native MongoDB aggregation pipelines. Also touches on (Rabbit)MQ pub-sub for handling large volumes of writes to the ledger when loading data.

[Project Readme](mongoDB_ODS/README.md)

### Chess
A chess game

[Project Readme](chess/README.md)

### Onboarding
A simple task-list app with composable sub-tasks, designed to check off onboarding tasks.

[Project Readme](onboarding/README.md)

### Airline seat allocation
A lean, but somewhat privacy-preserving process to issue airline tickets and allocate seats.

[Project Readme](airline/README.md)

### Broadcast
A model showing how a broadcaster can broadcast information to subscribers via the ledger in a non-guaranteed, but efficient manner.

[Project Readme](broadcast/README.md)
