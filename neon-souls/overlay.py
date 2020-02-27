import league
import pygame

class Overlay(league.DUGameObject):
    """
    The overlay class handles the initialization and updating of the HP information overlay. 
    HP information is taken from the current_health member of the player's health object. 
    """
    def __init__(self, player):
        """
        Inits the overlay.

        param - player: The player object whose HP will
        be displayed in the overlay.
        """
        super().__init__(self)
        self._layer = 1000
        self.player = player
        self.font = pygame.font.Font('freesansbold.ttf',32)
        self.image = pygame.Surface([6000, 40])
        self.image.fill((127, 127, 127))
        self.text = self.font.render(str(self.player.health.current_health) + " HP", True, (0,0,0))
        self.image.blit(self.text, (self.player.rect.centerx, 0))
        self.rect = self.image.get_rect()
        self.x = 0
        self.y = 0
        self.rect.x = 30
        self.rect.y = 0
        self.static = True

    def update(self, deltaTime):
        """
        Updates the overlay with the current health.
        Updates the x coordinate of the overlay text to follow the player
        across the map.
        """
        self.image.fill((127, 127, 127))
        self.text = self.font.render(str(self.player.health.current_health) + " HP", True, (0,0,0))
        self.image.blit(self.text, (self.player.rect.centerx, 0))
