# DAML Examples

## Overview

This repository contains examples for several use cases modeled in DAML. They showcase useful patterns and practices when writing DAML applications. Refer to the readme files for more information.

## Prerequisites

- [DAML SDK](https://docs.daml.com/getting-started/installation.html)

## Contributing
We welcome suggestions for improvements via issues, or direct contributions via pull requests.

## Examples

### Airline Seat Allocation
A lean, but somewhat privacy-preserving process to issue airline tickets and allocate seats.

[Project Readme](airline/README.md)

### Approval Chain
A three-step, sequential approval process, collecting signatures from approvers along the way.

[Project Readme](approval-chain/README.md)

### Auction
An auction model with private bids.

[Project Readme](auction/README.md)

### Broadcast
A model showing how a broadcaster can broadcast information to subscribers via the ledger in a non-guaranteed, but efficient manner.

[Project Readme](broadcast/README.md)

### Group Chat
A model demonstrating a distributed group chat application with dynamic, admin-less chat groups.

[Project Readme](chat/README.md)

### Chess
A chess game written in DAML.

[Project Readme](chess/README.md)

### Crowd Funding
A model for a crowd funding campaign where backers commit Ious to a project. The originator can claim the funds if they surpass a threshold, and funds can be reclaimed if the threshold isn't reached.

[Project Readme](crowd-funding/README.md)

### Expense Pool
A shared expense pool where expenses are added in form of Ious, which then get split fairly between the partcipants.

[Project Readme](expense-pool/README.md)

### Governance
A model demonstrating how on-chain governance can be modeled in DAML. Citizens can vote for the creation of a consititution contract, for the update of the constitution text, or for the upgrade of the constitution contract to a newer version.

[Project Readme](governance/README.md)

### Issuer Token
Example of token issuance by a central controlling party.

[Project Readme](issuertoken/README.md)

### Onboarding
A task-list app with composable sub-tasks, designed to check off onboarding tasks.

[Project Readme](onboarding/README.md)

### Option
A European style cash settled option.

[Project Readme](option/README.md)

### Shop
A marketplace example where vendors offer items to buyers.

[Project Readme](option/README.md)

### Task Tracking
A Jira-like work tracking model implementing a linear task workflow. Tasks can be created, assigned, reassigned, started and completed.

[Project Readme](task-tracking/README.md)

### Tic-Tac-Toe
A model for the Tic-Tac-Toe game for two players playing against each other.

[Project Readme](tic-tac-toe/README.md)

### Voting
A simple voting model where ballots are organized around proposals, and decision being taken are represented as contracts on the ledger.

[Project Readme](voting/README.md)
