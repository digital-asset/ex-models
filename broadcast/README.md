# Broadcast

## Overview

This example shows how a party `broadcaster` can send data to subscribers. DAML's divulgence mechanism ensures that the broadcast data lands in subscribers' PCSs and can be used to submit transactions. This is an alternative to the use of `observer`. It lacks the guarantees of `observer`, but subscribers don't find out about each other, and the transaction size of adding a new subscriber doesn't grow with the number of subscribers.

## Workflow
1. The `broadcaster` creates a `Broadcast` and `BroadcastData` which they want to broadcast.
2. Subscribers create `SubscriptionRequest` contracts to ask to be added to the `Broadcast`. The `broadcaster` accepts these via choice `AcceptSubscription`.
3. The `broadcaster` updates the `Broadcast` via the `BroadcastUpdate` choice on `Broadcast`.

## Building
To compile the project:
```
daml build
```

## Testing
The model is tested in the script `test_broadcast`. Note how as subscribers are added, the `BroadcastUpdate` transactions get larger, but the transaction to add a new subscriber is constant size.
To run all scripts:
```
daml test --color
```


## Running
To load the project into the sandbox and start navigator:
```
daml start
```
