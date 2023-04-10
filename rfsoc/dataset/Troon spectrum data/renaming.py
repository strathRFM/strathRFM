import os
import glob

directory = "C:\\Users\\eilid\\strathRFM\\rfsoc\\dataset\\Troon spectrum data\\"

files = glob.glob(directory + "S_??-??-??_*.sigmf-meta")

# Iterate through the list of files and rename them
for file in files:
    day = file.split("_")[1].split("-")[0]
    month = file.split("_")[1].split("-")[1]
    year = file.split("_")[1].split("-")[2]
    tt = file.split("_")[2].split(".")[0]

    new_filename = "S_{}-{}-{}_{}.sigmf-meta".format(year, month, day, tt)

    new_file_path = file.replace(os.path.basename(file), new_filename)
    if(file != new_file_path):
        os.rename(file, new_file_path)

    print("Renamed {} to {}".format(file, new_file_path))
