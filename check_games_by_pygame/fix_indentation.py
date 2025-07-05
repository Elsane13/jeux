import re

def fix_indentation(input_file, output_file):
    with open(input_file, 'r', encoding='latin-1') as f:
        lines = f.readlines()
    
    # Corriger la section des cartes de l'IA (lignes ~590-620)
    in_ia_section = False
    for i, line in enumerate(lines):
        if 'Afficher les cartes de l\'IA' in line:
            in_ia_section = True
            continue
            
        if in_ia_section and 'Afficher les cartes du joueur' in line:
            in_ia_section = False
            
        if in_ia_section and 'card_width = Carte._dos_carte.get_width()' in line:
            # Supprimer les doublons et corriger l'indentation
            if lines[i+1].strip().startswith('card_width = Carte._dos_carte.get_width()'):
                lines.pop(i+1)
            # Corriger l'indentation des lignes de dessin
            if 'pygame.draw.rect' in line and line.strip().startswith('pygame'):
                lines[i] = '                ' + line.lstrip()
    
    # Écrire les modifications dans un nouveau fichier
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)

if __name__ == "__main__":
    input_file = r"c:\Users\DELL\Desktop\projet-jeu2d\check_games_by_pygame\game\game.py"
    output_file = r"c:\Users\DELL\Desktop\projet-jeu2d\check_games_by_pygame\game\game_fixed.py"
    fix_indentation(input_file, output_file)
    print(f"Fichier corrigé enregistré sous : {output_file}")
