import numpy as np
import pandas as pd
import seaborn as sns

"""
Small script to plot all
collected valid data
and save the plot as a png
file to the figures folder
"""

# define colour palette
colours = ['#0ad2ff', '#8bd346', '#16a4d8', '#f9a52c', '#ec458d', '#efdf48', '#9b5fe0']

df = pd.read_csv('./datasets/all_data/all_collected_valid_data.csv', header=0, sep=',')
all_data_to_plot = df.loc[:, ['Date', 'Float time value', 'Lux']]
plot = sns.lineplot(data=all_data_to_plot,
                    x="Float time value",
                    y="Lux",
                    hue="Date",
                    linewidth=3.5,
                    palette=colours,
                    alpha=0.55,
                    err_style='band')
# set the ticks
plot.set(xticks=np.arange(0, 24, 1))
# set the labels
plot.set(xlabel='Time (Hour)', ylabel='Illuminance (Lux)')
fig = plot.get_figure()
# save the figure
fig.savefig("./helper_scripts/plots/figures/all-collected-data.png")
