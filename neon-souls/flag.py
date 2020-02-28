import pygame

import sys
sys.path.append('../')
import league


class Flag(league.DUGameObject):
    """
    Creates a final victory game object for the player to run over. The game is 
    over if the player runs over 
    """
    def __init__(self, x, y):
        """
        Inits the victory item. sets its location and sets won to false.

        param - x,y: the coordinates for the victory item
        """
        super().__init__(self)
        self._layer = 10
        self.x = x
        self.y = y
        self.won = False
        self.spritesheet = league.Spritesheet('./assets/18_midnight_spritesheet.png', 100, 8)
        self.image = pygame.Surface((100, 100))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.image_index_x = 0
        self.image_index_y = 0

    def win(self, player):
        """
        Called when the player collides with the victory item. Creates a winning
        icon at the end of the map. 

        param - player: The player colliding with the victory object
        """
        if not self.won:
            player.health.loss_rate = 0
            self.x -= (league.Settings.width // 3)
            self.y = (league.Settings.height // 2)
            self.image = pygame.image.load('./assets/win1.png').convert_alpha()
            self.won = True

    def update(self, delta_time):
        """
        Update function for the victory item

        param - delta_time: The game time that has passed since this function was 
        last called.
        """
        if self.won:
            self.rect = self.image.get_rect()
            self.rect.x = self.x
            self.rect.y = self.y
        else:
            self.get_image()

    def get_image(self):
        """
        TODO: Write comments
        """
        x = self.image_index_x * self.spritesheet.tile_size
        y = self.image_index_y * self.spritesheet.tile_size
        index = (8 * self.image_index_x - 1) + self.image_index_y
        base_sprite = self.spritesheet.sprites[(8 * self.image_index_x - 1) + self.image_index_y]
        sprite = league.game_objects.Drawable(self._layer)
        sprite.image = base_sprite.image
        # Set rectangle coords (using top-left coords here)
        self.image = sprite.image
        self.rect = sprite.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        if self.image_index_x == 7:
            self.image_index_x = 0
            self.image_index_y += 1
        elif self.image_index_x == 6 and self.image_index_y == 7:
            self.image_index_x = 0
            self.image_index_y = 0
        else:
            self.image_index_x += 1