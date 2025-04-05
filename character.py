import pygame, math, random
import common
pygame.init()
from objects import Object
from items import Item
from effects import Effect
from ai import AI
from weapons import Weapon
from shields import Shield
from cape import Cape
from feet import Foot

def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y1 - y2) ** 2)

class Character(Object) :
    def __init__(self, words):
        self.species = "human"
        self.stance = "stand"
        self.image = common.get_image("resources/characters/" + self.species + "/images/" + self.stance + ".png")
        self.org_hitbox = common.get_image("resources/characters/" + self.species + "/hitboxes/" + self.stance + ".png")
        self.hitbox = self.org_hitbox
        self.rect = self.hitbox.get_rect()
        super().__init__(words)
        self.control_type = words[3]
        self.lifetime = None
        if self.control_type == "clone" : self.lifetime = 900
        self.owner = self.id
        self.team = words[4]
        self.pos[0] -= int(self.rect.width/2)
        self.pos[1] -= int(self.rect.height/2)
        self.object_type = "character"
        self.name = "character"
        self.last_stance = self.stance
        self.orientation = 1
        self.orientation_locked = False
        self.last_rect = None
        self.size = [self.rect.width, self.rect.height]
        self.screen_pos = [0, 0]
        self.body_shift = [0, 0]
        self.speed = [0, 0]
        self.basic_speed = {"walking" : 0.4, "crawling" : 0.2, "running" : 0.7}
        self.haste_time = 0
        self.jump_power = 10
        self.resistance_power = [3, 1]
        self.is_onground = False
        self.is_onscale = False
        self.step_height = 5
        self.max_health = 80
        self.health = self.max_health
        self.health_regeneration = 0
        self.max_stamina = 100
        self.stamina = self.max_stamina
        self.stamina_regeneration = 0.05
        self.previous_health = None
        self.health_bar = pygame.Surface((80, 8))
        self.health_bar = self.prepare_bar()
        self.shield = Shield(("shield1", 0, 0))
        if self.team in common.team_colors.keys() : self.team_color = common.team_colors[self.team]
        self.cape = Cape(("cape1", 0, 0, self.team_color[0], self.team_color[1], self.team_color[2]))
        self.feet = [Foot(-1), Foot(1)]
        self.stun_time = 0
        self.fallen_time = 0
        self.death_time = 0
        self.is_alive = True
        self.body_angle = 0
        self.ai_delay = common.ai_delay
        if self.control_type == "clone" : self.items = [None, None, None, None]
        else : self.items = [None, None, None, None]
        self.items_images = [None, None, None, None]
        for i in range(4) : self.take_item(self.items[i], i)
        for i in range(6, 11, 1) :
            if len(words)>i : self.take_item(words[i])
            else : self.take_item(None)
        self.items_time = [0, 0, 0, 0]
        self.ai = AI(common.controls)
        self.clones = []
        self.cooldown_max = {"hit" : 50, "ultimate" : 500, "shield" : 180, "dash" : 300, "kick" : 150, "items":30, "roll":220}
        self.cooldown = self.cooldown_max.copy()
        for key in self.cooldown.keys() :
            self.cooldown[key] = 0
        if len(words)>5 :
            if words[5] == "random" : weapon_name = random.choice(common.weapons_list)
            else : weapon_name = words[5]
            self.change_weapon(weapon_name)
        else :
            self.change_weapon(random.choice(common.weapons_list))
        self.respawn_pos = self.pos.copy()
        self.update_image()
        self.killer_id = None
        self.kill_number = 0
        self.death_number = 0
        self.team_deaths = 0
        self.ace_number = 0
        self.invulnerability = 0
        self.dash_time = [0, 0]
        self.respawn_time = 0
        self.kick_time = 0
        self.roll_time = 0
        self.is_kicking = False

    def reset_cooldown(self, move):
        self.cooldown[move] = self.cooldown_max[move]

    def controls(self, controls, mouse_pos, screen_def):
        for clone in self.clones :
            clone.controls(controls, mouse_pos, screen_def)
            clone.lifetime -= 1
            if clone.lifetime <= 0 : clone.remove()
            if clone.lifetime <= 0 or not clone.is_alive : self.clones.remove(clone)
        if self.invulnerability > 0 : self.invulnerability -= 1
        if not self.is_alive :
            if type(self.respawn_time)==int : self.respawn_time -= 1
            return
        self.update_rect()
        self.manage_health(self.health_regeneration)
        self.manage_stamina(self.stamina_regeneration)
        for key in self.cooldown.keys():
            if self.cooldown[key] > 0 : self.cooldown[key] -= 1
        if not self.orientation_locked and not self.weapon.is_hitting and not self.stance in ["fallen"]:
            if mouse_pos[0] < screen_def[0]/2 : self.orientation = -1
            else : self.orientation = 1
        if self.stun_time > 0 : self.stun_time -= 1
        if self.fallen_time > 0 :
            self.fallen_time -= 1
            if self.fallen_time == 0 : self.recover_stance(self.last_stance)

        """ ABILITIES """

        if self.stun_time == 0 and self.fallen_time == 0 :
            if controls["ultimate"] and self.weapon.action == None and self.cooldown["ultimate"] == 0 and not self.is_kicking and not self.stance in ("climbing", "crawling", "rolling"):
                self.weapon.use_ultimate()
                if self.weapon.name == "hammer" :
                    rel_mouse = [mouse_pos[0] / screen_def[0] - 0.5, mouse_pos[1] / screen_def[1] - 0.5]
                    if rel_mouse[0] < -0.3: rel_mouse[0] = -0.3
                    if rel_mouse[0] > 0.3: rel_mouse[0] = 0.3
                    if rel_mouse[1] < -0.3: rel_mouse[1] = -0.3
                    if rel_mouse[1] > 0.3: rel_mouse[1] = 0.3
                    self.speed[0] += 60 * rel_mouse[0]
                    self.speed[1] += 20 * rel_mouse[1]
                    self.invulnerability = self.weapon.actions_duration["ultimate"]
                    self.reset_cooldown("ultimate")
            if self.weapon.is_ult :
                if self.weapon.name == "axe" :
                    dist = max(0.1, distance(self.screen_pos[0], self.screen_pos[1], mouse_pos[0], mouse_pos[1]))
                    angle = math.acos((mouse_pos[0] - self.screen_pos[0]) / dist)
                    if mouse_pos[1] > self.screen_pos[1]: angle *= -1
                    angle = math.degrees(angle)
                    effect = Effect(("shock_wave", self.rect.centerx, self.rect.centery - 15, angle, 0, self.team), owner=self.owner)
                    effect.grid_move()
                    self.reset_cooldown("ultimate")
                elif self.weapon.name == "hammer" :
                    self.weapon.inflict_damages(self.team, {"life" : [-20, "push", "drop", "ignore_block", "lateral"]})
                elif self.weapon.name == "sword" :
                    self.invulnerability = 2
                    self.weapon.inflict_damages(self.team, {"life": [-20, "push_high", "lateral"]})
                    self.reset_cooldown("ultimate")
                elif self.weapon.name == "bow" :
                    angle = self.angle_mouse(mouse_pos)
                    if self.stance != "crouched" :
                        if math.pi/3 < angle and angle < math.pi/2 : angle = math.pi/3
                        if math.pi/2 < angle and angle < 2/3*math.pi : angle = 2/3*math.pi
                        if 4/3*math.pi < angle and angle < 3/2*math.pi : angle = 4/3*math.pi
                        if 3/2*math.pi < angle and angle < 5/6*math.pi : angle = 5/6*math.pi
                    force = 26
                    object = Effect(["fire_arrow", self.rect.centerx + force * math.cos(angle), self.rect.centery - 15 - force * math.sin(angle), math.degrees(angle), self.orientation, self.team], force=(force * math.cos(angle), -force * math.sin(angle)), owner=self.owner)
                    object.grid_move()
                    self.reset_cooldown("ultimate")
                elif self.weapon.name == "sword" :
                    self.weapon.inflict_damages(self.team, {"life": [-20, "push", "lateral"]})
            if not self.stance in ["climbing", "crawling", "rolling"] and not self.is_kicking :
                if controls["hit"] :
                    if not self.weapon.is_hitting and self.cooldown["hit"] == 0 and self.weapon.action in [None, "normal", "raise", "raised"] and self.shield.action_counter == 0 and self.weapon.charge_power == 0 :
                        if self.manage_stamina(-8) : self.weapon.charge()
                else :
                    if 0 < self.weapon.charge_power and self.weapon.charge_power < 30 and self.weapon.action_counter == 0 :
                        self.reset_cooldown("hit")
                        self.weapon.hit()
                        self.weapon.charge_power = 0
            if self.weapon.charge_power >= 30 :
                self.weapon.action = None
                if not controls["hit"]:
                    self.reset_cooldown("hit")
                    self.weapon.charge_power = 0
                    stamina_cost = 0
                    if self.weapon.name in ["bow"] : stamina_cost = 4
                    if self.manage_stamina(-stamina_cost) : self.weapon.heavy_hit()
                    else : self.weapon.hit()
                if self.weapon.name in ["bow"] :
                    if self.orientation == 1 : self.weapon.angle = math.degrees(self.angle_mouse(mouse_pos))
                    else : self.weapon.angle = math.degrees(math.pi - self.angle_mouse(mouse_pos))
                    if self.stance != "crouched":
                        if self.weapon.angle > 180 : self.weapon.angle -= 360
                        if self.weapon.angle > 60 : self.weapon.angle = 60
                        if self.weapon.angle < -60 : self.weapon.angle = -60
            if controls["shield"] and self.cooldown["shield"] == 0 and not self.stance in ("climbing", "crawling", "rolling") :
                self.reset_cooldown("shield")
                self.shield.raise_shield()
            if controls["run"] and not self.shield.is_blocking :
                self.kick_time += 1
                if self.weapon.action in [None, "normal"] : self.weapon.raise_weapon()
            else:
                if self.weapon.action == "raised" : self.weapon.return_normal()
                elif 0 < self.kick_time and self.kick_time < 30  and self.cooldown["kick"] == 0 :
                    if (self.stance == "stand" or (self.stance == "rolling" and self.roll_time > 25)) and not self.weapon.action in ["hit", "heavy_hit", "ultimate"] :
                        self.is_kicking = True
                        self.roll_time = 1000
                        self.speed[0] += 6*self.orientation
                        self.speed[1] -= 6
                        self.reset_cooldown("kick")
                        for foot in self.feet : foot.kick()
                        self.weapon.raise_weapon()
                self.kick_time = 0
            if self.is_kicking :
                results = self.feet[1].inflict_damages(self.team, {"life":[-10, "drop", "kick"]})
                self.apply_effects(results)
                if self.feet[0].action_counter == 0 : self.is_kicking = False
            if common.Xor((controls["move right"], controls["move left"])) : self.kick_time = 200
            if self.shield.is_blocking :
                if abs(self.speed[0]) > 8 : self.shield.inflict_damages(self.team, {"life":[-10, "drop", "ignore_block", "bash"]})
            else : self.shield.exceptions = []
            if controls["roll"] and not self.stance in ["rolling", "climbing"] and self.cooldown["roll"] == 0 and self.weapon.action in [None, "normal"] :
                self.rect.x += 10*self.orientation
                self.recover_stance("rolling")
                if self.stance == "rolling" :
                    self.exceptions = []
                    self.roll_time = 1
                    self.orientation_locked = True
                    self.reset_cooldown("roll")
                    self.shield.action_counter = 0
                    self.shield.update(self.orientation)
                else :
                    self.rect.x -= 10 * self.orientation
            if self.roll_time > 0 :
                self.roll_time += 1
                self.body_angle -= 9
                if self.roll_time >= 10 :
                    self.speed[0] = 8 * self.orientation
                    self.inflict_damages(self.team, {"life": [-10, "drop", "ignore_block", "roll"]})
                if self.roll_time >= 70 :
                    self.body_angle = 0
                    self.orientation_locked = False
                    self.recover_stance("stand")
                    if self.stance == "rolling" :
                        self.recover_stance("crouched")
                        if self.stance == "rolling" : self.recover_stance("crawling")
                    self.roll_time = 0
            elif self.stance == "rolling" :
                self.speed[1] = 0
                self.recover_stance(self.last_stance)

            """ MOVE VERTICALLY """

            if self.is_onscale and common.Xor((controls["jump"], controls["crouch"])) :
                old_stance = self.stance
                if self.weapon.action_counter == 0 and not self.shield.is_blocking : self.recover_stance("climbing")
                if not "scale" in self.collide_background() : self.recover_stance(old_stance)
            else :
                if common.Xor((controls["move right"], controls["move left"])) :
                    if self.stance == "crouched" and self.weapon.action_counter == 0 and not self.shield.is_blocking : self.recover_stance("crawling")
                if self.stance in ["crouched", "crawling", "climbing"] and not controls["crouch"]:
                    old_stance = self.stance
                    if self.is_onground or self.is_onscale :
                        self.recover_stance("stand")
                        if self.stance != "stand" : self.recover_stance(old_stance)

            """ SPEED """

            if self.stance in ["stand", "climbing"]:
                speed = self.basic_speed["walking"]
                if controls["run"] and self.is_onground and not self.shield.is_blocking and not self.weapon.action in ["ultimate"]:
                    if common.Xor((controls["move right"], controls["move left"])) :
                        if self.manage_stamina(-0.2) : speed = self.basic_speed["running"]
                if self.is_onscale and not self.is_onground : speed /= 2
            elif self.stance in ["crawling", "crouched"] : speed = self.basic_speed["crawling"]
            else : speed = 0
            if self.haste_time > 0 :
                self.haste_time -= 1
                speed *= 3
            if controls["move left"]:
                if not self.feet[1].action : self.acceleration(-speed, 0)
                if self.dash_time[0] <= 0 : self.dash_time[0] -= 1
                elif 1 < self.dash_time[0] and self.cooldown["dash"] == 0:
                    self.acceleration(-15, 0)
                    self.reset_cooldown("dash")
                    self.dash_time = [0, 0]
            else:
                if -15 < self.dash_time[0] and self.dash_time[0] < 0 : self.dash_time[0] = 1
                elif self.dash_time[0] > 0 and self.dash_time[0] < 15 : self.dash_time[0] += 1
                else : self.dash_time[0] = 0
            if controls["move right"]:
                if not self.feet[1].action : self.acceleration(speed, 0)
                if self.dash_time[1] <= 0 : self.dash_time[1] -= 1
                elif 1 < self.dash_time[1] and self.cooldown["dash"] == 0:
                    self.acceleration(15, 0)
                    self.reset_cooldown("dash")
                    self.dash_time = [0, 0]
            else:
                if -15 < self.dash_time[1] and self.dash_time[1] < 0 : self.dash_time[1] = 1
                elif self.dash_time[1] > 0 and self.dash_time[1] < 15 : self.dash_time[1] += 1
                else : self.dash_time[1] = 0
            if controls["jump"] and not self.stance in ["rolling"]:
                if self.is_onscale :
                    self.acceleration(0, -0.01*self.jump_power)
                elif self.is_onground and not controls["crouch"]:
                    self.acceleration(0, -self.jump_power)
                    self.recover_stance("stand")
            elif controls["crouch"] :
                if self.is_onground :
                    if not self.stance in ["crouched", "crawling"] : self.recover_stance("crouched")
                elif self.is_onscale : self.acceleration(0, 0.01*self.jump_power)
            if not self.is_onground and not self.is_onscale and not self.stance in ["rolling"]: self.recover_stance("stand")
            self.rect.y += 1
            in_frame = common.rect_in_map(self.rect)
            self.rect.y -= 1
            if not in_frame : self.is_onground = True
            elif self.is_onground : self.lose_balance()

            """ ITEMS """

            for i in range(4) :
                if controls["item"+str(i+1)] and self.items[i] :
                    self.items_time[i] += 1
                    if self.items_time[i] > 60 :
                        self.give_item(i, mouse_pos)
                        self.items_time[i] = 0
            if self.cooldown["items"] == 0 :
                for i in range(4) :
                    if not controls["item"+str(i+1)] and 0 < self.items_time[i] and self.items_time[i] < 20:
                        self.items_time[i] = 0
                        self.use_item(i, mouse_pos)
                        self.reset_cooldown("items")
                        break
        if self.weapon.is_hitting :
            results = []
            if self.weapon.name == "axe" : results = self.weapon.inflict_damages(self.team, {"life" : [-20, "push", "lateral"], "tree" : -1})
            if self.weapon.name == "hammer" : results = self.weapon.inflict_damages(self.team, {"life" : [-20, "push", "lateral"], "break": -0.3})
            if self.weapon.name == "bow" : results = self.weapon.inflict_damages(self.team, {"life": [-10, "push", "lateral"]})
            if self.weapon.name == "sword" : results = self.weapon.inflict_damages(self.team, {"life": [-15, "push", "lateral"]})
            if len(results) > 0 : self.apply_effects(results)
        if self.weapon.is_heavy_hitting :
            if self.weapon.name == "bow" :
                angle, force = self.calc_throw(mouse_pos, 0.6, 18, 26)
                if self.orientation == 1 :  angle = math.radians(self.weapon.angle)
                else : angle = -math.pi - math.radians(self.weapon.angle)
                object = Effect(["arrow", self.rect.centerx + force * math.cos(angle), self.rect.centery - 15 - force * math.sin(angle), math.degrees(angle), self.orientation, self.team], force=(force * math.cos(angle), - force * math.sin(angle)), owner=self.owner)
                object.grid_move()
        if self.health == 0 and self.is_alive : self.die()
        if self.stance == "crouched": self.shield.angle = 15
        else : self.shield.angle = 0
        if self.team in common.escape_teams :
            if "escape" in self.collide_background() : self.escape()
        if controls["collect/interact"] and self.control_type != "clone":
            groups = common.sort_groups(groups=("item"), area=(self.get_area()))
            for item in groups["items"]:
                if self.is_alive and item.is_pickable:
                    if pygame.sprite.collide_mask(self, item):
                        if self.take_item(item.name): item.alive = False
            common.clean_groups(groups)
            for clone in self.clones :
                groups = common.sort_groups(groups=("item"), area=(clone.get_area()))
                for item in groups["items"]:
                    if clone.is_alive and item.is_pickable:
                        if pygame.sprite.collide_mask(clone, item):
                            if self.take_item(item.name): item.alive = False
                common.clean_groups(groups)
        if self.team in common.flag_teams :
            groups = common.sort_groups(groups=("background"), area=self.get_area(120))
            for background in groups["background"] :
                if background.name == "flag_pole" :
                    if common.distance(self.rect.centerx, self.rect.centery, background.rect.centerx, background.rect.centery) < 120 :
                        if self.team in background.teams_influence.keys() : background.teams_influence[self.team] += 1
                        else : background.teams_influence[self.team] = 1
            common.clean_groups(groups)
        if common.norm(self.speed) > 5 : self.enable_spikes()
        self.weapon.update(self.orientation)
        self.shield.update(self.orientation)
        self.cape.update(self.orientation, self.body_angle, self.stance)
        for foot in self.feet: foot.update(self)

    def get_signpost(self):
        text = False
        if "signpost" in self.collide_background():
            groups = common.sort_groups(groups="background", area=self.get_area())
            for background in groups["background"] :
                if background.name.startswith("signpost") :
                    text = common.signposts[background.text]
                    center = [background.screen_pos[0]+background.rect.width/2, background.screen_pos[1]-75]
        if text : return (text, center)
        return False

    def apply_effects(self, results):
        if "push_back" in results:
            self.speed[0] += self.orientation * -5
            self.weapon.is_hitting = False
            self.weapon.return_normal()
        if "fall" in results:
            self.weapon.charge_power = 0
            self.recover_stance("fallen")
            if self.stance == "fallen" :
                self.fallen_time = 75
                self.invulnerability = self.fallen_time + 30
                self.speed = [0, 0]
                self.roll_time = 0
                self.body_angle = 0
                self.orientation_locked = False
                self.cancel_moves()
                self.stun_time = 0
            else :
                self.last_stance = self.stance
                self.recover_stance("fallen")
        if "stun" in results or "blocked" in results :
            self.stun_time = 150
            self.cancel_moves()
            for i in (0, 120, 240):
                object = Effect(("stun_star", self.rect.centerx - 10, self.rect.y - 30, 0, 0, i))
                object.grid_move()

    def cancel_moves(self):
        self.weapon.return_normal()
        self.shield.angle = 0
        self.shield.rotate_speed = 0
        self.shield.shift = [0, 0]
        self.shield.action_counter = 0
        self.weapon.is_hitting = False
        self.weapon.is_ult = False
        self.shield.is_blocking = False
        self.shield.action_counter = 0
        self.weapon.arm_lenght = 20

    def die(self, count_kill=True):
        object = Effect(("dead_human", self.rect.centerx, self.rect.centery + 15))
        object.grid_move()
        effect = Effect(("blood0", self.rect.centerx, self.rect.centery - 25))
        effect.grid_move()
        if self.weapon :
            item = Item(("weapon_"+self.weapon.name, self.rect.centerx, self.rect.centery))
            item.grid_move()
        for i in range(len(self.items)):
            if self.items[i] :
                item = Item((self.items[i], self.rect.centerx, self.rect.centery - 5), force=(2*len(self.items)-4*i, -5))
                item.grid_move()
                self.items[i] = None
                self.items_images[i] = pygame.Surface((0, 0))
        self.mask = pygame.mask.Mask((0, 0))
        self.is_alive = False
        self.speed = [0, 0]
        self.cancel_moves()
        if self.control_type == "clone" : self.remove()
        else :
            if self.team in common.respawn_times.keys(): self.respawn_time = common.respawn_times[self.team]
            else : self.respawn_time = common.respawn_time
            if not self.respawn_time : self.remove()
        for clone in self.clones:
            clone.remove()
            self.clones.remove(clone)

        if count_kill and self.control_type != "clone" :
            self.death_number += 1
            mates_alive = 0
            groups = common.sort_groups(groups=("character"))
            for character in groups["characters"]:
                if character.team == self.team and character.is_alive: mates_alive += 1
                if character != self and character.id == self.killer_id : character.kill_number += 1
                if mates_alive == 0:
                    if character.team == self.team : character.team_deaths += 1
                    else : character.ace_number += 1
            common.clean_groups(groups)

    def escape(self):
        common.escape_score[self.team] += 1
        self.remove()

    def respawn(self, pos=None, health_prop=1):
        if not pos : pos = self.respawn_pos.copy()
        self.pos[0] = pos[0]
        self.pos[1] = pos[1]
        self.haste_time = 0
        self.mask = pygame.mask.from_surface(self.hitbox)
        self.health = int(self.max_health*health_prop)
        self.stamina = self.max_stamina
        self.is_alive = True
        self.fallen_time = 0
        self.stun_time = 0
        self.invulnerability = 50
        self.orientation_locked = False
        self.cooldown = self.cooldown_max.copy()
        self.killer_id = None
        self.change_weapon(self.weapon.name)
        self.stance = "stand"
        self.shield.action_counter = 0
        self.shield.update(self.orientation)
        for key in self.cooldown.keys() :
            if not key in ["hit", "ultimate"] : self.cooldown[key] = 0

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
            self.is_onground = True
        elif self.pos[1] < 0:
            self.pos[1] = 0
            self.speed[1] = 0

    def climb_step(self):
        i = 0
        is_colliding = True
        while i<self.step_height and is_colliding :
            i+=1
            self.pos[1] -= 1
            self.rect.y -= 1
            is_colliding = common.cm_el(common.block_interactions, self.collide_background())
        if is_colliding :
            self.pos[1] += i
            self.rect.y += i
        return is_colliding

    def lose_balance(self):
        self.rect.x += 1
        self.rect.y += self.step_height
        if common.cm_el(self.collide_background(), common.block_interactions) :
            self.rect.x -= 2
            if common.cm_el(self.collide_background(), common.block_interactions):
                self.rect.x += 1
                self.rect.y -= self.step_height
            else :
                self.pos = [self.rect.x, self.rect.y]
                self.is_onground = False
        else :
            self.pos = [self.rect.x, self.rect.y]
            self.is_onground = False

    def update_image(self):
        self.image = common.get_image("resources/characters/" + self.species + "/images/" + self.stance + ".png")
        self.hitbox = common.get_image("resources/characters/" + self.species + "/hitboxes/" + self.stance + ".png")
        if self.body_angle == 0 : self.body_shift = [0, 0]
        else :
            old_rect = self.hitbox.get_rect()
            self.image = pygame.transform.rotozoom(self.image.copy(), self.body_angle, 1)
            new_rect = self.hitbox.get_rect()
            self.body_shift = [(old_rect.width-new_rect.width)/2, (old_rect.height-new_rect.height)/2]
        if self.orientation == -1 : self.image = pygame.transform.flip(self.image.copy(), True, False)
        self.mask = pygame.mask.from_surface(self.hitbox)
        self.size = [self.hitbox.get_rect().width, self.hitbox.get_rect().height]
        self.rect.width = self.size[0]
        self.rect.height = self.size[1]

    def update_rect(self, move_x=True, move_y=True):
        if move_x :
            self.rect.x = self.pos[0]
            self.screen_pos[0] = int(self.pos[0] - common.camera_x + self.body_shift[0])
        if move_y :
            self.rect.y = self.pos[1]
            self.screen_pos[1] = int(self.pos[1] - common.camera_y + self.body_shift[1])
        self.rect = self.hitbox.get_rect(center=self.rect.center)
        self.grid_move()
        weapon_pos = [self.pos[0], self.pos[1]]
        weapon_screen_pos = [self.screen_pos[0], self.screen_pos[1]]
        if self.stance == "crouched":
            weapon_pos[0] += -15 * self.orientation
            weapon_pos[1] += 5
            weapon_screen_pos[0] += -15 * self.orientation
            weapon_screen_pos[1] += 5
        img_rect = self.image.get_rect()
        self.weapon.update_rect(self.orientation, weapon_pos, weapon_screen_pos, (self.rect.width, self.rect.height))
        self.shield.update_rect(self.orientation, weapon_pos, weapon_screen_pos, (self.rect.width, self.rect.height))
        self.cape.update_rect(self.orientation, self.pos, self.screen_pos, (img_rect.width, img_rect.height))
        for foot in self.feet : foot.update_rect(pos=(self.rect.centerx+3*self.orientation-foot.rect.width/2+foot.shift[0], self.rect.y+self.rect.height-foot.rect.height+foot.shift[1]))

    def update_pos(self):
        self.is_onground = False
        self.pos[0] += self.speed[0]
        self.update_rect(True, False)
        if common.cm_el(common.block_interactions, self.collide_background()):
            if self.speed[1] >= 0 :
                if self.climb_step() :
                    self.pos[0] -= self.speed[0]
                    self.speed[0] = 0
            else :
                self.pos[0] -= self.speed[0]
                self.speed[0] = 0
        self.update_rect(True, False)
        self.pos[1] += self.speed[1]
        self.update_rect(False, True)
        if common.cm_el(common.block_interactions, self.collide_background()):
            if self.speed[1] >= 0 :
                self.is_onground = True
            self.pos[1] -= self.speed[1]
            self.speed[1] = 0
        self.update_rect(False, True)
        if "scale" in self.collide_background() and self.fallen_time == 0 :
            if not self.is_onscale :
                self.speed = [0, 0]
                self.is_onscale = True
            if not self.is_onground :
                self.pos[1] += 1
                self.update_rect(False, True)
                if common.cm_el(common.block_interactions, self.collide_background()): self.is_onground = True
                self.pos[1] -= 1
                self.update_rect(False, True)
        elif self.is_onscale :
            self.pos[1] += 1
            self.update_rect(False, True)
            if "scale" in self.collide_background() :
                self.pos[1] += 1
                self.update_rect(False, True)
                if self.speed[1] < 0 : self.speed[1] = 0
            else :
                self.is_onscale = False
            self.pos[1] -= 1
            self.update_rect(False, True)

    def recover_stance(self, stance):
        saved_stance = self.stance
        old_rect = self.size.copy()
        self.stance = stance
        self.update_image()
        new_rect = self.size.copy()
        self.pos[0] += (old_rect[0] - new_rect[0]) / 2
        self.rect.x += (old_rect[0] - new_rect[0]) / 2
        self.pos[1] -= (new_rect[1] - old_rect[1])
        self.rect.y -= (new_rect[1] - old_rect[1])
        self.update_image()
        if common.rect_in_map(self.rect) :
            if common.cm_el(common.block_interactions, self.collide_background()) : blocked = True
            else : blocked = False
        else : blocked = True
        if blocked :
            self.stance = saved_stance
            self.update_image()
            self.pos[0] -= (old_rect[0] - new_rect[0]) / 2
            self.rect.x -= (old_rect[0] - new_rect[0]) / 2
            self.pos[1] += (new_rect[1] - old_rect[1])
            self.rect.y += (new_rect[1] - old_rect[1])

    def acceleration(self, force_x, force_y):
        self.speed[0] += force_x
        self.speed[1] += force_y

    def resistance(self, air_density):
        self.speed[0] *= (1 - air_density * self.resistance_power[0])
        self.speed[1] *= (1 - air_density * self.resistance_power[1])

    def display(self):
        if self.stance in ["crawling", "climbing", "fallen", "rolling"] :
            common.screen.blit(self.image, self.screen_pos)
            if self.feet[0].is_visible :
                common.screen.blit(self.feet[0].image, self.feet[0].screen_pos)
                common.screen.blit(self.feet[1].image, self.feet[1].screen_pos)
            common.screen.blit(self.cape.image, self.cape.screen_pos)
        else :
            if self.orientation == 1 :
                common.screen.blit(self.shield.image, self.shield.screen_pos)
                if self.feet[0].is_visible:
                    common.screen.blit(self.feet[0].image, self.feet[0].screen_pos)
                    common.screen.blit(self.feet[1].image, self.feet[1].screen_pos)
                common.screen.blit(self.image, self.screen_pos)
                common.screen.blit(self.cape.image, self.cape.screen_pos)
                common.screen.blit(self.weapon.image, self.weapon.screen_pos)
            else :
                common.screen.blit(self.weapon.image, self.weapon.screen_pos)
                if self.feet[0].is_visible:
                    common.screen.blit(self.feet[0].image, self.feet[0].screen_pos)
                    common.screen.blit(self.feet[1].image, self.feet[1].screen_pos)
                common.screen.blit(self.image, self.screen_pos)
                common.screen.blit(self.cape.image, self.cape.screen_pos)
                common.screen.blit(self.shield.image, self.shield.screen_pos)
        if self.previous_health != self.health :
            self.previous_health = self.health
            if self.control_type == "player" : self.health_bar = self.prepare_bar(back_color=(255, 0, 0), front_color=(0, 255, 0))
            else : self.health_bar = self.prepare_bar()
        common.screen.blit(self.health_bar, (self.screen_pos[0] - 40 + int(self.rect.width/2), self.screen_pos[1] - 10, 80, 10))

    def take_item(self, name, index=None):
        def apply_changes(i, name):
            if name:
                self.items[i] = name
                image = common.get_image("resources/items/" + name + ".png")
                rect = image.get_rect()
                if rect.width > 45 or rect.height > 45:
                    image = pygame.transform.scale(image, (int(45 * rect.width / max(rect.width, rect.height)), int(45 * rect.height / max(rect.width, rect.height))))
                self.items_images[i] = image
            else:
                self.items_images[i] = pygame.Surface((0, 0))
        if index == None :
            taken = False
            for i in range(len(self.items)) :
                if not self.items[i] :
                    apply_changes(i, name)
                    taken = True
                    break
        else :
            taken = True
            apply_changes(index, name)
        return taken

    def calc_throw(self, mouse_pos, mult, minimum, maximum):
        center = [self.screen_pos[0]+self.rect.width/2, self.screen_pos[1]+self.rect.height/2]
        dist = max(0.1, distance(center[0], center[1], mouse_pos[0], mouse_pos[1]))
        angle = common.length_to_angle(mouse_pos[0]-center[0], mouse_pos[1]-center[1])
        force = dist * mult
        if force > maximum : force = maximum
        if force < minimum : force = minimum
        return angle, force

    def angle_mouse(self, mouse_pos):
        center = [self.screen_pos[0]+self.rect.width/2, self.screen_pos[1]+self.rect.height/2]
        return common.length_to_angle(mouse_pos[0]-center[0], mouse_pos[1]-center[1])

    def use_item(self, index, mouse_pos):
        name = self.items[index]
        if name :
            blank_image = pygame.Surface((0, 0))
            self.items[index] = None
            self.items_images[index] = blank_image
            if name.startswith("weapon_") :
                old_weapon = self.weapon.name
                self.change_weapon(name[7:])
                self.take_item("weapon_"+old_weapon)
            if name == "wood":
                angle, force = self.calc_throw(mouse_pos, 0.1, 7, 25)
                object = Item(["wood", self.rect.centerx + force * math.cos(angle), self.rect.centery - 15 - force * math.sin(angle)], force=(force * math.cos(angle), -force * math.sin(angle)))
                if object != None:
                    object.grid_move()
            if name == "knife":
                angle, force = self.calc_throw(mouse_pos, 0.4, 6, 30)
                object = Effect(["knife", self.rect.centerx + force * math.cos(angle), self.rect.centery - 15 - force * math.sin(angle), math.degrees(angle), 0, self.team], force=(force * math.cos(angle), -force * math.sin(angle)), owner=self.owner)
                object.grid_move()
            if name == "stone":
                angle, force = self.calc_throw(mouse_pos, 0.3, 4, 24)
                object = Effect(["stone", self.rect.centerx + force * math.cos(angle), self.rect.centery - 15 - force * math.sin(angle), math.degrees(angle), 0, self.team], force=(force * math.cos(angle), -force * math.sin(angle)), owner=self.owner)
                object.grid_move()
            if name == "rope" :
                angle, force = self.calc_throw(mouse_pos, 0.3, 15, 15)
                object = Effect(["rope", self.rect.centerx + force * math.cos(angle), self.rect.centery - 15 - force * math.sin(angle), math.degrees(angle), 0, self.team], force=(force * math.cos(angle), -force * math.sin(angle)), owner=self)
                object.grid_move()
            if name == "health_potion" :
                self.manage_health(20)
            if name == "stamina_potion" :
                self.manage_stamina(30)
                self.cooldown["ultimate"] = int(self.cooldown["ultimate"]/2)
            if name == "clone_potion" :
                character = Character(("human", self.rect.centerx, self.rect.centery, "clone", self.team))
                character.change_weapon(self.weapon.name)
                character.speed[0] = (len(self.clones)*3+5)*self.orientation
                character.owner == self.id
                character.grid_move()
                self.clones += [character]
            if name == "haste_potion" :
                self.haste_time = 120
                effect = Effect(("haste_fire1", self.pos[0], self.pos[1]), owner=self)
                effect.grid_move()
                effect = Effect(("haste_fire1", self.pos[0], self.pos[1], 0, 1), owner=self)
                effect.grid_move()
            if name == "fruit_red" :
                self.manage_health(5)
            if name == "mine" :
                object = Effect(["mine_exploding1", self.rect.centerx, self.rect.centery, 0, 0, self.team], owner=self.owner)
                object.grid_move()
            if name == "grenade" :
                angle, force = self.calc_throw(mouse_pos, 0.2, 3, 15)
                object = Effect(["grenade_exploding1", self.rect.centerx + force * math.cos(angle), self.rect.centery - 15 - force * math.sin(angle), 0, 0, self.team], force=(force * math.cos(angle), -force * math.sin(angle)), owner=self.owner)
                object.grid_move()

    def give_item(self, index, mouse_pos):
        angle, force = self.calc_throw(mouse_pos, 0.05, 3.5, 12)
        item = Item((self.items[index], self.rect.centerx + force * math.cos(angle), self.rect.centery - 15 - force * math.sin(angle)), force=(force * math.cos(angle), -force * math.sin(angle)))
        item.grid_move()
        self.items[index] = None
        self.items_images[index] = pygame.Surface((0, 0))

    def change_weapon(self, weapon):
        if weapon :
            self.weapon = Weapon(weapon, owner=self.owner)
            self.weapon.actions_duration["charge"] = 20
            if weapon == "axe" :
                self.cooldown_max["ultimate"] = 540
                self.cooldown_max["hit"] = 50
            elif weapon == "hammer" :
                self.cooldown_max["ultimate"] = 420
                self.cooldown_max["hit"] = 60
            elif weapon == "bow" :
                self.weapon.actions_duration["charge"] = 20
                self.cooldown_max["ultimate"] = 500
                self.cooldown_max["hit"] = 65
            elif weapon == "sword" :
                self.cooldown_max["ultimate"] = 600
                self.cooldown_max["hit"] = 55
        else :
            self.weapon = None
        self.reset_cooldown("hit")
        self.reset_cooldown("ultimate")