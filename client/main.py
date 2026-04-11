from views.menu_view import MenuView
import arcade


# Constantes de configuração da janela
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
SCREEN_TITLE = "Forca Distribuída - Tactile Playroom"

def main():
    """Função principal que inicializa o jogo."""
    # Cria a janela do jogo
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    
    # Instancia e exibe a tela de Menu
    menu_view = MenuView()
    window.network = None
    window.show_view(menu_view)
    
    # Inicia o loop da engine
    arcade.run()

if __name__ == "__main__":
    main()