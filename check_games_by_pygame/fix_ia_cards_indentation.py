def fix_ia_cards_indentation(input_file, output_file):
    with open(input_file, 'r', encoding='latin-1') as f:
        lines = f.readlines()
    
    ia_section_start = None
    ia_section_end = None
    
    # Trouver la section des cartes de l'IA
    for i, line in enumerate(lines):
        if 'Afficher les cartes de l\'IA' in line:
            ia_section_start = i
        elif 'Afficher les cartes du joueur' in line and ia_section_start is not None:
            ia_section_end = i
            break
    
    if ia_section_start is not None and ia_section_end is not None:
        # Supprimer la ligne en double de card_width
        for i in range(ia_section_start, ia_section_end):
            if 'card_width = Carte._dos_carte.get_width()' in lines[i] and \
               'card_width = Carte._dos_carte.get_width()' in lines[i+1]:
                lines.pop(i+1)
                break
        
        # Corriger l'indentation des appels pygame.draw.rect
        for i in range(ia_section_start, ia_section_end):
            if 'pygame.draw.rect' in lines[i]:
                lines[i] = '                ' + lines[i].lstrip()
    
    # Écrire les modifications dans un nouveau fichier
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"Fichier corrigé enregistré sous : {output_file}")

if __name__ == "__main__":
    input_file = r"c:\Users\DELL\Desktop\projet-jeu2d\check_games_by_pygame\game\game.py"
    output_file = r"c:\Users\DELL\Desktop\projet-jeu2d\check_games_by_pygame\game\game_fixed_indent.py"
    fix_ia_cards_indentation(input_file, output_file)
