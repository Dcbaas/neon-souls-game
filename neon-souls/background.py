import league
import pygame

class Background(league.DGameObject):
    def __init__(self, image_path, layer=0):
        super().__init__(self)
        self._layer = layer
        self.image = pygame.image.load(image_path).convert()
        self.image = pygame.transform.scale(self.image, (league.Settings.width, league.Settings.height))
        self.image.set_alpha(255)
        self.rect = self.image.get_rect()
        self.x = 0
        self.y = 0
        self.rect.x = 000
        self.rect.y = 0
        self.static = True

    # def to_string(self):
    #     return 'layer: {} image: {}, rect: {} x: {} y: {} rect.x: {} rect.y: {}'.format(self._layer, self.image, self.rect, self.x, self.y, self.rect.x, self)
