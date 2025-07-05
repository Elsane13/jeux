import pygame
import sys
from game.game import ChequeGames
from game.constants import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, PLAYER_HAND_Y

def main():
    pygame.init()
    ecran = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Débogage Position des Cartes")
    
    # Créer une instance du jeu
    jeu = ChequeGames(ecran)
    
    # Police pour le débogage
    font = pygame.font.Font(None, 24)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Effacer l'écran
        ecran.fill((0, 100, 0))  # Fond vert foncé comme le jeu
        
        # Afficher le jeu
        jeu.afficher()
        
        # Afficher les informations de débogage
        debug_info = [
            f"Cartes dans la main du joueur: {len(jeu.joueur.main)}",
            f"Largeur de l'écran: {SCREEN_WIDTH}",
            f"Hauteur de l'écran: {SCREEN_HEIGHT}",
            f"Position Y des cartes du joueur: {PLAYER_HAND_Y}",
            "",
            "Positions des cartes (index, x, y, largeur, hauteur):"
        ]
        
        # Afficher les positions des cartes du joueur
        if hasattr(jeu.joueur, 'main') and jeu.joueur.main:
            card_width = jeu.joueur.main[0]._creer_surface().get_width()
            card_height = jeu.joueur.main[0]._creer_surface().get_height()
            debug_info.append(f"Dimensions d'une carte: {card_width}x{card_height}")
            
            # Calculer la largeur totale nécessaire
            overlap = int(card_width * 0.4)
            total_width = len(jeu.joueur.main) * (card_width - overlap) + overlap
            start_x = (SCREEN_WIDTH - total_width) // 2
            
            for i, carte in enumerate(jeu.joueur.main):
                debug_info.append(f"Carte {i}: x={carte.rect.x}, y={carte.rect.y}, w={card_width}, h={card_height}")
        
        # Afficher les informations de débogage
        y_offset = 10
        for line in debug_info:
            text = font.render(line, True, WHITE)
            ecran.blit(text, (10, y_offset))
            y_offset += 20
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
