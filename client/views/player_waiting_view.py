import arcade
import arcade.gui

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
        
        # Arcade 3.3.3+: Convertendo o label texto nativamente em um bloco/cartão branco
        waiting_label.with_background(color=arcade.color.WHITE)
        waiting_label.with_padding(top=30, right=40, bottom=30, left=40)
        self.v_box.add(waiting_label)

        dots = arcade.gui.UILabel(text="• • •", font_size=24, text_color=(0, 93, 164))
        self.v_box.add(dots)

        # Arcade 3.3.3+: UIAnchorLayout
        anchor = arcade.gui.UIAnchorLayout()
        anchor.add(child=self.v_box, anchor_x="center_x", anchor_y="center_y")
        self.manager.add(anchor)

    def on_show_view(self):
        self.manager.enable()
        arcade.set_background_color((237, 248, 255))

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        self.clear()
        self.manager.draw()