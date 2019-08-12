# Dutch Auction

## Overview
This project demonstrates how embedding DAML contracts can be used to prevent information leakage during multip-party transactions. The alternative is to use the [multi-party agreement protocol](https://docs.daml.com/daml/patterns/multiparty-agreement.html); however this reveals the identity of parties involved.
This example is a simplified version of auctions [used for IPOs](https://en.wikipedia.org/wiki/Dutch_auction#Public_offerings). You can see a more elaborate example in [bond issuance](https://github.com/digital-asset/ex-bond-issuance).

## Workflow
There is a `seller` party, and two or more bidders. The `seller` generates an `Auction` contract, only vibile to her, and then embedds it into `AuctionInvitation`s for each individual participant. Each bidder responds to the invitaiton with a `Bid`, visible _only to him and the seller_. When the auction finishes at `Auction.end` time, an off-ledger process collects all the bids, caluclates the resulting allocations as an `AuctionResult`.

## Building
```
daml build
```

## Testing
```
daml test
```

## Running
todo - create an external process that monitors `Auctions` and triggers `CompleteAuction` at the appropriate time.