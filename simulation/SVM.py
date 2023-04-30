# Data processing
from numpy import where
import pandas as pd
# Model and performance
from sklearn import svm
from sklearn.svm import OneClassSVM
from matplotlib import use as mpl_use
# networking
import socket
# multithreading
import threading


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
SIZE = 1024
FORMAT = "utf-8"


def anomaly_detection(conn, addr):

    # to plot some data,
    # change/delete/update to other matplotLib back-end
    # if using other OS than MacOSX
    # I had to add this as the default one
    # caused the app to crash while running the app on my laptop
    # mpl_use('MacOSX')

    # import training data, specify that it has a header
    data = pd.read_csv("../datasets/first_half_of_day_data_1.csv",header=0)
    # choose the features
    df = data[["Lux","Float time value"]]
    # normalise the data

    normalized_training_data = df / df.max()
    # model specification
    model = svm.SVC(kernel='rbf', C=1.0)
    model.fit(normalized_training_data[["Lux", "Float time value"]],data["Label"])
    # max df value (to be used for data normalisation)
    max_df_value = df.max()
    # receive the data from the server
    msg = conn.recv(SIZE).decode(FORMAT)
    if not (len(msg) <= 0):
        decoded_received_data = [float(x) for x in msg.split(",")]

        # Print the received message
        print(f"\n{colours.BOLD}{colours.BLUE}⫸{colours.ENDC}"
              f" Data received: {colours.BOLD}{colours.BLUE}"
              f"{decoded_received_data[0]},{decoded_received_data[1]}{colours.ENDC}", end='')

        # convert the data to a dataframe
        print("data to be predicted")
        data_to_be_predicted = pd.DataFrame([decoded_received_data], columns=["Lux", "Float time value"])
        print(data_to_be_predicted)
        # normalise the data
        normalized_data_for_predictions = data_to_be_predicted / max_df_value

        # make the prediction
        prediction = model.predict(normalized_data_for_predictions)

        # filter outlier indexes
        outlier_index = where(prediction == -1)
        # filter outlier values
        outlier_values = normalized_data_for_predictions.iloc[outlier_index]
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


'''
def main():
    mpl_use('MacOSX')
    # import training data
    data = pd.read_csv("datasets/trainingLightData.csv")
    # pick the features
    df = data[["hour", "light"]]
    # model specification
    model = OneClassSVM(kernel='rbf', gamma=0.014, nu=0.02).fit(df)

    # import data for predictions
    data2 = pd.read_csv("datasets/mixedLightData.csv")
    # input features
    dff = pd.DataFrame(data2[["hour", "light"]])

    # dff = data2[["hour","light"]]

    # make the predictions
    y_pred = model.predict(dff)

    # filter outlier indexes
    outlier_index = where(y_pred == -1)
    # filter outlier values

    outlier_values = dff.iloc[outlier_index]
    # visualize outputs
    # title
    plt.title("Anomaly detection using one class SVM")
    # set x,y axis ticks
    plt.xticks(range(0, 24))
    plt.yticks(np.arange(0, 19000, 1000))
    # labels
    plt.xlabel("Time of the day (hour)")
    plt.ylabel("Light level (lux)")

    # all the given data
    plt.scatter(data2["hour"], data2["light"],
                color='#5D9C59', label="Valid data", marker="s", s=200, alpha=.5)
    # anomalies
    plt.scatter(outlier_values["hour"],outlier_values["light"]
              ,color='#DF2E38',label="Anomalous data",marker="s",s=200, alpha=.5)

    plt.legend(loc="upper left")

    plt.savefig("figures/figure1.png")


if __name__ == "__main__":
    main()
'''


def main():
    port = 59998
    ip_addr = socket.gethostbyname('localhost')
    address = (ip_addr, port)

    # Print information: Listening on {IP}:{PORT}
    print(f"\n{colours.BOLD}{colours.BLUE}〘{colours.ENDC}"
        f" Cloud SVM service is listening on {colours.BOLD}"
        f"{colours.GREEN}{ip_addr}:{port}{colours.YELLOW} 〙{colours.ENDC}")
    print(f"{colours.BLUE}--------------{colours.CYAN}--------------{colours.GREEN}--------------"
        f"{colours.YELLOW}--------------{colours.ENDC}")

    # set up the server-cloud connection
    svm_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    svm_server.bind(address)
    svm_server.listen()

    # Main program loop
    while True:
        # Wait for the server to connect and accept the connection
        conn, addr = svm_server.accept()

        # Do anomaly detection
        anomaly_detection(conn, addr)

        # Create a separate thread to handle separate data
        thread = threading.Thread(target=anomaly_detection, args=(conn, addr))
        thread.start()


if __name__ == "__main__":
    main()
