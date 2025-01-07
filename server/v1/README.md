# Server V1

## Overview
This is a V1 of the game server.  It's main concerns are allowing clients
to connect with unique ids, have a session, have a simple api for all needed
communictation, getting other player information, and having a working prototype.

It is not concerned with sercurity/encryption of server/client communications,
session/player persistence, having multiple lobbies per host and other 
similarly fancy features.

Everything is namespaced with `v1` to help make it clear to migrate to `v2`
int the future.
