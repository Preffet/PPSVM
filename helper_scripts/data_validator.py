import pandas as pd
from datetime import datetime

"""
Simple script to check the initial dataset.
Checks if there are any empty cells,
if fields which should be numeric are numeric,
if date is in the right format, and if
lux and time values are within a reasonable range
"""


# ANSI escape codes to print coloured text
class Colours:
    ENDC = '\033[0m'
    BLUE = '\033[94m'


# function to locate empty and NaN columns in the dataset
def check_for_empty_cells(data_frame):
    missing_cols, missing_rows = (
        (data_frame.isnull().sum(x) | data_frame.eq('').sum(x))
                .loc[lambda x: x.gt(0)].index
            for x in (0, 1))

    if not data_frame.loc[missing_rows, missing_cols].empty:
        # print the columns with the located empty cells
        print("Columns with empty or NaN values found:")
        print(data_frame.loc[missing_rows, missing_cols])
        return 1
    else:
        return 0


# function to validate lux values
def validate_lux(val):
    try:
        # check if it is a numerical value
        float(val['Lux'])
        # check if it is >=0 and <=200 000
        if not 0 <= float(val['Lux']) <= 200000:
                invalid = True
                print("\nInvalid Lux value found:")
                print(val)
    except:
        print("\nNon-numeric Lux value found:")
        print(val)


# function to check if the
# date values are in a correct format
def validate_date(val):
    # check the data type
    try:
        datetime.strptime(val['Date'], '%m/%d/%Y')
    except:
        print("Invalid date found:")
        print(val)


"""
Program entry point. First read the data,
then check for empty cells, if not found,
check if numeric fields are actually numeric,
after that, check their range. Finally,
validate the date fields.
"""


def main():
    print(f"{Colours.BLUE}Running this script will provide information about any invalid data present in the dataset.")
    print(f"If this is the only message displayed, then all the data in the dataset is valid.{Colours.ENDC}")
    # open the file which contains the dataset for reading
    df = pd.read_csv(
        "./datasets/all_data/all_collected_valid_data.csv",
            sep=",",
            header=0)
    # convert values to strings
    df['Hour'] = df['Hour'].astype(str)
    df['Minute'] = df['Minute'].astype(str)
    df['Lux'] = df['Lux'].astype(str)

    # if no empty/NaN cells exist,
    # check data format and values
    if not (check_for_empty_cells(df)):

        # check if all hour fields are numeric (int)
        if not (df[~df['Hour'].map(lambda x: x.isnumeric())]).empty:

            print("Non-numeric hour values found:")
            print(df[~df['Hour'].map(lambda x: x.isnumeric())])

        # in they are, check if the data is between 0 and 23
        else:
            # convert hours to integers
            df['Hour'] = df['Hour'].astype(int)
            filtered_invalid_hour = df[~df['Hour'].between(0, 23)]
            if not filtered_invalid_hour.empty:

                print("Invalid hour values found:")
                print(filtered_invalid_hour)

        # check if all minute fields are numeric (int)
        if not (df[~df['Minute'].map(lambda x: x.isnumeric())]).empty:

            print("Non-numeric minute values found:")
            print(df[~df['Hour'].map(lambda x: x.isnumeric())])

        # if they are, check if the data is between 0 and 59 minutes
        else:
            df['Minute'] = df['Minute'].astype(int)
            filtered_invalid_mins = df[~df['Minute'].between(0, 59)]
            if not filtered_invalid_mins.empty:
                print("\nInvalid minute values found:")
                print(filtered_invalid_mins)

        # Check if the date field is valid
        df.apply(lambda x: validate_date(x), axis=1)

        # check if all lux fields are numeric (int/float)
        # and between 0 and 200 000 lux
        df.apply(lambda x: validate_lux(x), axis=1)


"""
Program entry point
"""
if __name__ == "__main__":
    main()
