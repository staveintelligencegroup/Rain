import glob
from math import pi

import pandas as pd
import polars as pl
import plotly.graph_objects as go


subjects = ["02", "03", "04", "08", "09", "11", "12", "13", "15", "17", "18", "19", "20"]
subject_data = pd.DataFrame(index=subjects, columns=range(12))
for subject in subjects:
    file_dirs = glob.glob(f"/home/mjcshields/Stave/RTS-Luna/Data-Phase1/Subjects 2-20/{subject}/*.csv")
    critical_freq = 50000
    epoch_reactance = pd.DataFrame(index=range(12), columns=["mu24", "mu34", "mu568"])

    file_dirs.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))

    i=0
    for file in file_dirs:
        data = pd.read_csv(file, header=None, encoding="utf_16", skiprows=6, usecols=range(7))
        data = pl.DataFrame(data)
        temp = data.drop_nulls()
        temp = temp.with_row_count(name="row")
        starting_rows = (temp.filter(pl.col("0") == "100000").select(pl.col("row")))["row"].to_list()
        ending_rows = (temp.filter(pl.col("0") == "3").select(pl.col("row")))["row"].to_list()
        data = data.drop_nulls()

        channel_reactance = pd.DataFrame(columns=[f"channel_{channel}_reactance" for channel in range(2, 8)])
        for channel, start, end in zip(range(2, 9), starting_rows, ending_rows):
            subset = data[start:end]
            subset = subset.cast(pl.Float64)
            subset = subset.with_columns((abs(50000 - pl.col("0"))).alias("freq_diff"))
            subset = subset.filter(pl.col("freq_diff") == pl.col("freq_diff").min())

            reactance = 0.5 * pi * subset[0, 0] * subset[0, 6]
            channel_reactance.loc[0, f"channel_{channel}_reactance"] = reactance
            channel_reactance.loc[0, f"channel_{channel}_resistance"] = subset[0, 3]

        epoch_reactance.loc[i, "mu24"] = (channel_reactance.loc[0, "channel_2_reactance"] + channel_reactance.loc[0, "channel_4_reactance"])/2
        epoch_reactance.loc[i, "mu34"] = (channel_reactance.loc[0, "channel_3_reactance"] + channel_reactance.loc[0, "channel_4_reactance"])/2
        epoch_reactance.loc[i, "mu568"] = (channel_reactance.loc[0, "channel_5_reactance"] + channel_reactance.loc[0, "channel_6_reactance"] + channel_reactance.loc[0, "channel_8_reactance"])/3
        epoch_reactance.loc[i, "mu24_resistance"] = (channel_reactance.loc[0, "channel_2_resistance"] + channel_reactance.loc[
            0, "channel_4_resistance"]) / 2
        epoch_reactance.loc[i, "mu34_resistance"] = (channel_reactance.loc[0, "channel_3_resistance"] + channel_reactance.loc[
            0, "channel_4_resistance"]) / 2
        epoch_reactance.loc[i, "mu568_resistance"] = (channel_reactance.loc[0, "channel_5_resistance"] + channel_reactance.loc[
            0, "channel_6_resistance"] + channel_reactance.loc[0, "channel_8_resistance"]) / 3
        i += 1

    epoch_reactance["noise_reduced_reactance"] = ((epoch_reactance["mu24"] - (epoch_reactance["mu24"] + epoch_reactance["mu34"])/epoch_reactance["mu568"]) + (epoch_reactance["mu34"] - (epoch_reactance["mu24"] + epoch_reactance["mu34"])/epoch_reactance["mu568"]))/epoch_reactance[[col for col in epoch_reactance.columns if "resistance" in col]].mean(axis=1)
    subject_data.loc[subject, :] = epoch_reactance["noise_reduced_reactance"]

fig = go.Figure()
for x in ["mu24", "mu34", "mu568"]:
    for y in ["mu24_resistance", "mu34_resistance", "mu568_resistance"]:
        fig.add_trace(go.Scatter(x=epoch_reactance[x], y=epoch_reactance[y], text=epoch_reactance.index,
                                 name=f"{x} vs. {y}", mode="markers", marker_color=epoch_reactance.index))
fig.update_layout(
    font=dict(
        family="Courier New, monospace",
        size=18,  # Set the font size here
        color="RebeccaPurple"
    )
)
fig.show()

fig = go.Figure()
for subject in subjects:
    fig.add_trace(go.Scatter(x=subject_data.columns, y=subject_data.loc[subject, :], name=f"Subject {subject}"))
fig.show()