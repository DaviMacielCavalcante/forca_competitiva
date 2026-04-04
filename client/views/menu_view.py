import arcade
import arcade.gui

class MenuView(arcade.View):
    def __init__(self):
        super().__init__()
        
        # Gerenciador de interface 
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Cores (R, G, B, A)
        self.color_surface = (237, 248, 255, 255)          # Background
        self.color_primary = (0, 93, 164, 255)            # Cor primária
        self.color_card    = (255, 255, 255, 255)         # Cards/Containers
        self.color_input   = (209, 232, 247, 255)         # Cor de Contraste
        self.color_text_sec = (128, 128, 128, 255)        # Textos

        self.setup_ui()

    def setup_ui(self):
        """Monta a interface seguindo o layout 'Digital Board Game'."""
        
        # Layout vertical para centralizar os cards de Host e Join
        self.v_box = arcade.gui.UIBoxLayout(space_between=30)

        # Título
        title = arcade.gui.UILabel(
            text="HANGMAN",
            font_size=28,
            text_color=self.color_primary,
            bold=True
        )
        self.v_box.add(title.with_padding(bottom=20))

        # Estilo de Botões
        btn_style = {
            "normal": arcade.gui.UIFlatButton.UIStyle(
                font_color=(255, 255, 255, 255),
                bg=self.color_primary,
            ),
            "hover": arcade.gui.UIFlatButton.UIStyle(
                font_color=(255, 255, 255, 255),
                bg=(0, 115, 200, 255),
            ),
            "press": arcade.gui.UIFlatButton.UIStyle(
                font_color=(255, 255, 255, 255),
                bg=(0, 70, 130, 255),
            ),
            "disabled": arcade.gui.UIFlatButton.UIStyle(
                font_color=self.color_text_sec,
                bg=(200, 200, 200, 255),
            )
        }

        # Card de Host
        host_box = arcade.gui.UIBoxLayout(space_between=8, align="left")
        host_box.add(arcade.gui.UILabel(text="HOST A SESSION", font_size=10, text_color=self.color_text_sec))
        host_box.add(arcade.gui.UILabel(text="Create Group", font_size=20, text_color=self.color_primary, bold=True))
        
        # Botão de Host
        self.host_button = arcade.gui.UIFlatButton(
            text="Generate Room Code",
            width=320,
            style=btn_style
        )
        self.host_button.on_click = self.on_host_click
        
        # Adiciona o botão com um espaçamento no topo
        host_box.add(self.host_button.with_padding(top=10))
        
        host_card = host_box.with_padding(all=25).with_background(color=self.color_card)
        self.v_box.add(host_card)

        # Card de Join
        join_box = arcade.gui.UIBoxLayout(space_between=12, align="left")
        join_box.add(arcade.gui.UILabel(text="ENTER ARENA", font_size=10, text_color=self.color_text_sec))
        join_box.add(arcade.gui.UILabel(text="Join Group", font_size=20, text_color=(0, 0, 0, 255), bold=True))
        
        # Input
        self.code_input = arcade.gui.UIInputText(
            width=320,
            height=45,
            text="", # Deixei vazio inicialmente para ficar mais limpo
            text_color=(60, 60, 60, 255)
        )
        input_bg = self.code_input.with_padding(all=10).with_background(color=self.color_input)
        join_box.add(input_container := input_bg)

        # Botão Join
        join_button = arcade.gui.UIFlatButton(
            text="Join Game →",
            width=340,
            style=btn_style
        )
        join_button.on_click = self.on_join_click
        join_box.add(join_button)

        join_card = join_box.with_padding(all=25).with_background(color=self.color_card)
        self.v_box.add(join_card)

        # Ancoragem do layout
        anchor_layout = arcade.gui.UIAnchorLayout()
        anchor_layout.add(
            child=self.v_box,
            anchor_x="center_x",
            anchor_y="center_y"
        )
        self.manager.add(anchor_layout)

    def on_host_click(self, event):
        """Lógica disparada ao clicar em 'Generate Room Code'."""
        print("Enviando pacote TCP solicitando criação de sala...")
        
        # TODO Futuro: Aqui você vai enviar o pacote pro servidor e aguardar.
        # Por enquanto, simulamos a resposta bem-sucedida do servidor:
        codigo_recebido = "GX-892"
        
        # Atualizamos a interface para mostrar o código gerado
        self.host_button.text = f"CODE: {codigo_recebido}"
        
        # Removemos a função de clique para evitar que o usuário crie várias salas
        self.host_button.on_click = lambda e: None
        
        print(f"Sala criada com sucesso. Aguardando jogadores em: {codigo_recebido}")

    def on_join_click(self, event):
        """Lógica disparada ao clicar em 'Join Game'."""
        codigo = self.code_input.text.strip()
        if codigo:
            print(f"Enviando pacote TCP solicitando entrada na sala: {codigo}")
        else:
            print("Por favor, digite um código de sala válido.")

    def on_draw(self):
        self.clear()
        self.manager.draw()

    def on_show_view(self):
        """Define a cor base da 'mesa' do jogo."""
        arcade.set_background_color(self.color_surface)