# save this as test_client.py and run in another terminal
import socket, json

conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn.connect(("localhost", 32348))
conn.sendall(b'{"acao": "entrar", "nome": "Joao"}\n')
response = conn.recv(1024)
print(response)
conn.close()
