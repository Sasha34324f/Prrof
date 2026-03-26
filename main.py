from flask import Flask, jsonify
import os

app = Flask(__name__)

proxy_data = {
    "id": "GPP1082880",
    "order_id": "GPO8128546",
    "ip": "153.80.100.17",
    "status": "active",
    "type": "private_ipv4",
    "auth": {
        "login": "GXjt8nK3",
        "password": "ghhPdd4C"
    },
    "ports": {
        "http": 63924,
        "socks5": 63925
    },
    "location": {
        "country": "Romania",
        "city": "Random"
    },
    "expires": "2026-03-29 14:40:24"
}

@app.route("/")
def home():
    return "Proxy API is running 🚀"

@app.route("/proxy")
def proxy():
    return jsonify(proxy_data)

@app.route("/proxy/http")
def proxy_http():
    return f"http://{proxy_data['auth']['login']}:{proxy_data['auth']['password']}@{proxy_data['ip']}:{proxy_data['ports']['http']}"

@app.route("/proxy/socks5")
def proxy_socks5():
    return f"socks5://{proxy_data['auth']['login']}:{proxy_data['auth']['password']}@{proxy_data['ip']}:{proxy_data['ports']['socks5']}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
