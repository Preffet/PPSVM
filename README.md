## Privacy Preserving SVM Code
## Installation
To run the Project, first start the SVM.py file and select the privacy options. Following this, Run the Server.py to start the server listener between the client nodes and the SVM.

The data which the clients send is stored in the /datasets/simulation_nodes.
Different datasets are picked depending on the time of the day. To update the application to real time, go to client.py and change current_hour = 10 to datetime.now().hour. Do the same in the SVM.py script too so that predictions could be made using the right training data.

- If the code runs, but as soon as the server receives a message there is an error about a missing scaler, then pull this version of the code, it has been fixed.
- If the server starts, but nothing happens, most likely it failed to bind to a port -> change the global PORT variable to a different number, make sure to update the PORT variable in the client.py code to the same number.


## Testing
All the tests to check privacy/accuracy loss are provided in the /tests folder
- membership_inference.py test the membership attack accuracy on different clasifers.
- privatised_dataset_tests.py test the effect of applying different levels of laplacian noise to the datasets
- testing_objective_perturbation.py evaluate accuracy tradeoff when running differentially private SVM with different epsilon values
