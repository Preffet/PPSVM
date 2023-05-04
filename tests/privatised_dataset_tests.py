import pandas as pd
from sklearn import model_selection
from sklearn.metrics import accuracy_score
from sklearn.model_selection import cross_validate, GridSearchCV
from sklearn.preprocessing import MinMaxScaler
from warnings import simplefilter
from sklearn.svm import SVC
from Laplace_dataset_privatiser import DataConverter, LaplacePrivacyPreserver
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
    BLUE = '\033[94m'


# Program Entry Point
def main():
    # import the dataset (with the headers)
    df = pd.read_csv('./datasets/training/balanced/day1_1.csv', header=0, sep=',')

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

    # make a copy of X_test and X_train
    X_test_copy = X_test
    X_train_copy = X_train

    # normalise the data (X training and testing values)
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.fit_transform(X_test)

    # define the model, c=150 was the best
    # parameter value found after doing parameter tuning
    clf = SVC(kernel="rbf", C=500)
    # define the parameter values for testing classic svm
    param_grid = {'C': [0.001, 0.1, 1, 5, 10, 25, 50, 100, 150, 200, 300, 400, 500]}
    # fit the data
    clf.fit(X_train, y_train)
    results = []
    accuracy = 0
    # run several times
    for i in range(5):
        kfold = model_selection.KFold(n_splits=10, shuffle=True)
        scoring_values = ['accuracy']
        # make a prediction on unseen data
        y_train_pred = clf.predict(X_test)
        # each time do k-fold cross validation
        run_results = cross_validate(estimator=clf,
                                 X=X_train,
                                 y=y_train,
                                 cv=kfold,
                                 scoring=scoring_values,
                                 return_train_score=True)

        run_results = sum(run_results['train_accuracy'])/10
        results.append(run_results)
        accuracy += accuracy_score(y_test, y_train_pred)

    # Print statistics
    print(f"{colours.BOLD}{colours.BLUE}Non-Privatised Dataset SVM:{colours.ENDC}")
    print(f"{colours.BOLD}{colours.GREEN}⫸"
          f"{colours.ENDC}Average Cross Validation Accuracy"
          f"{colours.BOLD}{colours.GREEN} {sum(results)/5}\n{colours.ENDC}", end='')

    print(f"{colours.BOLD}{colours.GREEN}⫸"
          f"{colours.ENDC}Accuracy Predicting Unseen Data"
          f"{colours.BOLD}{colours.GREEN} {accuracy/5}\n{colours.ENDC}")

    # parameter tuning using GridSearchCV for non privatised datasets
    print(f"{colours.BOLD}{colours.BLUE}Parameter Tuning For Non-Privatised Dataset SVM:{colours.ENDC}")
    grid = GridSearchCV(clf, param_grid, refit=True, verbose=4, cv=10)
    grid.fit(X_train, y_train)
    print(grid.best_estimator_)
    # optionally, print the confusion matrix
    #grid_predictions = grid.predict(X_test)
    #print(confusion_matrix(y_test, grid_predictions))

    # define the data converter
    ad = DataConverter()
    # reset x_train to original values,
    # normalisation will be done after adding noise
    X_train = scaler.inverse_transform(X_train)
    dataInput = ad.convert_from_original(X_train)
    target_values = ad.convert_from_original(y_train)
    # define data privatiser
    data_privatiser = LaplacePrivacyPreserver(1.0)
    # get data sensitivity value
    inputSensitivity = data_privatiser.get_data_sensitivity_values(dataInput)

    # define test epsilon values
    epsilon = [5.0, 4.0, 3.0, 1.0, 0.2, 0.1, 0.01]
    # define classifier and k-fold values for the tests with privatised data
    clf2 = SVC(kernel="rbf", C=500)
    kfold2 = model_selection.KFold(n_splits=10, shuffle=True)
    print(f"{colours.BOLD}{colours.BLUE}\nPrivatised Dataset SVM:{colours.ENDC}")
    # test each epsilon value using cross validation
    for i in epsilon:
        results2 = []
        accuracy2 = 0
        for k in range(5):
            data_privatiser = LaplacePrivacyPreserver(i*10)
            privatised_y_vals = target_values
            scoring_values = ['accuracy']
            privatised_data = data_privatiser.privatise_data(dataInput, sensitivity_values_list=inputSensitivity)
            # normalise the data
            privatised_data = scaler.fit_transform(privatised_data)
            # fit the data
            clf2.fit(privatised_data, privatised_y_vals)
            # predict clean data
            y_train_pred2 = clf2.predict(X_test)
            # run cross validation
            run_results2 = cross_validate(
                estimator=clf2,
                X=privatised_data,
                y=privatised_y_vals,
                cv=kfold2,
                scoring=scoring_values,
                return_train_score=True)

            run_results2 = sum(run_results2['train_accuracy'])/10
            results2.append(run_results2)
            accuracy2 += accuracy_score(y_test,y_train_pred2)

        # print the statistics:
        # Epsilon x cross validation accuracy,
        # Accuracy using epsilon x to predict unseen clean data
        print(f"{colours.BOLD}{colours.CYAN}⫸"
              f"{colours.ENDC} Epsilon {colours.BOLD}{colours.YELLOW}{i}"
              f"{colours.ENDC} Cross Validation Accuracy: "
              f"{colours.BOLD}{colours.CYAN}"
              f"{sum(results2)/5}{colours.ENDC}")

        print(f"{colours.BOLD}{colours.CYAN}⫸"
              f"{colours.ENDC}{colours.ENDC} Accuracy using Epsilon "
              f"{colours.BOLD}{colours.YELLOW}{i}{colours.ENDC} "
              f"data to predict unseen clean data"
              f"{colours.BOLD}{colours.CYAN} {accuracy2/5}"
              f"\n{colours.ENDC}")


# Program entry point
if __name__ == '__main__':
    main()
