import pygame, math, random
import common
pygame.init()
from objects import Object

class Item(Object):
    def __init__(self, words, force=(0,0)):
        super().__init__(words)
        self.object_type = "item"
        self.name = words[0]
        self.image = common.get_image("resources/items/"+self.name+".png")
        self.rect = self.image.get_rect()
        self.pos = [int(words[1]) - int(self.rect.width/2), int(words[2]) - int(self.rect.height/2)]
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]
        self.pos_shift = [0,0]
        self.period = 60
        self.amplitude = 5
        self.speed = [force[0], force[1]]
        self.is_pickable = False
        self.alive = True
        self.lifetime = common.items_lifetime
        self.has_gravity = True
        self.is_shaking = True

    def update_rect(self, weight_intensity, border_size):
        if self.has_gravity : self.speed[1] += weight_intensity
        self.speed[0] *= 0.97
        self.speed[1] *= 0.97
        self.pos[0] += self.speed[0]
        self.pos[1] += self.speed[1]
        self.rect.x = int(self.pos[0])
        self.rect.y = int(self.pos[1])
        self.interact(common.grid_objects)
        if self.alive :
            if self.lifetime == 0 :
                self.alive = False
            else:
                if self.lifetime > 0 :
                    if self.link == 0 : self.lifetime -= 1
                if common.cm_el(common.block_interactions, self.collide_background()):
                    self.pos[0] -= self.speed[0]
                    self.pos[1] -= self.speed[1]
                    self.speed  = [0, 0]
                self.collide_border(border_size)
                if abs(self.speed[0]) <= 4 and abs(self.speed[1]) <= 4:
                    self.is_pickable = True
                else :
                    self.is_pickable = False
                if self.is_shaking : self.pos_shift[1] = self.amplitude*(-1+math.cos((common.frame_number%self.period)/self.period*2*3.1415))
                self.screen_pos[0] = int(self.rect.x + self.pos_shift[0] - common.camera_x)
                self.screen_pos[1] = int(self.rect.y + self.pos_shift[1] - common.camera_y)
                self.grid_move()
        else :
            self.remove()
            pygame.sprite.Sprite.kill(self)

    def interact(self, grid_objects):
        if self.name == "wood":
            groups = common.sort_groups(groups=("background"), area=(self.get_area()))
            for background in groups["background"]:
                if pygame.sprite.collide_mask(self, background):
                    if background.name.startswith("bridge"):
                        if background.modify(["repair"]):
                            self.alive = False
                    elif background.name.startswith("gate"):
                        if background.modify(["repair"]) :
                            self.alive = False
            common.clean_groups(groups)
            groups = common.sort_groups(groups=("effect"), area=(self.get_area()))
            for effect in groups["effects"] :
                if effect.name.startswith("campfire") :
                    if pygame.sprite.collide_mask(self, effect) :
                        effect.fire_power += 30
                        self.alive = False
            common.clean_groups(groups)