import socket
import select
from datetime import date, datetime, timedelta

# 12.6 Server Neta Itshayek

MAX_MSG_LENGTH = 1024
SERVER_PORT = 5555
SERVER_IP = "0.0.0.0"


def print_client_sockets(client_sockets):
    for c in client_sockets:
        print("\t", c.getpeername())


def return_time(time_now):
    minute = "0"
    if time_now.minute < 10:
        minute = minute + str(time_now.minute)
    else:
        minute = str(time_now.minute)

    time = str(time_now.hour) + ":" + minute
    return time


def main():
    print("Setting up server...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen()
    print("Listening for clients...")
    client_sockets = []
    messages_to_send = []
    managers = []

    while True:
        rlist, wlist, xlist = select.select([server_socket] + client_sockets, client_sockets, [])
        for current_socket in rlist:
            if current_socket is server_socket:
                connection, client_address = current_socket.accept()
                print("New client joined", client_address)
                client_sockets.append(connection)
                print_client_sockets(client_sockets)
            else:
                name_length = current_socket.recv(4).decode()
                name = current_socket.recv(int(name_length)).decode()
                command = current_socket.recv(1).decode()
                request_length = current_socket.recv(4).decode()
                request = current_socket.recv(int(request_length)).decode()

                if command == "5":
                    private_message_length = current_socket.recv(4).decode()
                    private_message = current_socket.recv(int(private_message_length)).decode()

                if name == "@Neta" and name not in managers:
                    managers.append("@Neta")

                current_time = datetime.now()
                new_time = return_time(current_time)
                if request == "@Neta is a manager now":
                    request_length = str(len(request))
                    zfill_length = request_length.zfill(4)
                    request = zfill_length + request
                    for new_other_current_socket2 in wlist:
                        if new_other_current_socket2 is not current_socket:
                            new_other_current_socket2.send(request.encode())
                else:
                    if request == "view-managers":
                        for i in range(len(managers)):
                            request = managers[i] + " \n"
                            request_length = str(len(request))
                            zfill_length = request_length.zfill(4)
                            request = zfill_length + request
                            print(request)
                            current_socket.send(request.encode())
                    else:
                        if request == "quit":
                            if name in managers:
                                managers.remove(name)
                            request = new_time + " " + name + " has left the chat!"
                            request_length = str(len(request))
                            zfill_length = request_length.zfill(4)
                            request = zfill_length + request
                            for new_other_current_socket in wlist:
                                if new_other_current_socket is not current_socket:
                                    new_other_current_socket.send(request.encode())
                            print("The connection is closed", )
                            client_sockets.remove(current_socket)
                            current_socket.close()
                            print_client_sockets(client_sockets)

                        else:
                            if command == "1":
                                request = new_time + " " + name + ": " + request + "1"
                                print(request)
                                messages_to_send.append((current_socket, request))
                            if command == "2" and name in managers and request not in managers:
                                managers.append("@" + request)
                                request = new_time + " " + "@" + request + " is a manager now" + "2"
                                print(request)
                                messages_to_send.append((current_socket, request))
                            if command == "3" and name in managers:
                                request = new_time + " " + request + " has been kicked from the chat!" + "3"
                                print(request)
                                messages_to_send.append((current_socket, request))
                            if command == "4" and name in managers:
                                request = new_time + " " + request + " cannot speak here" + "4"
                                print(request)
                                messages_to_send.append((current_socket, request))
                            if command == "5":
                                request = request + "$" + new_time + " !" + name + ": " + private_message + "5"
                                print(request)
                                messages_to_send.append((current_socket, request))

        for message in messages_to_send:
            current_socket, data = message
            for other_current_socket in wlist:
                if other_current_socket is not current_socket:
                    request_length = str(len(data))
                    zfill_length = request_length.zfill(4)
                    request = zfill_length + data
                    other_current_socket.send(request.encode())
            messages_to_send.remove(message)


if __name__ == '__main__':
    main()
