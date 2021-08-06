# Universal Auto-Tracking Protocol

## Abstract

This protocol can be used between trackers and randomized games to implement
auto-tracking, instead of having direct access to sockets or processes from Lua.

The game (or mod, or interface program) implements the server side as a web-
socket server.
The tracker framework implments an auto-reconnecting websocket client.
The tracker pack uses a simple interface with callbacks in Lua to match states.

**NOTE:** if the game/mod can not directly implement a websocket server, an
interface program is required that communicates with both tracker and game.\
One such program is [UATBridge](https://github.com/black-sliver/UATBridge).


## Default Host and Port

`ws://localhost:65399`\
`ws://localhost:44444` fallback


## Framing

Each packet is a single websocket message that contains a json array with one
object per command, with command name in "cmd" and command arguments in named keys.
Multiple commands in one packet are to be handled as atomic as possible.

`[{"cmd": "<CommandName>", ...}, ...]`

Unknown arguments are to be ignored, invalid commands should get an ErrorReply.
Because of the async nature (see below) the next packet does not have to be a
reply to the previous request.

If the websocket message was not valid json, the connection should be closed.


## Naming

Argument keys are lower case, command names are CamelCased, variable names are
game specific.


## Commands Client -> Server

### Sync
Reads all variables from the server for one slot (player/seat) if `slot` is set,
or all slots if `slot` is empty.

Argument  | Required | Type             | Description
--------- | -------- | ---------------- | ----------- 
`slot`    | optional | string           | identifier of the requested slot

#### Example
```
> [{"cmd": "Sync"}]
< [{"cmd": "Var", "name": "Sword", "value": 2}, ...]
```


## Commands Server -> Client

### Info
This is automatically sent when connecting to the server to detect protocol
version, features and slots (if any). An error should be displayed if the server
is incompatible. The user should be prompted to select a slot if there is more
than one.

Argument  | Required | Type             | Description
--------- | -------- | ---------------- | ----------- 
`protocol`| required | integer          | the protocol version/revision
`name`    | optional | string           | representing the mod or game name connected to
`version` | optional | string           | representing the mod or game version
`features`| optional | array of strings | optional features supported
`slots`   | optional | array of strings | identifiers if the game has multiple players/seats/slots

#### Example
```
> [{"cmd": "Info", "name": "SomeGame Randomizer", "version": "1.0.0-mod1.0.0",
    "protocol": 0, "features": [], "slots": []}]
```

### Var
This is sent for each variable after a Sync, or when any variable changed.

Argument  | Required | Type             | Description
--------- | -------- | ---------------- | ----------- 
`name`    | required | string           | name of the variable
`value`   | required | any              | value of the variable
`slot`    | optional | string           | identifier for player/seat/slot

#### Example
see Sync

### ErrorReply
This reply is sent when the client sent an errorneous command,
mostly for debugging purposes.

Argument     | Required | Type             | Description
------------ | -------- | ---------------- | ----------- 
`name`       | required | string           | name of the command that was rejected
`argument`   | optional | string           | name of the argument causing the error, if any
`reason`     | required | string           | one of `unknown cmd`, `missing argument`, `bad value`, `unknown`
`description`| optional | string           | additional text, e.g. exception messages or validator output

If the validation's output can not be mapped to `reason`, `reason` should be
set to `unknown`.
If a fatal exception is caught after validation, the connection should be
terminated.

#### Examples
```
< [{"cmd": "HelloWorld"}]
> [{"cmd": "ErrorReply", "name": "HelloWorld", "reason": "unknown cmd"}]
```
```
< [{"cmd": "Sync", "slot": "Unknown Slot"}]
> [{"cmd": "ErrorReply", "name": "Sync", "argument": "slot",
    "reason": "bad value"}]
```
