import glob

import pandas as pd
import plotly.express as px


file_dirs = glob.glob("/home/mjcshields/Stave/RTS-Luna/Data-Phase1/Subjects 2-20/*")

unreadable = []
channel2 = pd.DataFrame()
for file_dir in file_dirs:
    files = glob.glob(file_dir + "/*.csv")
    files.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))

    complete_channel = []

    for file in files:
        try:
            data = pd.read_csv(file, header=None, encoding="utf_16", skiprows=5)
            starting_index = 1
            ending_index = 0
            for index, row in data.iterrows():
                if "CH 3" in str(row[0]):
                    ending_index = index - 2
                    break
            complete_channel = complete_channel + data.loc[starting_index:ending_index,
                                                  data.columns.tolist()[6]].to_list()
        except Exception as e:
            print(e)
            unreadable.append(file)

    if len(complete_channel) > 0:
        if len(complete_channel) < channel2.shape[0]:
            complete_channel.extend([0] * (channel2.shape[0] - len(complete_channel)))
        elif len(complete_channel) > channel2.shape[0] != 0:
            complete_channel = complete_channel[:channel2.shape[0]]
        channel2[file_dir.split("/")[-1]] = complete_channel

fig = px.imshow(channel2)
fig.show()