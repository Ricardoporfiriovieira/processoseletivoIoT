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
