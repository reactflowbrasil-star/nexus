# Nexus + Evolution GO Custom

O Nexus incorpora o `evolution-go-custom` como backend oficial de WhatsApp em:

```text
backend/evolution-go-custom
```

## Inicialização

1. Entre em `backend/evolution-go-custom`.
2. Copie `.env.example` para `.env`.
3. Defina uma `GLOBAL_API_KEY` forte e exclusiva.
4. Suba o ambiente com o compose de `deploy/docker-compose.yml`.
5. Configure o front-end Nexus para apontar para `http://localhost:8080` ou para a URL pública do serviço.

O Manager fica em `/manager`, a documentação em `/swagger/index.html` e a API usa o header `apikey`.

## Contrato usado pelo Nexus

- Criar instância: `POST /instance/create`
- Consultar QR Code: `GET /instance/qr`
- Listar instâncias: `GET /instance/all`
- Enviar mensagem: endpoints `/send/*`
- Eventos: webhooks configurados por instância

As credenciais devem permanecer somente no ambiente do backend; o `index.html` não contém chaves nem segredos.

## Origem

- Repositório: `https://github.com/NathanAshford/evolution-go-custom`
- Branch integrada: `main`
- Commit integrado: `8e606359a221fe34f5fcc34131767deb3dc43af4`
