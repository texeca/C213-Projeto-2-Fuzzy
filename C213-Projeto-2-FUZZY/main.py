import sys
import numpy as np
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout,
                             QHBoxLayout, QLabel, QGridLayout, QFrame)
from PyQt5.QtCore import QTimer, Qt
from controle_fuzzy import criar_controlador_fuzzy
from mqtt_cliente import ClienteMQTT, TOPICO_COMANDO
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class ElevadorGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Painel Elevador COMPAQ Slim")
        self.setFixedSize(400, 750)
        self.setStyleSheet("font-family: Arial; font-size: 12pt;")

        from elevador import Elevador

        # Estado inicial
        self.posicao_atual = 4.0
        self.setpoint = 4.0
        self.k2 = 0.251287
        self.elevador = Elevador(posicao_inicial=self.posicao_atual, k2=self.k2)
        self.tempo = 0
        self.x_data = []
        self.y_data = []
        self.velocidade_data = []
        self.erro_data = []
        self.tempo_total = []
        self.posicoes = []
        self.erro_anterior = 0
        self.ultimo_andar = 'T'
        self.startup_duration = 2.0
        self.startup_max_power = 31.5

        # Mapa de alturas dos andares
        self.floor_positions = {
            'SS': 0.0, 'T': 4.0, '1': 8.0, '2': 11.0, '3': 14.0,
            '4': 17.0, '5': 20.0, '6': 23.0, '7': 26.0, '8': 29.0, 'C': 32.0
        }

        # Controlador Fuzzy
        self.controlador = criar_controlador_fuzzy()
        self.simulation = self.controlador  # compatível com os métodos externos

        # Cliente MQTT
        self.mqtt = ClienteMQTT(self.receber_comando_mqtt)
        self.mqtt.conectar()

        # Layout principal
        layout = QVBoxLayout(self)
        self.figure = Figure(figsize=(5, 2))
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.line, = self.ax.plot([], [], lw=2, color="red")
        layout.addWidget(self.canvas)

        painel = QFrame()
        painel.setStyleSheet("background-color: white; border: 1px solid gray;")
        painel_layout = QVBoxLayout(painel)

        cabecalho = QLabel("<b style='color: white;'>VILLARTA</b><br><span style='color:white;'>elevadores</span>")
        cabecalho.setStyleSheet("background-color: #2a5da0; font-size: 14pt;")
        cabecalho.setAlignment(Qt.AlignCenter)
        cabecalho.setFixedHeight(60)
        painel_layout.addWidget(cabecalho)

        info = QLabel("CAPACIDADE 975kg\n13 PASSAGEIROS")
        info.setAlignment(Qt.AlignCenter)
        painel_layout.addWidget(info)

        botoes_topo = QHBoxLayout()
        for icone in ['<|>', '🔔', '>|<']:
            b = QPushButton(icone)
            b.setEnabled(False)
            botoes_topo.addWidget(b)
        painel_layout.addLayout(botoes_topo)

        botoes_layout = QGridLayout()
        self.botoes = {}
        self.andares = [['7', '8', 'C'], ['4', '5', '6'], ['1', '2', '3'], ['SS', 'T', '']]
        for i, linha in enumerate(self.andares):
            for j, andar in enumerate(linha):
                if andar == '': continue
                botao = QPushButton(andar)
                botao.setFixedSize(60, 60)
                botao.setStyleSheet("background-color: lightgray; border-radius: 30px;")
                botao.clicked.connect(self.handle_botao)
                botoes_layout.addWidget(botao, i, j)
                self.botoes[andar] = botao

        painel_layout.addLayout(botoes_layout)

        self.label_direcao = QLabel("Direção: -")
        self.label_direcao.setAlignment(Qt.AlignCenter)
        painel_layout.addWidget(self.label_direcao)

        self.label_posicao = QLabel("Posição atual: 4.0 m")
        self.label_posicao.setAlignment(Qt.AlignCenter)
        painel_layout.addWidget(self.label_posicao)

        self.label_status = QLabel("Status: Parado")
        self.label_status.setAlignment(Qt.AlignCenter)
        painel_layout.addWidget(self.label_status)

        telefone = QLabel("☎ (35) 62133 – 6115")
        telefone.setAlignment(Qt.AlignCenter)
        telefone.setStyleSheet("font-size: 10pt; color: gray;")
        painel_layout.addWidget(telefone)

        layout.addWidget(painel)

        self.timer = QTimer()
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.atualizar_simulacao)

    def get_floor_position(self, floor_name: str) -> float:
        if floor_name in self.floor_positions:
            return self.floor_positions[floor_name]
        elif floor_name.startswith('andar_'):
            return self.floor_positions[floor_name]
        else:
            raise ValueError(f"Andar desconhecido: {floor_name}")

    def compute_startup_power(self, elapsed_time: float, direction: int) -> float:
        if elapsed_time >= self.startup_duration:
            return None
        return (self.startup_max_power / self.startup_duration) * elapsed_time

    def compute_control(self, current_position: float, target_position: float, previous_error: float):
        current_error = target_position - current_position
        error_magnitude = abs(current_error)
        delta_error = error_magnitude - abs(previous_error)

        error_input = max(0, min(36, error_magnitude))
        delta_input = max(-10, min(10, delta_error))

        try:
            self.simulation.input['erro'] = error_input
            self.simulation.input['delta_erro'] = delta_input
            self.simulation.compute()
            motor_power = self.simulation.output['potencia_motor']
        except Exception as e:
            print(f"[Fuzzy erro] {e}")
            motor_power = min(85.0, max(5.0, error_magnitude * 2.5))
            print(f"[Fallback] potência = {motor_power:.1f}%")

        return motor_power, current_error

    def handle_botao(self):
        andar_str = self.sender().text()
        self.set_setpoint_andar(andar_str)

    def set_setpoint_andar(self, andar_str):
        self.setpoint = self.get_floor_position(andar_str)

        for botao in self.botoes.values():
            botao.setStyleSheet("background-color: lightgray; border-radius: 30px;")

        self.botoes[andar_str].setStyleSheet("background-color: red; color: white; border-radius: 30px;")
        self.label_status.setText("Status: Em movimento")
        self.label_direcao.setText("Direção: ↑" if self.setpoint > self.posicao_atual else "Direção: ↓")
        self.tempo = 0
        self.tempo_total = []
        self.posicoes = []
        self.timer.start()

    def atualizar_simulacao(self):
        motor_power, erro_atual = self.compute_control(self.posicao_atual, self.setpoint, self.erro_anterior)
        self.elevador.atualizar_posicao(motor_power, erro_atual)

        if self.tempo < self.startup_duration:
            startup = self.compute_startup_power(self.tempo, 1 if erro_atual > 0 else -1)
            if startup is not None:
                motor_power = startup

        delta_posicao = (motor_power / 100.0) * self.k2
        self.posicao_atual += np.sign(erro_atual) * delta_posicao


        self.tempo += 0.2
        self.tempo_total.append(self.tempo)
        self.x_data.append(self.tempo)
        self.y_data.append(self.posicao_atual)
        self.ax.clear()
        self.ax.plot(self.x_data, self.y_data, label='Movimento')
        self.ax.set_title('Posição do Elevador (em tempo real)')
        self.ax.set_xlabel('Tempo (s)')
        self.ax.set_ylabel('Posição (m)')
        self.ax.grid(True)
        self.x_data = []
        self.y_data = []
        self.x_data = []
        self.y_data = []
        self.line.set_data(self.x_data, self.y_data)
        self.canvas.draw()
        print(f'[INFO] Tempo: {self.tempo:.1f}s | Posição: {self.posicao_atual:.2f} m | Erro: {erro_atual:.2f}')
        self.posicoes.append(self.posicao_atual)
        self.label_posicao.setText(f"Posição atual: {self.posicao_atual:.2f} m")
        self.mqtt.publicar_status(f"{self.posicao_atual:.2f} m")

        # Determinar andar atual com base na posição mais próxima
        diferencas = {andar: abs(self.posicao_atual - altura) for andar, altura in self.floor_positions.items()}
        andar_atual = min(diferencas, key=diferencas.get)

        if andar_atual != self.ultimo_andar:
            for botao in self.botoes.values():
                if 'background-color: red' not in botao.styleSheet():
                    botao.setStyleSheet("background-color: lightgray; border-radius: 30px;")
            self.botoes[andar_atual].setStyleSheet("background-color: blue; color: white; border-radius: 30px;")
            self.ultimo_andar = andar_atual

        if abs(erro_atual) < 0.05:
            self.label_status.setText("Status: Parado")
            self.label_direcao.setText("Direção: -")
            self.timer.stop()

        self.erro_anterior = erro_atual

    def receber_comando_mqtt(self, client, userdata, msg):
        comando = msg.payload.decode()
        print(f"Comando MQTT recebido: {comando}")
        if comando in self.floor_positions:
            self.set_setpoint_andar(comando)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = ElevadorGUI()
    gui.show()
    sys.exit(app.exec_())