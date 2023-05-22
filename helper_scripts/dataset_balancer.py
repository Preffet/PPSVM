import pandas as pd
from imblearn.over_sampling import RandomOverSampler
import matplotlib.pyplot as plt
import matplotlib
from imblearn.under_sampling import RandomUnderSampler
# update/change matplotlib backend if not running on macosx
# as it might give errors on Windows if left as it is
matplotlib.use('MACOSX')


"""
Simple script to balance out uneven datasets
either by under sampling or over sampling.
It also plots the class distribution before
and after balancing the datasets.
"""

# load the chosen dataset
dataset_name = "all_data_including_anomalous"
df = pd.read_csv(f'../datasets/all_data/{dataset_name}.csv', header=0, sep=',')
# get x values and labels
X = df.drop(['Label'], axis=1)
y = df['Label']

# check the class distribution and plot it
plt.figure()
plot1 = y.value_counts().plot.pie(
    autopct='%.2f',
    colors=['#97BC62FF', '#BD6565'])

# set plot title
title = f"Class balance in the {dataset_name}.csv file"
plot1.set_title(title)
figure_name = f"plots/class-distribution-{dataset_name}.png"

# save the image of the class distribution before balancing
plot1.figure.savefig(figure_name)

# create a figure for the second pie chart
plt.figure()
# balance out the classes
# change to RandomOversampler to do oversampling instead
ros = RandomOverSampler(sampling_strategy="auto")
X_res, y_res = ros.fit_resample(X, y)
# set title
title = f"Class balance in the {dataset_name}.csv file"

# plot the class distribution after balancing it
plot2 = y_res.value_counts().plot.pie(autopct='%.2f',colors=['#97BC62FF', '#BD6565'])
plot2.set_title(title)
plot2.figure.savefig(f"plots/class-distribution-after-balancing-{dataset_name}.png")

# save the dataset to a file
X_res.columns = [
    'Date',
    'Hour',
    'Minute',
    'Lux',
    'Float time value']
dataset = X_res.assign(Label=y_res.reset_index(drop=True))
dataset.to_csv(f"balanced-{dataset_name}.csv", index=False)
