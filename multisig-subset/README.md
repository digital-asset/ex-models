# Multi-signature X-of-Y Contracts

## Overview

This example models a simple agreement contract, which can be archived by a subset of its signatories. First, all signing parties sign the agreement. Then, subsets of the agreement signatories can create and sign a request for archival on the agreement. Once sufficient signatures are given on the request, the agreement can be archived using either two or three of its signatories.

## Workflow
1. A party creates an `Agreement` contract.
2. Other parties provide their signature on the agreement by calling the `Sign` choice.
3. A signatory of the agreement creates an `ArchivalRequest` contract.
4. Further signatories sign the archival request by calling the `ArchivalRequest_Sign` choice.
5. Once sufficient signatures on the request have been collected, one of the signatories can call the `ArchiveWithTwo` or `ArchiveWithThree` choice to archive the original agreement with at least two respectively three signatures.

## Building
To compile the project:
```
da compile
```

## Testing
To test all scenarios:
```
da run damlc -- test daml/MultisigSubset.daml
```

## Running
To load the project into the sandbox and start navigator:
```
da start
```

## Contributing
We welcome suggestions for improvements via issues, or direct contributions via pull requests.
