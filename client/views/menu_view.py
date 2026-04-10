import arcade
import arcade.gui
from .host_view import HostView
from .player_waiting_view import PlayerWaitingView

class MenuView(arcade.View):
    def __init__(self, is_host=True):
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.is_host = is_host 
        
        # Layout central (Elementos principais)
        self.v_box = arcade.gui.UIBoxLayout(space_between=16)

        title = arcade.gui.UILabel(text="HANGMAN", font_size=36, text_color=(0, 93, 164), bold=True)
        self.v_box.add(title)

        subtitle = arcade.gui.UILabel(text="LOBBY DA PARTIDA", font_size=14, text_color=arcade.color.DARK_GRAY)
        self.v_box.add(subtitle)

        # Input Text para inserir código
        self.code_input = arcade.gui.UIInputText(
            width=250, height=40, text="Ex: CODIGO-123", text_color=arcade.color.BLACK
        )
        self.code_input.with_background(color=arcade.color.WHITE)
        self.code_input.with_padding(top=10, right=10, bottom=10, left=10)
        self.v_box.add(self.code_input)

        connect_button = arcade.gui.UIFlatButton(
            text="Conectar", width=250,
            style={
                "normal": {"bg_color": (0, 93, 164), "font_color": arcade.color.WHITE},
                "hover": {"bg_color": (0, 110, 190), "font_color": arcade.color.WHITE},
                "press": {"bg_color": (0, 75, 140), "font_color": arcade.color.WHITE}
            }
        )
        connect_button.on_click = self.on_click_connect
        self.v_box.add(connect_button)

        # Cartão de Jogadores
        self.players_box = arcade.gui.UIBoxLayout(space_between=12)
        mock_players = ["1. Você", "2. Aguardando conexão...", "3. Aguardando conexão..."]
        for player in mock_players:
            self.players_box.add(arcade.gui.UILabel(text=player, font_size=16, text_color=arcade.color.BLACK))

        self.players_box.with_background(color=arcade.color.WHITE)
        self.players_box.with_padding(top=20, right=60, bottom=20, left=60)
        self.v_box.add(self.players_box)

        # Botão Iniciar Partida
        start_button = arcade.gui.UIFlatButton(
            text="Iniciar Partida", width=250,
            style={
                "normal": {"bg_color": (0, 93, 164), "font_color": arcade.color.WHITE},
                "hover": {"bg_color": (0, 110, 190), "font_color": arcade.color.WHITE},
                "press": {"bg_color": (0, 75, 140), "font_color": arcade.color.WHITE}
            }
        )
        start_button.on_click = self.on_click_start
        self.v_box.add(start_button)

        # --- NOVO: BOTÃO DE SAIR (EXIT) ---
        # Botão mais discreto, estilo "Secundário" (Fundo branco/vermelho)
        exit_button = arcade.gui.UIFlatButton(
            text="Sair do Jogo", width=120, height=40,
            style={
                "normal": {"bg_color": arcade.color.WHITE, "font_color": arcade.color.DARK_RED},
                "hover": {"bg_color": arcade.color.LIGHT_GRAY, "font_color": arcade.color.DARK_RED},
                "press": {"bg_color": arcade.color.GRAY, "font_color": arcade.color.DARK_RED}
            }
        )
        exit_button.on_click = self.on_click_exit

        # --- ANCORAGEM MÚLTIPLA ---
        # 1. Ancora os elementos principais no centro
        main_anchor = arcade.gui.UIAnchorLayout()
        main_anchor.add(child=self.v_box, anchor_x="center_x", anchor_y="center_y")
        self.manager.add(main_anchor)

        # 2. Ancora o botão de sair no canto inferior direito
        exit_anchor = arcade.gui.UIAnchorLayout()
        exit_anchor.add(child=exit_button, anchor_x="right", anchor_y="bottom", align_x=-20, align_y=20)
        self.manager.add(exit_anchor)

    def on_show_view(self):
        self.manager.enable()
        arcade.set_background_color((237, 248, 255))

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        self.clear()
        self.manager.draw()

    def on_click_connect(self, event):
        # TODO: FAZER A CONEXÃO VIA REDE E EXIBIR NA TELA
        codigo_inserido = self.code_input.text
        print(f"Tentando estabelecer conexão com o código: {codigo_inserido}")

    def on_click_start(self, event):
        print("Iniciando a partida...")
        if self.is_host:
            self.window.show_view(HostView())
        else:
            self.window.show_view(PlayerWaitingView())

    def on_click_exit(self, event):
        print("Encerrando o jogo...")
        arcade.exit() # Função oficial do Arcade para fechar a aplicação