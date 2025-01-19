# Overview

This game is used by the client and the server and is more modularized
(though very much imperfectly) to allow for an easier mental model and
code reuse compared to V1.  It aims to mainly separate out the network
code from the game code, giving a consistent interface for the client
and server to communication.  Additionally, it separates out the
async functionality from the pygame for easier comprehension of what
is happening.