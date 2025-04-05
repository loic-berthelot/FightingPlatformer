import pygame, math
from objects import Object

class Shield(Object):
    def __init__(self, words):
        super().__init__((words[0], 0, 0))
        self.object_type = "shield"
        self.name = words[0]
        self.aspects = {}
        for aspect in ("in", "raised", "out") : self.aspects[aspect] = pygame.image.load("resources/shields/"+self.name+"_"+aspect+".png")
        self.org_image = self.aspects["in"]
        self.image = self.org_image
        self.rect = self.image.get_rect()
        self.is_blocking = True
        self.action_counter = 0
        self.angle = 0
        self.rotate_speed = 0
        self.orientation = 1
        self.shift = [0, 0]
        self.shield_duration = 110

    def update(self, orientation):
        if self.action_counter > 0:
            if self.shield_duration - 10 < self.action_counter and self.action_counter <= self.shield_duration:
                self.shift[0] += 1.50
                self.shift[1] -= 0.75
            elif self.action_counter == self.shield_duration - 10 :
                self.is_blocking = True
                self.org_image = self.aspects["raised"]
            elif self.action_counter == 16 :
                self.is_blocking = False
                if self.orientation == 1 : self.org_image = self.aspects["in"]
                else : self.org_image = self.aspects["out"]
            elif 0 < self.action_counter and self.action_counter <= 15:
                self.shift[0] -= 1
                self.shift[1] += 0.5
        else :
            self.is_blocking = False
            self.angle = 0
            self.rotate_speed = 0
        self.angle += self.rotate_speed
        if self.action_counter != 0 : self.action_counter -= 1
        if self.action_counter == 0 :
            self.orientation = orientation
            self.shift = [0,0]
            if self.orientation == 1 : self.org_image = self.aspects["in"]
            else : self.org_image = self.aspects["out"]
        self.image = self.org_image.copy()
        self.hitbox = pygame.image.load("resources/hitboxes/shield.png")
        if orientation == -1 :
            self.image = pygame.transform.flip(self.image.copy(), True, False)
            self.hitbox = pygame.transform.flip(self.hitbox.copy(), True, False)
        if self.angle != 0 :
            self.image = pygame.transform.rotozoom(self.image.copy(), self.orientation * self.angle, 1)
            self.hitbox = pygame.transform.rotozoom(self.hitbox.copy(), self.orientation * self.angle, 1)
        self.mask = pygame.mask.from_surface(self.hitbox)

    def update_rect(self, orientation, character_pos, character_screen_pos, character_size):
        self.rect = self.image.get_rect()
        self.orientation = orientation
        shift = [self.shift[0]*self.orientation, self.shift[1]]
        shift[0] += self.orientation * -30
        shift[1] += 50
        rect = self.image.get_rect()
        if self.orientation == 1: shift[0] += character_size[0]
        else: shift[0] -= rect[2]
        shift[1] -= rect[3] / 2
        shift[0] += self.orientation * 20 * math.cos(math.radians(self.angle))
        shift[1] -= 20 * math.sin(math.radians(self.angle))
        self.rect.x = character_pos[0] + shift[0]
        self.rect.y = character_pos[1] + shift[1]
        self.screen_pos[0] = character_screen_pos[0] + shift[0]
        self.screen_pos[1] = character_screen_pos[1] + shift[1]

    def raise_shield(self):
        success = False
        if self.action_counter == 0 :
            self.action_counter = self.shield_duration
            success = True
        return success
