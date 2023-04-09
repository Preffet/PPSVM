import json
import base64
import paho.mqtt.client as mqtt
from datetime import datetime

# Type the IP of your server
mqttip = '192.168.230.1'
mqttport = 1883

# Type your username and password. If the private MQTT server does not require username and password, commend the lines
# mqtt_username = 'username'
# mqtt_password = 'password'

# Replace the "id" with the id of your application and "eui" with your device eui
# mqttrxtopic = 'application/SensorBox/device/a8610a3439307f10/rx'

mqttrxtopic = 'application/SensorBox/device/a8610a3530408b09/rx'


# Convert string to hexadecimal
def strtohex(s):
    return r"\x" + r'\x'.join([hex(ord(c)).replace('0x', '') for c in s])


# #Once subscribed to the message, call back this method
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

        # datanumbers = base64.b64decode(data)

        datanumbers = bytearray(base64.b64decode(data))
        print("DATANUMBERS: ", datanumbers)
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

        print('Number of Bytes: ', len(datanumbers))

        # Convert the timestamp to local time
        strlocaltime = datetime.fromtimestamp(timestamp)
        print('---------------- devEUI:[%s] rxpk info -------------------' % devEUI)
        print('+\t applicationName:\t%s' % applicationName)
        print('+\t applicationID:\t\t%s' % applicationID)
        print('+\t deviceName:\t\t%s' % deviceName)
        print('+\t datetime:\t\t%s' % strlocaltime)
        print('+\t fCnt:\t\t\t%d' % fCnt)
        print('+\t fPort:\t\t\t%d' % fPort)
        print('+\t data:\t\t\t%s' % data)
        print('+\t data:\t\t\t%s' % datanumbers)
        # print('+\t data:\t\t\t%s' % mydata)
        # print('Data Length: ', len(mydata))

        # print('+\t datahex:\t\t%s' % datahex)
        print('----------------------------------------------------------')
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
        print('Send \'Hello RAKwireless\' to node %s' % deveui)

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


mqttc = mqtt.Client()
mqttc.on_message = onmessage

# If there is no username and password, please comment the following line:
# mqttc.usernamepwset(mqttusername, password=mqttpassword)

# Connect to mqtt broker, the heartbeat time is 60s
mqttc.connect(mqttip, mqttport, 60)
mqttc.subscribe(mqttrxtopic, 0)

mqttc.loop_forever()