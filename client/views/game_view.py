import arcade
import arcade.gui

# Importamos o Interlúdio (criaremos o arquivo dele depois, mas já deixamos o gancho pronto)
# from .interlude_view import InterludeView 

class GameView(arcade.View):
    def __init__(self, secret_word="PALAVRA", is_host=False):
        super().__init__()
        self.manager = arcade.gui.UIManager()
        
        # --- ESTADOS DO JOGO ---
        self.secret_word = secret_word.upper()
        self.is_host = is_host
        self.attempts_left = 3            # 3 chances individuais por jogador
        self.time_left = 60.0             # Timer padrão (1 minuto)
        self.guessed_letters = set()      # Conjunto de letras já reveladas
        self.is_game_over = False

        # --- LAYOUT PRINCIPAL ---
        self.v_box = arcade.gui.UIBoxLayout(space_between=20)

        # 1. Cabeçalho: Timer e Tentativas
        self.status_box = arcade.gui.UIBoxLayout(vertical=False, space_between=40)
        
        # Label do Timer (A ser atualizado via UDP)
        self.timer_label = arcade.gui.UILabel(
            text=f"Tempo: {int(self.time_left)}s",
            font_size=18,
            text_color=(0, 93, 164),
            bold=True
        )
        self.status_box.add(self.timer_label)

        # Label de Tentativas Individuais
        self.attempts_label = arcade.gui.UILabel(
            text=f"Tentativas: {self.attempts_left}/3",
            font_size=18,
            text_color=arcade.color.DARK_RED
        )
        self.status_box.add(self.attempts_label)
        self.v_box.add(self.status_box)

        # 2. Tela da Forca: Container Horizontal para os "Game Tiles" (Letras)
        # Inspirado no design system: Cartões individuais ao invés de um texto corrido
        self.word_box = arcade.gui.UIBoxLayout(vertical=False, space_between=8)
        self.build_word_display()
        self.v_box.add(self.word_box)

        # 3. Área de Interação (Só aparece se o jogador tiver tentativas e não for o host)
        if not self.is_host:
            self.input_box = arcade.gui.UIBoxLayout(space_between=10)
            
            self.guess_input = arcade.gui.UIInputText(
                width=200, height=40, text="Letra ou Palavra", text_color=arcade.color.BLACK
            )
            # Regra "No-Line" & "Game Cards" (Arcade 3.3.3)
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
            # Feedback visual para o host que está apenas assistindo
            host_msg = arcade.gui.UILabel(
                text="Você é o Host. Acompanhe os jogadores!", font_size=14, text_color=arcade.color.DARK_GRAY
            )
            self.v_box.add(host_msg.with_background(color=arcade.color.WHITE).with_padding(top=10, right=20, bottom=10, left=20))

        # Ancora central do Arcade 3.3.3+
        anchor = arcade.gui.UIAnchorLayout()
        anchor.add(child=self.v_box, anchor_x="center_x", anchor_y="center_y")
        self.manager.add(anchor)

    # --- FUNÇÕES DE CONSTRUÇÃO DE INTERFACE ---
    
    def build_word_display(self):
        """
        Função que constrói ou reconstrói os espaços da palavra na interface.
        Reflete a quantidade de caracteres e revela os que já foram acertados.
        """
        self.word_box.clear() # Limpa os blocos atuais
        
        for char in self.secret_word:
            if char in self.guessed_letters:
                # Letra revelada: Fundo azul primário, texto branco (Tactile Playroom rule)
                lbl = arcade.gui.UILabel(text=char, font_size=24, text_color=arcade.color.WHITE, bold=True)
                tile = lbl.with_background(color=(0, 93, 164)).with_padding(top=15, right=20, bottom=15, left=20)
            else:
                # Letra escondida: Fundo branco, traço invisível/cinza
                lbl = arcade.gui.UILabel(text="_", font_size=24, text_color=arcade.color.BLACK, bold=True)
                tile = lbl.with_background(color=arcade.color.WHITE).with_padding(top=15, right=20, bottom=15, left=20)
                
            self.word_box.add(tile)

    def update_interface_text(self):
        """Atualiza os textos de status na tela."""
        self.timer_label.text = f"Tempo: {int(self.time_left)}s"
        self.attempts_label.text = f"Tentativas: {self.attempts_left}/3"

    # --- FUNÇÕES DE LÓGICA E REDES (Ganchos) ---
    
    def sync_timer_via_udp(self, udp_time_received):
        """
        MÉTODO PARA O SEU PROTOCOLO UDP:
        Sempre que o cliente UDP receber o pacote de sincronização do timer,
        chame essa função para atualizar o relógio oficial do jogo.
        """
        self.time_left = udp_time_received
        self.update_interface_text()

    def reveal_letter_from_server(self, letter):
        """
        MÉTODO DE SINCRONIZAÇÃO:
        Chamado quando OUTRO jogador acerta uma letra e o servidor avisa a todos.
        """
        self.guessed_letters.add(letter.upper())
        self.build_word_display()

    def on_guess_submit(self, event):
        """Lógica acionada quando o jogador tenta adivinhar."""
        if self.attempts_left <= 0 or self.is_game_over:
            return

        guess = self.guess_input.text.strip().upper()
        
        # Validação simples
        if not guess:
            return
            
        print(f"Enviando tentativa para o servidor: {guess}")
        # AQUI ENTRA SEU SOCKET/WEBHOOK: Enviar o 'guess' para o servidor validar [7].
        
        # --- SIMULAÇÃO DE LÓGICA LOCAL (Substitua pelo retorno do servidor depois) ---
        if guess in self.secret_word and len(guess) == 1:
            # Acertou uma letra
            self.reveal_letter_from_server(guess)
        elif guess == self.secret_word:
            # Acertou a palavra inteira
            for char in guess:
                self.guessed_letters.add(char)
            self.build_word_display()
            print("Você acertou a palavra toda!")
        else:
            # Errou
            self.attempts_left -= 1
            self.update_interface_text()
            if self.attempts_left == 0:
                print("Você gastou todas as suas tentativas. Apenas assista agora!")
                self.input_box.clear() # Remove a caixa de texto para ele não tentar mais

    # --- MÉTODOS DO ARCADE ---

    def on_show_view(self):
        self.manager.enable()
        # Regra "The Table"
        arcade.set_background_color((237, 248, 255))

    def on_hide_view(self):
        self.manager.disable()

    def on_update(self, delta_time):
        """
        Loop de atualização do Arcade. 
        Enquanto o UDP não é implementado, fazemos o timer rodar localmente.
        """
        if self.is_game_over:
            return

        self.time_left -= delta_time
        self.update_interface_text()

        # Condição de fim de tempo [6]
        if self.time_left <= 0:
            self.time_left = 0
            self.is_game_over = True
            print("O tempo acabou! Transicionando para o Interlúdio...")
            # Descomente a linha abaixo quando criar a tela de Interlúdio
            # self.window.show_view(InterludeView())

    def on_draw(self):
        self.clear()
        self.manager.draw()