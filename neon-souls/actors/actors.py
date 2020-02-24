import sys
sys.path.append('../../')

from abc import ABC
import pygame
import math

from league import Character
from league import OffScreenException
from league import Drawable
from league import Settings
from physics import GravityBound, GravityManager
from .animation import WalkingAnimatedSprite, ConstantAnimatedSprite
from mechanics import Health

import logging

logger = logging.getLogger('actor')


"""
Contains all the classes for actors that exist in the game

Date 2/22/2020
"""
class ActorBase(Character):
    """
    The base actor for all actors that exist in the game. contains shared 
    functions and has initialization that all actors use. 
    """

    def __init__(self, image_path, image_size, z=0, x=0, y=0):
        """
        Constructor for base actor. Initializes shared features for all actors.
        image_path assumes actor has a static image. Some actors send a None 
        because they never have a static image. If None the image is not set.

        param - image_path: The path this actors sprite
        param - image_size: The size of this actors sprite
        param - x, y, z: The starting coordinates of this actor
        """
        super().__init__(z=z, x=x, y=y)

        self.x = x
        self.y = y
        self.image_size = image_size

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

        self.collide_function = pygame.sprite.collide_rect
        self.collisions = []

        self.collider = Drawable()
        self.collider.image = pygame.Surface([Settings.tile_size, Settings.tile_size])
        self.collider.rect = self.collider.image.get_rect()
    
    def handle_map_collisions(self):
        """
        Shared function for most actors. Checks if the actor is colliding with the 
        impassible ground in the map. Kills velocity in horizontal or vertical 
        direction depending on what axis the actor hit from. Checks the top, 
        bottom, left, and right sides of the actor to see exactly where the hit
        occured. 

        THIS FUNCTION ISN'T PERFECT. SOMETIMES THE ACTOR CAN FALL IN SUCH A WAY 
        THAT THE EDGES OF THE ACTOR WON'T DETECT THE MAP. THE ACTOR WILL FALL
        THROUGH THE FLOOR IN THIS CASE.
        """
        for collision in self.collisions:
            bot = bool(collision.rect.collidepoint(self.rect.midbottom))
            top = bool(collision.rect.collidepoint(self.rect.midtop))
            right = bool(collision.rect.collidepoint(self.rect.midright))
            left = bool(collision.rect.collidepoint(self.rect.midleft))

            # # stop on bot or top
            self.velocity[1] = 0 if bot and self.velocity[1] > 0 else self.velocity[1]
            self.velocity[1] = 0 if top and self.velocity[1] < 0 else self.velocity[1]
            

            self.velocity[0] = 0 if right and self.velocity[0] > 0 else self.velocity[0]
            self.velocity[0] = 0 if left and self.velocity[0] < 0 else self.velocity[0]

class Player(ActorBase, GravityBound):
    """
    Player class. The player class repesents the player on the screen. It has 
    functions for handling user input and for handling collisions in game. 
    The player implements GravityBound interface meaning every update, the player
    is affected by gravity.
    """
    MAX_JUMP_VELOCITY = -10
    MAX_FALL_VELOCITY = 20
    def __init__(self, static_image_path, walking_sprite_path, running_sprite_path, image_size, gravity_region, z=0, x=0, y=0, layer=5):
        """
        Initalizes the player. The player has a custom sprite manager so it sets image_path to none. 
        
        param - static_image_path: The path to the standing stance of the player
        param - walking image_path: A list of paths for the walking sprites of the player.
        param - image_size: The size of the player
        param - gravity_region: The region of gravity affecting the player
        param - x, y, z: Starting location of the player.
        param - layer: the layer the player exists in.
        """
        super().__init__(None, image_size, z=z, x=x, y=y)
        self._layer = layer
        self.velocity = [0,0]
        self.speed = 200
        self.gravity_region = gravity_region
        self.facing_left = False
        self.last_hit = pygame.time.get_ticks()

        self.sprite_manager = WalkingAnimatedSprite(static_image_path, running_sprite_path)
        self.get_image([0,0])
        self.blocks = pygame.sprite.Group()

        self.health = Health(3, 1)

        self.last_tick = pygame.time.get_ticks()
        self.weapon_cooldown = 300


    def move_player(self, time, inputs):
        """
        Handles movement based input of the player. In the old version of player
        made in class, multiple inputs could not be handled. Now velocity is 
        calculated based on the inputs the player is passing in.

        param - time: the delta time that has passed since this function was called last
        param - inputs: A dict representing inputs on W, A, and D.
        """
        amount = self.speed * time
        if inputs['W'] is True:
            jump_velocity = self.velocity[1] - amount
            self.velocity[1] = jump_velocity \
                if jump_velocity >= self.MAX_JUMP_VELOCITY else self.MAX_JUMP_VELOCITY

        if self.velocity[1] > self.MAX_FALL_VELOCITY:
            self.velocity[1] = self.MAX_FALL_VELOCITY        

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

    def update(self, time):
        """
        Implements updatable from game object. Updates the players location based
        on the current frame's velocity. Also checks that the player is colliding
        with the game world. Will also check the players health and kill the player
        if the health reaches zero

        param - time: the delta time that has passed since this function was last called.
        """
        # For some reason the rect object is position at 0,0 at the start of every update function.
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        self.handle_map_collisions()
        
        self.x = self.x + self.velocity[0]
        self.y = self.y + self.velocity[1]
        self.rect.x = self.x
        self.rect.y = self.y

        # self.collisions = []
        for sprite in self.blocks:
            self.collider.rect.x = sprite.x
            self.collider.rect.y = sprite.y
            if pygame.sprite.collide_rect(self, self.collider):
                self.collisions.append(sprite)


        if self.health.at_zero():
            logger.fatal('OH NO YOU DIED')
            exit(0) 
    
    def process_gravity(self, time, gravity_vector):
        """
        Implements function from gravity bound. Updates the player's velocity to
        have the player affected by gravity. 

        param - time: the delta time that has passed since this function was called last
        param - gravity_vector: the vector of gravity that will affect the player.
        """
        gravity_vector = (gravity_vector[0] * time, gravity_vector[1] * time)

        # Right now we ignore a horizontal gravity cause we can't handle
        # it right now
        # self.velocity[0] = self.velocity[0] + gravity_vector[0]
        self.velocity[1] = self.velocity[1] + gravity_vector[1]

    def get_gravity_name(self):
        """
        Returns the gravity region this player is affected by.
        """
        return self.gravity_region

    def get_image(self, vector):
        """
        Gets the next image that will represent the player. If the player is 
        moving this will get the next image in the moving image list. 
        If the player isn't moving then it returns the player standing.

        param - vector: the vector of the player

        Previously, David wanted this function static but then made it an
        instance member. But the original function signature remained. 
        """
        if vector[0] == 0:
            self.image = self.sprite_manager.get_static_image(self.facing_left).convert_alpha()
        else:
            self.image = self.sprite_manager.get_walking_image(self.facing_left)

        self.image = pygame.transform.scale(self.image, self.image_size)

    def check_weapon_cooldown(self):
        current = pygame.time.get_ticks()
        if current - self.last_tick >= self.weapon_cooldown:
            self.last_tick = current
            return True

        else:
            return False

    def loadBullet(self):
        bullet = Projectile(self.x + 70, self.y + 47, self.facing_left)
        return bullet

    def take_dmg(self, object):
        now = pygame.time.get_ticks()
        if now - self.last_hit > 1000:
            self.health.lose_health()
            logger.info('{} HP'.format(self.health.current_health))
            self.last_hit = now


class Projectile(ActorBase):
    IMAGE_PATH = './assets/shot-2.png'
    def __init__(self, x, y, facing_left, image_path=IMAGE_PATH):
        
        super().__init__(image_path, (15,11), x, y)
        self._layer = 50
        self.rect.x = x
        self.rect.y = y
        self.facing_left = facing_left
        self.kill_function = None

        if(self.facing_left): 
            self.image = pygame.transform.flip(self.image, True, False)

    def update(self, time):
        if( self.facing_left ):
            self.rect.x = self.rect.x - 8
        else:
            self.rect.x = self.rect.x + 8

class SentinalEnemy(ActorBase):
    """
    Class for sentinal enemy. Named for the sprite name it belongs to in 
    assets/warped_enemies_pack_1_files/sentinal

    A hovering robot that does a static patrol. 
    
    Previously David wanted this 
    actor to pursue the player if they got in range. However there started being 
    performance issues that caused David to not implement this feature. Concersn
    that having multiples of this actor having that check would kill performance 
    hard.
    """

    def __init__(self, sprite_loader_path, image_size, patrol_list, kill_function, z=0, x=0, y=0, speed=100, layer=5):
        """
        Initializes the Sentinal. Unlike the player, the sentinal has only one continusous changing sprite.
        The sentinial has a patrol list which it follows a path to reach every point in the path.

        param - sprite_loader_path: The list of paths to the sentinal's sprite 
        rotation
        param - image_size: The size of this sentinal
        param - patrol_list: A list of coordinates the sentinal will go to in 
        rotation
        param - x, y, z: The starting location of this sentinal
        param - speed: the speed of this sentinal
        param - layer: the layer this sentinal exists in. 
        """
        super().__init__(None, image_size, z=z, x=x, y=y)
        self._layer = layer
        self.velocity = [0,0]
        self.speed = speed
        self.facing_left = False

        self.patrol_list = patrol_list
        self.current_patrol_point = patrol_list[0]
        self.patrol_index = 0

        self.rerender = True
        
        self.sprite_manager = ConstantAnimatedSprite(sprite_loader_path)
        self.image = self.sprite_manager.get_sprite(self.facing_left)
        self.blocks = pygame.sprite.Group()

        self.kill_function = kill_function

    def update(self, deta_game_time):
        """
        Implements update function for updatable. Determines the patrol path for the 
        for this actor and updates its position

        param - deta_game_time: the delta time since this function was last called.
        """
        # For some reason the rect object is position at 0,0 at the start of every update function.
        self.rect.x = self.x
        self.rect.y = self.y
        self.determine_move(deta_game_time)
        if self.rerender:
            self.get_image(self.velocity)

        self.rerender = not self.rerender

        self.x = self.x + self.velocity[0]
        self.y = self.y + self.velocity[1]
        self.rect.x = self.x
        self.rect.y = self.y

    def determine_move(self, delta_game_time):
        """
        Helper function. Determines how this sentinal will move. If its reached
        a patrol point, it cycles to the next one. Currently it only does 
        patrol points on the same plane so patrol points with a y component 
        will not be respected.       
        """
        self.update_patrol_point()
        dist_from_x = self.current_patrol_point[0] - self.x
        if dist_from_x < 0:
            amount = -self.speed * delta_game_time
            self.velocity = [amount, 0]
        else:
            amount = self.speed * delta_game_time
            self.velocity = [amount, 0]
    
    def update_patrol_point(self):
        """
        Helper function. Checks if this sentinal has reached the patrol point
        if so, it cycles the next patrol point is queued 
        """
        dist_from_x = self.current_patrol_point[0] - self.x
        if abs(dist_from_x) < 25:
            self.patrol_index = (self.patrol_index + 1) % len(self.patrol_list)
            self.current_patrol_point = self.patrol_list[self.patrol_index]

    def get_image(self, vector):
        """
        Cycles the sentinals current sprite.

        param - vector: the current vector of this sentinal 
        """
        self.facing_left = True if self.velocity[0] < 0 else False
        self.image = self.sprite_manager.get_sprite(self.facing_left)
        self.image = pygame.transform.scale(self.image, self.image_size)
        # self.rect = self.image.get_rect()

    def get_killed(self, projectile):
        projectile.kill_function(projectile)
        self.kill_function(self)
