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
                msg = conn.recv(SIZE)

            # if the message is empty, close the connection
            # but do not add the client to the blocklist
            if not(len(msg) <= 0):

                # Print the message: Message from {IP}:{PORT} : {MESSAGE}
                print(f"{colours.BOLD}{colours.YELLOW}✦{colours.ENDC}"
                                  f"{colours.ENDC} Message from {addr[0]}:{addr[1]}:"
                      f"{colours.BOLD}{colours.YELLOW} {msg.decode(FORMAT)}{colours.ENDC}",end = '')



                # check if the received data is anomalous using one class SVM
                # send received data to the cloud to be checked
                # and get the decision whether the data is anomalous
                decision = handle_cloud(msg)

                # if it is, inform the administrators and add the ip
                # to the blocklist
                if not decision == "valid":
                    malicious = True
                    data = [int(x) for x in msg.decode().split(",")]
                    # Print malicious data received: {data}
                    print(f"\n{colours.BOLD}{colours.RED}⫸{colours.ENDC}"
                                      f" Malicious data received: {colours.BOLD}{colours.RED}"
                                      f"{int(data[0])},{int(data[1])}{colours.ENDC}", end='')
                    # add ip to the blocklist
                    currentDateAndTime = datetime.now()
                    blocklist.write(f"{addr[0]}:{addr[1]},{currentDateAndTime}\n")
                    # Print: IP added to the blocklist {IP}
                    print(f"\n{colours.BOLD}{colours.RED}⫸{colours.ENDC}"
                                          f" IP added to the blocklist: {colours.BOLD}"
                                          f"{colours.RED}{addr[0]}:{addr[1]}{colours.ENDC}", end='')

                    # Inform the node that it got blocked and
                    # close the connection
                    msg = "blocked"
                    conn.send(msg.encode(FORMAT))
                    connected = False
                    conn.close()
            else:
                connected = False
                conn.close()
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


# Handle the communication between the
# server and the cloud (SVM)
def handle_cloud(msg):
    port = 59999
    address = (IP, port)

    # set up the server-cloud connection
    cloud_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cloud_server.connect(address)

    data_to_send = [float(x) for x in msg.decode(FORMAT).split(",")]

    cloud_server.send(msg)
    # send received data to the cloud

    # print information: sent data to SVM: {data}
    print(f"{colours.BOLD}{colours.ORANGE}✦{colours.ENDC}"
              f"{colours.ENDC} Sent data to SVM:"
              f"{colours.BOLD}{colours.ORANGE} {int(data_to_send[0])},{int(data_to_send[1])}{colours.ENDC}")

    # receive the decision if the data is malicious
    decision = cloud_server.recv(SIZE).decode(FORMAT)
    # print information about the decision,
    # decision: {decision}
    print(f"{colours.BOLD}{colours.ORANGE}✦{colours.ENDC}"
          f"{colours.ENDC} Returned decision:"
          f"{colours.BOLD}{colours.ORANGE} {decision}{colours.ENDC}\n ")
    return decision

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
        print("error")
        sys.exit()


if __name__ == "__main__":
    main()
