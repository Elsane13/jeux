import pygame
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.game import ChequeGames
from game.constants import SCREEN_WIDTH, SCREEN_HEIGHT, DARK_GREEN, WHITE, PLAYER_HAND_Y, CARD_WIDTH, CARD_HEIGHT

def main():
    # Initialisation de Pygame
    pygame.init()
    
    # Création de la fenêtre
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Débogage Simple des Cartes")
    
    # Création d'une instance du jeu
    jeu = ChequeGames(screen)
    
    # Police pour le texte
    font = pygame.font.Font(None, 24)
    
    # Boucle principale
    clock = pygame.time.Clock()
    running = True
    
    while running:
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Effacer l'écran
        screen.fill(DARK_GREEN)
        
        # Afficher les cartes du joueur
        if hasattr(jeu, 'joueur') and hasattr(jeu.joueur, 'main') and jeu.joueur.main:
            # Calculer la largeur totale nécessaire
            card_spacing = 30  # Espacement entre les cartes
            card_width = CARD_WIDTH
            total_width = (len(jeu.joueur.main) - 1) * card_spacing + card_width
            start_x = (SCREEN_WIDTH - total_width) // 2
            
            for i, carte in enumerate(jeu.joueur.main):
                # Calculer la position x avec espacement
                x = start_x + i * card_spacing
                y = PLAYER_HAND_Y
                
                # Mettre à jour la position de la carte
                if not hasattr(carte, 'rect'):
                    carte.rect = pygame.Rect(x, y, card_width, CARD_HEIGHT)
                else:
                    carte.rect.x = x
                    carte.rect.y = y
                
                # Dessiner un rectangle de débogage
                pygame.draw.rect(screen, (255, 0, 0), (x, y, card_width, CARD_HEIGHT), 2)
                
                # Dessiner la carte si possible
                if hasattr(carte, 'dessiner'):
                    try:
                        carte.dessiner(screen, (x, y))
                    except Exception as e:
                        print(f"Erreur lors du dessin de la carte {i}: {e}")
                        # Dessiner une carte de remplacement en cas d'erreur
                        pygame.draw.rect(screen, (100, 100, 200), (x, y, card_width, CARD_HEIGHT))
                        error_text = font.render(f"Carte {i}", True, WHITE)
                        screen.blit(error_text, (x + 10, y + 10))
                
                # Afficher les informations de débogage
                debug_info = [
                    f"{i}: ({x},{y})",
                    f"{carte.valeur} de {carte.symbole}",
                    f"{card_width}x{CARD_HEIGHT}"
                ]
                
                for j, info in enumerate(debug_info):
                    text_surface = font.render(info, True, WHITE)
                    screen.blit(text_surface, (x + 5, y + 5 + j * 20))
        
        # Afficher le nombre de cartes
        if hasattr(jeu, 'joueur') and hasattr(jeu.joueur, 'main'):
            count_text = f"Cartes: {len(jeu.joueur.main)}"
            count_surface = font.render(count_text, True, WHITE)
            screen.blit(count_surface, (10, 10))
        
        # Mettre à jour l'affichage
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
