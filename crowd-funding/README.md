# Crowd Funding

## Overview

This example models the concept of crowd funding campaign where backers contribute money to a project, but the collected funds can only be released if they exceed a predefined threshold. If the threshold is not reached the funds can be reclaimed. A suggested extension to this model is to introduce a time threshold, which controls when claims or reclaims can happen.

## Workflow
1. The `originator` creates a `Project` contract defining the required `threshold` to reach.
2. The originator invites backers via invite/accept, collecting signatures from each on the `Project` contract.
3. Backers can then `Pledge` `Iou`s to the project, which get locked up in the process. Pledges can only be done before the project's `deadline`.
4. Once the `deadline` has passed and if the raised amount exceeds the `threshold` of the `Project` the `originator` can `Claim` the raised funds, which subsequently get transferred to him using the collected authorization on the `Project` contract.
5. If the raised funds are below the `threshold` the backers can trigger a `Reclaim` for the `Iou`s to be returned.

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
