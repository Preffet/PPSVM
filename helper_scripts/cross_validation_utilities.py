import math
import pandas as pd
from datetime import datetime
import pickle as pkl
from sklearn.preprocessing import StandardScaler

"""
This file contains 2 helper functions used for testing/training 
output perturbation SVM. The first function, create_folds_file(),
generates csv files containing the folds for k-fold cross validation,
second function, train_test_split() splits the data into the
training and testing subsets, scales them and saves the scaler
"""


"""
1.
k-fold cross validation function used to 
test the output perturbation SVM.
It generates a csv file containing folds for k-fold
cross validation. First the original dataset is shuffled,
then the data is split into k folds and .
Finally, these folds are appended to a list, which is 
converted to a dataframe and exported as folds{date}. csv file.
P.S. The first line in the files is a header.
"""


def create_folds_file(df):
    # number of folds for k-fold cross validation
    folds_num = 10
    # randomise the indexes
    df_random = df.sample(frac=1)
    # find the fold size
    fold_size = math.floor(df_random.shape[0]/folds_num)

    all_folds = []

    # generate the folds
    # (& store the indexes to the original dataset, not the actual values)
    for i in range(0, folds_num):
        # get all data indexes between the start of the current
        # and the next fold
        if i != fold_size:
            fold_data = df_random.iloc[(i) * fold_size: (i + 1) * fold_size].index.values
        else:
            # if it is the last fold just get all the remaining data indexes
            fold_data = df_random.iloc[(i) * fold_size:].index.values

        # append the current fold to the list of all folds
        all_folds.append(fold_data)

    # save to a csv file & return the file name
    filename = 'cross_validation_folds/folds{' + datetime.today().strftime('%Hh:%Mm:%Ss') + '}.csv'
    pd.DataFrame(all_folds).to_csv(filename, header=True, index=False)
    return filename


"""
2.
Function which performs train, test, split and
data pre-processing (scaling using 
scikit-learn StandardScaler()). It is 
called when iterating over each fold in the
cross-validation procedure and generates test/train sets for each fold.
Also, it saves the scaler as scaler.pkl file to be used 
later when plotting results, debugging etc.
"""


def train_test_split(data, folds_path, fold_number):

    # read the fold indices
    fold_ind = pd.read_csv(folds_path).iloc[fold_number].dropna().values

    # test, train dataset split
    # 1. test
    test = data.iloc[fold_ind]
    test_x_data = test.loc[:, ['Lux', 'Float time value']]
    test_y_data = test.loc[:, ['Label']]
    # 2. train
    train = data.drop(fold_ind, axis='index')
    train_x_data = train.loc[:, ['Lux', 'Float time value']]
    train_y_data = train.loc[:, ['Label']]

    # standardize features by removing the mean and scaling to unit variance.
    # The standard score of a sample x is calculated as:
    #  z = (x - u) / s
    # where u is the mean of the training samples
    scaler = StandardScaler()

    # standardize the data (x training and testing values)
    train_x_data = pd.DataFrame(scaler.fit_transform(train_x_data), columns=['Lux', 'Float time value'])
    test_x_data = pd.DataFrame(scaler.transform(test_x_data), columns=['Lux', 'Float time value'])

    # combine with labels
    training_data = train_x_data.assign(Label=train_y_data["Label"].reset_index(drop=True))
    testing_data = test_x_data.assign(Label=test_y_data["Label"].reset_index(drop=True))

    # reset the indices
    training_data.reset_index(inplace=True, drop=True, )
    testing_data.reset_index(inplace=True, drop=True, )

    # save the scaler as pkl file
    with open(f"scaler/scaler.pkl", "wb") as outfile:
        pkl.dump(scaler, outfile)

    return training_data, testing_data

