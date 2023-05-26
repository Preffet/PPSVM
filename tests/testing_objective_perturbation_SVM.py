import pandas as pd
from numpy import mean
import numpy as np
from sklearn.preprocessing import StandardScaler

from privacy_preserving_svms import objective_function_perturbation_SVM as obj_SVM
from helper_scripts import cross_validation_utilities as cv_utils

""""
Script which contains functions to find the 
best parameters for the objective perturbation SVM
using k fold cross validation and grid search written
from scratch. It also contains a script to evaluate the
performance of the SVM when using different epsilon values.
Call different test functions in the main function 
(at the end of the script).
"""

# define the range of values for h to test
# in huber loss function it controls the
# transition point between the squared loss and the linear loss
# for plain svm c values that were tested were 0.001,0.01,0.1,1,10,100,1000

# since h=1/2c, equivalent h vals were tested:
# 500, 50, 5, 0.5, 0.05, 0.005, 0.0005
h_vals = [500, 50, 5, 0.5, 0.05, 0.005, 0.0005]

# define the range of values for lambda to test,
# used for regularization
# [0.002, 0.02, 0.2, 2.0, 20.0, 200.0, 2000.0]
lambda_vals = [1/h for h in h_vals]



# ANSI escape codes to print coloured/bold text
class Colours:
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'


""""
Function which contains grid
search implemented from scratch to find
the best lambda and h values using
k fold cross validation
"""


def grid_search(data):
    # small helper function to find the highest accuracy
    def find_highest_accuracy(accuracies_list):
        highest_accuracy = -1
        highest_entry = None
        for entry in accuracies_list:
                if entry['accuracy'] > highest_accuracy:
                    highest_accuracy = entry['accuracy']
                    highest_entry = entry
        # return the entry containing the highest accuracy
        return highest_entry

    # inform the user that it might take a while to complete
    print(f"{Colours.CYAN}Starting grid search for optimal hyperparameters.\n{Colours.ENDC}"
          "Please note that if you have chosen a large number"
          " of lambda/h parameters or runs, the process may take"
          " a significant amount of time to complete (>1-2minutes). :) ")
    # define the epsilon
    epsilon = 0.5
    # number of runs
    runs = 5
    # number of bucket files
    for j in range(0, runs):
        path_to_folds_file = cv_utils.create_folds_file(data)
        accuracies_list = []
        for h in h_vals:
                for l in lambda_vals:
                    results_buckets = np.zeros(20)
                    cv_list = []
                    for i in range(0, 10):
                        # get train and test data for the current fold
                        training, testing = cv_utils.train_test_split(data, folds_path=path_to_folds_file, fold_number=i)

                        scaler = StandardScaler()
                        training[['Lux', 'Float time value']] = scaler.fit_transform(training[['Lux', 'Float time value']])
                        testing[['Lux', 'Float time value']] = scaler.transform(testing[['Lux', 'Float time value']])

                        # define the svm
                        huber = obj_SVM.SVM(privatised=True, lambda_value=l, h_val=h)
                        huber.model_fit(data=training, epsilon_p=epsilon)
                        accuracy = 1 - huber.evaluate(testing)
                        cv_list.append(accuracy)
                    accuracies_dict = {'accuracy': mean(cv_list), 'h': h, 'lambda': l}
                    accuracies_list.append(accuracies_dict)

        # print the best discovered parameters
        print(f"Best discovered parameters during run {j+1}:\n"
              f"{Colours.BLUE}"
              f"{find_highest_accuracy(accuracies_list=accuracies_list)}"
              f"{Colours.ENDC}")

""""
Evaluate the performance of the SVM when using
different epsilon values.
0 epsilon = the mechanism is perfectly private but completely
useless because it doesn't allow any information to be shared.
When it is close to 0, the mechanism is highly private,
but might not provide very accurate results.
"""


def privacy_accuracy_evaluation(data):
    # all epsilon values which will be tested
    epsilon_values = [0.02, 0.05, 0.07, 0.1, 0.5, 0.7, 0.9]
    # svm parameters
    h_val = 1
    privatised_lambda = public_lambda = 0.2
    # how many times the evaluation will be run
    runs = 2
    # store accuracies for each epsilon value
    # (accuracy at index 0 = accuracy running svm
    # for each run. +1 because we will also store the
    # accuracy of the plain svm at the last index
    run_avg = np.zeros(len(epsilon_values)+1)
    for run in range(0, runs):
        folds_location = cv_utils.create_folds_file(data)
        print(f"{Colours.BLUE}\nRUN NUMBER : {run}{Colours.ENDC} ")
        # store accuracies for each epsilon value
        # (accuracy at index 0 = accuracy running svm
        # using epsilon at index 0) for each fold
        # +1 because we will also store the
        # accuracy of the plain svm at the last index
        accuracy_list = np.zeros(len(epsilon_values)+1)

        # each run do 10 k fold cross validation
        for k in range(0, 10):
            # iterate through each fold
            # and create the train/test data subsets
            train, test = cv_utils.train_test_split(data, folds_path=folds_location, fold_number=k)
            scaler = StandardScaler()
            train[['Lux', 'Float time value']] = scaler.fit_transform(train[['Lux', 'Float time value']])
            test[['Lux', 'Float time value']] = scaler.transform(test[['Lux', 'Float time value']])
            print(f"{Colours.CYAN}\nFOLD NUMBER : {k}{Colours.ENDC}")

            epsilon_val_index = 0
            # check each epsilon value
            for epsilon_value in epsilon_values:
                # define the objective perturbation SVM
                huber = obj_SVM.SVM(privatised=True, lambda_value=privatised_lambda, h_val=h_val)
                huber.model_fit(data=train, epsilon_p=epsilon_value)
                # get the accuracy
                accuracy = 1 - huber.evaluate(train)
                # store the accuracy
                accuracy_list[epsilon_val_index] = accuracy_list[epsilon_val_index] + accuracy
                epsilon_val_index = epsilon_val_index + 1
                print(f"epsilon {epsilon_value} accuracy {accuracy}")
            # not privatised Huber loss SVM
            plain_svm = obj_SVM.SVM(lambda_value=public_lambda, h_val=h_val, privatised=False)
            plain_svm.model_fit(epsilon_p=None, data=train)
            accuracy_plain = 1 - plain_svm.evaluate(test)
            # add the plain svm accuracy value to the last index (9)
            accuracy_list[len(epsilon_values)] = accuracy_list[len(epsilon_values)] + accuracy_plain
            print(f"plain {accuracy_plain}")

        # get the average accuracies of the whole run
        run_avg = run_avg + accuracy_list/10

    # get the overall average of all the runs
    final_average = run_avg/runs
    # print the results
    print(f"\n{Colours.GREEN}AVERAGE ACCURACY:{Colours.ENDC}")
    for j in range(0, len(epsilon_values)-1):
        print(f"epsilon {epsilon_values[j]} accuracy {final_average[j]}")
    last_index = len(epsilon_values)-1
    print(f"plain Huber svm accuracy {final_average[last_index]}")


""""
Program entry function
"""
def main():
    # load the dataset
    data = pd.read_csv('../datasets/training/balanced/afternoon_0.csv', header=0, sep=',')
    # choose the function (grid search/privacy and accuracy trade-off evaluation)
    grid_search(data)
    privacy_accuracy_evaluation(data)


""""
Program entry point
"""
if __name__ == '__main__':
    main()
