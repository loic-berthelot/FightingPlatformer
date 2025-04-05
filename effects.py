import pygame, random, math
import common, items
from objects import Object
pygame.init()

class Effect(Object) :
    def __init__(self, words, force=(0, 0), owner=None):
        super().__init__(words)
        self.object_type = "effect"
        self.name = words[0]
        self.org_image = common.get_image("resources/effects/"+self.name+".png")
        self.image = self.org_image
        self.rect = self.image.get_rect()
        self.update_image("effects")
        self.rect.x = int(words[1])
        self.rect.y = int(words[2])
        self.screen_pos = [0, 0]
        self.is_visible = True
        self.lifetime = -1
        self.speed = [force[0], force[1]]
        self.owner = owner
        self.collide_type = "none"
        try: self.org_hitbox = common.get_image("resources/hitboxes/" + self.name + ".png")
        except: self.org_hitbox = self.org_image
        if len(words) > 3:
            self.angle = float(words[3])
            if len(words) > 4: self.flip = int(words[4])
        self.image = self.org_image
        self.hitbox = self.org_hitbox
        self.mask = pygame.mask.from_surface(self.hitbox)
        if self.name.startswith("flame") :
            self.lifetime = 15
            self.pos[0] += random.randint(-50, 25)
            self.pos[1] += random.randint(-30, -15)
            self.image = pygame.transform.rotozoom(self.image, random.randint(-30, 30), random.randint(7, 14)/10)
        if self.name == "shock_wave" :
            self.exceptions = []
            self.team = words[5]
            self.pos[0] -= int(self.rect.width/2)
            self.pos[1] -= int(self.rect.height/2)
            self.lifetime = 55
            self.speed = [10*math.cos(math.radians(self.angle)), -10*math.sin(math.radians(self.angle))]
            self.pos[0] += 3*self.speed[0]
            self.pos[1] += 3*self.speed[1]
        if self.name == "stun_star" :
            self.lifetime = 120
            self.angle = words[5]
        if self.name.startswith("campfire") :
            self.fire_power = 0
        if self.name in ["knife", "arrow", "fire_arrow"] :
            self.team = words[5]
            self.flip = 0
        if self.name == "stone" :
            self.team = words[5]
            self.rotate_speed = 3
            self.lifetime = 150
        if self.name == "rope" :
            self.target = None
            self.team = words[5]
            self.lifetime = 100
        if self.name == "pedestal" :
            self.reload_time = 900
        if self.name == "dead_human" :
            self.lifetime = 180
        if self.name.startswith("blood") or self.name.startswith("big_blood") :
            self.pos[0] -= int(self.rect.width/2)
            self.pos[1] -= int(self.rect.height/2)
            self.lifetime = 100
        if self.name.startswith("haste_fire"):
            self.lifetime = 120
        if self.name.startswith("tent"):
            self.team = words[5]
            self.team_size = int(words[6])
            self.max_reload_time = int(words[7])
            self.reload_time = self.max_reload_time
            self.spawn_info = []
            if len(words)>6:
                for i in range(8, len(words), 1) : self.spawn_info += [words[i]]
        if self.name.startswith("mine_exploding") :
            self.team = words[5]
            self.lifetime = 120
        if self.name.startswith("grenade_exploding") :
            self.team = words[5]
            self.lifetime = 100
        if self.name.startswith("explosion"):
            self.lifetime = 10
        if self.name.startswith("fruit_tree"):
            self.max_health = 3
            self.health = self.max_health
            self.max_links_number = 3
            self.links_number = 0
            self.max_reload_time = 250
            self.reload_time = self.max_reload_time
        if self.name.startswith("dead_tree") :
            self.regrow_time = common.tree_regrow_time
        if self.name.startswith("rock"):
            self.is_breakable = True
            self.max_health = 3.49
            self.health = int(self.name[4:])+0.49
            self.reload_time = 600
        if self.name.startswith("platform"):
            self.all_pos = [[int(words[1]), int(words[2])], [int(words[6]), int(words[7])]]
            self.moving_distance = common.distance(self.all_pos[0][0], self.all_pos[0][1], self.all_pos[1][0], self.all_pos[1][1])
            self.speed = [0,0]
            self.acceleration = float(words[5])
            self.collide_type = "platform"
            self.direction = 1
            self.blocked_time = 0
        if self.name.startswith("spikes") :
            self.reload_time = 40
            self.enabled = False
        if self.name.startswith("crate"):
            self.reload_time = 1800
            self.collide_type = "crate"
        if self.name.startswith("tree") or self.name.startswith("fruit_tree"):
            self.collide_type = "tree"
            self.max_health = 3
            self.health = self.max_health
        if self.name == "guillotine_blade" :
            self.blade_pos = self.pos[1]
            self.blade_speed = 0
            self.reload_time = 0
        if self.name == "ai_beacon" :
            if len(words) > 6 : self.power = [float(words[5]), float(words[6])]
            elif len(words) == 6 : self.power = float(words[5])
            else : self.power = 0
        self.update_image("effects")

    def interact(self, game_parameters):
        groups = common.sort_groups(area=(self.get_area(100)))
        self.pos[0] += self.speed[0]
        self.pos[1] += self.speed[1]
        self.update_rect()
        if self.name in ["rope"] : self.stay_in_frame()
        if self.lifetime == 0:
            if self.name.startswith("mine_exploding") or self.name.startswith("grenade_exploding"):
                effect = Effect(["small_particle", self.rect.centerx, self.rect.centery], owner=self.owner)
                if self.name.startswith("mine") :
                    range_max = 200
                    damages = 40
                if self.name.startswith("grenade"):
                    range_max = 120
                    damages = 25
                for angle in range (0, 360, 6) :
                    for length in range(0, range_max+10, 10) :
                        effect.rect.x = self.rect.centerx+length*math.cos(math.radians(angle))
                        effect.rect.y = self.rect.centery+length*math.sin(math.radians(angle))
                        effect.inflict_damages(self.team, {"life": [-damages, "persistent", "ignore_block", "drop", "hurts_owner"], "break": -1})
                        if common.cm_el(common.block_interactions, effect.collide_background()) : break
                for i in range(1, 8, 1) :
                    angle = i/4*math.pi
                    object = Effect(("explosion"+str(i), self.rect.centerx, self.rect.centery), force=(20*math.cos(angle), 20*math.sin(angle)))
                    object.grid_move()
            if self.name.startswith("fruit_unripe"):
                from items import Item
                item = Item(("fruit_red", self.rect.centerx, self.rect.centery))
                item.angle = self.angle
                item.update_image("items")
                item.link = self.owner.id
                item.has_gravity = False
                item.is_shaking = False
                item.grid_move()
            self.remove()
        elif self.lifetime != -1 : self.lifetime -= 1
        if self.lifetime != 0 :
            if "flame" in self.name:
                self.pos[1] -= 0.3
            if self.name == "shock_wave":
                self.inflict_damages(self.team, {"life": [-10, "drop", "ignore_block"], "mine" : ["enable", "disable"]})
                if self.lifetime > 6 :
                    if common.cm_el(common.block_interactions, self.collide_background()) :
                        self.lifetime = 6
            if self.name == "stun_star":
                self.angle += 2
                self.update_image("effects")
            if self.name == "dead_human" :
                self.physic_interaction(0.5 * game_parameters["weight_intensity"], game_parameters["air_density"])
                if common.cm_el(common.block_interactions, self.collide_background()) :
                    self.pos[1] -= self.speed[1]
                    self.speed[1] = 0
                    self.update_rect()
            if self.name.startswith("campfire") :
                if self.fire_power > 0:
                    if self.fire_power > 100 : self.fire_power = 100
                    if common.frame_number % 2 == 0:
                        object = Effect(["flame" + str(random.randint(1, 2)), self.rect.centerx, self.rect.centery])
                        object.grid_move()
                    if common.frame_number % 30 == 0:
                        self.fire_power -= 1
                        for character in groups["characters"]:
                            if 70 > self.distance(character.rect.centerx, character.rect.centery, self.rect.centerx, self.rect.centery):
                                character.manage_health(1)
            if self.name in ["knife", "arrow", "fire_arrow"] :
                if self.speed != [0, 0] :
                    old_angle = self.angle
                    self.angle = math.degrees(common.length_to_angle(self.speed[0], self.speed[1]))
                    if int(old_angle) != int(self.angle) : self.update_image("effects")
                    self.physic_interaction(0.5 * game_parameters["weight_intensity"], game_parameters["air_density"])
                    if self.name == "knife" : results = self.inflict_damages(self.team, {"life" : [-20, "destroy", "shield_stop", "reverse"]})
                    elif self.name == "arrow" : results = self.inflict_damages(self.team, {"life": [-15, "destroy", "shield_stop", "reverse"]})
                    elif self.name == "fire_arrow" : results = self.inflict_damages(self.team, {"life": [-20, "drop", "reverse"]})
                    if "destroy" in results or "stop" in results :
                        self.lifetime = 12
                        self.speed = [0, 0]
                    interaction_types = common.block_interactions.copy()
                    if self.name != "fire_arrow" : interaction_types += ["dummy"]
                    if common.cm_el(interaction_types, self.collide_background()) :
                        self.pos[0] -= self.speed[0]
                        self.pos[1] -= self.speed[1]
                        max_coordinate = max(abs(self.speed[0]), abs(self.speed[1]), 1)
                        collide_speed = [self.speed[0]/max_coordinate, self.speed[1]/max_coordinate]
                        for i in range(int(max_coordinate)) :
                            self.pos[0] += collide_speed[0]
                            self.pos[1] += collide_speed[1]
                            self.update_rect()
                            if common.cm_el(common.block_interactions, self.collide_background()):
                                self.pos[0] += 2*collide_speed[0]
                                self.pos[1] += 2*collide_speed[1]
                                self.update_rect()
                                break
                        self.speed = [0, 0]
                        if self.name == "fire_arrow" : self.lifetime = 0
                        else : self.lifetime = 50
            if self.name == "stone" :
                self.physic_interaction(0.5*game_parameters["weight_intensity"], game_parameters["air_density"])
                if common.cm_el(common.block_interactions, self.collide_background()) :
                    self.rotate_speed = 0
                    self.pos[0] -= self.speed[0]
                    self.pos[1] -= self.speed[1]
                    self.speed = [0, 0]
                if common.norm(self.speed) > 2 :
                    results = self.inflict_damages(self.team, {"life" : [-5, "destroy", "stun"]})
                    self.angle += self.rotate_speed
                    self.update_image("effects")
                    if "destroy" in results :
                        self.remove()
                        self.lifetime = 0
            if self.name == "rope" :
                if 50 < self.lifetime :
                    if "attached" in self.inflict_damages(self.team, {"life" : [-10, "attach", "attach_friends"]}) : self.lifetime = 50
                if self.lifetime < 50 :
                    if self.target :
                        if self.lifetime > 10 :
                            self.target.speed[0] = (self.owner.rect.centerx - self.rect.centerx) / self.lifetime
                            self.target.speed[1] = (self.owner.rect.centery - self.rect.centery) / self.lifetime
                        self.pos[0] = self.target.rect.centerx - self.rect.width/2
                        self.pos[1] = self.target.rect.centery - self.rect.height/2
                    else :
                        self.speed[0] = (self.owner.rect.centerx - self.rect.centerx) / self.lifetime
                        self.speed[1] = (self.owner.rect.centery - self.rect.centery) / self.lifetime
            if self.name == "pedestal" :
                if self.reload_time == 0 :
                    name = random.choice(common.items_pedestal)
                    item = items.Item((name, self.rect.centerx, self.rect.centery-25))
                    item.grid_move()
                    item.link = self.id
                    self.reload_time = -1
                elif self.reload_time == -1 :
                    is_linked = False
                    for item in groups["items"] :
                        if item.link == self.id :
                            is_linked = True
                            break
                    if not is_linked : self.reload_time = 900
                else : self.reload_time -= 1
            if self.name.startswith("fruit_tree") :
                if self.health > 0 :
                    rect = self.image.get_rect()
                    if self.reload_time == 0 :
                        effect = Effect(("fruit_unripe", self.rect.centerx+random.uniform(-0.3, 0.3)*rect.width, self.rect.centery+random.uniform(-0.4, 0)*rect.height))
                        effect.angle = random.uniform(-30, 30)
                        effect.update_image("effects")
                        effect.grid_move()
                        effect.owner = self
                        effect.lifetime = 300
                        self.reload_time = -1
                    elif self.reload_time == -1 :
                        self.links_number = 0
                        for item in groups["items"] :
                            if item.link == self.id : self.links_number += 1
                        for effect in groups["effects"] :
                            if effect.owner == self : self.links_number += 1
                        if self.links_number < self.max_links_number : self.reload_time = self.max_reload_time
                    else :
                        self.reload_time -= 1
            if self.name.startswith("dead_tree") or self.name.startswith("dead_fruit_tree"):
                if self.regrow_time == 0 :
                    old_rect = self.image.get_rect()
                    self.name = self.name[5:]
                    self.update_image("effects")
                    new_rect = self.image.get_rect()
                    self.pos[1] += old_rect.height - new_rect.height
                    if self.flip % 2 >= 1: self.pos[0] += old_rect.width - new_rect.width
                    self.update_rect()
                    self.health = 3
                else : self.regrow_time -= 1
            if self.name.startswith("fruit_unripe") :
                if self.owner.name.startswith("dead") : self.remove()
            if self.name.startswith("haste_fire") :
                self.pos = [self.owner.rect.centerx, self.owner.rect.centery+12]
                if self.flip == 0 : self.pos[0] += self.owner.rect.width/2 + 5
                else : self.pos[0] += -self.owner.rect.width/2-self.rect.width-5
                if self.lifetime%10 == 0 :
                    self.name = "haste_fire"+str((int(self.name[10:])+1)%3)
                    self.image = common.get_image("resources/effects/"+self.name+".png")
                    self.update_image("effects")
                self.stay_in_frame(goto="border")
            if self.name.startswith("explosion"):
                if common.cm_el(common.block_interactions, self.collide_background()) :self.remove()
            if self.name.startswith("spikes"):
                if self.reload_time > 0 : self.reload_time -= 1
                if int(self.name[6:]) > 0 or self.enabled :
                    self.enabled = False
                    if self.reload_time == 0:
                        self.reload_time = 60
                        last_rect = self.rect.copy()
                        self.name = "spikes"+str((int(self.name[6:])-1)%3)
                        self.update_image("effects")
                        self.update_rect()
                        new_rect = self.rect.copy()
                        if not self.flip%4 >= 2 : self.pos[0] += last_rect.width - new_rect.width
                        if not self.flip%2 >= 1 : self.pos[1] += last_rect.height - new_rect.height
                        self.update_rect()
                        if int(self.name[6:]) > 1 :
                            self.exceptions = []
                            self.inflict_damages(None, {"life" : [-1000, "persistent", "ignore_block"]})
            if self.name == "guillotine_blade":
                self.pos[1] += self.blade_speed
                self.update_rect()
                if self.reload_time > 0 :
                    self.reload_time -= 1
                else :
                    if self.blade_speed >= 0 :
                        self.blade_speed += 0.3
                        self.inflict_damages(None, {"life" : [-1000, "persistent", "ignore_block"]})
                        if self.pos[1]-self.blade_pos > 105 :
                            self.blade_speed = -1.5
                            self.exceptions = []
                    else :
                        if self.pos[1] < self.blade_pos :
                            self.blade_speed = 0
                            self.reload_time = 40
            if self.name.startswith("flag"):
                total_people = 0
                total_influence = 0
                for team in self.owner.teams_influence.keys() :
                    total_people += 1
                    if team == self.owner.flag_team : total_influence += 1
                    else : total_influence -= 1
                self.owner.flag_height += 200/self.owner.capture_time*total_influence
                if self.owner.flag_height < 0 :
                    self.owner.flag_height = 0
                    for team in self.owner.teams_influence.keys():
                        if self.owner.teams_influence[team] > total_people/2 :
                            self.owner.flag_team = team
                            break
                if self.owner.flag_height >= 200 :
                    self.owner.flag_height = 200
                    if self.owner.flag_team in common.flags_raised.keys() :
                        common.flags_raised[self.owner.flag_team] += 1
                self.owner.teams_influence = {}
                self.pos[1] = self.owner.rect.y+self.owner.rect.height+10 - self.owner.flag_height
                self.update_rect()
                if self.owner.flag_height < 30 : self.is_visible = False
                else : self.is_visible = True
                if self.name != "flag_"+self.owner.flag_team :
                    self.name = "flag_"+self.owner.flag_team
                    self.update_image("effects")
            if self.name.startswith("blood") or self.name.startswith("big_blood"):
                if self.name.startswith("blood") :  nb_pictures = 7
                else : nb_pictures = 11
                self.physic_interaction(0.5 * game_parameters["weight_intensity"], game_parameters["air_density"])
                if common.cm_el(common.block_interactions, self.collide_background()) :
                    self.rotate_speed = 0
                    self.speed = [0, 0]
                    if self.lifetime > 10 : self.lifetime = 10
                elif self.name != "blood"+str(int(common.frame_number/5)%nb_pictures):
                    self.name = "blood"+str(int(common.frame_number/5)%nb_pictures)
                    self.update_image("effects")
            if self.name.startswith("tent") :
                if self.reload_time == 0 :
                    group_characters = common.sort_groups(groups=("character"))
                    team_number = 0
                    for character in group_characters["characters"]:
                        if self.team == character.team : team_number += 1
                    common.clean_groups(group_characters)
                    if self.team_size > team_number :
                        self.reload_time = self.max_reload_time
                        from character import Character
                        object = Character(["human", self.rect.centerx, self.rect.centery, "ai", self.team]+self.spawn_info)
                        object.grid_move()
                else :
                    self.reload_time -= 1
            if self.name.startswith("mine_exploding") or self.name.startswith("grenade_exploding"):
                if common.frame_number%4==0 : self.pos[0] -= 3
                elif common.frame_number%4==2 : self.pos[0] += 3
                self.physic_interaction(0.5 * game_parameters["weight_intensity"], game_parameters["air_density"])
                if common.cm_el(common.block_interactions, self.collide_background()) :
                    self.pos[0] -= self.speed[0]
                    self.pos[1] -= self.speed[1]
                    self.speed = [0, 0]
            if self.name.startswith("rock"):
                self.reload_time -= 1
                if self.reload_time == 0 :
                    self.manage_health(1)
                    self.reload_time = 600
                if int(self.health) != int(self.name[4:]) :
                    if int(self.health) < int(self.name[4:]) :
                        item = items.Item(("stone", self.rect.centerx, self.rect.centery))
                        item.grid_move()
                    old_rect = self.rect.copy()
                    self.name = "rock"+str(int(self.health))
                    self.update_image("effects")
                    self.pos[0] += old_rect.width-self.rect.width
                    self.pos[1] += old_rect.height - self.rect.height
                    self.update_rect()
            if self.name.startswith("broken_crate") :
                self.reload_time -= 1
                if self.reload_time == 0 :
                    self.reload_time = 1800
                    self.name = self.name[7:]
                    self.update_image("effects")
            if self.name.startswith("platform"): #self.speed already added to self.pos above
                self.pos[1] += -1
                self.update_rect()
                group_moving = common.merge_groups(common.sort_groups(groups=("character", "effect"), area=self.get_area()))
                for object in group_moving :
                    if not pygame.sprite.collide_mask(self, object) or not object.name in common.platform_interactions : group_moving.remove(object)
                self.pos[1] += 1
                self.update_rect()
                for object in common.merge_groups(common.sort_groups(groups=("character", "effect"), area=self.get_area())) :
                    if object.name in common.platform_interactions :
                        if pygame.sprite.collide_mask(self, object) and not object in group_moving : group_moving.add(object)
                self.pos[0] -= self.speed[0]
                self.pos[1] -= self.speed[1]+1
                self.update_rect()
                for object in common.merge_groups(common.sort_groups(groups=("character", "effect"), area=self.get_area())):
                    if object.name in common.platform_interactions :
                        if pygame.sprite.collide_mask(self, object) and not object in group_moving: group_moving.add(object)
                self.pos[0] += self.speed[0]
                self.pos[1] += self.speed[1]+1
                self.update_rect()
                blocked = False
                for object in group_moving :
                    if object != self :
                        object.pos[0] += self.speed[0]
                        object.pos[1] += self.speed[1]
                        object.update_rect()
                        if "block" in object.collide_background() or not common.rect_in_map(object.rect):
                            object.pos[0] -= self.speed[0]
                            object.pos[1] -= self.speed[1]
                            object.update_rect()
                            self.pos[0] -= 2*self.speed[0]
                            self.pos[1] -= 2*self.speed[1]
                            self.speed = [0, 0]
                            blocked = True
                            break
                if blocked :
                    self.blocked_time += 1
                    if self.blocked_time >= 5 :
                        self.blocked_time = 0
                        self.direction *= -1
                        self.speed = [0, 0]
                else :
                    self.blocked_time -= 0.5
                    if self.blocked_time < 0 : self.blocked_time = 0
                self.update_rect()
                common.clean_groups(group_moving)
                def outside_way(point1, point2, pos) :
                    if (pos[0]>point1[0] and pos[0]>point2[0]) or (pos[0]<point1[0] and pos[0]<point2[0]) or (pos[1]>point1[1] and pos[1]>point2[1]) or (pos[1]<point1[1] and pos[1]<point2[1]) : return True
                    else : return False
                if outside_way(self.all_pos[0], self.all_pos[1], self.pos) :
                    if self.direction == -1 :
                        self.pos[0] = self.all_pos[0][0]
                        self.pos[1] = self.all_pos[0][1]
                    elif self.direction == 1 :
                        self.pos[0] = self.all_pos[1][0]
                        self.pos[1] = self.all_pos[1][1]
                    self.direction *= -1
                    self.speed = [0, 0]
                self.speed[0] += (self.all_pos[1][0] - self.all_pos[0][0]) / self.moving_distance * self.acceleration * self.direction
                self.speed[1] += (self.all_pos[1][1] - self.all_pos[0][1]) / self.moving_distance * self.acceleration * self.direction
                self.speed[0] *= 0.95
                self.speed[1] *= 0.95
        common.clean_groups(groups)

    def display(self):
        #if self.screen_pos[0] + self.rect.width >= 0 and self.screen_pos[0] <= screen_def[0] and self.screen_pos[1] + self.rect.height >= 0 and self.screen_pos[1] <= screen_def[1]:
        if not self.name in ["ai_beacon"] : common.screen.blit(self.image, self.screen_pos)
        if self.name.startswith("mine_exploding"): pygame.draw.circle(common.screen, (200, 20, 20), (self.screen_pos[0]+self.rect.width/2, self.screen_pos[1]+self.rect.height/2), 200, 2)
        if self.name.startswith("grenade_exploding"): pygame.draw.circle(common.screen, (200, 20, 20), (self.screen_pos[0] + self.rect.width / 2, self.screen_pos[1] + self.rect.height / 2), 120, 2)
        if self.name == "rope" : pygame.draw.line(common.screen, (150, 50, 0), (self.owner.screen_pos[0]+self.owner.rect.width/2, self.owner.screen_pos[1]+self.owner.rect.height/2), (self.screen_pos[0]+self.rect.width/2, self.screen_pos[1]+self.rect.height/2), 2)
        if self.name == "guillotine_blade": pygame.draw.line(common.screen, (170,110,20), (self.screen_pos[0] + self.rect.width/2, self.screen_pos[1]-self.pos[1]+self.blade_pos), (self.screen_pos[0] + self.rect.width/2, self.screen_pos[1]), 2)
        #if self.name == "ai_beacon" : screen.blit(common.write(self.power), (self.screen_pos[0], self.screen_pos[1]-20))