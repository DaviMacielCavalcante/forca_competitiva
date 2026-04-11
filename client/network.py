class NetworkClient:

    def connect(self, host: str, port: int, name: str):
        
        pass
    
    def poll(self) -> list[dict]:
        
        return []

    def send_word(self, word: str):
        
        pass

    def send_letter(self, letter: str):
        
        pass

    def disconnect(self):

        pass 
    
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