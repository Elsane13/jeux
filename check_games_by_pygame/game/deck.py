import random
from .constants import Symbole
from .card import Carte

class Deck:
    def __init__(self):
        self.cartes = []
        self.defausse = []
        self.initialiser()
    
    def initialiser(self):
        """Initialise un nouveau paquet de 52 cartes uniques (sans jokers)"""
        self.cartes = []
        
        # Ajouter les cartes normales (1-13 pour chaque symbole sauf JOKER)
        for symbole in Symbole:
            if symbole != Symbole.JOKER:  # Ne pas ajouter de cartes pour le symbole JOKER
                for valeur in range(1, 14):  # 1 à 13 inclus
                    self.cartes.append(Carte(valeur, symbole))
        
        # Vérifier qu'on a bien 52 cartes standard
        if len(self.cartes) != 52:
            print(f"Attention: Le paquet contient {len(self.cartes)} cartes au lieu de 52")
        
        # Afficher le nombre de cartes pour débogage
        print(f"Paquet initialisé avec {len(self.cartes)} cartes (sans jokers)")
        
        self.melanger()
    
    def melanger(self):
        """Mélange le paquet de cartes"""
        random.shuffle(self.cartes)
    
    def piocher(self, nombre=1):
        """Pioche un certain nombre de cartes du paquet"""
        cartes_piochees = []
        for _ in range(nombre):
            if not self.cartes:  # Si le paquet est vide
                if not self.defausse:  # Si la défausse est aussi vide
                    return cartes_piochees  # Retourne ce qu'on a pu piocher
                # On remélange la défausse dans le paquet
                self.cartes = self.defausse[:-1]  # On garde la dernière carte de la défausse
                self.defausse = [self.defausse[-1]] if self.defausse else []
                self.melanger()
            
            if self.cartes:  # S'il reste des cartes à piocher
                carte = self.cartes.pop()
                carte.face_cachee = False
                cartes_piochees.append(carte)
        
        return cartes_piochees
    
    def ajouter_defausse(self, carte):
        """Ajoute une carte à la défausse"""
        self.defausse.append(carte)
    
    def obtenir_derniere_carte_defausse(self):
        """Retourne la dernière carte de la défausse (None si vide)"""
        return self.defausse[-1] if self.defausse else None
    
    def __len__(self):
        """Retourne le nombre de cartes restantes dans le paquet"""
        return len(self.cartes)
