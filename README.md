![Badge tracking last commit](https://img.shields.io/github/last-commit/Preffet/PPSVM?color=%23013987)
![Badge tracking number of files](https://img.shields.io/github/directory-file-count/Preffet/PPSVM?color=%23016a87)
![Badge tracking code size](https://img.shields.io/github/languages/code-size/Preffet/PPSVM?color=%2301877a)
![Badge tracking repo size](https://img.shields.io/github/repo-size/Preffet/PPSVM?color=%23013987)
![github-header-image(1)](https://github.com/Preffet/PPSVM/assets/84241003/3a7b177e-67ee-4780-8c7e-37caabc1ec42)

---------------------------------------------------------------------------

## Privacy Preserving SVM Code
## Installation
To run the Project, first start the SVM.py file and select the privacy options. Following this, Run the Server.py to start the server listener between the client nodes and the SVM.

- If the code runs, but as soon as the server receives a message there is an error about a missing scaler, please pull this version of the code, it has been fixed.
- If the server starts, but nothing happens, most likely it failed to bind to a port because some other application is using the same port. To fix this change the global PORT variable to a different number, make sure to update the PORT variable in the client.py code to the same number.

The data which the clients send is stored in the /datasets/simulation_nodes.
Different datasets are picked depending on the time of the day. For testing purposes, the time has been set to 10 am,
but you can update the application to real time. To do so, go to client.py and change current_hour = 10 to datetime.now().hour. Do the same in the SVM.py script so that predictions could be made using the right training data. Then you can update the csv files. day1.csv represents morning (6am-12am), day2.csv represents afternoon (12am-9pm), night.csv (9pm-6am). So if you change the current_hour to for example, 14, then the nodes will send data from the day2.csv file and the SVM will be trained on the specific data for this time period.

## Testing
All the tests to check privacy/accuracy loss are provided in the /tests folder
- membership_inference.py test the membership attack accuracy on different clasifers.
- privatised_dataset_tests.py test the effect of applying different levels of laplacian noise to the datasets
- testing_objective_perturbation.py evaluate accuracy tradeoff when running differentially private SVM with different epsilon values


