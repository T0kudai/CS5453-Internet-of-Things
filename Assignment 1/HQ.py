import paho.mqtt.client as mqttClient
import time

all_clients = []
for i in range(1, 7):
    all_clients.append("uav" + str(i))

client_name = "HQ"

loc = open("./sample_inputs/vehicle_location.txt")
lines = loc.readlines()

output = open("output.txt", "w")


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        global Connected  # Use global variable
        Connected = True  # Signal connection
    else:
        print("Connection failed Return Code : ", rc)


def on_message(client, userdata, message):
    # print(message.topic)
    # print(message.payload)
    if message.topic == "final/uav1":
        print("Received communication from UAV")
        text = message.payload.decode("utf-8")
        # print(text)
        output.write(text + "\n")


Connected = False  # global variable for the state of the connection

broker_address = "127.0.0.1"  # Broker address
port = 1883  # Broker port

client = mqttClient.Client(client_name)  # create new instance
client.on_connect = on_connect  # attach function to callback
client.on_message = on_message  # attach function to callback
client.connect(broker_address, port=port)  # connect to broker
client.loop_start()  # start the loop


for cl in all_clients:
    client.subscribe("final/" + cl)
while Connected != True:  # Wait for connection
    time.sleep(0.1)

try:
    for l in lines:
        for c in all_clients:
            print("Sent message to UAV")
            client.publish(str("location/" + c), l)
        time.sleep(10)
    output.close()
    loc.close()
except KeyboardInterrupt:
    print("exiting")
    client.disconnect()
    client.loop_stop()
    output.close()
    loc.close()
