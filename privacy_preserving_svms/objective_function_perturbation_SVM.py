import numpy as np
from scipy import optimize

"""
Implementation of differentially private SVM.
This class which allows to train and evaluate 
both: differentially private svm
(using objective perturbation) and plain
svm with modified loss function (Huber)

Credits: 
Chaudhuri, K., Monteleoni, C. and Sarwate, A. (2011)
‘Differentially Private Empirical Risk Minimization’,
Journal of Machine Learning Research, 12, pp. 1069–1109.
Available at: https://jmlr.org/papers/volume12/chaudhuri11a/chaudhuri11a.pdf.

Algorithm 2 ERM with objective perturbation,

Implementation in R:
(Explanations)
https://search.r-project.org/CRAN/refmans/DPpack/html/svmDP.html
"""


class SVM:
    def __init__(self, privatised, lambda_value, h_val):
        self.private = privatised
        self.h = h_val
        self.lambda_value = lambda_value
        self.c = 1/(self.h*2)

    """"
    fit the SVM model (train)
    """
    def model_fit(self, epsilon_p, data):
        # dataset labels
        train_y = data["Label"]
        # dataset features
        train_x = data.drop(columns=["Label"])

        train_x = train_x.values
        train_y = train_y.values
        # number of features
        self.n = train_x.shape[0]
        self.num_of_features = train_x.shape[1]
        # at first guess the optimisation value
        initial_f = np.ones(self.num_of_features)
        
        if self.private:
            # calculate epsilon p prime
            c_squared = self.c ** 2
            n_squared = self.n ** 2
            lambda_squared = self.lambda_value ** 2

            first_term = 2 * self.c / (self.n * self.lambda_value)
            second_term = c_squared / (n_squared * lambda_squared)

            epsilon_p_prime = epsilon_p - np.log(1 + first_term + second_term)

            # determine the delta value
            if epsilon_p_prime > 0:
                delta_val = 0

            else:
                exp_term = np.exp(epsilon_p / 4) - 1
                numerator = self.c / (self.n * exp_term)
                delta_val = numerator - self.lambda_value
                epsilon_p_prime = epsilon_p / 2

            # create noise according to epsilon_p_prime
            scale_factor = 2 / epsilon_p_prime
            size_parameter = self.num_of_features
            noise = np.random.exponential(scale_factor, size_parameter)

            # use BFGS method to optimise the function
            initial_guess = initial_f
            additional_args = (train_x, train_y, noise)
            display = False
            solution = optimize.fmin_bfgs(self.func, initial_guess, args=additional_args, disp=display)
            f = solution

            norm_f_squared = np.linalg.norm(f) ** 2
            self.f = f + (delta_val * norm_f_squared) / 2

        else:
            # if the training is not privatised
            # we should pass a vector with all 0s
            noise = np.zeros(self.num_of_features)
            # use the BFGS method to optimise the function
            solution = optimize.fmin_bfgs(self.func, initial_f, args=(train_x, train_y, noise), disp=False)
            self.f = solution


    """"
    function to find
    the empirical loss
    """
    def func(self, f, train_x, train_y, noise):
        # find the location of the training data to prediction function
        z = np.dot(f.T, train_x.T) * train_y

        # Specify the conditions
        conditions_list = [
            z > 1 + self.h,
            np.abs(1 - z) <= self.h,
            z < 1 - self.h
        ]

        # Specify the corresponding choices
        choices_list = [
            0,
            (1 / (4 * self.h)) * (1 + self.h - z),
            1 - z
        ]

        # Select the loss based on the conditions and choices
        loss_value = np.select(conditions_list, choices_list)

        # return regularized emperical loss, noise is added in this step
        return np.mean(loss_value + (self.lambda_value / 2 * (np.linalg.norm(f) ** 2)) + ((1 / self.n) * np.dot(np.transpose(noise), f)))

    #  make a prediction
    def predict(self, data_sample):
        # flatten the data if it is a numpy array
        flattened_data = data_sample.values.flatten()\
            if not isinstance(data_sample, np.ndarray) else data_sample.flatten()
        # make the prediction
        prediction = np.sign(np.dot(self.f.T, flattened_data))
        return prediction

    # prediction function used for membership inference attacks
    def membership_inference_predict(self, data):
        list = []
        for datapoint in enumerate(data):
            pred = np.sign(np.dot(np.transpose(self.f), datapoint[1]))
            list.append(pred)
        return list

    # train function for membership inference attacks
    def fit_membership_inference(self, train_x, train_y, epsilon_p):
        self.n = train_x.shape[0]
        self.num_of_features = train_x.shape[1]
        # make an initial guess about the optimisation
        innitial_f = np.ones(self.num_of_features)
        # check if training should be privatised
        if self.private:
            # calculate epsilon p prime
            c_squared = self.c ** 2
            n_squared = self.n ** 2
            lambda_squared = self.lambda_value ** 2

            first_term = 2 * self.c / (self.n * self.lambda_value)
            second_term = c_squared / (n_squared * lambda_squared)

            epsilon_p_prime = epsilon_p - np.log(1 + first_term + second_term)

            # check which delta_val should be used
            if epsilon_p_prime > 0:
                delta_val = 0
            else:
                denominator = 2 * self.h * self.n * (np.exp(epsilon_p / 4) - 1)
                delta_val = (1 / denominator) - self.lambda_value
                epsilon_p_prime = epsilon_p / 2

            # create noise according to epsilon_p_prime
            # use the exp distribution where beta value is 2/epsilon_p_prime
            noise = np.random.exponential(2 / epsilon_p_prime, self.num_of_features)

            # optimize function func with BFGS method
            sol = optimize.fmin_bfgs(self.func, innitial_f, args=(train_x, train_y, noise), disp=False)
            f = sol

            self.f = f + (delta_val * np.linalg.norm(f) ** 2) / 2

        else:
            # if the training should not be privatised,
            # use a vector with all 0s instead of noise
            noise = np.zeros(self.num_of_features)
            # optimize function func with BFGS method
            sol = optimize.fmin_bfgs(self.func, innitial_f, args=(train_x, train_y, noise), disp=False)
            self.f = sol

    """
    Prediction function.
    It calculates the location of the testing data relative to the predictor vector f
    and return the error rate 
    """
    def evaluate(self, test_data):
        # test data labels
        df_test_y = test_data["Label"]
        # test data features
        df_test_x = test_data.drop(columns="Label")

        test_x = df_test_x.values
        test_y = df_test_y.values

        error_number = 0
        for idx, datapoint in enumerate(test_x):
            prediction = np.sign(np.dot(np.transpose(self.f), datapoint))
            if prediction != test_y[idx]:
                error_number += 1

        return error_number/test_x.shape[0]
