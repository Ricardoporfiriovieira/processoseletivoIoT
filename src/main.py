"""
Contador de Producao Nao-Intrusivo
===================================
Firmware MicroPython para ESP32 simulado no Wokwi.

Cenario: LIGHT - Deteccao de pecas em esteira por sensor optico (LDR),
monitoramento de micro-paradas e reset manual de turno.

Componentes:
  - ldr1: Fotorresistor (LDR) no pino ADC GPIO 34
  - btn1: Botao de reset de turno no GPIO 23 (pull-up interno)

Autor: Ricardo PorfÃ­rio
"""

from machine import Pin, ADC
import time

# =============================================================================
# CONSTANTES DE CONFIGURACAO
# =============================================================================

# Pinos de hardware
PINO_LDR = 34          # Pino ADC para o sensor LDR
PINO_BOTAO = 23        # Pino digital para o botao de reset

# Limiares de luminosidade (em valor ADC bruto 0-4095)
# No Wokwi, o LDR retorna valores ADC proporcionais ao lux:
#   - lux alto (800) -> ADC alto (ambiente iluminado / esteira livre)
#   - lux baixo (50)  -> ADC baixo (peca bloqueando o sensor)
LIMIAR_BLOQUEIO = 1000    # Abaixo deste valor = peca presente (lux baixo)
LIMIAR_LIVRE = 2000       # Acima deste valor = esteira livre (lux alto)

# Temporizacao
TEMPO_MICRO_PARADA_MS = 5000   # Tempo para detectar micro-parada (5 segundos)
TEMPO_DEBOUNCE_MS = 50         # Tempo de debounce do botao (50ms)

# Intervalo do loop principal
INTERVALO_LOOP_MS = 50         # Polling a cada 50ms (nao-bloqueante)

# =============================================================================
# CONFIGURACAO DE HARDWARE
# =============================================================================

# Configura o ADC para leitura do LDR
adc_ldr = ADC(Pin(PINO_LDR))
adc_ldr.atten(ADC.ATTN_11DB)    # Faixa de leitura 0-3.3V
adc_ldr.width(ADC.WIDTH_12BIT)  # Resolucao de 12 bits (0-4095)

# Configura o botao com pull-up interno
botao_reset = Pin(PINO_BOTAO, Pin.IN, Pin.PULL_UP)

# =============================================================================
# VARIAVEIS DE ESTADO DO SISTEMA
# =============================================================================

# Contagem de pecas
contador_pecas = 0

# Estado do sensor de luz
#   False = esteira livre (lux alto)
#   True  = peca presente (lux baixo / bloqueado)
sensor_bloqueado = False

# Controle de micro-parada
tempo_inicio_bloqueio = 0    # Timestamp do inicio do bloqueio
micro_parada_alertada = False  # Evita alertas repetidos para o mesmo evento

# Controle de debounce do botao
ultimo_estado_botao = 1        # Pull-up: 1 = solto, 0 = pressionado
tempo_ultimo_debounce = 0
botao_estavel = 1              # Estado estavel apos debounce
botao_anterior_estavel = 1     # Estado estavel do ciclo anterior

# =============================================================================
# FUNCOES DO SISTEMA
# =============================================================================


def ler_luminosidade():
    """Le o valor bruto do ADC conectado ao LDR."""
    return adc_ldr.read()


def verificar_deteccao_peca(valor_adc):
    """
    Implementa a logica de deteccao de pecas por transicao de luz.

    A contagem so e incrementada na BORDA DE SUBIDA: quando a luz retorna
    ao estado normal apos ter sido bloqueada, garantindo que a peca passou
    completamente pelo sensor.

    Tambem monitora o tempo de bloqueio continuo para detectar micro-paradas.
    """
    global sensor_bloqueado, contador_pecas
    global tempo_inicio_bloqueio, micro_parada_alertada

    agora = time.ticks_ms()

    if not sensor_bloqueado:
        # Estado atual: LIVRE -> Verifica se houve transicao para BLOQUEADO
        if valor_adc < LIMIAR_BLOQUEIO:
            sensor_bloqueado = True
            tempo_inicio_bloqueio = agora
            micro_parada_alertada = False
    else:
        # Estado atual: BLOQUEADO
        if valor_adc > LIMIAR_LIVRE:
            # Transicao de BLOQUEADO -> LIVRE (borda de subida)
            # A peca passou completamente pelo sensor
            sensor_bloqueado = False
            contador_pecas += 1
            print("Peca detectada! Total: {}".format(contador_pecas))


def verificar_micro_parada():
    """
    Verifica se o sensor permanece bloqueado por tempo excessivo,
    indicando uma micro-parada na esteira (gargalo ou travamento).

    Usa temporizador nao-bloqueante com time.ticks_diff().
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

    Detecta a borda de descida (transicao de solto para pressionado)
    para acionar o reset de turno. Usa debounce por software para
    evitar falsos gatilhos causados por bounce mecanico.
    """
    global ultimo_estado_botao, tempo_ultimo_debounce
    global botao_estavel, botao_anterior_estavel
    global contador_pecas, sensor_bloqueado
    global tempo_inicio_bloqueio, micro_parada_alertada

    leitura_atual = botao_reset.value()
    agora = time.ticks_ms()

    # Detecta mudanca na leitura bruta e reinicia o timer de debounce
    if leitura_atual != ultimo_estado_botao:
        tempo_ultimo_debounce = agora
    ultimo_estado_botao = leitura_atual

    # Verifica se o tempo de debounce passou
    if time.ticks_diff(agora, tempo_ultimo_debounce) >= TEMPO_DEBOUNCE_MS:
        # Atualiza o estado estavel
        if leitura_atual != botao_estavel:
            botao_anterior_estavel = botao_estavel
            botao_estavel = leitura_atual

            # Detecta borda de descida: solto (1) -> pressionado (0)
            if botao_anterior_estavel == 1 and botao_estavel == 0:
                # Reset de turno
                contador_pecas = 0
                sensor_bloqueado = False
                tempo_inicio_bloqueio = 0
                micro_parada_alertada = False
                print("Turno resetado com sucesso. Contadores zerados.")


# =============================================================================
# LOOP PRINCIPAL (ARQUITETURA NAO-BLOQUEANTE)
# =============================================================================

# Mensagem de inicializacao (obrigatoria para o CI)
print("Contador de Producao Inicializado")

while True:
    # Leitura do sensor de luminosidade
    valor_ldr = ler_luminosidade()

    # Logica de deteccao de pecas (transicoes de luz)
    verificar_deteccao_peca(valor_ldr)

    # Logica de deteccao de micro-paradas (temporizador nao-bloqueante)
    verificar_micro_parada()

    # Logica de reset de turno (botao com debounce)
    verificar_botao_reset()

    # Pausa nao-bloqueante para evitar saturacao do loop
    time.sleep_ms(INTERVALO_LOOP_MS)
