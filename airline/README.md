# Airline

## Overview
This DAML model shows a process to issue airline tickets, and manage the seat allocation of a flight. The process is privacy preserving in the sense that passengers don't get to see each other's tickets. The process enables transactional, self-service seat choices, requiring passengers to know about each other, even before they get on the flight.

## Building
To compile the project:
```
daml build
```

## Testing
To test all DAML scripts:
```
daml test --color
```

## Running
To load the project into the sandbox and start navigator:
```
daml start
```
