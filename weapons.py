import pygame, math, common
pygame.init()
from objects import Object

class Weapon(Object) :
    def __init__(self, name, owner=None):
        super().__init__(("weapon", 0, 0))
        self.object_type = "weapon"
        self.name = name
        self.owner = owner
        self.actions_duration = {"charge" : 20, "hit" : 40, "ultimate" : 50, "heavy_hit" : 50, "raise" : 15}
        ultimate_durations = {"sword" : 120}
        if self.name in ultimate_durations.keys() : self.actions_duration["ultimate"] = ultimate_durations[self.name]
        if self.name in ["bow"] : self.name_index = 0
        else : self.name_index = None
        self.update_image()
        self.screen_pos = [0, 0]
        default_angles = {"bow":-90}
        if self.name in default_angles.keys() : self.default_angle = default_angles[self.name]
        else : self.default_angle = 0
        self.angle = self.default_angle
        tangent_shifts = {"bow": 6}
        if self.name in tangent_shifts.keys() : self.tangent_shift = tangent_shifts[self.name]
        else : self.tangent_shift = 0
        self.is_hitting = False
        self.is_heavy_hitting = False
        self.action_counter = 0
        self.rotate_speed = 0
        self.arm_lenght = 15
        self.is_ult = False
        self.action = None
        self.charge_power = 0

    def update(self, orientation):
        if self.action == "charge" :
            self.charge_power += 1
            if self.action_counter > 0 :
                self.angle += 100 / self.actions_duration["charge"]
                self.arm_lenght += 27 / self.actions_duration["charge"]
                if self.name == "bow" :
                    if self.name_index == 0 :
                        self.name_index = 1
                        self.update_image()
                    elif self.action_counter == 1 :
                        self.name_index = 2
                        self.update_image()
        elif self.action == "hit" :
            if self.name == "bow" and self.name_index != 0 :
                self.name_index = 0
                self.update_image()
            if int(self.actions_duration["hit"]*0.63) < self.action_counter :
                if self.action_counter == int(self.actions_duration["hit"]) : self.is_hitting = True
                self.angle -= 480/self.actions_duration["hit"]
                if int(self.actions_duration["hit"]*0.75) < self.action_counter : self.arm_lenght -= 146 / self.actions_duration["hit"]
            elif 0 < self.action_counter and self.action_counter <= int(self.actions_duration["hit"]*0.63) :
                self.is_hitting = False
                self.angle += 100/self.actions_duration["hit"]
                self.arm_lenght += 16 / self.actions_duration["hit"]
            else :
                self.angle = self.default_angle
                self.arm_lenght = 15
                self.action = None
        elif self.action == "heavy_hit":
            if self.name == "bow":
                self.name_index = 0
                self.update_image()
                if int(self.actions_duration["heavy_hit"] * 0.67) <= self.action_counter and self.action_counter <= self.actions_duration["heavy_hit"]:
                    if self.action_counter == self.actions_duration["heavy_hit"] : self.is_heavy_hitting = True
                    else : self.is_heavy_hitting = False
                elif int(self.actions_duration["heavy_hit"] * 0.33) < self.action_counter and self.action_counter < self.actions_duration["heavy_hit"] * 0.67:
                    self.is_heavy_hitting = False
                else : self.action = "normal"
        elif self.action == "ultimate" :
            if self.name == "axe" :
                if self.is_ult : self.is_ult = False
                if int(self.actions_duration["ultimate"] * 0.67) < self.action_counter and self.action_counter <= self.actions_duration["ultimate"]:
                    self.angle += 300 / self.actions_duration["ultimate"]
                    self.arm_lenght += 80 / self.actions_duration["hit"]
                elif int(self.actions_duration["ultimate"] * 0.42) < self.action_counter and self.action_counter <= int(self.actions_duration["ultimate"] * 0.67):
                    if self.action_counter == int(self.actions_duration["ultimate"] * 0.67): self.is_ult = True
                    self.angle -= 720 / self.actions_duration["ultimate"]
                    if int(self.actions_duration["ultimate"] * 0.5) < self.action_counter: self.arm_lenght -= 220 / self.actions_duration["ultimate"]
                elif 0 < self.action_counter and self.action_counter <= int(self.actions_duration["ultimate"] * 0.42):
                    self.angle += 150 / self.actions_duration["ultimate"]
                    self.arm_lenght += 25 / self.actions_duration["ultimate"]
                else:
                    self.is_ult = False
                    self.angle = 0
                    self.arm_lenght = 20
                    self.action = None
            elif self.name == "hammer" :
                if int(self.actions_duration["ultimate"] * 0.67) < self.action_counter and self.action_counter <= self.actions_duration["ultimate"]:
                    self.angle += 300 / self.actions_duration["ultimate"]
                    self.arm_lenght += 80 / self.actions_duration["hit"]
                elif int(self.actions_duration["ultimate"] * 0.42) < self.action_counter and self.action_counter <= int(self.actions_duration["ultimate"] * 0.67):
                    if self.action_counter == int(self.actions_duration["ultimate"] * 0.67): self.is_ult = True
                    self.angle -= 720 / self.actions_duration["ultimate"]
                    if int(self.actions_duration["ultimate"] * 0.5) < self.action_counter: self.arm_lenght -= 220 / self.actions_duration["ultimate"]
                elif 0 < self.action_counter and self.action_counter <= int(self.actions_duration["ultimate"] * 0.42):
                    self.angle += 150 / self.actions_duration["ultimate"]
                    self.arm_lenght += 25 / self.actions_duration["ultimate"]
                else:
                    self.is_ult = False
                    self.angle = 0
                    self.arm_lenght = 15
                    self.action = None
            elif self.name == "sword" :
                if self.action_counter > 0 :
                    self.angle -= 20
                    self.is_ult = True
                else :
                    self.action = "normal"
                    self.is_ult = False
            elif self.name == "bow" :
                if self.name_index == 0 :
                    self.name_index = 1
                    self.update_image()
                if int(self.actions_duration["ultimate"]*0.4) < self.action_counter :
                    if self.name_index == 1:
                        self.name_index = 2
                        self.update_image()
                    self.angle += 150 / self.actions_duration["ultimate"]
                    self.arm_lenght += 60 / self.actions_duration["ultimate"]
                elif int(self.actions_duration["ultimate"]*0.2) <= self.action_counter and self.action_counter <= int(self.actions_duration["ultimate"]*0.4) :
                    if self.action_counter == int(self.actions_duration["ultimate"]*0.4) :
                        self.is_ult = True
                        self.name_index = 0
                        self.update_image()
                    else : self.is_ult = False
                else : self.action = "normal"
        elif self.action == "raise" :
            if 0 < self.action_counter :
                if self.angle < 80 : self.angle += 6
                if self.arm_lenght < 45 : self.arm_lenght += 2
                if self.arm_lenght > 45 : self.arm_lenght -= 2
            else : self.action = "raised"
        elif self.action == "raised" :
            if self.action_counter < 20 :
                self.arm_lenght += 0.3
                if self.action_counter == 0 : self.action_counter = 40
            else : self.arm_lenght -= 0.3
        elif self.action == "normal" :
            self.rotate_speed = 0
            if self.name_index != None and self.name_index != 0 :
                self.name_index = 0
                self.update_image()
            speed = 4
            if self.angle - self.default_angle > 360 : self.angle = self.angle%360
            if abs((self.angle-self.default_angle)%360) <= speed :
                self.angle = self.default_angle
                self.arm_lenght = 15
                self.action = None
            else:
                self.arm_lenght -= (self.arm_lenght-15)/abs(self.angle-self.default_angle)
                if (self.angle - self.default_angle)%360 > 180 or (self.angle - self.default_angle)%360 < -180 : self.angle += speed
                else : self.angle -= speed
        self.angle += self.rotate_speed
        if self.action_counter > 0 : self.action_counter -= 1
        self.orientation = orientation
        if self.angle != 0 :
            self.image = pygame.transform.rotozoom(self.org_image, self.angle, 1)
            self.hitbox = pygame.transform.rotozoom(self.org_hitbox, self.angle, 1)
        else :
            self.image = self.org_image
            self.hitbox = self.org_hitbox
        if orientation == -1 :
            self.image = pygame.transform.flip(self.image, True, False)
            self.hitbox = pygame.transform.flip(self.hitbox, True, False)
        self.mask = pygame.mask.from_surface(self.hitbox)

    def update_image(self):
        if self.name_index == None : self.org_image = common.get_image("resources/weapons/" + self.name + ".png")
        else : self.org_image = common.get_image("resources/weapons/" + self.name + str(self.name_index) + ".png")
        self.org_hitbox = common.get_image("resources/hitboxes/" + self.name + ".png")
        self.image = self.org_image
        self.rect = self.image.get_rect()

    def update_rect(self, orientation, character_pos, character_screen_pos, character_size):
        self.orientation = orientation
        shift = [0, 0]
        shift[0] += self.orientation * -40
        shift[1] += 50
        rect = self.image.get_rect()
        if self.orientation == 1: shift[0] += character_size[0]
        else: shift[0] -= rect[2]
        shift[1] -= rect[3] / 2
        shift[0] += self.orientation * self.arm_lenght * math.cos(math.radians(self.angle))
        shift[1] -= self.arm_lenght * math.sin(math.radians(self.angle))
        shift[0] += self.orientation * self.tangent_shift * math.sin(math.radians(self.angle))
        shift[1] -= self.tangent_shift * math.cos(math.radians(self.angle))
        self.screen_pos[0] = character_screen_pos[0] + shift[0]
        self.screen_pos[1] = character_screen_pos[1] + shift[1]
        self.rect.x = character_pos[0] + shift[0]
        self.rect.y = character_pos[1] + shift[1]
        rect = self.image.get_rect()
        self.rect.width = rect.width
        self.rect.height = rect.height

    def charge(self):
        self.return_normal(True)
        self.action_counter = self.actions_duration["charge"]
        self.rotate_speed = 0
        self.exceptions = []
        self.action = "charge"

    def hit(self):
        self.action_counter = self.actions_duration["hit"]
        self.rotate_speed = 0
        self.exceptions = []
        self.action = "hit"

    def raise_weapon(self):
        self.action_counter = self.actions_duration["raise"]
        self.rotate_speed = 0
        self.action = "raise"

    def heavy_hit(self):
        if self.name in ["bow"] :
            self.action_counter = self.actions_duration["heavy_hit"]
            self.action = "heavy_hit"
            self.rotate_speed = 0
            self.exceptions = []
        else :
            self.hit()

    def use_ultimate(self):
        self.exceptions = []
        self.action_counter = self.actions_duration["ultimate"]
        self.action = "ultimate"

    def return_normal(self, directly = False):
        self.arm_lenght = 15
        if directly :
            self.action = None
            self.angle = 0
        else :
            self.action = "normal"