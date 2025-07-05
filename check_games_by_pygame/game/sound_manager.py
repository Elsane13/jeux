import os
import pygame
from pathlib import Path

class SoundManager:
    def __init__(self):
        """Initialise le gestionnaire de sons"""
        self.sounds = {}
        self.volume = 0.5  # Volume par défaut à 50%
        self.muted = False
        self._init_sounds()
    
    def _init_sounds(self):
        """Charge tous les sons du dossier Sounds"""
        base_dir = Path(__file__).parent.parent
        sounds_dir = base_dir / 'Sounds'
        
        # Dictionnaire de correspondance entre les noms de fichiers et leurs utilisations
        sound_mapping = {
            '108396__filmfan87__hand-hitting-table.wav': 'card_play',
            '793598__ajaysingh318__card-flipping-75622-1-audiotrimmer.mp3': 'card_flip',
            'click-a.ogg': 'click',
            'switch-a.ogg': 'switch',
            'tap-a.ogg': 'tap'
        }
        
        for filename, sound_name in sound_mapping.items():
            sound_path = sounds_dir / filename
            try:
                if sound_path.exists():
                    sound = pygame.mixer.Sound(str(sound_path))
                    sound.set_volume(self.volume)
                    self.sounds[sound_name] = sound
                    print(f"Son chargé: {sound_name} ({filename})")
                else:
                    print(f"Avertissement: Fichier son non trouvé: {sound_path}")
            except Exception as e:
                print(f"Erreur lors du chargement du son {filename}: {e}")
    
    def play(self, sound_name, loops=0):
        """Joue un son
        
        Args:
            sound_name (str): Nom du son à jouer
            loops (int): Nombre de boucles (-1 pour une boucle infinie)
        """
        if self.muted or sound_name not in self.sounds:
            return
            
        try:
            self.sounds[sound_name].play(loops=loops)
        except Exception as e:
            print(f"Erreur lors de la lecture du son {sound_name}: {e}")
    
    def set_volume(self, volume):
        """Définit le volume de tous les sons
        
        Args:
            volume (float): Niveau de volume entre 0.0 et 1.0
        """
        self.volume = max(0.0, min(1.0, volume))  # S'assure que le volume est entre 0 et 1
        for sound in self.sounds.values():
            sound.set_volume(self.volume)
    
    def toggle_mute(self):
        """Active/désactive le son"""
        self.muted = not self.muted
        if self.muted:
            pygame.mixer.pause()
        else:
            pygame.mixer.unpause()
        return self.muted
