import pygame
import sys
from game.game import ChequeGames
from game.constants import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, PLAYER_HAND_Y, AI_HAND_Y, CARD_WIDTH, CARD_HEIGHT

def main():
    # Initialisation de Pygame
    pygame.init()
    ecran = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Débogage Positions des Cartes")
    
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
        
        # Mettre à jour le jeu
        jeu.mettre_a_jour()
        
        # Afficher le jeu
        jeu.afficher()
        
        # Afficher les informations de débogage
        debug_info = [
            f"=== DÉBOGAGE POSITIONS DES CARTES ===",
            f"Largeur de l'écran: {SCREEN_WIDTH}px",
            f"Hauteur de l'écran: {SCREEN_HEIGHT}px",
            f"Position Y IA: {AI_HAND_Y}px",
            f"Position Y Joueur: {PLAYER_HAND_Y}px",
            f"Largeur carte: {CARD_WIDTH}px",
            f"Hauteur carte: {CARD_HEIGHT}px",
            "",
            f"Cartes IA: {len(jeu.ia.main)}",
            f"Cartes Joueur: {len(jeu.joueur.main)}",
            "",
            "=== POSITIONS DES CARTES DU JOUEUR ==="
        ]
        
        # Afficher les positions des cartes du joueur
        if hasattr(jeu.joueur, 'main') and jeu.joueur.main:
            for i, carte in enumerate(jeu.joueur.main):
                debug_info.append(f"Carte {i}: x={carte.rect.x}, y={carte.rect.y}")
        
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
