from channels.routing import route
from apps.auth_chat.consumers import ws_connect, ws_disconnect, ws_post


channel_routing = [
	route('websocket.connect', ws_connect),
	route('websocket.disconnect', ws_disconnect),
	route("websocket.receive", ws_post),
]
