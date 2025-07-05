def fix_file(input_file, output_file):
    with open(input_file, 'r', encoding='latin-1') as f:
        lines = f.readlines()
    
    # Trouver le début de la section des cartes de l'IA
    start_line = -1
    for i, line in enumerate(lines):
        if 'Afficher les cartes de l\'IA' in line:
            start_line = i
            break
    
    if start_line == -1:
        print("Section des cartes de l'IA non trouvée")
        return
    
    # Supprimer la ligne en double de card_width
    for i in range(start_line, min(start_line + 50, len(lines))):
        if 'card_width = Carte._dos_carte.get_width()' in lines[i] and \
           i + 1 < len(lines) and 'card_width = Carte._dos_carte.get_width()' in lines[i+1]:
            lines.pop(i+1)
            break
    
    # Corriger l'indentation des appels pygame.draw.rect
    for i in range(start_line, min(start_line + 100, len(lines))):
        if 'pygame.draw.rect' in lines[i]:
            lines[i] = '                ' + lines[i].lstrip()
    
    # Écrire les modifications dans un nouveau fichier
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"Fichier corrigé enregistré sous : {output_file}")

if __name__ == "__main__":
    input_file = r"c:\Users\DELL\Desktop\projet-jeu2d\check_games_by_pygame\game\game.py"
    output_file = r"c:\Users\DELL\Desktop\projet-jeu2d\check_games_by_pygame\game\game_fixed_manual.py"
    fix_file(input_file, output_file)
