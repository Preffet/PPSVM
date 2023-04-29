import numpy as np
import pandas as pd
from sklearn import model_selection, svm, metrics
from sklearn.metrics import accuracy_score
from sklearn.model_selection import cross_validate
from sklearn.preprocessing import MinMaxScaler
from warnings import simplefilter
from abstract_data_privatiser import ABCPrivacyPreserver
from sklearn.exceptions import ConvergenceWarning
from sklearn.model_selection import train_test_split
simplefilter("ignore", category=ConvergenceWarning)


# ANSI escape codes to print coloured/bold text
class colours:
    ENDC = '\033[0m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'


class LaplacePrivacyPreserver(ABCPrivacyPreserver):
  # default values
  mean_value = 0.0
  epsilon_value = 1.0

  def __init__(self, epsilon_val=1.0):
    # check if provided epsilon value is valid
    if type(epsilon_val) != float:
      raise ValueError('Epsilon value has to be a float')
    if epsilon_val <= 0.0:
      raise ValueError('Epsilon value has to be >0.0')
    self.epsilon_value = epsilon_val

  def privatise_single_value(self, data, sensitivity_level=1.0):
    # convert it to a float
    try:
      float_value = float(data)
    except:
      raise ValueError('The value to be sanitised has to be float')
    # define the sensitivity value:
    # how much of an impact can an individual value
    # have on the outcome of the queries?
    sensitivity_level = max(0.001, sensitivity_level)
    # ddd noise to the value:
    # epsilon attribute represents the privacy budget,
    # which is a measure of how much privacy is being
    # provided to the data. Together with the sensitivity
    # it determines the scale of the noise added to the data.
    # the noise is drawn from the Laplace distribution
    noise_value = np.random.laplace(self.mean_value, sensitivity_level / self.epsilon_value, 1)[0]
    return float(float_value + noise_value)


class DataConverter:
    # convert np array into a list
    def convert_from_original(self, original_data):
        if type(original_data) == np.ndarray:
            converted_data = []
            # loop through all the data entries
            for value in original_data:
                converted_data.append(self.convert_from_original(value))
            return converted_data
        else:
            return self.covert_to_float(original_data)

    # convert the data to a float
    def covert_to_float(self, data):
        try:
            return float(data)
        except:
            # inform the user if errors occur
            raise ValueError('Data could not be converted to float')


# Program Entry Point
def main():
    # import the dataset (with the headers)
    df = pd.read_csv('datasets/first_half_of_day_data_1.csv', header=0, sep=',')

    # define the scaler
    scaler = MinMaxScaler()

    # get X and y values from the dataset
    X = df.loc[:, ['Float time value', 'Lux']]
    y = df['Label']

    # convert to numpy array
    X = X.values
    y = y.values

    # split the data into train and test datasets
    # 70% for training, 30% for predictions
    X_train, X_test, y_train, y_test = train_test_split(X, y,test_size=0.3)

    # normalise the data (X training and testing values)
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.fit_transform(X_test)

    # define the model
    clf = svm.SVC(C=10, max_iter=10000, kernel='linear')
    # fit the data
    clf.fit(X_train, y_train)


    kfold = model_selection.KFold(n_splits=10,shuffle=True)
    scoring_values = ['accuracy']
    # make a prediction on unseen data
    y_train_pred = clf.predict(X_test)
    results = cross_validate(estimator=clf,
                             X=X_train,
                             y=y_train,
                             cv=kfold,
                             scoring=scoring_values,
                             return_train_score=True)
    # Print statistics
    print(f"{colours.BOLD}{colours.GREEN}⫸"
          f"{colours.ENDC}Average Cross Validation Accuracy using clean data"
          f"{colours.BOLD}{colours.GREEN} {sum(results['train_accuracy'])/10}\n{colours.ENDC}", end='')

    print(f"{colours.BOLD}{colours.GREEN}⫸"
          f"{colours.ENDC}Accuracy predicting clean unseen data using clean training data"
          f"{colours.BOLD}{colours.GREEN} {(accuracy_score(y_test, y_train_pred))}\n{colours.ENDC}")

    # define the data adapter
    ad = DataConverter()
    # reset x_train to original values,
    # normalisation will be done after adding noise
    X_train = scaler.inverse_transform(X_train)
    dataInput = ad.convert_from_original(X_train)
    dataTarget = ad.convert_from_original(y_train)
    # define data privatiser
    privatizer = LaplacePrivacyPreserver(1.0)
    # get data sensitivity value
    inputSensitivity = privatizer.get_data_sensitivity_values(dataInput)

    # define test epsilon values
    epsilon = [30.0, 15.0, 10.0, 5.0, 2.5, 1.0, 0.01]
    # define classifier and k-fold values for the tests with privatised data
    clf2 = svm.SVC(C=100, max_iter=1000, kernel='linear')
    kfold2 = model_selection.KFold(n_splits=10, shuffle=True)
    # test each epsilon value using cross validation
    for i in epsilon:
        privatizer = LaplacePrivacyPreserver(i)
        privateData = privatizer.privatise_data(dataInput, sensitivity_values_list=inputSensitivity)
        # normalise the data
        privateData = scaler.fit_transform(privateData)
        # could test noisy labels too, but that is future work
        privateTargets = dataTarget
        # fit the data
        clf2.fit(privateData, privateTargets)
        scoring_values = ['accuracy']
        # run cross validation
        results2 = cross_validate(
            estimator=clf2,
            X=privateData,
            y=privateTargets,
            cv=kfold2,
            scoring=scoring_values,
            return_train_score=True)
        # print the statistics:
        # Epsilon x cross validation accuracy,
        # Accuracy using epsilon x to predict unseen clean data
        print(f"{colours.BOLD}{colours.CYAN}⫸"
              f"{colours.ENDC} Epsilon {colours.BOLD}{colours.YELLOW}{i}"
              f"{colours.ENDC} Cross Validation Accuracy: "
              f"{colours.BOLD}{colours.CYAN}"
              f"{sum(results2['train_accuracy'])/10}{colours.ENDC}")
        y_train_pred2 = clf2.predict(X_test)
        print(f"{colours.BOLD}{colours.CYAN}⫸"
              f"{colours.ENDC}{colours.ENDC} Accuracy using Epsilon "
              f"{colours.BOLD}{colours.YELLOW}{i}{colours.ENDC} "
              f"data to predict unseen clean data"
              f"{colours.BOLD}{colours.CYAN} {(accuracy_score(y_test, y_train_pred2))}"
              f"\n{colours.ENDC}")


# Program entry point
if __name__ == '__main__':
    main()
