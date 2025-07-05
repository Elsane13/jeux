import pygame
import sys
from pathlib import Path
from .constants import *
from .constants import MINI_BLACK

class Bouton:
    def __init__(self, x, y, largeur, hauteur, texte, couleur, couleur_texte=WHITE, taille_texte=36):
        self.rect = pygame.Rect(x, y, largeur, hauteur)
        self.couleur = couleur
        self.texte = texte
        self.couleur_texte = couleur_texte
        self.taille_texte = taille_texte
        self.police = pygame.font.Font(None, self.taille_texte)
        self.est_survole = False
    
    def dessiner(self, surface):
        # Dessiner le fond du bouton
        couleur = self.couleur
        if self.est_survole:
            # Rendre la couleur plus claire quand la souris est dessus
            couleur = tuple(min(c + 30, 255) for c in self.couleur)
        
        pygame.draw.rect(surface, couleur, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)
        
        # Dessiner le texte centré
        texte_surface = self.police.render(self.texte, True, self.couleur_texte)
        texte_rect = texte_surface.get_rect(center=self.rect.center)
        surface.blit(texte_surface, texte_rect)
    
    def est_survole_par_souris(self, pos_souris):
        self.est_survole = self.rect.collidepoint(pos_souris)
        return self.est_survole
    
    def est_clique(self, pos_souris, evenement):
        if evenement.type == pygame.MOUSEBUTTONDOWN and evenement.button == 1:
            return self.rect.collidepoint(pos_souris)
        return False


class MenuPrincipal:
    def __init__(self, largeur, hauteur):
        self.largeur = largeur
        self.hauteur = hauteur
        self.surface = pygame.Surface((largeur, hauteur), pygame.SRCALPHA)
        
        # Initialiser la musique d'accueil
        self.musique_accueil = None
        self.initialiser_musique()
        
        # Couleurs du thème
        self.couleur_fond = MINI_BLACK  # Utilisation de la couleur MINI_BLACK
        self.couleur_bouton = (0, 100, 0)   # Vert foncé
        self.couleur_texte = (255, 255, 255) # Blanc
        self.couleur_survol = (0, 128, 0)   # Vert plus clair
        
        # Création des boutons
        bouton_largeur = 300
        bouton_hauteur = 70
        espacement = 30
        y_depart = (hauteur - (3 * bouton_hauteur + 2 * espacement)) // 2
        
        self.bouton_jouer = Bouton(
            (largeur - bouton_largeur) // 2,
            y_depart,
            bouton_largeur, bouton_hauteur,
            "JOUER",
            self.couleur_bouton,
            self.couleur_texte,
            40
        )
        
        self.bouton_regles = Bouton(
            (largeur - bouton_largeur) // 2,
            y_depart + bouton_hauteur + espacement,
            bouton_largeur, bouton_hauteur,
            "RÈGLES",
            self.couleur_bouton,
            self.couleur_texte,
            40
        )
        
        self.bouton_quitter = Bouton(
            (largeur - bouton_largeur) // 2,
            y_depart + 2 * (bouton_hauteur + espacement),
            bouton_largeur, bouton_hauteur,
            "QUITTER",
            (139, 0, 0),  # Rouge foncé
            self.couleur_texte,
            40
        )
        
        self.boutons = [self.bouton_jouer, self.bouton_regles, self.bouton_quitter]
        self.affichage_regles = False
        
    def initialiser_musique(self):
        """Initialise et joue la musique d'accueil en boucle"""
        try:
            if not pygame.mixer.get_init():
                print("ERREUR: Le module de mixage audio n'est pas initialisé")
                return
                
            # Chemin vers le fichier audio de l'écran d'accueil
            musique_path = Path(__file__).parent.parent / 'Sounds' / 'MO.ogg'
            print(f"Tentative de chargement de la musique depuis: {musique_path}")
            
            if not musique_path.exists():
                print(f"ERREUR: Le fichier audio n'existe pas: {musique_path}")
                # Afficher le contenu du dossier Sounds
                sounds_dir = musique_path.parent
                print(f"Contenu du dossier {sounds_dir}:")
                for f in sounds_dir.glob('*'):
                    print(f"  - {f.name}")
                return
                
            try:
                pygame.mixer.music.load(str(musique_path))
                print("Musique chargée avec succès")
                
                pygame.mixer.music.set_volume(0.5)  # Volume à 50%
                pygame.mixer.music.play(-1)  # -1 pour boucler la musique
                print("Musique démarrée en boucle")
                
                # Vérifier si la musique est en cours de lecture
                if pygame.mixer.music.get_busy():
                    print("La musique est en cours de lecture")
                else:
                    print("ATTENTION: La musique ne semble pas être en cours de lecture")
                    
            except pygame.error as e:
                print(f"ERREUR Pygame lors du chargement/lecture: {e}")
                print(f"Détails: {pygame.get_error()}")
                
        except Exception as e:
            print(f"ERREUR inattendue dans initialiser_musique: {e}")
            import traceback
            traceback.print_exc()
    
        # Charger le logo
        try:
            logo_path = Path(__file__).parent.parent / 'assets' / 'logo.png'
            if logo_path.exists():
                self.logo = pygame.image.load(str(logo_path)).convert_alpha()
                # Redimensionner le logo si nécessaire
                max_width = 400
                ratio = max_width / self.logo.get_width()
                new_height = int(self.logo.get_height() * ratio)
                self.logo = pygame.transform.scale(self.logo, (max_width, new_height))
            else:
                self.logo = None
        except Exception as e:
            print(f"Erreur lors du chargement du logo: {e}")
            self.logo = None
    
    def gerer_evenements(self, evenement):
        pos_souris = pygame.mouse.get_pos()
        
        # Vérifier si la souris survole un bouton
        for bouton in self.boutons:
            bouton.est_survole_par_souris(pos_souris)
        
        # Gérer les clics
        if evenement.type == pygame.MOUSEBUTTONDOWN:
            if self.bouton_jouer.est_clique(pos_souris, evenement):
                return "JOUER"
            elif self.bouton_regles.est_clique(pos_souris, evenement):
                self.affichage_regles = not self.affichage_regles
            elif self.bouton_quitter.est_clique(pos_souris, evenement):
                return "QUITTER"
        
        return None
    
    def afficher(self, ecran):
        """Affiche le menu sur l'écran fourni et gère la boucle d'événements"""
        clock = pygame.time.Clock()
        en_cours = True
        
        while en_cours:
            # Gestion des événements
            for evenement in pygame.event.get():
                if evenement.type == pygame.QUIT:
                    pygame.quit()
                    return False
                    
                # Gérer les événements de la souris
                if evenement.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                    # Vérifier les survols de souris
                    pos_souris = pygame.mouse.get_pos()
                    for bouton in self.boutons:
                        bouton.est_survole_par_souris(pos_souris)
                    
                    # Gérer les clics
                    if evenement.type == pygame.MOUSEBUTTONDOWN:
                        if self.bouton_jouer.est_clique(pos_souris, evenement):
                            return True
                        elif self.bouton_regles.est_clique(pos_souris, evenement):
                            self.affichage_regles = not self.affichage_regles
                        elif self.bouton_quitter.est_clique(pos_souris, evenement):
                            pygame.quit()
                            return False
            
            # Remplir l'arrière-plan avec la couleur de fond
            ecran.fill(MINI_BLACK)
            
            # Créer une nouvelle surface pour le menu
            self.surface = pygame.Surface((self.largeur, self.hauteur), pygame.SRCALPHA)
            
            # Créer un fond avec un léger flou
            fond = pygame.Surface((self.largeur, self.hauteur), pygame.SRCALPHA)
            pygame.draw.rect(fond, (*self.couleur_fond, 200), (0, 0, self.largeur, self.hauteur), border_radius=15)
            self.surface.blit(fond, (0, 0))
            
            # Afficher le logo ou le titre
            if hasattr(self, 'logo') and self.logo is not None:
                try:
                    logo_rect = self.logo.get_rect(centerx=self.largeur//2, top=self.hauteur//8)
                    self.surface.blit(self.logo, logo_rect)
                except (AttributeError, pygame.error) as e:
                    print(f"Erreur lors de l'affichage du logo: {e}")
                    self._afficher_titre()
            else:
                # Afficher le titre si le logo n'est pas chargé
                self._afficher_titre()
            
            # Afficher les boutons
            for bouton in self.boutons:
                bouton.dessiner(self.surface)
            
            # Afficher les règles si demandé
            if self.affichage_regles:
                self._afficher_regles()
            
            # Afficher la surface du menu centrée sur l'écran
            pos_x = (ecran.get_width() - self.largeur) // 2
            pos_y = (ecran.get_height() - self.hauteur) // 2
            ecran.blit(self.surface, (pos_x, pos_y))
            
            # Mettre à jour l'affichage
            pygame.display.flip()
            
            # Limiter le taux de rafraîchissement
            clock.tick(60)
            
    def __del__(self):
        """Nettoie les ressources lors de la suppression du menu"""
        try:
            # Vérifier si le module audio est initialisé
            if pygame.mixer and pygame.mixer.get_init():
                # Arrêter la musique si elle est en cours de lecture
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
        except Exception as e:
            # Ignorer les erreurs lors de la suppression
            pass
            
        # Nettoyer les autres ressources
        if hasattr(self, 'logo'):
            del self.logo
            
    def _afficher_titre(self):
        """Affiche le titre du jeu"""
        if not hasattr(self, 'police_titre'):
            self.police_titre = pygame.font.Font(None, 80)
        titre = self.police_titre.render("CHEQUE GAMES", True, self.couleur_texte)
        titre_rect = titre.get_rect(centerx=self.largeur//2, y=self.hauteur//8)
        self.surface.blit(titre, titre_rect)
    
    def _afficher_regles(self):
        # Créer une surface semi-transparente pour l'arrière-plan
        overlay = pygame.Surface((self.largeur, self.hauteur), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Noir semi-transparent
        self.surface.blit(overlay, (0, 0))
        
        # Créer la surface des règles
        regles_largeur = min(800, self.largeur - 100)
        regles_hauteur = min(600, self.hauteur - 100)
        regles_surface = pygame.Surface((regles_largeur, regles_hauteur), pygame.SRCALPHA)
        
        # Dessiner le fond de la fenêtre des règles
        pygame.draw.rect(regles_surface, (50, 50, 50, 250), regles_surface.get_rect(), border_radius=15)
        pygame.draw.rect(regles_surface, (100, 100, 100), regles_surface.get_rect(), 2, border_radius=15)
        
        # Titre des règles
        font_titre = pygame.font.Font(None, 48)
        titre = font_titre.render("RÈGLES DU JEU", True, (255, 215, 0))  # Or
        titre_rect = titre.get_rect(center=(regles_largeur // 2, 40))
        regles_surface.blit(titre, titre_rect)
        
        # Bouton de fermeture (en haut à droite)
        bouton_fermer = Bouton(
            regles_largeur - 50, 
            10, 
            40, 40, 
            "X", 
            (200, 0, 0),  # Rouge foncé
            (255, 255, 255),  # Blanc
            32
        )
        bouton_fermer.rect.center = (regles_largeur - 30, 30)  # Position précise
        
        # Dessiner le bouton de fermeture
        pygame.draw.rect(regles_surface, bouton_fermer.couleur, bouton_fermer.rect, border_radius=20)
        pygame.draw.rect(regles_surface, (255, 255, 255), bouton_fermer.rect, 2, border_radius=20)
        texte_fermer = pygame.font.Font(None, 32).render(bouton_fermer.texte, True, bouton_fermer.couleur_texte)
        texte_fermer_rect = texte_fermer.get_rect(center=bouton_fermer.rect.center)
        regles_surface.blit(texte_fermer, texte_fermer_rect)
        
        # Conteneur défilable pour le contenu
        contenu_rect = pygame.Rect(30, 80, regles_largeur - 60, regles_hauteur - 120)
        
        # Texte des règles avec une meilleure mise en page
        font_texte = pygame.font.Font(None, 28)
        font_sous_titre = pygame.font.Font(None, 32)
        
        # Liste des règles avec des sections
        sections = [
            ("DÉROULEMENT DU JEU", [
                "• Chaque joueur commence avec 5 cartes",
                "• À votre tour, posez une carte de même valeur ou de même symbole que celle du dessus de la pile",
                "• Si vous ne pouvez pas jouer, piochez une carte"
            ]),
            ("CARTES SPÉCIALES", [
                "• As (A) : Fait passer le tour de l'adversaire",
                "• 2 : Peut être placé sur n'importe quelle carte",
                "• 7 : Fait piocher 2 cartes (effet cumulable)",
                "• Valet (J) : Permet de changer de symbole",
                "• Joker : Fait piocher 4 cartes et change de symbole"
            ]),
            ("FIN DE PARTIE", [
                "• Le premier joueur à ne plus avoir de cartes en main remporte la manche",
                "• Le premier à gagner 3 manches gagne la partie"
            ])
        ]
        
        y_offset = 20
        for titre_section, regles_section in sections:
            # Titre de section
            titre = font_sous_titre.render(titre_section, True, (255, 215, 0))  # Or
            regles_surface.blit(titre, (40, y_offset + 80))
            y_offset += 40
            
            # Règles de la section
            for ligne in regles_section:
                if ligne.startswith("•"):
                    texte = font_texte.render(ligne, True, (255, 255, 255))  # Blanc
                    regles_surface.blit(texte, (60, y_offset + 80))
                    y_offset += 30
                else:
                    y_offset += 10  # Espacement supplémentaire entre les sections
        
        # Positionner la surface des règles au centre
        rect_regles = regles_surface.get_rect(center=(self.largeur // 2, self.hauteur // 2))
        self.surface.blit(regles_surface, rect_regles)
        
        # Vérifier si l'utilisateur clique sur le bouton de fermeture
        pos_souris = pygame.mouse.get_pos()
        bouton_fermer_abs_rect = pygame.Rect(
            rect_regles.left + bouton_fermer.rect.left,
            rect_regles.top + bouton_fermer.rect.top,
            bouton_fermer.rect.width,
            bouton_fermer.rect.height
        )
        
        # Mettre à jour l'état de survol du bouton
        bouton_fermer.est_survole = bouton_fermer_abs_rect.collidepoint(pos_souris)
        
        # Gérer le clic sur le bouton de fermeture
        if pygame.mouse.get_pressed()[0]:  # Si clic gauche
            if bouton_fermer_abs_rect.collidepoint(pos_souris):
                self.affichage_regles = False
                # Éviter les clics multiples
                pygame.time.delay(200)
