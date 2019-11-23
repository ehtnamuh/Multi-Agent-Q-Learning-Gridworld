import numpy as np
from PIL import Image
import cv2

class Blob:
    def __init__(self, my_color, SIZE):
        self.SIZE = SIZE
        self.color = my_color
        self.score = 0
        self.x = np.random.randint(0, self.SIZE)
        self.y = np.random.randint(0, self.SIZE)
    
    def __str__(self):
        return "%d, %d"%(self.x, self.y)
    
    def get_pos(self):
        return (self.x, self.y)
    
    def randomize_pos(self):
        self.x = np.random.randint(0, self.SIZE)
        self.y = np.random.randint(0, self.SIZE)
        return self.get_pos()
    
    def __sub__(self, other):
        return (self.x-other.x, self.y-other.y)
    
    def action(self, choice):
        if choice == 0: self.move(x= 0, y= -1)
        elif choice == 1: self.move(x= 0, y= 1)
        elif choice == 2: self.move(x= -1 , y= 0)
        elif choice == 3: self.move(x= 1, y= 0)
        
    # up down left right x-axis left, y axis going down
    def try_action(self, choice):
        if choice == 0:   x, y= 0, -1
        elif choice == 1: x, y = 0, 1
        elif choice == 2: x, y = -1, 0
        elif choice == 3: x, y = 1, 0
        return (self.x + x, self.y + y)
    
    def move(self, x=False, y=False):
        self.x += x
        self.y += y
        
        if self.x < 0: self.x = 0
        elif self.x > self.SIZE-1: self.x = self.SIZE-1
        
        if self.y < 0: self.y = 0
        elif self.y > self.SIZE-1: self.y = self.SIZE-1