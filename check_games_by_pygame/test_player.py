import pygame
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.player import Joueur
from game.card import Carte
from game.constants import Symbole, SCREEN_WIDTH, SCREEN_HEIGHT, DARK_GREEN, WHITE, CARD_WIDTH, CARD_HEIGHT

def main():
    # Initialisation de Pygame
    pygame.init()
    
    # Création de la fenêtre
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Test de la classe Joueur")
    
    # Création d'un joueur
    joueur = Joueur("Testeur")
    
    # Création de quelques cartes de test
    cartes = [
        Carte(1, Symbole.COEUR),    # As de cœur
        Carte(7, Symbole.CARREAU),  # 7 de carreau
        Carte(11, Symbole.TREFLE),   # Valet de trèfle
        Carte(13, Symbole.PIQUE),    # Roi de pique
        Carte(0, Symbole.JOKER)      # Joker
    ]
    
    # Donner les cartes au joueur
    joueur.recevoir_cartes(cartes)
    
    # Police pour le texte
    font = pygame.font.Font(None, 36)
    
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
                # Tester la suppression d'une carte avec la touche ESPACE
                elif event.key == pygame.K_SPACE and joueur.main:
                    joueur.jouer_carte(0)  # Jouer la première carte
        
        # Effacer l'écran
        screen.fill(DARK_GREEN)
        
        # Afficher les cartes du joueur
        for i, carte in enumerate(joueur.main):
            if hasattr(carte, 'rect'):
                # Dessiner un rectangle de débogage
                pygame.draw.rect(screen, (255, 0, 0), carte.rect, 2)
                
                # Dessiner la carte
                if hasattr(carte, 'dessiner'):
                    carte.dessiner(screen, (carte.rect.x, carte.rect.y))
                
                # Afficher les informations de la carte
                info = f"{carte.valeur} {carte.symbole.name}"
                text_surface = font.render(info, True, WHITE)
                screen.blit(text_surface, (carte.rect.x, carte.rect.y - 30))
        
        # Afficher les instructions
        instructions = [
            "ESPACE: Jouer la première carte",
            f"Cartes restantes: {len(joueur.main)}",
            "ÉCHAP: Quitter"
        ]
        
        for i, ligne in enumerate(instructions):
            text = font.render(ligne, True, WHITE)
            screen.blit(text, (10, 10 + i * 30))
        
        # Mettre à jour l'affichage
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
