# Nexus Relay — recebimento de mensagens em tempo real

O Evolution GO envia os eventos (incl. `MESSAGES_UPSERT`) para a env
`WEBHOOK_URL`. O relay recebe, guarda em memória e o Nexus CRM lê via
polling (3s) no navegador.

## Ativar no servidor (1 minuto)

```bash
cd backend/evolution-go-custom-content/deploy

# 1. Aponta o webhook do Evolution GO para o relay (rede interna do docker)
echo "WEBHOOK_URL=http://nexus-relay:9090/webhook" >> .env

# 2. (opcional) muda a porta pública do relay
# echo "RELAY_PORT=9090" >> .env

# 3. Sobe o relay e reinicia o Evolution GO (para ler a nova env)
docker compose up -d nexus-relay
docker compose up -d --force-recreate evolution-go
```

## Configurar no Nexus CRM

1. Abra **Integrações → Evolution GO → Config**
2. Em **"Relay de recebimento (webhook)"**, cole:
   `http://SEU-SERVIDOR:9090/messages`
   (o mesmo host/IP público onde o Evolution GO responde, porta 9090)
3. Salve — o inbox passa a importar as mensagens recebidas a cada 3s

## Notas

- Se o Evolution GO estiver atrás de reverse proxy com HTTPS, exponha
  também a porta 9090 no proxy (ou use o IP direto — o relay já envia
  headers CORS, então o navegador do CRM consegue ler de qualquer origem).
- O relay guarda até 500 mensagens (última hora) em memória — é só um
  canal ao vivo, o histórico fica no próprio WhatsApp/CRM.
- Teste manual: `curl http://localhost:9090/messages`
