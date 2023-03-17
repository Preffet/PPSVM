'''
╔═══════════════════════════════════════════════════╗
 Privacy Preserving SVM for anomaly detection in ASNs
╚═══════════════════════════════════════════════════╝
Justina Metrikyte (c0037826), 2023 May
'''

###### Step 1: Import Libraries
# Synthetic dataset
import csv

from numpy import where
from sklearn.datasets import make_classification
# Data processing
import pandas as pd
import numpy as np
from collections import Counter
# Visualization
import matplotlib.pyplot as plt
# Model and performance
from sklearn.svm import OneClassSVM
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from matplotlib import use as mpl_use
from sklearn.utils import Bunch


mpl_use('MacOSX')

# import training data
data = pd.read_csv("dataset.csv")
df = data[["month", "temperature","humidity"]]

# model specification
model = OneClassSVM(kernel = 'rbf', gamma = 0.001, nu = 0.03).fit(df)

# import data for predictions
data2 = pd.read_csv("test.csv")# input data
dff = data2[["month", "temperature","humidity"]]
# make the predictions
y_pred = model.predict(dff)

# filter outlier indexes
outlier_index = where(y_pred == -1)
# filter outlier values
print(outlier_index)
outlier_values = dff.iloc[outlier_index]
print(outlier_values)

# visualize outputs
plt.scatter(data2["temperature"],dff["humidity"])
plt.scatter(outlier_values["temperature"],outlier_values["humidity"], c = "r")
plt.savefig("figure1.png")

