![Badge tracking number of files](https://img.shields.io/github/directory-file-count/Preffet/PPSVM?color=%23016a87)
![Badge tracking code size](https://img.shields.io/github/languages/code-size/Preffet/PPSVM?color=%2301877a)
![Badge tracking repo size](https://img.shields.io/github/repo-size/Preffet/PPSVM?color=%23013987)
-----------------------------------------------------------------------------
<img width="970" alt="Screen Shot 2023-05-26 at 21 13 09" src="https://github.com/Preffet/PPSVM/assets/84241003/e8e50f61-be77-4074-ac7d-0e25d9b9a24d">

-----------------------------------------------------------------------------
## Installation
To run the project, first go to the simulation folder, start the SVM.py file and select the privacy options. Following this, run the server.py to start the server listener between the client nodes and the SVM. Finally, run the client.py file to simulate sensor node/s.


-----------------------------------------------------------------------------
## Troubleshooting
- If the code runs, but as soon as the server receives a message there is an error about a missing scaler, please download this version of the code, it has been fixed.
- If the server starts, but nothing happens, most likely it failed to bind to a port because some other application is using the same port on your pc. To fix this, change the global PORT variable in the server.py to a different number, make sure to update the PORT variable in the client.py code to the same number as well.


-----------------------------------------------------------------------------
# Email Addresses
To update the email address (so that you could receive a notification when an anomalous sensor node is detected) simply change the email in the admin_email.csv file in the /email folder.

-----------------------------------------------------------------------------
# Different Datasets
The data which the clients send is stored in the /datasets/simulation_nodes.
Different datasets are picked depending on the time of the day. For testing purposes, the time has been set to 10 am,
but you can update the application to real time. To do so, go to client.py and change current_hour = 10 to datetime.now().hour. Do the same in the SVM.py script so that predictions could be made using the right training data. Then you can update the csv files. day1.csv represents morning (6am-12am), day2.csv represents afternoon (12am-9pm), night.csv (9pm-6am). So if the current_hour variable is equal to, for example, 14, then the nodes will send data from the day2.csv file and the SVM will be trained on the specific data for this time period.



-----------------------------------------------------------------------------
## Testing
All the tests to check privacy/accuracy loss are provided in the /tests folder
- membership_inference.py test the membership attack accuracy on different classifiers.
- privatised_dataset_tests.py test the effect of applying different levels of laplacian noise to the datasets
- testing_objective_perturbation.py evaluate accuracy tradeoff when running differentially private SVM with different epsilon values


-----------------------------------------------------------------------------
## Results
The grid search results can be seen in the /results folder. The accuracy evaluation tests have been done manually so there are no csv files, I directly put the statistics in when making diagrams and running the testing scripts.


-----------------------------------------------------------------------------
## Overall Project Structure
```
.
├── README.md
├── datasets
│   ├── all_data
│   │   ├── all_collected_valid_data.csv
│   │   ├── all_data_including_anomalous.csv
│   │   └── balanced-all_data_including_anomalous.csv
│   ├── simulation_nodes
│   │   ├── malicious
│   │   │   └── malicious.csv
│   │   └── valid
│   │       ├── day1.csv
│   │       ├── day2.csv
│   │       └── night.csv
│   └── training
│       ├── balanced
│       │   ├── afternoon_0.csv
│       │   ├── afternoon_1.csv
│       │   ├── balanced-all_data_including_anomalous.csv
│       │   ├── day1_0.csv
│       │   ├── day1_1.csv
│       │   ├── day2_1.csv
│       │   ├── membership_inference_noisy.csv
│       │   ├── membership_inference_original.csv
│       │   ├── morning_0.csv
│       │   ├── morning_1.csv
│       │   └── night.csv
│       └── original
│           ├── day1_0.csv
│           ├── day1_1.csv
│           ├── day2_0.csv
│           ├── day2_1.csv
│           └── night.csv
├── email
│   ├── admin_email.csv
│   ├── instructions.txt
│   ├── real_implementation_email.html
│   └── simulation_email.html
├── helper_scripts
│   ├── cross_validation_utilities.py
│   ├── data_validator.py
│   ├── dataset_balancer.py
│   └── plots
│       ├── class-distribution-after-balancing-night.png
│       ├── class-distribution-night.png
│       ├── figures
│       │   ├── all-collected-data-with-anomalies.png
│       │   └── all-collected-data.png
│       ├── plot-all-data-with-anomalies.py
│       └── plot-all-data.py
├── privacy_preserving_svms
│   ├── Laplace_dataset_privatiser.py
│   ├── abstract_data_privatiser.py
│   └── objective_function_perturbation_SVM.py
├── real_implementation
│   ├── GatewayMQTT.py
│   ├── arduino_sensor_box_code
│   │   └── Arduino Code.ino
│   ├── detection_system_files
│   │   ├── blocklist.csv
│   │   ├── clients.csv
│   │   └── malicious_data_received.csv
│   └── send_email_report.py
├── requirements.txt
├── results
│   ├── differentiallyPrivate_SVM_Grid_Search+Privacy_Eval.txt
│   └── simple_SVM_grid_search_results.txt
├── simulation
│   ├── SVM.py
│   ├── client.py
│   ├── detection_system_files
│   │   ├── blocklist.csv
│   │   ├── clients.csv
│   │   └── scalers
│   │       ├── df1scaler.pkl
│   │       └── df2scaler.pkl
│   ├── malicious_client.py
│   └── server.py
├── tests
│   ├── cross_validation_folds
│   │   └── folds{21h:34m:03s}.csv
│   ├── membership_inference_attacks.py
│   ├── privatised_dataset_tests.py
│   ├── scaler
│   │   └── scaler.pkl
│   └── testing_objective_perturbation_SVM.py
└── write-up
    └── dissertation.pdf
```

-----------------------------------------------------------------------------
## Paper

The full dissertation write-up is located in the /write-up folder, it has been updated to fix initial formatting problems. These problems were caused by unfamiliarity with the LaTeX editor and downloading the document before the LaTeX compilation process was complete. The updated version now has these issues resolved.

-----------------------------------------------------------------------------

## Early Experiments with a LoraWan Router

Inside real_implementation, you'll find an initial implementation 
of a one-class SVM on an actual Arduino router.
However, as the research direction shifted towards exploring
differentially private SVMs and noise addition, and the access to the router was limited, 
these early efforts were no longer central to the final
work and thus were not discussed in the dissertation.
Essentially, the presence of these files is a testament to
the research journey, reflecting an evolutionary path rather than the final destination.