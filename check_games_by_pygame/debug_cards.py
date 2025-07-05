import pygame
from game.game import ChequeGames
from game.constants import SCREEN_WIDTH, SCREEN_HEIGHT, PLAYER_HAND_Y

def print_card_positions(jeu):
    print("\n=== POSITIONS DES CARTES DU JOUEUR ===")
    print(f"Nombre de cartes: {len(jeu.joueur.main)}")
    
    if not jeu.joueur.main:
        print("Aucune carte dans la main du joueur")
        return
    
    # Afficher les dimensions de la première carte
    card_width = jeu.joueur.main[0]._creer_surface().get_width()
    card_height = jeu.joueur.main[0]._creer_surface().get_height()
    print(f"Dimensions d'une carte: {card_width}x{card_height}")
    
    # Afficher les positions de chaque carte
    for i, carte in enumerate(jeu.joueur.main):
        print(f"Carte {i}: x={carte.rect.x}, y={carte.rect.y}")
    
    # Calculer la largeur totale nécessaire avec le chevauchement actuel
    overlap = card_width // 2  # Chevauchement actuel (50%)
    total_width = len(jeu.joueur.main) * (card_width - overlap) + overlap
    print(f"\nLargeur totale nécessaire: {total_width}px")
    
    # Calculer la position de départ pour centrer les cartes
    start_x = (SCREEN_WIDTH - total_width) // 2
    print(f"Position de départ recommandée pour centrer: x={start_x}")

def main():
    # Initialiser pygame
    pygame.init()
    ecran = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    # Créer une instance du jeu
    jeu = ChequeGames(ecran)
    
    # Afficher les positions des cartes
    print_card_positions(jeu)
    
    # Afficher les dimensions de l'écran
    print("\n=== CONFIGURATION DE L'ÉCRAN ===")
    print(f"Largeur de l'écran: {SCREEN_WIDTH}px")
    print(f"Hauteur de l'écran: {SCREEN_HEIGHT}px")
    print(f"Position Y des cartes du joueur: {PLAYER_HAND_Y}px")

if __name__ == "__main__":
    main()
