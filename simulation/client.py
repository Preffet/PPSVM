import os
import random
import socket
import time
import sys

# Public variables
# IP address used for client-server connection
from datetime import datetime

IP = socket.gethostbyname('localhost')
# port used for client-server connection
PORT = 1228
# full address
ADDR = (IP, PORT)
# message size
SIZE = 1024
# message format
FORMAT = "utf-8"


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
    # Try to connect to the server
    connected = False
    try:
        # setup sockets
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
              f" Connected to the server at {Colours.BOLD}{Colours.GREEN}"
              f"{IP}:{PORT}{Colours.YELLOW} 〙{Colours.ENDC}")
        print(f"{Colours.BLUE}------------{Colours.CYAN}------------{Colours.GREEN}------------"
              f"{Colours.YELLOW}----------{Colours.ENDC}\n")
    # Catch the errors that occur when setting up the connection
    except:
        connected = False
        print(f"\n{Colours.BOLD}{Colours.RED}"
              f"Could not connect to the server. Quitting..."
              f"{Colours.ENDC}")
        sys.exit()

    # when client successfully connects to the server
    # every 10s send randomly chosen data from
    # the valid.csv file to simulate an honest sensor node
    while connected:
        try:
            # sleep for a bit
            time.sleep(10)
            # get the path to the current directory
            dir_path = os.path.dirname(os.path.dirname(__file__))

            # check time & pick a valid dataset
            current_hour = 23#datetime.now().hour

            if (6 > current_hour >= 0) or (21 <= current_hour < 24):
                print("night")
                # get the dataset with valid night data
                path_to_data = dir_path + "/datasets/simulation_nodes/valid/night.csv"

            elif 6 <= current_hour < 13:
                print("day1")
                # get the dataset with valid data for the first half of the day
                path_to_data = dir_path + "/datasets/simulation_nodes/valid/day1.csv"

            else:
                print("day2")
                # get the dataset with valid data for the second half of the day
                path_to_data = dir_path + "/datasets/simulation_nodes/valid/day2.csv"

            # Read a random line from the dataset containing valid sensor readings
            with open(path_to_data) as f:
                lines = f.readlines()
                msg = random.choice(lines[1:])
            print(f"{Colours.BOLD}{Colours.CYAN}⫸{Colours.ENDC} Sent: "
                  f"{Colours.BOLD}{Colours.CYAN}{msg}{Colours.ENDC}", end='')
            # send the message to the server
            client.send(msg.encode(FORMAT))
            # receive the message from the server
            msg = client.recv(SIZE).decode(FORMAT)
            # check if the node got blocked, if yes,
            # print the information
            if msg == "blocked":
                # print the data the server received
                # and that the node got blocked
                print(f"\n{Colours.BOLD}{Colours.RED}✦{Colours.ENDC}"
                      f" Blocked by the server for sending"
                      f"{Colours.BOLD}{Colours.RED} "
                      f"malicious data{Colours.ENDC}\n")
                # disconnect
                connected = False
            else:
                # print the data the server received
                print(f"{Colours.BOLD}{Colours.YELLOW}\n✦{Colours.ENDC}"
                      f" Decision received from the server:"
                      f" {Colours.BOLD}{Colours.YELLOW}{msg}{Colours.ENDC}\n")

        # Catch the errors that occur when sending messages
        except:
            print(f"\n{Colours.BOLD}{Colours.RED}"
                  f"Could not send the message. Quitting..."
                  f"{Colours.ENDC}")
            sys.exit()


# Program entry point
if __name__ == "__main__":
    main()
