import os
import pygame
from .constants import (
    Symbole, CARD_WIDTH, CARD_HEIGHT, SCALE_FACTOR, 
    get_couleur_symbole, SYMBOLES, COULEUR_SYMBOLES
)
from pathlib import Path

class Carte:
    """Classe représentant une carte à jouer"""
    
    # Variables de classe pour la gestion des images
    _images_chargees = False
    _images = {}
    _dos_carte = None
    
    @classmethod
    def _charger_images(cls):
        """Charge les images des cartes une seule fois (méthode de classe)"""
        if cls._images_chargees:
            return
            
        # Chemin du dossier des images
        base_dir = Path(__file__).parent.parent
        # Utilisation du dossier 'asset' comme emplacement standard
        image_dir = base_dir / 'asset'
        
        # Créer le dossier s'il n'existe pas
        image_dir.mkdir(parents=True, exist_ok=True)
        
        # Charger le dos de la carte
        try:
            dos_path = image_dir / 'card_back.png'
            if dos_path.exists():
                cls._dos_carte = pygame.image.load(str(dos_path)).convert_alpha()
                # Redimensionner si nécessaire
                if cls._dos_carte.get_size() != (CARD_WIDTH, CARD_HEIGHT):
                    cls._dos_carte = pygame.transform.scale(
                        cls._dos_carte, 
                        (int(CARD_WIDTH * SCALE_FACTOR), int(CARD_HEIGHT * SCALE_FACTOR))
                    )
        except Exception as e:
            print(f"Erreur lors du chargement du dos de la carte: {e}")
            # Créer une surface de secours
            cls._dos_carte = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
            cls._dos_carte.fill((50, 50, 150))  # Fond bleu foncé
            pygame.draw.rect(cls._dos_carte, (100, 100, 255), 
                          (2, 2, CARD_WIDTH-4, CARD_HEIGHT-4), 2)
        
        # Dictionnaire de correspondance entre les symboles et leurs noms
        symbol_mapping = {
            Symbole.COEUR: 'hearts',
            Symbole.CARREAU: 'diamonds',
            Symbole.TREFLE: 'clubs',
            Symbole.PIQUE: 'spades'
        }
        
        # Dictionnaire pour la correspondance des symboles avec les préfixes de fichiers
        symbol_prefixes = {
            Symbole.COEUR: 'card_hearts_',
            Symbole.CARREAU: 'card_diamonds_',
            Symbole.TREFLE: 'card_clubs_',
            Symbole.PIQUE: 'card_spades_'
        }
        
        # Charger les images des cartes pour chaque symbole
        for symbole, symbole_str in symbol_mapping.items():
            for valeur in range(1, 14):  # De 1 (As) à 13 (Roi)
                # Construire le nom du fichier selon le format dans le dossier
                if valeur == 1:
                    valeur_str = 'A'
                elif valeur == 11:
                    valeur_str = 'J'
                elif valeur == 12:
                    valeur_str = 'Q'
                elif valeur == 13:
                    valeur_str = 'K'
                else:
                    valeur_str = f"{valeur:02d}"
                
                # Utiliser le préfixe approprié pour chaque symbole
                prefixe = symbol_prefixes[symbole]
                nom_fichier = f"{prefixe}{valeur_str}.png"
                chemin = image_dir / nom_fichier
                
                try:
                    if chemin.exists():
                        image = pygame.image.load(str(chemin)).convert_alpha()
                        # Redimensionner l'image à la taille standard des cartes
                        new_width = int(CARD_WIDTH * SCALE_FACTOR)
                        new_height = int(CARD_HEIGHT * SCALE_FACTOR)
                        image = pygame.transform.scale(image, (new_width, new_height))
                        cls._images[(valeur, symbole)] = image
                        print(f"Image chargée: {nom_fichier}")
                    else:
                        print(f"Fichier non trouvé: {chemin}")
                except Exception as e:
                    print(f"Erreur lors du chargement de l'image {chemin}: {e}")
        
        cls._images_chargees = True
    
    def __init__(self, valeur: int, symbole: Symbole):
        self.valeur = valeur
        self.symbole = symbole
        self.face_cachee = False
        self.est_selectionnee = False
        self.offset_x = 0
        self.offset_y = 0
        self._charger_images()
        self.surface = self._creer_surface()
        self.rect = self.surface.get_rect()
        self.original_position = (0, 0)
    
    def selectionner(self, pos):
        """Sélectionne la carte et calcule l'offset par rapport à la souris"""
        self.est_selectionnee = True
        self.offset_x = self.rect.x - pos[0]
        self.offset_y = self.rect.y - pos[1]
        self.original_position = (self.rect.x, self.rect.y)
    
    def deselectionner(self):
        """Désélectionne la carte"""
        self.est_selectionnee = False
    
    def deplacer(self, pos):
        """Déplace la carte à la position de la souris"""
        if self.est_selectionnee:
            self.rect.x = pos[0] + self.offset_x
            self.rect.y = pos[1] + self.offset_y
    
    def deplacer_vers(self, pos):
        """Déplace la carte vers la position spécifiée (utilisé pour le glisser-déposer)"""
        self.rect.topleft = (pos[0] - self.rect.width // 2, pos[1] - self.rect.height // 2)
    
    def annuler_deplacement(self):
        """Annule le déplacement et replace la carte à sa position d'origine"""
        self.rect.x, self.rect.y = self.original_position
        self.est_selectionnee = False
    
    def _creer_surface(self):
        """
        Crée la surface graphique de la carte.
        
        Returns:
            pygame.Surface: La surface de la carte, ou une surface vide en cas d'erreur critique.
        """
        try:
            # Si la carte est face cachée, on retourne le dos de la carte
            if self.face_cachee:
                return self._creer_surface_dos_carte()
            
            # Créer la surface pour une carte normale
            return self._creer_surface_carte_normale()
            
        except Exception as e:
            print(f"Erreur critique dans _creer_surface pour {self.valeur} de {self.symbole}: {e}")
            # Retourner une surface vide en cas d'erreur critique
            return pygame.Surface((0, 0), pygame.SRCALPHA)
    
    def _creer_surface_dos_carte(self):
        """Crée une surface pour le dos d'une carte"""
        if hasattr(Carte, '_dos_carte') and Carte._dos_carte is not None:
            return Carte._dos_carte.copy()
        
        # Créer un dos de carte simple si non chargé
        width = int(CARD_WIDTH * SCALE_FACTOR)
        height = int(CARD_HEIGHT * SCALE_FACTOR)
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(surface, (50, 50, 50), (0, 0, width, height), border_radius=12)
        pygame.draw.rect(surface, (100, 0, 0), (3, 3, width-6, height-6), border_radius=10)
        return surface
    
    def _creer_surface_carte_normale(self):
        """Crée une surface pour une carte"""
        cle_image = (self.valeur, self.symbole)
        
        # Vérifier si l'image existe
        if cle_image not in Carte._images:
            print(f"Avertissement: Image non trouvée pour la carte {self.valeur} de {self.symbole}")
            return self._creer_surface_par_defaut()
        
        # Utiliser l'image chargée
        try:
            image = Carte._images[cle_image]
            surface = pygame.Surface((image.get_width(), image.get_height()), pygame.SRCALPHA)
            surface.blit(image, (0, 0))
            return surface
        except Exception as e:
            print(f"Erreur avec l'image de la carte {self.valeur} de {self.symbole}: {e}")
            return self._creer_surface_par_defaut()
        
    def _creer_surface_par_defaut(self):
        """Crée une surface par défaut si l'image n'est pas trouvée"""
        # Créer une surface avec la taille standard des cartes
        width = int(CARD_WIDTH * SCALE_FACTOR)
        height = int(CARD_HEIGHT * SCALE_FACTOR)
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Couleur de fond plus douce (blanc cassé)
        COULEUR_FOND = (250, 250, 245)
        COULEUR_CONTOUR = (50, 50, 50)
        
        # Dessiner le contour de la carte avec des coins arrondis
        pygame.draw.rect(surface, COULEUR_CONTOUR, 
                        (0, 0, width, height), 
                        border_radius=12)
        
        # Fond principal de la carte
        pygame.draw.rect(surface, COULEUR_FOND, 
                        (3, 3, width - 6, height - 6), 
                        border_radius=10)
        
        # Déterminer la couleur en fonction du symbole
        couleur = get_couleur_symbole(self.symbole, self.valeur)
        
        # Ajuster la luminosité pour un meilleur contraste
        if couleur == (255, 0, 0):  # Rouge
            couleur = (200, 0, 0)  # Rouge plus foncé
        elif couleur == (0, 0, 0):  # Noir
            couleur = (30, 30, 30)  # Noir profond
        
        # Police pour les valeurs et symboles
        police_valeur = pygame.font.Font(None, int(28 * SCALE_FACTOR))
        police_symbole = pygame.font.Font(None, int(72 * SCALE_FACTOR))
        police_symbole_petit = pygame.font.Font(None, int(20 * SCALE_FACTOR))
        
        # Afficher la valeur en haut à gauche
        texte_valeur = self._obtenir_texte_valeur()
        if texte_valeur:  # S'assurer que le texte n'est pas vide
            texte = police_valeur.render(texte_valeur, True, couleur)
            surface.blit(texte, (12 * SCALE_FACTOR, 10 * SCALE_FACTOR))
        
        # Afficher le symbole en petit à côté de la valeur
        texte_symbole_petit = police_symbole_petit.render(SYMBOLES.get(self.symbole, '?'), True, couleur)
        surface.blit(texte_symbole_petit, (15 * SCALE_FACTOR, 35 * SCALE_FACTOR))
        
        # Afficher le symbole en grand au centre
        texte_symbole = police_symbole.render(SYMBOLES.get(self.symbole, '?'), True, couleur)
        texte_rect = texte_symbole.get_rect(center=(CARD_WIDTH * SCALE_FACTOR // 2, CARD_HEIGHT * SCALE_FACTOR // 2))
        surface.blit(texte_symbole, texte_rect)
        
        # Afficher la valeur en bas à droite (tournée à l'envers)
        if texte_valeur:  # S'assurer que le texte n'est pas vide
            texte_surface = police_valeur.render(texte_valeur, True, couleur)
            texte_valeur_bas = pygame.transform.rotate(texte_surface, 180)
            surface.blit(texte_valeur_bas, 
                       (CARD_WIDTH * SCALE_FACTOR - 35 * SCALE_FACTOR, 
                        CARD_HEIGHT * SCALE_FACTOR - 35 * SCALE_FACTOR))
        
        # Afficher le symbole en petit en bas à droite (tourné)
        texte_symbole_bas = pygame.transform.rotate(texte_symbole_petit, 180)
        surface.blit(texte_symbole_bas, 
                    (CARD_WIDTH * SCALE_FACTOR - 20 * SCALE_FACTOR, 
                     CARD_HEIGHT * SCALE_FACTOR - 15 * SCALE_FACTOR))
        
        # Effet de brillance subtil en haut à gauche
        brillance = pygame.Surface((CARD_WIDTH * SCALE_FACTOR, 60 * SCALE_FACTOR), pygame.SRCALPHA)
        pygame.draw.rect(brillance, (255, 255, 255, 15), 
                        (0, 0, CARD_WIDTH * SCALE_FACTOR, 60 * SCALE_FACTOR), 
                        border_top_left_radius=10, border_top_right_radius=10)
        surface.blit(brillance, (0, 0))
        
        # Si la carte est sélectionnée, ajouter une bordure jaune
        if hasattr(self, 'est_selectionnee') and self.est_selectionnee:
            pygame.draw.rect(surface, (255, 215, 0), 
                          (0, 0, CARD_WIDTH * SCALE_FACTOR, CARD_HEIGHT * SCALE_FACTOR), 
                          3, border_radius=12)
        
        return surface
    
    def _obtenir_texte_valeur(self):
        """Retourne la représentation textuelle de la valeur de la carte"""
        if self.valeur == 1:  # As
            return "A"
        elif self.valeur == 11:  # Valet
            return "V"
        elif self.valeur == 12:  # Dame
            return "D"
        elif self.valeur == 13:  # Roi
            return "R"
        else:
            return str(self.valeur)
    
    def est_speciale(self):
        """Vérifie si la carte a un effet spécial"""
        return self.valeur in [1, 7, 8, 11]  # As, 7, 8, Valet
    
    def peut_etre_jouee_sur(self, autre_carte):
        """Vérifie si cette carte peut être jouée sur une autre carte"""
        if not autre_carte:
            return True
            
        # Une carte peut être jouée si elle a la même valeur ou le même symbole
        return self.valeur == autre_carte.valeur or self.symbole == autre_carte.symbole
    
    def appliquer_effet(self, jeu):
        """Applique l'effet spécial de la carte"""
        if self.valeur == 1:  # As - Fait passer le tour de l'adversaire
            jeu.passer_tour = True
            print("L'adversaire passe son tour!")
            
        elif self.valeur == 7:  # 7 - Fait piocher 2 cartes
            jeu.cartes_a_piocher += 2
            print(f"L'adversaire doit piocher {jeu.cartes_a_piocher} cartes!")
            
        elif self.valeur == 8:  # 8 - Fait rejouer le même joueur
            jeu.as_joue = True
            print("Rejouez!")
            
        elif self.valeur == 11:  # Valet - Change le sens du jeu
            jeu.sens_jeu *= -1
            print("Sens du jeu inversé!")
            
        # Les autres cartes n'ont pas d'effet spécial
    
    def retourner(self):
        """Retourne la carte (face visible/cachée)"""
        self.face_cachee = not self.face_cachee
        self.surface = self._creer_surface()
    
    def dessiner(self, surface, position=None):
        """Dessine la carte sur la surface donnée à la position spécifiée.
        
        Si position est None, utilise la position actuelle de la carte (self.rect).
        Sinon, dessine la carte à la position spécifiée sans modifier self.rect.
        """
        # Sauvegarder la position actuelle
        old_pos = self.rect.topleft if hasattr(self, 'rect') else (0, 0)
        
        try:
            # Si une position est fournie, créer un nouveau rect temporaire
            if position is not None:
                temp_rect = pygame.Rect(position[0], position[1], 
                                     self.rect.width if hasattr(self, 'rect') else CARD_WIDTH,
                                     self.rect.height if hasattr(self, 'rect') else CARD_HEIGHT)
            else:
                temp_rect = self.rect
            
            # Dessiner la carte
            if self.face_cachee:
                self._dessiner_dos_carte(surface, temp_rect)
            else:
                # Essayer de dessiner avec l'image, sinon utiliser le dessin par défaut
                if (self.valeur, self.symbole) in Carte._images:
                    self._dessiner_avec_image(surface, temp_rect, position)
                else:
                    self._dessiner_face_programmatique(surface, temp_rect)
                    
            # Si la carte est sélectionnée, dessiner un contour jaune
            if hasattr(self, 'est_selectionnee') and self.est_selectionnee:
                pygame.draw.rect(surface, (255, 215, 0), temp_rect, 3, border_radius=12)
                
        except Exception as e:
            print(f"Erreur lors du dessin de la carte: {e}")
            # En cas d'erreur, restaurer l'ancienne position
            if hasattr(self, 'rect'):
                self.rect.topleft = old_pos
            # Créer une surface par défaut en cas d'erreur
            self._creer_surface_par_defaut()
    
    def _dessiner_face_programmatique(self, surface, rect):
        """Dessine la face d'une carte de manière programmatique"""
        # Dessiner le fond de la carte avec des coins arrondis
        pygame.draw.rect(surface, (255, 255, 255), rect, border_radius=12)
        pygame.draw.rect(surface, (0, 0, 0), rect, 2, border_radius=12)
            
        # Obtenir la couleur du texte en fonction du symbole
        text_color = get_couleur_symbole(self.symbole, self.valeur)
            
        # Afficher la valeur et le symbole de la carte
        font = pygame.font.Font(None, 36)
            
        # Afficher la valeur en haut à gauche
        valeur_texte = self._obtenir_texte_valeur()
        if valeur_texte:
            texte = font.render(valeur_texte, True, text_color)
            surface.blit(texte, (rect.x + 10, rect.y + 10))
            
        # Afficher le symbole de la carte
        self._dessiner_symbole(surface, rect, text_color)
    
    def _dessiner_symbole(self, surface, rect, color):
        """Dessine le symbole d'une carte"""
        symbole_texte = SYMBOLES.get(self.symbole, '?')
        if symbole_texte:
            symbole_font = pygame.font.Font(None, 72)
            texte_symbole = symbole_font.render(symbole_texte, True, color)
            texte_rect = texte_symbole.get_rect(center=rect.center)
            surface.blit(texte_symbole, texte_rect)
    
    def _dessiner_avec_image(self, surface, rect, position):
        """Dessine la carte en utilisant une image chargée"""
        try:
            carte_surface = self._creer_surface()
            if carte_surface and carte_surface.get_size() != (0, 0):
                surface.blit(carte_surface, rect.topleft)
            else:
                # En cas d'erreur avec l'image, utiliser le dessin programmatique
                print("Erreur: Surface de carte vide, utilisation du dessin programmatique")
                self._dessiner_face_programmatique(surface, rect)
        except Exception as e:
            print(f"Erreur lors du chargement de l'image: {e}")
            # En cas d'erreur, utiliser le dessin programmatique
            self._dessiner_face_programmatique(surface, rect)
            
    def __str__(self):
        """Retourne une représentation textuelle de la carte"""
        valeur_str = self._obtenir_texte_valeur()
        symbole_str = SYMBOLES.get(self.symbole, '?')
        return f"{valeur_str} de {symbole_str}"
