import pygame, math, os
import common
from character import Character
from background import Background
from items import Item
from effects import Effect

pygame.init()

def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y1 - y2) ** 2)

class Game():
    def __init__(self, map):
        common.grid_objects = []
        self.keysdown = []
        self.controlsdown = common.controls.copy()
        self.mouse_pressed = [False, False, False, False, False]
        self.mouse_roll = 0
        self.background_color = (100, 20, 20)
        self.light_color = (0, 0, 0)
        self.light_intensity = 0
        self.vision_fading = 0
        self.group_objects = pygame.sprite.LayeredUpdates()
        common.screen_def = pygame.display.Info().current_w, pygame.display.Info().current_h
        self.map_name = map
        common.round_ends = {"ace": []}
        common.round_end = 60
        common.escape_teams = []
        common.escape_score = {}
        common.death_vision = "fading"
        common.respawn_time = 180
        common.respawn_times = {}
        common.local_messages = []
        self.mode = "BACKGROUND"
        file = open("maps/" + self.map_name + ".wilds", "r")
        self.load_map(file)
        file.close()
        for i in range(math.ceil(common.border_size[1] / 100)) :
            line = []
            for j in range(math.ceil(common.border_size[0] / 100)) :
                objects = {}
                for type in ("character", "background", "item", "effect"):
                    objects[type] = []
                line += [objects]
            common.grid_objects += [line]
        for object in self.group_objects :
            object.grid_move()
            if object.object_type == "character" :
                if object.control_type == "player" :
                    self.character = object
            pygame.sprite.Sprite.kill(object)
        self.group_objects = pygame.sprite.LayeredUpdates()
        self.zoom = 1
        common.camera_x = 0
        common.camera_y = 0
        self.parameters = {"air_density" : 0.03, "weight_intensity" : 0.4}
        self.weight_intensity = 0.4
        self.font = pygame.font.SysFont("Arial", 12)
        common.frame_number = 0
        common.round_timer = -1
        self.mouse_pos = pygame.mouse.get_pos()
        self.icons = {}
        for filename in os.listdir("resources/icons") : self.icons[filename[:len(filename)-4]] = pygame.image.load("resources/icons/"+filename)
        self.settings_open = False

    def read_text(self, text, mode="all") :
        if mode == "all" :
            words = []
            word = ""
            for letter in text:
                if letter == " ":
                    if len(word) > 0 : words += [word]
                    word = ""
                else:
                    if not letter in ("\n"): word += letter
            if len(word) > 0 : words += [word]
        if mode == "dictionary" :
            words = []
            word = ""
            for letter in text:
                if letter == " " and len(words)==0:
                    if len(word) > 0: words += [word]
                    word = ""
                else:
                    if not letter in ("\n"): word += letter
            if len(word) > 0: words += [word]
        return words

    def load_map(self, file):
        def create_object(words):
            if words[0] in ["MAP", "BACKGROUND", "CHARACTERS", "ITEMS", "EFFECTS", "DESCRIPTION", "VICTORY", "DEFEAT", "ROUND", "TEXT"] :
                self.mode = words[0]
            else :
                if self.mode == "MAP":
                    if words[0] == "background_color" :
                        if len(words) >= 4 :
                            self.background_color = (int(words[1]), int(words[2]), int(words[3]))
                        else :
                            try :
                                image = pygame.image.load("resources/background_color/"+words[1])
                                rect = image.get_rect()
                                if common.adapt_background == "adjust" :
                                    self.background_color = pygame.transform.scale(image, (common.screen_def[0], common.screen_def[1]-200))
                                elif common.adapt_background == "keep_proportions" :
                                    scale = [rect.width/common.screen_def[0], rect.height/(common.screen_def[1]-200)]
                                    if scale[0] < 1 :
                                        scale[1]/=scale[0]
                                        scale[0] = 1
                                    if scale[1] < 1 :
                                        scale[0] /= scale[1]
                                        scale[1] = 1
                                    if scale[0] > 1 and scale[1] > 1:
                                        if scale[0] > scale[1] :
                                            scale[0]/=scale[1]
                                            scale[1] = 1
                                        else :
                                            scale[1]/=scale[0]
                                            scale[0] = 1
                                    self.background_color = pygame.transform.scale(image, (int(common.screen_def[0]*scale[0]), int((common.screen_def[1]-200)*scale[1])))
                                else : self.background_color = image
                                self.background_color = self.background_color.convert()
                            except :
                                pass
                    if words[0] == "adapt_background" : common.adapt_background = words[1]
                    if words[0] == "light_color": self.light_color = (int(words[1]), int(words[2]), int(words[3]))
                    if words[0] == "light_intensity": self.light_intensity = int(words[1])
                    if words[0] == "border_size": common.border_size = (int(words[1]), int(words[2]))
                    if words[0] == "respawn_time":
                        if len(words)>2 :
                            if words[2] == "none":  common.respawn_times[words[1]] = None
                            elif words[2] == "waiting" : common.respawn_times[words[1]] = "waiting"
                            else : common.respawn_times[words[1]] = int(words[2])
                        else :
                            if words[1] == "none" : common.respawn_time = None
                            elif words[1] == "waiting" : common.respawn_time = "waiting"
                            else : common.respawn_time = int(words[1])
                    if words[0] == "round_end" : common.round_end = int(words[1])
                    if words[0] == "escape_teams" :
                        for word in words :
                            if word != "escape_teams" : common.escape_teams += [word]
                            for value in common.escape_teams:
                                common.escape_score[value] = 0
                    if words[0] == "death_vision" :
                        common.death_vision = words[1]
                        if words[1] == "none" : common.death_vision = None
                    if words[0] == "vision_fading" : common.max_vision_fading = int(words[1])
                    if words[0] == "items_lifetime" :  common.items_lifetime = int(words[1])
                    if words[0] == "ai_delay" : common.ai_delay = int(words[1])
                    if words[0] == "flag_teams" :
                        common.flag_teams = []
                        for i in range(1, len(words)) : common.flag_teams += [words[i]]
                        common.flags_raised = {}
                        for team in common.flag_teams : common.flags_raised[team] = 0
                if self.mode == "BACKGROUND" :
                    object = Background(words)
                    self.group_objects.add(object)
                if self.mode == "CHARACTERS" :
                    object = Character(words)
                    self.group_objects.add(object)
                if self.mode == "ITEMS":
                    object = Item(words)
                    self.group_objects.add(object)
                if self.mode == "EFFECTS":
                    object = Effect(words)
                    self.group_objects.add(object)
                if self.mode == "VICTORY" :
                    common.victory_types[words[0]] = words[1]
                    if words[1] == "none" : common.victory_types[words[0]] == None
                    elif words[1] == "true" : common.victory_types[words[0]] = True
                    elif words[1] == "false" : common.victory_types[words[0]] = False
                    else :
                        try : common.victory_types[words[0]] = int(common.victory_types[words[0]])
                        except : pass
                if self.mode == "DEFEAT" :
                    if len(words) == 2 :
                        common.defeat_types[words[0]] = words[1]
                        if words[1] == "none" : common.defeat_types[words[0]] == None
                        else :
                            try : common.defeat_types[words[0]] = int(common.defeat_types[words[0]])
                            except :pass
                    elif words[0] == "teams_escape" : common.defeat_types["teams_escape"][words[1]] = int(words[2])
                if self.mode == "ROUND" :
                    if words[0] == "ace" : common.round_ends["ace"] += [words[1]]
                if self.mode == "TEXT" :
                    common.signposts[words[0]] = words[1]
        common.init()
        for line in file :
            if self.mode == "TEXT" : words = self.read_text(line, mode="dictionary")
            else : words = self.read_text(line)
            if len(words) > 0 :
                if words[0] == "LOOP" :
                    words_end = []
                    for i in range(4, len(words), 1):
                        words_end += [words[i]]
                    for i in range(int(words[1])):
                        if i > 0 :
                            words_end[1] = int(words_end[1])+int(words[2])
                            words_end[2] = int(words_end[2]) + int(words[3])
                        if len(words) > 0 : create_object(words_end)
                else :
                   create_object(words)

    def check_end(self):
        result = None
        if common.defeat_types["my_deaths"] != None :
            if self.character.death_number >= common.defeat_types["my_deaths"] : result = "defeat"
        if common.defeat_types["ace"] != None :
            if self.character.team_deaths >= common.defeat_types["ace"] : result = "defeat"
        for team in common.escape_teams :
            if common.escape_score[team] >= common.defeat_types["teams_escape"][team] : result = "defeat"
        if common.victory_types["my_kills"] != None :
            if self.character.kill_number >= common.victory_types["my_kills"] : result = "victory"
        if common.victory_types["my_escape"] and "escape" in self.character.collide_background() :
            result = "victory"
        if common.victory_types["ace"] != None :
            if self.character.ace_number >= common.victory_types["ace"] : result = "victory"
        if common.defeat_types["flags_raised"]:
            for team in common.flags_raised.keys() :
                if team != self.character.team and common.flags_raised[team] >= common.defeat_types["flags_raised"] : result = "defeat"
        if common.victory_types["flags_raised"] :
            if common.flags_raised[self.character.team] >= common.victory_types["flags_raised"] : result = "victory"
        return result

    def end_round(self):
        groups = common.sort_groups(groups=("character"))
        if common.round_timer == 0 :
            common.round_timer = -1
            for character in groups["characters"]:
                if character.is_alive : character.die(count_kill=False)
                character.respawn()
            common.clean_groups(groups)
            groups = common.sort_groups(groups=("effect", "item"))
            for effect in groups["effects"]:
                if effect.name in common.end_round_remove : effect.remove()
            for item in groups["items"] : item.remove()
        elif common.round_timer > 0 : common.round_timer -= 1
        else :
            teams_ace = {}
            for key in common.round_ends["ace"] :  teams_ace[key] = 0
            for character in groups["characters"] :
                if character.is_alive and character.team in teams_ace.keys() : teams_ace[character.team] += 1
            if 0 in teams_ace.values() : common.round_timer = common.round_end
        common.clean_groups(groups)

    def keydown(self, type, key):
        if type == "button" : self.keysdown += [key]
        else :
            if key >= 4:
                if key % 2 == 1 : self.mouse_roll -= 5
                else : self.mouse_roll += 5
            else : self.mouse_pressed[key-1] = True

    def keyup(self, type, key):
        if type=="button" :
            if key in self.keysdown : self.keysdown.remove(key)
        elif key < 4 : self.mouse_pressed[key - 1] = False

    def manage_rolling(self):
        if self.mouse_roll > 0:
            if self.mouse_roll > 10 : self.mouse_roll = 10
            self.mouse_pressed[3] = False
            self.mouse_pressed[4] = True
            self.mouse_roll -= 1
        elif self.mouse_roll < 0:
            if self.mouse_roll < -10 : self.mouse_roll = -10
            self.mouse_pressed[3] = True
            self.mouse_pressed[4] = False
            self.mouse_roll += 1
        else:
            self.mouse_pressed[3] = False
            self.mouse_pressed[4] = False

    def get_visible_area(self):
        area = []
        area += [math.floor((common.camera_x -10) / 100)]
        area += [math.ceil((common.camera_x + common.screen_def[0] +10) / 100)]
        area += [math.floor((common.camera_y-10)/ 100)]
        if common.interface_type : area += [math.ceil((common.camera_y + common.screen_def[1] - 190) / 100)]
        else : area += [math.ceil((common.camera_y + common.screen_def[1]+10) / 100)]
        return area

    def controls(self, control_keys):
        self.mouse_pos = pygame.mouse.get_pos()
        for key in control_keys.keys() :
            if type(control_keys[key]) == str :
                button = int(control_keys[key][5])-1
                if self.mouse_pressed[button] : self.controlsdown[key] = True
                else : self.controlsdown[key] = False
            else :
                if control_keys[key] in self.keysdown :  self.controlsdown[key] = True
                else:  self.controlsdown[key] = False
        self.character.controls(self.controlsdown, self.mouse_pos, common.screen_def)
        groups = common.sort_groups(groups=("character"))
        for character in groups["characters"] :
            if character != self.character and character.control_type != "clone":
                if character.control_type == "ai" and common.frame_number%character.ai_delay == 0 : ai = character.ai.return_controls(character)
                else : ai = character.ai.return_none()
                controls = ai[0].copy()
                mouse_pos = ai[1].copy()
                mouse_pos[0] = int(mouse_pos[0]*common.screen_def[0])
                mouse_pos[1] = int(mouse_pos[1] * common.screen_def[1])
                character.controls(controls, mouse_pos, common.screen_def)
        common.clean_groups(groups)

    def move_camera(self, pos):
        groups = common.sort_groups(area=self.get_visible_area(), groups=("background"))
        common.camera_x = pos[0]
        common.camera_y = pos[1]
        for background in groups["background"] : background.update_rect()
        common.clean_groups(groups)

    def update_rect(self):
        self.move_camera((int(self.character.pos[0]-common.screen_def[0]/2+self.character.size[0]/2), int(self.character.pos[1]-common.screen_def[1]/2+100+self.character.size[1]/2)))

    def display(self):
        if type(self.background_color) == tuple : common.screen.fill(self.background_color)
        else : common.screen.blit(self.background_color, (0, 0, common.screen_def[0], common.screen_def[1]-200))
        common.frame_number += 1
        groups = common.sort_groups(area=self.get_visible_area())
        for background in groups["background"] : background.display()
        for effect in groups["effects"] :
            if effect.is_visible : effect.display()
        for item in groups["items"] : item.display()
        pygame.draw.rect(common.screen, (255, 255, 255), (-common.camera_x, -common.camera_y, common.border_size[0], common.border_size[1]), 3)
        for character in groups["characters"] :
            if character.is_alive :
                character.update_rect(True, True)
                character.grid_move()
                character.update_image()
                if character != self.character : character.display()
        if self.character.is_alive : self.character.display()
        if self.light_intensity != 0 :
            surface = pygame.Surface(common.screen_def)
            surface.fill(self.light_color)
            surface.set_alpha(self.light_intensity)
            common.screen.blit(surface, (0, 0))
        common.clean_groups(groups)
        text = self.character.get_signpost()
        if text :
            text_image = common.write(text[0], color=(255, 255, 255))
            rect = text_image.get_rect()
            pygame.draw.rect(common.screen, (20, 20, 20), (text[1][0]-rect.width/2-10, text[1][1]-rect.height/2-10, rect.width+20, rect.height+20))
            common.screen.blit(text_image, (text[1][0]-rect.width/2, text[1][1]-rect.height/2))
        lm = common.local_messages
        for i in range(len(lm)) :
            text = None
            lm[i][3] -= 1
            if lm[i][4] == "substract_health" :
                text = common.write(lm[i][0], 20, (150, 0, 0))
                lm[i][2] -= 0.4
            if lm[i][4] == "add_health" :
                text = common.write(lm[i][0], 20, (0, 200, 20))
                lm[i][2] -= 0.4
            if text :
                rect = text.get_rect()
                common.screen.blit(text, (lm[i][1]-common.camera_x-rect.width/2, lm[i][2]-common.camera_y-rect.height/2))
        for message in lm:
            if message[3] <= 0 : lm.remove(message)

    def display_fps(self, clock):
        fps = int(clock.get_fps())
        common.screen.blit(self.font.render(str(fps), 1, (255, 255, 255)), (5, 5))

    def display_interface(self):
        pygame.draw.rect(common.screen, (50, 50, 50), (0, common.screen_def[1]-200, common.screen_def[0], 200), 0)
        pygame.draw.rect(common.screen, (200, 0, 0), (int(common.screen_def[0]/2 - 50), common.screen_def[1]-160, 400,  15), 0)
        pygame.draw.rect(common.screen, (0, 200, 0), (int(common.screen_def[0] / 2 - 50), common.screen_def[1] - 160, int(400*self.character.health/self.character.max_health), 15), 0)
        common.screen.blit(self.font.render(str(int(self.character.health)), 1, (255, 255, 255)), (common.screen_def[0]/2+355, common.screen_def[1]-160))
        pygame.draw.rect(common.screen, (190, 190, 190), (int(common.screen_def[0] / 2 - 50), common.screen_def[1] - 180, 400, 15), 0)
        pygame.draw.rect(common.screen, (0, 165, 240), (int(common.screen_def[0] / 2 - 50), common.screen_def[1] - 180, int(400 * self.character.stamina / self.character.max_stamina), 15), 0)
        common.screen.blit(self.font.render(str(int(self.character.stamina)), 1, (255, 255, 255)), (common.screen_def[0] / 2 + 355, common.screen_def[1] - 180))
        for i in range(4) :
            rect = self.character.items_images[i].get_rect()
            common.screen.blit(self.character.items_images[i], (int(common.screen_def[0] / 2 - 300+i*60 + 25 -int(rect.width/2)), common.screen_def[1]-190 + 3*math.cos((common.frame_number%50)/50*2*3.1415) + 25 -int(rect.height/2)))
            pygame.draw.rect(common.screen, (255, 255, 255), (int(common.screen_def[0] / 2 - 300 + i * 60), common.screen_def[1] - 190, 50, 50), 3)
        shift_x = 0
        for key in self.character.cooldown.keys() :
            common.screen.blit(self.icons[key], (int(common.screen_def[0] / 2 - 300 + shift_x), common.screen_def[1]-100))
            if self.character.cooldown[key] != 0 :
                surface = pygame.Surface((60, 60))
                surface.fill((50, 50, 50))
                surface.set_alpha(150)
                y = 60
                for i in range(int(60*self.character.cooldown[key]/self.character.cooldown_max[key])) :
                    y -= 1
                    half_width = int(abs(math.sqrt(900 - (30 - y)**2)))
                    pygame.draw.line(surface, (255, 255, 255, 0), (30-half_width, y), (30+half_width, y), 1)
                common.screen.blit(surface, (int(common.screen_def[0] / 2 - 300 + shift_x), common.screen_def[1]-100))
            shift_x += 75
        pygame.draw.rect(common.screen, (255, 255, 255), (int(common.screen_def[0] / 2 - 400), common.screen_def[1]-150, 80, 80), 3)
        common.screen.blit(self.icons["weapon_"+self.character.weapon.name], (int(common.screen_def[0] / 2 - 400), common.screen_def[1]-150))

    def display_scoreboard(self):
        pygame.draw.rect(common.screen, (190, 190, 190), (int(common.screen_def[0]/3), 0, int(common.screen_def[0]/3), 100))
        left_height = 10
        right_height = 10
        if common.defeat_types["my_deaths"] != None :
            common.screen.blit(common.write("lives : " + str(common.defeat_types["my_deaths"] - self.character.death_number)), (int(common.screen_def[0] / 3) + 20, left_height))
            left_height += 30
        if common.defeat_types["ace"] != None :
            common.screen.blit(common.write("team lives : " + str(common.defeat_types["ace"] - self.character.team_deaths)), (int(common.screen_def[0] / 3) + 20, right_height))
            left_height += 30
        if len(common.defeat_types["teams_escape"]) > 0 :
            sentence = "If "
            for team in common.defeat_types["teams_escape"] :
                sentence += str(common.defeat_types["teams_escape"][team] - common.escape_score[team]) + " " + team + " or "
            sentence=sentence[:len(sentence)-4]
            sentence +=" pass the door, you lose."
            common.screen.blit(common.write(sentence, size=15),  (int(common.screen_def[0] / 3) + 20, left_height))
            left_height += 30
        if common.defeat_types["flags_raised"] :
            best_team = None
            best_score = 0
            for team in common.flags_raised.keys() :
                if team != self.character.team and (not best_team or common.flags_raised[team] > best_score):
                    best_team = team
                    best_score = common.flags_raised[team]
            common.screen.blit(common.write("Flags captured ("+best_team+") : "+str(best_score)+" / "+str(common.defeat_types["flags_raised"]), size=15), (int(common.screen_def[0] / 3) + 20, left_height))
            left_height += 30
        if common.victory_types["my_kills"] != None :
            text = "kills : "+str(self.character.kill_number)+" / "+str(common.victory_types["my_kills"])
            common.screen.blit(common.write(text), (int(2*common.screen_def[0]/3)-20-6*len(text), right_height))
            right_height += 30
        if common.victory_types["ace"] != None :
            text = "All opponents killed : " + str(self.character.ace_number) + " / " + str(common.victory_types["ace"]) + " times"
            common.screen.blit(common.write(text), (int(2 * common.screen_def[0] / 3) - 20 - 7 * len(text), right_height))
            right_height += 30
        if common.victory_types["my_escape"] :
            common.screen.blit(common.write("Escape of this terrible place to win.", size=15), (int(2 * common.screen_def[0] / 3) -210, right_height))
            right_height += 30
        if common.victory_types["flags_raised"] :
            common.screen.blit(common.write("Flags to capture : "+str(common.flags_raised[self.character.team])+" / "+str(common.victory_types["flags_raised"]), size=15), (int(2 * common.screen_def[0] / 3) -150, right_height))
            right_height += 30

    def display_respawn(self):
        if common.death_vision in ["death"] : self.display()
        elif common.death_vision == "fading" :
            self.display()
            self.vision_fading += 1
            if self.vision_fading > common.max_vision_fading : self.vision_fading = common.max_vision_fading
            radius = math.ceil(common.norm((common.screen_def[0]/2, common.screen_def[1]/2)))
            width = int(self.vision_fading/common.max_vision_fading*radius)
            pygame.draw.circle(common.screen, (0,0,0), (common.screen_def[0]/2, common.screen_def[1]/2), radius, width)
        else : common.screen.fill((0, 0, 0))
        font = pygame.font.SysFont("Arial", 35)
        if self.character.respawn_time:
            if self.character.respawn_time == "waiting" : text = "Waiting..."
            else :
                time = self.character.respawn_time
                if time < 0:time = 0
                time = int(time/60)
                text = "Respawn in "+str(time)
            text_img = font.render(text, 1, (255, 255, 255))
            rect = text_img.get_rect()
            common.screen.blit(text_img, (int(common.screen_def[0]/2-rect.width/2), int(common.screen_def[1]/2-rect.height/2)))

    def interactions(self):
        #common.clean_groups(groups)
        #groups = common.sort_groups()
        for team in common.flags_raised.keys() :
            common.flags_raised[team] = 0
        groups = common.sort_groups()
        #print(groups["effects"])
        #print(common.len_groups(groups))
        for item in groups["items"] :
            item.update_rect(self.weight_intensity, common.border_size)
        #print(common.len_groups(groups))
        common.clean_groups(groups)
        groups = common.sort_groups()
        for character in groups["characters"] :
            if character.is_alive :
                if not character.is_onscale : character.acceleration(0, self.weight_intensity)
                character.resistance(self.parameters["air_density"])
                character.update_pos()
                character.collide_border(common.border_size)
            elif character.respawn_time == 0 : character.respawn(character.respawn_pos, 1)
        print(common.len_groups(groups))
        common.clean_groups(groups)
        groups = common.sort_groups()
        for effect in groups["effects"] :
            effect.interact(self.parameters)
            effect.update_rect()
            effect.grid_move()
        print(common.len_groups(groups))
        common.clean_groups(groups)
        groups = common.sort_groups()
        for background in groups["background"]:
            if hasattr(background, "first_frame") :
                if background.first_frame :
                    background.first_frame = False
                    if background.name == "guillotine" :
                        effect = Effect(("guillotine_blade", background.pos[0], background.pos[1]+8, 0, background.flip))
                        effect.grid_move()
                    if background.name == "flag_pole" :
                        effect = Effect(("flag_bear", background.rect.centerx, background.pos[1] + 8, 0, background.flip), owner=background)
                        effect.grid_move()
        print(common.len_groups(groups))
        common.clean_groups(groups)