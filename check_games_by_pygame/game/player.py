import pygame
from .constants import INITIAL_HEARTS, INITIAL_CARDS, CARD_WIDTH, CARD_HEIGHT
from .card import Carte

class Joueur:
    def __init__(self, nom: str, est_ia: bool = False):
        self.nom = nom
        self.est_ia = est_ia
        self.main = []
        self.coeurs = INITIAL_HEARTS
        self.est_actif = True
    
    def recevoir_cartes(self, cartes):
        """Ajoute des cartes à la main du joueur et initialise leurs positions"""
        from .constants import CARD_WIDTH, CARD_HEIGHT  # Import local pour éviter les problèmes d'importation circulaire
        
        for carte in cartes:
            # Initialiser la position de la carte si elle n'existe pas
            if not hasattr(carte, 'rect') or not carte.rect:
                carte.rect = pygame.Rect(0, 0, CARD_WIDTH, CARD_HEIGHT)
            
            # S'assurer que la carte a une surface
            if not hasattr(carte, 'surface') or carte.surface is None:
                if hasattr(carte, '_creer_surface'):
                    carte.surface = carte._creer_surface()
            
            self.main.append(carte)
        
        # Mettre à jour les positions des cartes
        self._mettre_a_jour_positions()
    
    def _mettre_a_jour_positions(self):
        """
        Met à jour les positions des cartes dans la main du joueur
        avec un espacement dynamique et une gestion des erreurs
        """
        if not self.main:
            return
            
        try:
            from .constants import SCREEN_WIDTH, PLAYER_HAND_Y, CARD_WIDTH, CARD_HEIGHT
            
            nb_cartes = len(self.main)
            
            # Espacement minimum entre les cartes (en pixels)
            min_espacement = 20
            max_espacement = 120
            marge_laterale = 40  # Marge de chaque côté de l'écran
            
            # Calcul de l'espacement en fonction du nombre de cartes
            espacement = min(max_espacement, 
                          max(min_espacement, 
                              (SCREEN_WIDTH - 2 * marge_laterale - CARD_WIDTH) / max(1, nb_cartes - 1)))
            
            # Calculer la largeur totale nécessaire
            largeur_totale = (nb_cartes - 1) * espacement + CARD_WIDTH
            
            # Ajuster si la largeur dépasse l'écran
            if largeur_totale > SCREEN_WIDTH - 2 * marge_laterale:
                largeur_totale = SCREEN_WIDTH - 2 * marge_laterale
                espacement = (largeur_totale - CARD_WIDTH) / max(1, nb_cartes - 1)
            
            # Centrer les cartes
            x_depart = (SCREEN_WIDTH - largeur_totale) // 2
            
            # Mettre à jour les positions
            for i, carte in enumerate(self.main):
                x = int(x_depart + i * espacement)
                y = PLAYER_HAND_Y
                
                # Créer ou mettre à jour le rectangle de la carte
                if not hasattr(carte, 'rect') or not carte.rect:
                    carte.rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)
                else:
                    carte.rect.x = x
                    carte.rect.y = y
                    
        except Exception as e:
            print(f"Erreur dans _mettre_a_jour_positions: {e}")
            # En cas d'erreur, utiliser un espacement fixe comme solution de secours
            for i, carte in enumerate(self.main):
                if hasattr(carte, 'rect'):
                    carte.rect.x = 50 + i * 90  # Espacement fixe de 90px
                    carte.rect.y = PLAYER_HAND_Y
                    

    
    def jouer_carte(self, index_carte: int):
        """Joue une carte de la main du joueur et met à jour les positions"""
        if 0 <= index_carte < len(self.main):
            carte_jouee = self.main.pop(index_carte)
            # Mettre à jour les positions des cartes restantes
            self._mettre_a_jour_positions()
            return carte_jouee
        return None
    
    def peut_jouer(self, derniere_carte) -> bool:
        """Vérifie si le joueur peut jouer une carte"""
        return any(carte.peut_etre_jouee_sur(derniere_carte) for carte in self.main)
    
    def piocher_carte(self, deck):
        """Fait piocher une carte au joueur"""
        nouvelle_carte = deck.piocher(1)
        if nouvelle_carte:
            self.recevoir_cartes(nouvelle_carte)
            return nouvelle_carte[0]
        return None
    
    def perdre_coeur(self):
        """Fait perdre un cœur au joueur"""
        if self.coeurs > 0:
            self.coeurs -= 1
            if self.coeurs == 0:
                self.est_actif = False
            return True
        return False
    
    def a_gagne(self) -> bool:
        """Vérifie si le joueur a gagné (plus de cartes en main)"""
        return len(self.main) == 0 and self.coeurs > 0
    
    def __str__(self):
        return f"{self.nom} ({self.coeurs} ❤) - Cartes: {', '.join(str(c) for c in self.main)}"
