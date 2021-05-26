from ebsockets import connections

client = connections.ebsocket_client()

ip = input("ip >>> ") or connections.utility.get_local_ip()
port = int(input("port >>> ") or 7982)

print(f"Connecting to {ip}:{port}")
client.connect_to((ip,port))

while True:
    message_content = input("send event >>> ")

    if message_content:
        send_event = connections.ebsocket_event('message', content=message_content)
        print(f"Sending event {send_event}...")
        client.send_event(send_event)
    
    events, connected = client.pump()

    for event in events:
        print(f"New event received {event}")