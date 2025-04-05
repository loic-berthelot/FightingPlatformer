import pygame, math, common
pygame.init()
from objects import Object

class Foot(Object) :
    def __init__(self, side):
        super().__init__(("foot", 0, 0))
        self.object_type = "foot"
        self.stance = "stand"
        self.org_image = common.get_image("resources/feet/"+self.stance+".png")
        self.mask = pygame.mask.from_surface(self.org_image)
        self.image = self.org_image.copy()
        self.rect = self.image.get_rect()
        self.shift = [0, 0]
        self.orientation = 1
        self.foot_side = side
        self.moving_direction = self.foot_side
        self.is_visible = True
        self.previous_stance = None
        self.previous_direction = 1
        self.action = None
        self.action_counter = 0
        self.leg_length = 25
        self.exceptions = []

    def update(self, character):
        if character.orientation != self.previous_direction :
            self.previous_direction = character.orientation
            self.shift = [self.shift[0] * -1, 0]
            self.orientation *= -1
        if character.stance != self.previous_stance:
            self.previous_stance = character.stance
            if character.stance != "stand" : self.action = None
            if character.stance == "crawling" : self.shift = [character.orientation * -28, 0]
            elif character.stance == "climbing" : self.shift = [self.foot_side * -7, 0]
            else : self.shift = [0, 0]
            if character.stance in ["stand", "crawling", "climbing"] : self.is_visible = True
            else : self.is_visible = False
            if character.stance == "climbing" : self.org_image = common.get_image("resources/feet/climbing.png")
            else : self.org_image = common.get_image("resources/feet/stand.png")
            if character.stance in ["climbing"]: self.orientation = 0
            self.moving_direction = self.foot_side
        if self.action == "kick" :
            self.org_image = common.get_image("resources/feet/stand.png")
            if self.foot_side == 1 :
                if self.orientation*character.orientation < 90 : self.orientation += 4*character.orientation
                self.shift = [self.leg_length * math.sin(math.radians(self.orientation)), -self.leg_length + self.leg_length * math.cos(math.radians(self.orientation))]
            else :
                self.orientation = 0
                self.shift = [0, 0]
            if self.action_counter == 0 : self.action = "normal"
        elif self.action == "normal" :
            self.org_image = common.get_image("resources/feet/stand.png")
            if abs(self.orientation) <= 3 :
                self.orientation = 0
                self.action = None
            else :
                if self.orientation * character.orientation > 0 : self.orientation -= 3 * character.orientation
                elif self.orientation * character.orientation < 0 : self.orientation += 3 * character.orientation
            self.shift = [self.leg_length * math.sin(math.radians(self.orientation)), -self.leg_length + self.leg_length * math.cos(math.radians(self.orientation))]
        else :
            if character.stance == "stand" :
                if abs(character.speed[0]) < 1 or not character.is_onground:
                    if abs(self.shift[0]) < 2 :
                        self.shift[0] = 0
                        self.moving_direction = self.foot_side
                        speed = 0
                    else :
                        if self.shift[0] < 0 : self.moving_direction = 1
                        else : self.moving_direction = -1
                        speed = 1.5*self.moving_direction
                else : speed = character.speed[0]*self.moving_direction
                if self.shift[0] < -15 : self.moving_direction = 1
                if self.shift[0] > 15 : self.moving_direction = -1
                self.shift[0] += 0.5*abs(speed)*self.moving_direction
                self.orientation = math.degrees(math.atan(self.shift[0]/35))
            elif character.stance == "crawling" :
                self.orientation = -90*character.orientation
                self.shift[0] += 0.5*abs(character.speed[0])*self.moving_direction
                if self.shift[0]*character.orientation < -36 : self.moving_direction = character.orientation
                elif self.shift[0]*character.orientation > -20 : self.moving_direction = -character.orientation
            elif character.stance == "climbing" :
                if abs(character.speed[1]) < 0.5 :
                    self.shift[1] = 0
                    self.moving_direction = self.foot_side
                else :
                    self.shift[1] += 0.5*self.moving_direction*abs(character.speed[1])
                    if self.shift[1] > 15 : self.moving_direction = -1
                    if self.shift[1] < -15 : self.moving_direction = 1
            else :
                self.shift = [0,0]
        if self.action_counter > 0 : self.action_counter -= 1
        self.image = self.org_image.copy()
        if character.orientation < 0 : self.image = pygame.transform.flip(self.image, True, False)
        if self.orientation != 0 : self.image = pygame.transform.rotozoom(self.image, self.orientation, 1)
        self.mask = pygame.mask.from_surface(self.org_image)

    def kick(self):
        self.action = "kick"
        self.action_counter = 30
        self.exceptions = []
