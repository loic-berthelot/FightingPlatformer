import pygame, common, math
pygame.init()
from objects import Object

class Cape(Object) :
    def __init__(self, words):
        super().__init__(words)
        self.stance = "stand"
        self.name = words[0]
        self.pos = [words[1], words[2]]
        self.color = (words[3], words[4], words[5])
        self.shift = [0, 0]
        self.orientation = 1
        self.screen_pos = self.pos.copy()
        self.org_image = common.get_image("resources/characters/human/cape/"+self.name+"_"+self.stance+".png")
        self.image = self.org_image.copy()
        self.angle = 0

    def update(self, orientation, angle, stance):
        self.orientation = orientation
        self.angle = angle
        self.stance = stance
        try : self.image = common.get_image("resources/characters/human/cape/" + self.name + "_" + self.stance + ".png")
        except : self.image = common.get_image("resources/characters/human/cape/none.png")
        if angle != 0 : self.image = pygame.transform.rotozoom(self.image.copy(), angle, 1)
        rect = self.image.get_rect()
        colorimage = pygame.Surface((rect.width, rect.height)).convert_alpha()
        colorimage.fill(self.color)
        self.image.blit(colorimage, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        self.image = pygame.transform.flip(self.image, self.orientation==-1, False)

    def update_rect(self, orientation, character_pos, character_screen_pos, character_size):
        self.orientation = orientation
        rect = self.image.get_rect()
        if self.stance == "rolling" :
            shift = [character_size[0]/2-rect.width/2, character_size[1]/2-rect.height/2]
            if self.orientation == 1 : angle = math.radians(self.angle)
            else : angle = math.radians(180-self.angle)
            dx = -14
            dy = -12*self.orientation
            shift[0] += dx*math.cos(angle) - dy*math.sin(angle)
            shift[1] += -dx*math.sin(angle) - dy*math.cos(angle)
        else :
            shift = [self.shift[0]*self.orientation, self.shift[1] + 19]
            if self.orientation == 1 : shift[0] += character_size[0]
            else : shift[0] -= rect.width
            if self.stance == "stand" :
                shift[0] += self.orientation * -28
            elif self.stance == "crouched" :
                shift[0] += self.orientation * -45
                shift[1] += 3
            elif self.stance == "crawling":
                shift[0] += self.orientation * -68
                shift[1] += 25
            elif self.stance == "climbing" :
                shift[0] += self.orientation * -28
        self.screen_pos[0] = character_screen_pos[0] + shift[0]
        self.screen_pos[1] = character_screen_pos[1] + shift[1]