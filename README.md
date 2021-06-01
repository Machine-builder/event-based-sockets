---
# event-based-sockets
##### by MACHINE_BUILDER
###
---
### Systems Overview
---

`ebsockets` is a python library aiming to simplify server-client systems.

the whole system is designed to be easy to use, and it's setup to use events.  
events are basically containers of information, which contain an `event`, and `__dict__` attribute  
`__dict__` in an event is in the form of `key: value` pairs, which allows for easy read & write functionality.

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
### Code Examples
---

Here's a basic server, which just relays any received events out to all clients.

```python
# import ebsockets so we can use its classes
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

Here is a basic client script, which can connect to a server and send messages

```python
# import ebsockets so we can use its classes
import ebsockets

# initialise a client, which we'll connect to the server with
client = connections.ebsocket_client()

# ask the user for the server ip and port, and use preset defaults
ip = input("ip >>> ") or connections.utility.get_local_ip()
port = int(input("port >>> ") or 7982)
# if nothing is entered above, the ip will be the local ip, and port will be 7982

print(f"Connecting to {ip}:{port}")
# try to connect to the server address
client.connect_to((ip,port))

while True:
    # ask the user to type something
    message_content = input("send event >>> ")

    # check if the user actually entered any text, or left the input blank
    if message_content:
        # create and send a new "message" event to the server, with a content attribute
        send_event = connections.ebsocket_event('message', content=message_content)
        client.send_event(send_event)
    
    # use client.pump() to see server responses
    events, connected = client.pump()

    # iterate through all new server events, and print them
    for event in events:
        print(f"New event received {event}")
        if event.compare_type('message'):
            print(event.get_attribute('content'))
```

---
### Extra Notes
---

feel free to create pull requests to fix any bugs you might find!
this project is in incredibly early development, so there's probabaly a few lurking
