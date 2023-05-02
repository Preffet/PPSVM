# Data processing
import numpy as np
from numpy import where
import pandas as pd
# Model and performance
from sklearn import svm
from sklearn.preprocessing import MinMaxScaler
# networking
import socket
# multithreading
import threading


# ANSI escape codes to print coloured/bold text
from sklearn.svm import SVC

from Laplace_dataset_privatiser import DataConverter, LaplacePrivacyPreserver


class colours:
    ENDC = '\033[0m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    ORANGE = '\033[38;5;173m'


# public variables
# message size
SIZE = 1024
# port of the server
SERVER_PORT = 59991
# message format
FORMAT = "utf-8"
# available choices for epsilon values when
# running SVMs in privacy-preserving way
EPSILON_VALUES = [5.0, 4.0, 1.0, 0.5, 0.25]


# function to get the chosen SVM type as
# well as privacy epsilon parameters
# from the user
def get_svm_parameters():
    # small function to print all available epsilon options
    def print_options(epsilon_values):
        print(f"{colours.BOLD}{colours.BLUE}1. {colours.ENDC}{epsilon_values[0]}\n"
              f"{colours.BOLD}{colours.CYAN}2. {colours.ENDC}{epsilon_values[1]}\n"
              f"{colours.BOLD}{colours.GREEN}3. {colours.ENDC}{epsilon_values[2]}\n"
              f"{colours.BOLD}{colours.YELLOW}4. {colours.ENDC}{epsilon_values[3]}\n"
              f"{colours.BOLD}{colours.ORANGE}5. {colours.ENDC}{epsilon_values[4]}\n")

    # small function to check if the entered value is correct
    # and if it is, return it
    def get_value(number_up_to):
        while True:
            try:
                number = input(f"Enter a number between 1 and {number_up_to}: ")
                if number.isdigit():
                    number = int(number)
                else:
                    raise ValueError()
                if 1 <= number <= number_up_to:
                    break
                raise ValueError()
            except ValueError:
                print(f"Input must be an integer between 1 and {number_up_to}.")
        return number

    # get the parameters from the user
    # 1.Ask the user to choose the SVM type:
    # - Not privacy preserving
    # - Preserving dataset privacy
    # - Differentially private SVM
    print(f"\n{colours.BOLD}{colours.BLUE}Choose The SVM Type:{colours.ENDC}\n"
          f"{colours.BOLD}{colours.CYAN}1.{colours.ENDC}Not Private\n"
          f"{colours.BOLD}{colours.GREEN}2.{colours.ENDC}Using Privatised Dataset\n"
          f"{colours.BOLD}{colours.YELLOW}3.{colours.ENDC}Differentially Private SVM\n"
          f"{colours.BOLD}{colours.ORANGE}4.{colours.ENDC}Privatised Dataset + Differentially Private SVM\n")
    svm_type = get_value(4)

    # 2.Ask the user to choose the privacy parameter
    # if they choose option 2, 3, or 4

    # if it is option 2 or 3 ask for one
    # epsilon value
    epsilon1 = 0
    if svm_type in (2, 3):
        print(f"\n{colours.BOLD}{colours.BLUE}Choose The Epsilon Value ",end='')
        if svm_type == 2: print(f"(default is 5.0):{colours.ENDC}")
        if svm_type == 3: print(f"(default is 0.25):{colours.ENDC}")
        print_options(epsilon_values=EPSILON_VALUES)
        epsilon1 = EPSILON_VALUES[get_value(5)-1]

    # if it is option 4 ask for two
    # epsilon values
    # one for dataset privatisation and
    # another for SVM
    epsilon2 = 0
    if svm_type == 4:
        print(f"\n{colours.BOLD}{colours.BLUE}Choose the Epsilon Value for Dataset Privatisation ")
        print(f"(default is 5.0):{colours.ENDC}")
        print_options(epsilon_values=EPSILON_VALUES)
        epsilon1 = EPSILON_VALUES[get_value(5)-1]
        print(f"\n{colours.BOLD}{colours.BLUE}Choose the Epsilon Value for Privacy-Preserving SVM ")
        print(f"(default is 0.25):{colours.ENDC}")
        print_options(epsilon_values=EPSILON_VALUES)
        epsilon2 = EPSILON_VALUES[get_value(5)-1]

    # Print information about the chosen parameters
    # non privatised svm
    if svm_type == 1:
        print(f"{colours.BLUE}"
              f"\nRunning a non-privatised SVM"
              f"{colours.ENDC}")
    # svm using privatised dataset
    if svm_type == 2:
        print(f"{colours.BLUE}"
              f"\nRunning a SVM with a privatised dataset with epsilon"
              f" {epsilon1}{colours.ENDC}")
    # differentially private svm
    if svm_type == 3:
        print(f"{colours.BLUE}"
              f"\nRunning a Differentially-Private SVM with epsilon"
              f" {epsilon1}{colours.ENDC}")
    # differentially private svm with a privatised dataset
    if svm_type == 4:
        print(f"{colours.BLUE}"
              f"\nRunning a Differentially-Private SVM (epsilon {epsilon2})\n"
              f"with a Privatised Dataset (epsilon {epsilon1})"
              f"{colours.ENDC}")
    # separator line (-----)
    print(f"{colours.BLUE}--------------{colours.CYAN}"
          f"--------------{colours.GREEN}--------------"
          f"{colours.YELLOW}--------------{colours.ENDC}")

    # return the SVM choice and epsilon values
    return svm_type, epsilon1, epsilon2


# function to privatise the dataset and get the training data
def privatised_training_dataset(eps):
    # import the dataset (with the headers)
    df = pd.read_csv('../datasets/all_data_including_anomalous.csv',
                     header=0, sep=',')

    # define the scaler
    scaler = MinMaxScaler()

    # get X and y values from the dataset
    X = df.loc[:, ['Float time value', 'Lux']]
    y = df['Label']

    # convert to numpy array
    X = X.values
    y = y.values

    # define data converter
    ad = DataConverter()
    data_input = ad.convert_from_original(X)
    target_values = ad.convert_from_original(y)
    # define the data privatiser
    data_privatiser = LaplacePrivacyPreserver(eps * 10)
    # get data sensitivity value
    input_sensitivity = data_privatiser.get_data_sensitivity_values(data_input)
    privatised_data = data_privatiser.privatise_data(
        data_input,
        sensitivity_values_list=input_sensitivity)
    # normalise the data
    privatised_data = scaler.fit_transform(pd.DataFrame(privatised_data, columns=['Float time value', 'Lux']))
    privatised_data = pd.DataFrame(privatised_data, columns=['Float time value', 'Lux'])
    # could test noisy labels too, but that is future work
    privatised_y_vals = pd.DataFrame(target_values, columns=['Label'])
    # return the privatised dataset and scaler
    return privatised_data, privatised_y_vals, scaler


# function get the training data from a not privatised dataset
def non_privatised_training_dataset():
    # define the scaler
    scaler = MinMaxScaler()
    # import training data, specify that it has a header
    df = pd.read_csv("../datasets/all_data_including_anomalous.csv", header=0)
    # get X and y values from the dataset
    X = df.loc[:, ['Float time value', 'Lux']]
    y = df['Label']
    # convert to numpy array
    #X = X.values
    #y = y.values
    # normalise the training data and convert it back to a pd dataframe
    X_train = scaler.fit_transform(X)
    X_train = pd.DataFrame(X_train, columns=['Float time value', 'Lux'])
    # return training X,y values and the scaler
    return X_train, y, scaler


# function to prepare the received data for predictions
def prepare_received_data(msg, scaler):
    decoded_received_data = [float(x) for x in msg.split(",")]

    # Print the received message
    print(f"\n{colours.BOLD}{colours.BLUE}⫸{colours.ENDC}"
          f" Data received: {colours.BOLD}{colours.BLUE}"
          f"{decoded_received_data[0]},{decoded_received_data[1]}{colours.ENDC}", end='')

    # convert the data to a dataframe
    decoded_received_data = pd.DataFrame([decoded_received_data], columns=['Float time value', 'Lux'])
    # scale it
    decoded_received_data = scaler.transform(decoded_received_data)

    # convert to df again
    data_to_be_predicted = pd.DataFrame(decoded_received_data, columns=['Float time value', 'Lux'])
    return data_to_be_predicted


# function where the anomaly detection is
# done using the chosen SVM type and epsilon values
def anomaly_detection(conn, addr, parameters):

    # if the user choose to use not privatised dataset
    if parameters[0] == 1 or parameters[0] == 3:
        # retrieve x,y train values and scaler
        returned_data_info = non_privatised_training_dataset()
        X_train = returned_data_info[0]
        y = returned_data_info[1]
        scaler = returned_data_info[2]

    # if the user chose to use privatised dataset
    if parameters[0] == 2 or parameters[0] == 4:
        # get the privatised X_train and y values and scaler
        dataset_info = privatised_training_dataset(parameters[1])
        X_train = dataset_info[0]
        y = dataset_info[1]
        scaler = dataset_info[2]

    # model specification
    # if the user chose to use
    # non-privacy preserving SVM
    if parameters[0] == 1 or parameters[0] == 2:
        # rbf clasifier
        model = svm.SVC(kernel='rbf', C=100.0)
        # linear clasifier
        # model = svm.SVC(kernel='linear', C=1.0)
        # fit the training data
        model.fit(X_train, np.ravel(y))




    # receive the data from the server
    msg = conn.recv(SIZE).decode(FORMAT)
    if not (len(msg) <= 0):
        # prepare data for predictions
        data_to_be_predicted = prepare_received_data(msg, scaler)
        print("data to be pred")
        print(data_to_be_predicted)
        print("unscaled data")
        print(scaler.inverse_transform(data_to_be_predicted))

        # make the prediction
        prediction = model.predict(data_to_be_predicted)
        print("prediction")
        print(prediction)


        # filter outlier indexes
        outlier_index = where(prediction == 0)
        # filter outlier values
        outlier_values = data_to_be_predicted.iloc[outlier_index]
        # determine if the received data is anomalous
        if not outlier_values.size == 0:
            decision = "anomalous"
            # print that the received data is anomalous
            # decision: anomalous
            print(f"\n{colours.BOLD}{colours.RED}⫸{colours.ENDC}"
                  f" Decision: {colours.BOLD}{colours.RED}"
                  f"anomalous{colours.ENDC}\n")
        else:
            decision = "valid"
            # print that the received data is valid
            # decision: valid
            print(f"\n{colours.BOLD}{colours.GREEN}⫸{colours.ENDC}"
                  f" Decision: {colours.BOLD}{colours.GREEN}"
                  f"valid{colours.ENDC}\n")

        conn.send(decision.encode(FORMAT))
    else:
        return



# Program Entry Point
def main():
    # make the user choose the type of SVM
    # they want to use as well as the epsilon privacy value
    parameters = get_svm_parameters()

    # set up the connection between the server and the cloud SVM
    # using sockets
    ip_addr = socket.gethostbyname('localhost')
    address = (ip_addr, SERVER_PORT)
    svm_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    svm_server.bind(address)
    svm_server.listen()

    # Print information: Listening on {IP}:{PORT}
    # -------------------------------------------
    print(f"{colours.BOLD}{colours.BLUE}〘{colours.ENDC}"
          f" Cloud SVM service is listening on {colours.BOLD}"
          f"{colours.GREEN}{ip_addr}:{SERVER_PORT}"
          f"{colours.YELLOW} 〙{colours.ENDC}")
    print(f"{colours.BLUE}--------------{colours.CYAN}"
          f"--------------{colours.GREEN}--------------"
          f"{colours.YELLOW}--------------{colours.ENDC}")

    # Main program loop
    while True:

        # Wait for the server to connect and accept the connection
        conn, addr = svm_server.accept()

        # Do anomaly detection
        anomaly_detection(conn, addr, parameters)

        # Create a separate thread to handle separate data
        # when doing anomaly detection
        thread = threading.Thread(target=anomaly_detection, args=(conn, addr, parameters))
        thread.start()


if __name__ == "__main__":
    main()
