import arcade
import arcade.gui
# Importando a tela do jogo para fazer a transição
from .game_view import GameView 

class PlayerWaitingView(arcade.View):
    def __init__(self):
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.v_box = arcade.gui.UIBoxLayout(space_between=30)

        title = arcade.gui.UILabel(text="Player View", font_size=28, text_color=arcade.color.BLACK)
        self.v_box.add(title)

        waiting_label = arcade.gui.UILabel(
            text="Aguardando o Host escolher a palavra...",
            font_size=16,
            text_color=arcade.color.DARK_GRAY
        )
        
        # Estilo "Game Card" (Arcade 3.3.3+)
        waiting_label.with_background(color=arcade.color.WHITE)
        waiting_label.with_padding(top=30, right=40, bottom=30, left=40)
        self.v_box.add(waiting_label)

        dots = arcade.gui.UILabel(text="• • •", font_size=24, text_color=(0, 93, 164))
        self.v_box.add(dots)

        anchor = arcade.gui.UIAnchorLayout()
        anchor.add(child=self.v_box, anchor_x="center_x", anchor_y="center_y")
        self.manager.add(anchor)

    def on_show_view(self):
        self.manager.enable()
        arcade.set_background_color((237, 248, 255))

    def on_hide_view(self):
        self.manager.disable()

    # --- LÓGICA DE REDE E TRANSIÇÃO ---
    def on_receive_game_start(self, secret_word_from_server):
        """
        GATILHO DE REDE: 
        Quando o seu protocolo de rede (ex: Socket.IO) receber o evento do servidor 
        informando que a palavra foi escolhida, ele deve invocar este método na view atual.
        """
        print("Sinal do servidor recebido! Transicionando para a partida...")
        
        # Transita os jogadores (adivinhadores) para a GameView
        game_view = GameView(secret_word=secret_word_from_server, is_host=False)
        self.window.show_view(game_view)

    def on_draw(self):
        self.clear()
        self.manager.draw()