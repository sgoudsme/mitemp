import paho.mqtt.client as mqtt


class MqttHandler:
    """Handling all communication via MQTT. Makes an instance of the mqtt client. Gets all the messages and redirects
    it to the messageHandler of the objectHandler instance. Sends all messages to the broker.

    """
    def __init__(self, host, subList, usr, passw, funct):
        """Constructor of the MqttHandler

        :param host: adress of the broker
        :param subList: list of all topics to subscribe
        :param funct: function it runs when it got a message

        """

        self.connected = False
        self.host = host
        self.client = mqtt.Client()

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.username_pw_set(usr, passw)

        self.client.connect_async(host, 1883, 60)

        self.client.loop_start()
        self._funct = funct
        self._subList = subList

    # The callback for when the client receives a message. nuo= not used object (no idea what it is for)
    def on_connect(self, client, userdata, flags, rc):
        """When connected to the broker, subscribe to the provided topics.

        :param client: the client instance for this callback (not used)
        :param userdata: the private user data as set in Client() or userdata_set() (not used)
        :param flags: response flags sent by the broker (not used)
        :param rc: result code from the client. 0 when connected and everything ok

        """
        print("Mqtt connected with result code "+str(rc))
        self.connected = True

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        for value in self._subList:
            self.client.subscribe(value)

    def subscribe(self, tpc):
        """Add subscription to list of MQTT

        :param tpc: topic to subscribe to

        """

        self.client.subscribe(tpc)
        self._subList.append(tpc)

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        """When a message is received, this function is called. it is like a callback-function.

        :param client: the client instance for this callback
        :param userdata: the private user data as set in Client() or userdata_set()
        :param msg: got all the information of the message (broker and payload)

        """
        pyld = msg.payload.decode('utf-8')
        print("Received topic: " + msg.topic + ", msg: " + pyld)
        self._funct(msg.topic, pyld)

    def publish(self, topic, msg, retain=False):
        """Function to call when to publish to the broker.

        :param topic: subject of the messagee
        :param msg: content of the message

        """
        try:
            self.client.publish(topic, msg, retain=retain)
        except Exception as ex:
            print("Cannot publish message: " + str(ex))


'''
    def __del__(self):
        self.client.loop_stop()
        self.client.disconnect()
        del self.client
        print self.host, 'deleted'
'''
