'''
╔═══════════════════════════════════════════════════╗
 Privacy Preserving SVM for anomaly detection in ASNs
  Justina Metrikyte (c0037826), Newcastle University
╚═══════════════════════════════════════════════════╝
'''

## Import Libraries
import numpy as np
from numpy import where
# Data processing
import pandas as pd
# Visualization
import matplotlib.pyplot as plt
# Model and performance
from sklearn.svm import OneClassSVM
from matplotlib import use as mpl_use

# Change/delete/update to other matplotLib back-end
# if using other OS than MacOSX, I had to add this as the default one
# caused the app to crash while running on my laptop
mpl_use('MacOSX')

# import training data
data = pd.read_csv("datasets/trainingLightData.csv")
# pick the features
df = data[["hour","light"]]

# model specification
model = OneClassSVM(kernel = 'rbf', gamma =0.01, nu = 0.1).fit(df)

# import data for predictions
data2 = pd.read_csv("datasets/mixedLightData.csv")
# input features
dff = data2[["hour","light"]]

# make the predictions
y_pred = model.predict(dff)

# filter outlier indexes
outlier_index = where(y_pred == -1)
# filter outlier values
print(outlier_index)
outlier_values = dff.iloc[outlier_index]
print(outlier_values)

# visualize outputs
# title
plt.title("Anomaly detection for data from light sensors")
# set x,y axis ticks
plt.xticks(range(0, 24))
plt.yticks(np.arange(0, 21000, 1000))
# labels
plt.xlabel("Time of the day (hour)")
plt.ylabel("Light level (lux)")

# all the given data
plt.scatter(data2["hour"],data2["light"],
            color='#5D9C59',label="Valid data",marker="s",s=200,alpha=.5)
# anomalies
plt.scatter(outlier_values["hour"],outlier_values["light"]
            ,color='#DF2E38',label="Anomalous data",marker="s",s=200, alpha=.5)

plt.legend(loc="upper left")


plt.savefig("figures/figure1.png")



