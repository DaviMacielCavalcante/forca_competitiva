# O que aprendi — Davi

Anotações pessoais das lições que saíram da implementação do `client/network.py` (Fase 0 + Tarefa 1 do INTEGRATION_TODO). Serve de referência pra mim e pros colegas que forem mexer no módulo depois.

---

## Fase 0 — Contrato do `NetworkClient`

### 1. "Contrato antes de implementação"

Fase 0 existe como etapa separada por um motivo específico: **fixar as assinaturas públicas** (nomes de métodos, parâmetros, tipos de retorno) com corpos vazios (`pass` / `return []`), pra destravar trabalho paralelo. Enquanto eu implemento os sockets, o João Miguel e o Pablo já podem escrever `self.window.network.connect(host, port, name)` nas views deles — só precisam que a classe e os métodos existam. Congelar a forma do buraco antes de preencher.

### 2. Fake vs stub — dois test doubles diferentes

- **`NetworkClient`** (stub puro): corpo `pass`, não faz nada. Só declara a forma da API.
- **`FakeNetworkClient`** (fake funcional): mesma interface, mas **funciona de verdade** — tem fila interna, `inject()` empurra mensagens, `poll()` drena.

Mental model: o fake é o **simulador de voo**, a view é o **piloto**, o servidor real é o **avião**. Quando o Pablo testa a `GameView`, o fake está **no lugar** do servidor, não testando o servidor. O `assert` é sobre o estado da view, nunca sobre o estado do fake.

### 3. Retorno consistente de coleções

`poll()` sempre devolve uma lista — vazia (`[]`) quando não tem nada, cheia quando tem. **Nunca `None`**. Isso permite o idioma `for msg in network.poll():` funcionar sem `if result is not None`. Regra geral de API em Python: "devolva coleção vazia em vez de `None` pra coleções".

### 4. Semântica de referências em Python (o truque do reference-swap)

Isso é grande e vai voltar a morder em outros contextos:

- `a = b` **não copia nada**. Só cria outro nome apontando pro mesmo objeto.
- `a = []` **não esvazia** uma lista. Só faz o nome `a` apontar pra uma lista nova.
- Mexer numa lista (`clear`, `append`) afeta todos os nomes colados nela. *Reatribuir* um nome só afeta aquele nome.

O `poll()` do `FakeNetworkClient` explora exatamente essa distinção:

```python
def poll(self) -> list[dict]:
    messages = self._queue   # "messages" e "self._queue" apontam pra MESMA lista (cheia)
    self._queue = []         # "self._queue" passa a apontar pra uma lista NOVA, vazia
    return messages          # devolve a lista antiga, intacta, com todas as mensagens
```

Três linhas. Não esvaziamos a lista antiga — **abandonamos** ela e damos à instância uma lista nova. A lista antiga sobrevive porque `messages` ainda a segura.

### 5. Type hints não podem mentir

Declarar `-> dict` num método cujo corpo é `pass` (que retorna `None`) é mentira pro type checker e pro leitor. Métodos de ação (`connect`, `send_word`, `disconnect`) não retornam nada — sem `-> tipo` na assinatura. Só `poll()` tem `-> list[dict]` porque é o único que de fato devolve dados.

### 6. Erros bobos que eu esqueci (pra não esquecer de novo)

- **`self` em todo método de instância.** Inclusive `__init__`. Sem ele, `NetworkClient()` explode com `TypeError`.
- **`pool` ≠ `poll`.** `pool` é piscina. `poll` (dois `l`) é "consultar". Uma letra errada quebra o contrato inteiro.
- **Nomes das classes são literais.** O INTEGRATION_TODO pede `NetworkClient`, não `NetworkInterface`. Se eu renomear, o `import` dos colegas quebra.
- **`list.remove()` ≠ `list.clear()`.** `remove(x)` tira **um elemento por valor**, `clear()` esvazia tudo.

---

## Tarefa 1 — Implementação real (sockets + threads)

### 7. `recv()` é bloqueante → vive em thread separada

`socket.recv()` **para a thread** até o SO entregar pelo menos um byte. Se eu chamasse isso dentro do `on_update` do game loop, o jogo congelaria toda vez que a rede ficasse quieta. Por isso a thread leitora fica **dedicada** a isso, presa em `recv()` o tempo todo, sem atrapalhar ninguém.

### 8. Padrão produtor–consumidor com `queue.Queue`

Forma idiomática de threads falarem em Python:

- **Produtor:** thread leitora. Recebe bytes, parseia, empurra dicts na fila com `self._queue.put(msg)`.
- **Consumidor:** `poll()` chamado pela view. Drena com `get_nowait()` num loop.

A `Queue` é o **único** ponto de contato entre as threads. Ela é thread-safe (tem locks internos em `put` e `get`). Regra prática: **thread fala com thread via `queue.Queue`**, sempre. Uma `list` comum **não** é thread-safe.

### 9. `q.get()` vs `q.get_nowait()`

- **`q.get()`** é bloqueante. Se a fila está vazia, para a thread até alguém fazer `put`. Péssimo pro game loop — congelaria o jogo.
- **`q.get_nowait()`** é não bloqueante. Se não tem item, levanta `queue.Empty` imediatamente.

Idioma pra drenar fila sem bloquear:

```python
messages = []
while True:
    try:
        messages.append(self._queue.get_nowait())
    except queue.Empty:
        break
return messages
```

### 10. Daemon thread

`threading.Thread(target=..., daemon=True)`. Marca a thread como "serviço de fundo": quando o programa principal termina, ela é **morta automaticamente**. Sem isso, uma thread em `while True: recv(...)` nunca termina sozinha e o processo Python fica pendurado pra sempre após o fechamento da janela. Threads de rede **sempre** `daemon=True`.

### 11. Framing em TCP (o motivo do buffer)

**TCP é um protocolo de bytes, não de mensagens.** Quando o servidor faz `sendall(b'{"a":1}\n')`, não há garantia nenhuma de como os bytes chegam no `recv()` do outro lado:

1. Mensagem exata: `b'{"a":1}\n'`.
2. Parcial: `b'{"a":'` (resto vem no próximo `recv`).
3. Colada: `b'{"a":1}\n{"b":2}\n'` (duas mensagens).
4. Mistura: `b'{"a":1}\n{"b":'` (uma completa + uma começando).

TCP só garante **ordem** e **entrega**, não **limites de mensagem**. Solução na aplicação: **delimitador + buffer**.

- Acumula tudo que `recv` devolve num buffer de bytes.
- Loop interno: enquanto tiver `\n` no buffer, parte em `(antes, _, depois)` com `buffer.partition(b"\n")`, processa `antes` como mensagem completa, `buffer = depois`.
- Quando não tem mais `\n`, sai do loop interno, volta pro `recv`.

O loop interno drena **todas** as mensagens completas do buffer antes de voltar pro `recv`. O que sobrar (parcial) fica no buffer pro próximo ciclo.

### 12. UDP é orientado a datagramas → sem buffer

Cada `recvfrom()` devolve exatamente **um datagrama**, inteiro, tal como foi enviado. Não existe "parcial", não existe "colado". Então o `_udp_reader` é bem mais simples: só recebe, parseia, enfileira. Sem buffer, sem `partition`, sem loop interno.

`recvfrom` devolve `(data, address)` — desempacotar com `_` pra descartar o endereço se não for usado: `data, _ = sock.recvfrom(1024)`.

### 13. `bind` em UDP no cliente (é só no cliente? não)

Em TCP, `bind` é coisa de servidor. Em UDP, **não existe conexão** — qualquer lado que queira *receber* datagramas precisa estar associado a uma porta local, e isso se faz com `bind`. Então o **cliente** também dá `bind` no socket UDP.

`bind(("", 32350))` — a string vazia significa "todas as interfaces de rede locais" (loopback, WiFi, ethernet, etc.). Equivale a `"0.0.0.0"` em TCP.

### 14. TCP e UDP usam portas **diferentes** por design

No nosso protocolo:
- TCP: porta configurável (default 32348 no servidor)
- UDP: porta **32350 hardcoded** no servidor (`server/udp_server.py:16`)

O `port` que o usuário digita no `MenuView` é **só TCP**. A porta UDP é constante do protocolo — o cliente **obrigatoriamente** dá `bind(("", 32350))`, não no `port` do TCP. Erro comum: reutilizar a mesma variável nos dois.

### 15. `recv()` devolve `b""` quando o peer fecha (não `None`)

Fim normal de vida de um socket TCP. Check correto é `if not data: break` (bytes vazios são falsy). **Nunca** `if data is None` — isso nunca acontece e cria loop infinito consumindo CPU.

### 16. Parar thread bloqueada em `recv()` — fechar o socket

Setar `self._running = False` **sozinho não funciona**. A thread está presa **dentro** do `recv()`, não entre iterações do loop. Ela só checa a flag depois que o `recv` retorna — e se o servidor está quieto, nunca retorna.

Solução: **fechar o socket** no `disconnect()`. O SO sacode a thread bloqueada, `recv` retorna com `b""` ou lança `OSError`. A thread aí volta ao topo do loop, vê `_running = False`, e sai.

Por isso `disconnect()` e tratamento de erro no reader têm que ser desenhados **juntos**. O `disconnect` fecha o socket; o reader precisa de `try/except OSError: break` no `recv` pra não explodir quando isso acontecer.

### 17. `OSError` pega tudo

`ConnectionRefusedError`, `ConnectionResetError`, `BrokenPipeError` — todos subclasses de `OSError` em Python 3. Capturar `OSError` num bloco pega todos de uma vez. Mais qualquer outro erro de rede.

Detalhe: `ConnectionRefusedError` é levantado pelo `connect()` (servidor offline), não pelo `recv()`. Esse **não** deve ser capturado dentro do `NetworkClient` — deixa propagar pra view tratar (mostrar "servidor offline" pro usuário).

### 18. `disconnect()` idempotente

Todas as checagens `if self._tcp_socket is not None` + reset `self._tcp_socket = None` depois de fechar fazem `disconnect()` ser seguro de chamar:

- Antes de `connect()` (sockets ainda são `None`)
- Duas vezes seguidas (segunda chamada é no-op)
- Depois de erro parcial na conexão

### 19. `thread.join(timeout=N)`

Espera a thread realmente morrer, mas com prazo. Sem timeout, se algo der errado e a thread não sair, o `join` trava o programa pra sempre. Com timeout, volta depois de N segundos mesmo que a thread não tenha saído — melhor perder uma thread zumbi do que travar tudo.

### 20. Extrair helper quando vejo código repetido

Quando escrevi `_send(self, message: dict)`, eliminei três cópias idênticas de `json.dumps(...) + "\n"` + `.encode()` + `sendall(...)` nos métodos `connect`, `send_word` e `send_letter`. Se amanhã alguém mudar o delimitador do protocolo, arruma em **um** lugar só.

Convenção: `_` inicial marca método "privado por convenção" em Python. Não é proteção real, é sinal pro leitor: "não chame de fora da classe".
