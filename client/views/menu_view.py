import arcade
import arcade.gui
from .host_view import HostView
from .player_waiting_view import PlayerWaitingView

class MenuView(arcade.View):
    def __init__(self, is_host=True):
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.is_host = is_host 
        
        self.v_box = arcade.gui.UIBoxLayout(space_between=24)

        # Título principal
        title = arcade.gui.UILabel(
            text="HANGMAN",
            font_size=36,
            text_color=(0, 93, 164), # Azul primário
            bold=True
        )
        self.v_box.add(title)

        subtitle = arcade.gui.UILabel(
            text="LOBBY DA PARTIDA",
            font_size=14,
            text_color=arcade.color.DARK_GRAY
        )
        self.v_box.add(subtitle)

        # Container da Lista de jogadores 
        self.players_box = arcade.gui.UIBoxLayout(space_between=12)
        mock_players = ["1. Você", "2. Aguardando conexão...", "3. Aguardando conexão..."]
        
        for player in mock_players:
            self.players_box.add(
                arcade.gui.UILabel(text=player, font_size=16, text_color=arcade.color.BLACK)
            )

        # Arcade 3.3.3+: Aplicando os estilos de "Game Card" branco sem usar UIBorder/UIPadding
        self.players_box.with_background(color=arcade.color.WHITE)
        self.players_box.with_padding(top=30, right=60, bottom=30, left=60)
        self.v_box.add(self.players_box)

        # Botão Iniciar Partida (Primary Button)
        # Botão Iniciar Partida (Primary Button)
        start_button = arcade.gui.UIFlatButton(
            text="Iniciar Partida",
            width=250,
            style={
                "normal": {
                    "bg_color": (0, 93, 164),       # Cor primária
                    "font_color": arcade.color.WHITE
                },
                "hover": {                          # <-- Alterado de "hovered" para "hover"
                    "bg_color": (0, 110, 190),      
                    "font_color": arcade.color.WHITE
                },
                "press": {                          # <-- Alterado de "pressed" para "press"
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
        # Regra "The Table"
        arcade.set_background_color((237, 248, 255))

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        self.clear()
        self.manager.draw()

    def on_click_start(self, event):
        print("Iniciando a partida...")
        if self.is_host:
            self.window.show_view(HostView())
        else:
            self.window.show_view(PlayerWaitingView())