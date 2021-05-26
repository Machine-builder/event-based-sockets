# event-based-sockets
#### by MACHINE_BUILDER

**ebsockets** is a python library aiming to simplify server-client systems.

the whole system is designed to be easy to use, and it's setup to use events.
events are basically containers of information, which contain an `event_type`, and `data`
`data` in an event is in the form of `key: value` pairs, which allows for easy read & write functionality.

events can be sent and recieved by the server system & client systems easily, with just a single
function - `client.send_event(...)` will send an event class instance to the connected server,
`client.recv_event()` can also be used to receive a single event from the server,
and `client.pump()` is used to receive all of the events that the server might've sent.
