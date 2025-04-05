import pygame, common
pygame.init()
from objects import Object

class Background(Object):
    def __init__(self, words):
        super().__init__(words)
        self.object_type = "background"
        self.name = words[0]
        if len(words) > 3:
            self.angle = int(words[3])
            if len(words) > 4:
                self.flip = int(words[4])
        self.image = common.get_image("resources/background/"+self.name+".png")
        self.rect = self.image.get_rect()
        self.update_image("background")
        self.rect = self.image.get_rect()
        self.pos = [int(words[1]), int(words[2])]
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]
        self.screen_pos=[self.pos[0],self.pos[1]]
        self.collide_type = "block"
        self.mask = pygame.mask.from_surface(self.hitbox)
        if self.name .startswith("signpost") :
            self.collide_type = "signpost"
        if self.name in ["beam1"] :
            self.collide_type = "none"
        if self.name.startswith("scale"): self.collide_type = "scale"
        if self.name in ["escape_door1"]: self.collide_type = "escape"
        if self.name.startswith("gate") or self.name.startswith("bridge"):
            self.max_health = 2
            if "solid" in self.name : self.health = self.max_health
            else : self.health = 0
            if len(words) > 5: self.health = int(words[5])
        if self.collide_type == "none":
            self.mask = pygame.mask.Mask(size=(0, 0), fill=False)
        if self.name.startswith("gate") or self.name.startswith("bridge") :
            self.is_breakable = True
        if self.name.startswith("signpost"):
            self.text = words[5]
        if self.name in ["guillotine", "flag_pole"] :
            self.first_frame = True
        if self.name == "flag_pole" :
            self.collide_type = "none"
            self.teams_influence = {}
            if len(words) > 5 : self.capture_time = int(words[5])
            else : self.capture_time = 600
            if len(words) > 6 : self.flag_team = words[6]
            else : self.flag_team = "bear"
            if len(words) > 7 : self.flag_height = int(words[7])
            else : self.flag_height = 0
        if self.name.startswith("training_dummy") :
            self.max_health = 0
            self.health = self.max_health
            self.collide_type = "dummy"

    def display(self):
        #if self.screen_pos[0] + self.rect.width >= 0 and self.screen_pos[0] <= screen_def[0] and self.screen_pos[1] + self.rect.height >= 0 and self.screen_pos[1] <= screen_def[1]:
        common.screen.blit(self.image, self.screen_pos)
        if self.is_breakable:
            if self.health != self.max_health :
                if self.name.startswith("gate") :
                    self.health_bar = self.prepare_bar(width=60)
                    common.screen.blit(self.health_bar, (self.screen_pos[0] - 30 + int(self.rect.width/2), self.screen_pos[1] + 100, 60, 10))
                else :
                    self.health_bar = self.prepare_bar(width=100)
                    common.screen.blit(self.health_bar, (self.screen_pos[0] - 50 + int(self.rect.width / 2), self.screen_pos[1] + 10, 60, 10))

    def modify(self, actions):
        if type(actions)==str : actions = [actions]
        groups = common.sort_groups(groups=("character"), area=(self.get_area()))
        success = False
        for action in actions :
            if action == "repair" :
                if self.name.startswith("bridge"):
                    if self.health != self.max_health:
                        success = True
                        self.health += 1
                    if self.name.startswith("bridge_destroyed"):
                        if self.health >= self.max_health :
                            self.name = "bridge_solid"+self.name[16:]
                            self.update_image("background")
                            success = True
                            for character in groups["characters"] :
                                if pygame.sprite.collide_mask(self, character):
                                    self.name = "bridge_destroyed" + self.name[12:]
                                    self.update_image("background")
                                    success = False
                                    break
                elif self.name.startswith("gate"):
                    if self.health != self.max_health:
                        success = True
                        self.health += 1
                    if self.name.startswith("gate_destroyed"):
                        if self.health >= self.max_health :
                            self.name = "gate_solid" + self.name[14:]
                            self.update_image("background")
                            for character in groups["characters"]:
                                if pygame.sprite.collide_mask(self, character):
                                    self.name = "gate_destroyed" + self.name[10:]
                                    self.update_image("background")
                                    success = False
                                    break
            elif action == "destroy" :
                if self.name.startswith("bridge_solid"):
                    self.name = "bridge_destroyed" + self.name[12:]
                elif self.name.startswith("gate_solid"):
                    self.name = "gate_destroyed" + self.name[10:]
                success = True
                self.update_image("background")
        common.clean_groups(groups)
        return success