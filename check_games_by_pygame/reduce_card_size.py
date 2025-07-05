"""
Script pour réduire la taille des cartes de moitié en modifiant le facteur d'échelle.
"""

def reduce_card_size():
    # Chemin vers le fichier constants.py
    constants_path = r'c:\Users\DELL\Desktop\projet-jeu2d\check_games_by_pygame\game\constants.py'
    
    try:
        # Lire le contenu du fichier
        with open(constants_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Vérifier si la réduction a déjà été appliquée
        for i, line in enumerate(lines):
            if 'SCALE_FACTOR = ' in line:
                # Extraire la valeur numérique avant le commentaire
                value_part = line.split('=')[1].split('#')[0].strip()
                current_scale = float(value_part)
                if current_scale == 0.5:
                    print("Les cartes sont déjà réduites de moitié.")
                    return
                
                # Mettre à jour le facteur d'échelle à 0.5 (moitié de la taille)
                lines[i] = 'SCALE_FACTOR = 0.5  # Facteur d\'échelle réduit de moitié\n'
                break
        
        # Écrire les modifications dans le fichier
        with open(constants_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print("La taille des cartes a été réduite de moitié avec succès.")
        print("Redémarrez le jeu pour voir les changements.")
        
    except Exception as e:
        print(f"Une erreur s'est produite lors de la modification du fichier : {e}")

if __name__ == "__main__":
    reduce_card_size()
