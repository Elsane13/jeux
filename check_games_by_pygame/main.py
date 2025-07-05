import pygame
import sys
import os
import traceback
from pathlib import Path
from game.game import ChequeGames
from game.menu import MenuPrincipal
from game.constants import SCREEN_WIDTH, SCREEN_HEIGHT, GREEN, BLACK, MINI_BLACK

def init_pygame():
    """Initialise Pygame et retourne True si tout s'est bien passé"""
    try:
        # Initialiser pygame avec tous les modules nécessaires
        print("Initialisation de Pygame...")
        pygame.init()
        
        print("Initialisation du module de mixage audio...")
        # Essayer différentes configurations audio
        try:
            pygame.mixer.quit()  # S'assurer qu'aucun mixeur n'est déjà initialisé
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            print(f"Mixeur initialisé: {pygame.mixer.get_init()}")
            print(f"Pygame version: {pygame.version.ver}")
            print(f"SDL version: {'.'.join(str(x) for x in pygame.get_sdl_version())}")
        except Exception as e:
            print(f"Erreur lors de l'initialisation du mixeur: {e}")
            # Essayer une configuration plus simple
            try:
                pygame.mixer.quit()
                pygame.mixer.init()
                print(f"Mixeur réinitialisé avec les paramètres par défaut: {pygame.mixer.get_init()}")
            except Exception as e2:
                print(f"Échec de l'initialisation du mixeur: {e2}")
                return False
        
        # Vérifier que les modules nécessaires sont chargés
        if not pygame.get_init():
            print("ERREUR: Pygame n'est pas initialisé")
            return False
            
        if not pygame.mixer.get_init():
            print("ERREUR: Le module de mixage audio n'est pas initialisé")
            return False
        
        # Vérifier la disponibilité des polices
        if not pygame.font.get_init():
            print("Avertissement: Le module de police n'est pas initialisé correctement")
            
        return True
    except Exception as e:
        print(f"Erreur critique lors de l'initialisation de Pygame: {e}")
        return False

def main():
    """Fonction principale du jeu"""
    # Initialisation de Pygame
    if not init_pygame():
        print("Échec de l'initialisation de Pygame")
        return
    
    # Création de la fenêtre
    ecran = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Jeu de Cartes")
    
    # Création du menu principal avec la largeur et la hauteur de l'écran
    menu = MenuPrincipal(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    # Boucle principale du menu
    en_jeu = menu.afficher(ecran)
    
    # Si l'utilisateur a choisi de quitter depuis le menu
    if not en_jeu:
        pygame.quit()
        return
    
    # Création du jeu
    try:
        jeu = ChequeGames(ecran)
    except Exception as e:
        print(f"Erreur lors de l'initialisation du jeu: {e}")
        traceback.print_exc()
        pygame.quit()
        return
    
    # Horloge pour contrôler le taux de rafraîchissement
    horloge = pygame.time.Clock()
    
    # Boucle principale du jeu
    en_cours = True
    while en_cours:
        # Gestion des événements
        for evenement in pygame.event.get():
            if evenement.type == pygame.QUIT:
                en_cours = False
            elif evenement.type == pygame.MOUSEBUTTONDOWN:
                if evenement.button == 1:  # Clic gauche
                    jeu.gerer_clic_souris(evenement.pos, 'down')
            elif evenement.type == pygame.MOUSEBUTTONUP:
                if evenement.button == 1:  # Relâchement du clic gauche
                    jeu.gerer_clic_souris(evenement.pos, 'up')
            elif evenement.type == pygame.MOUSEMOTION:
                # Pour le suivi du mouvement de la souris (glisser-déposer)
                if evenement.buttons[0]:  # Si le bouton gauche est maintenu enfoncé
                    jeu.gerer_clic_souris(evenement.pos, 'motion')
            elif evenement.type == pygame.KEYDOWN:
                if evenement.key == pygame.K_ESCAPE:
                    en_cours = False
        
        # Mise à jour du jeu
        jeu.mettre_a_jour()
        
        # Affichage
        ecran.fill(GREEN)  # Fond vert pour la table de jeu
        jeu.afficher()
        
        # Rafraîchissement de l'écran
        pygame.display.flip()
        
        # Limiter le taux de rafraîchissement
        horloge.tick(60)
    
    # Fermeture de Pygame
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()