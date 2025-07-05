import pygame
import sys
import os
from typing import List, Optional, Tuple
from pathlib import Path
from .constants import *
from .card import Carte
from .deck import Deck
from .player import Joueur
from .sound_manager import SoundManager

class ChequeGames:
    def __init__(self, ecran):
        """
        Initialise le jeu avec l'écran fourni.
        Gère les erreurs d'initialisation des polices et des ressources.
        """
        self.ecran = ecran
        
        # Initialisation des polices avec gestion d'erreur
        try:
            self.police = pygame.font.Font(None, 36)
            self.gros_texte = pygame.font.Font(None, 48)
        except Exception as e:
            print(f"Erreur lors du chargement des polices: {e}")
            # Polices de secours
            self.police = pygame.font.SysFont('Arial', 24)
            self.gros_texte = pygame.font.SysFont('Arial', 36)
        
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
        self.dernier_joueur = None  # Pour le cas où le joueur gagne mais l'adversaire peut encore jouer
        
        # Variables pour le glisser-déposer
        self.carte_selectionnee = None
        self.drag_en_cours = False
        self.dernier_clic = 0  # Pour la détection du double-clic
        
        # Variables pour l'animation de l'IA
        self.ia_en_cours = False
        self.ia_carte_jouee = None
        self.ia_position_finale = PILE_POS
        self.ia_temps_animation = 0
        self.ia_delai_entre_tours = 1000  # 1 seconde entre les tours de l'IA
        self.dernier_tour_ia = 0
        
        # Initialisation du gestionnaire de sons
        try:
            self.sound_manager = SoundManager()
        except Exception as e:
            print(f"Erreur lors de l'initialisation du gestionnaire de sons: {e}")
            self.sound_manager = None
        
        # Pour gérer l'effet de l'As (rejouer)
        self.as_joue = False  # Indique si un As a été joué au tour précédent
        
        # Pour gérer le blocage des effets par un Valet
        self.effet_bloque_par_valet = False  # Indique si un effet a été bloqué par un Valet
        
        # Variables pour l'animation de pioche
        self.animation_pioche = None  # Carte en cours d'animation
        self.animation_pioche_depart = None  # Position de départ de l'animation
        self.animation_pioche_arrivee = None  # Position d'arrivée de l'animation
        self.animation_pioche_debut = 0  # Temps de début de l'animation
        self.animation_pioche_duree = 500  # Durée de l'animation en ms
        
        # Initialisation des boutons du menu de sélection de symbole
        self.boutons_symbole = []  # Pour stocker les boutons de sélection de symbole
        
        # Distribution des cartes initiales
        self._distribuer_cartes_initiales()
        
        # Première carte de la défausse (doit être une carte normale)
        while True:
            premiere_carte = self.paquet.piocher(1)[0]
            if not premiere_carte.est_speciale():  # On n'accepte que les cartes normales
                self.paquet.ajouter_defausse(premiere_carte)
                break
            else:
                # Remettre la carte spéciale dans le paquet
                self.paquet.cartes.insert(0, premiere_carte)
    
    def _demarrer_animation_pioche(self, carte, depart, arrivee):
        """Démarre une animation de pioche"""
        self.animation_pioche = carte
        self.animation_pioche_depart = depart
        self.animation_pioche_arrivee = arrivee
        self.animation_pioche_debut = pygame.time.get_ticks()
    
    def _mettre_a_jour_animation_pioche(self):
        """Met à jour l'animation de pioche et retourne True si elle est terminée"""
        if not self.animation_pioche:
            return True
            
        temps_ecoule = pygame.time.get_ticks() - self.animation_pioche_debut
        progression = min(temps_ecoule / self.animation_pioche_duree, 1.0)
        
        # Calcul de la position actuelle (interpolation linéaire)
        x = self.animation_pioche_depart[0] + (self.animation_pioche_arrivee[0] - self.animation_pioche_depart[0]) * progression
        y = self.animation_pioche_depart[1] + (self.animation_pioche_arrivee[1] - self.animation_pioche_depart[1]) * progression
        
        # Mettre à jour la position de la carte
        self.animation_pioche.rect.x = x
        self.animation_pioche.rect.y = y
        
        # Si l'animation est terminée
        if progression >= 1.0:
            self.animation_pioche = None
            return True
        return False
    
    def _afficher_infos_joueurs(self):
        """Affiche les informations des joueurs"""
        # Joueur humain
        texte_joueur = f"{self.joueur.nom}: {self.joueur.coeurs} ♥ | Cartes: {len(self.joueur.main)}"
        surf_texte = self.police.render(texte_joueur, True, WHITE)
        self.ecran.blit(surf_texte, (20, SCREEN_HEIGHT - 40))
        
        # IA
        texte_ia = f"{self.ia.nom}: {self.ia.coeurs} ♥ | Cartes: {len(self.ia.main)}"
        surf_texte = self.police.render(texte_ia, True, WHITE)
        self.ecran.blit(surf_texte, (20, 20))
        
        # Tour actuel
        tour_texte = f"Tour: {self.joueur_actif.nom}"
        surf_tour = self.police.render(tour_texte, True, WHITE)
        self.ecran.blit(surf_tour, (SCREEN_WIDTH // 2 - 50, 20))
        
    def afficher(self):
        """Affiche l'ensemble du jeu"""
        # Afficher la pile de pioche (face cachée)
        if self.paquet.cartes:  # S'il reste des cartes dans la pioche
            # Position de la pile de pioche (à gauche de la défausse)
            pioche_x, pioche_y = PILE_POS[0] - 150, PILE_POS[1]
            
            # Afficher le dos de la carte pour la pioche
            if hasattr(Carte, '_dos_carte') and Carte._dos_carte:
                self.ecran.blit(Carte._dos_carte, (pioche_x, pioche_y))
            else:
                # Si pas d'image de dos, dessiner un rectangle simple
                pygame.draw.rect(self.ecran, (0, 0, 150), 
                              (pioche_x, pioche_y, CARD_WIDTH, CARD_HEIGHT), 
                              border_radius=5)
                pygame.draw.rect(self.ecran, (0, 0, 0), 
                              (pioche_x, pioche_y, CARD_WIDTH, CARD_HEIGHT), 
                              2, border_radius=5)
            
            # Afficher le nombre de cartes restantes dans la pioche
            texte_pioche = self.police.render(str(len(self.paquet.cartes)), True, WHITE)
            self.ecran.blit(texte_pioche, (pioche_x + 10, pioche_y + CARD_HEIGHT + 5))
        
        # Afficher les cartes de la défausse (si elle n'est pas vide)
        if self.paquet.defausse:
            derniere_carte = self.paquet.defausse[-1]
            # Afficher la dernière carte de la défausse
            derniere_carte.dessiner(self.ecran, PILE_POS)
            
            # Afficher un contour pour la défausse
            if hasattr(derniere_carte, 'rect'):
                defausse_x, defausse_y = PILE_POS
                contour_width = derniere_carte.rect.width + 10
                contour_height = derniere_carte.rect.height + 10
                contour = pygame.Surface((contour_width, contour_height), pygame.SRCALPHA)
                pygame.draw.rect(contour, (255, 255, 255, 100), 
                              (0, 0, contour_width, contour_height), 2, border_radius=5)
                self.ecran.blit(contour, (defausse_x - 5, defausse_y - 5))
        
        # Afficher les cartes de l'IA (face cachée)
        for i, _ in enumerate(self.ia.main):
            # Utiliser la largeur du dos de la carte ou la largeur par défaut
            card_width = Carte._dos_carte.get_width() if hasattr(Carte, '_dos_carte') and Carte._dos_carte else CARD_WIDTH
            # Utiliser la largeur réelle de la carte pour le positionnement
            card_width = Carte._dos_carte.get_width() if hasattr(Carte, '_dos_carte') and Carte._dos_carte else CARD_WIDTH
            x = 50 + i * (card_width // 2)  # Chevauchement partiel des cartes
            card_height = Carte._dos_carte.get_height() if hasattr(Carte, '_dos_carte') and Carte._dos_carte else CARD_HEIGHT
            if i > 0 and i == len(self.ia.main) - 1:
                x -= 20  # Ajustement pour la dernière carte
            y = AI_HAND_Y
            
            # Afficher le dos de la carte pour l'IA
            if hasattr(Carte, '_dos_carte') and Carte._dos_carte:
                self.ecran.blit(Carte._dos_carte, (x, y))
            else:
                pygame.draw.rect(self.ecran, (0, 0, 150), (x, y, card_width, card_height), border_radius=5)
                pygame.draw.rect(self.ecran, (0, 0, 0), (x, y, card_width, card_height), 2, border_radius=5)
        
        # Afficher les cartes du joueur (sauf celle en cours de déplacement)
        for i, carte in enumerate(self.joueur.main):
            if i != self.carte_selectionnee:  # Ne pas afficher la carte sélectionnée ici
                # Obtenir la surface de la carte pour avoir ses dimensions réelles
                surface_carte = carte._creer_surface()
                card_width = surface_carte.get_width()
                
                # Calculer la position x avec un chevauchement des cartes
                x = 50 + i * (card_width // 2)
                if i > 0 and i == len(self.joueur.main) - 1:
                    x -= 20  # Ajustement pour la dernière carte
                    
                y = PLAYER_HAND_Y
                
                # Mettre à jour la position de la carte
                carte.rect.x = x
                carte.rect.y = y
                
                # Dessiner la carte à sa position actuelle
                carte.dessiner(self.ecran, (x, y))
                
        # Afficher la carte sélectionnée par-dessus tout le reste
        if self.carte_selectionnee is not None and self.carte_selectionnee < len(self.joueur.main):
            carte = self.joueur.main[self.carte_selectionnee]
            # La position est déjà mise à jour par _gerer_deplacement_souris
            carte.dessiner(self.ecran, (carte.rect.x, carte.rect.y))
            
        # Afficher la carte que l'IA est en train de jouer
        if self.ia_carte_jouee is not None and self.ia_en_cours:
            # Calculer la position actuelle de la carte pendant l'animation
            temps_ecoule = pygame.time.get_ticks() - self.ia_temps_animation
            duree_animation = 500  # 0.5 seconde
            progression = min(temps_ecoule / duree_animation, 1.0)
            
            # Position de départ (main de l'IA)
            x_depart = 50 + (self.ia.main.index(self.ia_carte_jouee) if self.ia_carte_jouee in self.ia.main else 0) * (CARD_WIDTH // 2)
            y_depart = AI_HAND_Y
            
            # Position d'arrivée (pile de défausse)
            x_arrivee = PILE_POS[0]
            y_arrivee = PILE_POS[1]
            
            # Position actuelle (interpolation linéaire)
            x = x_depart + (x_arrivee - x_depart) * progression
            y = y_depart + (y_arrivee - y_depart) * progression
            
            # Afficher la carte à la position actuelle
            self.ia_carte_jouee.dessiner(self.ecran, (int(x), int(y)))
        
        # Afficher les informations des joueurs
        self._afficher_infos_joueurs()
        
        # Afficher un message si c'est la dernière chance
        if hasattr(self, 'derniere_chance') and self.derniere_chance:
            last_chance_text = self.gros_texte.render("DERNIÈRE CHANCE!", True, (255, 0, 0))
            text_rect = last_chance_text.get_rect(center=(SCREEN_WIDTH//2, 50))
            self.ecran.blit(last_chance_text, text_rect)
    
    def afficher_menu_choix_symbole(self):
        """Affiche un menu pour choisir un nouveau symbole"""
        if not hasattr(self, 'menu_actif') or not self.menu_actif:
            self.menu_actif = True
            self.symbole_choisi = None
            
            # Calculer la position du menu (au centre de l'écran)
            menu_x = SCREEN_WIDTH // 2 - 100
            menu_y = SCREEN_HEIGHT // 2 - 50
            
            # Créer des boutons pour chaque symbole
            self.boutons_symbole = []
            symboles = [Symbole.COEUR, Symbole.CARREAU, Symbole.TREFLE, Symbole.PIQUE]
            noms_symboles = {
                Symbole.COEUR: "Cœur",
                Symbole.CARREAU: "Carreau",
                Symbole.TREFLE: "Trèfle",
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
        # Distribuer 5 cartes à chaque joueur
        for _ in range(INITIAL_CARDS):
            self.joueur.recevoir_cartes(self.paquet.piocher(1))
            self.ia.recevoir_cartes(self.paquet.piocher(1))
    
    def changer_joueur(self):
        """Passe au joueur suivant"""
        print(f"[DEBUG] changer_joueur - Avant changement: joueur_actif={self.joueur_actif.nom}, dernier_joueur={getattr(self, 'dernier_joueur', None)}, dernier_chance={getattr(self, 'derniere_chance', False)}")
        
        # Jouer un son de changement de tour
        if hasattr(self, 'sound_manager') and self.sound_manager:
            self.sound_manager.play('switch')
        
        # Vérifier si un effet a été bloqué par un Valet
        if self.effet_bloque_par_valet and not self.partie_terminee:
            print(f"[DEBUG] Effet bloqué par un Valet, {self.joueur_actif.nom} rejoue")
            self.effet_bloque_par_valet = False  # Réinitialiser pour le prochain tour
            return  # Le même joueur rejoue
            
        # Vérifier si un As a été joué au tour précédent
        if self.as_joue and not self.partie_terminee:
            print(f"[DEBUG] Un As a été joué, {self.joueur_actif.nom} rejoue")
            self.as_joue = False  # Réinitialiser pour le prochain tour
            return  # Le même joueur rejoue
        
        if hasattr(self, 'derniere_chance') and self.derniere_chance:
            # Si c'était la dernière chance de l'adversaire, la partie est terminée
            self.partie_terminee = True
            self.gagnant = self.dernier_joueur
            print(f"La partie est terminée ! {self.gagnant.nom} a gagné !")
            print(f"[DEBUG] Fin de partie - Dernière chance, gagnant: {self.gagnant.nom}")
            return
            
        # Si le joueur actuel n'a plus de cartes, il gagne la partie
        if not self.joueur_actif.main:
            self.partie_terminee = True
            self.gagnant = self.joueur_actif
            print(f"La partie est terminée ! {self.gagnant.nom} a gagné en se débarrassant de toutes ses cartes !")
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
        
        # Si c'est le tour de l'IA, démarrer son tour
        if self.joueur_actif == self.ia and not self.partie_terminee:
            print("[DEBUG] Démarrage du tour de l'IA depuis changer_joueur")
            self.ia_en_cours = True
            self.dernier_tour_ia = pygame.time.get_ticks()
    
    def commencer_tour_ia(self):
        """Démarre le tour de l'IA avec un délai"""
        if not self.partie_terminee and self.joueur_actif == self.ia:
            self.ia_en_cours = True
            self.dernier_tour_ia = pygame.time.get_ticks()
    
    def choisir_meilleur_symbole_ia(self):
        """Choisit le meilleur symbole pour l'IA en fonction de ses cartes"""
        # Compter les occurrences de chaque symbole dans la main de l'IA
        symboles = {}
        for carte in self.ia.main:
            if carte.valeur != 11:  # Ne pas compter les Valets
                if carte.symbole in symboles:
                    symboles[carte.symbole] += 1
                else:
                    symboles[carte.symbole] = 1
        
        # Retourner le symbole le plus présent, ou un symbole aléatoire si aucun symbole n'est trouvé
        if symboles:
            return max(symboles.items(), key=lambda x: x[1])[0]
        else:
            from random import choice
            from .constants import Symbole
            return choice(list(Symbole))
    
    def jouer_tour_ia(self):
        """Fait jouer l'IA"""
        print(f"\n[DEBUG] Début de jouer_tour_ia - Tour de l'IA")
        
        # Vérifier si l'IA doit piocher des cartes
        if self.cartes_a_piocher > 0:
            print(f"[DEBUG] L'IA doit piocher {self.cartes_a_piocher} cartes")
            self.piocher_carte()
            return True
            
        # Logique de jeu de l'IA
        print("[DEBUG] Recherche d'une carte jouable pour l'IA.")
        derniere_carte = self.paquet.obtenir_derniere_carte_defausse()
        print(f"[DEBUG] Dernière carte sur la défausse: {derniere_carte}")
        
        # 1. Chercher une carte spéciale (As, 7, Valet, Joker)
        for i, carte in enumerate(self.ia.main):
            if carte.valeur in [0, 1, 7, 11]:  # Joker, As, 7, Valet
                if not derniere_carte or carte.peut_etre_jouee_sur(derniere_carte):
                    # Si c'est un Valet, choisir le meilleur symbole pour l'IA
                    if carte.valeur == 11 and self.cartes_a_piocher == 0:
                        self.symbole_choisi = self.choisir_meilleur_symbole_ia()
                        print(f"[DEBUG] L'IA a choisi le symbole: {self.symbole_choisi}")
                        self.ia.main[i].symbole = self.symbole_choisi
                    print(f"[DEBUG] L'IA joue une carte spéciale: {carte}")
                    return self.jouer_carte_ia(i)
        
        # 2. Chercher une carte de même symbole ou valeur forcée
        if derniere_carte:
            for i, carte in enumerate(self.ia.main):
                if (carte.symbole == derniere_carte.symbole or 
                    (self.symbole_force and carte.symbole == self.symbole_force)):
                    print(f"[DEBUG] L'IA joue une carte de même symbole/forcée: {carte}")
                    return self.jouer_carte_ia(i)
            
            # 3. Chercher une carte de même valeur
            for i, carte in enumerate(self.ia.main):
                if carte.valeur == derniere_carte.valeur:
                    print(f"[DEBUG] L'IA joue une carte de même valeur: {carte}")
                    return self.jouer_carte_ia(i)
        
        # Si aucune carte ne peut être jouée, piocher
        print("[DEBUG] Aucune carte jouable trouvée, l'IA pioche une carte")
        self.piocher_carte()
        return True
        
    def jouer_carte_ia(self, index_carte):
        """Méthode utilitaire pour jouer une carte avec l'IA"""
        if 0 <= index_carte < len(self.ia.main):
            carte = self.ia.main[index_carte]
            print(f"IA joue : {carte}")
            self.ia_carte_jouee = carte
            self.ia_temps_animation = pygame.time.get_ticks()
            
            # Jouer la carte
            if self.jouer_carte(index_carte):
                print("[DEBUG] Carte jouée avec succès par l'IA")
                return True
            else:
                print("[ERREUR] Échec de la tentative de jouer la carte, l'IA va piocher")
                self.ia_carte_jouee = None
                self.piocher_carte()
                return True
        return False
    
    def afficher_menu_choix_symbole(self):
        """Affiche un menu pour choisir un nouveau symbole"""
        if not hasattr(self, 'menu_actif') or not self.menu_actif:
            self.menu_actif = True
            self.symbole_choisi = None
            
            # Calculer la position du menu (au centre de l'écran)
            menu_x = SCREEN_WIDTH // 2 - 100
            menu_y = SCREEN_HEIGHT // 2 - 50
            
            # Créer des boutons pour chaque symbole
            self.boutons_symbole = []
            symboles = [Symbole.COEUR, Symbole.CARREAU, Symbole.TREFLE, Symbole.PIQUE]
            noms_symboles = {
                Symbole.COEUR: "Cœur",
                Symbole.CARREAU: "Carreau",
                Symbole.TREFLE: "Trèfle",
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
        
        # Si c'est un Valet et qu'il n'y a pas d'attaque en cours, afficher le menu de sélection
        if carte_a_jouer.valeur == 11 and self.cartes_a_piocher == 0 and not hasattr(self, 'menu_actif'):
            print("[DEBUG] Affichage du menu de sélection de symbole pour le Valet")
            self.afficher_menu_choix_symbole()
            # Stocker l'index de la carte Valet pour pouvoir la jouer après la sélection du symbole
            self.carte_valet_en_attente = index_carte
            return False  # On attend que l'utilisateur choisisse un symbole
        
        # Vérifier si la carte peut être jouée
        if not (carte_a_jouer.peut_etre_jouee_sur(derniere_carte) or 
               (self.symbole_force and carte_a_jouer.symbole == self.symbole_force)):
            print(f"Carte invalide : {carte_a_jouer} ne peut pas être jouée sur {derniere_carte}")
            return False
        
        # Vérifier si on peut contrer une attaque (7 ou Joker) ou bloquer avec un Valet
        if self.cartes_a_piocher > 0:
            if carte_a_jouer.valeur not in [7, 0, 11]:  # 7, Joker (0) ou Valet (11)
                print(f"Vous devez jouer un 7, un Joker ou un Valet pour contrer l'attaque de {self.cartes_a_piocher} cartes!")
                return False
                
            # Si c'est un Valet qui est joué pour bloquer un effet
            if carte_a_jouer.valeur == 11 and self.cartes_a_piocher > 0:
                print(f"{self.joueur_actif.nom} utilise un Valet pour bloquer l'effet de la carte précédente !")
                self.effet_bloque_par_valet = True
                self.cartes_a_piocher = 0  # Annule l'effet de pioche
                
                # Jouer la carte normalement (sans effet spécial)
                carte_jouee = self.joueur_actif.jouer_carte(index_carte)
                self.paquet.ajouter_defausse(carte_jouee)
                print(f"{self.joueur_actif.nom} joue : {carte_jouee} (effet bloqué)")
                
                # Vérifier si le joueur a gagné
                if not self.joueur_actif.main:
                    self.dernier_joueur = self.joueur_actif
                    self.derniere_chance = True
                    self.changer_joueur()
                else:
                    self.changer_joueur()
                return True
            
        # Réinitialiser le symbole forcé si on joue une carte valide
        if self.symbole_force and carte_a_jouer.symbole == self.symbole_force:
            self.symbole_force = None
        
        # La carte peut être jouée
        carte_jouee = self.joueur_actif.jouer_carte(index_carte)
        self.paquet.ajouter_defausse(carte_jouee)
        print(f"{self.joueur_actif.nom} joue : {carte_jouee}")
        
        # Gestion des contre-attaques (7 ou Joker)
        if self.cartes_a_piocher > 0 and carte_jouee.valeur in [7, 0]:
            if carte_jouee.valeur == 7:  # 7 ajoute 2 cartes
                self.cartes_a_piocher += 2
                print(f"Contre-attaque ! {self.joueur_actif.nom} ajoute 2 cartes. Total à piocher: {self.cartes_a_piocher}")
            else:  # Joker ajoute 4 cartes
                self.cartes_a_piocher += 4
                print(f"Contre-attaque JOKER ! {self.joueur_actif.nom} ajoute 4 cartes. Total à piocher: {self.cartes_a_piocher}")
            
            # Vérifier si le joueur a gagné après avoir joué sa carte de contre-attaque
            if not self.joueur_actif.main:
                self.dernier_joueur = self.joueur_actif
                self.derniere_chance = True
                self.changer_joueur()
            else:
                self.changer_joueur()  # Passe à l'adversaire qui peut contre-attaquer
            return True
        
        # Appliquer les effets spéciaux (sauf si c'est un Valet qui a déjà été traité)
        if carte_jouee.est_speciale() and carte_jouee.valeur != 11:  # Ne pas appliquer l'effet du Valet ici
            carte_jouee.appliquer_effet(self)
        
        # Vérifier si le joueur a gagné (plus de cartes en main)
        if not self.joueur_actif.main:
            self.dernier_joueur = self.joueur_actif
            self.derniere_chance = True  # Donner une dernière chance à l'adversaire
            self.changer_joueur()
            return True
            
        # Gestion des effets de cartes spéciales
        if carte_jouee.valeur == 1:  # As - Le joueur actif rejoue
            print(f"{self.joueur_actif.nom} joue un As ! Il rejoue.")
            self.as_joue = True  # Active l'effet de l'As pour le prochain tour
            # Ne pas appeler changer_joueur() ici, le joueur actif rejoue
            return True
            
        if carte_jouee.valeur == 7:  # 7 - Fait piocher 2 cartes à l'adversaire
            print(f"{self.joueur_actif.nom} joue un 7 ! L'adversaire doit piocher 2 cartes.")
            self.cartes_a_piocher = 2
            self.changer_joueur()  # Passe au tour de l'adversaire qui pourra contre-attaquer
            return True
            
        if carte_jouee.valeur == 11:  # Valet - Change la couleur
            print(f"{self.joueur_actif.nom} joue un Valet et change la couleur.")
            # Le symbole a déjà été choisi via l'interface
            if hasattr(self, 'symbole_choisi') and self.symbole_choisi:
                print(f"La couleur a été changée en {self.symbole_choisi.name}")
                self.symbole_force = self.symbole_choisi
                delattr(self, 'symbole_choisi')
            self.changer_joueur()
            return True
            
        if carte_jouee.valeur == 0:  # Joker - Fait piocher 4 cartes à l'adversaire
            print(f"JOKER ! {self.joueur_actif.nom} fait piocher 4 cartes à l'adversaire !")
            self.cartes_a_piocher = 4
            self.changer_joueur()  # Passe au tour de l'adversaire qui pourra contre-attaquer
            return True
            
        # Pour les cartes normales, on passe simplement au tour suivant
        self.changer_joueur()
        return True
    
    def piocher_carte(self):
        """Fait piocher une carte au joueur actif et passe le tour à l'adversaire"""
        print(f"[DEBUG] piocher_carte - Début - Joueur actif: {self.joueur_actif.nom}, cartes_a_piocher: {self.cartes_a_piocher}")
        
        if self.cartes_a_piocher > 0:
            # Cas où le joueur doit piocher des cartes à cause d'un 7 ou d'un joker
            print(f"[DEBUG] Pioche forcée de {self.cartes_a_piocher} cartes pour {self.joueur_actif.nom}")
            cartes = self.paquet.piocher(self.cartes_a_piocher)
            if cartes:  # Si des cartes ont été piochées
                # Position de départ de l'animation (haut de l'écran pour l'IA, bas pour le joueur)
                if self.joueur_actif.est_ia:
                    depart = (self.ecran.get_width() // 2, 0)
                else:
                    depart = (self.ecran.get_width() // 2, self.ecran.get_height())
                
                # Position d'arrivée (main du joueur)
                arrivee = (100 + len(self.joueur_actif.main) * 30, 
                          self.ecran.get_height() - 150 if not self.joueur_actif.est_ia else 50)
                
                # Démarrer l'animation pour chaque carte
                for i, carte in enumerate(cartes):
                    # Positionner la carte pour l'animation
                    carte.rect.x, carte.rect.y = depart
                    # Démarrer l'animation avec un léger décalage pour chaque carte
                    pygame.time.delay(100 * i)  # Délai entre chaque animation
                    self._demarrer_animation_pioche(carte, depart, arrivee)
                    # Attendre que l'animation soit terminée
                    while not self._mettre_a_jour_animation_pioche():
                        pygame.time.delay(16)  # ~60 FPS
                        self.afficher()
                        pygame.display.flip()
                
                self.joueur_actif.recevoir_cartes(cartes)
                print(f"{self.joueur_actif.nom} pioche {len(cartes)} cartes!")
                self.cartes_a_piocher = 0
                
                # Le tour passe automatiquement à l'adversaire après avoir pioché
                print(f"[DEBUG] Avant changement de joueur (pioche forcée)")
                self.changer_joueur()
                print(f"[DEBUG] Après changement de joueur (pioche forcée), nouveau joueur: {self.joueur_actif.nom}")
                
                # Si c'est au tour de l'IA, on active son tour
                if self.joueur_actif.est_ia and not self.partie_terminee:
                    print("[DEBUG] Activation du tour de l'IA après pioche forcée")
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
        
        # Position de départ de l'animation (haut de l'écran pour l'IA, bas pour le joueur)
        if self.joueur_actif.est_ia:
            depart = (self.ecran.get_width() // 2, 0)
        else:
            depart = (self.ecran.get_width() // 2, self.ecran.get_height())
        
        # Position d'arrivée (main du joueur)
        arrivee = (100 + len(self.joueur_actif.main) * 30, 
                  self.ecran.get_height() - 150 if not self.joueur_actif.est_ia else 50)
        
        # Démarrer l'animation
        derniere_carte_piochee = cartes_piochees[-1]
        derniere_carte_piochee.rect.x, derniere_carte_piochee.rect.y = depart
        self._demarrer_animation_pioche(derniere_carte_piochee, depart, arrivee)
        
        # Attendre que l'animation soit terminée
        while not self._mettre_a_jour_animation_pioche():
            pygame.time.delay(16)  # ~60 FPS
            self.afficher()
            pygame.display.flip()
            
        self.joueur_actif.recevoir_cartes(cartes_piochees)
        print(f"{self.joueur_actif.nom} pioche une carte: {derniere_carte_piochee}")
        
        # Piocher une carte termine automatiquement le tour du joueur
        print(f"[DEBUG] Avant changement de joueur (pioche normale), joueur actuel: {self.joueur_actif.nom}")
        self.changer_joueur()
        print(f"[DEBUG] Après changement de joueur (pioche normale), nouveau joueur: {self.joueur_actif.nom}")
        
        # Si c'est au tour de l'IA, on active son tour
        if self.joueur_actif.est_ia and not self.partie_terminee:
            print("[DEBUG] Activation du tour de l'IA après pioche normale")
            self.ia_en_cours = True
            self.dernier_tour_ia = pygame.time.get_ticks()
    
    def mettre_a_jour(self):
        """Met à jour l'état du jeu"""
        # Vérifier si c'est le tour de l'IA et que la partie n'est pas terminée
        if self.joueur_actif == self.ia and not self.partie_terminee:
            print(f"\n[DEBUG] Tour de l'IA - ia_en_cours={self.ia_en_cours}, partie_terminee={self.partie_terminee}")
            
            # Vérifier si l'IA n'a plus de cartes (victoire de l'IA)
            if not self.ia.main:
                print("[DEBUG] L'IA n'a plus de cartes, elle a gagné!")
                self.partie_terminee = True
                self.gagnant = self.ia
                return
                
            # Si l'IA n'est pas déjà en train de jouer, démarrer son tour
            if not self.ia_en_cours:
                print("[DEBUG] Démarrage du tour de l'IA")
                self.ia_en_cours = True
                self.dernier_tour_ia = pygame.time.get_ticks()
                return
                
            # Vérifier si le délai minimum est écoulé
            temps_actuel = pygame.time.get_ticks()
            if temps_actuel - self.dernier_tour_ia >= self.ia_delai_entre_tours:
                print("[DEBUG] Exécution du tour de l'IA")
                # Jouer le tour de l'IA
                self.jouer_tour_ia()
        
        # Vérifier si la partie est terminée (joueur n'a plus de cartes)
        if not self.partie_terminee and self.joueur_actif == self.joueur and not self.joueur.main:
            print("[DEBUG] Le joueur n'a plus de cartes, il a gagné!")
            self.animation_pioche.dessiner(self.ecran, (self.animation_pioche.rect.x, self.animation_pioche.rect.y))
        
        # Afficher la pioche (dos de carte) à gauche de la défausse
        if hasattr(self.paquet, 'cartes') and len(self.paquet.cartes) > 0:
            pioche_x = PILE_POS[0] - CARD_WIDTH - 20  # 20 pixels d'espacement
            pioche_y = PILE_POS[1]
            
            # Dessiner plusieurs cartes décalées pour l'effet de pile
            nb_cartes_visibles = min(3, len(self.paquet.cartes))
            for i in range(nb_cartes_visibles):
                offset = i * 2  # Décalage de 2 pixels pour chaque carte de la pile
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
            
            # Ajouter un motif de carte retournée
            pygame.draw.rect(self.ecran, (30, 30, 150), 
                          (pioche_x + 20, pioche_y + 20, 
                           CARD_WIDTH - 40, CARD_HEIGHT - 40))
            pygame.draw.rect(self.ecran, (80, 80, 200), 
                          (pioche_x + 30, pioche_y + 30, 
                           CARD_WIDTH - 60, CARD_HEIGHT - 60))
            
            # Afficher le nombre de cartes restantes dans un badge
            texte = self.police.render(str(len(self.paquet.cartes)), True, (255, 255, 255))
            # Créer un fond arrondi pour le compteur
            counter_bg = pygame.Surface((texte.get_width() + 20, texte.get_height() + 10), pygame.SRCALPHA)
            pygame.draw.rect(counter_bg, (0, 0, 0, 180), 
                          (0, 0, texte.get_width() + 20, texte.get_height() + 10), 
                          border_radius=10)
            self.ecran.blit(counter_bg, (pioche_x + CARD_WIDTH - 30, pioche_y + CARD_HEIGHT - 30))
            # Afficher le texte du compteur
            self.ecran.blit(texte, (pioche_x + CARD_WIDTH - 20, pioche_y + CARD_HEIGHT - 25))
            
        # Afficher la pile de défausse (zone de dépôt des cartes)
        if hasattr(self.paquet, 'defausse') and len(self.paquet.defausse) > 0:
            derniere_carte = self.paquet.defausse[-1]
            defausse_x = PILE_POS[0]
            defausse_y = PILE_POS[1]
            
            # Obtenir les dimensions de la carte depuis la surface créée
            carte_surface = derniere_carte._creer_surface()
            largeur_carte = carte_surface.get_width() if carte_surface else CARD_WIDTH
            hauteur_carte = carte_surface.get_height() if carte_surface else CARD_HEIGHT
            
            # Afficher plusieurs cartes décalées pour l'effet de pile (comme pour la pioche)
            nb_cartes_visibles = min(3, len(self.paquet.defausse))
            for i in range(nb_cartes_visibles):
                offset = i * 2  # Décalage de 2 pixels pour chaque carte de la pile
                # Dessiner le rectangle de la carte avec une bordure (même style que la pioche)
                pygame.draw.rect(self.ecran, (0, 0, 120), 
                              (defausse_x + offset, defausse_y + offset, 
                               largeur_carte, hauteur_carte), 
                              border_radius=12)
                pygame.draw.rect(self.ecran, (200, 200, 200), 
                              (defausse_x + offset, defausse_y + offset, 
                               largeur_carte, hauteur_carte), 
                              2, border_radius=12)
            
            # Afficher la dernière carte de la défausse (face visible)
            derniere_carte.dessiner(self.ecran, (defausse_x, defausse_y))
            
            # Afficher un contour pour indiquer la zone de dépôt (seulement si c'est le tour du joueur)
            if self.joueur_actif == self.joueur and not hasattr(self, 'menu_actif'):
                # Utiliser la taille réelle de la carte pour le contour
                contour_width = largeur_carte + 10
                contour_height = hauteur_carte + 10
                contour = pygame.Surface((contour_width, contour_height), pygame.SRCALPHA)
                pygame.draw.rect(contour, (255, 255, 255, 100), 
                              (0, 0, contour_width, contour_height), 2, border_radius=5)
                self.ecran.blit(contour, (defausse_x - 5, defausse_y - 5))
        
        # Afficher les cartes de l'IA (face cachée)
        for i, _ in enumerate(self.ia.main):
                        # Utiliser la largeur du dos de la carte ou la largeur par d�faut
            card_width = Carte._dos_carte.get_width() if hasattr(Carte, '_dos_carte') and Carte._dos_carte else CARD_WIDTH
                            # Utiliser la largeur r�elle de la carte pour le positionnement
            card_width = Carte._dos_carte.get_width() if hasattr(Carte, '_dos_carte') and Carte._dos_carte else CARD_WIDTH
            x = 50 + i * (card_width // 2)  # Chevauchement partiel des cartes
            card_height = Carte._dos_carte.get_height() if hasattr(Carte, '_dos_carte') and Carte._dos_carte else CARD_HEIGHT
            if i > 0 and i == len(self.ia.main) - 1:
                x -= 20  # Ajustement pour la dernière carte
            y = AI_HAND_Y
            
            # Afficher le dos de la carte pour l'IA
            if hasattr(Carte, '_dos_carte') and Carte._dos_carte:
                self.ecran.blit(Carte._dos_carte, (x, y))
            else:
                                pygame.draw.rect(self.ecran, (0, 0, 150), (x, y, card_width, card_height), border_radius=5)
                                pygame.draw.rect(self.ecran, (0, 0, 0), (x, y, card_width, card_height), 2, border_radius=5)
        
                # Afficher les cartes du joueur (sauf celle en cours de déplacement)
        for i, carte in enumerate(self.joueur.main):
            if i != self.carte_selectionnee:  # Ne pas afficher la carte sélectionnée ici
                # Obtenir la surface de la carte pour avoir ses dimensions réelles
                surface_carte = carte._creer_surface()
                card_width = surface_carte.get_width()
                
                # Calculer la position x avec un chevauchement des cartes
                x = 50 + i * (card_width // 2)
                if i > 0 and i == len(self.joueur.main) - 1:
                    x -= 20  # Ajustement pour la dernière carte
                    
                y = PLAYER_HAND_Y
                
                # Mettre à jour la position de la carte
                carte.rect.x = x
                carte.rect.y = y
                
                # Dessiner la carte à sa position actuelle
                carte.dessiner(self.ecran, (x, y))
        # Afficher la carte sélectionnée par-dessus tout le reste
        if self.carte_selectionnee is not None and self.carte_selectionnee < len(self.joueur.main):
            carte = self.joueur.main[self.carte_selectionnee]
            # La position est déjà mise à jour par _gerer_deplacement_souris
            carte.dessiner(self.ecran, (carte.rect.x, carte.rect.y))
            
        # Afficher la carte que l'IA est en train de jouer
        if self.ia_carte_jouee is not None and self.ia_en_cours:
            # Calculer la position actuelle de la carte pendant l'animation
            temps_ecoule = pygame.time.get_ticks() - self.ia_temps_animation
            duree_animation = 500  # 0.5 seconde
            progression = min(temps_ecoule / duree_animation, 1.0)
            
            # Position de départ (main de l'IA)
            x_depart = 50 + (self.ia.main.index(self.ia_carte_jouee) if self.ia_carte_jouee in self.ia.main else 0) * (CARD_WIDTH // 2)
            y_depart = AI_HAND_Y
            
            # Position d'arrivée (pile de défausse)
            x_arrivee = PILE_POS[0]
            y_arrivee = PILE_POS[1]
            
            # Position actuelle (interpolation linéaire)
            x = x_depart + (x_arrivee - x_depart) * progression
            y = y_depart + (y_arrivee - y_depart) * progression
            
            # Afficher la carte à la position actuelle
            self.ia_carte_jouee.dessiner(self.ecran, (int(x), int(y)))
        
        # Afficher les informations des joueurs
        self._afficher_infos_joueurs()
        
        # Afficher un message si c'est la dernière chance
        if hasattr(self, 'derniere_chance') and self.derniere_chance:
            last_chance_text = self.gros_texte.render("DERNIÈRE CHANCE!", True, (255, 0, 0))
            text_rect = last_chance_text.get_rect(center=(SCREEN_WIDTH//2, 50))
            self.ecran.blit(last_chance_text, text_rect)
        
        if hasattr(self, 'gagnant') and self.gagnant and self.gagnant == self.joueur:
            texte = "Félicitations, vous avez gagné!"
            couleur = GOLD
        else:
            texte = "L'IA a gagné..."
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
        """Gère les événements de souris
        
        Args:
            pos_souris: Tuple (x, y) de la position de la souris
            type_evenement: Type d'événement ('down', 'up', 'motion')
        """
        # Si le menu de sélection de symbole est actif
        if hasattr(self, 'menu_actif') and self.menu_actif and type_evenement == 'down':
            # Vérifier si un bouton de symbole a été cliqué
            for bouton in self.boutons_symbole:
                if bouton['rect'].collidepoint(pos_souris):
                    print(f"[DEBUG] Symbole sélectionné: {bouton['symbole']}")
                    # Jouer un son de clic
                    if hasattr(self, 'sound_manager') and self.sound_manager:
                        self.sound_manager.play('click')
                    self.symbole_choisi = bouton['symbole']
                    self.menu_actif = False  # Fermer le menu
                    
                    # Si c'était un Valet qui attendait la sélection d'un symbole
                    if hasattr(self, 'carte_valet_en_attente'):
                        # Rejouer la carte Valet maintenant que le symbole est choisi
                        index = self.carte_valet_en_attente
                        delattr(self, 'carte_valet_en_attente')
                        self.jouer_carte(index)
                    return True  # Événement traité
            return False
            
        # Vérifier si on a cliqué sur la pioche
        if type_evenement == 'down' and not self.partie_terminee and self.joueur_actif == self.joueur and self.paquet.cartes:
            # Position de la pioche (à gauche de la défausse)
            pioche_x, pioche_y = PILE_POS[0] - 150, PILE_POS[1]
            # Vérifier si le clic est dans la zone de la pioche
            pioche_rect = pygame.Rect(pioche_x, pioche_y, CARD_WIDTH, CARD_HEIGHT)
            if pioche_rect.collidepoint(pos_souris):
                print("[DEBUG] Clic sur la pioche")
                self.piocher_carte()
                return True
                
        # Gestion du glisser-déposer des cartes (logique existante)
        if type_evenement == 'down' and not self.partie_terminee and self.joueur_actif == self.joueur:
            # Vérifier si on a cliqué sur une carte du joueur (en partant de la fin pour sélectionner la carte du dessus)
            for i in range(len(self.joueur.main) - 1, -1, -1):
                if self.joueur.main[i].rect.collidepoint(pos_souris):
                    self.carte_selectionnee = i
                    self.drag_en_cours = True
                    # Jouer un son de clic
                    if hasattr(self, 'sound_manager') and self.sound_manager:
                        self.sound_manager.play('click')
                    return True
                    
        elif type_evenement == 'up' and self.drag_en_cours and self.carte_selectionnee is not None:
            self.drag_en_cours = False
            if self.carte_selectionnee < len(self.joueur.main):
                # Vérifier si la carte est déposée sur la pile de défausse
                derniere_carte = self.paquet.obtenir_derniere_carte_defausse()
                if derniere_carte and self.joueur.main[self.carte_selectionnee].peut_etre_jouee_sur(derniere_carte):
                    # Jouer un son de carte jouée
                    if hasattr(self, 'sound_manager') and self.sound_manager:
                        self.sound_manager.play('card_play')
                    self.jouer_carte(self.carte_selectionnee)
                # Réinitialiser la position de la carte
                self.carte_selectionnee = None
            return True
            
        elif type_evenement == 'motion' and self.drag_en_cours and self.carte_selectionnee is not None:
            # Mettre à jour la position de la carte pendant le glisser
            if self.carte_selectionnee < len(self.joueur.main):
                self.joueur.main[self.carte_selectionnee].rect.x = pos_souris[0] - CARD_WIDTH // 2
                self.joueur.main[self.carte_selectionnee].rect.y = pos_souris[1] - CARD_HEIGHT // 2
        self.ecran.fill(DARK_GREEN)
        
        # Mettre à jour les positions des cartes avant l'affichage
        if hasattr(self, 'joueur') and hasattr(self.joueur, '_mettre_a_jour_positions'):
            self.joueur._mettre_a_jour_positions()
            # Créer une surface semi-transparente pour le menu de sélection
            menu_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            menu_surface.fill((0, 0, 0, 180))  # Noir semi-transparent
            self.ecran.blit(menu_surface, (0, 0))
            
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
        
        # Afficher la pioche (dos de carte) à gauche de la défausse
        if hasattr(self.paquet, 'cartes') and len(self.paquet.cartes) > 0:
            pioche_x = PILE_POS[0] - CARD_WIDTH - 20  # 20 pixels d'espacement
            pioche_y = PILE_POS[1]
            
            # Dessiner plusieurs cartes décalées pour l'effet de pile
            nb_cartes_visibles = min(3, len(self.paquet.cartes))
            for i in range(nb_cartes_visibles):
                offset = i * 2  # Décalage de 2 pixels pour chaque carte de la pile
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
            
            # Ajouter un motif de carte retournée
            pygame.draw.rect(self.ecran, (30, 30, 150), 
                          (pioche_x + 20, pioche_y + 20, 
                           CARD_WIDTH - 40, CARD_HEIGHT - 40))
            pygame.draw.rect(self.ecran, (80, 80, 200), 
                          (pioche_x + 30, pioche_y + 30, 
                           CARD_WIDTH - 60, CARD_HEIGHT - 60))
            
            # Afficher le nombre de cartes restantes dans un badge
            texte = self.police.render(str(len(self.paquet.cartes)), True, (255, 255, 255))
            # Créer un fond arrondi pour le compteur
            counter_bg = pygame.Surface((texte.get_width() + 20, texte.get_height() + 10), pygame.SRCALPHA)
            pygame.draw.rect(counter_bg, (0, 0, 0, 180), 
                          (0, 0, texte.get_width() + 20, texte.get_height() + 10), 
                          border_radius=10)
            self.ecran.blit(counter_bg, (pioche_x + CARD_WIDTH - 30, pioche_y + CARD_HEIGHT - 30))
            # Afficher le texte du compteur
            self.ecran.blit(texte, (pioche_x + CARD_WIDTH - 20, pioche_y + CARD_HEIGHT - 25))
            
        # Afficher la pile de défausse (zone de dépôt des cartes)
        if hasattr(self.paquet, 'defausse') and len(self.paquet.defausse) > 0:
            # Afficher la dernière carte de la défausse
            derniere_carte = self.paquet.defausse[-1]
            derniere_carte.dessiner(self.ecran, (PILE_POS[0], PILE_POS[1]))
            
            # Afficher un contour pour indiquer la zone de dépôt (seulement si c'est le tour du joueur)
            if self.joueur_actif == self.joueur and not hasattr(self, 'menu_actif'):
                # Créer une surface semi-transparente pour le contour
                contour = pygame.Surface((CARD_WIDTH + 10, CARD_HEIGHT + 10), pygame.SRCALPHA)
                pygame.draw.rect(contour, (255, 255, 255, 100), 
                              (0, 0, CARD_WIDTH + 10, CARD_HEIGHT + 10), 2, border_radius=5)
                self.ecran.blit(contour, (PILE_POS[0] - 5, PILE_POS[1] - 5))
        
        # Afficher les cartes de l'IA (face cachée)
        for i, _ in enumerate(self.ia.main):
                        # Utiliser la largeur du dos de la carte ou la largeur par d�faut
            card_width = Carte._dos_carte.get_width() if hasattr(Carte, '_dos_carte') and Carte._dos_carte else CARD_WIDTH
                            # Utiliser la largeur r�elle de la carte pour le positionnement
            card_width = Carte._dos_carte.get_width() if hasattr(Carte, '_dos_carte') and Carte._dos_carte else CARD_WIDTH
            x = 50 + i * (card_width // 2)  # Chevauchement partiel des cartes
            card_height = Carte._dos_carte.get_height() if hasattr(Carte, '_dos_carte') and Carte._dos_carte else CARD_HEIGHT
            if i > 0 and i == len(self.ia.main) - 1:
                x -= 20  # Ajustement pour la dernière carte
            y = AI_HAND_Y
            
            # Afficher le dos de la carte pour l'IA
            if hasattr(Carte, '_dos_carte') and Carte._dos_carte:
                self.ecran.blit(Carte._dos_carte, (x, y))
            else:
                                pygame.draw.rect(self.ecran, (0, 0, 150), (x, y, card_width, card_height), border_radius=5)
                                pygame.draw.rect(self.ecran, (0, 0, 0), (x, y, card_width, card_height), 2, border_radius=5)
        
                # Afficher les cartes du joueur (sauf celle en cours de déplacement)
        for i, carte in enumerate(self.joueur.main):
            if i != self.carte_selectionnee:  # Ne pas afficher la carte sélectionnée ici
                # Obtenir la surface de la carte pour avoir ses dimensions réelles
                surface_carte = carte._creer_surface()
                card_width = surface_carte.get_width()
                
                # Calculer la position x avec un chevauchement des cartes
                x = 50 + i * (card_width // 2)
                if i > 0 and i == len(self.joueur.main) - 1:
                    x -= 20  # Ajustement pour la dernière carte
                    
                y = PLAYER_HAND_Y
                
                # Mettre à jour la position de la carte
                carte.rect.x = x
                carte.rect.y = y
                
                # Dessiner la carte à sa position actuelle
                carte.dessiner(self.ecran, (x, y))
        # Afficher la carte sélectionnée par-dessus tout le reste
        if self.carte_selectionnee is not None and self.carte_selectionnee < len(self.joueur.main):
            carte = self.joueur.main[self.carte_selectionnee]
            # La position est déjà mise à jour par _gerer_deplacement_souris
            carte.dessiner(self.ecran, (carte.rect.x, carte.rect.y))
            
        # Afficher la carte que l'IA est en train de jouer
        if self.ia_carte_jouee is not None and self.ia_en_cours:
            # Calculer la position actuelle de la carte pendant l'animation
            temps_ecoule = pygame.time.get_ticks() - self.ia_temps_animation
            duree_animation = 500  # 0.5 seconde
            progression = min(temps_ecoule / duree_animation, 1.0)
            
            # Position de départ (main de l'IA)
            x_depart = 50 + (self.ia.main.index(self.ia_carte_jouee) if self.ia_carte_jouee in self.ia.main else 0) * (CARD_WIDTH // 2)
            y_depart = AI_HAND_Y
            
            # Position d'arrivée (pile de défausse)
            x_arrivee = PILE_POS[0]
            y_arrivee = PILE_POS[1]
            
            # Position actuelle (interpolation linéaire)
            x = x_depart + (x_arrivee - x_depart) * progression
            y = y_depart + (y_arrivee - y_depart) * progression
            
            # Afficher la carte à la position actuelle
            self.ia_carte_jouee.dessiner(self.ecran, (int(x), int(y)))
        
        # Afficher les informations des joueurs
        self._afficher_infos_joueurs()
        
        # Afficher un message si c'est la dernière chance
        if hasattr(self, 'derniere_chance') and self.derniere_chance:
            last_chance_text = self.gros_texte.render("DERNIÈRE CHANCE!", True, (255, 0, 0))
            text_rect = last_chance_text.get_rect(center=(SCREEN_WIDTH//2, 50))
            self.ecran.blit(last_chance_text, text_rect)
            x = x_depart + (x_arrivee - x_depart) * progression
            y = y_depart + (y_arrivee - y_depart) * progression
            
            # Afficher la carte à la position actuelle
            self.ia_carte_jouee.dessiner(self.ecran, (int(x), int(y)))
        
        # Afficher les informations des joueurs
        self._afficher_infos_joueurs()
        
        # Afficher un message si c'est la dernière chance
        if hasattr(self, 'derniere_chance') and self.derniere_chance:
            last_chance_text = self.gros_texte.render("DERNIÈRE CHANCE!", True, (255, 0, 0))
            text_rect = last_chance_text.get_rect(center=(SCREEN_WIDTH//2, 50))
            self.ecran.blit(last_chance_text, text_rect)













