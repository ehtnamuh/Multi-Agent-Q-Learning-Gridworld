import numpy as np
from PIL import Image
from PIL import ImageDraw
from cv2 import cv2
from typing import overload
import Blob
import MyConstants

# PLAYER COLLISION STATES
class States():
    HIT_ENEMY = 'hit_enemy'
    HIT_OBSTACLE = 'hit_obstacle'
    HIT_FOOD = 'hit_food'
    HIT_TRAP = 'hit_trap'

# RED CHASES BLUE; BLUE CHASES GREEN; GREEN CHASES RED
class MyGame():
    # Object Color data
    PLAYER_N = 1
    FOOD_N = 2
    ENEMY_N = 3
    OBSTACLE_N = 4
    TRAP_N = 5
    d = {1: (255, 175, 0),
        2: (0, 255, 0),
        3: (0, 0, 255),
        4: (255, 255, 255),
        5: (0, 165, 255)}
    
    # Obstacles N trap locations by lvl
    levels = {'level1': {
        'obstacles': [(2, 3), (2, 5), (2, 6), (2, 7),
                    (6, 3), (6, 5), (6, 6), (6, 7),
                    (4, 3), (4, 8)],
        'traps': [(4, 5), (8, 1)]
    }, 'level2': {
        'obstacles': [ (1,2), (3,2), (1,6), (2,5), (3,6), (5,4), (6,5), (7,4), (9,4), (9,7)],
        'traps': [(2, 9), (7, 1)]
    }}

    # Game States
    STATE_ENEMY_WIN = "ENEMY_WIN"
    STATE_PLAYER_WIN = "PLAYER_WIN"
    STATE_FOOD_WIN = "FOOD_WIN"
    STATE_DRAW = "DRAW"
    
    def __init__(self, level='level1', SIZE=10, is_training = False):
        if (SIZE < 10):
            SIZE = 10
        self.SIZE = SIZE
        self.game_end_condition = False
        self.episode_number = 0
        self.trap_counter = 0
        self.environment = []
        self.is_training = is_training
        self.game_state = self.STATE_DRAW
        # TODO: READ LEVELS FORM FILE LATER
        # self.levels = some file read operation
        self.load_level(level)
        self.Blobs = { MyConstants.PLAYER: None, MyConstants.ENEMY: None, MyConstants.FOOD: None }
        # self.player, self.enemy, self.food = None, None, None
        self.create_blobs()

    def load_level(self, level='level1'):
        self.obstacle_list = self.levels[level]['obstacles']
        self.trap_list = self.levels[level]['traps']

    def update_environment(self):
        self.environment = np.zeros(
            (self.SIZE, self.SIZE, 3), dtype=np.uint8)
        for obstacle in self.obstacle_list:
            self.environment[obstacle[1]][obstacle[0]] = self.d[self.OBSTACLE_N]
        for trap in self.trap_list:
            self.environment[trap[1]][trap[0]] = self.d[self.TRAP_N]
        
        if (self.Blobs[MyConstants.FOOD].is_active): 
            self.environment[self.Blobs[MyConstants.FOOD].y][self.Blobs[MyConstants.FOOD].x] = self.Blobs[MyConstants.FOOD].color
        
        if (self.Blobs[MyConstants.PLAYER].is_active): self.environment[self.Blobs[MyConstants.PLAYER].y][self.Blobs[MyConstants.PLAYER].x] = self.Blobs[MyConstants.PLAYER].color
        
        if (self.Blobs[MyConstants.ENEMY].is_active): self.environment[self.Blobs[MyConstants.ENEMY].y][self.Blobs[MyConstants.ENEMY].x] = self.Blobs[MyConstants.ENEMY].color

    def reset_environment(self):
        self.environment = []
        self.episode_number += 1
        self.trap_counter = 0
        self.game_state = self.STATE_DRAW
        self.create_blobs()
        self.game_end_condition = False
        self.update_environment()

    def create_blobs(self):
        if (self.Blobs[MyConstants.PLAYER] == None): self.Blobs[MyConstants.PLAYER] = Blob.Blob(self.d[self.PLAYER_N], self.SIZE)
        if (self.Blobs[MyConstants.ENEMY] == None): self.Blobs[MyConstants.ENEMY] = Blob.Blob(self.d[self.ENEMY_N] ,self.SIZE)
        if (self.Blobs[MyConstants.FOOD] == None): self.Blobs[MyConstants.FOOD] = Blob.Blob(self.d[self.FOOD_N], self.SIZE)
        self.Blobs[MyConstants.PLAYER].activate()
        self.Blobs[MyConstants.ENEMY].activate()
        self.Blobs[MyConstants.FOOD].activate()
        self.Blobs[MyConstants.PLAYER].randomize_pos()
        self.Blobs[MyConstants.ENEMY].randomize_pos()
        self.Blobs[MyConstants.FOOD].randomize_pos()
        while ( self.Blobs[MyConstants.PLAYER].get_pos() in self.obstacle_list or
                self.Blobs[MyConstants.PLAYER].get_pos() in self.trap_list):
            self.Blobs[MyConstants.PLAYER].randomize_pos()
        while (self.Blobs[MyConstants.ENEMY].get_pos() in self.obstacle_list or
                self.Blobs[MyConstants.ENEMY].get_pos() in self.trap_list):
            self.Blobs[MyConstants.ENEMY].randomize_pos()
        while (self.Blobs[MyConstants.FOOD].get_pos() in self.obstacle_list or
                self.Blobs[MyConstants.FOOD].get_pos() in self.trap_list):
            self.Blobs[MyConstants.FOOD].randomize_pos()
    
    def draw_message(self, image, location, my_msg, my_color):
        ImageDraw.Draw(
            image  # Image
        ).text(
            location,  # Coordinates
            my_msg,  # Text
            my_color  # Color
        )

    def draw_score(self, image):
        my_message = "PLAYER SCORE: " + str( self.Blobs[MyConstants.PLAYER].score )
        self.draw_message(image, (0,0),  my_message, self.Blobs[MyConstants.PLAYER].color)
        my_message = "ENEMY SCORE: " + str( self.Blobs[MyConstants.ENEMY].score )
        self.draw_message(image, (0,10),  my_message, self.Blobs[MyConstants.ENEMY].color)
        my_message = "FOOD SCORE: " + str( self.Blobs[MyConstants.FOOD].score )
        self.draw_message(image, (0,20),  my_message, self.Blobs[MyConstants.FOOD].color)
        my_message = "EPISODE NO: " + str( self.episode_number )
        self.draw_message(image, (0,30),  my_message, (255, 255, 255))

    def draw_game_state(self, image):
        if self.game_state == self.STATE_ENEMY_WIN: my_color = self.Blobs[MyConstants.ENEMY].color
        elif self.game_state == self.STATE_FOOD_WIN: my_color = self.Blobs[MyConstants.FOOD].color
        elif self.game_state == self.STATE_PLAYER_WIN: my_color = self.Blobs[MyConstants.PLAYER].color
        else: my_color =  (255, 255, 255)
        self.draw_message(image, (232, 0), self.game_state, my_color)

    def render(self, W_WIDTH=300, W_HEIGHT=300, show = False, final_frame = False):
        img = Image.fromarray(self.environment, "RGB")
        img = img.resize((W_WIDTH, W_HEIGHT))
        self.draw_score(img)
        if final_frame: 
            self.draw_game_state(img)
        img = np.array(img)
        if show: 
            cv2.imshow("Catch A Fly", img)
        return img

    # update scores calls update environment implicitly
    def update_scores(self):
        if self.Blobs[MyConstants.PLAYER].get_pos() == self.Blobs[MyConstants.FOOD].get_pos() and  self.Blobs[MyConstants.FOOD].is_active:
            self.Blobs[MyConstants.FOOD].deactivate()
            self.Blobs[MyConstants.PLAYER].score += 1
            self.game_state = self.STATE_PLAYER_WIN
            self.game_end_condition = True
        elif self.Blobs[MyConstants.ENEMY].get_pos() == self.Blobs[MyConstants.PLAYER].get_pos() and self.Blobs[MyConstants.PLAYER].is_active:
            self.Blobs[MyConstants.PLAYER].deactivate() 
            self.Blobs[MyConstants.ENEMY].score += 1
            self.game_state = self.STATE_ENEMY_WIN
            self.game_end_condition = True
        elif self.Blobs[MyConstants.FOOD].get_pos() == self.Blobs[MyConstants.ENEMY].get_pos() and self.Blobs[MyConstants.ENEMY].is_active:
            self.Blobs[MyConstants.ENEMY].deactivate() 
            self.Blobs[MyConstants.FOOD].score += 1
            self.game_state = self.STATE_FOOD_WIN
            self.game_end_condition = True
        self.update_environment()
    
    def check_traps(self, col_st, viewer):
        if col_st[States.HIT_TRAP] == True:
            self.Blobs[viewer].deactivate()
            self.trap_counter += 1
            if self.trap_counter >= 2:
                self.game_end_condition = True

    # returns player collision state
    def check_player_collisions(self, position, viewer):
        col_st = {States.HIT_OBSTACLE: False, States.HIT_TRAP: False,
                        States.HIT_ENEMY: False, States.HIT_FOOD: False}
        if position in self.obstacle_list:
            col_st[States.HIT_OBSTACLE] = True
        if position in self.trap_list:
            col_st[States.HIT_TRAP] = True
        if (viewer == MyConstants.PLAYER):
            if position == self.Blobs[MyConstants.ENEMY].get_pos():
                col_st[States.HIT_ENEMY] = True
            if position == self.Blobs[MyConstants.FOOD].get_pos():
                col_st[States.HIT_FOOD] = True
        if (viewer == MyConstants.ENEMY):
            if position == self.Blobs[MyConstants.FOOD].get_pos():
                col_st[States.HIT_ENEMY] = True
            if position ==self.Blobs[MyConstants.PLAYER].get_pos():
                col_st[States.HIT_FOOD] = True
        if (viewer == MyConstants.FOOD):
            if position == self.Blobs[MyConstants.PLAYER].get_pos():
                col_st[States.HIT_ENEMY] = True
            if position ==self.Blobs[MyConstants.ENEMY].get_pos():
                col_st[States.HIT_FOOD] = True
        return col_st

    # every entity takes 1 step , 1  tick of this game
    def env_step(self, action=False, viewer = MyConstants.PLAYER):
        # Prevent things from crossing over walls
        if not action:
            action = np.random.randint(0, 4)
        player_col_st = self.check_player_collisions(self.Blobs[viewer].try_action(action), viewer)
        hit_obstacle = player_col_st['hit_obstacle']
        if not hit_obstacle:
            self.Blobs[viewer].action(action)
        
        # update scores calls update environment implicitly
        self.check_traps(player_col_st, viewer)
        self.update_scores() 
        return (self.get_obeservation(viewer), player_col_st, self.game_end_condition)

    # format (player, enemy, food)
    def get_obeservation(self, viewer=MyConstants.PLAYER):
        if viewer == MyConstants.PLAYER:
            return (self.Blobs[MyConstants.PLAYER].get_pos(), self.Blobs[MyConstants.ENEMY].get_pos(), self.Blobs[MyConstants.FOOD].get_pos())
        if viewer == MyConstants.ENEMY:
            return (self.Blobs[MyConstants.ENEMY].get_pos(), self.Blobs[MyConstants.FOOD].get_pos(), self.Blobs[MyConstants.PLAYER].get_pos())
        if viewer == MyConstants.FOOD:
            return (self.Blobs[MyConstants.FOOD].get_pos(), self.Blobs[MyConstants.PLAYER].get_pos(), self.Blobs[MyConstants.ENEMY].get_pos())

    def get_blobs(self):
        return self.Blobs
    
    # returns number of blobs in trap
    def get_trap_counter(self):
        return self.trap_counter