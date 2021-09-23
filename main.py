from server.websocket_server import WebsocketServer
from server.socketServer import new_client, client_left, message_received

PORT = 8040
OutPORT = 30040

if __name__ == '__main__':
    # Timer(UPDATE_TIME, upDateDevice).start()
    print("start socket server @ 0.0.0.0:" + str(PORT) + " @ 0.0.0.0:" + str(OutPORT))
    server = WebsocketServer(PORT, host="0.0.0.0")
    server.set_fn_new_client(new_client)
    server.set_fn_client_left(client_left)
    server.set_fn_message_received(message_received)
    server.run_forever()