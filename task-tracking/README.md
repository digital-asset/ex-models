# Task Tracking

## Overview

This example models a sequential task tracking tool with each step represented by a template. A party creates a task and proposes assignment to another party. The receiving party can accept or redirect the assignment. An assigned task can then be started and the start time is recorded. The started task can then be completed, recording the end time of the task. Completed tasks can be deleted by the assigned person.

## Workflow
1. The creator creates a `NewTask`.
2. The creator `Assign`s the task to the assignee, creating a `TaskAssignmentProposal`.
3. The assignee can `Accept`s the proposal which creates an `AssignedTask`.
4. The assignee can then `Start` the assigned task, recording the start time of the task.
5. The assignee then `Complete`s the started task, recording the end time of the task.
6. Finally, the assignee can `Delete` the completed task removing it from the ledger.

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
