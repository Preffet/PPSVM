"""
Class for implementing offline differential privacy.
It adds noise from the Laplace distribution depending
on the calculated sensitivity value/s
"""


class ABCPrivacyPreserver():
    # privatise the provided raw data using different
    # calculated sensitivity values for each column (if there are several)
    def privatise_data(self, raw_values, sensitivity_value=0.01, sensitivity_values_list=None):
        if type(raw_values) == list:
            # return an empty list if provided list is empty
            if len(raw_values) == 0:
                return []
            privatised_data = []
            # if there is no sensitivity values list provided,
            # get one for the given raw data
            if type(raw_values[0]) == list and sensitivity_values_list is None:
                sensitivity_values_list = self.getSensitivityList(raw_values)
            # initialise the counter
            # used to index into the sensitivity_value list when
            # the sensitivity value for a single value is not provided as a float
            counter = 0
            # If the current value entry in the list is not a list,
            # set the sensitivity value to either the sensitivity
            # _value if it is a float, or the value in the sensitivity_value
            # list at the current counter index.
            for value_entry in raw_values:
                if type(value_entry) is list:
                    sensitivity_val = sensitivity_values_list
                else:
                    if type(sensitivity_value) is float:
                        sensitivity_val = sensitivity_value
                    else:
                        sensitivity_val = sensitivity_value[counter]
                # append the privatised data to the list
                privatised_data.append(self.privatise_data(value_entry, sensitivity_val))
                counter += 1
            return privatised_data
        # add noise to a single value if no list is provided
        else:
            return self.privatise_single_value(raw_values, sensitivity_value)

    # get the list of sensitivity values for the provided data
    def get_data_sensitivity_values(self, raw_data_list):
        data_sensitivity_vals_list = []
        for i in range(len(raw_data_list[0])):
            # get all data in the i-th column
            column_data = [row[i] for row in raw_data_list]
            # get the sensitivity value for that column
            single_sensitivity_val = abs(max(column_data)-min(column_data))
            # append to all the sensitivity values
            data_sensitivity_vals_list.append(single_sensitivity_val)
        return data_sensitivity_vals_list

