import arcade
import arcade.gui
from .host_view import HostView
from .player_waiting_view import PlayerWaitingView
from ..network import NetworkClient

class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.is_host = False
        
        # Layout central (Elementos principais)
        self.v_box = arcade.gui.UIBoxLayout(space_between=16)

        title = arcade.gui.UILabel(text="HANGMAN", font_size=36, text_color=(0, 93, 164), bold=True)
        self.v_box.add(title)

        subtitle = arcade.gui.UILabel(text="LOBBY DA PARTIDA", font_size=14, text_color=arcade.color.DARK_GRAY)
        self.v_box.add(subtitle)

        # Input Text para inserir código
    
        self.nome_input = arcade.gui.UIInputText(
            width=250, height=40, text="Digite o seu nome", text_color=arcade.color.BLACK
        )

        self.nome_input.with_background(color=arcade.color.WHITE)
        self.nome_input.with_padding(top=10, right=10, bottom=10, left=10)
        self.v_box.add(self.nome_input)

        self.host_input = arcade.gui.UIInputText(
            width=250, height=40, text="Digite o endereço e porta do host", text_color=arcade.color.BLACK
        )

        self.host_input.with_background(color=arcade.color.WHITE)
        self.host_input.with_padding(top=10, right=10, bottom=10, left=10)
        self.v_box.add(self.host_input)

        self.connect_button = arcade.gui.UIFlatButton(
            text="Conectar", width=250,
            style={
                "normal": {"bg_color": (0, 93, 164), "font_color": arcade.color.WHITE},
                "hover": {"bg_color": (0, 110, 190), "font_color": arcade.color.WHITE},
                "press": {"bg_color": (0, 75, 140), "font_color": arcade.color.WHITE},
                "disabled": {"bg_color": arcade.color.GRAY, "font_color": arcade.color.LIGHT_GRAY}
            }
        )
        self.connect_button.on_click = self.on_click_connect
        self.v_box.add(self.connect_button)

        # Cartão de Jogadores
        self.players_box = arcade.gui.UIBoxLayout(space_between=12)
        mock_players = ["1. Você", "2. Aguardando conexão...", "3. Aguardando conexão..."]
        for player in mock_players:
            self.players_box.add(arcade.gui.UILabel(text=player, font_size=16, text_color=arcade.color.BLACK))

        self.players_box.with_background(color=arcade.color.WHITE)
        self.players_box.with_padding(top=20, right=60, bottom=20, left=60)
        self.v_box.add(self.players_box)

        # Botão Iniciar Partida
        self.start_button = arcade.gui.UIFlatButton(
            text="Iniciar Partida", width=250,
            style={
                "normal": {"bg_color": (0, 93, 164), "font_color": arcade.color.WHITE},
                "hover": {"bg_color": (0, 110, 190), "font_color": arcade.color.WHITE},
                "press": {"bg_color": (0, 75, 140), "font_color": arcade.color.WHITE}
            }
        )
        self.start_button.on_click = self.on_click_start
        self.v_box.add(self.start_button)
        self.start_button.visible = False

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

    def on_update(self, delta_time):
        if self.window.network is None:
            return

        for msg in self.window.network.poll():
            if isinstance(msg, list):
                # lista de jogadores do lobby
                self.players_box.clear()
                for i, player in enumerate(msg, start=1):
                    label = arcade.gui.UILabel(
                        text=f"{i}. {player['nome']}",
                        font_size=16,
                        text_color=arcade.color.BLACK
                    )
                    self.players_box.add(label)

            elif isinstance(msg, dict) and msg.get("acao") == "voce_e_o_host":
                self.is_host = True
                self.start_button.visible = True
                
            elif isinstance(msg, dict) and msg.get("acao") == "partida_iniciada":
                self.window.show_view(PlayerWaitingView(network=self.window.network, scores={}))

    def on_click_connect(self, event):
        nome = self.nome_input.text.strip()
        host_str = self.host_input.text.strip()

        if not nome or not host_str:
            print("Nome e host não podem estar vazios.")
            return

        try:
            host, port_str = host_str.split(":")
            port = int(port_str)
        except ValueError:
            print("Host inválido. Use o formato 127.0.0.1:32348")
            return

        self.window.network = NetworkClient()
        self.window.network.connect(host, port, nome)
        self.connect_button.disabled = True

    def on_click_start(self, event):
        print("Iniciando a partida...")
        if self.is_host:
            self.window.show_view(HostView(self.window.network))
        else:
            self.window.show_view(PlayerWaitingView())

    def on_click_exit(self, event):
        print("Encerrando o jogo...")
        arcade.exit() # Função oficial do Arcade para fechar a aplicação