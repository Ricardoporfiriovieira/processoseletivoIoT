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
