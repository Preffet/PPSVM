import numpy
import numpy as np
import pandas as pd # for CSV file I/O operations
from matplotlib import pyplot as plt
from numpy import where, ndarray
from sklearn import svm, preprocessing
from sklearn.inspection import DecisionBoundaryDisplay
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, classification_report, accuracy_score
from sklearn import svm
from matplotlib import use as mpl_use
mpl_use('MacOSX')
import matplotlib.lines as mlines
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer


from abstractPrivatizer import AbstractPrivatizer
class LaplacePrivatizer(AbstractPrivatizer):
  _mean = 0.0
  _epsilon = 1.0

  def __init__(self, epsilon=1.):
    if (type(epsilon) != float):
      raise ValueError('Not a valid epsilon')
    if (epsilon <= 0.0):
      raise ValueError('Not a valid epsilon')
    self._epsilon = epsilon

  def privatizeSingleAnswer(self, value, sensitivityValue=1.):
    sanitizedTruth = 0
    try:
      sanitizedTruth = float(value)
    except:
      raise ValueError('Not valid value to be privatized')
    sensitivityValue = max(0.00001, sensitivityValue)
    noise = np.random.laplace(self._mean, sensitivityValue / self._epsilon, 1)[0]
    return float(sanitizedTruth + noise)

class GeneralAdapter:
  dimensions = 2
  initialVaue = 0
  def __init__(self, dimensions, initialValue = 0):
    self.dimensions = dimensions
    self.initialValue = initialValue

  def fromRaw(self, rawData):
    if (type(rawData) == np.ndarray):
      adaptedData = []
      for data in rawData:
        adaptedData.append(self.fromRaw(data))
      return adaptedData
    else:
      return self.toFloat(rawData)

  def toFloat(self, value):
    try:
      return float(value)
    except:
      raise ValueError('Cannot parse to float')

  def toDiscreteValue(self, data):
    if type(data) == list:
      intList = []
      for value in data:
        intList.append(self.toDiscreteValue(value))
      return intList
    elif type(data) == float:
      discreteWithZeroMean = round(data - self.initialValue)

      discreteWithinBounds = 0
      if (discreteWithZeroMean >= (self.dimensions-1)):
        discreteWithinBounds = self.dimensions-1
      elif(discreteWithZeroMean <= 0):
        discreteWithinBounds = 0
      else:
        discreteWithinBounds = discreteWithZeroMean % self.dimensions

      discreteValue = discreteWithinBounds + self.initialValue
      return discreteValue
    else:
      raise ValueError('It only accepts lists of float values')

def main():
    df = pd.read_csv('more.csv', header=0, sep=',')

    X = df.loc[:, ['time', 'lux']]
    y = df['label']

    # convert to numpy array
    X = X.values
    max_time,max_light = X.max(axis=0)
    min_time, min_light = X.min(axis=0)
    y = y.values


    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5, random_state=990)
    # normalise the data
    normalized_training_data = df / df.max()

    clf = svm.SVC(kernel='linear')
    # learn from the data
    clf.fit(X_train, y_train)

    # Predict the test set
    predictions = clf.predict(X_test)

    print(str(accuracy_score(y_test, predictions)).replace('.', ','))
    print("predictions")


    # get the separating hyperplane
    fig, ax = plt.subplots(1, 1,squeeze=True)
    for i in range(len(clf.coef_)):
        w = clf.coef_[i]
        a = -w[0] / w[1]
        xx = np.linspace(min_time,max_time)
        yy = a * xx - (clf.intercept_[i]) / w[1]
        ax.plot(xx,yy, 'k-')
        DecisionBoundaryDisplay.from_estimator(
            clf,
            X,
            plot_method="contour",
            colors="k",
            levels=[-1, 0, 1],
            alpha=0.5,
            linestyles=["--", "-", "--"],
            ax=ax,
        )

    # Generate scatter plot for training data
    # filter out valid training data values
    valid_training_data = where(y_train == 1)
    valid_training_data_values = X_train[valid_training_data]
    # plot valid training values
    for x in range(valid_training_data_values.shape[0]):
        ax.scatter(valid_training_data_values[x][0], valid_training_data_values[x][1]
                    , color='#00FF00', label="Learned Valid Values", marker="o", s=200, alpha=.5)

    # filter out invalid training data values
    invalid_training_data = where(y_train == 0)
    invalid_training_data_values = X_train[invalid_training_data]

    # plot invalid training values
    for x in range(invalid_training_data_values.shape[0]):
        ax.scatter(invalid_training_data_values[x][0],
                   invalid_training_data_values[x][1],
                   color='#DF2E38',
                   label="Learned Invalid Values",
                   marker="o", s=200, alpha=.5)

    # filter predicted valid data
    # filter valid data indexes
    valid_index = where(predictions == 1)
    # filter filter valid data values
    valid_values = X_test[valid_index]

    # filter predicted invalid data indexes
    outlier_index = where(predictions == 0)
    # filter outlier values
    outlier_values = X_test[outlier_index]

    for x in range(outlier_values.shape[0]):
        ax.scatter(outlier_values[x][0],
                   outlier_values[x][1],
                   color='#DF2E38',
                   label="Predicted Anomalous Values",
                   marker="*", s=200, alpha=.6,edgecolor="k")

    for x in range(valid_values.shape[0]):
        ax.scatter(valid_values[x][0],
                    valid_values[x][1],
                    color='#00FF00',
                    label="Predicted Valid Values",
                    marker="*",
                    s=200,
                    alpha=.6,
                    edgecolor="k",)

    # plot support vectors
    ax.scatter(
        clf.support_vectors_[:, 0],
        clf.support_vectors_[:, 1],
        s=100,
        facecolors="None",
        edgecolor='black',
        linewidth=2,
    )

    plt.xlabel('Time')
    plt.ylabel('Illuminance (Lux)')



    green = '#00FF00'
    red = '#DF2E38'

    red_data = mlines.Line2D([], [], color=red, marker='o', linestyle='None',
                                  markersize=10, label='Learned Invalid Data', alpha=.6)
    green_data = mlines.Line2D([], [], color=green, marker='o', linestyle='None',
                                  markersize=10, label='Learned Valid Data', alpha=.6)
    predicted_data_valid = mlines.Line2D([], [], color=green, marker='*', linestyle='None',
                                  markersize=10, label='Predicted Valid Data', alpha=.6,markeredgecolor='k')
    predicted_data_invalid = mlines.Line2D([], [], color=red, marker='*', linestyle='None',
                                  markersize=10, label='Predicted Invalid Data', alpha=.6,markeredgecolor='k')
    hyperplane = mlines.Line2D([], [], color='k', linestyle='-',
                                  markersize=10, label='Hyperplane', alpha=.6,markeredgecolor='k')


    plt.xticks(np.arange(0, 5, 1.0))
    plt.xlabel("Time")
    plt.ylabel("Light Level (Lux)")
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
              ncol=3, fancybox=True, shadow=True,
              handles=[green_data,predicted_data_valid,red_data,predicted_data_invalid, hyperplane])


    # show the plot
    plt.show()
    # save the plot
    plt.savefig('collectedLightData.png')




    ad = GeneralAdapter(7, 1)

    dataInput = ad.fromRaw(X)
    dataTarget = ad.fromRaw(y)

    privatizer = LaplacePrivatizer(1.0)

    inputSensitivity = privatizer.getSensitivityList(dataInput)
    targetSensitivity = 7

    #     epsilon = [1.0, 1.5, 2.0, 2.5, 3.0]
    epsilon = [30.0, 20.0, 10.0, 5.0, 4.0, 3.0, 2.0, 1.0, 0.5, 0.01, 0.001]

    privatizer = LaplacePrivatizer(1.0)
    privateData = privatizer.privatize(dataInput, sensitivityList=inputSensitivity)
    for i in epsilon:
        privatizer = LaplacePrivatizer(i)
        privateData = privatizer.privatize(dataInput, sensitivityList=inputSensitivity)

        #         privateTargetsFloat = privatizer.privatize(dataTarget, sensitivityList = targetSensitivity)
        #         privateTargets = ad.toDiscreteValue(privateTargetsFloat)
        privateTargets = dataTarget

        clf = svm.SVC(kernel='linear')
        clf.fit(privateData, privateTargets)

        y_pred = clf.predict(X_test)
        print(str(accuracy_score(y_test, y_pred)).replace('.', ','))

if __name__ == '__main__':
    main()