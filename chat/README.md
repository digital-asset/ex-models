# Group Chat

## Overview

This example demonstrates how to implement a group chat with dynamic groups in DAML. All members of a `ChatGroup` have equal rights -- there is no owner, admin or operator. `Message` history is maintained as the group changes (ie new members get to see old messages). All messages are signed by all current members so history can't be falsified unless all members decide to do so jointly.

Maintaining the message history and tight linking between messages and group requires the maintenance of an index of all messages. Doing so globally would make the posting of messages racy between group members. To avoid this, the index is sharded by member in `MessageIndex`.

The message history per group grows indefinitely and changes in membership require all messages to be re-signed by the new mambership. Transactions changing group membership therefore grow in complexity O(#messages * #members).

## Workflow
1. Anyone can start a group by creating a `GroupChat` contract.
2. New group members are onboarded by existing members. Discovery happens off-ledger. Ie `Alice` is assumed to have told `Bob` and `Charlie` about her group "troll-bot" in the included scripts.
3. Members can post messages with the `Post_Message` choice and leave the group using the `LeaveGroup` choice as they please.

## Building
To compile the project:
```
daml build
```

## Testing
The model is tested in a series of sequential scripts terminating in `archive_charlie`. Note how `Post_Message` is a relatively small transaction, whereas `LeaveGroup` and `AddMember` get larger as the group grows.
To test all scripts:
```
daml test --color
```

## Running
To load the project into the sandbox and start navigator:
```
daml start
```
