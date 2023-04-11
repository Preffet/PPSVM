import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# ANSI escape codes to print coloured/bold text
class colours:
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    GREEN = '\033[92m'
    RED = '\033[91m'


def send_email():
    # get the path to the admin email addresses
    path_to_emails = os.path.dirname(os.path.dirname(__file__))
    path_to_emails = path_to_emails + "/email/admin_email.csv"
    file = open(path_to_emails, "r")
    admin_emails_string = file.read()
    admin_emails_list = admin_emails_string.split(",")
    file.close()

    port = 465  # For SSL
    # this is Google App password for sending emails,
    # not an actual Google account password
    password = 'gcjdhpydrjstnibz'
    sender_email = 'a15764291@gmail.com'

    # get the path to the email html document
    email_html = os.path.dirname(os.path.dirname(__file__))
    email_html = email_html + "/Email/real_implementation_email.html"
    with open(email_html, 'r', encoding='utf-8') as f:
        html_string = f.read()

    # get the path to the blocklist.csv file
    path_to_blocklist_csv = os.path.dirname(__file__)
    path_to_blocklist_csv = path_to_blocklist_csv + "/detection_system_files/blocklist.csv"
    # get the path to the received malicious data
    path_to_malicious_data = os.path.dirname(__file__)
    path_to_malicious_data = path_to_malicious_data + "/detection_system_files/malicious_data_received.csv"

    # get the names of the malicious devices
    first_words_in_line = []
    with open(path_to_blocklist_csv, "r") as file:
        for line in file:
            first_words_in_line.append(line.split(',')[0])
    malicious_devices = ', '.join(map(str, first_words_in_line[1:]))

    # replace placeholder text with the actual data
    html_string = html_string.replace("{device_names}", malicious_devices)

    try:
        # format the email
        message = MIMEMultipart()
        message['Subject'] = "Potential Malicious Nodes Identified on Network"
        message['From'] = sender_email
        message['To'] = admin_emails_string
        # Attach the html doc defined earlier, as a MIMEText html content type to the MIME message
        message.attach(MIMEText(html_string, "html"))
        # Attach the blocklist file
        attach_file_to_email(message, path_to_blocklist_csv, filename="blocklist.csv")
        # Attach received malicious data
        attach_file_to_email(message, path_to_malicious_data, filename="anomalous_data.csv")
        # Convert it as a string
        email_string = message.as_string()

        # send the email
        server = smtplib.SMTP_SSL("smtp.gmail.com", port)
        server.login(sender_email, password)
        server.sendmail(sender_email, admin_emails_list, email_string)
        server.quit()
        print(f"\n{colours.BOLD}{colours.GREEN}Email sent successfully{colours.ENDC}\n")
    except:
        print(f"\n{colours.BOLD}{colours.RED}Unable to send the email to the administrators, make sure that the admin_email.csv file is not empty and that you are connected to the Internet (not the Arduino gateway).{colours.ENDC}\n")
        return


def attach_file_to_email(email_message, file, filename):
    # Open the attachment file for reading in binary mode, and make it a MIMEApplication class
    with open(file, "rb") as f:
        file_attachment = MIMEApplication(f.read())
    # Add header/name to the attachments
    file_attachment.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )
    # Attach the file to the message
    email_message.attach(file_attachment)


def main():
    send_email()


if __name__ == "__main__":
    main()
