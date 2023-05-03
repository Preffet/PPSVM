import pandas as pd
from datetime import datetime


# function to locate empty and NaN columns in the dataset
def check_for_empty_cells(data_frame):
    missing_cols, missing_rows = (
        (data_frame.isnull().sum(x) | data_frame.eq('').sum(x))
                .loc[lambda x: x.gt(0)].index
            for x in (0, 1))

    if not data_frame.loc[missing_rows, missing_cols].empty:
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
        if not 0 <= float(val['Lux'])<=200000:
                invalid = True
                print("\nInvalid Lux value found:")
                print(val)
    except:
        print("\nNon-numeric Lux value found:")
        print(val)


# function to check if the
# date values are in correct format
def validate_date(val):
    # check the data type
    try:
        datetime.strptime(val['Date'],'%Y-%m-%d')
    except:
        print("Invalid date date found:")
        print(val)


# program entry point
def main():
    # open the file which contains the dataset for reading
    df = pd.read_csv(
        "datasets/all_data/collected_light_data.csv",
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


if __name__ == "__main__":
    main()