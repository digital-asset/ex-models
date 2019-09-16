# Dutch Auction and Secondary Market using Generic Templates

## Overview
This example showcases the use of DAML's [Generic Templates](https://docs.daml.com/daml/reference/generic-templates.html) in the context of a [Dutch Auction](https://docs.daml.com/daml/reference/generic-templates.html) and a [Secondary Market](https://www.investopedia.com/terms/s/secondarymarket.asp). The templates are generic with regards to the `Asset` that is auctioned or traded. The implementation has three different asset types _(Cash, Gold and Receivables)_ but can be easily extended to any daml contract that satisfies the constraints of `Asset t` and `Quantity t` found in [`Asset.daml`](https://github.com/digital-asset/ex-models/blob/master/generic-auction-market/daml/Asset.daml).

## Workflow
The auction and secondary market workflows are demonstated in the `auctionExample` and `marketExample` scenarios respectively in [`Main.daml`](https://github.com/digital-asset/ex-models/blob/master/generic-auction-market/daml/Main.daml)

## Building
```
daml build
```

## Running
```
daml start
```
