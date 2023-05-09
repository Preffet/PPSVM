import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib as mpl
from matplotlib.lines import Line2D

"""
Small script to plot all collected data,
both valid and anomalous, and save the 
plot as a png file to the figures folder
"""

# define colours
green_colour = ['#6bb002']
green = [x for x in green_colour for reps in range(7)]
red = ['#F90627']

# load the dataset
df = pd.read_csv('./datasets/all_data/all_data_including_anomalous.csv', header=0, sep=',')
all_data = df.loc[:, ['Date', 'Float time value', 'Lux', 'Label']]

# filter the valid and invalid data entries
anomalous_data = all_data.loc[df['Label'] == -1]
valid_data = all_data.loc[df['Label'] == 1]

# set parameters for plotting
sns.set_palette(red, desat=0.4)
mpl.rcParams['lines.markersize'] = 6

# invalid data
plot = sns.scatterplot(
    data=anomalous_data,
    x="Float time value",
    y="Lux",
    alpha=0.45,
    size=None,
    style=None,
    sizes=None,
    size_order=None,
    size_norm=None,
    marker='o')

# valid data
plot = sns.lineplot(
    data=valid_data,
    x="Float time value",
    y="Lux",
    hue="Date",
    linewidth=3.5,
    palette=green,
    alpha=0.7,
    err_style='band')

# set the ticks
plot.set(xticks=np.arange(0, 24, 1))
# set the labels
plot.set(xlabel='Time (Hour)', ylabel='Illuminance (Lux)')
# remove the original legend
plot.get_legend().remove()
# replace it with a better one
custom_lines = [Line2D([0], [0], color='#6bb002', lw=4),
                Line2D([], [], color='#BD455B', marker='o', linestyle='None', markersize=7)]

plot.legend(custom_lines,
            ['Valid Data', 'Anomalous Data'],
            loc="upper left",
            fancybox=True,
            framealpha=0.9)

fig = plot.get_figure()
# save the figure
fig.savefig("./helper_scripts/plots/figures/all-collected-data-with-anomalies.png")
