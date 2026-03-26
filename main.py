import socket
import threading

USERNAME = "user"
PASSWORD = "pass"

def handle_client(client):
    try:
        # greeting
        client.recv(262)
        client.sendall(b"\x05\x02")  # username/password auth

        # auth
        version = client.recv(1)
        username_len = client.recv(1)[0]
        username = client.recv(username_len).decode()
        password_len = client.recv(1)[0]
        password = client.recv(password_len).decode()

        if username != USERNAME or password != PASSWORD:
            client.sendall(b"\x01\x01")  # auth failed
            client.close()
            return

        client.sendall(b"\x01\x00")  # auth success

        # request
        version, cmd, _, addr_type = client.recv(4)

        if addr_type == 1:  # IPv4
            addr = socket.inet_ntoa(client.recv(4))
        else:
            client.close()
            return

        port = int.from_bytes(client.recv(2), 'big')

        # connect to target
        remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote.connect((addr, port))

        client.sendall(b"\x05\x00\x00\x01" + socket.inet_aton(addr) + port.to_bytes(2, 'big'))

        # forwarding
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
    server.bind(("0.0.0.0", 1080))
    server.listen(100)

    print("SOCKS5 proxy running on port 1080...")

    while True:
        client, addr = server.accept()
        threading.Thread(target=handle_client, args=(client,)).start()

if __name__ == "__main__":
    start()
