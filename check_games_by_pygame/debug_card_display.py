import pygame
import sys
from game.game import ChequeGames
from game.constants import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK

def main():
    pygame.init()
    ecran = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Débogage Affichage des Cartes")
    
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
        ecran.fill(WHITE)
        
        # Afficher le jeu
        jeu.afficher()
        
        # Afficher les informations de débogage
        debug_info = [
            f"Cartes dans la main du joueur: {len(jeu.joueur.main)}",
            f"Carte sélectionnée: {jeu.carte_selectionnee}",
            ""
        ]
        
        # Afficher les positions des cartes du joueur
        for i, carte in enumerate(jeu.joueur.main):
            debug_info.append(f"Carte {i}: ({carte.rect.x}, {carte.rect.y}) - {carte}")
        
        # Afficher les informations de débogage
        y_offset = 10
        for line in debug_info:
            text = font.render(line, True, BLACK)
            ecran.blit(text, (10, y_offset))
            y_offset += 20
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
