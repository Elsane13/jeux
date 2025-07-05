from enum import Enum, auto

# Paramètres de l'écran
SCREEN_WIDTH = 800  # Largeur réduite
SCREEN_HEIGHT = 600  # Hauteur réduite
FPS = 60
SCALE_FACTOR = 0.5  # Facteur d'échelle réduit de moitié

# Dimensions des cartes
CARD_WIDTH = 80  # Largeur réduite de moitié (160/2)
CARD_HEIGHT = 120  # Hauteur réduite de moitié (240/2)

# Dossiers
ASSETS_DIR = 'assets'
IMAGE_DIR = 'image'

# Chemins complets
def get_asset_path(*paths):
    """Retourne le chemin complet vers un fichier dans le dossier assets"""
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, ASSETS_DIR, *paths)

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 128, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
GOLD = (255, 215, 0)
PURPLE = (128, 0, 128)
DARK_GREEN = (0, 100, 0)
YELLOW = (255, 255, 0)
LIGHT_BLUE = (100, 149, 237)  # Bleu ciel pour le dos des cartes
MINI_BLACK = (13, 13, 26)

# Paramètres du jeu
INITIAL_HEARTS = 3
INITIAL_CARDS = 5

# Dimensions de base (pour le redimensionnement)
BASE_WIDTH = 1280
BASE_HEIGHT = 720

# Chemins des images
LOGO_PATH = get_asset_path('logo.png')

# Symboles des cartes (noms des dossiers d'images)
class Symbole(Enum):
    COEUR = "coeur"
    CARREAU = "carreau"
    TREFLE = "trefle"
    PIQUE = "pique"
    JOKER = "joker"

    # Méthode pour obtenir le nom du dossier correspondant
    def get_dossier(self):
        return {
            Symbole.COEUR: 'hearts',
            Symbole.CARREAU: 'diamonds',
            Symbole.TREFLE: 'clubs',
            Symbole.PIQUE: 'spades',
        }.get(self, '')

# Valeurs spéciales des cartes
class Valeur(Enum):
    AS = 1
    DEUX = 2
    TROIS = 3
    QUATRE = 4
    CINQ = 5
    SIX = 6
    SEPT = 7
    HUIT = 8
    NEUF = 9
    DIX = 10
    VALET = 11
    DAME = 12
    ROI = 13

# Mappage des symboles vers les caractères d'affichage
SYMBOLES = {
    Symbole.COEUR: '♥',
    Symbole.CARREAU: '♦',
    Symbole.TREFLE: '♣',
    Symbole.PIQUE: '♠',
}

def get_couleur_symbole(symbole, valeur=None):
    """Retourne la couleur appropriée pour un symbole donné.
    Pour les jokers, la couleur dépend de la valeur (0=noir, 1=rouge)."""
    if symbole == Symbole.COEUR or symbole == Symbole.CARREAU:
        return RED
    elif symbole == Symbole.TREFLE or symbole == Symbole.PIQUE:
        return BLACK
    elif symbole == Symbole.JOKER:
        return RED if valeur == 1 else BLACK  # Joker rouge si valeur=1, noir sinon
    return BLACK

# Couleurs des symboles (version simplifiée, utilisez get_couleur_symbole pour la couleur réelle)
COULEUR_SYMBOLES = {
    Symbole.COEUR: RED,
    Symbole.CARREAU: RED,
    Symbole.TREFLE: BLACK,
    Symbole.PIQUE: BLACK,
    Symbole.JOKER: RED  # Valeur par défaut, utilisez get_couleur_symbole pour la couleur précise
}

# Dimensions des cartes (doivent correspondre à la taille des images chargées)
# Utilisation des dimensions réduites de moitié (80x120 pixels)
CARD_WIDTH = 80  # Largeur des cartes réduite
CARD_HEIGHT = 120  # Hauteur des cartes réduite
SCALE_FACTOR = 0.5  # Facteur de redimensionnement à 50%

# Positions
# Position de la pile de défausse (centrée)
PILE_POS = (SCREEN_WIDTH // 2 - CARD_WIDTH // 2, SCREEN_HEIGHT // 2 - CARD_HEIGHT // 2)
# Position de la main du joueur (en bas de l'écran)
PLAYER_HAND_Y = SCREEN_HEIGHT - CARD_HEIGHT - 20
# Position de la main de l'IA (en haut de l'écran)
AI_HAND_Y = 20

# Valeurs spéciales pour l'affichage
VALEURS_SPECIALES = {
    1: "A",   # As
    11: "J",  # Valet
    12: "Q",  # Dame
    13: "K"   # Roi
}

# Chemins des dossiers
IMAGE_DIR = "asset"
