import arcade
import arcade.gui
from .game_view import GameView 
from .podium_view import PodiumView # Vamos usar no futuro para a última rodada

class PlayerWaitingView(arcade.View):
    def __init__(self, network, current_round=1, total_rounds=0, scores={}):
        super().__init__()
        self.network = network
        self.manager = arcade.gui.UIManager()
        
        # Estados da partida recebidos pela transição
        self.scores = scores
        self.current_round = current_round
        self.total_rounds = total_rounds

        self.v_box = arcade.gui.UIBoxLayout(space_between=30)

        # Cabeçalho da tela
        title = arcade.gui.UILabel(
            text=f"Scores Rodada {self.current_round - 1}", 
            font_size=28, 
            text_color=(0, 93, 164), 
            bold=True
        )
        self.v_box.add(title)

        # --- TABELA DE PONTUAÇÕES (O Scorecard) ---
        self.scoreboard_box = arcade.gui.UIBoxLayout(space_between=16) # Espaçamento vertical substitui as linhas [3]
        
        # Título da Tabela
        self.scoreboard_box.add(
            arcade.gui.UILabel(text="PLACAR ATUAL", font_size=18, text_color=arcade.color.BLACK, bold=True)
        )

        # Preenchendo as linhas da tabela dinamicamente
        for player, score in self.scores.items():
            # Linha horizontal para Nome e Pontuação
            row = arcade.gui.UIBoxLayout(vertical=False, space_between=80)
            row.add(arcade.gui.UILabel(text=player, font_size=16, text_color=arcade.color.DARK_GRAY))
            row.add(arcade.gui.UILabel(text=f"{score} pts", font_size=16, text_color=(0, 93, 164), bold=True))
            self.scoreboard_box.add(row)

        # Regra do "Game Card": Fundo branco cobrindo toda a tabela [2]
        self.scoreboard_box.with_background(color=arcade.color.WHITE)
        self.scoreboard_box.with_padding(top=20, right=40, bottom=20, left=40)
        self.v_box.add(self.scoreboard_box)

        # --- AVISO DE ESPERA ---
        waiting_label = arcade.gui.UILabel(
            text="Aguardando o Host da próxima rodada escolher a palavra...",
            font_size=14,
            text_color=arcade.color.DARK_GRAY
        )
        self.v_box.add(waiting_label)

        dots = arcade.gui.UILabel(text="• • •", font_size=24, text_color=(0, 93, 164))
        self.v_box.add(dots)

        # Ancoragem centralizada
        anchor = arcade.gui.UIAnchorLayout()
        anchor.add(child=self.v_box, anchor_x="center_x", anchor_y="center_y")
        self.manager.add(anchor)
        
    def on_update(self, delta_time):
        
        messages_list = self.network.poll()
        
        for msg in messages_list:
            ## Caso o player se torne o host, transiciona
                
            if msg.get("acao") == "voce_e_o_host":
                from .host_view import HostView
                
                host_view = HostView(network=self.network)
                self.window.show_view(host_view)
            
            if "revealed_letters" in msg:
                
                word = "".join(
                    letter for letter in msg["revealed_letters"]
                )
                
                self.on_receive_game_start(secret_word_from_server=word)

    def on_show_view(self):
        self.manager.enable()
        # Regra "The Table"
        arcade.set_background_color((237, 248, 255))

    def on_hide_view(self):
        self.manager.disable()

    # --- LÓGICA DE REDE E TRANSIÇÃO ---
    def on_receive_game_start(self, secret_word_from_server):
        print("Sinal do servidor recebido! Iniciando a próxima rodada...")
        # Incrementa a rodada e repassa o placar atualizado para a próxima tela do jogo
        game_view = GameView(
            secret_word=secret_word_from_server, 
            is_host=False, 
            scores=self.scores,
            current_round=self.current_round + 1,
            total_rounds=self.total_rounds,
            network=self.network
        )
        self.window.show_view(game_view)

    def on_draw(self):
        self.clear()
        self.manager.draw()