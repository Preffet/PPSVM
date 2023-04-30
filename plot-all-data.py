import numpy as np
import pandas as pd
import seaborn as sns

# plot all the collected data and
# save to a file
from matplotlib import ticker

df = pd.read_csv('datasets/collected_light_data.csv', header=0, sep=',')
all_data_to_plot = df.loc[:, ['Date', 'Float time value', 'Lux']]
plot = sns.lineplot(data=all_data_to_plot, x="Float time value", y="Lux", hue="Date",linewidth = 3.5, palette=['#0ad2ff', '#8bd346', '#16a4d8', '#f9a52c', '#ec458d', '#efdf48', '#9b5fe0'], alpha  = 0.55, err_style='band')
plot.set(xticks=np.arange(0,24,1))
plot.set(xlabel='Time (Hour)', ylabel='Illuminance (Lux)')
fig = plot.get_figure()
fig.savefig("all-collected-data.png")
