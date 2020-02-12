import sys
sys.path.append('../../')

from abc import ABC
import pygame

from league import Character
from league import OffScreenException
from league import Drawable
from league import Settings
from physics import GravityBound, GravityManager
from .animation import WalkingAnimatedSprite 

import logging

logger = logging.getLogger('Player')

class ActorBase(Character, GravityBound):
    def __init__(self, image_path, image_size, z=0, x=0, y=0):
        super().__init__(z=z, x=x, y=y)

        self.x = x
        self.y = y
        self.image_size = image_size

        print(image_path)
        if image_path is None:
            self.image = None
        else:
            try:
                self.image = pygame.image.load(image_path).convert_alpha()
                self.image = pygame.transform.scale(self.image, image_size)
            except FileNotFoundError as file_error:
                raise FileNotFoundError('{} was not found'.format(image_path))

            self.rect = self.image.get_rect()
            
            self.blocks = pygame.sprite.Group()

        self.collide_function = pygame.sprite.collide_circle
        self.collisions = []

        self.collider = Drawable()
        self.collider.image = pygame.Surface([Settings.tile_size, Settings.tile_size])
        self.collider.rect = self.collider.image.get_rect()


class Player(ActorBase, GravityBound):
    MAX_JUMP_VELOCITY = -10
    def __init__(self, static_image_path, walking_sprite_path, image_size, gravity_region, z=0, x=0, y=0):
        super().__init__(None, image_size, z=z, x=x, y=y)
        self.velocity = [0,0]
        self.gravity_vector = [0,0]
        self.speed = 100
        self.gravity_region = gravity_region
        self.facing_left = False

        self.sprite_manager = WalkingAnimatedSprite(static_image_path, walking_sprite_path)
        self.get_image([0,0])
        self.blocks = pygame.sprite.Group()

    def move_player(self, time, inputs):
        amount = self.speed * time
        if inputs['W'] is True:
            jump_velocity = self.velocity[1] - amount
            self.velocity[1] = jump_velocity \
                if jump_velocity >= self.MAX_JUMP_VELOCITY else self.MAX_JUMP_VELOCITY
            

        # XOR Statement
        # https://python-reference.readthedocs.io/en/latest/docs/operators/bitwise_XOR.html
        # If either key is pressed BUT not both @ the same time.
        if inputs['D'] ^ inputs['A']:
            if inputs['D'] is True:
                self.velocity[0] = amount
            elif inputs['A'] is True:
                self.velocity[0] = -amount
        else:
            self.velocity[0] = 0

        ## PUT THIS AFTER ALL the calculations
        if True in inputs.values():
            self.facing_left = self.velocity[0] < 0

        self.get_image(self.velocity)

        # try:
        #     if not self.in_world():
        #         raise OffScreenException
        #     else:
        #         self.x = self.x + self.velocity[0]
        #         self.y = self.y + self.velocity[1]
        #         self.update(0)
        #         if len(self.collisions) > 0:
        #             logger.info(self.collisions[0].group()) # Statement is breaking collisions for some reason. How do i find out group? 
        #             self.x = self.x - self.velocity[0]
        #             self.y = self.y - self.velocity[1]
        #             self.update(0)
        #             self.collisions = []
        # except:
        #     pass

    def in_world(self):
        """
        Todo Check that we are still in the world
        """
        return True

   # Checks for collisions by comparing coordinates of self and iterative sprite in a certain group.
    #TODO Explore the possibility that we may have more than one sprite group.
    def update(self, time):
        self.x = self.x + self.velocity[0]
        self.y = self.y + self.velocity[1]

        self.rect.x = self.x
        self.rect.y = self.y
        self.collisions = []
        for sprite in self.blocks:
            self.collider.rect.x = sprite.x
            self.collider.rect.y = sprite.y
            if pygame.sprite.collide_rect(self, self.collider):
                self.collisions.append(sprite)
    
    # def process_gravity(self, time):
    #     gravity_manager = GravityManager.get_instance()
    #     gravity = gravity_manager.get_gravity(self.gravity_region)
    #     grav_amount = (gravity[0] * time, gravity[1] * time)
    #     self.velocity[0] = self.velocity[0] + grav_amount[0]
    #     self.velocity[1] = self.velocity[1] + grav_amount[1]
        
    #     # logger.debug('velocity: {}'.format(self.velocity))
    #     try:
    #         if not self.in_world():
    #             raise OffScreenException
    #         else:
    #             self.x = self.x + self.velocity[0]
    #             self.y = self.y + self.velocity[1]
    #             self.update(0)
    #             # TODO: manage collisions
    #     except:
    #         pass

    #     self.velocity = [0,0]

    def process_gravity(self, time, gravity_vector):
        # gravity_vector[0] = gravity_vector[0] * time
        # gravity_vector[1] = gravity_vector[1] * time
        gravity_vector = (gravity_vector[0] * time, gravity_vector[1] * time)

        # Right now we ignore a horizontal gravity cause we can't handle
        # it right now
        # self.velocity[0] = self.velocity[0] + gravity_vector[0]
        self.velocity[1] = self.velocity[1] + gravity_vector[1]

    def get_gravity_name(self):
        return self.gravity_region

    def get_image(self, vector):
        if vector[0] == 0:
            self.image = self.sprite_manager.get_static_image(self.facing_left).convert_alpha()
        else:
            self.image = self.sprite_manager.get_walking_image(self.facing_left)

        logger.debug(self.image)
        self.image = pygame.transform.scale(self.image, self.image_size)
        self.rect = self.image.get_rect()
    




    


    


