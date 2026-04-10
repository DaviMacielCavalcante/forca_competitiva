import arcade
import arcade.gui
# Importações necessárias para as transições circulares
from .host_view import HostView
from .podium_view import PodiumView 

class GameView(arcade.View):
    def __init__(self, secret_word="PALAVRA", is_host=True, scores=None, current_round=1, total_rounds=4):
        super().__init__()
        self.manager = arcade.gui.UIManager()
        
        # --- ESTADOS DA PARTIDA E DA REDE ---
        self.secret_word = secret_word.upper()
        self.is_host = is_host
        
        # Gestão de Rodadas e Pontos
        self.current_round = current_round
        self.total_rounds = total_rounds
        self.scores = scores if scores is not None else {"1. Você": 0, "2. Jogador B": 0, "3. Jogador C": 0}

        self.attempts_left = 3
        self.time_left = 60.0
        self.guessed_letters = set()
        self.is_game_over = False

        # --- LAYOUT PRINCIPAL ---
        self.v_box = arcade.gui.UIBoxLayout(space_between=20)

        # 1. Cabeçalho
        self.status_box = arcade.gui.UIBoxLayout(vertical=False, space_between=40)
        
        # Indicador de Rodada e Timer
        self.round_label = arcade.gui.UILabel(
            text=f"Rodada {self.current_round}/{self.total_rounds}", font_size=18, text_color=arcade.color.BLACK
        )
        self.status_box.add(self.round_label)

        self.timer_label = arcade.gui.UILabel(
            text=f"Tempo: {int(self.time_left)}s", font_size=18, text_color=(0, 93, 164), bold=True
        )
        self.status_box.add(self.timer_label)
        
        if not self.is_host:
            self.attempts_label = arcade.gui.UILabel(
                text=f"Tentativas: {self.attempts_left}/3", font_size=18, text_color=arcade.color.DARK_RED
            )
            self.status_box.add(self.attempts_label)
        
        self.v_box.add(self.status_box)

        # 2. Tela da Forca (Tiles)
        self.word_box = arcade.gui.UIBoxLayout(vertical=False, space_between=8)
        self.build_word_display()
        self.v_box.add(self.word_box)

        # 3. Interação do Jogador ou Host
        if not self.is_host:
            self.input_box = arcade.gui.UIBoxLayout(space_between=10)
            self.guess_input = arcade.gui.UIInputText(
                width=200, height=40, text="Letra ou Palavra", text_color=arcade.color.BLACK
            )
            self.guess_input.with_background(color=arcade.color.WHITE)
            self.guess_input.with_padding(top=10, right=10, bottom=10, left=10)
            self.input_box.add(self.guess_input)

            self.guess_button = arcade.gui.UIFlatButton(
                text="Tentar Sorte", width=200,
                style={
                    "normal": {"bg_color": (0, 93, 164), "font_color": arcade.color.WHITE},
                    "hover": {"bg_color": (0, 110, 190), "font_color": arcade.color.WHITE},
                    "press": {"bg_color": (0, 75, 140), "font_color": arcade.color.WHITE}
                }
            )
            self.guess_button.on_click = self.on_guess_submit
            self.input_box.add(self.guess_button)
            self.v_box.add(self.input_box)
        else:
            host_msg = arcade.gui.UILabel(text="Você é o Host. Acompanhe os jogadores!", font_size=14, text_color=arcade.color.DARK_GRAY)
            self.v_box.add(host_msg.with_background(color=arcade.color.WHITE).with_padding(top=10, right=20, bottom=10, left=20))

        anchor = arcade.gui.UIAnchorLayout()
        anchor.add(child=self.v_box, anchor_x="center_x", anchor_y="center_y")
        self.manager.add(anchor)

    # (Métodos build_word_display, update_interface_text e on_guess_submit permanecem iguais a versão anterior)
    def build_word_display(self):
        self.word_box.clear()
        for char in self.secret_word:
            if char in self.guessed_letters:
                lbl = arcade.gui.UILabel(text=char, font_size=24, text_color=arcade.color.WHITE, bold=True)
                tile = lbl.with_background(color=(0, 93, 164)).with_padding(top=15, right=20, bottom=15, left=20)
            else:
                lbl = arcade.gui.UILabel(text="_", font_size=24, text_color=arcade.color.BLACK, bold=True)
                tile = lbl.with_background(color=arcade.color.WHITE).with_padding(top=15, right=20, bottom=15, left=20)
            self.word_box.add(tile)

    def update_interface_text(self):
        self.timer_label.text = f"Tempo: {int(self.time_left)}s"
        if not self.is_host:
            self.attempts_label.text = f"Tentativas: {self.attempts_left}/3"

    def on_guess_submit(self, event):
        # Lógica resumida (idêntica ao passo anterior)
        if self.attempts_left <= 0 or self.is_game_over: return
        guess = self.guess_input.text.strip().upper()
        if not guess: return
        print(f"Tentativa: {guess}")
        
    def on_show_view(self):
        self.manager.enable()
        arcade.set_background_color((237, 248, 255))

    def on_hide_view(self):
        self.manager.disable()

    def on_update(self, delta_time):
        """Loop local de update"""
        if self.is_game_over:
            return

        self.time_left -= delta_time
        self.update_interface_text()

        # Condição de fim de rodada
        if self.time_left <= 0:
            self.time_left = 0
            self.is_game_over = True
            print("O tempo acabou! Avaliando para onde ir...")
            self.handle_round_transition()

    def handle_round_transition(self):
        """
        Lógica central estratégica:
        Define para qual tela o jogador vai após a rodada acabar.
        """
        # 1. Verifica se foi a última rodada da partida
        if self.current_round >= self.total_rounds:
            print("Partida finalizada! Movendo para o Podium View...")
            # Quando criar o podium_view, ative esta linha:
            # self.window.show_view(PodiumView(scores=self.scores))
            return
            
        # 2. Se a partida continua, o sistema de rede deve dizer quem é o próximo Host.
        # Aqui, simularemos uma variável que virá da sua rede:
        i_am_next_host = False # TODO: Substitua por validação real via WebSockets
    
        from .player_waiting_view import PlayerWaitingView
        
        if i_am_next_host:
            # Sou o próximo a escolher a palavra, não vejo as pontuações e vou escrever
            self.window.show_view(HostView())
        else:
            # Sou jogador novamente, fico aguardando e avalio como estão meus pontos
            # Passo meu dicionário de scores, rodada atual e o total pra tela de espera exibir
            self.window.show_view(PlayerWaitingView(
                scores=self.scores,
                current_round=self.current_round,
                total_rounds=self.total_rounds
            ))

    def on_draw(self):
        self.clear()
        self.manager.draw()