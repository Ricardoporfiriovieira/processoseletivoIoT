# Processo Seletivo Ã¢â‚¬â€œ Intensivo Maker | IoT

## Etapa PrÃƒÂ¡tica Ã¢â‚¬â€œ Sistemas Embarcados

---

### IdentificaÃƒÂ§ÃƒÂ£o do Candidato

- **Nome completo:** Ricardo PorfÃƒÂ­rio
- **GitHub:** Ricardo PorfÃƒÂ­rio
- **E-mail:** ricardoporfiriovieira@gmail.com

---

## VisÃƒÂ£o Geral da SoluÃƒÂ§ÃƒÂ£o

Este projeto implementa um **Contador de ProduÃƒÂ§ÃƒÂ£o NÃƒÂ£o-Intrusivo** para monitoramento de esteiras transportadoras industriais, utilizando um ESP32 simulado no Wokwi com MicroPython.

**O que o sistema faz:**
- Detecta a passagem de peÃƒÂ§as/caixas em uma esteira por meio de um sensor ÃƒÂ³ptico (LDR), que identifica a interrupÃƒÂ§ÃƒÂ£o e o retorno do feixe de luz.
- MantÃƒÂ©m um contador acumulativo de peÃƒÂ§as produzidas.
- Monitora micro-paradas na esteira: quando o sensor permanece bloqueado por mais de 5 segundos, emite um alerta de gargalo.
- Permite ao operador resetar manualmente o turno via botÃƒÂ£o fÃƒÂ­sico, zerando todos os contadores.

**InteraÃƒÂ§ÃƒÂ£o do usuÃƒÂ¡rio:**
- O operador acompanha a produÃƒÂ§ÃƒÂ£o pelo terminal serial (UART).
- Pode pressionar o botÃƒÂ£o de reset a qualquer momento para encerrar o turno atual.

---

## Arquitetura do Sistema Embarcado

### Fluxo Principal (`main.py`)

```
InicializaÃƒÂ§ÃƒÂ£o
      |
      v
  Imprime "Contador de Producao Inicializado"
      |
      v
  +----------------------------------+
  |         LOOP PRINCIPAL           |
  |    (nÃƒÂ£o-bloqueante, 50ms)        |
  |                                  |
  |  1. Ler valor ADC do LDR        |
  |  2. Verificar detecÃƒÂ§ÃƒÂ£o de peÃƒÂ§a   |
  |  3. Verificar micro-parada      |
  |  4. Verificar botÃƒÂ£o de reset     |
  |  5. Sleep 50ms                   |
  +----------------------------------+
```

### MÃƒÂ¡quina de Estados do Sensor LDR

O sistema opera com dois estados para o sensor ÃƒÂ³ptico:

| Estado         | CondiÃƒÂ§ÃƒÂ£o                        | DescriÃƒÂ§ÃƒÂ£o                      |
| :------------- | :------------------------------ | :----------------------------- |
| **LIVRE**      | ADC < 1000 (lux alto, ~800)     | Esteira livre, sem obstruÃƒÂ§ÃƒÂ£o   |
| **BLOQUEADO**  | ADC > 2000 (lux baixo, ~50)     | PeÃƒÂ§a presente sobre o sensor   |

A contagem de peÃƒÂ§as ÃƒÂ© incrementada exclusivamente na **borda de subida** (transiÃƒÂ§ÃƒÂ£o BLOQUEADO para LIVRE), garantindo que a peÃƒÂ§a passou completamente pelo sensor antes de registrar o evento.

### EstratÃƒÂ©gia de TemporizaÃƒÂ§ÃƒÂ£o

Todas as temporizaÃƒÂ§ÃƒÂµes utilizam `time.ticks_ms()` e `time.ticks_diff()` para garantir uma **arquitetura totalmente nÃƒÂ£o-bloqueante**, conforme requisito do CI:

- **Micro-parada:** Temporizador iniciado quando o sensor entra em estado BLOQUEADO. Se `ticks_diff >= 5000ms`, emite o alerta.
- **Debounce do botÃƒÂ£o:** Filtragem por software com janela de 50ms para evitar falsos gatilhos mecÃƒÂ¢nicos.

---

## Componentes Utilizados na SimulaÃƒÂ§ÃƒÂ£o

| Componente                    | ID no Wokwi | Pino ESP32 | FunÃƒÂ§ÃƒÂ£o                                         |
| :---------------------------- | :---------- | :--------- | :--------------------------------------------- |
| ESP32 DevKit C v4             | `esp`     | Ã¢â‚¬â€          | Microcontrolador principal                     |
| Fotorresistor (LDR)           | `ldr1`    | GPIO 34    | Sensor ÃƒÂ³ptico de detecÃƒÂ§ÃƒÂ£o de peÃƒÂ§as             |
| BotÃƒÂ£o Push-button             | `btn1`    | GPIO 23    | Reset manual de turno (pull-up interno)        |
| Monitor Serial                | Ã¢â‚¬â€           | TX/RX      | SaÃƒÂ­da de logs e telemetria via UART            |

### ConexÃƒÂµes ElÃƒÂ©tricas

- **LDR para ESP32:** VCC para 3V3, GND para GND, saÃƒÂ­da analÃƒÂ³gica (AO) para GPIO 34.
- **BotÃƒÂ£o para ESP32:** Terminal 1 para GND, Terminal 2 para GPIO 23 (com pull-up interno habilitado no firmware).

---

## DecisÃƒÂµes TÃƒÂ©cnicas Relevantes

### OrganizaÃƒÂ§ÃƒÂ£o do CÃƒÂ³digo

O firmware foi estruturado com separaÃƒÂ§ÃƒÂ£o clara de responsabilidades:

- **Constantes de configuraÃƒÂ§ÃƒÂ£o** agrupadas no topo do arquivo para fÃƒÂ¡cil parametrizaÃƒÂ§ÃƒÂ£o (`LIMIAR_BLOQUEIO`, `LIMIAR_LIVRE`, `TEMPO_MICRO_PARADA_MS`, etc.).
- **FunÃƒÂ§ÃƒÂµes dedicadas** para cada subsistema:
  - `ler_luminosidade()` Ã¢â‚¬â€ abstrai a leitura do ADC.
  - `verificar_deteccao_peca()` Ã¢â‚¬â€ lÃƒÂ³gica de transiÃƒÂ§ÃƒÂµes de luz.
  - `verificar_micro_parada()` Ã¢â‚¬â€ temporizador de gargalo.
  - `verificar_botao_reset()` Ã¢â‚¬â€ debounce e reset de turno.

### Debounce por Software

Implementei debounce por amostragem temporal: a cada iteraÃƒÂ§ÃƒÂ£o do loop, o estado bruto do botÃƒÂ£o ÃƒÂ© lido. Se houver mudanÃƒÂ§a, o timer de debounce ÃƒÂ© reiniciado. O estado sÃƒÂ³ ÃƒÂ© aceito como estÃƒÂ¡vel apÃƒÂ³s 50ms sem variaÃƒÂ§ÃƒÂ£o, prevenindo mÃƒÂºltiplos disparos por bounce mecÃƒÂ¢nico.

### DetecÃƒÂ§ÃƒÂ£o por Borda de Subida

A contagem de peÃƒÂ§as ÃƒÂ© feita na **borda de subida** (retorno da luz) e nÃƒÂ£o na borda de descida (bloqueio). Isso garante que a peÃƒÂ§a passou completamente pelo sensor antes de ser contabilizada, evitando contagens duplicadas ou prematuras.

### Histerese nos Limiares

Utilizei dois limiares distintos (`LIMIAR_BLOQUEIO = 1000` e `LIMIAR_LIVRE = 2000`) ao invÃƒÂ©s de um ÃƒÂºnico valor, criando uma faixa de histerese que evita oscilaÃƒÂ§ÃƒÂµes falsas quando a leitura do sensor estÃƒÂ¡ prÃƒÂ³xima do limiar de transiÃƒÂ§ÃƒÂ£o.

---

## Resultados Obtidos

### Requisitos Atendidos

| Requisito                              | Status |
| :------------------------------------- | :----: |
| Mensagem de inicializaÃƒÂ§ÃƒÂ£o exata        |   OK   |
| DetecÃƒÂ§ÃƒÂ£o e contagem de peÃƒÂ§as (borda)   |   OK   |
| Mensagem "Peca detectada! Total: X"    |   OK   |
| DetecÃƒÂ§ÃƒÂ£o de micro-parada (> 5s)        |   OK   |
| Mensagem "Alerta: Micro-parada..."     |   OK   |
| Reset de turno via botÃƒÂ£o com debounce  |   OK   |
| Mensagem "Turno resetado..."           |   OK   |
| Arquitetura nÃƒÂ£o-bloqueante             |   OK   |
| Casamento exato de strings para CI     |   OK   |

### Mensagens Seriais (casamento exato com o CI)

```
Contador de Producao Inicializado
Peca detectada! Total: 1
Alerta: Micro-parada detectada!
Turno resetado com sucesso. Contadores zerados.
```

---

## ComentÃƒÂ¡rios Adicionais

### Principais DecisÃƒÂµes

- O intervalo do loop principal foi definido em 50ms para equilibrar responsividade do sensor com consumo de processamento.
- A utilizaÃƒÂ§ÃƒÂ£o de `time.ticks_ms()` em vez de `time.sleep()` garante que nenhuma funcionalidade ÃƒÂ© bloqueada enquanto aguarda temporizadores.
- O uso de pull-up interno no botÃƒÂ£o simplifica o circuito, dispensando resistores externos.

### Melhorias Futuras

- ImplementaÃƒÂ§ÃƒÂ£o de display OLED para visualizaÃƒÂ§ÃƒÂ£o local da contagem sem depender do terminal serial.
- AdiÃƒÂ§ÃƒÂ£o de LED indicador de status (verde para operaÃƒÂ§ÃƒÂ£o normal, vermelho para micro-parada).
- Armazenamento de dados de turno em NVS (Non-Volatile Storage) para persistÃƒÂªncia apÃƒÂ³s resets.
- CÃƒÂ¡lculo e exibiÃƒÂ§ÃƒÂ£o de mÃƒÂ©tricas de produtividade (peÃƒÂ§as/minuto, tempo mÃƒÂ©dio de ciclo).
