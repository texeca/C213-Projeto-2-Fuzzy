import paho.mqtt.client as mqtt

BROKER = 'broker.hivemq.com'
PORT = 1883
TOPICO_COMANDO = "elevador/comando"
TOPICO_STATUS = "elevador/status"

class ClienteMQTT:
    def __init__(self, on_message_callback):
        self.cliente = mqtt.Client()
        self.cliente.on_connect = self.on_connect
        self.cliente.on_message = on_message_callback

    def conectar(self):
        self.cliente.connect(BROKER, PORT, 60)
        self.cliente.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        print("Conectado ao broker MQTT com código:", rc)
        client.subscribe(TOPICO_COMANDO)

    def publicar_status(self, mensagem):
        self.cliente.publish(TOPICO_STATUS, mensagem)

    def desconectar(self):
        self.cliente.loop_stop()
        self.cliente.disconnect()
