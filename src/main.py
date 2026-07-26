"""
Contador de Producao Nao-Intrusivo
===================================
Firmware MicroPython para ESP32 simulado no Wokwi.

Cenario: LIGHT - Deteccao de pecas em esteira por sensor optico (LDR),
monitoramento de micro-paradas e reset manual de turno.

Componentes:
  - ldr1: Fotorresistor (LDR) no pino ADC GPIO 34
  - btn1: Botao de reset de turno no GPIO 23 (pull-up interno)

Autor: Ricardo Porfirio
"""

from machine import Pin, ADC
import time



PINO_LDR = 34         
PINO_BOTAO = 23        

LIMIAR_BLOQUEIO = 2000   
LIMIAR_LIVRE = 1000     

TEMPO_MICRO_PARADA_MS = 5000   
TEMPO_DEBOUNCE_MS = 50        

INTERVALO_LOOP_MS = 50       


adc_ldr = ADC(Pin(PINO_LDR))
adc_ldr.atten(ADC.ATTN_11DB)    
adc_ldr.width(ADC.WIDTH_12BIT) 

botao_reset = Pin(PINO_BOTAO, Pin.IN, Pin.PULL_UP)

contador_pecas = 0


sensor_bloqueado = False

# Controle de micro-parada
tempo_inicio_bloqueio = 0   
micro_parada_alertada = False 

# Controle de debounce do botao
ultimo_estado_botao = 1        
tempo_ultimo_debounce = 0
botao_estavel = 1             
botao_anterior_estavel = 1    


def ler_luminosidade():
    """Le o valor bruto do ADC conectado ao LDR."""
    return adc_ldr.read()


def verificar_deteccao_peca(valor_adc):
    """
    Implementa a logica de deteccao de pecas por transicao de luz.
    """
    global sensor_bloqueado, contador_pecas
    global tempo_inicio_bloqueio, micro_parada_alertada

    agora = time.ticks_ms()

    if not sensor_bloqueado:
        # Estado atual: LIVRE
        if valor_adc > LIMIAR_BLOQUEIO:
            sensor_bloqueado = True
            tempo_inicio_bloqueio = agora
            micro_parada_alertada = False
    else:
        # Estado atual: BLOQUEADO
        if valor_adc < LIMIAR_LIVRE:
            sensor_bloqueado = False
            contador_pecas += 1
            print("Peca detectada! Total: {}".format(contador_pecas))


def verificar_micro_parada():
    """
    Verifica se o sensor permanece bloqueado
    """
    global micro_parada_alertada

    if sensor_bloqueado and not micro_parada_alertada:
        agora = time.ticks_ms()
        tempo_bloqueado = time.ticks_diff(agora, tempo_inicio_bloqueio)

        if tempo_bloqueado >= TEMPO_MICRO_PARADA_MS:
            print("Alerta: Micro-parada detectada!")
            micro_parada_alertada = True


def verificar_botao_reset():
    """
    Verifica o estado do botao de reset com tratamento de debounce.
    """
    global ultimo_estado_botao, tempo_ultimo_debounce
    global botao_estavel, botao_anterior_estavel
    global contador_pecas, sensor_bloqueado
    global tempo_inicio_bloqueio, micro_parada_alertada

    leitura_atual = botao_reset.value()
    agora = time.ticks_ms()

    if leitura_atual != ultimo_estado_botao:
        tempo_ultimo_debounce = agora
    ultimo_estado_botao = leitura_atual

    if time.ticks_diff(agora, tempo_ultimo_debounce) >= TEMPO_DEBOUNCE_MS:
        if leitura_atual != botao_estavel:
            botao_anterior_estavel = botao_estavel
            botao_estavel = leitura_atual

            if botao_anterior_estavel == 0 and botao_estavel == 1:
                contador_pecas = 0
                sensor_bloqueado = False
                tempo_inicio_bloqueio = 0
                micro_parada_alertada = False
                print("Turno resetado com sucesso. Contadores zerados.")


print("Contador de Producao Inicializado")

while True:
    valor_ldr = ler_luminosidade()

    verificar_deteccao_peca(valor_ldr)

    verificar_micro_parada()

    verificar_botao_reset()

    time.sleep_ms(INTERVALO_LOOP_MS)
