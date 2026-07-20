"""
Contador de Producao Nao-Intrusivo
===================================
Firmware MicroPython para ESP32 simulado no Wokwi.

Cenario: LIGHT - Deteccao de pecas em esteira por sensor optico (LDR)

Autor: Ricardo PorfÃ­rio
"""

from machine import Pin, ADC
import time

# Pinos de hardware
PINO_LDR = 34

# Limiares de luminosidade
LIMIAR_BLOQUEIO = 1000
LIMIAR_LIVRE = 2000

# Intervalo do loop
INTERVALO_LOOP_MS = 50

# Configura o ADC para leitura do LDR
adc_ldr = ADC(Pin(PINO_LDR))
adc_ldr.atten(ADC.ATTN_11DB)
adc_ldr.width(ADC.WIDTH_12BIT)

# Variaveis de estado
contador_pecas = 0
sensor_bloqueado = False


def ler_luminosidade():
    """Le o valor bruto do ADC conectado ao LDR."""
    return adc_ldr.read()


def verificar_deteccao_peca(valor_adc):
    global sensor_bloqueado, contador_pecas

    if not sensor_bloqueado:
        if valor_adc < LIMIAR_BLOQUEIO:
            sensor_bloqueado = True
    else:
        if valor_adc > LIMIAR_LIVRE:
            sensor_bloqueado = False
            contador_pecas += 1
            print("Peca detectada! Total: {}".format(contador_pecas))


# Mensagem de inicializacao
print("Contador de Producao Inicializado")

while True:
    valor_ldr = ler_luminosidade()
    verificar_deteccao_peca(valor_ldr)
    time.sleep_ms(INTERVALO_LOOP_MS)
