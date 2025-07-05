import pygame
import sys
import os
import importlib.util

# Ajouter le répertoire parent au chemin Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importer les constantes
from game.constants import SCREEN_WIDTH, PLAYER_HAND_Y, CARD_WIDTH, CARD_HEIGHT

def patch_game_module():
    """Applique le correctif au module game"""
    try:
        # Importer le module game
        import game.game
        
        # Sauvegarder la classe originale
        original_cheque_games = game.game.ChequeGames
        
        # Créer une sous-classe qui surcharge la méthode afficher
        class PatchedChequeGames(original_cheque_games):
            def afficher(self):
                # Appeler la méthode parente pour les éléments de base
                super().afficher()
                
                # Vérifier si le joueur a des cartes
                if not hasattr(self, 'joueur') or not hasattr(self.joueur, 'main') or not self.joueur.main:
                    return
                    
                # Calculer l'espacement entre les cartes
                nb_cartes = len(self.joueur.main)
                if nb_cartes <= 0:
                    return
                    
                # Utiliser la largeur de la première carte comme référence
                try:
                    surface_carte = self.joueur.main[0]._creer_surface()
                    card_width = surface_carte.get_width()
                except:
                    card_width = CARD_WIDTH
                    
                # Calculer l'espacement entre les cartes (30% de chevauchement)
                espacement = int(card_width * 0.7)
                largeur_totale = (nb_cartes - 1) * espacement + card_width
                
                # Centrer les cartes sur l'écran
                x_depart = (SCREEN_WIDTH - largeur_totale) // 2
                
                # Afficher les cartes du joueur (sauf celle en cours de déplacement)
                for i, carte in enumerate(self.joueur.main):
                    if i != self.carte_selectionnee:  # Ne pas afficher la carte sélectionnée ici
                        # Calculer la position x avec espacement
                        x = x_depart + i * espacement
                        y = PLAYER_HAND_Y
                        
                        # Mettre à jour la position de la carte
                        if not hasattr(carte, 'rect') or not carte.rect:
                            carte.rect = pygame.Rect(x, y, card_width, CARD_HEIGHT)
                        else:
                            carte.rect.x = x
                            carte.rect.y = y
                        
                        # Dessiner la carte à sa position actuelle
                        carte.dessiner(self.ecran, (x, y))
        
        # Remplacer la classe d'origine par la version patchée
        game.game.ChequeGames = PatchedChequeGames
        print("Patch d'affichage des cartes appliqué avec succès!")
        return True
        
    except Exception as e:
        print(f"Erreur lors de l'application du patch: {e}")
        return False

# Si ce script est exécuté directement, appliquer le patch
if __name__ == "__main__":
    if patch_game_module():
        print("Le jeu devrait maintenant afficher correctement toutes les cartes du joueur.")
    else:
        print("Impossible d'appliquer le patch. Vérifiez les erreurs ci-dessus.")
