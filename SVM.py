'''
╔═══════════════════════════════════════════════════╗
 Privacy Preserving SVM for anomaly detection in ASNs
  Justina Metrikyte (c0037826), Newcastle University
╚═══════════════════════════════════════════════════╝
'''

## Import Libraries
from numpy import where
# Data processing
import pandas as pd
# Model and performance
from sklearn.svm import OneClassSVM
from matplotlib import use as mpl_use

def anomaly_detection(dataToCheck):
    # Change/delete/update to other matplotLib back-end
    # if using other OS than MacOSX, I had to add this as the default one
    # caused the app to crash while running on my laptop
    mpl_use('MacOSX')

    # import training data
    data = pd.read_csv("datasets/trainingLightData.csv")
    # pick the features
    df = data[["hour","light"]]
    # normalise the data
    normalized_training_data = df / df.max()

    # model specification
    model = OneClassSVM(kernel='rbf', gamma=39, nu=0.03).fit(normalized_training_data)

    # import data for predictions
    data_to_be_predicted = pd.DataFrame([dataToCheck], columns = ["hour","light"])
    # normalise this data, take the max values from the training data
    normalized_data_for_predictions = data_to_be_predicted / df.max()

    # make the prediction
    prediction = model.predict(normalized_data_for_predictions)

    # filter outlier indexes
    outlier_index = where(prediction == -1)
    # filter outlier values
    outlier_values = normalized_data_for_predictions.iloc[outlier_index]
    return outlier_values


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