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

# Configura o ADC para leitura do LDR
adc_ldr = ADC(Pin(PINO_LDR))
adc_ldr.atten(ADC.ATTN_11DB)
adc_ldr.width(ADC.WIDTH_12BIT)

# Mensagem de inicializacao
print("Contador de Producao Inicializado")

while True:
    valor = adc_ldr.read()
    time.sleep_ms(100)
