import pygame
from game.game import ChequeGames

def main():
    # Initialiser pygame
    pygame.init()
    
    # Créer une instance du jeu
    jeu = ChequeGames(pygame.display.set_mode((800, 600)))
    
    # Afficher les informations sur les cartes du joueur
    print("=== CARTES DU JOUEUR ===")
    print(f"Nombre de cartes: {len(jeu.joueur.main)}")
    
    if jeu.joueur.main:
        # Afficher les dimensions de la première carte
        card_width = jeu.joueur.main[0]._creer_surface().get_width()
        card_height = jeu.joueur.main[0]._creer_surface().get_height()
        print(f"Dimensions d'une carte: {card_width}x{card_height}")
        
        # Afficher la position de chaque carte
        for i, carte in enumerate(jeu.joueur.main):
            print(f"Carte {i}: x={carte.rect.x}, y={carte.rect.y}")
    else:
        print("Aucune carte dans la main du joueur")

if __name__ == "__main__":
    main()
