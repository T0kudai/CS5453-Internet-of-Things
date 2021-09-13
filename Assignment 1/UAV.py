import paho.mqtt.client as mqttClient
import time
import sys
import math
import numpy as np

all_clients = []
for i in range(1, 7):
    all_clients.append("uav" + str(i))

client_name = sys.argv[1]  # client name should be unique
file_location = "./sample_inputs/" + client_name + ".txt"
# print(file_location)
loc = open(file_location)
lines = iter(loc.readlines())


dist = []
uav_dist = {}


def str_to_list(str):
    str = str[2:-1]
    l = [float(s) for s in str.split(",")]
    return l


def min_index(a, b, c, d, e, f):
    list = [a, b, c, d, e, f]
    index = list.index(min(list))


def black_magic():
    u1 = []
    u2 = []
    u3 = []
    u4 = []
    u5 = []
    u6 = []

    if client_name == "uav1":
        u1 = dist
        u2 = str_to_list(uav_dist["uav2"])
        u3 = str_to_list(uav_dist["uav3"])
        u4 = str_to_list(uav_dist["uav4"])
        u5 = str_to_list(uav_dist["uav5"])
        u6 = str_to_list(uav_dist["uav6"])
    elif client_name == "uav2":
        u2 = dist
        u1 = str_to_list(uav_dist["uav1"])
        u3 = str_to_list(uav_dist["uav3"])
        u4 = str_to_list(uav_dist["uav4"])
        u5 = str_to_list(uav_dist["uav5"])
        u6 = str_to_list(uav_dist["uav6"])
    elif client_name == "uav3":
        u3 = dist
        u2 = str_to_list(uav_dist["uav2"])
        u1 = str_to_list(uav_dist["uav1"])
        u4 = str_to_list(uav_dist["uav4"])
        u5 = str_to_list(uav_dist["uav5"])
        u6 = str_to_list(uav_dist["uav6"])
    elif client_name == "uav4":
        u4 = dist
        u2 = str_to_list(uav_dist["uav2"])
        u3 = str_to_list(uav_dist["uav3"])
        u1 = str_to_list(uav_dist["uav1"])
        u5 = str_to_list(uav_dist["uav5"])
        u6 = str_to_list(uav_dist["uav6"])
    elif client_name == "uav5":
        u5 = dist
        u2 = str_to_list(uav_dist["uav2"])
        u3 = str_to_list(uav_dist["uav3"])
        u4 = str_to_list(uav_dist["uav4"])
        u1 = str_to_list(uav_dist["uav1"])
        u6 = str_to_list(uav_dist["uav6"])
    elif client_name == "uav6":
        u6 = dist
        u2 = str_to_list(uav_dist["uav2"])
        u3 = str_to_list(uav_dist["uav3"])
        u4 = str_to_list(uav_dist["uav4"])
        u5 = str_to_list(uav_dist["uav5"])
        u1 = str_to_list(uav_dist["uav1"])

    dist_array = [u1, u2, u3, u4, u5, u6]
    dist_array = np.array(dist_array)

    col = []
    for i in range(6):
        row_val = dist_array[i, :]
        min_index = np.argmin(row_val)
        col.append(min_index + 1)
        dist_array[:, min_index] = 10000
    # print(col)
    return col


def distances(message, uav_location):
    message = message.decode("UTF-8").strip().split(" ")
    vehicles = []
    for i in range(0, len(message) - 1, 2):
        vehicles.append([message[i], message[i + 1]])
    # print(vehicles)
    # print(uav_location)
    for loc in vehicles:
        d = math.sqrt(
            (int(loc[0]) - int(uav_location[0])) ** 2
            + (int(loc[1]) - int(uav_location[1])) ** 2
        )
        # print(d)
        dist.append(d)


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        global Connected  # Use global variable
        Connected = True  # Signal connection
    else:
        print("Connection failed")


def on_message(client, userdata, message):
    if message.topic.strip().split("/")[0] == "location":
        print("Received message from HQ")
        dist.clear()
        uav_dist.clear()
        t = next(lines).strip().split(" ")
        distances(message.payload, t)

        for cl in all_clients:
            if cl != client_name:
                print("Communication sent to other UAV")
                client.publish(str("vehicle/" + cl), client_name + ": " + str(dist))

    elif message.topic.strip().split("/")[0] == "vehicle":
        print("Communication received from other UAV")
        mes = message.payload.decode("UTF-8")
        # print(d)
        uav = mes.split(":")[0]
        d = mes.split(":")[1]
        uav_dist[uav] = d
        if len(uav_dist) == 5:
            result = black_magic()
            result = [str(x) for x in result]

            client.publish(str("final/" + client_name), " ".join(result))
            print("Sent message to HQ")


Connected = False  # global variable for the state of the connection
broker_address = "127.0.0.1"  # Broker address
port = 1883  # Broker port
user = "admin"  # Connection username
password = "hivemq"  # Connection password


client = mqttClient.Client(client_name)  # create new instance
client.on_connect = on_connect  # attach function to callback
client.on_message = on_message  # attach function to callback
client.connect(broker_address, port=port)  # connect to broker
client.loop_start()  # start the loop
client.subscribe("location/" + client_name)
client.subscribe("vehicle/" + client_name)

while Connected != True:  # Wait for connection
    time.sleep(0.1)

try:
    while True:
        time.sleep(2)
except KeyboardInterrupt:
    print("exiting")
    client.disconnect()
    client.loop_stop()
    loc.close()