"""
Script pour corriger les dimensions des cartes dans le jeu.
"""
import re

def fix_card_sizes():
    # Chemin vers le fichier game.py
    game_path = r'c:\Users\DELL\Desktop\projet-jeu2d\check_games_by_pygame\game\game.py'
    
    try:
        # Lire le contenu du fichier
        with open(game_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier si la correction a déjà été appliquée
        if 'Obtenir la surface de la carte pour avoir ses dimensions réelles' in content:
            print("La correction des dimensions des cartes a déjà été appliquée.")
            return
        
        # Trouver la section à modifier
        pattern = r'(# Afficher les cartes du joueur \(sauf celle en cours de déplacement\).*?)(?=# Afficher la carte sélectionnée)'
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            print("Impossible de trouver la section à modifier dans le fichier game.py")
            return
        
        # Remplacer par la version corrigée
        old_section = match.group(1)
        new_section = """        # Afficher les cartes du joueur (sauf celle en cours de déplacement)
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
        """
        
        # Remplacer l'ancienne section par la nouvelle
        new_content = content.replace(old_section, new_section)
        
        # Écrire les modifications dans le fichier
        with open(game_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("Les dimensions des cartes ont été corrigées avec succès.")
        
    except Exception as e:
        print(f"Une erreur s'est produite lors de la modification du fichier : {e}")

if __name__ == "__main__":
    fix_card_sizes()
