from abc import ABC

import numpy as np
from privacy_preserving_svms.abstract_data_privatiser import ABCPrivacyPreserver


# class which is responsible for preparing
# dataset for privatisation and adding
# laplace noise to increase the privacy of
# individual entries
class LaplacePrivacyPreserver(ABCPrivacyPreserver, ABC):
    # default values
    mean_value = 0.0
    epsilon_value = 1.0

    def __init__(self, epsilon_val=1.0):
        # check if provided epsilon value is valid
        if type(epsilon_val) != float:
          raise ValueError('Epsilon value has to be a float')
        if epsilon_val <= 0.0:
          raise ValueError('Epsilon value has to be >0.0')
        self.epsilon_value = epsilon_val

    def privatise_single_value(self, data, sensitivity_level=1.0):
        # convert it to a float
        try:
          float_value = float(data)
        except:
          raise ValueError('The value to be sanitised has to be float')
        # define the sensitivity value:
        # how much of an impact can an individual value
        # have on the outcome of the queries?
        sensitivity_level = max(0.001, sensitivity_level)
        # add noise to the value:
        # epsilon attribute represents the privacy budget,
        # which is a measure of how much privacy is being
        # provided to the data. Together with the sensitivity
        # it determines the scale of the noise added to the data.
        # the noise is drawn from the Laplace distribution
        noise_value = np.random.laplace(self.mean_value, sensitivity_level / self.epsilon_value, 1)[0]
        return float(float_value + noise_value)


class DataConverter:
    # convert np array into a list
    def convert_from_original(self, original_data):
        if type(original_data) == np.ndarray:
            converted_data = []
            # loop through all the data entries
            for value in original_data:
                converted_data.append(self.convert_from_original(value))
            return converted_data
        else:
            return self.covert_to_float(original_data)

    # convert the data to a float
    def covert_to_float(self, data):
        try:
            return float(data)
        except:
            # inform the user if errors occur
            raise ValueError('Data could not be converted to float')

