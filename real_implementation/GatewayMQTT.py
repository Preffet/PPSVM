'''
This is just a script I used to test
whether or not I could send emails
or not when anomalies are detected on the
real network, in order to add the created
svm, the svm from scikit learn library should be
replaced
'''
import json
import base64
import os
import paho.mqtt.client as mqtt
from datetime import datetime
import pandas as pd
from numpy import where
from sklearn.svm import OneClassSVM
# server information
mqttip = '192.168.230.1'
mqttport = 1883
model = None
max_df_value = None


# ANSI escape codes to print coloured/bold text
class colours:
    ENDC = '\033[0m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    ORANGE = '\033[38;5;173m'


# Type your username and password. If the private MQTT server does not require username and password, comment the lines
# mqtt_username = 'username'
# mqtt_password = 'password'

# Replace the "id" with the id of your application and "eui" with your device eui
# mqttrxtopic = 'application/SensorBox/device/a8610a3439307f10/rx'
mqttrxtopic = 'application/SensorBox/device/a8610a3530408b09/rx'
mqttc = mqtt.Client()


def svm_model():
    # get the path to the training data
    path_to_data = os.path.dirname(os.path.dirname(__file__))
    path_to_data = path_to_data + "/datasets/training_light_data.csv"
    # import training data
    data = pd.read_csv(path_to_data)
    # choose the features
    df = data[["hour", "light"]]
    # normalise the data
    normalized_training_data = df / df.max()

    # model specification
    model = OneClassSVM(kernel='rbf', gamma=39, nu=0.03)
    model.fit(normalized_training_data)
    # max df value (to be used for data normalisation)
    max_df_value = df.max()
    return model, max_df_value


def anomaly_detection(lux_value, device_name, dev_eui):
    # round lux values
    lux_value_for_prediction = round(lux_value)
    current_date_and_time = datetime.now()
    hour = current_date_and_time.hour
    # minute = currentDateAndTime.minute
    # timestamp_in_minutes = hour*60+minute
    # print(minute)
    # convert the data to a list
    data_list = [hour, lux_value_for_prediction]
    # convert data to a dataframe
    data_to_be_predicted = pd.DataFrame([data_list], columns=["hour", "light"])
    # normalise the data
    normalized_data_for_predictions = data_to_be_predicted / max_df_value

    # make the prediction
    prediction = model.predict(normalized_data_for_predictions)

    # filter outlier indexes
    outlier_index = where(prediction == -1)
    # filter outlier values
    outlier_values = normalized_data_for_predictions.iloc[outlier_index]
    if not outlier_values.size == 0:
        in_the_blocklist_already = False
        decision = "anomalous"
        # print that the received data is anomalous
        # decision: anomalous
        print(f"\n{colours.BOLD}{colours.RED}⫸{colours.ENDC}"
              f" SVM Decision: {colours.BOLD}{colours.RED}{decision}{colours.ENDC}")

        # get the path to the blocklist.csv file
        path_to_blocklist_csv = os.path.dirname(__file__)
        path_to_blocklist_csv = path_to_blocklist_csv + "/detection_system_files/blocklist.csv"
        # add the node to the blocklist
        with open(path_to_blocklist_csv, "a+") as blocklist:
            # check if the node is not in the blocklist already
            blocklist.seek(0)
            blocklist_contents = blocklist.read()
            if device_name not in blocklist_contents:
                blocklist.write(f"{device_name},"
                                f"{dev_eui},"
                                f"{current_date_and_time.date()} "
                                f"{current_date_and_time.hour}:{current_date_and_time.minute}\n")
            else:
                in_the_blocklist_already = True

        # get the path to the malicious_data_received.csv file (logs)
        path_to_logs = os.path.dirname(__file__)
        path_to_logs = path_to_logs + "/detection_system_files/malicious_data_received.csv"
        # add the malicious information received to the logs
        with open(path_to_logs, "a+") as log_file:
            log_file.write(f"{device_name},"
                            f"{dev_eui},"
                            f"{current_date_and_time.date()} "
                            f"{current_date_and_time.hour}:{current_date_and_time.minute},"
                           f"{lux_value_for_prediction}\n")

        # if the device is not in the blocklist already
        # Print: device added to the blocklist {device_name}, device EUI {device_eui}
        if not in_the_blocklist_already:
            print(f"{colours.BOLD}{colours.RED}⫸{colours.ENDC}"
                  f" Device {colours.BOLD}"
                  f"{colours.RED}{device_name}"
                  f"{colours.ENDC} added to the blocklist{colours.ENDC}\n")
        # if the device in the blocklist already print a reminder to inform the system administrators
        else:
            print(f"{colours.BOLD}{colours.RED}⫸ {colours.ENDC}"
                  f"Device {colours.RED}{colours.BOLD}{device_name}{colours.ENDC} "
                  f"is already in the blocklist,\n"
                  f"   please run the{colours.RED}{colours.BOLD} send_email_report.py{colours.ENDC} script"
                  f" to inform the administrators.\n")
    else:
        decision = "valid"
        # print that the received data is valid
        # decision: valid
        print(f"\n{colours.BOLD}{colours.GREEN}⫸{colours.ENDC}"
              f" Decision: {colours.BOLD}{colours.GREEN}{decision}{colours.ENDC}")


# Convert string to hexadecimal
def strtohex(s):
    return r"\x" + r'\x'.join([hex(ord(c)).replace('0x', '') for c in s])


# Once subscribed to the message, call back this method
def onmessage(mqttc, obj, msg):
    onprintraknodeinfo(msg.payload)


# Print the subscribed node information
def onprintnoderxinfo(jsonrx):
    try:
        devEUI = jsonrx['devEUI']
        applicationID = jsonrx['applicationID']
        applicationName = jsonrx['applicationName']
        deviceName = jsonrx['deviceName']
        timestamp = jsonrx['timestamp']
        fCnt = jsonrx['fCnt']
        fPort = jsonrx['fPort']
        data = jsonrx['data']


        datanumbers = bytearray(base64.b64decode(data))
        recv_value = int.from_bytes(datanumbers, byteorder='little')

        Soil_Temp_Nums = datanumbers[0:4]
        Soil_Temp = int.from_bytes(Soil_Temp_Nums, byteorder='little')

        Soil_Moist1_Nums = datanumbers[4:5]
        Soil_Moist1 = int.from_bytes(Soil_Moist1_Nums, byteorder='little')

        Soil_Moist2_Nums = datanumbers[5:6]
        Soil_Moist2 = int.from_bytes(Soil_Moist2_Nums, byteorder='little')

        Soil_pH_Nums = datanumbers[6:8]
        Soil_pH = int.from_bytes(Soil_pH_Nums, byteorder='little')

        Soil_NIT_Nums = datanumbers[8:10]
        Soil_NIT = int.from_bytes(Soil_NIT_Nums, byteorder='little')

        Soil_PHOS_Nums = datanumbers[10:12]
        Soil_PHOS = int.from_bytes(Soil_PHOS_Nums, byteorder='little')

        Soil_POT_Nums = datanumbers[12:14]
        Soil_POT = int.from_bytes(Soil_POT_Nums, byteorder='little')

        LUX_Nums = datanumbers[14:18]
        LUX = int.from_bytes(LUX_Nums, byteorder='little')

        AmbT_Nums = datanumbers[18:22]
        AmbT = int.from_bytes(AmbT_Nums, byteorder='little')

        AmbH_Nums = datanumbers[22:26]
        AmbH = int.from_bytes(AmbH_Nums, byteorder='little')

        BAT_Nums = datanumbers[26:28]
        BAT = int.from_bytes(BAT_Nums, byteorder='little')

        '''
        print('Datanums: ', datanumbers)
        print('soil temp datanumbers: ', Soil_Temp_Nums)
        print('soil moist1 datanumbers: ', Soil_Moist1_Nums)
        print('soil moist2 datanumbers: ', Soil_Moist2_Nums)
        print('soil pH datanumbers: ', Soil_pH_Nums)
        print('soil NIT datanumbers: ', Soil_NIT_Nums)
        print('soil PHOS datanumbers: ', Soil_PHOS_Nums)
        print('soil POT datanumbers: ', Soil_POT_Nums)
        print('LUX datanumbers: ', LUX_Nums)
        print('Amb T datanumbers: ', AmbT_Nums)
        print('Amb H datanumbers: ', AmbH_Nums)
        print('Battery Nums: ', BAT_Nums)
        print(recv_value)
        print("Soil Temp", undo_numpad(Soil_Temp))
        print("Soil Moist1", Soil_Moist1)
        print("Soil Moist2", Soil_Moist2)
        print("Soil pH", phnpk_bat_unpad(Soil_pH))
        print("Nitrogen", phnpk_bat_unpad(Soil_NIT))
        print("Phosphorus", phnpk_bat_unpad(Soil_PHOS))
        print("Potassium", phnpk_bat_unpad(Soil_POT))
        print("LUX", lux_unpad(LUX))
        print("Ambient Temp degC", undo_numpad(AmbT))
        print("Ambient Humidity", undo_humpad(AmbH))
        print("Battery", phnpk_bat_unpad(BAT))
        '''
        # print('Number of Bytes: ', len(datanumbers))

        # Convert the timestamp to local time
        strlocaltime = datetime.fromtimestamp(timestamp)

        # Print the device EUI and the header
        print(f"\n\n\n{colours.CYAN}----------{colours.BLUE}"
              f" devEUI:[{devEUI}] rxpk info{colours.CYAN} -----------{colours.ENDC}")
        print(f"{colours.CYAN}+{colours.ENDC}\t deviceName:\t\t{deviceName}")
        print(f"{colours.CYAN}+{colours.ENDC}\t datetime:\t\t{strlocaltime}")
        print(f"{colours.CYAN}+{colours.ENDC}\t fPort:\t\t\t{fPort}")


        # Print a text separator line
        print(f"{colours.CYAN}---------------{colours.BLUE}----------------------------"
              f"{colours.CYAN}---------------{colours.ENDC}\n")
        # Print lux data numbers
        print(f"{colours.BOLD}{colours.YELLOW}✦ {colours.ENDC}"
              f"Lux data numbers: {colours.YELLOW}{colours.BOLD}"
              f"{LUX_Nums}{colours.ENDC}")
        # Print the actual Lux value
        print(f"{colours.BOLD}{colours.YELLOW}✦ {colours.ENDC}"
              f"Lux value: {colours.YELLOW}{colours.BOLD}"
              f"{lux_unpad(LUX)}{colours.ENDC}")
        # Print time value
        current_date_and_time = datetime.now()
        print(f"{colours.BOLD}{colours.YELLOW}✦ {colours.ENDC}"
              f"Time value: {colours.YELLOW}{colours.BOLD}"
              f"{str(current_date_and_time.hour)}:{str(current_date_and_time.minute)}{colours.ENDC}")
        # Print timespan value
        print(f"{colours.BOLD}{colours.YELLOW}✦ {colours.ENDC}"
              f"Timespan value: {colours.YELLOW}{colours.BOLD}"
              f"{str(current_date_and_time.hour*60+current_date_and_time.minute)}")

        # Get the path to the clients.csv file
        path_to_clients_csv = os.path.dirname(__file__)
        path_to_clients_csv = path_to_clients_csv + "/detection_system_files/clients.csv"
        # Add the device to the clients list
        with open(path_to_clients_csv, "a+") as clients:
            clients.seek(0)
            if not (f"{deviceName},{devEUI}") in clients.read():
                id = len(clients.readlines()) + 1
                clients.write(f"{id},"f"{deviceName},"f"{devEUI}\n")

        # Do anomaly detection
        anomaly_detection(lux_unpad(LUX), deviceName, devEUI)
    except Exception as e:
        print(e)
    finally:
        pass


def onprintraknodeinfo(payload):
    jsonstr = payload.decode()
    try:
        jsonrx = json.loads(jsonstr)
        onprintnoderxinfo(jsonrx)
        deveui = jsonrx['devEUI']
        appid = jsonrx['applicationID']
        appname = jsonrx['applicationName']
        # Industrial gateway default tx topic
        tx_topic = 'application/%s/device/%s/tx' % (appname, deveui)
        str_hello = "Hello RAKwireless"
        tx_msg = '{"confirmed":true,"fPort":10,"data":"%s" }' % base64.b64encode(str_hello.encode("utf-8")).decode(
            "utf-8")
        mqttc.publish(tx_topic, tx_msg, qos=0, retain=False)
    except Exception as e:
        raise e
    finally:
        pass


def undo_numpad(formatted_num):
    if formatted_num >= 900000:
        num = float(formatted_num - 900000) / 100
        if formatted_num >= 100000:
            num = -num
        return num
    else:
        num = float(formatted_num - 100000) / 100
        return num


def phnpk_bat_unpad(pad_num):
    return (pad_num - 10000) / 100


def lux_unpad(num):
    num -= 100000000
    num /= 100
    return num


def undo_humpad(num):
    num -= 10000
    num /= 100
    return num


# program entry point
def main():

    # train and assign the svm model
    global model
    model = svm_model()[0]

    # assign the max dataframe values (will be used for data normalisation)
    global max_df_value
    max_df_value = svm_model()[1]

    # receive the message, print it and do anomaly detection
    # function calls:
    # onmessage() -> onprintraknodeinfo()
    # -> onprintnoderxinfo() -> anomaly_detection()
    # if data is anomalous send_email()
    mqttc.on_message = onmessage

    # If there was username and password:
    # mqttc.usernamepwset(mqttusername, password=mqttpassword)

    # Connect to mqtt broker, the heartbeat time is 60s
    mqttc.connect(mqttip, mqttport, 60)
    mqttc.subscribe(mqttrxtopic, 0)
    mqttc.loop_forever()


if __name__ == "__main__":
    main()
