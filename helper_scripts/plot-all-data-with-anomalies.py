# plot all the collected data and
# save to a file
import numpy as np
import pandas as pd
import seaborn as sns

green_colour = ['#6bb002']
green = [x for x in green_colour for reps in range(7)]
red = ['#F90627']
# load the dataset
df = pd.read_csv('./datasets/all_data/all_data_including_anomalous.csv', header=0, sep=',')
all_data = df.loc[:, ['Date', 'Float time value', 'Lux', 'Label']]
# filter the valid and invalid data entries
anomalous_data = all_data.loc[df['Label'] == -1]
valid_data = all_data.loc[df['Label'] == 1]

sns.set_palette(red, desat=0.4)
import matplotlib as mpl
mpl.rcParams['lines.markersize'] = 6
plot = sns.scatterplot(data=anomalous_data,
                x="Float time value", y="Lux",
                alpha  = 0.45,
                size=None,
                style=None,
                sizes=None,
                size_order=None,
                size_norm=None,
                marker='o')

plot = sns.lineplot(data=valid_data, x="Float time value", y="Lux", hue="Date",linewidth = 3.5, palette=green, alpha  = 0.7, err_style='band')
plot.set(xticks=np.arange(0,24,1))
plot.set(xlabel='Time (Hour)', ylabel='Illuminance (Lux)')
plot.get_legend().remove()
from matplotlib.lines import Line2D
custom_lines = [Line2D([0], [0], color='#6bb002', lw=4),
                Line2D([], [], color='#BD455B', marker='o', linestyle='None',
                                               markersize=7)]
plot.legend(custom_lines, ['Valid Data', 'Anomalous Data'], loc = "upper left",fancybox=True, framealpha=0.9)
#plot = sns.lineplot(data=anomalous_data, x="Float time value", y="Lux", hue="Date",linewidth = 3.5, palette=['#0ad2ff', '#8bd346', '#16a4d8', '#f9a52c', '#ec458d', '#efdf48', '#9b5fe0'], alpha  = 0.55, err_style='band')
fig = plot.get_figure()
fig.savefig("./helper_scripts/plots/all-collected-data-with-anomalies.png")
