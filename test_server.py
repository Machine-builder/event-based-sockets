from ebsockets import connections

server = connections.ebsocket_server(7982)
system = connections.ebsocket_system(server)

print(f"Server hosting on : {server.address[0]}:{server.address[1]}")

while True:
    
    new_clients, new_events, disconnected_clients = system.pump()

    for new_client in new_clients:
        connection, address = new_client
        print(f"New connection: {connection}:{address}")
    
    for event in new_events:
        print(f"New event: {event}")
        from_connection = event.from_connection
        system.send_event_to(
            from_connection,
            connections.ebsocket_event('response', status='OK'))
        
        message_content = event.get_attribute('content')
        if message_content is not None:
            system.send_event_to_clients(
                connections.ebsocket_event('message', content=message_content))
        
        if event.compare_type('periodic'):
            print("Periodic message content", event.get_attribute('content'))
    
    for client in disconnected_clients:
        print(f"Client disconnected {client[1][0]}:{client[1][0]}")