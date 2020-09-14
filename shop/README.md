# Shop

## Overview
This example models a simple shop management system. Vendors can offer items, which can be bought by users. During a purchase the item and payment are swapped atomically.

## Workflow
1. The producer produces `Item`s and distributes them to vendors.
2. The issuer issues `Iou`s and distributes them to users.
3. The owner creates a `Shop` contract and onboards vendors and users via invite/accept creating mutually signed relationship contracts for each.
4. The vendor offers an item for a set price via the `OfferItem` choice on its `VendorRelationship` contract.
5. The user buys the item via the `BuyItem` choice on its `UserRelationship` contract.
6. The `Item` and the `Iou` are swapped atomically between vendor and user.

## Building
To compile the project:
```
da compile
```

## Testing
To test all scripts:
```
da run damlc -- test daml/ApprovalChain.daml
```

This example follows a behaviour-driven (aka script-based) testing approach and implements useful helpers, which are explained in the following.

### Test definition
```haskell
data Test a b = Test with
  given : Script a
  when : a -> Script b
  then_ : a -> b -> Script Bool
```
The `Test a b` type constructor creates a `Test` type given a fixture type `a` and a result type `b`. The type encapsulates the given, when, and then steps of a behaviour-driven test and allows for a generic `run` function to be defined:
```haskell
run : Test a b -> Script ()
run test = do
  fixture <- test.given
  result <- test.when fixture
  check <- test.then_ fixture result
  assert $ check
```
In the following each field of the `Test` type is explained in more detail.

### Test setup
The `given` field with signature `Script a` provides a fixture object of type `a` when bound. The fixture script is responsible for setting up all contracts required at the start of each test. These contracts should be bundled in a record type so they can be brought into scope conveniently via record wildcard pattern matching. Here is an example of a fixture type and a corresponding script:
```haskell
data Fixture = Fixture with
  operator : Party
  issuer : Party
  owner : Party
  amount : Decimal

given_fixture : Script Fixture
given_fixture = do
  operator <- allocateParty "Operator"
  issuer <- allocateParty "Issuer"
  owner <- allocateParty "Owner"
  let amount = 10.0
  pure Fixture with ..
```

### Test action
The `when` field with signature `a -> Script b` is a function that takes a fixture of type `a` and returns a script that provides a result of type `b` when bound. This function is responsible to execute the actual test. Any test result that needs to be verified should be encapsulated in the result type `b` which can be a record type specifically created for this purpose or simply a domain object of your model. Here is an example of an action with a result type `Iou`:
```haskell
when_action : Fixture -> Script Iou
when_action fix =
  let Fixture{..} = fix
  iouId <- submit issuer do createCmd Iou with issuer; owner; amount
  Some iou <- queryContractId issuer iouId
  pure iou
```

### Test condition
The `then_` field with signature `a -> b -> Script Bool` is a function taking a fixture of type `a` and a result of type `b`, and returns a script that provides a boolean test result. The function is responsible for verifying the test result against the expectiations. Here is an example verifying that the Iou created in the `when` step above does in fact have the expected amount speficied in the `fixture`:
```haskell
then_condition : Fixture -> Iou -> Script Bool
then_condition fix res =
  pure $ res.amount == fix.amount
```

### Usage
To specify a test define the three functions as explained above and combine them in a `Test` object. This object can then be passed to the generic `run` function.

```haskell
let correct_iou_amount = Test with
      given = given_fixture
      when = when_action
      then_ = then_condition
run correct_iou_amount
```

The main benefit of splitting up a test like this is the ability to reuse individual steps. In particular the test fixture is usually the same for many tests and having this step encapsulated in a function allows direct reuse. Less often one might also be able to reuse a `when` step or a `then` condition across tests. A possible extension to this model is the addition of a tear-down step. This would allow a test to clean up the ledger after it has run.

## Running
To load the project into the sandbox and start navigator:
```
daml start
```

## Contributing
We welcome suggestions for improvements via issues, or direct contributions via pull requests.
