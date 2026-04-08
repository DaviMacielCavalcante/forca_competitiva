import arcade
import arcade.gui
from .host_view import HostView
from .player_waiting_view import PlayerWaitingView

class MenuView(arcade.View):
    def __init__(self, is_host=True):
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.is_host = is_host 
        
        # Diminuí um pouco o espaço entre elementos para acomodar a nova seção
        self.v_box = arcade.gui.UIBoxLayout(space_between=16)

        # Título principal (Hierarquia "Voice")
        title = arcade.gui.UILabel(
            text="HANGMAN",
            font_size=36,
            text_color=(0, 93, 164), 
            bold=True
        )
        self.v_box.add(title)

        subtitle = arcade.gui.UILabel(
            text="LOBBY DA PARTIDA",
            font_size=14,
            text_color=arcade.color.DARK_GRAY
        )
        self.v_box.add(subtitle)

        # --- NOVA SEÇÃO: CAMPO DE CÓDIGO DE CONEXÃO ---
        # Input Text para inserir o código do jogador (Scorecard style)
        self.code_input = arcade.gui.UIInputText(
            width=250, height=40, text="Ex: CODIGO-123", text_color=arcade.color.BLACK
        )
        
        # Arcade 3.3.3+: Aplicando o estilo de cartão branco
        self.code_input.with_background(color=arcade.color.WHITE)
        self.code_input.with_padding(top=10, right=10, bottom=10, left=10)
        self.v_box.add(self.code_input)

        # Botão para enviar o código e tentar a conexão
        connect_button = arcade.gui.UIFlatButton(
            text="Conectar",
            width=250,
            style={
                "normal": {
                    "bg_color": (0, 93, 164), 
                    "font_color": arcade.color.WHITE
                },
                "hover": {
                    "bg_color": (0, 110, 190), 
                    "font_color": arcade.color.WHITE
                },
                "press": {
                    "bg_color": (0, 75, 140), 
                    "font_color": arcade.color.WHITE
                }
            }
        )
        connect_button.on_click = self.on_click_connect
        self.v_box.add(connect_button)

        # --- CARTÃO DA LISTA DE JOGADORES (Game Cards) ---
        self.players_box = arcade.gui.UIBoxLayout(space_between=12)
        mock_players = ["1. Você", "2. Aguardando conexão...", "3. Aguardando conexão..."]
        
        for player in mock_players:
            self.players_box.add(
                arcade.gui.UILabel(text=player, font_size=16, text_color=arcade.color.BLACK)
            )

        self.players_box.with_background(color=arcade.color.WHITE)
        self.players_box.with_padding(top=20, right=60, bottom=20, left=60)
        self.v_box.add(self.players_box)

        # --- BOTÃO INICIAR PARTIDA ---
        start_button = arcade.gui.UIFlatButton(
            text="Iniciar Partida",
            width=250,
            style={
                "normal": {
                    "bg_color": (0, 93, 164), 
                    "font_color": arcade.color.WHITE
                },
                "hover": {
                    "bg_color": (0, 110, 190), 
                    "font_color": arcade.color.WHITE
                },
                "press": {
                    "bg_color": (0, 75, 140), 
                    "font_color": arcade.color.WHITE
                }
            }
        )
        start_button.on_click = self.on_click_start
        self.v_box.add(start_button)

        # Arcade 3.3.3+: Substituição do antigo UIAnchorWidget por UIAnchorLayout
        anchor = arcade.gui.UIAnchorLayout()
        anchor.add(child=self.v_box, anchor_x="center_x", anchor_y="center_y")
        self.manager.add(anchor)

    def on_show_view(self):
        self.manager.enable()
        # Regra "The Table" (Mesa do tabuleiro)
        arcade.set_background_color((237, 248, 255))

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        self.clear()
        self.manager.draw()

    # --- LÓGICA DE CONEXÃO E TRANSIÇÃO ---
    def on_click_connect(self, event):
        """
        Esta função captura o código inserido no campo de texto
        para validar e estabelecer a conexão P2P / WebSocket.
        """
        codigo_inserido = self.code_input.text
        print(f"Tentando estabelecer conexão com o código: {codigo_inserido}")
        # TODO: Injetar a lógica de sockets aqui para trocar dados com os outros clientes

    def on_click_start(self, event):
        print("Iniciando a partida...")
        if self.is_host:
            self.window.show_view(HostView())
        else:
            self.window.show_view(PlayerWaitingView())