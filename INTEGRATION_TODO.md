# Integração Cliente ↔ Servidor — TO-DO

Documento de trabalho para conectar as views em [client/views/](client/views/) com o backend TCP/UDP em [server/](server/), [lobby/](lobby/) e [game/](game/).

## Decisões já tomadas

- **Host/porta**: configuráveis pelo usuário na tela de menu (sem valor fixo no código).
- **Botão "Iniciar Partida"**: permanece, mas fica **visível apenas para o jogador marcado como host** pelo servidor.
- **Placar agregado**: fora do escopo desta integração — será tratado depois.
- **Identificação do autor do acerto**: fora do escopo desta integração — será feito via broadcast depois.

## Divisão de responsabilidades

| Dev | Arquivos | Escopo |
| --- | --- | --- |
| **Davi** | `client/network.py`, `client/main.py` | Fundação de rede + bootstrap da janela |
| **João Miguel** | `client/views/menu_view.py`, `client/views/host_view.py` | Fluxo de entrada (lobby + escolha da palavra) |
| **Pablo Vinicíus** | `client/views/game_view.py`, `client/views/player_waiting_view.py`, `client/views/podium_view.py` | Fluxo de jogo (partida + espera entre rodadas + pódio) |

### Como trabalhar em paralelo sem se bloquear

Todas as views dependem do `NetworkClient`, então **Davi faz primeiro a Fase 0** (ver abaixo): commita um stub de `client/network.py` com a API pública fixada (assinaturas + `pass`) e um `FakeNetworkClient` que devolve mensagens pré-programadas via `poll()`. Com isso João Miguel e Pablo conseguem desenvolver e testar suas views contra o `FakeNetworkClient` sem esperar a implementação real de sockets/threads.

#### Fase 0 — Contrato do `NetworkClient` (Davi, primeiro commit)

- [x] Criar `client/network.py` com:
  - [x] Classe `NetworkClient` contendo as assinaturas (`connect`, `send_word`, `send_letter`, `poll`, `disconnect`) com corpo `pass`/`return []`.
  - [x] Classe `FakeNetworkClient` com a mesma interface, mas que permite enfileirar mensagens manualmente (ex.: `fake.inject({"acao": "voce_e_o_host"})`) para que as views sejam testadas sem servidor rodando.
- [x] Abrir PR/branch curta só com esse stub para destravar os outros dois devs.

Depois da Fase 0, os três podem trabalhar em branches independentes.

## Protocolo atual (referência)

Mensagens são JSON delimitadas por `\n`.

**Cliente → Servidor (TCP):**
- `{"acao": "entrar", "nome": "<nome>"}`
- `{"acao": "palavra", "palavra": "<palavra>"}`
- `{"acao": "letra", "letra": "<letra>"}`

**Servidor → Cliente (TCP):**
- Ack: `{"status": "ok"}`
- Lobby (lista): `[{"id": "...", "nome": "..."}, ...]`
- Host: `{"acao": "voce_e_o_host"}`
- Estado do jogo: `{"revealed_letters": [...], "correct": bool, "remaining_attempts": int, "score": int?}`
- Fim de rodada: `{"acao": "game_over_word_guessed" | "game_over_attempts_exhausted", ...}`

**Servidor → Cliente (UDP, porta 32350):**
- `{"tempo": <segundos>}`

## Tarefas

### 1. Módulo de rede do cliente — `client/network.py` — **@Davi**

- [x] Criar classe `NetworkClient` com:
  - [x] Socket TCP + thread leitora que faz parse delimitado por `\n` e enfileira dicts numa `queue.Queue` thread-safe.
  - [x] Socket UDP escutando na porta 32350, também enfileirando `{"tempo": N}`.
  - [x] Método `connect(host: str, port: int, name: str)` — abre TCP, inicia threads, envia `{"acao": "entrar", "nome": ...}`.
  - [x] Método `send_word(word: str)` — envia `{"acao": "palavra", "palavra": word}`.
  - [x] Método `send_letter(letter: str)` — envia `{"acao": "letra", "letra": letter}`.
  - [x] Método `poll() -> list[dict]` — drena a fila sem bloquear (para ser chamado em `on_update`).
  - [x] Método `disconnect()` — fecha sockets e encerra threads.
- [x] Tratar `ConnectionRefusedError` / `ConnectionResetError` / JSON inválido sem derrubar a thread.
- [ ] Guardar a instância em `window.network` para ser compartilhada entre as views.

### 2. `MenuView` — [client/views/menu_view.py](client/views/menu_view.py) — **@João Miguel**

- [x] Substituir o campo "CÓDIGO-123" por **dois inputs**: `Nome` e `Host` (ex.: `127.0.0.1:32348`).
- [x] No `on_click_connect`:
  - [x] Validar nome não vazio e parsear `host:port`.
  - [x] Instanciar `NetworkClient` e chamar `connect(...)`; guardar em `self.window.network`.
  - [x] Desabilitar o botão "Conectar" após sucesso.
- [x] Implementar `on_update`:
  - [x] Drenar `window.network.poll()`.
  - [x] Ao receber lista de lobby, **substituir** o mock `mock_players` por labels dinâmicos reais (reconstruir `players_box`).
  - [x] Ao receber `{"acao": "voce_e_o_host"}`, marcar `self.is_host = True` e **mostrar** o botão "Iniciar Partida"; caso contrário mantê-lo oculto.
- [x] `on_click_start` (só aparece pro host): transicionar para `HostView` passando `self.window.network`.
- [x] Tratamento do botão "Iniciar Partida":
  - [x] Visível apenas quando `self.is_host` for `True` (esconder via `v_box` condicional ou remover/readicionar).

### 3. `HostView` — [client/views/host_view.py](client/views/host_view.py) — **@João Miguel**

- [x] Receber `network` no `__init__` (`HostView(network)`).
- [x] `on_click_submit`: chamar `self.network.send_word(word)` em vez de só mudar de view localmente.
- [x] Após enviar, transicionar para `GameView(secret_word=word, is_host=True, network=self.network)`.

### 4. `GameView` — [client/views/game_view.py](client/views/game_view.py) — **@Pablo Vinicíus**

- [ ] Receber `network` no `__init__`.
- [ ] `on_guess_submit`: chamar `self.network.send_letter(guess)` — remover lógica local de acerto.
- [ ] `on_update`:
  - [ ] Drenar `self.network.poll()`.
  - [ ] Para cada mensagem:
    - [ ] `revealed_letters` → atualizar `self.guessed_letters` a partir das posições preenchidas e chamar `build_word_display()`.
    - [ ] `remaining_attempts` → atualizar `self.attempts_left` e `update_interface_text()`.
    - [ ] `score` → acumular em `self.scores["1. Você"]` (placeholder até o broadcast real).
    - [ ] `tempo` (UDP) → atualizar `self.time_left` em vez do decremento local.
    - [ ] `acao == "game_over_word_guessed"` ou `"game_over_attempts_exhausted"` → `self.is_game_over = True`; chamar `handle_round_transition()`.
- [ ] Remover o decremento local `self.time_left -= delta_time` (o timer agora vem do UDP).
- [ ] `handle_round_transition`: passar `self.network` para `HostView`/`PlayerWaitingView`/`PodiumView`.

### 5. `PlayerWaitingView` — [client/views/player_waiting_view.py](client/views/player_waiting_view.py) — **@Pablo Vinicíus**

- [ ] Receber `network` no `__init__`.
- [ ] Implementar `on_update`:
  - [ ] Drenar `self.network.poll()`.
  - [ ] `{"acao": "voce_e_o_host"}` → transicionar para `HostView(self.network)`.
  - [ ] `revealed_letters` recebido → rodada começou; transicionar para `GameView(is_host=False, network=self.network, ...)` (passando a palavra reconstruída a partir das letras reveladas + `_`).

### 6. `PodiumView` — [client/views/podium_view.py](client/views/podium_view.py) — **@Pablo Vinicíus**

- [ ] Receber `network` opcional (só precisa se houver "jogar de novo" — fora de escopo agora).
- [ ] No botão "Back to Menu", chamar `network.disconnect()` antes de voltar pro `MenuView()`.

### 7. `client/main.py` — **@Davi**

- [x] Inicializar `window.network = None` antes de mostrar a `MenuView`.
- [x] Remover `sys.path.append('../client/views')` (e o `import sys` que ficou órfão). Motivo: caminhos relativos são resolvidos a partir do **cwd** em que o `python` foi invocado, não do diretório do script — então `'../client/views'` apontava pra fora do repositório e nem existia. Mesmo assim a importação `from views.menu_view import MenuView` funcionava, porque quando se roda `python client/main.py` a partir do repo root, o Python já adiciona automaticamente o diretório do script (`client/`) em `sys.path[0]`, e `client/views/` é um pacote (tem `__init__.py`). O `append` era gambiarra inútil: não fazia diferença nenhuma e ainda poluía o `sys.path` com um caminho inexistente.

## Pontos em aberto (pós-integração)

- Broadcast de placar agregado do servidor para os clientes.
- Identificação do autor de cada acerto (incluir `player_id`/`nome` em `broadcast_game_state`).
- Fluxo de reconexão/queda do servidor.
- Mensagem de "partida terminada" para ir ao `PodiumView` (hoje o servidor não envia nada específico para fim de partida, só fim de rodada).
