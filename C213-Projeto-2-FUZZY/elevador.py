class Elevador:
    def __init__(self, posicao_inicial=4.0, k2=0.251287):
        self.posicao_atual = posicao_inicial
        self.k2 = k2

    def atualizar_posicao(self, potencia_motor, erro):
        direcao = 1 if erro > 0 else -1
        delta = direcao * (potencia_motor / 100.0) * self.k2
        self.posicao_atual += delta
        print(f"[MOVIMENTO] Erro: {erro:.2f} | ΔPos: {delta:.4f} | Posição atual: {self.posicao_atual:.2f} m")
        print(f"[POTÊNCIA] Potência atual do motor: {potencia_motor:.2f}%")
        return self.posicao_atual

    def resetar(self, nova_posicao):
        self.posicao_atual = nova_posicao
