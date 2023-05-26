![Badge tracking number of files](https://img.shields.io/github/directory-file-count/Preffet/PPSVM?color=%23016a87)
![Badge tracking code size](https://img.shields.io/github/languages/code-size/Preffet/PPSVM?color=%2301877a)
![Badge tracking repo size](https://img.shields.io/github/repo-size/Preffet/PPSVM?color=%23013987)
-----------------------------------------------------------------------------

-----------------------------------------------------------------------------
## Installation
To run the Project, first start the SVM.py file and select the privacy options. Following this, Run the Server.py to start the server listener between the client nodes and the SVM.


-----------------------------------------------------------------------------
## Troubleshooting
- If the code runs, but as soon as the server receives a message there is an error about a missing scaler, please pull this version of the code, it has been fixed.
- If the server starts, but nothing happens, most likely it failed to bind to a port because some other application is using the same port. To fix this change the global PORT variable to a different number, make sure to update the PORT variable in the client.py code to the same number.


-----------------------------------------------------------------------------
# Different Datasets
The data which the clients send is stored in the /datasets/simulation_nodes.
Different datasets are picked depending on the time of the day. For testing purposes, the time has been set to 10 am,
but you can update the application to real time. To do so, go to client.py and change current_hour = 10 to datetime.now().hour. Do the same in the SVM.py script so that predictions could be made using the right training data. Then you can update the csv files. day1.csv represents morning (6am-12am), day2.csv represents afternoon (12am-9pm), night.csv (9pm-6am). So if you change the current_hour to for example, 14, then the nodes will send data from the day2.csv file and the SVM will be trained on the specific data for this time period.


-----------------------------------------------------------------------------
# Email Adresses
To update the email address (so that you could receive a notifcation when an anomalous sensor node is detected) simply change the email in the admin_email.csv file in the /email folder.


-----------------------------------------------------------------------------
## Testing
All the tests to check privacy/accuracy loss are provided in the /tests folder
- membership_inference.py test the membership attack accuracy on different clasifers.
- privatised_dataset_tests.py test the effect of applying different levels of laplacian noise to the datasets
- testing_objective_perturbation.py evaluate accuracy tradeoff when running differentially private SVM with different epsilon values


-----------------------------------------------------------------------------
## Results
The grid search results can be seen in the /results folder. The accuracy evaluation tests have been done manually so there are no csv files, I directly put the statistics in when making diagrams and running the testing scripts.


-----------------------------------------------------------------------------
## Overall Project Structure


