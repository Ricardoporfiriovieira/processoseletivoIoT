"""
Contador de Producao Nao-Intrusivo
===================================
Firmware MicroPython para ESP32 simulado no Wokwi.

Cenario: LIGHT - Deteccao de pecas em esteira por sensor optico (LDR),
monitoramento de micro-paradas e reset manual de turno.

Autor: Ricardo PorfÃ­rio
"""

from machine import Pin, ADC
import time

# Pinos de hardware
PINO_LDR = 34

# Limiares de luminosidade
LIMIAR_BLOQUEIO = 1000
LIMIAR_LIVRE = 2000

# Temporizacao
TEMPO_MICRO_PARADA_MS = 5000

# Intervalo do loop
INTERVALO_LOOP_MS = 50

# Configura o ADC para leitura do LDR
adc_ldr = ADC(Pin(PINO_LDR))
adc_ldr.atten(ADC.ATTN_11DB)
adc_ldr.width(ADC.WIDTH_12BIT)

# Variaveis de estado
contador_pecas = 0
sensor_bloqueado = False
tempo_inicio_bloqueio = 0
micro_parada_alertada = False


def ler_luminosidade():
    """Le o valor bruto do ADC conectado ao LDR."""
    return adc_ldr.read()


def verificar_deteccao_peca(valor_adc):
    global sensor_bloqueado, contador_pecas
    global tempo_inicio_bloqueio, micro_parada_alertada

    agora = time.ticks_ms()

    if not sensor_bloqueado:
        if valor_adc < LIMIAR_BLOQUEIO:
            sensor_bloqueado = True
            tempo_inicio_bloqueio = agora
            micro_parada_alertada = False
    else:
        if valor_adc > LIMIAR_LIVRE:
            sensor_bloqueado = False
            contador_pecas += 1
            print("Peca detectada! Total: {}".format(contador_pecas))


def verificar_micro_parada():
    global micro_parada_alertada

    if sensor_bloqueado and not micro_parada_alertada:
        agora = time.ticks_ms()
        tempo_bloqueado = time.ticks_diff(agora, tempo_inicio_bloqueio)

        if tempo_bloqueado >= TEMPO_MICRO_PARADA_MS:
            print("Alerta: Micro-parada detectada!")
            micro_parada_alertada = True


# Mensagem de inicializacao
print("Contador de Producao Inicializado")

while True:
    valor_ldr = ler_luminosidade()
    verificar_deteccao_peca(valor_ldr)
    verificar_micro_parada()
    time.sleep_ms(INTERVALO_LOOP_MS)
