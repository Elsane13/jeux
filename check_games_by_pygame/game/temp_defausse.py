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
