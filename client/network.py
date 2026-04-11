import json
import queue
import socket
import threading

class NetworkClient:
    
    def __init__(self):
        
        self._queue = queue.Queue()
        self._tcp_socket = None
        self._udp_socket = None 
        self._tcp_thread = None
        self._udp_thread = None 
        self._running = False
        
    def _send(self, message: dict):
    
        json_data = json.dumps(message) + "\n"
        
        bytes_data = json_data.encode()
        
        self._tcp_socket.sendall(bytes_data)
        
    def _tcp_reader(self):
        # Roda numa thread dedicada (daemon) pelo padrão produtor-consumidor:
        # socket.recv() é BLOQUEANTE — se fosse chamado na thread do game loop,
        # o jogo congelaria toda vez que a rede ficasse quieta. Por isso esta
        # thread fica presa em recv() o tempo todo e só se comunica com a view
        # empurrando dicts já decodificados em self._queue (que é uma
        # queue.Queue, thread-safe). A view drena essa fila via poll() no
        # on_update, sem bloquear.
        #
        # TCP é um stream de bytes, não de mensagens: um único recv() pode
        # devolver uma mensagem inteira, meia mensagem, ou várias coladas.
        # Por isso acumulamos bytes num buffer e só consumimos pedaços
        # terminados em '\n' (o delimitador do protocolo). O que sobrar
        # depois do último '\n' é uma mensagem parcial e fica no buffer
        # pro próximo recv completar.
        #
        # recv() devolve b"" (não None) quando o servidor fecha a conexão —
        # por isso o check é `if not data: break`. JSON inválido é ignorado
        # silenciosamente pra não derrubar a thread inteira por causa de
        # uma mensagem corrompida.
        buffer = b""

        while self._running:
            
            try:
                data = self._tcp_socket.recv(1024)
            except OSError:
                break
            
            if not data:
                break
            
            buffer += data
            
            while b"\n" in buffer:
                
                before, _, after = buffer.partition(b"\n")
                
                buffer = after
                
                try: 
                    message = json.loads(before)
                    self._queue.put(message)
                except json.JSONDecodeError:
                    pass
                    

    def _udp_reader(self):
        # Mesma ideia do _tcp_reader: roda numa thread daemon dedicada porque
        # recvfrom() é bloqueante, e empurra os dicts decodificados na MESMA
        # self._queue que o TCP usa — a view drena tudo junto no poll(), sem
        # precisar saber de qual canal veio cada mensagem.
        #
        # Diferença essencial pro TCP: UDP é orientado a datagramas, não a
        # bytes. Cada recvfrom() devolve exatamente UM datagrama, inteiro,
        # tal como foi enviado pelo sendto() do servidor. Não existe
        # "mensagem partida ao meio" nem "mensagens coladas", então não
        # precisamos de buffer, delimitador nem loop interno de partition.
        # Só: recebeu → parseou → enfileirou.
        #
        # recvfrom() devolve uma tupla (data, address); descartamos o
        # address com `_` porque confiamos que vem do servidor — o único
        # que manda datagramas pra esta porta. JSON inválido é ignorado
        # pra não derrubar a thread.
        while self._running:
            
            try:
                data, _ = self._udp_socket.recvfrom(1024)
            except OSError:
                break
                
            try: 
                message = json.loads(data)
                self._queue.put(message)
            except json.JSONDecodeError:
                pass

    def connect(self, host: str, port: int, name: str):
        
        self._tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._tcp_socket.connect((host, port))
        
        self._udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # escuta na porta em todas as interfaces locais
        self._udp_socket.bind(("", 32350))
        
        message = {
            "acao": "entrar",
            "nome": name
        }
        
        self._send(message=message)
        
        self._tcp_thread = threading.Thread(target=self._tcp_reader, daemon=True)
        self._udp_thread = threading.Thread(target=self._udp_reader, daemon=True)
        
        self._running = True
        
        self._tcp_thread.start()      
        self._udp_thread.start()
        
    
    def poll(self) -> list[dict]:
        
        messages = []
        
        while True:
            try:
                messages.append(self._queue.get_nowait())
            except queue.Empty:
                break
            
        return messages

    def send_word(self, word: str):
        
        word_dict = {
            "acao": "palavra",
            "palavra": word
        }
        
        self._send(message=word_dict)

    def send_letter(self, letter: str):
        
        letter_dict = {
            "acao": "letra",
            "letra": letter
        }
        
        self._send(message=letter_dict)

    def disconnect(self):
        
        self._running = False
        
        if self._tcp_socket is not None:
            try:
                self._tcp_socket.close()
            except OSError:
                pass
            self._tcp_socket = None

        if self._udp_socket is not None:
            try:
                self._udp_socket.close()
            except OSError:
                pass
            self._udp_socket = None
            
        if self._tcp_thread is not None:
            self._tcp_thread.join(timeout=1)
        if self._udp_thread is not None:
            self._udp_thread.join(timeout=1)
    
class FakeNetworkClient:
    
    def __init__(self):
        self._queue = []

    def connect(self, host: str, port: int, name: str):
        
        pass
    
    def poll(self) -> list[dict]:
        
        messages = self._queue
        
        self._queue = []
        
        return messages

    def send_word(self, word: str):
        
        pass

    def send_letter(self, letter: str):
        
        pass

    def disconnect(self):

        pass
    
    def inject(self, message: dict):
        
        self._queue.append(message)