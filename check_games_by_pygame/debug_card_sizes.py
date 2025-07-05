"""
Script de débogage pour vérifier les dimensions des cartes.
"""
import pygame
import sys
import os
from pathlib import Path

# Ajouter le répertoire parent au chemin d'import
sys.path.append(str(Path(__file__).parent))

from game.constants import *
from game.card import Carte
from game.constants import Symbole

def main():
    # Initialisation de Pygame
    pygame.init()
    
    # Création d'une fenêtre
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Débogage des dimensions des cartes")
    
    # Police pour afficher le texte
    font = pygame.font.Font(None, 24)
    
    # Création de quelques cartes de test
    test_cards = [
        (1, Symbole.COEUR),    # As de Coeur
        (7, Symbole.CARREAU),  # 7 de Carreau
        (11, Symbole.TREFLE),  # Valet de Trèfle
        (13, Symbole.PIQUE),   # Roi de Pique
        (0, Symbole.JOKER)     # Joker
    ]
    
    # Créer les instances de cartes
    cartes = [Carte(v, s) for v, s in test_cards]
    
    # Afficher les informations de débogage
    print("=== DIMENSIONS DES CARTES ===")
    print(f"CARD_WIDTH = {CARD_WIDTH}, CARD_HEIGHT = {CARD_HEIGHT}")
    print(f"SCALE_FACTOR = {SCALE_FACTOR}")
    
    if hasattr(Carte, '_dos_carte') and Carte._dos_carte is not None:
        dos_width, dos_height = Carte._dos_carte.get_size()
        print(f"\nDos de carte: {dos_width}x{dos_height}")
    else:
        print("\nAvertissement: Le dos de carte n'est pas chargé")
    
    print("\nCartes chargées:")
    for carte in cartes:
        surface = carte._creer_surface()
        width, height = surface.get_size()
        print(f"- {carte}: {width}x{height}")
    
    # Boucle principale
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Effacer l'écran
        screen.fill((50, 50, 50))
        
        # Afficher les informations
        y_offset = 20
        
        # Titre
        title = font.render("DIMENSIONS DES CARTES", True, (255, 255, 0))
        screen.blit(title, (20, y_offset))
        y_offset += 30
        
        # Constantes
        const_text = font.render(f"CARD_WIDTH = {CARD_WIDTH}, CARD_HEIGHT = {CARD_HEIGHT}, SCALE_FACTOR = {SCALE_FACTOR}", 
                               True, (255, 255, 255))
        screen.blit(const_text, (20, y_offset))
        y_offset += 30
        
        # Dimensions du dos de carte
        if hasattr(Carte, '_dos_carte') and Carte._dos_carte is not None:
            dos_width, dos_height = Carte._dos_carte.get_size()
            dos_text = font.render(f"Dos de carte: {dos_width}x{dos_height}", True, (200, 200, 255))
            screen.blit(dos_text, (20, y_offset))
            y_offset += 30
        
        # Afficher les cartes avec leurs dimensions
        x_pos = 20
        for i, carte in enumerate(cartes):
            surface = carte._creer_surface()
            width, height = surface.get_size()
            
            # Dessiner la carte
            screen.blit(surface, (x_pos, y_offset))
            
            # Afficher les dimensions
            dim_text = font.render(f"{carte}: {width}x{height}", True, (255, 255, 255))
            screen.blit(dim_text, (x_pos, y_offset + height + 5))
            
            # Déplacer la position pour la prochaine carte
            x_pos += width + 20
            
            # Si on dépasse la largeur de l'écran, passer à la ligne suivante
            if x_pos > SCREEN_WIDTH - 200:
                x_pos = 20
                y_offset += height + 50
        
        pygame.display.flip()
        clock.tick(30)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
