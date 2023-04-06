# Import libraries
from numpy import where
# Data processing
import pandas as pd
# Model and performance
from sklearn.svm import OneClassSVM
from matplotlib import use as mpl_use
import socket
import sys
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

def SVM_model():
    # Change/delete/update to other matplotLib back-end
    # if using other OS than MacOSX
    # I had to add this as the default one
    # caused the app to crash while running on my laptop
    mpl_use('MacOSX')

    # import training data
    data = pd.read_csv("datasets/trainingLightData.csv")
    # choose the features
    df = data[["hour", "light"]]
    # normalise the data
    normalized_training_data = df / df.max()
    print("df hour:")
    print(df["hour"])
    print("max hour:")
    print(df.max()["hour"])
    print("normalised hour")
    normalized_training_data["hour"]=df["hour"].div(df.max()["hour"])
    print(normalized_training_data["hour"])

    # model specification
    model = OneClassSVM(kernel='rbf', gamma=39, nu=0.03)
    model.fit(normalized_training_data)
    # max df value (to be used for data normalisation)
    df_max = df.max()
    return model, df_max


def anomaly_detection(conn,addr):

    # Change/delete/update to other matplotLib back-end
    # if using other OS than MacOSX
    # I had to add this as the default one
    # caused the app to crash while running on my laptop
    mpl_use('MacOSX')

    # import training data
    data = pd.read_csv("datasets/trainingLightData.csv")
    # choose the features
    df = data[["hour", "light"]]
    # normalise the data

    normalized_training_data = df / df.max()


    # model specification
    model = OneClassSVM(kernel='rbf', gamma=39, nu=0.03)
    model.fit(normalized_training_data)
    # max df value (to be used for data normalisation)
    max_df_value = df.max()
    # receive the data from the server
    msg = conn.recv(SIZE).decode(FORMAT)

    if not (len(msg) <= 0):
        decoded_received_data = [int(x) for x in msg.split(",")]

        # Print the received message
        print(f"\n{colours.BOLD}{colours.BLUE}⫸{colours.ENDC}"
              f" Data received: {colours.BOLD}{colours.BLUE}"
              f"{decoded_received_data[0]},{decoded_received_data[1]}{colours.ENDC}", end='')


        # convert the data to a dataframe
        data_to_be_predicted = pd.DataFrame([decoded_received_data], columns = ["hour","light"])
        # normalise the data
        normalized_data_for_predictions = data_to_be_predicted / max_df_value

        # make the prediction
        prediction = model.predict(normalized_data_for_predictions)

        # filter outlier indexes
        outlier_index = where(prediction == -1)
        # filter outlier values
        outlier_values = normalized_data_for_predictions.iloc[outlier_index]
        decision = ""
        if not outlier_values.size == 0:
            decision = "anomalous"
            # print that the received data is anomalous
            # decision: anomalous
            print(f"\n{colours.BOLD}{colours.RED}⫸{colours.ENDC}"
                  f" Decision: {colours.BOLD}{colours.RED}"
                  f"anomalous{colours.ENDC}", end='')
        else:
            decision = "valid"
            # print that the received data is valid
            # decision: valid
            print(f"\n{colours.BOLD}{colours.GREEN}⫸{colours.ENDC}"
                  f" Decision: {colours.BOLD}{colours.GREEN}"
                  f"valid{colours.ENDC}")

        conn.send(decision.encode(FORMAT))
    else:
        print("no data received")
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
        port = 59999
        IP = socket.gethostbyname('localhost')
        address = (IP, port)

        # Print information: Listening on {IP}:{PORT}
        print(f"\n{colours.BOLD}{colours.BLUE}〘{colours.ENDC}"
              f" Cloud SVM service is listening on {colours.BOLD}{colours.GREEN}{IP}:{port}{colours.YELLOW} 〙{colours.ENDC}")
        print(f"{colours.BLUE}--------------{colours.CYAN}--------------{colours.GREEN}--------------"
              f"{colours.YELLOW}--------------{colours.ENDC}")

        # get the SVM model
        # and maximum dataframe value (used for data normalisation)

        # set up the server-cloud connection
        SVM_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        SVM_server.bind(address)
        SVM_server.listen()

        # Main program loop
        while True:
            # Wait for the server to connect and accept the connection
            conn, addr = SVM_server.accept()

            # Do anomaly detection
            anomaly_detection(conn,addr)

            # Create a separate thread to handle separate data
            thread = threading.Thread(target=anomaly_detection, args=( conn, addr))
            thread.start()



if __name__ == "__main__":
    main()