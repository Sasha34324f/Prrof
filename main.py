import socket
import threading

LISTEN_IP = "0.0.0.0"
LISTEN_PORT = 1080

USERNAME = "admin"
PASSWORD = "1234"

def handle_client(client):
    try:
        # greeting
        version, nmethods = client.recv(2)
        methods = client.recv(nmethods)

        # говорим: нужна авторизация (0x02)
        client.sendall(b"\x05\x02")

        # auth request
        version = client.recv(1)
        ulen = client.recv(1)[0]
        username = client.recv(ulen).decode()
        plen = client.recv(1)[0]
        password = client.recv(plen).decode()

        if username != USERNAME or password != PASSWORD:
            client.sendall(b"\x01\x01")  # fail
            client.close()
            return

        client.sendall(b"\x01\x00")  # success

        # request
        data = client.recv(4)
        cmd = data[1]

        if cmd != 1:
            client.close()
            return

        atyp = client.recv(1)[0]

        if atyp == 1:  # IPv4
            addr = socket.inet_ntoa(client.recv(4))
        elif atyp == 3:  # domain
            domain_len = client.recv(1)[0]
            addr = client.recv(domain_len).decode()
        else:
            client.close()
            return

        port = int.from_bytes(client.recv(2), 'big')

        remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote.connect((addr, port))

        client.sendall(b"\x05\x00\x00\x01" + socket.inet_aton("0.0.0.0") + (0).to_bytes(2, 'big'))

        def forward(src, dst):
            while True:
                data = src.recv(4096)
                if not data:
                    break
                dst.sendall(data)

        threading.Thread(target=forward, args=(client, remote)).start()
        threading.Thread(target=forward, args=(remote, client)).start()

    except:
        client.close()

def start():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((LISTEN_IP, LISTEN_PORT))
    server.listen(100)

    print(f"SOCKS5 с авторизацией запущен на {LISTEN_IP}:{LISTEN_PORT}")
    print(f"Логин: {USERNAME} Пароль: {PASSWORD}")

    while True:
        client, addr = server.accept()
        threading.Thread(target=handle_client, args=(client,)).start()

if __name__ == "__main__":
    start()
