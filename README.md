---
# event-based-sockets
##### by MACHINE_BUILDER
###
---
### Systems Overview
---

`ebsockets` is a python library aiming to simplify server-client systems.

the whole system is designed to be easy to use, and it's setup to use events.  
events are basically containers of information, which contain an `event_type`, and `data`  
`data` in an event is in the form of `key: value` pairs, which allows for easy read & write functionality.

events can be sent and recieved by the server system & client systems easily, with just a few  
simple functions.

For the client, these are the main functions:  
`client.send_event(...)` will send an event class instance to the connected server,  
`client.recv_event()` can also be used to receive a single event from the server,  
and `client.pump()` is used to receive all of the events that the server might've sent.

And for a server system, these are the main functions:  
`system.pump()` can be used to receive all new events - it also returns lists of useful  
information, such as new connections, and disconnected clients.  
`system.send_event_to(...)` can be used to send an event to a specific client,  
`system.send_event_to_clients(...)` is like `system.send_event_to()`, but
this function sends an event to all clients currently connected.

---
### Code examples
---

Here's a basic server, which just relays any received events out to all clients.

```python
# import ebsockets.connections
import ebsockets

# initialise a server class
server = ebsockets.connections.ebsocket_server(7982)
# initialise the system with the server class we created above
system = ebsockets.connections.ebsocket_system(server)

# display the server's ip and port
print(f"Server hosting on : {server.address[0]}:{server.address[1]}")

while True:
    # get main server information from system.pump()
    new_clients, new_events, disconnected_clients = system.pump()

    # iterate through all new clients & print their connections
    for new_client in new_clients:
        connection, address = new_client
        print(f"New connection: {connection}:{address}")
    
    # iterate through all new events & forward on to all clients
    for event in new_events:
        print(f"New event: {event}")
        # check if the event is a message
        if event.compare_type('message'):
            message_content = event.get_attribute('content')
            # create a new event with the same message content as the original event
            system.send_event_to_clients(
                ebsockets.connections.ebsocket_event('message', content=message_content))
    
    # iterate through clients who've disconnected, and print their connections
    for client in disconnected_clients:
        print(f"Client disconnected {client[1][0]}:{client[1][0]}")
```
