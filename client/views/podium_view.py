import arcade
import arcade.gui

class PodiumView(arcade.View):
    def __init__(self, scores=None):
        super().__init__()
        self.manager = arcade.gui.UIManager()
        
        # Recebe os pontos da partida (ou gera dados falsos para teste)
        self.scores = scores if scores is not None else {
            "1. Você": 2100, 
            "2. Alex Rivera": 1450, 
            "3. Casey Chen": 980, 
            "4. Jogador D": 500,
            "5. Jogador E": 100
        }

        # Ordena os jogadores por pontuação (do maior para o menor)
        self.sorted_players = sorted(self.scores.items(), key=lambda item: item[1], reverse=True)
        print(self.sorted_players)

        # Layout Vertical principal
        self.v_box = arcade.gui.UIBoxLayout(space_between=30)

        # Título Principal
        title = arcade.gui.UILabel(
            text="FINAL RANKINGS",
            font_size=36,
            text_color=(0, 93, 164), # Azul Primário
            bold=True
        )
        self.v_box.add(title)

        # --- CONSTRUINDO O PÓDIO (TOP 3) ---
        self.podium_box = arcade.gui.UIBoxLayout(vertical=False, space_between=15)

        podium_order = []
        
        # Correção: Adicionando os índices específicos [1],  e [2] para pegar apenas a tupla do jogador
        if len(self.sorted_players) > 1: 
            podium_order.append((2, self.sorted_players[1])) # 2º Lugar
        if len(self.sorted_players) > 0: 
            podium_order.append((1, self.sorted_players[0])) # 1º Lugar
        if len(self.sorted_players) > 2: 
            podium_order.append((3, self.sorted_players[2])) # 3º Lugar

        print(podium_order)

        # Agora a iteração receberá exatamente: (Posição, ("Nome", Pontuação))
        for position, (player_name, score) in podium_order:
            
            # 1. Primeiro definimos as variáveis de cor e tamanho do cartão com base na posição
            if position == 1:
                # 1º Lugar: Azul primário, Texto Branco
                c_pos = arcade.color.WHITE
                c_name = arcade.color.WHITE
                c_score = arcade.color.WHITE
                bg_color = (0, 93, 164)
                pad_v = 60
                pad_h = 40
            else:
                # 2º e 3º Lugares: Cartões Brancos, Texto Escuro/Azul
                c_pos = (0, 93, 164)
                c_name = arcade.color.BLACK
                c_score = (0, 93, 164)
                bg_color = arcade.color.WHITE
                pad_v = 30
                pad_h = 30

            # 2. Criamos o cartão
            card = arcade.gui.UIBoxLayout(space_between=10)
            
            # 3. Criamos os labels PASSANDO AS CORES CORRETAS DIRETAMENTE NA CRIAÇÃO (text_color)
            pos_label = arcade.gui.UILabel(text=f"{position}º", font_size=20, bold=True, text_color=c_pos)
            name_label = arcade.gui.UILabel(text=player_name, font_size=16, text_color=c_name)
            score_label = arcade.gui.UILabel(text=f"{score} PTS", font_size=14, text_color=c_score)
            
            # Adiciona os textos ao cartão
            card.add(pos_label)
            card.add(name_label)
            card.add(score_label)

            # 4. Aplica a estilização "Game Card" em volta do bloco todo
            styled_card = card.with_background(color=bg_color).with_padding(top=pad_v, bottom=pad_v, left=pad_h, right=pad_h)

            self.podium_box.add(styled_card)

        self.v_box.add(self.podium_box)

        # --- LISTA DOS DEMAIS JOGADORES (4º em diante) ---
        if len(self.sorted_players) > 3:
            others_box = arcade.gui.UIBoxLayout(space_between=5)
            for i in range(3, len(self.sorted_players)):
                player_name, score = self.sorted_players[i]
                row = arcade.gui.UIBoxLayout(vertical=False, space_between=60)
                row.add(arcade.gui.UILabel(text=f"{i+1}º {player_name}", font_size=14, text_color=arcade.color.BLACK))
                row.add(arcade.gui.UILabel(text=f"{score} pts", font_size=14, text_color=arcade.color.BLACK))
                others_box.add(row.with_background(color=arcade.color.WHITE).with_padding(top=10, bottom=10, left=20, right=20))
            self.v_box.add(others_box)

        # --- BOTÃO VOLTAR AO MENU ---
        back_button = arcade.gui.UIFlatButton(
            text="Back to Menu", width=200,
            style={
                "normal": {"bg_color": (0, 93, 164), "font_color": arcade.color.WHITE},
                "hover": {"bg_color": (0, 110, 190), "font_color": arcade.color.WHITE},
                "press": {"bg_color": (0, 75, 140), "font_color": arcade.color.WHITE}
            }
        )
        back_button.on_click = self.on_click_back
        self.v_box.add(back_button)

        # Ancoragem central
        anchor = arcade.gui.UIAnchorLayout()
        anchor.add(child=self.v_box, anchor_x="center_x", anchor_y="center_y")
        self.manager.add(anchor)

    def on_show_view(self):
        self.manager.enable()
        arcade.set_background_color((237, 248, 255))

    def on_hide_view(self):
        self.manager.disable()

    def on_click_back(self, event):
        from .menu_view import MenuView
        self.window.show_view(MenuView())

    def on_draw(self):
        self.clear()
        self.manager.draw()