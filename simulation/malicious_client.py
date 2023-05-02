import os
import random
import socket
import time
import sys

# Public variables
# message size
SIZE = 1024
# message format
FORMAT = "utf-8"
# ip address used for client-server connection
IP = socket.gethostbyname('localhost')
# port number used for client-server connection
PORT = 1223
# full address
ADDR = (IP, PORT)


# ANSI escape codes to print coloured/bold text
class Colours:
    ENDC = '\033[0m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    ORANGE = '\033[38;5;173m'


# Program entry point
def main():
    # Connect to the server
    connected = False
    # Catch the errors that occur when setting up the client
    try:
        # set up sockets
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDR)
        connected = True
        # Print the header - client IP address {IP}:{PORT}
        print(f"\n       "
              f" Client IP "
              f"{Colours.BOLD}{Colours.BLUE}"
              f"{client.getsockname()[0]}:{client.getsockname()[1]}"
              f"{Colours.ENDC}")
        # Print the header - connected to the server at {IP}:{PORT}
        print(f"{Colours.BOLD}{Colours.BLUE}〘{Colours.ENDC}"
              f" Connected to the server at {Colours.BOLD}{Colours.GREEN}{IP}:{PORT}{Colours.YELLOW} 〙{Colours.ENDC}")
        print(f"{Colours.BLUE}------------{Colours.CYAN}------------{Colours.GREEN}------------"
              f"{Colours.YELLOW}----------{Colours.ENDC}\n")
    except:
        connected = False
        print(f"\n{Colours.BOLD}{Colours.RED}Could not connect to the server. Quitting...{Colours.ENDC}")
        sys.exit()

    # send malicious data every 10s
    # when connected to the server
    while connected:
        # sleep for 10s
        time.sleep(10)
        try:
            # get the path to the file with the malicious data
            path_to_data = os.path.dirname(os.path.dirname(__file__))
            path_to_data = path_to_data + "/datasets/invalid_light_data.csv"
            # read a random line from the dataset containing invalid sensor readings
            with open(path_to_data) as file:
                lines = file.readlines()
                message = random.choice(lines[1:])
            # print >Sent: {data sent}
            print(f"{Colours.BOLD}{Colours.CYAN}⫸"
                  f"{Colours.ENDC} Sent: "
                  f"{Colours.BOLD}{Colours.CYAN}"
                  f"{message}{Colours.ENDC}", end='')
            # send the message to the server
            client.send(message.encode(FORMAT))

            # check if the node got blocked,
            # if yes, print the information and quit
            rcv_msg = client.recv(SIZE).decode(FORMAT)
            if rcv_msg == "blocked":
                # print the data the server received
                print(f"{Colours.BOLD}{Colours.RED}⫸"
                      f"{Colours.ENDC} Blocked by the server, the data was"
                      f" {Colours.BOLD}{Colours.RED}"
                      f"malicious{Colours.ENDC}\n")
                connected = False
            else:
                # print the data the server received
                print(f"{Colours.BOLD}{Colours.YELLOW}✦"
                      f"{Colours.ENDC}Received by the server:"
                      f" {Colours.BOLD}{Colours.YELLOW}"
                      f"{message}{Colours.ENDC}\n")

        # if any errors occur, inform the user
        # that the message could not be sent and quit
        except:
            print(f"\n{Colours.BOLD}{Colours.RED}"
                  f"Could not send the message. Quitting..."
                  f"{Colours.ENDC}")
            sys.exit()


if __name__ == "__main__":
    main()
