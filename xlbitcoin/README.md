# XLBitcoin

## Overview

This example demonstrates an over the counter (OTC) Bitcoin trading application that is deployable in [project:DABL](https://www.projectdabl.com)

## Workflow
The `test` scenario in `Trading.daml` demonstrates the workflow

## Dependencies
1. This example uses MS Excel as its front-end. It leverages the [`xlwings`](https://www.xlwings.org/) Excel Add In to connect the workbook to a stateless python program
2. Python3 with the [`xlwings`](https://www.xlwings.org/), [`requests`](https://requests.kennethreitz.org/en/master/), [`pandas`](https://pandas.pydata.org/) and [`python-bitcoinlib`](https://github.com/petertodd/python-bitcoinlib) packages
3. [Blockcypher](https://www.blockcypher.com/) for querying the Bitcoin blockchain and pushing signed transactions

## Running
- Install MS Excel with the xlwings Add In
- Install python3 and all the required packages
- Get a free blockcypher API Token
- Fill in the '.keys' hidden file with your private bitcoin testnet keys, (or create your own file)
- Create a new ledger in [project:DABL](https://www.projectdabl.com) and follow the onboarding process described in the `test` scenario in `Trading.daml`
- Launch the Excel spreadsheet and agree to "enable macros". (If it is your first time running xlwings you will need to do some additional setup to enable the `RunPython` command)
