import socket
import select
from datetime import datetime
from ServerConstants import MANAGER_NAME, RECEIVE_LENGTH_SIZE, COMMAND_LENGTH_SIZE, SERVER_IP, SERVER_PORT

# 12.6 Server Neta Itshayek

client_sockets, messages_to_send, managers, rlist, wlist, xlist = [[], [], [], [], [], []]

def handle_command_1(current_socket, new_time, name, request):
    request = new_time + " " + name + ": " + request + "1"
    print(request)
    messages_to_send.append((current_socket, request))

def handle_command_2(current_socket, new_time, name, request):
    if name in managers and request not in managers:
        managers.append("@" + request)
        request = new_time + " " + "@" + request + " is a manager now" + "2"
        print(request)
        messages_to_send.append((current_socket, request))

def handle_command_3(current_socket, new_time, name, request):
    if name in managers:
        request = new_time + " " + request + " has been kicked from the chat!" + "3"
        print(request)
        messages_to_send.append((current_socket, request))

def handle_command_4(current_socket, new_time, name, request):
    if name in managers:
        request = new_time + " " + request + " cannot speak here" + "4"
        print(request)
        messages_to_send.append((current_socket, request))

def handle_command_5(current_socket, new_time, name, request):
    private_message_length = current_socket.recv(RECEIVE_LENGTH_SIZE).decode()
    private_message = current_socket.recv(int(private_message_length)).decode()
    request = request + "$" + new_time + " !" + name + ": " + private_message + "5"
    print(request)
    messages_to_send.append((current_socket, request))

def handle_quit_message(current_socket, new_time, name, request):
    if name in managers:
        managers.remove(name)
    request = new_time + " " + name + " has left the chat!"
    request_length = str(len(request))
    zfill_length = request_length.zfill(RECEIVE_LENGTH_SIZE)
    request = zfill_length + request
    for new_other_current_socket in wlist:
        if new_other_current_socket is not current_socket:
            new_other_current_socket.send(request.encode())
    print("The connection is closed", )
    client_sockets.remove(current_socket)
    current_socket.close()
    print("\t".join([x.getsockname()[0] for x in client_sockets]))

def handle_view_managers_message(current_socket, new_time, name, request):
    for i in range(len(managers)):
        request = managers[i] + " \n"
        request_length = str(len(request))
        zfill_length = request_length.zfill(RECEIVE_LENGTH_SIZE)
        request = zfill_length + request
        print(request)
        current_socket.send(request.encode())

def handle_manager_initialization_request(current_socket, new_time, name, request):
    request_length = str(len(request))
    zfill_length = request_length.zfill(RECEIVE_LENGTH_SIZE)
    request = zfill_length + request
    for new_other_current_socket2 in wlist:
        if new_other_current_socket2 is not current_socket:
            new_other_current_socket2.send(request.encode())

command_handlers = {
    "1": handle_command_1,
    "2": handle_command_2,
    "3": handle_command_3,
    "4": handle_command_4,
    "5": handle_command_5
}

request_handlers = {
    f"@{MANAGER_NAME} is a manager now": handle_manager_initialization_request,
    "quit": handle_quit_message,
    "view-managers": handle_view_managers_message
}

def run_server():
    print("Setting up server...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen()

    print("Listening for clients...")

    while True:
        rlist, wlist, xlist = select.select([server_socket] + client_sockets, client_sockets, [])
        for current_socket in rlist:
            if current_socket is server_socket:
                current_socket, client_address = current_socket.accept()
                print("New client joined", client_address)
                client_sockets.append(current_socket)
                print("\t".join([x.getsockname()[0] for x in client_sockets]))

            name_length = current_socket.recv(RECEIVE_LENGTH_SIZE).decode()
            name = current_socket.recv(int(name_length)).decode()
            command = current_socket.recv(COMMAND_LENGTH_SIZE).decode()
            request_length = current_socket.recv(RECEIVE_LENGTH_SIZE).decode()
            request = current_socket.recv(int(request_length)).decode()

            if name == f"@{MANAGER_NAME}" and name not in managers:
                managers.append(f"@{MANAGER_NAME}")

            new_time = datetime.now().strftime("%H:%M")
            request_handlers[request](current_socket, new_time, name, request)
            command_handlers[command](current_socket, new_time, name, request)

        for message in messages_to_send:
            current_socket, data = message
            for other_current_socket in wlist:
                if other_current_socket is not current_socket:
                    request_length = str(len(data))
                    zfill_length = request_length.zfill(RECEIVE_LENGTH_SIZE)
                    request = zfill_length + data
                    other_current_socket.send(request.encode())
            messages_to_send.remove(message)

def main():
    run_server()

if __name__ == '__main__':
    main()
