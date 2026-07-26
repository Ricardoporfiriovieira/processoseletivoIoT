# Relatório do Candidato

## Identificação do Candidato
- **Nome completo:** Ricardo Porfírio Vieira
- **GitHub:** Ricardoporfiriovieira
- **E-mail:** ricardoporfiriovieira@gmail.com

## Visão Geral da Solução
- **Objetivo do projeto:** Implementa um Contador de Produção Não-Intrusivo para monitoramento de esteiras transportadoras industriais, detectando a passagem de peças/caixas por meio de um sensor óptico (LDR) e mantendo um contador acumulativo.
- **Funções do sistema embarcado:** Monitora micro-paradas na esteira, emitindo um alerta de gargalo quando o sensor permanece bloqueado por mais de 5 segundos, além de contabilizar o número de peças produzidas.
- **Interação com usuário:** O operador acompanha a produção pelo terminal serial (UART) e pode pressionar o botão de reset físico a qualquer momento para encerrar o turno atual e zerar os contadores.

## Arquitetura do Sistema Embarcado
De forma geral, o programa pode ser "dividido" em quatro funções:

- **ler_luminosidade():** Lê o valor bruto do ADC conectado ao LDR.
```python
def ler_luminosidade():
    """Le o valor bruto do ADC conectado ao LDR."""
    return adc_ldr.read()
```

- **verificar_deteccao_peca(valor_adc):** Implementa a lógica de detecção de peças por transição de luz. A contagem de peças é incrementada exclusivamente na borda de subida (transição de BLOQUEADO para LIVRE), garantindo que a peça passou completamente pelo sensor.
```python
def verificar_deteccao_peca(valor_adc):
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
```

- **verificar_micro_parada():** Verifica se o sensor permanece bloqueado por um tempo maior ou igual ao limite de micro-parada e emite o alerta caso positivo. Utiliza a diferença entre o tempo atual e o início do bloqueio guardado.
```python
def verificar_micro_parada():
    global micro_parada_alertada

    if sensor_bloqueado and not micro_parada_alertada:
        agora = time.ticks_ms()
        tempo_bloqueado = time.ticks_diff(agora, tempo_inicio_bloqueio)

        if tempo_bloqueado >= TEMPO_MICRO_PARADA_MS:
            print("Alerta: Micro-parada detectada!")
            micro_parada_alertada = True
```

- **verificar_botao_reset():** Verifica o estado do botão de reset com tratamento de debounce não-bloqueante utilizando `time.ticks_ms()`. Reseta o contador e todos os estados quando uma borda de subida válida (botão solto após pressionado) é detectada.
```python
def verificar_botao_reset():
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
```

Todas essas funções são executadas dentro do loop principal, no qual também está presente `time.sleep_ms(INTERVALO_LOOP_MS)`, paralisando o programa por 50 milissegundos.

```python
while True:
    valor_ldr = ler_luminosidade()
    verificar_deteccao_peca(valor_ldr)
    verificar_micro_parada()
    verificar_botao_reset()
    time.sleep_ms(INTERVALO_LOOP_MS)
```

## Componentes Utilizados na Simulação
Liste os principais componentes definidos no diagram.json, por exemplo:

- **ESP32 DevKit C v4:** Controla toda a lógica do funcionamento do sistema.
- **Fotorresistor (LDR):** Sensor óptico utilizado para detectar a passagem de peças na esteira, com o pino conectado ao GPIO 34 (ADC).
- **Push Button:** Botão utilizado para realizar o reset manual de turno, reiniciando os contadores, conectado ao GPIO 23 (com pull-up interno).

## Decisões Técnicas Relevantes
O firmware foi estruturado de forma inteiramente não-bloqueante para garantir o monitoramento ininterrupto. Todas as temporizações utilizam `time.ticks_ms()` e `time.ticks_diff()`.
Para evitar múltiplos disparos falsos pelo botão mecânico, implementei um debounce por software via amostragem temporal: a cada iteração do loop, o estado do botão é lido. Se houver mudança, o timer de debounce é reiniciado.
Para detecção por meio do LDR, utilizei dois limiares distintos (`LIMIAR_BLOQUEIO = 2000` e `LIMIAR_LIVRE = 1000`) em vez de um único valor. Isso cria uma faixa de histerese, evitando oscilações falsas quando a leitura do sensor está próxima do limiar de transição. Além disso, a contagem de peças é feita apenas na borda de subida (retorno da luz, estado LIVRE), garantindo que a peça passou completamente.

## Resultados Obtidos
O sistema funciona conforme o esperado, detectando e contabilizando com sucesso cada peça após ela passar completamente pelo sensor. Também foi validada com sucesso a emissão do alerta de micro-parada quando a esteira fica com o feixe bloqueado por mais de 5 segundos. O reset através do botão obedece perfeitamente ao debounce configurado e foi observado que o loop não-bloqueante consegue atender adequadamente as exigências, permitindo inclusive o casamento de strings com a avaliação do CI perfeitamente, sem atrasos desnecessários.

## Comentários Adicionais (Opcional)
Uma escolha chave foi o uso do pull-up interno no pino do botão, o que simplifica o circuito montado no Wokwi pois dispensa resistores externos e facilita o diagrama.