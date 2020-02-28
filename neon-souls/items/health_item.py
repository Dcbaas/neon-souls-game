"""A Generic Item to add to player health"""
import pygame
from . import Item

class HealthItem(Item):
    """Regain player health using this cool item!"""
    def __init__(self, x, y, layer=3):
        super(HealthItem, self).__init__('./assets/health-item.png', x, y)
        self.heal_amount = 10

    def grab(self, player):
        """
        Add health to player on collision and play a cool sound!

        Args:
        player (actors.Player): instance of player to manipulate upon grabbing item
        """
        player.health.gain_health(self.heal_amount)
        effect = pygame.mixer.Sound('./assets/health-sound.wav')
        effect.play()
        self.kill()
