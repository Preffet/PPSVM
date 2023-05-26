
from __future__ import absolute_import, division, print_function, unicode_literals

import numpy as np
import pandas as pd
from IPython.display import clear_output
from matplotlib import pyplot as plt
from sklearn import metrics
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from privacy_preserving_svms import objective_function_perturbation_SVM as obj_perturb_svm
from art import config
from art.estimators.classification import BlackBoxClassifier
from art.attacks.evasion import HopSkipJump
from art.utils import to_categorical
from art.utils import load_dataset, get_file, compute_accuracy
#(x_train, y_train), (x_test, y_test), min_, max_ = load_dataset(str('mnist'))
# import the dataset (with the headers)
df = pd.read_csv('./datasets/training/balanced/morning_0.csv', header=0, sep=',')
#df = pd.read_csv('./datasets/training/balanced/membership_inference_original.csv', header=0, sep=',')

# define the scaler
scaler = StandardScaler()

# get X and y values from the dataset
X = df.loc[:, ['Lux','Float time value']]
y = df['Label']
# convert to numpy array
X = X.values
y = y.values
y = np.where(y == 0, -1, y)
# split the data into train and test datasets
# 70% for training, 30% for predictions
x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.50,random_state=1)
#(x_target, y_target), (x_shadow, y_shadow), _, _ = load_nursery(test_set=0.75)

# Sample predict function that reformats inputs, connects to wml scoring endpoint and
# returns one-hot encoded predictions

# Create blackbox object
model2 = SVC(C=100)
x_train = scaler.fit_transform(x_train)
model2.fit(x_train,y_train)

x_test = scaler.transform(x_test)
results = model2.predict(x_test)
model_1 = obj_perturb_svm.SVM(privatised=True, lambda_value=0.2, h_val=1)
# just add the y values to get all the data
model_1.fit_membership_inference(x_train,y_train,epsilon_p=0.3)

def manual_to_categorical(labels, nb_classes):
    result = np.zeros((len(labels), nb_classes))
    for i, label in enumerate(labels):
        if label == -1:
            result[i, 0] = 1
        else:  # assuming label is 1
            result[i, 1] = 1
    return result


def predict(x):
    x = np.array(x)
    predictions = model_1.membership_inference_predict(x)
    predictions = list(map(int, predictions))
    return manual_to_categorical(predictions, nb_classes=2)

classifier = BlackBoxClassifier(predict, x_test.shape,2)




import numpy as np
from art.attacks.inference.membership_inference import MembershipInferenceBlackBoxRuleBased

attack = MembershipInferenceBlackBoxRuleBased(classifier)

# infer attacked feature
inferred_train = attack.infer(x_train, y_train)
inferred_test = attack.infer(x_test, y_test)

# check accuracy
train_acc = np.sum(inferred_train) / len(inferred_train)
test_acc = 1 - (np.sum(inferred_test) / len(inferred_test))
acc = (train_acc * len(inferred_train) + test_acc * len(inferred_test)) / (len(inferred_train) + len(inferred_test))
print(f"Members Accuracy: {train_acc:.4f}")
print(f"Non Members Accuracy {test_acc:.4f}")
print(f"Attack Accuracy {acc:.4f}")


test_data = pd.DataFrame({
    'Lux': x_test[:, 0],
    'Time float value': x_test[:, 1],
    'Label': y_test
})

print('Base model accuracy: ')
print(accuracy_score(results,y_test))