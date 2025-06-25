# Elevador Fuzzy - Projeto C213

Simulação de controle fuzzy PD para elevadores residenciais usando Python, PyQt5 e MQTT.

## Requisitos

Instale as dependências com:

```bash
pip install -r requisitos.txt
```

## Execução

Para rodar a interface gráfica, use:

```bash
python main.py
```

A interface permite:

- Selecionar andares entre Térreo (T) e 8º;
- Visualizar posição, status e direção;
- Ver o gráfico de deslocamento da cabine;
- Receber comandos via MQTT (tópico `elevador/comando`);
- Publicar posição atual via MQTT (tópico `elevador/status`).

## Broker MQTT

Por padrão, usa o broker público:

```
broker.hivemq.com
```

Você pode testar comandos MQTT com ferramentas como [MQTT Explorer](http://mqtt-explorer.com/) ou `mosquitto_pub`.

## Estrutura do Projeto

```
ElevadorFuzzy/
├── main.py               # Interface principal com simulação
├── controle_fuzzy.py     # Lógica fuzzy PD
├── mqtt_cliente.py       # Cliente MQTT
├── elevador.py           # Simulação de movimentação
├── utils.py              # Funções auxiliares
├── requisitos.txt        # Dependências
```
