import pygame
import sys
from typing import List, Optional, Tuple
from .constants import *
from .card import Carte
from .deck import Deck
from .player import Joueur

class ChequeGames:
    def __init__(self, ecran):
        self.ecran = ecran
        self.police = pygame.font.Font(None, 36)
        self.gros_texte = pygame.font.Font(None, 48)
        
        # Initialisation des composants du jeu
        self.paquet = Deck()
        self.joueur = Joueur("Joueur", est_ia=False)
        self.ia = Joueur("IA", est_ia=True)
        self.joueur_actif = self.joueur  # Le joueur commence
        self.partie_terminee = False
        self.gagnant = None
        self.passer_tour = False
        self.cartes_a_piocher = 0
        self.symbole_force = None  # Pour forcer un symbole (effet du Valet)
        self.dernier_joueur = None  # Pour le cas oÃ¹ le joueur gagne mais l'adversaire peut encore jouer
        
        # Variables pour le glisser-dÃ©poser
        self.carte_selectionnee = None
        self.drag_en_cours = False
        self.dernier_clic = 0  # Pour la dÃ©tection du double-clic
        
        # Variables pour l'animation de l'IA
        self.ia_en_cours = False
        self.ia_carte_jouee = None
        self.ia_position_finale = PILE_POS
        self.ia_temps_animation = 0
        self.ia_delai_entre_tours = 1000  # 1 seconde entre les tours de l'IA
        self.dernier_tour_ia = 0
        
        # Pour gÃ©rer l'effet de l'As (rejouer)
        self.as_joue = False  # Indique si un As a Ã©tÃ© jouÃ© au tour prÃ©cÃ©dent
        
        # Pour gÃ©rer le blocage des effets par un Valet
        self.effet_bloque_par_valet = False  # Indique si un effet a Ã©tÃ© bloquÃ© par un Valet
        
        # Variables pour l'animation de pioche
        self.animation_pioche = None  # Carte en cours d'animation
        self.animation_pioche_depart = None  # Position de dÃ©part de l'animation
        self.animation_pioche_arrivee = None  # Position d'arrivÃ©e de l'animation
        self.animation_pioche_debut = 0  # Temps de dÃ©but de l'animation
        self.animation_pioche_duree = 500  # DurÃ©e de l'animation en ms
        
        # Distribution des cartes initiales
        self._distribuer_cartes_initiales()
        
        # PremiÃ¨re carte de la dÃ©fausse (doit Ãªtre une carte normale)
        while True:
            premiere_carte = self.paquet.piocher(1)[0]
            if not premiere_carte.est_speciale() or premiere_carte.valeur == 2:  # On accepte le 2 (passe-partout)
                self.paquet.ajouter_defausse(premiere_carte)
                break
            else:
                # Remettre la carte spÃ©ciale dans le paquet
                self.paquet.cartes.insert(0, premiere_carte)
    
    def _demarrer_animation_pioche(self, carte, depart, arrivee):
        """DÃ©marre une animation de pioche"""
        self.animation_pioche = carte
        self.animation_pioche_depart = depart
        self.animation_pioche_arrivee = arrivee
        self.animation_pioche_debut = pygame.time.get_ticks()
    
    def _mettre_a_jour_animation_pioche(self):
        """Met Ã  jour l'animation de pioche et retourne True si elle est terminÃ©e"""
        if not self.animation_pioche:
            return True
            
        temps_ecoule = pygame.time.get_ticks() - self.animation_pioche_debut
        progression = min(temps_ecoule / self.animation_pioche_duree, 1.0)
        
        # Calcul de la position actuelle (interpolation linÃ©aire)
        x = self.animation_pioche_depart[0] + (self.animation_pioche_arrivee[0] - self.animation_pioche_depart[0]) * progression
        y = self.animation_pioche_depart[1] + (self.animation_pioche_arrivee[1] - self.animation_pioche_depart[1]) * progression
        
        # Mettre Ã  jour la position de la carte
        self.animation_pioche.rect.x = x
        self.animation_pioche.rect.y = y
        
        # Si l'animation est terminÃ©e
        if progression >= 1.0:
            self.animation_pioche = None
            return True
        return False
    
    def afficher_menu_choix_symbole(self):
        """Affiche un menu pour choisir un nouveau symbole"""
        if not hasattr(self, 'menu_actif') or not self.menu_actif:
            self.menu_actif = True
            self.symbole_choisi = None
            
            # Calculer la position du menu (au centre de l'Ã©cran)
            menu_x = SCREEN_WIDTH // 2 - 100
            menu_y = SCREEN_HEIGHT // 2 - 50
            
            # CrÃ©er des boutons pour chaque symbole
            self.boutons_symbole = []
            symboles = [Symbole.COEUR, Symbole.CARREAU, Symbole.TREFLE, Symbole.PIQUE]
            noms_symboles = {
                Symbole.COEUR: "CÅur",
                Symbole.CARREAU: "Carreau",
                Symbole.TREFLE: "TrÃ¨fle",
                Symbole.PIQUE: "Pique"
            }
            
            for i, symbole in enumerate(symboles):
                bouton = {
                    'rect': pygame.Rect(menu_x + (i % 2) * 120, menu_y + (i // 2) * 60, 100, 50),
                    'symbole': symbole,
                    'texte': noms_symboles[symbole]
                }
                self.boutons_symbole.append(bouton)
                
    def _distribuer_cartes_initiales(self):
        """Distribue les cartes initiales aux joueurs"""
        # Distribuer 5 cartes Ã  chaque joueur
        for _ in range(INITIAL_CARDS):
            self.joueur.recevoir_cartes(self.paquet.piocher(1))
            self.ia.recevoir_cartes(self.paquet.piocher(1))
    
    def changer_joueur(self):
        """Passe au joueur suivant"""
        print(f"[DEBUG] changer_joueur - Avant changement: joueur_actif={self.joueur_actif.nom}, dernier_joueur={getattr(self, 'dernier_joueur', None)}, dernier_chance={getattr(self, 'derniere_chance', False)}")
        
        # VÃ©rifier si un effet a Ã©tÃ© bloquÃ© par un Valet
        if self.effet_bloque_par_valet and not self.partie_terminee:
            print(f"[DEBUG] Effet bloquÃ© par un Valet, {self.joueur_actif.nom} rejoue")
            self.effet_bloque_par_valet = False  # RÃ©initialiser pour le prochain tour
            return  # Le mÃªme joueur rejoue
            
        # VÃ©rifier si un As a Ã©tÃ© jouÃ© au tour prÃ©cÃ©dent
        if self.as_joue and not self.partie_terminee:
            print(f"[DEBUG] Un As a Ã©tÃ© jouÃ©, {self.joueur_actif.nom} rejoue")
            self.as_joue = False  # RÃ©initialiser pour le prochain tour
            return  # Le mÃªme joueur rejoue
        
        if hasattr(self, 'derniere_chance') and self.derniere_chance:
            # Si c'Ã©tait la derniÃ¨re chance de l'adversaire, la partie est terminÃ©e
            self.partie_terminee = True
            self.gagnant = self.dernier_joueur
            print(f"La partie est terminÃ©e ! {self.gagnant.nom} a gagnÃ© !")
            print(f"[DEBUG] Fin de partie - DerniÃ¨re chance, gagnant: {self.gagnant.nom}")
            return
            
        # Si le joueur actuel n'a plus de cartes, il gagne la partie
        if not self.joueur_actif.main:
            self.partie_terminee = True
            self.gagnant = self.joueur_actif
            print(f"La partie est terminÃ©e ! {self.gagnant.nom} a gagnÃ© en se dÃ©barrassant de toutes ses cartes !")
            print(f"[DEBUG] Fin de partie - Plus de cartes, gagnant: {self.gagnant.nom}")
            return
            
        if self.passer_tour:
            ancien_joueur = self.joueur_actif.nom
            print(f"{ancien_joueur} passe son tour!")
            self.passer_tour = False
            # On saute le tour du joueur actuel
            self.joueur_actif = self.ia if self.joueur_actif == self.joueur else self.joueur
            print(f"[DEBUG] Passage de tour: {ancien_joueur} -> {self.joueur_actif.nom}")
            print(f"\n--- Tour de {self.joueur_actif.nom} ---")
            return
            
        # Changer de joueur normalement
        ancien_joueur = self.joueur_actif.nom
        self.joueur_actif = self.ia if self.joueur_actif == self.joueur else self.joueur
        print(f"[DEBUG] Changement de joueur: {ancien_joueur} -> {self.joueur_actif.nom}")
        print(f"\n--- Tour de {self.joueur_actif.nom} ---")
        
        # Si c'est le tour de l'IA, dÃ©marrer son tour
        if self.joueur_actif == self.ia and not self.partie_terminee:
            print("[DEBUG] DÃ©marrage du tour de l'IA depuis changer_joueur")
            self.ia_en_cours = True
            self.dernier_tour_ia = pygame.time.get_ticks()
    
    def commencer_tour_ia(self):
        """DÃ©marre le tour de l'IA avec un dÃ©lai"""
        if not self.partie_terminee and self.joueur_actif == self.ia:
            self.ia_en_cours = True
            self.dernier_tour_ia = pygame.time.get_ticks()
    
    def jouer_tour_ia(self):
        """Fait jouer l'IA"""
        print(f"\n[DEBUG] DÃ©but de jouer_tour_ia - Tour de l'IA")
        
        # VÃ©rifier si l'IA doit piocher des cartes
        if self.cartes_a_piocher > 0:
            print(f"[DEBUG] L'IA doit piocher {self.cartes_a_piocher} cartes")
            self.piocher_carte()
            return True
            
        # Logique de jeu de l'IA
        print("[DEBUG] Recherche d'une carte jouable pour l'IA.")
        derniere_carte = self.paquet.obtenir_derniere_carte_defausse()
        print(f"[DEBUG] DerniÃ¨re carte sur la dÃ©fausse: {derniere_carte}")
        
        # 1. Chercher une carte spÃ©ciale (As, 7, Valet, Joker)
        for i, carte in enumerate(self.ia.main):
            if carte.valeur in [0, 1, 7, 11]:  # Joker, As, 7, Valet
                if not derniere_carte or carte.peut_etre_jouee_sur(derniere_carte):
                    print(f"[DEBUG] L'IA joue une carte spÃ©ciale: {carte}")
                    return self.jouer_carte_ia(i)
        
        # 2. Chercher une carte de mÃªme symbole ou valeur forcÃ©e
        if derniere_carte:
            for i, carte in enumerate(self.ia.main):
                if (carte.symbole == derniere_carte.symbole or 
                    (self.symbole_force and carte.symbole == self.symbole_force)):
                    print(f"[DEBUG] L'IA joue une carte de mÃªme symbole/forcÃ©e: {carte}")
                    return self.jouer_carte_ia(i)
            
            # 3. Chercher une carte de mÃªme valeur
            for i, carte in enumerate(self.ia.main):
                if carte.valeur == derniere_carte.valeur:
                    print(f"[DEBUG] L'IA joue une carte de mÃªme valeur: {carte}")
                    return self.jouer_carte_ia(i)
        
        # Si aucune carte ne peut Ãªtre jouÃ©e, piocher
        print("[DEBUG] Aucune carte jouable trouvÃ©e, l'IA pioche une carte")
        self.piocher_carte()
        return True
        
    def jouer_carte_ia(self, index_carte):
        """MÃ©thode utilitaire pour jouer une carte avec l'IA"""
        if 0 <= index_carte < len(self.ia.main):
            carte = self.ia.main[index_carte]
            print(f"IA joue : {carte}")
            self.ia_carte_jouee = carte
            self.ia_temps_animation = pygame.time.get_ticks()
            
            # Jouer la carte
            if self.jouer_carte(index_carte):
                print("[DEBUG] Carte jouÃ©e avec succÃ¨s par l'IA")
                return True
            else:
                print("[ERREUR] Ãchec de la tentative de jouer la carte, l'IA va piocher")
                self.ia_carte_jouee = None
                self.piocher_carte()
                return True
        return False
    
    def afficher_menu_choix_symbole(self):
        """Affiche un menu pour choisir un nouveau symbole"""
        if not hasattr(self, 'menu_actif') or not self.menu_actif:
            self.menu_actif = True
            self.symbole_choisi = None
            
            # Calculer la position du menu (au centre de l'Ã©cran)
            menu_x = SCREEN_WIDTH // 2 - 100
            menu_y = SCREEN_HEIGHT // 2 - 50
            
            # CrÃ©er des boutons pour chaque symbole
            self.boutons_symbole = []
            symboles = [Symbole.COEUR, Symbole.CARREAU, Symbole.TREFLE, Symbole.PIQUE]
            noms_symboles = {
                Symbole.COEUR: "CÅur",
                Symbole.CARREAU: "Carreau",
                Symbole.TREFLE: "TrÃ¨fle",
                Symbole.PIQUE: "Pique"
            }
            
            for i, symbole in enumerate(symboles):
                bouton = {
                    'rect': pygame.Rect(menu_x + (i % 2) * 120, menu_y + (i // 2) * 60, 100, 50),
                    'symbole': symbole,
                    'texte': noms_symboles[symbole]
                }
                self.boutons_symbole.append(bouton)
    
    def jouer_carte(self, index_carte: int) -> bool:
        """Tente de jouer une carte"""
        if not (0 <= index_carte < len(self.joueur_actif.main)):
            return False
            
        derniere_carte = self.paquet.obtenir_derniere_carte_defausse()
        carte_a_jouer = self.joueur_actif.main[index_carte]
        
        # Si c'est un Valet et qu'il n'y a pas d'attaque en cours, afficher le menu de sÃ©lection
        if carte_a_jouer.valeur == 11 and self.cartes_a_piocher == 0 and not hasattr(self, 'menu_actif'):
            print("[DEBUG] Affichage du menu de sÃ©lection de symbole pour le Valet")
            self.afficher_menu_choix_symbole()
            # Stocker l'index de la carte Valet pour pouvoir la jouer aprÃ¨s la sÃ©lection du symbole
            self.carte_valet_en_attente = index_carte
            return False  # On attend que l'utilisateur choisisse un symbole
        
        # VÃ©rifier si la carte peut Ãªtre jouÃ©e
        if not (carte_a_jouer.peut_etre_jouee_sur(derniere_carte) or 
               (self.symbole_force and carte_a_jouer.symbole == self.symbole_force)):
            print(f"Carte invalide : {carte_a_jouer} ne peut pas Ãªtre jouÃ©e sur {derniere_carte}")
            return False
        
        # VÃ©rifier si on peut contrer une attaque (7 ou Joker) ou bloquer avec un Valet
        if self.cartes_a_piocher > 0:
            if carte_a_jouer.valeur not in [7, 0, 11]:  # 7, Joker (0) ou Valet (11)
                print(f"Vous devez jouer un 7, un Joker ou un Valet pour contrer l'attaque de {self.cartes_a_piocher} cartes!")
                return False
                
            # Si c'est un Valet qui est jouÃ© pour bloquer un effet
            if carte_a_jouer.valeur == 11 and self.cartes_a_piocher > 0:
                print(f"{self.joueur_actif.nom} utilise un Valet pour bloquer l'effet de la carte prÃ©cÃ©dente !")
                self.effet_bloque_par_valet = True
                self.cartes_a_piocher = 0  # Annule l'effet de pioche
                
                # Jouer la carte normalement (sans effet spÃ©cial)
                carte_jouee = self.joueur_actif.jouer_carte(index_carte)
                self.paquet.ajouter_defausse(carte_jouee)
                print(f"{self.joueur_actif.nom} joue : {carte_jouee} (effet bloquÃ©)")
                
                # VÃ©rifier si le joueur a gagnÃ©
                if not self.joueur_actif.main:
                    self.dernier_joueur = self.joueur_actif
                    self.derniere_chance = True
                    self.changer_joueur()
                else:
                    self.changer_joueur()
                return True
            
        # RÃ©initialiser le symbole forcÃ© si on joue une carte valide
        if self.symbole_force and carte_a_jouer.symbole == self.symbole_force:
            self.symbole_force = None
        
        # La carte peut Ãªtre jouÃ©e
        carte_jouee = self.joueur_actif.jouer_carte(index_carte)
        self.paquet.ajouter_defausse(carte_jouee)
        print(f"{self.joueur_actif.nom} joue : {carte_jouee}")
        
        # Gestion des contre-attaques (7 ou Joker)
        if self.cartes_a_piocher > 0 and carte_jouee.valeur in [7, 0]:
            if carte_jouee.valeur == 7:  # 7 ajoute 2 cartes
                self.cartes_a_piocher += 2
                print(f"Contre-attaque ! {self.joueur_actif.nom} ajoute 2 cartes. Total Ã  piocher: {self.cartes_a_piocher}")
            else:  # Joker ajoute 4 cartes
                self.cartes_a_piocher += 4
                print(f"Contre-attaque JOKER ! {self.joueur_actif.nom} ajoute 4 cartes. Total Ã  piocher: {self.cartes_a_piocher}")
            
            # VÃ©rifier si le joueur a gagnÃ© aprÃ¨s avoir jouÃ© sa carte de contre-attaque
            if not self.joueur_actif.main:
                self.dernier_joueur = self.joueur_actif
                self.derniere_chance = True
                self.changer_joueur()
            else:
                self.changer_joueur()  # Passe Ã  l'adversaire qui peut contre-attaquer
            return True
        
        # Appliquer les effets spÃ©ciaux (sauf si c'est un Valet qui a dÃ©jÃ  Ã©tÃ© traitÃ©)
        if carte_jouee.est_speciale() and carte_jouee.valeur != 11:  # Ne pas appliquer l'effet du Valet ici
            carte_jouee.appliquer_effet(self)
        
        # VÃ©rifier si le joueur a gagnÃ© (plus de cartes en main)
        if not self.joueur_actif.main:
            self.dernier_joueur = self.joueur_actif
            self.derniere_chance = True  # Donner une derniÃ¨re chance Ã  l'adversaire
            self.changer_joueur()
            return True
            
        # Gestion des effets de cartes spÃ©ciales
        if carte_jouee.valeur == 1:  # As - Le joueur actif rejoue
            print(f"{self.joueur_actif.nom} joue un As ! Il rejoue.")
            self.as_joue = True  # Active l'effet de l'As pour le prochain tour
            # Ne pas appeler changer_joueur() ici, le joueur actif rejoue
            return True
            
        if carte_jouee.valeur == 7:  # 7 - Fait piocher 2 cartes Ã  l'adversaire
            print(f"{self.joueur_actif.nom} joue un 7 ! L'adversaire doit piocher 2 cartes.")
            self.cartes_a_piocher = 2
            self.changer_joueur()  # Passe au tour de l'adversaire qui pourra contre-attaquer
            return True
            
        if carte_jouee.valeur == 11:  # Valet - Change la couleur
            print(f"{self.joueur_actif.nom} joue un Valet et change la couleur.")
            # Le symbole a dÃ©jÃ  Ã©tÃ© choisi via l'interface
            if hasattr(self, 'symbole_choisi') and self.symbole_choisi:
                print(f"La couleur a Ã©tÃ© changÃ©e en {self.symbole_choisi.name}")
                self.symbole_force = self.symbole_choisi
                delattr(self, 'symbole_choisi')
            self.changer_joueur()
            return True
            
        if carte_jouee.valeur == 0:  # Joker - Fait piocher 4 cartes Ã  l'adversaire
            print(f"JOKER ! {self.joueur_actif.nom} fait piocher 4 cartes Ã  l'adversaire !")
            self.cartes_a_piocher = 4
            self.changer_joueur()  # Passe au tour de l'adversaire qui pourra contre-attaquer
            return True
            
        # Pour les cartes normales, on passe simplement au tour suivant
        self.changer_joueur()
        return True
    
    def piocher_carte(self):
        """Fait piocher une carte au joueur actif et passe le tour Ã  l'adversaire"""
        print(f"[DEBUG] piocher_carte - DÃ©but - Joueur actif: {self.joueur_actif.nom}, cartes_a_piocher: {self.cartes_a_piocher}")
        
        if self.cartes_a_piocher > 0:
            # Cas oÃ¹ le joueur doit piocher des cartes Ã  cause d'un 7 ou d'un joker
            print(f"[DEBUG] Pioche forcÃ©e de {self.cartes_a_piocher} cartes pour {self.joueur_actif.nom}")
            cartes = self.paquet.piocher(self.cartes_a_piocher)
            if cartes:  # Si des cartes ont Ã©tÃ© piochÃ©es
                # Position de dÃ©part de l'animation (haut de l'Ã©cran pour l'IA, bas pour le joueur)
                if self.joueur_actif.est_ia:
                    depart = (self.ecran.get_width() // 2, 0)
                else:
                    depart = (self.ecran.get_width() // 2, self.ecran.get_height())
                
                # Position d'arrivÃ©e (main du joueur)
                arrivee = (100 + len(self.joueur_actif.main) * 30, 
                          self.ecran.get_height() - 150 if not self.joueur_actif.est_ia else 50)
                
                # DÃ©marrer l'animation pour chaque carte
                for i, carte in enumerate(cartes):
                    # Positionner la carte pour l'animation
                    carte.rect.x, carte.rect.y = depart
                    # DÃ©marrer l'animation avec un lÃ©ger dÃ©calage pour chaque carte
                    pygame.time.delay(100 * i)  # DÃ©lai entre chaque animation
                    self._demarrer_animation_pioche(carte, depart, arrivee)
                    # Attendre que l'animation soit terminÃ©e
                    while not self._mettre_a_jour_animation_pioche():
                        pygame.time.delay(16)  # ~60 FPS
                        self.afficher()
                        pygame.display.flip()
                
                self.joueur_actif.recevoir_cartes(cartes)
                print(f"{self.joueur_actif.nom} pioche {len(cartes)} cartes!")
                self.cartes_a_piocher = 0
                
                # Le tour passe automatiquement Ã  l'adversaire aprÃ¨s avoir piochÃ©
                print(f"[DEBUG] Avant changement de joueur (pioche forcÃ©e)")
                self.changer_joueur()
                print(f"[DEBUG] AprÃ¨s changement de joueur (pioche forcÃ©e), nouveau joueur: {self.joueur_actif.nom}")
                
                # Si c'est au tour de l'IA, on active son tour
                if self.joueur_actif.est_ia and not self.partie_terminee:
                    print("[DEBUG] Activation du tour de l'IA aprÃ¨s pioche forcÃ©e")
                    self.ia_en_cours = True
                    self.dernier_tour_ia = pygame.time.get_ticks()
            return
        
        # Pioche normale (quand le joueur ne peut pas jouer)
        print("[DEBUG] Pioche normale pour", self.joueur_actif.nom)
        cartes_piochees = self.paquet.piocher(1)
        if not cartes_piochees:  # Si le paquet est vide
            print("Plus de cartes dans le paquet!")
            self.partie_terminee = True
            return
        
        # Position de dÃ©part de l'animation (haut de l'Ã©cran pour l'IA, bas pour le joueur)
        if self.joueur_actif.est_ia:
            depart = (self.ecran.get_width() // 2, 0)
        else:
            depart = (self.ecran.get_width() // 2, self.ecran.get_height())
        
        # Position d'arrivÃ©e (main du joueur)
        arrivee = (100 + len(self.joueur_actif.main) * 30, 
                  self.ecran.get_height() - 150 if not self.joueur_actif.est_ia else 50)
        
        # DÃ©marrer l'animation
        derniere_carte_piochee = cartes_piochees[-1]
        derniere_carte_piochee.rect.x, derniere_carte_piochee.rect.y = depart
        self._demarrer_animation_pioche(derniere_carte_piochee, depart, arrivee)
        
        # Attendre que l'animation soit terminÃ©e
        while not self._mettre_a_jour_animation_pioche():
            pygame.time.delay(16)  # ~60 FPS
            self.afficher()
            pygame.display.flip()
            
        self.joueur_actif.recevoir_cartes(cartes_piochees)
        print(f"{self.joueur_actif.nom} pioche une carte: {derniere_carte_piochee}")
        
        # Piocher une carte termine automatiquement le tour du joueur
        print(f"[DEBUG] Avant changement de joueur (pioche normale), joueur actuel: {self.joueur_actif.nom}")
        self.changer_joueur()
        print(f"[DEBUG] AprÃ¨s changement de joueur (pioche normale), nouveau joueur: {self.joueur_actif.nom}")
        
        # Si c'est au tour de l'IA, on active son tour
        if self.joueur_actif.est_ia and not self.partie_terminee:
            print("[DEBUG] Activation du tour de l'IA aprÃ¨s pioche normale")
            self.ia_en_cours = True
            self.dernier_tour_ia = pygame.time.get_ticks()
    
    def mettre_a_jour(self):
        """Met Ã  jour l'Ã©tat du jeu"""
        # VÃ©rifier si c'est le tour de l'IA et que la partie n'est pas terminÃ©e
        if self.joueur_actif == self.ia and not self.partie_terminee:
            print(f"\n[DEBUG] Tour de l'IA - ia_en_cours={self.ia_en_cours}, partie_terminee={self.partie_terminee}")
            
            # VÃ©rifier si l'IA n'a plus de cartes (victoire de l'IA)
            if not self.ia.main:
                print("[DEBUG] L'IA n'a plus de cartes, elle a gagnÃ©!")
                self.partie_terminee = True
                self.gagnant = self.ia
                return
                
            # Si l'IA n'est pas dÃ©jÃ  en train de jouer, dÃ©marrer son tour
            if not self.ia_en_cours:
                print("[DEBUG] DÃ©marrage du tour de l'IA")
                self.ia_en_cours = True
                self.dernier_tour_ia = pygame.time.get_ticks()
                return
                
            # VÃ©rifier si le dÃ©lai minimum est Ã©coulÃ©
            temps_actuel = pygame.time.get_ticks()
            if temps_actuel - self.dernier_tour_ia >= self.ia_delai_entre_tours:
                print("[DEBUG] ExÃ©cution du tour de l'IA")
                # Jouer le tour de l'IA
                self.jouer_tour_ia()
        
        # VÃ©rifier si la partie est terminÃ©e (joueur n'a plus de cartes)
        if not self.partie_terminee and self.joueur_actif == self.joueur and not self.joueur.main:
            print("[DEBUG] Le joueur n'a plus de cartes, il a gagnÃ©!")
            self.animation_pioche.dessiner(self.ecran, (self.animation_pioche.rect.x, self.animation_pioche.rect.y))
        
        # Afficher la pioche (dos de carte) Ã  gauche de la dÃ©fausse
        if hasattr(self.paquet, 'cartes') and len(self.paquet.cartes) > 0:
            pioche_x = PILE_POS[0] - CARD_WIDTH - 20  # 20 pixels d'espacement
            pioche_y = PILE_POS[1]
            
            # Dessiner plusieurs cartes dÃ©calÃ©es pour l'effet de pile
            nb_cartes_visibles = min(3, len(self.paquet.cartes))
            for i in range(nb_cartes_visibles):
                offset = i * 2  # DÃ©calage de 2 pixels pour chaque carte de la pile
                # Dessiner le rectangle de la carte avec une bordure
                pygame.draw.rect(self.ecran, (0, 0, 120), 
                              (pioche_x + offset, pioche_y + offset, 
                               CARD_WIDTH, CARD_HEIGHT))
                pygame.draw.rect(self.ecran, (200, 200, 200), 
                              (pioche_x + offset, pioche_y + offset, 
                               CARD_WIDTH, CARD_HEIGHT), 2)
            
            # Dessiner le dos de la carte principale par-dessus
            pygame.draw.rect(self.ecran, (0, 0, 150), 
                          (pioche_x, pioche_y, CARD_WIDTH, CARD_HEIGHT))
            pygame.draw.rect(self.ecran, (255, 255, 255), 
                          (pioche_x, pioche_y, CARD_WIDTH, CARD_HEIGHT), 2)
            
            # Ajouter un motif de carte retournÃ©e
            pygame.draw.rect(self.ecran, (30, 30, 150), 
                          (pioche_x + 20, pioche_y + 20, 
                           CARD_WIDTH - 40, CARD_HEIGHT - 40))
            pygame.draw.rect(self.ecran, (80, 80, 200), 
                          (pioche_x + 30, pioche_y + 30, 
                           CARD_WIDTH - 60, CARD_HEIGHT - 60))
            
            # Afficher le nombre de cartes restantes dans un badge
            texte = self.police.render(str(len(self.paquet.cartes)), True, (255, 255, 255))
            # CrÃ©er un fond arrondi pour le compteur
            counter_bg = pygame.Surface((texte.get_width() + 20, texte.get_height() + 10), pygame.SRCALPHA)
            pygame.draw.rect(counter_bg, (0, 0, 0, 180), 
                          (0, 0, texte.get_width() + 20, texte.get_height() + 10), 
                          border_radius=10)
            self.ecran.blit(counter_bg, (pioche_x + CARD_WIDTH - 30, pioche_y + CARD_HEIGHT - 30))
            # Afficher le texte du compteur
            self.ecran.blit(texte, (pioche_x + CARD_WIDTH - 20, pioche_y + CARD_HEIGHT - 25))
            
        # Afficher la pile de dÃ©fausse (zone de dÃ©pÃ´t des cartes)
        if hasattr(self.paquet, 'defausse') and len(self.paquet.defausse) > 0:
            derniere_carte = self.paquet.defausse[-1]
            defausse_x = PILE_POS[0]
            defausse_y = PILE_POS[1]
            
            # Afficher plusieurs cartes dÃ©calÃ©es pour l'effet de pile (comme pour la pioche)
            nb_cartes_visibles = min(3, len(self.paquet.defausse))
            for i in range(nb_cartes_visibles):
                offset = i * 2  # DÃ©calage de 2 pixels pour chaque carte de la pile
                # Dessiner le rectangle de la carte avec une bordure (mÃªme style que la pioche)
                pygame.draw.rect(self.ecran, (0, 0, 120), 
                              (defausse_x + offset, defausse_y + offset, 
                               derniere_carte.rect.width, derniere_carte.rect.height))
                pygame.draw.rect(self.ecran, (200, 200, 200), 
                              (defausse_x + offset, defausse_y + offset, 
                               derniere_carte.rect.width, derniere_carte.rect.height), 2)
            
            # Afficher la derniÃ¨re carte de la dÃ©fausse (face visible)
            derniere_carte.dessiner(self.ecran, (defausse_x, defausse_y))
            
            # Afficher un contour pour indiquer la zone de dÃ©pÃ´t (seulement si c'est le tour du joueur)
            if self.joueur_actif == self.joueur and not hasattr(self, 'menu_actif'):
                # Utiliser la taille rÃ©elle de la carte pour le contour
                contour_width = derniere_carte.rect.width + 10
                contour_height = derniere_carte.rect.height + 10
                contour = pygame.Surface((contour_width, contour_height), pygame.SRCALPHA)
                pygame.draw.rect(contour, (255, 255, 255, 100), 
                              (0, 0, contour_width, contour_height), 2, border_radius=5)
                self.ecran.blit(contour, (defausse_x - 5, defausse_y - 5))
        
        # Afficher les cartes de l'IA (face cachÃ©e)
        for i, _ in enumerate(self.ia.main):
                        # Utiliser la largeur du dos de la carte ou la largeur par défaut
            card_width = Carte._dos_carte.get_width() if hasattr(Carte, '_dos_carte') and Carte._dos_carte else CARD_WIDTH
                            # Utiliser la largeur réelle de la carte pour le positionnement
            card_width = Carte._dos_carte.get_width() if hasattr(Carte, '_dos_carte') and Carte._dos_carte else CARD_WIDTH
            x = 50 + i * (card_width // 2)  # Chevauchement partiel des cartes
            card_height = Carte._dos_carte.get_height() if hasattr(Carte, '_dos_carte') and Carte._dos_carte else CARD_HEIGHT
            if i > 0 and i == len(self.ia.main) - 1:
                x -= 20  # Ajustement pour la derniÃ¨re carte
            y = AI_HAND_Y
            
            # Afficher le dos de la carte pour l'IA
            if hasattr(Carte, '_dos_carte') and Carte._dos_carte:
                self.ecran.blit(Carte._dos_carte, (x, y))
            else:
                                pygame.draw.rect(self.ecran, (0, 0, 150), (x, y, card_width, card_height), border_radius=5)
                                pygame.draw.rect(self.ecran, (0, 0, 0), (x, y, card_width, card_height), 2, border_radius=5)
        
        # Afficher les cartes du joueur (sauf celle en cours de dÃ©placement)
        for i, carte in enumerate(self.joueur.main):
            if i != self.carte_selectionnee:  # Ne pas afficher la carte sÃ©lectionnÃ©e ici
                                # Utiliser la largeur réelle de la carte pour le positionnement
                card_width = Carte._dos_carte.get_width() if hasattr(Carte, '_dos_carte') and Carte._dos_carte else CARD_WIDTH
                x = 50 + i * (card_width // 2)
                if i > 0 and i == len(self.joueur.main) - 1:
                    x -= 20
                y = PLAYER_HAND_Y
                # Mettre Ã  jour la position de la carte
                carte.rect.x = x
                carte.rect.y = y
                # Dessiner la carte Ã  sa position actuelle
                carte.dessiner(self.ecran, (x, y))
        
        # Afficher la carte sÃ©lectionnÃ©e par-dessus tout le reste
        if self.carte_selectionnee is not None and self.carte_selectionnee < len(self.joueur.main):
            carte = self.joueur.main[self.carte_selectionnee]
            # La position est dÃ©jÃ  mise Ã  jour par _gerer_deplacement_souris
            carte.dessiner(self.ecran, (carte.rect.x, carte.rect.y))
            
        # Afficher la carte que l'IA est en train de jouer
        if self.ia_carte_jouee is not None and self.ia_en_cours:
            # Calculer la position actuelle de la carte pendant l'animation
            temps_ecoule = pygame.time.get_ticks() - self.ia_temps_animation
            duree_animation = 500  # 0.5 seconde
            progression = min(temps_ecoule / duree_animation, 1.0)
            
            # Position de dÃ©part (main de l'IA)
            x_depart = 50 + (self.ia.main.index(self.ia_carte_jouee) if self.ia_carte_jouee in self.ia.main else 0) * (CARD_WIDTH // 2)
            y_depart = AI_HAND_Y
            
            # Position d'arrivÃ©e (pile de dÃ©fausse)
            x_arrivee = PILE_POS[0]
            y_arrivee = PILE_POS[1]
            
            # Position actuelle (interpolation linÃ©aire)
            x = x_depart + (x_arrivee - x_depart) * progression
            y = y_depart + (y_arrivee - y_depart) * progression
            
            # Afficher la carte Ã  la position actuelle
            self.ia_carte_jouee.dessiner(self.ecran, (int(x), int(y)))
        
        # Afficher les informations des joueurs
        self._afficher_infos_joueurs()
        
        # Afficher un message si c'est la derniÃ¨re chance
        if hasattr(self, 'derniere_chance') and self.derniere_chance:
            last_chance_text = self.gros_texte.render("DERNIÃRE CHANCE!", True, (255, 0, 0))
            text_rect = last_chance_text.get_rect(center=(SCREEN_WIDTH//2, 50))
            self.ecran.blit(last_chance_text, text_rect)
        
        # Afficher un message de fin de partie si nÃ©cessaire
        if self.partie_terminee:
            self._afficher_ecran_fin()
    
    def _afficher_infos_joueurs(self):
        """Affiche les informations des joueurs"""
        # Joueur humain
        texte_joueur = f"{self.joueur.nom}: {self.joueur.coeurs} â¤ | Cartes: {len(self.joueur.main)}"
        surf_texte = self.police.render(texte_joueur, True, WHITE)
        self.ecran.blit(surf_texte, (20, SCREEN_HEIGHT - 40))
        
        # IA
        texte_ia = f"{self.ia.nom}: {self.ia.coeurs} â¤ | Cartes: {len(self.ia.main)}"
        surf_texte = self.police.render(texte_ia, True, WHITE)
        self.ecran.blit(surf_texte, (20, 20))
        
        # Tour actuel
        tour_texte = f"Tour: {self.joueur_actif.nom}"
        surf_tour = self.police.render(tour_texte, True, WHITE)
        self.ecran.blit(surf_tour, (SCREEN_WIDTH // 2 - 50, 20))
    
    def _afficher_ecran_fin(self):
        """Affiche l'Ã©cran de fin de partie"""
        # CrÃ©er une surface semi-transparente pour le fond
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Noir semi-transparent
        self.ecran.blit(overlay, (0, 0))
        
        # DÃ©terminer le message de victoire
        if hasattr(self, 'gagnant') and self.gagnant and self.gagnant == self.joueur:
            texte = "FÃ©licitations, vous avez gagnÃ©!"
            couleur = GOLD
        else:
            texte = "L'IA a gagnÃ©..."
            couleur = RED
            
        # Afficher le message principal
        texte_surface = self.gros_texte.render(texte, True, couleur)
        texte_rect = texte_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
        self.ecran.blit(texte_surface, texte_rect)
        
        # Afficher les instructions pour rejouer
        instructions = self.police.render("Appuyez sur R pour rejouer ou ECHAP pour quitter", True, WHITE)
        instructions_rect = instructions.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
        self.ecran.blit(instructions, instructions_rect)
    
    def gerer_clic_souris(self, pos_souris, type_evenement):
        """GÃ¨re les Ã©vÃ©nements de souris
        
        Args:
            pos_souris: Tuple (x, y) de la position de la souris
            type_evenement: Type d'Ã©vÃ©nement ('down', 'up', 'motion')
        """
        # Si le menu de sÃ©lection de symbole est actif
        if hasattr(self, 'menu_actif') and self.menu_actif and type_evenement == 'down':
            # VÃ©rifier si un bouton de symbole a Ã©tÃ© cliquÃ©
            for bouton in self.boutons_symbole:
                if bouton['rect'].collidepoint(pos_souris):
                    print(f"[DEBUG] Symbole sÃ©lectionnÃ©: {bouton['symbole']}")
                    self.symbole_choisi = bouton['symbole']
                    self.menu_actif = False  # Fermer le menu
                    
                    # Si c'Ã©tait un Valet qui attendait la sÃ©lection d'un symbole
                    if hasattr(self, 'carte_valet_en_attente'):
                        # Rejouer la carte Valet maintenant que le symbole est choisi
                        index = self.carte_valet_en_attente
                        delattr(self, 'carte_valet_en_attente')
                        self.jouer_carte(index)
                    return True  # ÃvÃ©nement traitÃ©
            return False
            
        # Gestion du glisser-dÃ©poser des cartes (logique existante)
        if type_evenement == 'down' and not self.partie_terminee and self.joueur_actif == self.joueur:
            # VÃ©rifier si on a cliquÃ© sur une carte du joueur
            for i, carte in enumerate(self.joueur.main):
                if carte.rect.collidepoint(pos_souris):
                    self.carte_selectionnee = i
                    self.drag_en_cours = True
                    return True
                    
        elif type_evenement == 'up' and self.drag_en_cours and self.carte_selectionnee is not None:
            self.drag_en_cours = False
            if self.carte_selectionnee < len(self.joueur.main):
                # VÃ©rifier si la carte est dÃ©posÃ©e sur la pile de dÃ©fausse
                derniere_carte = self.paquet.obtenir_derniere_carte_defausse()
                if derniere_carte and self.joueur.main[self.carte_selectionnee].peut_etre_jouee_sur(derniere_carte):
                    self.jouer_carte(self.carte_selectionnee)
                # RÃ©initialiser la position de la carte
                self.carte_selectionnee = None
            return True
            
        elif type_evenement == 'motion' and self.drag_en_cours and self.carte_selectionnee is not None:
            # Mettre Ã  jour la position de la carte pendant le glisser
            if self.carte_selectionnee < len(self.joueur.main):
                self.joueur.main[self.carte_selectionnee].rect.x = pos_souris[0] - CARD_WIDTH // 2
                self.joueur.main[self.carte_selectionnee].rect.y = pos_souris[1] - CARD_HEIGHT // 2
            return True
            
        return False
        
    def afficher(self):
        """Affiche l'Ã©tat actuel du jeu"""
        # Effacer l'Ã©cran
        self.ecran.fill(DARK_GREEN)
        
        # Afficher le menu de sÃ©lection de symbole si actif
        if hasattr(self, 'menu_actif') and self.menu_actif:
            # CrÃ©er un fond semi-transparent
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            s.fill((0, 0, 0, 180))  # Noir semi-transparent
            self.ecran.blit(s, (0, 0))
            
            # Afficher le titre
            texte_titre = self.police.render("Choisissez un symbole :", True, WHITE)
            self.ecran.blit(texte_titre, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 100))
            
            # Afficher les boutons
            for bouton in self.boutons_symbole:
                # Dessiner le bouton
                pygame.draw.rect(self.ecran, WHITE, bouton['rect'], 2)
                pygame.draw.rect(self.ecran, (50, 50, 50), bouton['rect'].inflate(-4, -4))
                
                # Afficher le texte du bouton
                texte = self.police.render(bouton['texte'], True, WHITE)
                texte_rect = texte.get_rect(center=bouton['rect'].center)
                self.ecran.blit(texte, texte_rect)
            
            # Ne pas afficher le reste du jeu tant que le menu est actif
            return
        
        # Afficher l'animation de pioche si elle est en cours
        if self.animation_pioche:
            self.animation_pioche.dessiner(self.ecran, (self.animation_pioche.rect.x, self.animation_pioche.rect.y))
        
        # Afficher la pioche (dos de carte) Ã  gauche de la dÃ©fausse
        if hasattr(self.paquet, 'cartes') and len(self.paquet.cartes) > 0:
            pioche_x = PILE_POS[0] - CARD_WIDTH - 20  # 20 pixels d'espacement
            pioche_y = PILE_POS[1]
            
            # Dessiner plusieurs cartes dÃ©calÃ©es pour l'effet de pile
            nb_cartes_visibles = min(3, len(self.paquet.cartes))
            for i in range(nb_cartes_visibles):
                offset = i * 2  # DÃ©calage de 2 pixels pour chaque carte de la pile
                # Dessiner le rectangle de la carte avec une bordure
                pygame.draw.rect(self.ecran, (0, 0, 120), 
                              (pioche_x + offset, pioche_y + offset, 
                               CARD_WIDTH, CARD_HEIGHT))
                pygame.draw.rect(self.ecran, (200, 200, 200), 
                              (pioche_x + offset, pioche_y + offset, 
                               CARD_WIDTH, CARD_HEIGHT), 2)
            
            # Dessiner le dos de la carte principale par-dessus
            pygame.draw.rect(self.ecran, (0, 0, 150), 
                          (pioche_x, pioche_y, CARD_WIDTH, CARD_HEIGHT))
            pygame.draw.rect(self.ecran, (255, 255, 255), 
                          (pioche_x, pioche_y, CARD_WIDTH, CARD_HEIGHT), 2)
            
            # Ajouter un motif de carte retournÃ©e
            pygame.draw.rect(self.ecran, (30, 30, 150), 
                          (pioche_x + 20, pioche_y + 20, 
                           CARD_WIDTH - 40, CARD_HEIGHT - 40))
            pygame.draw.rect(self.ecran, (80, 80, 200), 
                          (pioche_x + 30, pioche_y + 30, 
                           CARD_WIDTH - 60, CARD_HEIGHT - 60))
            
            # Afficher le nombre de cartes restantes dans un badge
            texte = self.police.render(str(len(self.paquet.cartes)), True, (255, 255, 255))
            # CrÃ©er un fond arrondi pour le compteur
            counter_bg = pygame.Surface((texte.get_width() + 20, texte.get_height() + 10), pygame.SRCALPHA)
            pygame.draw.rect(counter_bg, (0, 0, 0, 180), 
                          (0, 0, texte.get_width() + 20, texte.get_height() + 10), 
                          border_radius=10)
            self.ecran.blit(counter_bg, (pioche_x + CARD_WIDTH - 30, pioche_y + CARD_HEIGHT - 30))
            # Afficher le texte du compteur
            self.ecran.blit(texte, (pioche_x + CARD_WIDTH - 20, pioche_y + CARD_HEIGHT - 25))
            
        # Afficher la pile de dÃ©fausse (zone de dÃ©pÃ´t des cartes)
        if hasattr(self.paquet, 'defausse') and len(self.paquet.defausse) > 0:
            # Afficher la derniÃ¨re carte de la dÃ©fausse
            derniere_carte = self.paquet.defausse[-1]
            derniere_carte.dessiner(self.ecran, (PILE_POS[0], PILE_POS[1]))
            
            # Afficher un contour pour indiquer la zone de dÃ©pÃ´t (seulement si c'est le tour du joueur)
            if self.joueur_actif == self.joueur and not hasattr(self, 'menu_actif'):
                # CrÃ©er une surface semi-transparente pour le contour
                contour = pygame.Surface((CARD_WIDTH + 10, CARD_HEIGHT + 10), pygame.SRCALPHA)
                pygame.draw.rect(contour, (255, 255, 255, 100), 
                              (0, 0, CARD_WIDTH + 10, CARD_HEIGHT + 10), 2, border_radius=5)
                self.ecran.blit(contour, (PILE_POS[0] - 5, PILE_POS[1] - 5))
        
        # Afficher les cartes de l'IA (face cachÃ©e)
        for i, _ in enumerate(self.ia.main):
                        # Utiliser la largeur du dos de la carte ou la largeur par défaut
            card_width = Carte._dos_carte.get_width() if hasattr(Carte, '_dos_carte') and Carte._dos_carte else CARD_WIDTH
                            # Utiliser la largeur réelle de la carte pour le positionnement
            card_width = Carte._dos_carte.get_width() if hasattr(Carte, '_dos_carte') and Carte._dos_carte else CARD_WIDTH
            x = 50 + i * (card_width // 2)  # Chevauchement partiel des cartes
            card_height = Carte._dos_carte.get_height() if hasattr(Carte, '_dos_carte') and Carte._dos_carte else CARD_HEIGHT
            if i > 0 and i == len(self.ia.main) - 1:
                x -= 20  # Ajustement pour la derniÃ¨re carte
            y = AI_HAND_Y
            
            # Afficher le dos de la carte pour l'IA
            if hasattr(Carte, '_dos_carte') and Carte._dos_carte:
                self.ecran.blit(Carte._dos_carte, (x, y))
            else:
                                pygame.draw.rect(self.ecran, (0, 0, 150), (x, y, card_width, card_height), border_radius=5)
                                pygame.draw.rect(self.ecran, (0, 0, 0), (x, y, card_width, card_height), 2, border_radius=5)
        
        # Afficher les cartes du joueur (sauf celle en cours de dÃ©placement)
        for i, carte in enumerate(self.joueur.main):
            if i != self.carte_selectionnee:  # Ne pas afficher la carte sÃ©lectionnÃ©e ici
                                # Utiliser la largeur réelle de la carte pour le positionnement
                card_width = Carte._dos_carte.get_width() if hasattr(Carte, '_dos_carte') and Carte._dos_carte else CARD_WIDTH
                x = 50 + i * (card_width // 2)
                if i > 0 and i == len(self.joueur.main) - 1:
                    x -= 20
                y = PLAYER_HAND_Y
                # Mettre Ã  jour la position de la carte
                carte.rect.x = x
                carte.rect.y = y
                # Dessiner la carte Ã  sa position actuelle
                carte.dessiner(self.ecran, (x, y))
        
        # Afficher la carte sÃ©lectionnÃ©e par-dessus tout le reste
        if self.carte_selectionnee is not None and self.carte_selectionnee < len(self.joueur.main):
            carte = self.joueur.main[self.carte_selectionnee]
            # La position est dÃ©jÃ  mise Ã  jour par _gerer_deplacement_souris
            carte.dessiner(self.ecran, (carte.rect.x, carte.rect.y))
            
        # Afficher la carte que l'IA est en train de jouer
        if self.ia_carte_jouee is not None and self.ia_en_cours:
            # Calculer la position actuelle de la carte pendant l'animation
            temps_ecoule = pygame.time.get_ticks() - self.ia_temps_animation
            duree_animation = 500  # 0.5 seconde
            progression = min(temps_ecoule / duree_animation, 1.0)
            
            # Position de dÃ©part (main de l'IA)
            x_depart = 50 + (self.ia.main.index(self.ia_carte_jouee) if self.ia_carte_jouee in self.ia.main else 0) * (CARD_WIDTH // 2)
            y_depart = AI_HAND_Y
            
            # Position d'arrivÃ©e (pile de dÃ©fausse)
            x_arrivee = PILE_POS[0]
            y_arrivee = PILE_POS[1]
            
            # Position actuelle (interpolation linÃ©aire)
            x = x_depart + (x_arrivee - x_depart) * progression
            y = y_depart + (y_arrivee - y_depart) * progression
            
            # Afficher la carte Ã  la position actuelle
            self.ia_carte_jouee.dessiner(self.ecran, (int(x), int(y)))
        
        # Afficher les informations des joueurs
        self._afficher_infos_joueurs()
        
        # Afficher un message si c'est la derniÃ¨re chance
        if hasattr(self, 'derniere_chance') and self.derniere_chance:
            last_chance_text = self.gros_texte.render("DERNIÃRE CHANCE!", True, (255, 0, 0))
            text_rect = last_chance_text.get_rect(center=(SCREEN_WIDTH//2, 50))
            self.ecran.blit(last_chance_text, text_rect)
            x = x_depart + (x_arrivee - x_depart) * progression
            y = y_depart + (y_arrivee - y_depart) * progression
            
            # Afficher la carte Ã  la position actuelle
            self.ia_carte_jouee.dessiner(self.ecran, (int(x), int(y)))
        
        # Afficher les informations des joueurs
        self._afficher_infos_joueurs()
        
        # Afficher un message si c'est la derniÃ¨re chance
        if hasattr(self, 'derniere_chance') and self.derniere_chance:
            last_chance_text = self.gros_texte.render("DERNIÃRE CHANCE!", True, (255, 0, 0))
            text_rect = last_chance_text.get_rect(center=(SCREEN_WIDTH//2, 50))
            self.ecran.blit(last_chance_text, text_rect)


