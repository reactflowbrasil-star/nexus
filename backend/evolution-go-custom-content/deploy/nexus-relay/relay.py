"""Nexus Relay — recebe webhooks do Evolution GO e serve as mensagens
para o inbox do Nexus CRM (polling do navegador a cada 3s).

Rotas:
  POST /webhook   <- Evolution GO (env WEBHOOK_URL)
  GET  /messages  -> navegador (CORS liberado)

Sem dependências externas (apenas stdlib). Porta 9090.
"""
import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

MSGS = []
MAX = 500


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send(200, {"ok": True})

    def do_GET(self):
        if urlparse(self.path).path in ("/messages", "/"):
            now = time.time()
            MSGS[:] = [m for m in MSGS if now - m.get("_rcv", now) < 3600]
            self._send(200, {"messages": list(MSGS), "count": len(MSGS)})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        if urlparse(self.path).path != "/webhook":
            return self._send(404, {"error": "not found"})
        length = int(self.headers.get("Content-Length") or 0)
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except Exception:
            return self._send(400, {"error": "bad json"})
        event = payload.get("event") or ""
        data = payload.get("data") or {}
        if "MESSAGE" in event.upper() or ("key" in data and "message" in data):
            MSGS.append({
                "key": data.get("key", {}),
                "message": data.get("message", {}),
                "messageTimestamp": data.get("messageTimestamp", int(time.time())),
                "event": event,
                "_rcv": time.time(),
            })
            del MSGS[: max(0, len(MSGS) - MAX)]
        self._send(200, {"status": "success"})

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    print("Nexus relay ouvindo em :9090 (POST /webhook | GET /messages)")
    ThreadingHTTPServer(("0.0.0.0", 9090), Handler).serve_forever()
