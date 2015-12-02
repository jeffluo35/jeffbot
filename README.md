# jeffbot
A little irc bot

## Functions
List of functions in jeffbot
#### send(data)
Send ```data``` to server, also logging to stdout
#### join(chan)
Join ```chan``` on the irc server
#### pong()
Checks for pings from the server, and responds appropriately, in main loop
#### read(bytes)
Reads ```bytes``` from the socket, and strips newlines
#### initjoin(chan)
Do not use, only used in initial join
#### main()
The main loop
