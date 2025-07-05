import pygame
import sys
import os
from game.constants import *
from game.card import Carte
from game.symbols import Symbole

def main():
    # Initialisation de Pygame
    pygame.init()
    
    # Création de la fenêtre
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Test des dimensions des cartes")
    
    # Création d'une police pour afficher les informations
    font = pygame.font.Font(None, 36)
    
    # Création de quelques cartes de test
    test_cards = [
        Carte(1, Symbole.COEUR),    # As de Coeur
        Carte(7, Symbole.CARREAU),  # 7 de Carreau
        Carte(11, Symbole.TREFLE),  # Valet de Trèfle
        Carte(13, Symbole.PIQUE),   # Roi de Pique
        Carte(0, Symbole.JOKER)     # Joker
    ]
    
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
        
        # Afficher les informations sur la fenêtre
        title = font.render("Test des dimensions des cartes", True, (255, 255, 255))
        screen.blit(title, (20, 20))
        
        # Afficher les cartes avec leurs dimensions
        y_offset = 70
        for i, card in enumerate(test_cards):
            # Obtenir la surface de la carte
            card_surface = card._creer_surface()
            width, height = card_surface.get_size()
            
            # Afficher la carte
            screen.blit(card_surface, (50, y_offset))
            
            # Afficher les informations sur la carte
            card_info = f"{card} - Dimensions: {width}x{height} (Attendues: {CARD_WIDTH}x{CARD_HEIGHT})"
            text = font.render(card_info, True, (255, 255, 255))
            screen.blit(text, (50 + width + 20, y_offset + height//2 - 10))
            
            y_offset += height + 20
        
        # Afficher les informations sur le facteur d'échelle
        scale_info = f"SCALE_FACTOR: {SCALE_FACTOR}"
        text = font.render(scale_info, True, (255, 255, 255))
        screen.blit(text, (20, SCREEN_HEIGHT - 50))
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
