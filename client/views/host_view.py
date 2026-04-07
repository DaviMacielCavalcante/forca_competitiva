import arcade
import arcade.gui

class HostView(arcade.View):
    def __init__(self):
        super().__init__()
        self.manager = arcade.gui.UIManager()
        self.v_box = arcade.gui.UIBoxLayout(space_between=20)

        title = arcade.gui.UILabel(text="Host View", font_size=28, text_color=arcade.color.BLACK)
        self.v_box.add(title)

        subtitle = arcade.gui.UILabel(text="Prepare a palavra secreta", font_size=14, text_color=arcade.color.DARK_GRAY)
        self.v_box.add(subtitle)

        # Input Text
        self.word_input = arcade.gui.UIInputText(
            width=300, height=40, text="Ex: ELEFANTE", text_color=arcade.color.BLACK
        )
        
        # Arcade 3.3.3+: Modificando o próprio input ao invés de envelopá-lo com classes externas
        self.word_input.with_background(color=arcade.color.WHITE)
        self.word_input.with_padding(top=10, right=10, bottom=10, left=10)
        self.v_box.add(self.word_input)

        submit_button = arcade.gui.UIFlatButton(
            text="Confirmar Palavra ►", 
            width=300,
            style={
                "normal": {
                    "bg_color": (0, 93, 164), 
                    "font_color": arcade.color.WHITE
                },
                "hover": {                          # <-- Alterado aqui também
                    "bg_color": (0, 110, 190), 
                    "font_color": arcade.color.WHITE
                },
                "press": {                          # <-- E aqui
                    "bg_color": (0, 75, 140), 
                    "font_color": arcade.color.WHITE
                }
            }
        )

        submit_button.on_click = self.on_click_submit
        self.v_box.add(submit_button)

        # Arcade 3.3.3+: UIAnchorLayout
        anchor = arcade.gui.UIAnchorLayout()
        anchor.add(child=self.v_box, anchor_x="center_x", anchor_y="center_y")
        self.manager.add(anchor)

    def on_show_view(self):
        self.manager.enable()
        arcade.set_background_color((237, 248, 255))

    def on_hide_view(self):
        self.manager.disable()

    def on_click_submit(self, event):
        print(f"Palavra enviada: {self.word_input.text}")

    def on_draw(self):
        self.clear()
        self.manager.draw()