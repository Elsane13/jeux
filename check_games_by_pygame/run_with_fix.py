import sys
import os
import importlib.util

# Ajouter le répertoire parent au chemin Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importer le module fix_card_display pour appliquer le correctif
from fix_card_display import patch_game_module

# Appliquer le correctif
if not patch_game_module():
    print("Attention: Le correctif d'affichage n'a pas pu être appliqué correctement.")
    sys.exit(1)

# Importer et exécuter le jeu principal
from game.game import ChequeGames
import pygame

def main():
    # Initialisation de Pygame
    pygame.init()
    
    # Création de la fenêtre
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Jeu de Cartes avec Correctif d'Affichage")
    
    # Création d'une instance du jeu
    jeu = ChequeGames(screen)
    
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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Clic gauche
                    jeu.gerer_clic_souris(event.pos, 'down')
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Relâchement du clic gauche
                    jeu.gerer_clic_souris(event.pos, 'up')
            elif event.type == pygame.MOUSEMOTION:
                if event.buttons[0]:  # Si le bouton gauche est maintenu
                    jeu.gerer_clic_souris(event.pos, 'motion')
        
        # Mise à jour du jeu
        jeu.mettre_a_jour()
        
        # Affichage
        screen.fill((0, 100, 0))  # Fond vert foncé
        jeu.afficher()
        
        # Mise à jour de l'affichage
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
