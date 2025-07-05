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
    pygame.display.set_caption("Débogage des Cartes du Joueur")
    
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
        
        # Afficher les cartes du joueur avec des informations de débogage
        if hasattr(jeu, 'joueur') and hasattr(jeu.joueur, 'main'):
            main_joueur = jeu.joueur.main
            nb_cartes = len(main_joueur)
            
            # Afficher le nombre de cartes
            texte_nb_cartes = font.render(f"Cartes: {nb_cartes}", True, WHITE)
            screen.blit(texte_nb_cartes, (10, 10))
            
            if nb_cartes > 0:
                # Calculer l'espacement entre les cartes
                largeur_carte = CARD_WIDTH
                espacement = int(largeur_carte * 0.7)  # 70% de la largeur de la carte
                largeur_totale = (nb_cartes - 1) * espacement + largeur_carte
                x_depart = (SCREEN_WIDTH - largeur_totale) // 2
                
                for i, carte in enumerate(main_joueur):
                    # Calculer la position x avec espacement
                    x = x_depart + i * espacement
                    y = PLAYER_HAND_Y
                    
                    # Mettre à jour la position de la carte
                    if not hasattr(carte, 'rect') or not carte.rect:
                        carte.rect = pygame.Rect(x, y, largeur_carte, CARD_HEIGHT)
                    else:
                        carte.rect.x = x
                        carte.rect.y = y
                    
                    # Dessiner un rectangle de débogage
                    pygame.draw.rect(screen, (255, 0, 0), (x, y, largeur_carte, CARD_HEIGHT), 2)
                    
                    # Dessiner la carte
                    try:
                        carte.dessiner(screen, (x, y))
                    except Exception as e:
                        # En cas d'erreur, dessiner un rectangle de remplacement
                        pygame.draw.rect(screen, (100, 100, 200), (x, y, largeur_carte, CARD_HEIGHT))
                        texte_erreur = font.render(f"Erreur: {str(e)}", True, (255, 255, 0))
                        screen.blit(texte_erreur, (x + 5, y + 5))
                    
                    # Afficher les informations de débogage
                    infos = [
                        f"Carte {i}",
                        f"Pos: ({x}, {y})",
                        f"Taille: {largeur_carte}x{CARD_HEIGHT}"
                    ]
                    
                    for j, info in enumerate(infos):
                        texte_info = font.render(info, True, WHITE)
                        screen.blit(texte_info, (x + 5, y + 5 + j * 20))
        
        # Mettre à jour l'affichage
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
