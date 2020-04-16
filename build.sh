#!/bin/bash

#cd `dirname $0`
#cd ..

DIRS=("airline"
      "approval-chain"
      "auction"
      "broadcast"
      "chat"
      "chess"
      "crowd-funding"
      "expense-pool"
      "governance"
      "issuertoken"
      "onboarding"
      "option"
      "shop"
      "task-tracking"
      "tic-tac-toe"
      "voting"
      )

function cleanDars {
  for dr in ${DIRS[@]}
  do 
    rm -f $dr/.dist
  done
}

function buildDars {
  for dr in ${DIRS[@]}
  do
    echo "Building dar in $dr"
    cd $dr
    daml build
    cd ..
  done
}

function testDars {
  for dr in ${DIRS[@]}
  do
    echo "Testing dar in $dr"
    cd $dr
    daml test
    cd ..
  done
}

function updateVersion {
  if [ "$1" == "" ]; then
    echo "please provide the new version"
    exit 1
  fi
  for dr in ${DIRS[@]}
  do
    cat $dr/daml.yaml | sed -E "s/^(sdk-version:).*/\\1 $1/" > tmp.yml
    mv tmp.yml $dr/daml.yaml
  done
  cat daml.yaml | sed -E "s/^(sdk-version:).*/\\1 $1/" > tmp.yml
  mv tmp.yml daml.yaml
  cat ./.circleci/config.yml | sed -E "s/daml-sdk:.*/daml-sdk:$1/" > tmp.yml
  mv tmp.yml ./.circleci/config.yml
}

case $1 in

  update-version)
    updateVersion $2
    ;;
  build-dars)
    cleanDars
    buildDars
    ;;
  test-dars)
    testDars
    ;;
  *)
    echo "builder <command>"
    echo "  commands are:"
    echo "    build-dars - builds the dars"
    echo "    update-version <version> - changes the sdk version number"
    ;;
esac
