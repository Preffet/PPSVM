import matplotlib
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn import model_selection
from sklearn.metrics import accuracy_score
from sklearn.model_selection import cross_validate, GridSearchCV
from sklearn.preprocessing import StandardScaler
from warnings import simplefilter
from sklearn.svm import SVC
from privacy_preserving_svms.Laplace_dataset_privatiser import DataConverter, LaplacePrivacyPreserver
from sklearn.exceptions import ConvergenceWarning
from sklearn.model_selection import train_test_split
import seaborn as sns
simplefilter("ignore", category=ConvergenceWarning)
# update/change matplotlib backend if not running on macosx
# as it might give errors on Windows if left as it is
matplotlib.use('MACOSX')


# ANSI escape codes to print coloured/bold text
class Colours:
    ENDC = '\033[0m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'


# Program Entry Point
def main():
    # import the dataset (with the headers)
    df = pd.read_csv('./datasets/training/balanced/day2_1.csv', header=0, sep=',')

    # define the scaler
    scaler = StandardScaler()

    # get X and y values from the dataset
    X = df.loc[:, ['Lux','Float time value']]
    y = df['Label']

    # convert to numpy array
    X = X.values
    y = y.values

    # split the data into train and test datasets
    # 70% for training, 30% for predictions
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

    # make a copy of X_test and X_train
    X_test_copy = X_test
    X_train_copy = X_train

    # normalise the data (X training and testing values)
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # define the model, c=150 was the best
    # parameter value found after doing parameter tuning
    clf = SVC(kernel="linear", C=500)
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
    print(f"{Colours.BOLD}{Colours.BLUE}Non-Privatised Dataset SVM:{Colours.ENDC}")
    print(f"{Colours.BOLD}{Colours.GREEN}⫸"
          f"{Colours.ENDC}Average Cross Validation Accuracy"
          f"{Colours.BOLD}{Colours.GREEN} {sum(results)/5}\n{Colours.ENDC}", end='')

    print(f"{Colours.BOLD}{Colours.GREEN}⫸"
          f"{Colours.ENDC}Accuracy Predicting Unseen Data"
          f"{Colours.BOLD}{Colours.GREEN} {accuracy/5}\n{Colours.ENDC}")

    # parameter tuning using GridSearchCV for non privatised datasets
    print(f"{Colours.BOLD}{Colours.BLUE}Parameter Tuning For Non-Privatised Dataset SVM:{Colours.ENDC}")
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
    epsilon = [0.001]
    #  epsilon = [5.0, 4.0, 3.0, 1.0, 0.2, 0.1, 0.01]
    # define classifier and k-fold values for the tests with privatised data
    clf2 = SVC(kernel="linear", C=500)
    kfold2 = model_selection.KFold(n_splits=10, shuffle=True)
    print(f"{Colours.BOLD}{Colours.BLUE}\nPrivatised Dataset SVM:{Colours.ENDC}")
    # test each epsilon value using cross validation

    # plot
    fig, ax = plt.subplots()




    for i in epsilon:
        results2 = []
        accuracy2 = 0
        for k in range(5):
            data_privatiser = LaplacePrivacyPreserver(i*10)
            privatised_y_vals = target_values
            scoring_values = ['accuracy']
            privatised_data = data_privatiser.privatise_data(dataInput, sensitivity_values_list=inputSensitivity)
            data_copy = privatised_data


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


        df = pd.DataFrame(data_copy, columns=['Lux', 'Float time value'])
        df["Label"] = list(map(int, target_values))
        # replace -1s with 0s for membership inference attack to work
        df_copy = df.copy()
        df_copy['Label'].replace(-1,0,regex=True,inplace=True)
        print(df_copy)
        df_copy.to_csv("datasets/training/balanced/membership_inference_noisy.csv",index=False, encoding='utf-8',header=True)


        # print the statistics:
        # Epsilon x cross validation accuracy,
        # Accuracy using epsilon x to predict unseen clean data
        print(f"{Colours.BOLD}{Colours.CYAN}⫸"
              f"{Colours.ENDC} Epsilon {Colours.BOLD}{Colours.YELLOW}{i}"
              f"{Colours.ENDC} Cross Validation Accuracy: "
              f"{Colours.BOLD}{Colours.CYAN}"
              f"{sum(results2)/5}{Colours.ENDC}")

        print(f"{Colours.BOLD}{Colours.CYAN}⫸"
              f"{Colours.ENDC}{Colours.ENDC} Accuracy using Epsilon "
              f"{Colours.BOLD}{Colours.YELLOW}{i}{Colours.ENDC} "
              f"data to predict unseen clean data"
              f"{Colours.BOLD}{Colours.CYAN} {accuracy2/5}"
              f"\n{Colours.ENDC}")

    #df.plot.scatter('Lux', 'Float time value', c='Label', colormap='jet')
    #df.plot.savefig("all-collected-data-with-anomalies.png")
    sns.color_palette("tab10")
    plot = sns.scatterplot(
        data=df,
        x="Float time value",
        y="Lux",
        hue="Label",
        alpha=0.9,
        s=100,
        palette=[sns.color_palette("hls").as_hex()[0],sns.color_palette("hls").as_hex()[2]]
        )
    plt.show()

    # set the ticks

    # set the labels
    plot.set(xlabel='Time (Hour)', ylabel='Illuminance (Lux)')
    # remove the original legend
    #plot.get_legend().remove()
    # replace it with a better one
    #custom_lines = [Line2D([0], [0], color='#6bb002', lw=4),
                   # Line2D([], [], color='#BD455B', marker='o', linestyle='None', markersize=7)]

   # plot.legend(custom_lines,
               # ['Valid Data', 'Anomalous Data'],
               # loc="upper left",
               # fancybox=True,
               # framealpha=0.9)

    fig = plot.get_figure()
    # save the figure
    fig.savefig("nomalies.png")


# Program entry point

if __name__ == '__main__':
    main()
