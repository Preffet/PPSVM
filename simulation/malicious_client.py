import os
import random
import socket
import time
import sys

IP = socket.gethostbyname('localhost')
SIZE = 1024
FORMAT = "utf-8"
PORT = 5568
ADDR = (IP, PORT)


# ANSI escape codes to print coloured/bold text
class colours:
    ENDC = '\033[0m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    ORANGE = '\033[38;5;173m'


def main():
    # Connect to the server
    connected = False
    # Catch the errors that occur when setting up the client
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDR)
        connected = True
        # Print the header - client IP address {IP}:{PORT}
        print(f"\n       "
              f" Client IP "
              f"{colours.BOLD}{colours.BLUE}"
              f"{client.getsockname()[0]}:{client.getsockname()[1]}"
              f"{colours.ENDC}")
        # Print the header - connected to the server at {IP}:{PORT}
        print(f"{colours.BOLD}{colours.BLUE}〘{colours.ENDC}"
              f" Connected to the server at {colours.BOLD}{colours.GREEN}{IP}:{PORT}{colours.YELLOW} 〙{colours.ENDC}")
        print(f"{colours.BLUE}------------{colours.CYAN}------------{colours.GREEN}------------"
              f"{colours.YELLOW}----------{colours.ENDC}\n")
    except:
        connected = False
        print(f"\n{colours.BOLD}{colours.RED}Could not connect to the server. Quitting...{colours.ENDC}")
        sys.exit()

    while connected:
        # Sleep for a bit
        time.sleep(10)
        try:
            # get the path to the file with the valid data
            path_to_data = os.path.dirname(os.path.dirname(__file__))
            path_to_data = path_to_data + "/datasets/invalid_light_data.csv"
            # Read a random line from the dataset containing valid sensor readings
            with open(path_to_data) as f:
                lines = f.readlines()
                msg = random.choice(lines[1:])
            print(f"{colours.BOLD}{colours.CYAN}⫸{colours.ENDC} Sent: "
                  f"{colours.BOLD}{colours.CYAN}{msg}{colours.ENDC}", end='')
            # Send the message to the server
            client.send(msg.encode(FORMAT))

            # Check if the node got blocked, if yes, inform the user and quit
            rcv_msg = client.recv(SIZE).decode(FORMAT)
            if rcv_msg == "blocked":
                # print the data the server received
                print(f"{colours.BOLD}{colours.RED}⫸{colours.ENDC} Blocked by the server, the data was"
                      f" {colours.BOLD}{colours.RED}malicious{colours.ENDC}\n")
                connected = False
            else:
                # print the data the server received
                print(f"{colours.BOLD}{colours.YELLOW}✦{colours.ENDC}Received by the server:"
                      f" {colours.BOLD}{colours.YELLOW}{msg}{colours.ENDC}\n")
        except:
            print(f"\n{colours.BOLD}{colours.RED}Could not send the message. Quitting...{colours.ENDC}")
            sys.exit()


if __name__ == "__main__":
    main()