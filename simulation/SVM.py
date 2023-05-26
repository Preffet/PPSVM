# Data processing
import pickle as pkl
import numpy as np
from numpy import where
import pandas as pd
# Model and performance
from sklearn import svm
from sklearn.preprocessing import MinMaxScaler, StandardScaler
# networking
import socket
# multithreading
import threading
# dp data privatisation
from privacy_preserving_svms import objective_function_perturbation_SVM as obj_perturb_SVM
from privacy_preserving_svms.Laplace_dataset_privatiser import DataConverter, LaplacePrivacyPreserver


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


# public variables
# message size
SIZE = 1024
# port of the server
SERVER_PORT = 59991
# message format
FORMAT = "utf-8"
# available choices for epsilon values when
# running SVMs in privacy-preserving way
EPSILON_VALUES = [0.9, 0.5, 0.1]
# privacy preserving SVM lambda and h values
SVM_H = 5
SVM_LAMBDA = 0.002


# function to get the chosen SVM type as
# well as the privacy epsilon parameters from the user
def get_svm_parameters():
    # small function to print all available epsilon options
    def print_options(epsilon_values):
        print(f"{colours.BOLD}{colours.BLUE}1. {colours.ENDC}{epsilon_values[0]}\n"
              f"{colours.BOLD}{colours.CYAN}2. {colours.ENDC}{epsilon_values[1]}\n"
              f"{colours.BOLD}{colours.GREEN}3. {colours.ENDC}{epsilon_values[2]}\n")

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
    # - Privatised dataset + differentially private svm
    print(f"\n{colours.BOLD}{colours.BLUE}Choose The SVM Type:{colours.ENDC}\n"
          f"{colours.BOLD}{colours.CYAN}1.{colours.ENDC}Not Private\n"
          f"{colours.BOLD}{colours.GREEN}2.{colours.ENDC}Using Privatised Dataset\n"
          f"{colours.BOLD}{colours.YELLOW}3.{colours.ENDC}Differentially Private SVM\n"
          f"{colours.BOLD}{colours.ORANGE}4.{colours.ENDC}Privatised Dataset + Differentially Private SVM\n")
    svm_type = get_value(4)

    # 2.Ask the user to choose the privacy parameter
    # if they choose option 2, 3, or 4
    # (privatised dataset,
    # differentially private SVM
    # privatised dataset + differentially private SVM)

    # if it is option 2 or 3 ask for one
    # epsilon value
    epsilon1 = 0
    if svm_type in (2, 3):
        print(f"\n{colours.BOLD}{colours.BLUE}Choose The Epsilon Value ", end='')
        if svm_type == 2:
            print(f"(default is 5):{colours.ENDC}")
            print_options(epsilon_values=[i * 10 for i in EPSILON_VALUES])
            epsilon1 = EPSILON_VALUES[get_value(3) - 1] * 10
        if svm_type == 3:
            print(f"(default is 0.5):{colours.ENDC}")
            print_options(epsilon_values=EPSILON_VALUES)
            epsilon1 = EPSILON_VALUES[get_value(3) - 1]

    # if it is option 4 ask for two
    # epsilon values
    # one for dataset privatisation and
    # another for SVM
    epsilon2 = 0
    if svm_type == 4:
        print(f"\n{colours.BOLD}{colours.BLUE}Choose the Epsilon Value for Dataset Privatisation ")
        print(f"(default is 5.0):{colours.ENDC}")
        print_options(epsilon_values=[i * 10 for i in EPSILON_VALUES])
        epsilon1 = EPSILON_VALUES[get_value(3) - 1] * 10
        print(f"\n{colours.BOLD}{colours.BLUE}Choose the Epsilon Value for Privacy-Preserving SVM ")
        print(f"(default is 0.5):{colours.ENDC}")
        print_options(epsilon_values=EPSILON_VALUES)
        epsilon2 = EPSILON_VALUES[get_value(3) - 1]

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


# -------------------------------------------------------- #
# -------------------------------------------------------- #

# Function to choose & load the correct training
# datasets depending on the system time
def choose_training_dataset():
    # Get the current hour, at the moment, it is set to 23 for testing purposes, but
    # for real time testing, change current_hour variable value to datetime.now()
    # and then go to client.py file and change the current_hour variable to
    # datetime.now() too. These both values must match.
    current_hour = 10  # datetime.now().hour
    df2 = pd.DataFrame()
    # if it is night
    if (6 > current_hour >= 0) or (21 <= current_hour < 24):
        df1 = pd.read_csv('../datasets/training/balanced/night.csv',
                          header=0, sep=',')

    # if it is first half of the day
    elif 6 <= current_hour < 13:
        df1 = pd.read_csv('../datasets/training/balanced/morning_0.csv',
                          header=0, sep=',')
        df2 = pd.read_csv('../datasets/training/balanced/morning_1.csv',
                          header=0, sep=',')
    # if it is second half of the day
    else:
        df1 = pd.read_csv('../datasets/training/balanced/evening_0.csv',
                          header=0, sep=',')
        df2 = pd.read_csv('../datasets/training/balanced/evening_1.csv',
                          header=0, sep=',')
    # return the required dataframes
    return df1, df2


# function to privatise the dataset
# by adding laplace noise
def privatised_training_dataset(eps):
    # import the dataset (with the headers)
    df = pd.read_csv('../datasets/all_data/all_data_including_anomalous.csv',
                     header=0, sep=',')

    # define the scaler
    scaler = StandardScaler()

    # get X and y values from the dataset
    X = df.loc[:, ['Lux', 'Float time value']]
    y = df['Label']

    # convert to numpy array
    X = X.values
    y = y.values

    # define data converter
    ad = DataConverter()
    data_input = ad.convert_from_original(X)
    target_values = ad.convert_from_original(y)
    # define the data privatiser
    data_privatiser = LaplacePrivacyPreserver(eps * 100)
    # get data sensitivity value
    input_sensitivity = data_privatiser.get_data_sensitivity_values(data_input)
    privatised_data = data_privatiser.privatise_data(
        data_input,
        sensitivity_values_list=input_sensitivity)
    # normalise the data
    privatised_data = scaler.fit_transform(pd.DataFrame(privatised_data, columns=['Lux', 'Float time value']))
    privatised_data = pd.DataFrame(privatised_data, columns=['Lux', 'Float time value'])
    # could test noisy labels too, but that is future work
    privatised_y_vals = pd.DataFrame(target_values, columns=['Label'])
    # return the privatised dataset and scaler
    return privatised_data, privatised_y_vals, scaler


# -------------------------------------------------------- #
# -------------------------------------------------------- #


# function get the training data from the not privatised dataset
def non_privatised_training_dataset(df, name):
    # define the scaler
    scaler = StandardScaler()
    # get X and y values from the dataset
    X = df.loc[:, ['Lux', 'Float time value']]
    y = df['Label']
    # normalise the training data and convert it back to a pd dataframe
    X_train = scaler.fit_transform(X)
    X_train = pd.DataFrame(X_train, columns=['Lux', 'Float time value'])
    # save the scaler
    import pickle as pkl
    with open(f"detection_system_files/scalers/{name}scaler.pkl", "wb") as outfile:
        pkl.dump(scaler, outfile)

    # return training X,y values
    return X_train, y


# -------------------------------------------------------- #
# -------------------------------------------------------- #


# function to prepare the received data for predictions
def prepare_received_data(msg, name):
    with open(f"detection_system_files/scalers/{name}scaler.pkl", "rb") as infile:
        scaler = pkl.load(infile)
    decoded_received_data = [float(x) for x in msg.split(",")]

    # Print the received message
    print(f"\n{colours.BOLD}{colours.BLUE}⫸{colours.ENDC} Data received: {colours.BOLD}{colours.BLUE}{decoded_received_data[0]},{decoded_received_data[1]}{colours.ENDC}", end = '')

    # convert the data to a dataframe
    decoded_received_data = pd.DataFrame([decoded_received_data], columns=['Lux', 'Float time value'])

    # scale it
    decoded_received_data = scaler.transform(decoded_received_data)
    # convert to df again
    data_to_be_predicted = pd.DataFrame(decoded_received_data, columns=['Lux', 'Float time value'])
    # return pd dataframe containing the data to be predicted
    return data_to_be_predicted


# -------------------------------------------------------- #
# -------------------------------------------------------- #

# helper function to filter out
# outlier values after making a prediction
# and return the decision/s
def filter_outlier_values(prediction, data_to_be_predicted):
    # filter outlier indexes
    outlier_index = where(prediction == -1)
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
    return decision


# -------------------------------------------------------- #
# -------------------------------------------------------- #


# multithreaded function where the anomaly detection is
# done using the chosen SVM type and epsilon values.
# The dataset is chosen depending on a static value, but to simulate
# a real world scenario, it can be chosen based on real system time
# (see choose_training_dataset() function for instructions)
def anomaly_detection(conn, addr, parameters):
    # get model training datasets
    df1, df2 = choose_training_dataset()[0], choose_training_dataset()[1]

    # 1. dataset specification
    # if the user choose to use a not privatised dataset
    if parameters[0] == 1 or parameters[0] == 3:
        # retrieve x,y train values and scaler for the first classifier
        returned_data_info = non_privatised_training_dataset(df1, "df1")
        X_train_1 = returned_data_info[0]
        y_1 = returned_data_info[1]

        import pickle as pkl
        with open(f"detection_system_files/scalers/df1scaler.pkl", "rb") as infile:
            scaler_1 = pkl.load(infile)

        # retrieve x,y train values and scaler for the second classifier
        if not df2.empty:
            returned_data_info = non_privatised_training_dataset(df2, "df2")
            X_train_2 = returned_data_info[0]
            y_2 = returned_data_info[1]
            with open(f"detection_system_files/scalers/df2scaler.pkl", "rb") as infile:
                scaler_2 = pkl.load(infile)

    # if the user chose to use privatised dataset
    if parameters[0] == 2 or parameters[0] == 4:
        # get the privatised X_train and y
        # values and scaler for the 1st classifier
        dataset_info = privatised_training_dataset(parameters[1])
        X_train_1 = dataset_info[0]
        y_1 = dataset_info[1]
        scaler_1 = dataset_info[2]
        if not df2.empty:
            # get the privatised X_train and y values and scaler
            # or the 2nd classifier
            dataset_info = privatised_training_dataset(parameters[1])
            X_train_2 = dataset_info[0]
            y_2 = dataset_info[1]
            scaler_2 = dataset_info[2]

    # 2. model specification

    # if the user chose to use
    # non-privacy preserving SVM
    if parameters[0] == 1 or parameters[0] == 2:
        # linear svm
        model_1 = svm.SVC(kernel='linear', C=100.0)
        # fit the training data to the 1st classifier
        model_1.fit(X_train_1, np.ravel(y_1))
        # fit the training data to the 2nd classifier
        if not df2.empty:
            # linear svm
            model_2 = svm.SVC(kernel='linear', C=100.0)
            # fit the training data for the 2nd classifier
            model_2.fit(X_train_2, np.ravel(y_2))

    # if the user chose to use the privacy-preserving SVM
    if parameters[0] == 3 or parameters[0] == 4:
        model_1 = obj_perturb_SVM.SVM(privatised=True, lambda_value=SVM_LAMBDA, h_val=SVM_H)
        # just add the y values to get all the data
        X_train_1["Label"] = y_1
        model_1.model_fit(epsilon_p=parameters[1], data=X_train_1)
        if not df2.empty:
            model_2 = obj_perturb_SVM.SVM(privatised=True, lambda_value=SVM_LAMBDA, h_val=SVM_H)
            # just add the y values to get all the data
            X_train_2["Label"] = y_2
            model_2.model_fit(epsilon_p=parameters[1], data=X_train_2)

    # 3. receive a message, make a prediction
    # send back results to the server
    # 3.1. receive the message
    msg = conn.recv(SIZE).decode(FORMAT)
    if not (len(msg) <= 0):
        # 3.2. make predictions
        # prepare data for the 1st prediction
        data_to_be_predicted_1 = prepare_received_data(msg, "df1")
        # 3.2 make the prediction
        prediction_1 = model_1.predict(data_to_be_predicted_1)
        # get the decision
        decision = filter_outlier_values(prediction_1, data_to_be_predicted_1)
        # if not anomalous, make the second prediction
        if decision != "anomalous" and not df2.empty:
            # prepare data for the 2nd prediction
            data_to_be_predicted_2 = prepare_received_data(msg, "df2")
            # make the prediction
            prediction_2 = model_2.predict(data_to_be_predicted_2)
            # get the decision
            decision = filter_outlier_values(prediction_2, data_to_be_predicted_2)

        # 3.3 send back the prediction to the router (server)
        conn.send(decision.encode(FORMAT))
    else:
        return


# -------------------------------------------------------- #
# -------------------------------------------------------- #

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
        # when doing anomaly detection. This is done so that the
        # SVM could support multiple nodes and predict their data at
        # the same time
        thread = threading.Thread(target=anomaly_detection, args=(conn, addr, parameters))
        thread.start()


if __name__ == "__main__":
    main()