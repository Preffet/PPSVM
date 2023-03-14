import socket
import sys
import threading

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

def append_blocklist(ip,port,reason):
    f = open("blocklist.txt", "a")
    f.write("Now the file has more content!")
    f.close()

# Handle the communication between the server and the client
def handle_client(conn, addr):
    # Print information when a new connection is received
    # New connection from {IP}:{PORT}
    print(f"\n{colours.BOLD}{colours.CYAN}⫸{colours.ENDC}"
          f" New connection from {colours.BOLD}{colours.CYAN}{addr[0]}:{addr[1]}\n",end = '')

    connected = True
    # Run while the client is connected
    while connected:
        # Receive the message, if it is empty,
        # add the ip to the watchlist, close the connection
        msg = conn.recv(SIZE).decode(FORMAT)
        if (len(msg)<=0):
            connected = False
        else:
            # Print the message: Message from {IP}:{PORT} : {MESSAGE}
            print(f"{colours.BOLD}{colours.YELLOW}✦{colours.ENDC}"
                  f"{colours.ENDC} Message from {addr[0]}:{addr[1]} :{colours.BOLD}{colours.YELLOW} {msg}")
            # Send the message back that it was received
            conn.send(msg.encode(FORMAT))
    conn.close()
    # Print information about the closed connection
    # Connection closed {IP}:{PORT},
    # reason: {reason for closing the connection}
    print(f"\n{colours.BOLD}{colours.RED}⫸{colours.ENDC}"
          f" Connection closed {colours.BOLD}{colours.RED}"
          f"{addr[0]}:{addr[1]}{colours.ENDC}")
    print(f"   Reason: "
          f"{colours.BOLD}{colours.RED}test{colours.ENDC} \n", end='')
    # Print the number of currently active connections
    print(f"{colours.BOLD}{colours.GREEN}⫸{colours.ENDC}"
          f" Active connections: {colours.BOLD}{colours.GREEN}{threading.activeCount() - 1}\n")

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

    # Print "Quitting.." and stop the program
    # when a user or programmer interrupts a program's usual execution.
    except KeyboardInterrupt:
        print(f"\n{colours.BOLD}{colours.RED}Quitting...{colours.ENDC}")
        sys.exit()

if __name__ == "__main__":
    main()
