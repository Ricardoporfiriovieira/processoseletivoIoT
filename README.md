# Processo Seletivo â€“ Intensivo Maker | IoT

## Etapa PrÃ¡tica â€“ Sistemas Embarcados

---

### IdentificaÃ§Ã£o do Candidato

- **Nome completo:** Ricardo PorfÃ­rio
- **GitHub:** Ricardo PorfÃ­rio
- **E-mail:** ricardoporfiriovieira@gmail.com

---

## VisÃ£o Geral da SoluÃ§Ã£o

Este projeto implementa um **Contador de ProduÃ§Ã£o NÃ£o-Intrusivo** para monitoramento de esteiras transportadoras industriais, utilizando um ESP32 simulado no Wokwi com MicroPython.

**O que o sistema faz:**
- Detecta a passagem de peÃ§as/caixas em uma esteira por meio de um sensor Ã³ptico (LDR), que identifica a interrupÃ§Ã£o e o retorno do feixe de luz.
- MantÃ©m um contador acumulativo de peÃ§as produzidas.
- Monitora micro-paradas na esteira: quando o sensor permanece bloqueado por mais de 5 segundos, emite um alerta de gargalo.
- Permite ao operador resetar manualmente o turno via botÃ£o fÃ­sico, zerando todos os contadores.

**InteraÃ§Ã£o do usuÃ¡rio:**
- O operador acompanha a produÃ§Ã£o pelo terminal serial (UART).
- Pode pressionar o botÃ£o de reset a qualquer momento para encerrar o turno atual.

---

## Arquitetura do Sistema Embarcado

### Fluxo Principal (`main.py`)

```
InicializaÃ§Ã£o
      |
      v
  Imprime "Contador de Producao Inicializado"
      |
      v
  +----------------------------------+
  |         LOOP PRINCIPAL           |
  |    (nÃ£o-bloqueante, 50ms)        |
  |                                  |
  |  1. Ler valor ADC do LDR        |
  |  2. Verificar detecÃ§Ã£o de peÃ§a   |
  |  3. Verificar micro-parada      |
  |  4. Verificar botÃ£o de reset     |
  |  5. Sleep 50ms                   |
  +----------------------------------+
```

### MÃ¡quina de Estados do Sensor LDR

O sistema opera com dois estados para o sensor Ã³ptico:

| Estado         | CondiÃ§Ã£o                        | DescriÃ§Ã£o                      |
| :------------- | :------------------------------ | :----------------------------- |
| **LIVRE**      | ADC > 2000 (lux alto, ~800)     | Esteira livre, sem obstruÃ§Ã£o   |
| **BLOQUEADO**  | ADC < 1000 (lux baixo, ~50)     | PeÃ§a presente sobre o sensor   |

A contagem de peÃ§as Ã© incrementada exclusivamente na **borda de subida** (transiÃ§Ã£o BLOQUEADO para LIVRE), garantindo que a peÃ§a passou completamente pelo sensor antes de registrar o evento.

### EstratÃ©gia de TemporizaÃ§Ã£o

Todas as temporizaÃ§Ãµes utilizam `time.ticks_ms()` e `time.ticks_diff()` para garantir uma **arquitetura totalmente nÃ£o-bloqueante**, conforme requisito do CI:

- **Micro-parada:** Temporizador iniciado quando o sensor entra em estado BLOQUEADO. Se `ticks_diff >= 5000ms`, emite o alerta.
- **Debounce do botÃ£o:** Filtragem por software com janela de 50ms para evitar falsos gatilhos mecÃ¢nicos.

---

## Componentes Utilizados na SimulaÃ§Ã£o

| Componente                    | ID no Wokwi | Pino ESP32 | FunÃ§Ã£o                                         |
| :---------------------------- | :---------- | :--------- | :--------------------------------------------- |
| ESP32 DevKit C v4             | `esp`     | â€”          | Microcontrolador principal                     |
| Fotorresistor (LDR)           | `ldr1`    | GPIO 34    | Sensor Ã³ptico de detecÃ§Ã£o de peÃ§as             |
| BotÃ£o Push-button             | `btn1`    | GPIO 23    | Reset manual de turno (pull-up interno)        |
| Monitor Serial                | â€”           | TX/RX      | SaÃ­da de logs e telemetria via UART            |

### ConexÃµes ElÃ©tricas

- **LDR para ESP32:** VCC para 3V3, GND para GND, saÃ­da analÃ³gica (AO) para GPIO 34.
- **BotÃ£o para ESP32:** Terminal 1 para GND, Terminal 2 para GPIO 23 (com pull-up interno habilitado no firmware).

---

## DecisÃµes TÃ©cnicas Relevantes

### OrganizaÃ§Ã£o do CÃ³digo

O firmware foi estruturado com separaÃ§Ã£o clara de responsabilidades:

- **Constantes de configuraÃ§Ã£o** agrupadas no topo do arquivo para fÃ¡cil parametrizaÃ§Ã£o (`LIMIAR_BLOQUEIO`, `LIMIAR_LIVRE`, `TEMPO_MICRO_PARADA_MS`, etc.).
- **FunÃ§Ãµes dedicadas** para cada subsistema:
  - `ler_luminosidade()` â€” abstrai a leitura do ADC.
  - `verificar_deteccao_peca()` â€” lÃ³gica de transiÃ§Ãµes de luz.
  - `verificar_micro_parada()` â€” temporizador de gargalo.
  - `verificar_botao_reset()` â€” debounce e reset de turno.

### Debounce por Software

Implementei debounce por amostragem temporal: a cada iteraÃ§Ã£o do loop, o estado bruto do botÃ£o Ã© lido. Se houver mudanÃ§a, o timer de debounce Ã© reiniciado. O estado sÃ³ Ã© aceito como estÃ¡vel apÃ³s 50ms sem variaÃ§Ã£o, prevenindo mÃºltiplos disparos por bounce mecÃ¢nico.

### DetecÃ§Ã£o por Borda de Subida

A contagem de peÃ§as Ã© feita na **borda de subida** (retorno da luz) e nÃ£o na borda de descida (bloqueio). Isso garante que a peÃ§a passou completamente pelo sensor antes de ser contabilizada, evitando contagens duplicadas ou prematuras.

### Histerese nos Limiares

Utilizei dois limiares distintos (`LIMIAR_BLOQUEIO = 1000` e `LIMIAR_LIVRE = 2000`) ao invÃ©s de um Ãºnico valor, criando uma faixa de histerese que evita oscilaÃ§Ãµes falsas quando a leitura do sensor estÃ¡ prÃ³xima do limiar de transiÃ§Ã£o.

---

## Resultados Obtidos

### Requisitos Atendidos

| Requisito                              | Status |
| :------------------------------------- | :----: |
| Mensagem de inicializaÃ§Ã£o exata        |   OK   |
| DetecÃ§Ã£o e contagem de peÃ§as (borda)   |   OK   |
| Mensagem "Peca detectada! Total: X"    |   OK   |
| DetecÃ§Ã£o de micro-parada (> 5s)        |   OK   |
| Mensagem "Alerta: Micro-parada..."     |   OK   |
| Reset de turno via botÃ£o com debounce  |   OK   |
| Mensagem "Turno resetado..."           |   OK   |
| Arquitetura nÃ£o-bloqueante             |   OK   |
| Casamento exato de strings para CI     |   OK   |

### Mensagens Seriais (casamento exato com o CI)

```
Contador de Producao Inicializado
Peca detectada! Total: 1
Alerta: Micro-parada detectada!
Turno resetado com sucesso. Contadores zerados.
```

---

## ComentÃ¡rios Adicionais

### Principais DecisÃµes

- O intervalo do loop principal foi definido em 50ms para equilibrar responsividade do sensor com consumo de processamento.
- A utilizaÃ§Ã£o de `time.ticks_ms()` em vez de `time.sleep()` garante que nenhuma funcionalidade Ã© bloqueada enquanto aguarda temporizadores.
- O uso de pull-up interno no botÃ£o simplifica o circuito, dispensando resistores externos.

### Melhorias Futuras

- ImplementaÃ§Ã£o de display OLED para visualizaÃ§Ã£o local da contagem sem depender do terminal serial.
- AdiÃ§Ã£o de LED indicador de status (verde para operaÃ§Ã£o normal, vermelho para micro-parada).
- Armazenamento de dados de turno em NVS (Non-Volatile Storage) para persistÃªncia apÃ³s resets.
- CÃ¡lculo e exibiÃ§Ã£o de mÃ©tricas de produtividade (peÃ§as/minuto, tempo mÃ©dio de ciclo).
