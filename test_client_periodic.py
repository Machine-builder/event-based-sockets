from ebsockets import connections
import time

client = connections.ebsocket_client()

ip = input("ip >>> ") or connections.utility.get_local_ip()
port = int(input("port >>> ") or 7982)

print(f"Connecting to {ip}:{port}")
client.connect_to((ip,port))

message_delay = 3
next_message_at = time.time()+message_delay
count = 1

while True:
    if time.time() > next_message_at:
        print("Sending periodic message...")
        next_message_at = time.time()+message_delay
        client.send_event(
            connections.ebsocket_event('periodic', content=f'periodic send {count}'))
        count += 1
    
    events, connected = client.pump()

    for event in events:
        print(f"New event received {event}")