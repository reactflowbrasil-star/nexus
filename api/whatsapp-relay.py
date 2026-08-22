"""Relay de recebimento do WhatsApp (Evolution GO -> Nexus CRM).

O Evolution GO envia webhooks para POST aqui; o frontend Nexus faz GET
periodicamente (3s) e importa as mensagens recebidas na inbox.

Funciona como:
  - WSGI application(environ, start_response)
  - handler(request) / handler(event, context) (estilo serverless)
  - main(request) (Cloud Functions / Flask)
"""
import json
import time

_MESSAGES = []
_MAX = 500
_SECRET = None  # opcional: defina WEBHOOK_SECRET para validar


def _add(msg):
    _MSGS.append(msg)
    if len(_MSGS) > _MAX:
        del _MSGS[: len(_MSGS) - _MAX]


def _ok(body):
    return 200, {"application/json": json.dumps(body)}


def _dispatch(method, query, body):
    if method == "GET":
        return _ok({"messages": list(_MSGS), "count": len(_MSGS), "ts": time.time()})

    if method == "POST":
        event = body.get("event") or ""
        data = body.get("data") or {}
        # Formato Evolution API: event=MESSAGES_UPSERT, data={key:{remoteJid,fromMe,id}, message:{...}, messageTimestamp}
        if "MESSAGE" in event.upper() or ("key" in data and "message" in data):
            _add({
                "key": data.get("key", {}),
                "message": data.get("message", {}),
                "messageTimestamp": data.get("messageTimestamp", int(time.time())),
                "event": event,
                "_rcv": time.time(),
            })
            # limpa mensagens com mais de 1 hora
            now = time.time()
            _MSGS[:] = [m for m in _MSGS if now - m.get("_rcv", now) < 3600]
        return _ok({"status": "success"})

    return 405, {"application/json": json.dumps({"error": "method not allowed"})}


# ---------- WSGI ----------
def application(environ, start_response):
    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
        raw = environ["wsgi.input"].read(length) if length else b""
        body = json.loads(raw) if raw else {}
    except Exception:
        body = {}
    status, payload = _dispatch(environ.get("REQUEST_METHOD", "GET"), {}, body)
    body_bytes = b""
    for ctype, content in payload.items():
        body_bytes = content.encode()
        headers = [("Content-Type", ctype), ("Content-Length", str(len(body_bytes)))]
        break
    start_response("%d OK" % status if status == 200 else "%d Error" % status, headers)
    return [body_bytes]


# ---------- Serverless genérico (request object ou event/context) ----------
def handler(request_or_event, context=None):
    req = request_or_event
    # AWS-style: {httpMethod, body}
    if isinstance(req, dict) and "httpMethod" in req:
        try:
            body = json.loads(req.get("body") or "{}")
        except Exception:
            body = {}
        status, payload = _dispatch(req.get("httpMethod", "GET"), req.get("queryStringParameters") or {}, body)
        content = list(payload.values())[0]
        return {"statusCode": status, "headers": {"Content-Type": "application/json"}, "body": content}
    # Request object style (Flask/Starlette/Cloud Functions)
    method = getattr(req, "method", "GET")
    try:
        body = json.loads(req.get_data() or req.body or "{}") if method != "GET" else {}
    except Exception:
        body = {}
    status, payload = _dispatch(method, {}, body)
    content = list(payload.values())[0]

    class _Resp:
        status_code = status
        data = content
        def get_data(self, as_text=False):
            return content
    return _Resp()


def main(request):
    return handler(request)
