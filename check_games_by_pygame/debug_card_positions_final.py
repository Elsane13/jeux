import pygame
import sys
import os
from game.game import ChequeGames
from game.constants import SCREEN_WIDTH, SCREEN_HEIGHT, DARK_GREEN, WHITE, PLAYER_HAND_Y

def main():
    # Initialisation de Pygame
    pygame.init()
    
    # Création de la fenêtre
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Débogage des positions des cartes")
    
    # Création d'une instance du jeu
    jeu = ChequeGames(screen)
    
    # Police pour le texte de débogage
    font = pygame.font.Font(None, 24)
    
    # Boucle principale
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
        for i, carte in enumerate(jeu.joueur.main):
            # Obtenir la surface de la carte pour avoir ses dimensions réelles
            surface_carte = carte._creer_surface()
            card_width = surface_carte.get_width()
            card_height = surface_carte.get_height()
            
            # Calculer la position x avec un chevauchement des cartes
            overlap = int(card_width * 0.3)  # 30% de chevauchement
            total_width = (len(jeu.joueur.main) * (card_width - overlap)) + overlap
            start_x = (SCREEN_WIDTH - total_width) // 2
            x = start_x + i * (card_width - overlap)
            y = PLAYER_HAND_Y
            
            # Mettre à jour la position de la carte
            carte.rect.x = x
            carte.rect.y = y
            
            # Dessiner un rectangle de débogage
            pygame.draw.rect(screen, (255, 0, 0), (x, y, card_width, card_height), 2)
            
            # Dessiner la carte
            carte.dessiner(screen, (x, y))
            
            # Afficher les coordonnées
            coord_text = f"({x}, {y}) - {card_width}x{card_height}"
            text_surface = font.render(coord_text, True, WHITE)
            screen.blit(text_surface, (x, y - 25))
        
        # Mettre à jour l'affichage
        pygame.display.flip()
    
    # Quitter Pygame
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
