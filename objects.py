import pygame, math
import common
global_id = 1

class Object(pygame.sprite.Sprite):
    def __init__(self, words):
        super().__init__()
        self.pos = [int(words[1]), int(words[2])]
        self.screen_pos = [self.pos[0], self.pos[1]]
        self.give_id()
        self.grid_areas = []
        self.exceptions = []
        self.last_rect = None
        self.angle = 0
        self.flip = 0
        self.owner = None
        self.link = 0
        self.is_breakable = False

    def distance(self, x1, y1, x2, y2):
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def remove(self):
        for i in range(math.floor(self.last_rect.y / 100), math.ceil((self.last_rect.y + self.last_rect.height + 1) / 100)+1, 1):
            for j in range(math.floor(self.last_rect.x / 100), math.ceil((self.last_rect.x + self.last_rect.width + 1) / 100)+1, 1):
                if i >= 0 and j >= 0 and i < len(common.grid_objects) and j < len(common.grid_objects[i]):
                    if self in common.grid_objects[i][j][self.object_type] : common.grid_objects[i][j][self.object_type].remove(self)

    def get_neighbors(self):
        objects = pygame.sprite.Group()
        for i, j in self.grid_areas:
            for group in common.grid_objects[i][j].values() :
                for object in group :
                    if not object in objects :
                        objects.add(object)
                        object.grid_move()
        return objects

    def grid_move(self):
        difference = False
        new_areas = (math.floor(self.rect.x / 100), math.ceil((self.rect.x + self.rect.width+1) / 100), math.floor(self.rect.y / 100), math.ceil((self.rect.y + self.rect.height+1) / 100))
        if self.last_rect != None :
            old_areas = (math.floor(self.last_rect.x / 100), math.ceil((self.last_rect.x + self.last_rect.width+1) / 100), math.floor(self.last_rect.y / 100), math.ceil((self.last_rect.y + self.last_rect.height+1) / 100))
            if old_areas != new_areas :
                difference = True
                for i in range(old_areas[2], old_areas[3]+1, 1):
                    for j in range(old_areas[0], old_areas[1]+1, 1):
                        if i >= 0 and j >= 0 and i < len(common.grid_objects) and j < len(common.grid_objects[i]):
                            if self in common.grid_objects[i][j][self.object_type] : common.grid_objects[i][j][self.object_type].remove(self)
        if difference or self.last_rect == None:
            self.last_rect = self.rect.copy()
            self.grid_areas = []
            for i in range(new_areas[2], new_areas[3]+1, 1):
                for j in range(new_areas[0], new_areas[1]+1, 1):
                    if i >= 0 and j >= 0 and i < len(common.grid_objects) and j < len(common.grid_objects[i]):
                        if not self in common.grid_objects[i][j][self.object_type]:
                            common.grid_objects[i][j][self.object_type] += [self]
                            self.grid_areas += [(i, j)]

    def display(self):
        #if self.screen_pos[0] + self.rect.width >= 0 and self.screen_pos[0] <= screen_def[0] and self.screen_pos[1] + self.rect.height >= 0 and self.screen_pos[1] <= screen_def[1]:
        common.screen.blit(self.image, self.screen_pos)

    def update_image(self, directory):
        self.image = common.get_image("resources/"+directory+"/" + self.name + ".png")
        try : self.hitbox = common.get_image("resources/hitboxes/" + self.name + ".png")
        except : self.hitbox = common.get_image("resources/"+directory+"/" + self.name + ".png")
        if self.flip != 0 :
            self.image = pygame.transform.flip(self.image.copy(), self.flip % 2 >= 1, self.flip % 4 >= 2)
            self.hitbox = pygame.transform.flip(self.hitbox.copy(), self.flip % 2 >= 1, self.flip % 4 >= 2)
        if self.angle != 0 :
            self.image = pygame.transform.rotozoom(self.image.copy(), self.angle, 1)
            self.hitbox = pygame.transform.rotozoom(self.hitbox.copy(), self.angle, 1)
        self.mask = pygame.mask.from_surface(self.hitbox)
        rect = self.hitbox.get_rect()
        self.rect.width = rect.width
        self.rect.height = rect.height

    def update_rect(self, pos=None):
        if pos : self.pos = pos
        rect = self.image.get_rect()
        self.rect.width = rect.width
        self.rect.height = rect.height
        self.rect.x = int(self.pos[0])
        self.rect.y = int(self.pos[1])
        self.screen_pos[0] = int(self.pos[0] - common.camera_x)
        self.screen_pos[1] = int(self.pos[1] - common.camera_y)

    def prepare_bar(self, width=80, height=8, back_color = (150, 0, 0), front_color=(0, 150, 0)):
        back_bar = pygame.Surface((width, height))
        back_bar.fill(back_color)
        front_bar = pygame.Surface((int(width * self.health / self.max_health), height))
        front_bar.fill(front_color)
        back_bar.blit(front_bar, (0, 0, int(width * self.health / self.max_health), height))
        pygame.draw.rect(back_bar, (0, 0, 0), (0, 0, width, height), 1)
        return back_bar

    def get_area(self, radius=0):
        area = []
        area += [math.floor((self.rect.x-radius) / 100)]
        area += [math.ceil((self.rect.x + self.rect.width + radius) / 100)]
        area += [math.floor((self.rect.y-radius)/ 100)]
        area += [math.ceil((self.rect.y + self.rect.height + radius) / 100)]
        return area

    def collide_background(self):
        collisions = []
        groups = common.sort_groups(groups=["background", "effect"], area=self.get_area())
        for background in groups["background"] :
            if ((self.rect.x <= background.rect.x and self.rect.x+self.rect.width >= background.rect.x) or (self.rect.x > background.rect.x and self.rect.x <= background.rect.x+background.rect.width)) and ((self.rect.y <= background.rect.y and self.rect.y+self.rect.height >= background.rect.y) or (self.rect.y > background.rect.y and self.rect.y <= background.rect.y+background.rect.height)) :
                if pygame.sprite.collide_mask(self, background):
                    if background.collide_type != "none" and not background.collide_type in collisions : collisions += [background.collide_type]
        for effect in groups["effects"]:
            if ((self.rect.x <= effect.rect.x and self.rect.x + self.rect.width >= effect.rect.x) or (self.rect.x > effect.rect.x and self.rect.x <= effect.rect.x + effect.rect.width)) and ((self.rect.y <= effect.rect.y and self.rect.y + self.rect.height >= effect.rect.y) or (self.rect.y > effect.rect.y and self.rect.y <= effect.rect.y + effect.rect.height)) :
                if pygame.sprite.collide_mask(self, effect):
                    if effect.collide_type != "none" and not effect.collide_type in collisions: collisions += [effect.collide_type]
        common.clean_groups(groups)
        return collisions

    def collide_border(self, border_size):
        if self.pos[0] + self.rect.width > border_size[0]:
            self.pos[0] = border_size[0] - self.rect.width
            self.speed[0] = 0
        elif self.pos[0] < 0:
            self.pos[0] = 0
            self.speed[0] = 0
        if self.pos[1] + self.rect.height > border_size[1]:
            self.pos[1] = border_size[1] - self.rect.height
            self.speed[1] = 0
        elif self.pos[1] < 0:
            self.pos[1] = 0
            self.speed[1] = 0

    def manage_health(self, amount):
        self.health += amount
        if amount > 0 :  common.local_messages += [["+"+str(amount), self.rect.centerx, self.rect.y - 5, 60, "add_health"]]
        elif amount < 0 :  common.local_messages += [[str(amount), self.rect.centerx, self.rect.y - 5, 60, "substract_health"]]
        if self.health > self.max_health :
            self.health = self.max_health
        if self.health <= 0 : self.health = 0

    def manage_stamina(self, amount):
        result = True
        if amount >= 0 :
            self.stamina += amount
            if self.stamina > self.max_stamina : self.stamina = self.max_stamina
        else :
            if self.stamina + amount >= 0:
                self.stamina += amount
            else :
                result = False
        return result

    def physic_interaction(self, weight_intensity, air_density):
        self.speed[1] += weight_intensity
        self.speed[0] *= (1-air_density)
        self.speed[1] *= (1-air_density)

    def create_item(self, name):
        from items import Item
        object = Item([name, self.rect.centerx, self.rect.centery])
        object.grid_move()

    def inflict_damages(self, team=None, types={}):
        groups = common.sort_groups(groups=("character"), area=self.get_area())
        results = []
        if "life" in types.keys() :
            for character in groups["characters"] :
                if self.owner != character.id and character.team == team and "attach_friends" in types["life"]:
                    if pygame.sprite.collide_mask(self, character) :
                        self.target = character
                        common.clean_groups(groups)
                        return ("attached")
                if character.team != team or ("hurts_owner" in types["life"] and self.owner == character.id) :
                    if character.is_alive and not character.id in self.exceptions:
                        if character.invulnerability == 0 or "persistent" in types["life"]:
                            if character.shield.is_blocking and not "ignore_block" in types["life"]  :
                                if pygame.sprite.collide_mask(self, character.shield) :
                                    results += ["blocked"]
                                    if not character.id in self.exceptions : self.exceptions += [character.id]
                                if self.object_type == "weapon" :
                                    if character.weapon.is_hitting and self.orientation != character.orientation:
                                        if pygame.sprite.collide_mask(self, character.weapon) :
                                            character.apply_effects("push_back")
                                            results += ["push_back"]
                            if pygame.sprite.collide_mask(self, character) :
                                if not character.id in self.exceptions : self.exceptions += [character.id]
                                if "reverse" in types["life"] and character.is_kicking :
                                    self.angle += math.pi
                                    self.speed[0] *= -1
                                    self.speed[1] *= -1
                                    self.team = character.team
                                    break
                                elif not "blocked" in results and not "push_back" in results and (character.invulnerability == 0 or "persistent" in types["life"]):
                                    if character.shield.is_blocking and "lateral" in types["life"] and ((self.rect.centerx > character.rect.centerx and character.orientation == 1) or (self.rect.centerx < character.rect.centerx and character.orientation == -1)) :
                                        results += ["blocked"]
                                    else :
                                        if ("roll" in types["life"] and character.stance == "rolling") or ("kick" in types["life"] and character.is_kicking) :
                                            character.apply_effects("fall")
                                            self.apply_effects("fall")
                                        elif not ("bash" in types["life"] and character.stance == "rolling" ) :
                                            character.manage_health(types["life"][0])
                                        if hasattr(self, "owner") : owner = self.owner
                                        else : owner = self
                                        while(hasattr(owner, "owner")):
                                            if owner.owner : owner = owner.owner
                                            else : break
                                        if hasattr(owner, "id") : owner = owner.id
                                        character.killer_id = owner
                                        if character.health == 0 and self.owner != character.id : results += ["kill", "destroy"]
                                        from effects import Effect
                                        effect = Effect(("blood0", character.rect.centerx, character.rect.centery-25))
                                        effect.grid_move()
                                        if "push" in types["life"] : character.speed[0] += self.orientation*10
                                        if "push_high" in types["life"]: character.speed[0] += self.orientation*20
                                        if "drop" in types["life"] : character.apply_effects("fall")
                                        if "stun" in types["life"] : character.apply_effects("stun")
                                        if "attach" in types["life"] :
                                            self.target = character
                                            common.clean_groups(groups)
                                            return("attached")
                                if "destroy" in types["life"] : results += ["destroy"]
        if "shield_stop" in types["life"] and "blocked" in results : results += ["stop"]
        common.clean_groups(groups)
        groups = common.sort_groups(groups=("effect"), area=self.get_area())
        for effect in groups["effects"] :
            if not effect.id in self.exceptions:
                if (effect.name.startswith("tree") or effect.name.startswith("fruit_tree")) and "tree" in types.keys() :
                    if pygame.sprite.collide_mask(self, effect) :
                        effect.manage_health(-1)
                        if effect.health == 0 :
                            if effect.name.startswith("fruit_tree") :
                                group_fruits = common.sort_groups(groups=("item"), area=self.get_area())
                                for item in group_fruits["items"]:
                                    if item.name.startswith("fruit") :
                                        if item.link == effect.id : item.has_gravity = True
                                common.clean_groups(group_fruits)
                            old_rect = effect.image.get_rect()
                            effect.name = "dead_"+effect.name
                            effect.update_image("effects")
                            new_rect = effect.image.get_rect()
                            effect.pos[1] += old_rect.height-new_rect.height
                            if effect.flip%2 >= 1 : effect.pos[0] += old_rect.width - new_rect.width
                            effect.update_rect()
                            effect.regrow_time = common.tree_regrow_time
                            self.create_items(("wood", "wood", "wood"), (effect.rect.centerx, effect.rect.centery))
                        self.exceptions += [effect.id]
        common.clean_groups(groups)
        if "break" in types.keys():
            groups = common.sort_groups(groups=("background", "effect"), area=self.get_area())
            for background in groups["background"] :
                if background.is_breakable and not background.id in self.exceptions:
                    if pygame.sprite.collide_mask(self, background):
                        background.manage_health(types["break"])
                        if background.health == 0:
                            background.modify("destroy")
                        self.exceptions += [background.id]
            for effect in groups["effects"]:
                if effect.is_breakable and not effect.id in self.exceptions:
                    if pygame.sprite.collide_mask(self, effect):
                        effect.manage_health(types["break"])
                        self.exceptions += [effect.id]
            common.clean_groups(groups)
        if "mine" in types.keys() :
            group_items = common.sort_groups(groups=("items"), area=self.get_area())
            for item in group_items["items"]:
                if item.name == "mine" and "enable" in types["mine"] and not item.id in self.exceptions :
                    if pygame.sprite.collide_mask(self, item):
                        from effects import Effect
                        object = Effect(["mine_exploding1", item.rect.x, item.rect.y, 0, 0, self.team], owner=self.owner)
                        object.grid_move()
                        object.id = item.id
                        self.exceptions +=[object.id]
                        item.remove()
            common.clean_groups(group_items)
            group_effects = common.sort_groups(groups=("effects"), area=self.get_area())
            for effect in group_effects["effects"]:
                if effect.name.startswith("mine_exploding") and "disable" in types["mine"] and not effect.id in self.exceptions:
                    if pygame.sprite.collide_mask(self, effect):
                        from items import Item
                        object = Item(["mine", effect.rect.centerx, effect.rect.centery, 0, 0, self.team])
                        object.grid_move()
                        object.id = effect.id
                        self.exceptions += [object.id]
                        effect.remove()
            common.clean_groups(group_effects)
        common.clean_groups(groups)
        group_effects = common.sort_groups(groups=("effects"), area=self.get_area())
        for effect in group_effects["effects"]:
            if effect.name.startswith("crate") :
                if pygame.sprite.collide_mask(self, effect):
                    effect.name = "broken_"+effect.name
                    effect.update_image("effects")
                    from items import Item
                    item = Item(("fruit_red", effect.rect.centerx, effect.rect.centery))
                    item.grid_move()
        common.clean_groups(group_effects)
        group_background = common.sort_groups(groups=("background"), area=self.get_area())
        for background in group_background["background"] :
            if background.name.startswith("training_dummy") :
                if not background.id in self.exceptions :
                    if pygame.sprite.collide_mask(self, background) :
                        background.manage_health(types["life"][0])
                        self.exceptions += [background.id]
        common.clean_groups(group_background)

        return results

    def enable_spikes(self):
        group_effects = common.sort_groups(groups=("effect"), area=self.get_area())
        for effect in group_effects["effects"] :
            if effect.name.startswith("spikes"):
                if pygame.sprite.collide_mask(effect, self) : effect.enabled = True
        common.clean_groups(group_effects)

    def give_id(self):
        global global_id
        self.id = global_id
        global_id += 1

    def create_items(self, item_list, pos):
        from items import Item
        length = len(item_list)
        for i in range(length) :
            new_item = Item((item_list[i], pos[0]+i*10-length*5, pos[1]))
            new_item.grid_move()

    def stay_in_frame(self, goto="last"):
        if not common.rect_in_map(self.rect, self.pos):
            if goto=="border" :
                if self.pos[0]<=0 : self.pos[0] = 1
                if self.pos[1]<=0 : self.pos[1] = 1
                if self.pos[0] + self.rect.width >= common.border_size[0] : self.pos[0] = common.border_size[0] - self.rect.width-1
                if self.pos[1] + self.rect.height >= common.border_size[1] : self.pos[1] = common.border_size[1] - self.rect.height-1
            elif goto == "last" :
                self.pos[0] -= self.speed[0]
                self.pos[1] -= self.speed[1]