import csv
import os
import socket
import sys
import threading
from datetime import datetime
import smtplib

# variables for sending/receiving data
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import make_msgid


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

                # send received data to the cloud to be checked
                # and get the decision whether the data is anomalous
                # if it is, inform the administrators and add the ip
                # to the blocklist
                decision = handle_cloud(msg)
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

                    # Inform the node that it got blocked
                    message = "blocked"
                    conn.send(message.encode(FORMAT))
                    # email the administrators the information about the malicious node
                    # and updated blocklist
                    send_email(str(currentDateAndTime)[0:10], str(currentDateAndTime)[11:19], f"{addr[0]}:{addr[1]}", msg.decode())
                    # close the connection
                    connected = False
                    conn.close()

                # if the data is valid, inform the client
                else:
                    message = "valid"
                    conn.send(message.encode(FORMAT))
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
    print(f"{colours.BOLD}{colours.YELLOW}✦{colours.ENDC}"
              f"{colours.ENDC} Sent data to SVM:"
              f"{colours.BOLD}{colours.YELLOW} {int(data_to_send[0])},{int(data_to_send[1])}{colours.ENDC}")

    # receive the decision if the data is malicious
    decision = cloud_server.recv(SIZE).decode(FORMAT)
    # print information about the decision,
    # decision: {decision}
    if decision == "valid":
        print(f"{colours.BOLD}{colours.GREEN}✦{colours.ENDC}"
              f"{colours.ENDC} Returned decision:"
              f"{colours.BOLD}{colours.GREEN} {decision}{colours.ENDC}\n ")
    else:
        print(f"{colours.BOLD}{colours.RED}✦{colours.ENDC}"
              f"{colours.ENDC} Returned decision:"
              f"{colours.BOLD}{colours.RED} {decision}{colours.ENDC}\n ")
    return decision


def send_email(date,time,ip,data):

    # get admin email addresses
    file = open("Email/adminEmail.csv", "r")
    adminEmailAddress = file.read()
    file.close()

    port = 465  # For SSL
    password = 'gcjdhpydrjstnibz'
    sender_email = 'a15764291@gmail.com'
    receiver_email = adminEmailAddress

    # get the email html document
    with open('Email/email.html', 'r',encoding='utf-8') as f:
        html_string = f.read()

    # replace placeholder text with the actual data
    html_string = html_string.replace("{date}", date).replace("{time}", time).replace("{ip}", ip).replace("{data}", data)

    # format the email
    message = MIMEMultipart()
    message['Subject'] = "Potential Malicious Node Identified on Network"
    message['From'] = sender_email
    message['To'] = receiver_email
    # Attach the html doc defined earlier, as a MIMEText html content type to the MIME message
    message.attach(MIMEText(html_string, "html"))
    # Attach the blocklist file
    attach_file_to_email(message,"blocklist.csv")
    # Convert it as a string
    email_string = message.as_string()

    # send the email
    server = smtplib.SMTP_SSL("smtp.gmail.com", port)
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, email_string)
    server.quit()

def attach_file_to_email(email_message, filename):
    # Open the attachment file for reading in binary mode, and make it a MIMEApplication class
    with open("detectionSystemFiles/blocklist.csv", "rb") as f:
        file_attachment = MIMEApplication(f.read())
    # Add header/name to the attachments
    file_attachment.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )
    # Attach the file to the message
    email_message.attach(file_attachment)

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
        os._exit(1)


if __name__ == "__main__":
    main()
