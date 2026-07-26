# Processo Seletivo – Intensivo Maker | IoT

## Etapa Prática – Sistemas Embarcados

---

### Identificação do Candidato

- **Nome completo:** Ricardo Porfírio Vieira
- **GitHub:** Ricardoporfiriovieira
- **E-mail:** ricardoporfiriovieira@gmail.com

---

## Visão Geral da Solução

Este projeto implementa um **Contador de Produção Não-Intrusivo** para monitoramento de esteiras transportadoras industriais, utilizando um ESP32 simulado no Wokwi com MicroPython.

**O que o sistema faz:**
- Detecta a passagem de peças/caixas em uma esteira por meio de um sensor óptico (LDR), que identifica a interrupção e o retorno do feixe de luz.
- Mantém um contador acumulativo de peças produzidas.
- Monitora micro-paradas na esteira: quando o sensor permanece bloqueado por mais de 5 segundos, emite um alerta de gargalo.
- Permite ao operador resetar manualmente o turno via botão físico, zerando todos os contadores.

**Interação do usuário:**
- O operador acompanha a produção pelo terminal serial (UART).
- Pode pressionar o botão de reset a qualquer momento para encerrar o turno atual.

---

## Arquitetura do Sistema Embarcado

### Fluxo Principal (`main.py`)

```
Inicialização
      |
      v
  Imprime "Contador de Producao Inicializado"
      |
      v
  +----------------------------------+
  |         LOOP PRINCIPAL           |
  |    (não-bloqueante, 50ms)        |
  |                                  |
  |  1. Ler valor ADC do LDR        |
  |  2. Verificar detecção de peça   |
  |  3. Verificar micro-parada      |
  |  4. Verificar botão de reset     |
  |  5. Sleep 50ms                   |
  +----------------------------------+
```

### Máquina de Estados do Sensor LDR

O sistema opera com dois estados para o sensor óptico:

| Estado         | Condição                        | Descrição                      |
| :------------- | :------------------------------ | :----------------------------- |
| **LIVRE**      | ADC < 1000 (lux alto, ~800)     | Esteira livre, sem obstrução   |
| **BLOQUEADO**  | ADC > 2000 (lux baixo, ~50)     | Peça presente sobre o sensor   |

A contagem de peças é incrementada exclusivamente na **borda de subida** (transição BLOQUEADO para LIVRE), garantindo que a peça passou completamente pelo sensor antes de registrar o evento.

### Estratégia de Temporização

Todas as temporizações utilizam `time.ticks_ms()` e `time.ticks_diff()` para garantir uma **arquitetura totalmente não-bloqueante**, conforme requisito do CI:

- **Micro-parada:** Temporizador iniciado quando o sensor entra em estado BLOQUEADO. Se `ticks_diff >= 5000ms`, emite o alerta.
- **Debounce do botão:** Filtragem por software com janela de 50ms para evitar falsos gatilhos mecânicos.

---

## Componentes Utilizados na Simulação

| Componente                    | ID no Wokwi | Pino ESP32 | Função                                         |
| :---------------------------- | :---------- | :--------- | :--------------------------------------------- |
| ESP32 DevKit C v4             | `esp`       | —          | Microcontrolador principal                     |
| Fotorresistor (LDR)           | `ldr1`      | GPIO 34    | Sensor óptico de detecção de peças             |
| Botão Push-button             | `btn1`      | GPIO 23    | Reset manual de turno (pull-up interno)        |
| Monitor Serial                | —           | TX/RX      | Saída de logs e telemetria via UART            |

### Conexões Elétricas

- **LDR para ESP32:** VCC para 3V3, GND para GND, saída analógica (AO) para GPIO 34.
- **Botão para ESP32:** Terminal 1 para GND, Terminal 2 para GPIO 23 (com pull-up interno habilitado no firmware).

---

## Decisões Técnicas Relevantes

### Organização do Código

O firmware foi estruturado com separação clara de responsabilidades:

- **Constantes de configuração** agrupadas no topo do arquivo para fácil parametrização (`LIMIAR_BLOQUEIO`, `LIMIAR_LIVRE`, `TEMPO_MICRO_PARADA_MS`, etc.).
- **Funções dedicadas** para cada subsistema:
  - `ler_luminosidade()` — abstrai a leitura do ADC.
  - `verificar_deteccao_peca()` — lógica de transições de luz.
  - `verificar_micro_parada()` — temporizador de gargalo.
  - `verificar_botao_reset()` — debounce e reset de turno.

### Debounce por Software

Implementei debounce por amostragem temporal: a cada iteração do loop, o estado bruto do botão é lido. Se houver mudança, o timer de debounce é reiniciado. O estado só é aceito como estável após 50ms sem variação, prevenindo múltiplos disparos por bounce mecânico.

### Detecção por Borda de Subida

A contagem de peças é feita na **borda de subida** (retorno da luz) e não na borda de descida (bloqueio). Isso garante que a peça passou completamente pelo sensor antes de ser contabilizada, evitando contagens duplicadas ou prematuras.

### Histerese nos Limiares

Utilizei dois limiares distintos (`LIMIAR_BLOQUEIO = 2000` e `LIMIAR_LIVRE = 1000`) ao invés de um único valor, criando uma faixa de histerese que evita oscilações falsas quando a leitura do sensor está próxima do limiar de transição.

---

## Resultados Obtidos

### Requisitos Atendidos

| Requisito                              | Status |
| :------------------------------------- | :----: |
| Mensagem de inicialização exata        |   OK   |
| Detecção e contagem de peças (borda)   |   OK   |
| Mensagem "Peca detectada! Total: X"    |   OK   |
| Detecção de micro-parada (> 5s)        |   OK   |
| Mensagem "Alerta: Micro-parada..."     |   OK   |
| Reset de turno via botão com debounce  |   OK   |
| Mensagem "Turno resetado..."           |   OK   |
| Arquitetura não-bloqueante             |   OK   |
| Casamento exato de strings para CI     |   OK   |

### Mensagens Seriais (casamento exato com o CI)

```
Contador de Producao Inicializado
Peca detectada! Total: 1
Alerta: Micro-parada detectada!
Turno resetado com sucesso. Contadores zerados.
```

---

## Comentários Adicionais

### Principais Decisões

- O intervalo do loop principal foi definido em 50ms para equilibrar responsividade do sensor com consumo de processamento.
- A utilização de `time.ticks_ms()` em vez de `time.sleep()` garante que nenhuma funcionalidade é bloqueada enquanto aguarda temporizadores.
- O uso de pull-up interno no botão simplifica o circuito, dispensando resistores externos.