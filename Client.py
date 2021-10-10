import socket
import select
import msvcrt
from datetime import date, datetime, timedelta

# 12.6 Client Neta Itshayek

CLIENT_IP = "127.0.0.1"
CLIENT_PORT = 5555
client_input = ""


def send_request_to_server(my_socket, request, name, time_now, private_message):
    minute = "0"
    if time_now.minute < 10:
        minute = minute + str(time_now.minute)
    else:
        minute = str(time_now.minute)

    new_request = ""
    command = "0"
    if request == "quit" or "@Neta is a manager now" or "view-managers":
        command = "1"

    else:
        command = request[0]
        request = request[1:]

    if command == "1" or "2" or "3" or "4":
        zfill_name = str(len(name)).zfill(4)
        request_length = str(len(request))
        zfill_length = request_length.zfill(4)
        new_request = zfill_name + name + command + zfill_length + request
        my_socket.send(new_request.encode())

    if command == "5":
        zfill_name = str(len(name)).zfill(4)
        request_length = str(len(request))
        zfill_length = request_length.zfill(4)
        zfill_private_message = str(len(private_message)).zfill(4)
        new_request = zfill_name + name + command + zfill_length + request + zfill_private_message + private_message
        my_socket.send(new_request.encode())


def handle_server_response(my_socket):
    length = my_socket.recv(4).decode()

    if length.isdigit():
        data = my_socket.recv(int(length)).decode()
        return data
    else:
        return "Error"


def listen_for_data():
    while msvcrt.kbhit():
        key = msvcrt.getch()
        if key == b'\r':
            return True
        else:
            global client_input
            client_input += key.decode("utf-8")
    return False


def main():
    # open socket with the server
    my_socket = socket.socket()
    my_socket.connect((CLIENT_IP, CLIENT_PORT))

    print('Hey:)\n')
    print("***List of commands***\n"
          "1 - Message\n "
          "2 - Appointment of a manager\n"
          "3 - Kick user\n"
          "4 - Mute user\n"
          "5 - Private message\n"
          "quit\n"
          "view-managers")

    name = input("Please enter your name:\n")
    while "@" in name:
        print("Please enter without a @, try again")
        name = input("Please renter your name:\n"
                     "**without a @")
    print("Before requesting write the command number- \n"
          "** 1/2/3/4/5 **")
    if name == "Neta":
        name = "@Neta"
        print("@Neta is a manager now")

    finished = False
    private_message = ""
    count = 0
    time_now = datetime.now()
    muted_client = ""
    kicked_name = ""
    other_name = ""

    # loop until user requested to exit
    while not finished:
        rlist, wlist, xlist = select.select([my_socket], [my_socket], [])
        global client_input

        if count == 0 and name == "@Neta":
            count += 1
            for other_socket in wlist:
                time_now = datetime.now()
                send_request_to_server(other_socket, "@Neta is a manager now", name, time_now, private_message)

        for current_socket in rlist:
            data = handle_server_response(current_socket)
            if "@" in data and name in data and data[-1] == "2":
                name = "@" + name
            if name in data and "cannot speak here" in data and data[-1] == "4":
                muted_client = name
            if "!" in data and ":" in data and data.split("$")[0] == name and data[-1] == "5":
                other_name = name
            if name in data and "has been kicked from the chat" in data and data[-1] == "3":
                kicked_name = name
                print(data[0:-1])
                send_request_to_server(current_socket, "quit", kicked_name, time_now, private_message)
                finished = True
            else:
                if data[-1] != "5":
                    if "has left the chat!" in data or "@Neta is a manager now" in data:
                        print(data)
                    else:
                        print(data[0:-1])
                else:
                    if other_name == name:
                        data = data.split("$")[1]
                        print(data[0:-1])

        if listen_for_data():
            for other_socket in wlist:
                time_now = datetime.now()
                if client_input[0] == "5":
                    private_message = input("Enter your private message: ")
                if client_input == "quit":
                    send_request_to_server(other_socket, client_input, name, time_now, private_message)
                    done = True
                else:
                    if muted_client != name:
                        send_request_to_server(other_socket, client_input, name, time_now, private_message)
                    else:
                        print("You cannot speak here")
            client_input = ''

    my_socket.close()


if __name__ == '__main__':
    main()
