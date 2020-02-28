import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

import sys
sys.path.append('../')
import league


class CameraUpdates(pygame.sprite.LayeredUpdates):
    """
    Modified from
    https://stackoverflow.com/questions/14354171/add-scrolling-to-a-platformer-in-pygame/14357169#14357169
    Creates a camera object to follow the player around the map
    """
    def __init__(self, target, world_size):
        """
        Initalizes a camera object to follow a specific target.

        param - target: the target game object being followed
        param - world_size: The size of the world the camera will exist in.
        """
        super().__init__()
        self.target = target
        self.cam = pygame.Vector2(0, 0)
        self.world_size = world_size
        if self.target:
            self.add(target)

    def update(self, *args):
        """
        The update function for the camera. It updates the camera's position to 
        follow the player around the map. 

        param - *args: the arguemtns for this update function. In this case layers and the delta time
        """
        super().update(*args)
        if self.target:
            x = -self.target.rect.center[0] + league.Settings.width/2
            y = -self.target.rect.center[1] + league.Settings.height/4 # less upward movement on the camera
            if y < 0: # don't go under the floor
                y = 0
            self.cam += (pygame.Vector2((x, y)) - self.cam) * 0.05
            self.cam.x = max(-(self.world_size[0]-(league.Settings.width + (league.Settings.tile_size * 3))), min(-2 * league.Settings.tile_size, self.cam.x))

    def draw(self, surface):
        """
        Overrides the default draw function for LayeredUpdates. 
        """
        spritedict = self.spritedict
        surface_blit = surface.blit
        dirty = self.lostsprites
        self.lostsprites = []
        dirty_append = dirty.append
        init_rect = self._init_rect
        for spr in self.sprites():
            rec = spritedict[spr]
            newrect = surface_blit(spr.image, spr.rect.move(self.cam))
            if rec is init_rect:
                dirty_append(newrect)
            else:
                if newrect.colliderect(rec):
                    dirty_append(newrect.union(rec))
                else:
                    dirty_append(newrect)
                    dirty_append(rec)
            spritedict[spr] = newrect
        return dirty       
        