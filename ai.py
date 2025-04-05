import pygame, random, math
import common

class AI(pygame.sprite.Sprite):
    def __init__(self, controls):
        super().__init__()
        self.goals = []
        self.controls = controls.copy()
        self.center_screen = [common.screen_def[0] / 2 / common.screen_def[0], (common.screen_def[1] - 200) / 2 / common.screen_def[1]]
        self.mouse_pos = [0.5, 0.5]
        self.hitbox = pygame.image.load("resources/hitboxes/ai.png")
        self.rect = self.hitbox.get_rect()
        self.mask = pygame.mask.from_surface(self.hitbox)
        self.pos = [0, 0.5]
        self.shift = [0, 0]
        self.target_time = 0
        self.target_type = None
        for key in self.controls.keys() : self.controls[key] = False

    def get_area(self, radius=0):
        area = []
        area += [math.floor((self.rect.x-radius) / 100)]
        area += [math.ceil((self.rect.x + self.rect.width + radius) / 100)]
        area += [math.floor((self.rect.y-radius)/ 100)]
        area += [math.ceil((self.rect.y + self.rect.height + radius) / 100)]
        return area

    def collide_background(self):
        collisions = []
        groups = common.sort_groups(area=self.get_area())
        for background in groups["background"] :
            if ((self.rect.x <= background.rect.x and self.rect.x+self.rect.width >= background.rect.x) or (self.rect.x > background.rect.x and self.rect.x <= background.rect.x+background.rect.width)) and ((self.rect.y <= background.rect.y and self.rect.y+self.rect.height >= background.rect.y) or (self.rect.y > background.rect.y and self.rect.y <= background.rect.y+background.rect.height)) :
                if pygame.sprite.collide_mask(self, background):
                    if background.collide_type != "none" and not background.collide_type in collisions : collisions += [background.collide_type]
        common.clean_groups(groups)
        return collisions

    def aim(self, x, y, strenght):
        dist = math.sqrt(x*x + y*y)
        if dist == 0 : dist = 0.0001
        self.mouse_pos[0]= self.center_screen[0]+x/dist*strenght
        self.mouse_pos[1]= self.center_screen[1]+y/dist*strenght

    def check_obstacles(self, point1, point2):
        obstacles = False
        self.rect.centerx = point1[0]
        self.rect.centery = point1[1]
        dist = common.distance(point1[0], point1[1], point2[0], point2[1])
        dx = point2[0]-point1[0]
        dy = point2[1]-point1[1]
        for i in range(int(dist/10)):
            self.rect.centerx += 10*dx / dist
            self.rect.centery += 10*dy / dist
            if "block" in self.collide_background() :
                obstacles = True
                break
        return obstacles

    def rand(self, value):
        if random.randint(0, int(value/self.frequency)) == 0 : return True
        else : return False

    def local_collisions(self, pos_x, pos_y):
        self.rect.centerx = pos_x
        self.rect.centery = pos_y
        return self.collide_background()

    def reset_controls(self, hands=True, legs=True):
        if hands :
            for action in ["ultimate", "hit", "shield"] : self.controls[action] = False
        if legs :
            for action in ["move left", "move right", "jump", "crouch"] : self.controls[action] = False

    def select_moves(self, moves):
        if type(moves) == str : moves = [moves]
        for move in moves :
            self.controls[move] = True

    def unselect_moves(self, moves):
        if type(moves) == str : moves = [moves]
        for move in moves :
            self.controls[move] = False

    def return_none(self):
        return self.controls, self.mouse_pos

    def return_controls(self, mycharacter):
        self.frequency = mycharacter.ai_delay
        if mycharacter.weapon.name in ["bow"] : weapon_type = "ranged"
        else : weapon_type = "melee"
        self.target_time -= self.frequency
        if self.target_time < 0 : self.target_time = 0

        """ FIRST FRAME """

        if not hasattr(self, "target_pos"): self.target_pos = [mycharacter.rect.centerx, mycharacter.rect.centery]
        if not hasattr(self, "special_places") : #it means that self has not ai_beacons property too
            self.special_places = {}
            self.ai_beacons = []
            for element in ["flags", "guillotines", "spikes"] : self.special_places[element] = []
            group_traps = common.sort_groups(groups=("effect", "background"))
            for effect in group_traps["effects"]:
                if effect.name.startswith("spikes") : self.special_places["spikes"] += [[effect.rect.centerx, effect.rect.centery]]
                if effect.name == "ai_beacon":
                    if type(effect.power) == list : self.ai_beacons += [[effect.rect.centerx, effect.rect.centery, effect.power.copy()]]
                    else : self.ai_beacons += [[effect.rect.centerx, effect.rect.centery, effect.power]]
            for background in group_traps["background"]:
                if background.name == "guillotine" : self.special_places["guillotines"] += [[background.rect.centerx, background.rect.centery]]
                if background.name.startswith("flag") : self.special_places["flags"] += [background]
            common.clean_groups(group_traps)

        """ DEFINE GROUPS """

        trap_near = False
        for place in self.special_places["spikes"] :
            if common.distance(place[0], place[1], mycharacter.rect.centerx, mycharacter.rect.centery) < 150 :
                trap_near = True
                break
        if not trap_near :
            for place in self.special_places["guillotines"] :
                if common.distance(place[0], place[1], mycharacter.rect.centerx, mycharacter.rect.centery) < 150 : trap_near = True
        nearly_spikes = False
        nearly_guillotine = None
        if trap_near :
            group_traps = common.sort_groups(groups=("effect"), area=self.get_area(100))
            for effect in group_traps["effects"]:
                if effect.name.startswith("spikes"):
                    nearly_spikes = True
                if effect.name == "guillotine_blade":
                    if effect.blade_speed >= 0:  # or (effect.reload_time>0 and effect.reload_time<60):
                        nearly_guillotine = [effect.rect.centerx, effect.rect.centery]
                        break
            common.clean_groups(group_traps)
        nearly_flag = None
        if mycharacter.team in common.flag_teams :
            for flag in self.special_places["flags"] :
                if flag.flag_team != mycharacter.team or flag.flag_height < 200 :
                    if common.distance(flag.rect.centerx, flag.rect.centery, mycharacter.rect.centerx, mycharacter.rect.centery) < 300 :
                        nearly_flag = [flag.rect.centerx, flag.rect.centery]
        nearest_enemy = None
        dist_enemy = None
        groups = common.sort_groups(groups=("character", "item"))
        for character in groups["characters"] :
            if character.team != mycharacter.team and character.is_alive:
                if not nearest_enemy :
                    nearest_enemy = character
                    dist_enemy = common.distance(mycharacter.rect.centerx, mycharacter.rect.centery, character.rect.centerx, character.rect.centery)
                else :
                    d = common.distance(mycharacter.rect.centerx, mycharacter.rect.centery, character.rect.centerx, character.rect.centery)
                    if d <dist_enemy :
                        nearest_enemy = character
                        dist_enemy = d
        nearest_item = None
        dist_item = None
        for item in groups["items"]:
            if not nearest_item :
                nearest_item = item
                dist_item = common.distance(mycharacter.rect.centerx, mycharacter.rect.centery, item.rect.centerx, item.rect.centery)
            else:
                d = common.distance(mycharacter.rect.centerx, mycharacter.rect.centery, item.rect.centerx, item.rect.centery)
                if d < dist_item:
                    nearest_item = item
                    dist_item = d
        common.clean_groups(groups)

        """ MOVEMENT OF ARMS """

        if nearest_enemy :
            self.aim(nearest_enemy.rect.centerx-mycharacter.rect.centerx, nearest_enemy.rect.centery - mycharacter.rect.centery, 0.4)
            if self.rand(10) :
                if mycharacter.weapon.name in ["hammer"] :
                    groups = common.sort_groups(groups=["background"], area=mycharacter.get_area(100))
                    for background in groups["background"] :
                        if background.is_breakable :
                            if "solid" in background.name :
                                if common.distance(background.rect.centerx, background.rect.centery, mycharacter.rect.centerx, mycharacter.rect.centery)<100:
                                    if mycharacter.weapon.charge_power == 0 :
                                        self.reset_controls()
                                        self.select_moves("hit")
                                    else :
                                        self.unselect_moves("hit")
                                    self.target_pos = [background.rect.centerx, background.rect.centery]
                                    break
                    common.clean_groups(groups)
                if not self.controls["hit"] and dist_enemy < {"melee" : 100, "ranged" : 500}[weapon_type] and mycharacter.cooldown["hit"] == 0 and nearest_enemy.invulnerability < 15 :
                    if mycharacter.weapon.charge_power == 0:
                        self.reset_controls()
                        self.select_moves("hit")
                    else:
                        self.unselect_moves("hit")
                elif self.controls["hit"] and dist_enemy < {"melee" : 90, "ranged" : 500}[weapon_type] and not nearest_enemy.shield.is_blocking :
                    if dist_enemy < 90 or (weapon_type == "ranged" and not mycharacter.weapon.action and not self.check_obstacles(mycharacter.rect.center, self.target_pos)) :
                        self.unselect_moves("hit")
            if self.rand(15) and dist_enemy < 100 and mycharacter.cooldown["shield"] == 0:
                self.reset_controls(True, False)
                self.select_moves("shield")
            if mycharacter.weapon.name == "axe" :
                if self.rand(15) and dist_enemy < 500 and mycharacter.cooldown["ultimate"] == 0:
                    if not self.check_obstacles(mycharacter.rect.center, nearest_enemy.rect.center) :
                        self.reset_controls(True, False)
                        self.select_moves("ultimate")
            if mycharacter.weapon.name == "bow" :
                if self.rand(15) and dist_enemy < 500 and mycharacter.cooldown["ultimate"] == 0:
                    if not self.check_obstacles(mycharacter.rect.center, nearest_enemy.rect.center) :
                        self.reset_controls(True, False)
                        self.select_moves("ultimate")
            if mycharacter.weapon.name == "hammer" :
                if self.rand(15) and dist_enemy < 100 and mycharacter.cooldown["ultimate"] == 0:
                    if not self.check_obstacles(mycharacter.rect.center, nearest_enemy.rect.center) :
                        self.reset_controls(True, False)
                        self.select_moves("ultimate")
            if mycharacter.weapon.name == "sword" :
                if self.rand(15) and dist_enemy < 100 and mycharacter.cooldown["ultimate"] == 0:
                    if not self.check_obstacles(mycharacter.rect.center, nearest_enemy.rect.center) :
                        self.reset_controls(True, False)
                        self.select_moves("ultimate")
        else :
            self.reset_controls(True, False)

        """ CHOICE OF TARGET """

        if common.point_in_rect(self.target_pos, mycharacter.rect) and self.target_time > 0:
            self.target_time = 0
            if self.target_type == "ai_beacon":
                for i in range(len(self.ai_beacons)):
                    if self.target_pos == [self.ai_beacons[i][0], self.ai_beacons[i][1]]:
                        if type(self.ai_beacons[i][2]) == list:
                            self.ai_beacons[i][2][0] -= 1
                            self.ai_beacons[i][2][1] -= 1
                        else:
                            self.ai_beacons[i][2] -= 1
                        self.target_type = None
                        break
        if self.target_time == 0:
            if self.rand(10) :
                self.target_type = None
                dist_target = None
                highest_power = None
                for target in self.ai_beacons:
                    dist = common.distance(target[0], target[1], mycharacter.rect.centerx, mycharacter.rect.centery)
                    if type(target[2]) == list: power = random.uniform(target[2][0], target[2][1])
                    else : power = target[2]
                    if not self.target_type or power > highest_power or (power == highest_power and dist < dist_target) :
                        if dist < 500 and not self.check_obstacles((target[0], target[1]), mycharacter.rect.center):
                            self.target_type = "ai_beacon"
                            dist_target = dist
                            highest_power = power
                            self.target_pos = [target[0], target[1]]
                            self.target_time = 30 + dist * 0.5
            elif self.rand(20) and mycharacter.team in common.escape_teams :
                groups = common.sort_groups(groups=("background"), area = mycharacter.get_area(800))
                for background in groups["background"] :
                    if background.collide_type == "escape" :
                        if self.rand(25) or not self.check_obstacles(background.rect.center, mycharacter.rect.center) :
                            self.target_pos = [background.rect.centerx, background.rect.centery]
                            self.target_time = abs(mycharacter.rect.centerx - self.target_pos[0])
                            self.target_type = "escape"
                            break
                common.clean_groups(groups)
            elif self.rand(20) and nearly_flag :
                self.target_pos = nearly_flag.copy()
                self.target_time = 350
            elif self.rand(20) and nearest_item :
                if dist_item < 300 :
                    self.target_pos = [nearest_item.rect.centerx, nearest_item.rect.centery]
                    self.target_time = abs(mycharacter.rect.centerx - self.target_pos[0])
                    self.target_type = "item"
            elif self.rand(20) and nearest_enemy and dist_enemy < random.randint(350, 600) :
                if not self.check_obstacles(mycharacter.rect.center, nearest_enemy.rect.center) :
                    self.target_pos = [nearest_enemy.rect.centerx, nearest_enemy.rect.centery]
                    self.target_time = abs(mycharacter.rect.centerx - self.target_pos[0])
                    self.target_type = "enemy"
            elif self.rand(10) :
                if mycharacter.is_onscale : pos = [mycharacter.rect.centerx, mycharacter.rect.centery + random.randint(-450, -300)]
                else : pos = [mycharacter.rect.centerx + random.randint(-400, 400), mycharacter.rect.centery + random.randint(-50, 0)]
                if "scale" in self.local_collisions(pos[0], pos[1]) :
                    self.target_pos = pos.copy()
                    self.target_time = 0.7*common.distance(mycharacter.rect.centerx, mycharacter.rect.centery, self.target_pos[0], self.target_pos[1])
                    self.target_type = "scale"
            elif self.rand(60) :
                if self.rand(40) or common.distance(self.target_pos[0], self.target_pos[1], mycharacter.rect.centerx, mycharacter.rect.centery) < 100 :
                    self.target_pos = [max(0, min(mycharacter.rect.centerx + random.randint(-300, 300), common.border_size[0])), max(0, min(mycharacter.rect.centery + random.randint(-200, 200), common.border_size[1]))]
                    self.target_time = abs(mycharacter.rect.centerx-self.target_pos[0])
                    self.target_type = "nearly_random"

        """ MOVEMENT OF LEGS """

        if self.target_pos[0] < mycharacter.rect.x - mycharacter.rect.width/2 :
            self.reset_controls(False, True)
            self.select_moves("move left")
        elif self.target_pos[0] > mycharacter.rect.x + mycharacter.rect.width/2 :
            self.reset_controls(False, True)
            self.select_moves("move right")
        if mycharacter.is_onscale and "scale" in self.local_collisions(mycharacter.rect.centerx, mycharacter.rect.centery-20):
            if self.controls["move left"]:
                if not self.local_collisions(mycharacter.rect.centerx-mycharacter.rect.width/2-20, mycharacter.rect.centery):
                    self.unselect_moves(("move left", "move right"))
            if self.controls["move right"]:
                if not self.local_collisions(mycharacter.rect.centerx+mycharacter.rect.width/2+20, mycharacter.rect.centery):
                    self.unselect_moves(("move left", "move right"))
        if mycharacter.cooldown["dash"] == 0 :
            if mycharacter.dash_time[0] > 0 : self.controls["move left"] = False
            if mycharacter.dash_time[1] > 0: self.controls["move right"] = False
        if "scale" in mycharacter.collide_background() or self.rand(100):
            if mycharacter.rect.centery > self.target_pos[1]+15 :
                self.controls["jump"] = True
                self.controls["crouch"] = False
            elif mycharacter.rect.centery < self.target_pos[1]-15:
                self.controls["jump"] = False
                self.controls["crouch"] = True
            else:
                self.controls["jump"] = False
                self.controls["crouch"] = False
        if self.rand(25) and self.local_collisions(mycharacter.rect.centerx + 20 * mycharacter.orientation,mycharacter.rect.y + mycharacter.rect.height - 6):
            self.controls["jump"] = True
            self.controls["crouch"] = False
        if self.rand(50*mycharacter.stamina/mycharacter.max_stamina) and abs(mycharacter.rect.centerx-self.target_pos[0])<80 : self.controls["run"] = True
        if nearly_spikes : self.unselect_moves(("run", "jump"))
        if nearly_guillotine:
            if nearly_guillotine[0] < mycharacter.rect.centerx :
                self.unselect_moves("move left")
                self.select_moves("move right")
            else :
                self.unselect_moves("move right")
                self.select_moves("move left")

        """ COLLECT AND USE ITEMS """

        if nearest_item : self.controls["collect/interact"] = True
        else : self.controls["collect/interact"] = False
        for i in range(4):
            self.controls["item"+str(i+1)] = False
            if mycharacter.items[i] :
                if mycharacter.items[i] :
                    if mycharacter.items_time[i] == 0 :
                        if mycharacter.items[i] == "health_potion" :
                            if mycharacter.health < 50 and self.rand(20+5*mycharacter.health):
                                self.controls["item"+str(i+1)] = True
                        if mycharacter.items[i] == "fruit_red" :
                            if mycharacter.health < 50 and self.rand(20+5*mycharacter.health):
                                self.controls["item"+str(i+1)] = True
                        if mycharacter.items[i] == "haste_potion":
                            if self.rand(2000): self.controls["item" + str(i + 1)] = True
                        if mycharacter.items[i].startswith("weapon") :
                            if self.rand(1500) and mycharacter.items[i] != mycharacter.weapon : self.controls["item" + str(i + 1)] = True
                        if nearest_enemy :
                            if mycharacter.items[i] == "knife" and nearest_enemy.invulnerability < 15 and not nearest_enemy.shield.is_blocking :
                                if self.rand(500) and not self.check_obstacles(mycharacter.rect.center, nearest_enemy.rect.center): self.controls["item"+str(i+1)] = True
                            if mycharacter.items[i] == "grenade" and self.rand(1000) :
                                distance = common.distance(mycharacter.rect.centerx, mycharacter.rect.centery, nearest_enemy.rect.centerx, nearest_enemy.rect.centery)
                                if 200 < distance and distance < 500 :
                                    if not self.check_obstacles(mycharacter.rect.center, nearest_enemy.rect.center): self.controls["item" + str(i + 1)] = True
                            if mycharacter.items[i] == "stone" and nearest_enemy.invulnerability < 20 and not nearest_enemy.shield.is_blocking :
                                if self.rand(300) and not self.check_obstacles(mycharacter.rect.center, nearest_enemy.rect.center) : self.controls["item"+str(i+1)] = True
                            if mycharacter.items[i] == "rope" and nearest_enemy.invulnerability < 20 and not nearest_enemy.shield.is_blocking :
                                if self.rand(300) : self.controls["item"+str(i+1)] = True
                            if mycharacter.items[i] == "mine":
                                if dist_enemy < 50 and self.rand(100):
                                    self.controls["item" + str(i + 1)] = True
                            if mycharacter.items[i] == "clone_potion":
                                if self.rand(2000) : self.controls["item" + str(i + 1)] = True
                            if mycharacter.items[i] == "stamina_potion":
                                if self.rand(300) and mycharacter.stamina < mycharacter.max_stamina/2 and mycharacter.cooldown["ultimate"] > random.randint(-100, 600) : self.controls["item" + str(i + 1)] = True

        """ POSITION OF MOUSE """

        if self.mouse_pos[0] > 1 : self.mouse_pos[0] = 1
        if self.mouse_pos[0] < 0 : self.mouse_pos[0] = 0
        if self.mouse_pos[1] > 1 : self.mouse_pos[1] = 1
        if self.mouse_pos[1] < 0 : self.mouse_pos[1] = 0
        return self.controls, self.mouse_pos