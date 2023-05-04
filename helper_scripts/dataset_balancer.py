import pandas as pd
from imblearn.over_sampling import RandomOverSampler
import matplotlib.pyplot as plt
# helper script to balance out uneven datasets

# update to different backend if not using macOSX
import matplotlib
matplotlib.use('MACOSX')

# load the chosen dataset
dataset_name = "night"
df = pd.read_csv(f'../datasets/training/original/{dataset_name}.csv', header=0, sep=',')
# get x values and labels
X = df.drop(['Label'], axis=1)
y = df['Label']

# check the class distribution and plot it
plt.figure()
plot1 = y.value_counts().plot.pie(autopct='%.2f',colors=['#97BC62FF','#BD6565'])
# set plot title
title = f"Class balance in the {dataset_name}.csv file"
plot1.set_title(title)
figure_name = f"plots/class-distribution-{dataset_name}.png"
plot1.figure.savefig(figure_name)

# create a figure for the second pie chart
plt.figure()
# balance out the classes
ros = RandomOverSampler(sampling_strategy="not majority")
X_res, y_res = ros.fit_resample(X, y)
# set title
title = f"Class balance in the {dataset_name}.csv file"

# plot the class distribution after balancing it
plot2 = y_res.value_counts().plot.pie(autopct='%.2f',colors=['#97BC62FF', '#BD6565'])
plot2.set_title(title)
plot2.figure.savefig(f"plots/class-distribution-after-balancing-{dataset_name}.png")

# save the dataset to the file
X_res.columns = [
    'Date',
    'Hour',
    'Minute',
    'Lux',
    'Float time value']
dataset = X_res.assign(Label=y_res.reset_index(drop=True))

# save the balanced dataset to a file
dataset.to_csv(f"class-distribution-after-balancing-{dataset_name}", index=False)
