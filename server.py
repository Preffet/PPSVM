import socket
import sys
import threading
from datetime import datetime
import SVM

# variables for sending/receiving data
IP = socket.gethostbyname('localhost')
PORT = 5568
ADDR = (IP, PORT)
SIZE = 1024
FORMAT = "utf-8"

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

# Handle the communication between the server and the client
def handle_client(conn, addr):
    # Print information when a new connection is received
    # New connection from {IP}:{PORT}
    print(f"\n{colours.BOLD}{colours.CYAN}⫸{colours.ENDC}"
          f" New connection from {colours.BOLD}{colours.CYAN}{addr[0]}:{addr[1]}\n",end = '')
    # Add the client to the clients.csv and assign id if the client does not already exist
    with open("detectionSystemFiles/clients.csv", "r+") as file:
        id = len(file.readlines())+1
        if not(f"{addr[0]}:{addr[1]}" in file.read()):
            with open("detectionSystemFiles/clients.csv", "a") as f:
                f.write(f"{id},{addr[0]}:{addr[1]}\n")
    connected = True

    # Run while the client is connected
    while connected:
        # check if the connected client is not in the blocklist,
        # if not, receive the message, else close the connection
        malicious = False
        with open("detectionSystemFiles/blocklist.csv", "a+") as blocklist:
            if not (f"{addr[0]}:{addr[1]}" in blocklist.read()):
                msg = conn.recv(SIZE).decode(FORMAT)

            # if the message is empty, close the connection
            # but do not add the client to the blocklist
            if not(len(msg) <= 0):

                # Print the message: Message from {IP}:{PORT} : {MESSAGE}
                print(f"{colours.BOLD}{colours.YELLOW}✦{colours.ENDC}"
                                  f"{colours.ENDC} Message from {addr[0]}:{addr[1]} :{colours.BOLD}{colours.YELLOW} {msg}{colours.ENDC}")

                # convert data to the required format

                dataToCheck = [float(x) for x in msg.split(",")]
                # check if it is anomalous using one class SVM
                # if it is, inform the administrators and add the ip
                # to the blocklist
                if not SVM.anomaly_detection(dataToCheck).size == 0:
                    malicious=True
                    # add ip to the blocklist
                    print(f"\n{colours.BOLD}{colours.RED}⫸{colours.ENDC}"
                                      f" Malicious data received: {colours.BOLD}{colours.RED}"
                                      f"{dataToCheck[0]},{dataToCheck[1]}{colours.ENDC}", end='')
                    currentDateAndTime = datetime.now()
                    blocklist.write(f"{addr[0]}:{addr[1]},{currentDateAndTime}\n")
                    print(f"\n{colours.BOLD}{colours.RED}⫸{colours.ENDC}"
                                          f" IP added to the blocklist: {colours.BOLD}"
                                          f"{colours.RED}{addr[0]}:{addr[1]}{colours.ENDC}", end='')
                # close the connection
                if(malicious):
                    connected=False
                # Send the message back that it was
                # received, if the message was not malicious
                conn.send(msg.encode(FORMAT))
            else:
                connected = False
    conn.close()
    # Print information about the closed connection
    # Connection closed {IP}:{PORT},
    # reason: {reason for closing the connection}
    reason = "closed by the client" if not malicious else "malicious node"
    print(f"\n{colours.BOLD}{colours.RED}⫸{colours.ENDC}"
          f" Connection closed {colours.BOLD}{colours.RED}"
          f"{addr[0]}:{addr[1]}{colours.ENDC}")
    print(f"   Reason: "
          f"{colours.BOLD}{colours.RED}{reason}{colours.ENDC} \n", end='')
    # Print the number of currently active connections
    print(f"{colours.BOLD}{colours.GREEN}⫸{colours.ENDC}"
          f" Active connections: {colours.BOLD}{colours.GREEN}{threading.activeCount() - 2}\n{colours.ENDC}")

def main():
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(ADDR)
        server.listen()
        # Print information: Listening on {IP}:{PORT}
        print(f"\n{colours.BOLD}{colours.BLUE}〘{colours.ENDC}"
                  f" The server is listening on {colours.BOLD}{colours.GREEN}{IP}:{PORT}{colours.YELLOW} 〙{colours.ENDC}")
        print(f"{colours.BLUE}------------{colours.CYAN}------------{colours.GREEN}----------"
                  f"{colours.YELLOW}------------{colours.ENDC}")

        # Main program loop
        while True:
            # Wait for the client to connect and accept the connection
            conn, addr = server.accept()
            # Create a separate thread to handle the client
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            # Print information about active connections.
            # Active connections: {number of active connections}
            print(f"{colours.BOLD}{colours.GREEN}⫸{colours.ENDC}"
                      f" Active connections: {colours.BOLD}{colours.GREEN}{threading.activeCount() - 1}\n")

    # Quit if errors occur
    except:
        sys.exit()

if __name__ == "__main__":
    main()
