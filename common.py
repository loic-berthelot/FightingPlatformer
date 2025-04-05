import pygame, math, os, common
pygame.init()

screen = pygame.display.set_mode((0, 0), pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.FULLSCREEN)
screen_def = (pygame.display.Info().current_w, pygame.display.Info().current_h)
screen = pygame.display.set_mode(screen_def, pygame.DOUBLEBUF | pygame.HWSURFACE | pygame.FULLSCREEN)
pygame.display.set_caption("FightingPlatformer")
is_fullscreen = True
screen_corner = [0,25]

controls = {"move left": pygame.K_q, "move right": pygame.K_d, "jump": pygame.K_z, "crouch": pygame.K_s, "run" : "mouse3", "collect/interact" : pygame.K_SPACE,
                     "item1": pygame.K_e, "item2": pygame.K_r, "item3": pygame.K_f, "item4": pygame.K_g, "hit": "mouse1", "ultimate": pygame.K_LCTRL, "shield": "mouse4", "toggle scoreboard" : pygame.K_TAB, "roll" : "mouse5"}
interface_type = "normal"
camera_x = 0
camera_y = 0
weapons_list = ["axe", "hammer", "bow", "sword"]
items_list = ["health_potion", "stamina_potion", "haste_potion", "clone_potion", "knife", "rope", "mine", "grenade", "stone", "wood", "weapon_axe", "weapon_hammer", "weapon_bow", "weapon_sword"]
block_interactions = ["block", "platform"]
platform_interactions = ["character", "arrow", "fire_arrow", "grenade_exploding1", "mine_exploding1"]
end_round_remove = ["arrow", "dead_human", "fire_arrow", "grenade_exploding1", "mine_exploding1", "knife", "rope", "stone"]
team_colors = {"bear" : (160, 60, 0), "wolf" : (70, 70, 70), "raven" : (0, 20, 80), "snake" : (0, 100, 30), "none" : (0, 0, 0)}
all_images = {}

def init() :
    global border_size, items_lifetime, items_pedestal, tree_regrow_time, victory_types, defeat_types, round_end, round_ends, round_timer, escape_teams, escape_score, max_vision_fading, respawn_time, respawn_times, signposts, local_messages, ai_delay, frame_number, flag_teams, flags_raised, platform_interactions, adapt_background
    border_size = [100, 100]
    items_lifetime = 3600
    items_pedestal = ["health_potion", "stamina_potion", "haste_potion", "clone_potion", "knife", "rope", "mine", "grenade"]
    tree_regrow_time = 1800
    victory_types = {"my_kills" : None, "my_escape" : False, "ace" : None, "flags_raised" : None}
    defeat_types = {"my_deaths" : None, "ace" : None, "teams_escape" : {}, "flags_raised" : None}
    round_ends = {"ace": []}
    round_end = 60
    round_timer = -1
    escape_teams = []
    escape_score = {}
    max_vision_fading = 60
    respawn_time = 180
    respawn_times = {}
    signposts = {}
    ai_delay = 5
    frame_number = 0
    for item in items_list : platform_interactions += [item]
    local_messages = []
    flag_teams = ["bear", "wolf", "raven", "snake"]
    flags_raised = {}
    for team in flag_teams : flags_raised[team] = 0
    adapt_background = "keep_proportions"

def get_image(adress):
    global all_images
    try:
        if adress.startswith("resources/background"):
            try :
                new_adress = adress[:21] + "transparent/" + adress[21:]
                image = all_images[new_adress]
            except:
                new_adress = adress[:21] + "solid/" + adress[21:]
                image = all_images[new_adress]
        else :
            image = all_images[adress]
    except :
        if adress.startswith("resources/background"):
            new_adress = adress[:21] + "transparent/" + adress[21:]
            try :
                image = pygame.image.load(new_adress)
            except:
                new_adress = adress[:21] + "solid/" + adress[21:]
                image = pygame.image.load(new_adress)
                image = image.convert()
            all_images[new_adress] = image
        else :
            image = pygame.image.load(adress)
            all_images[adress] = image
    return image.copy()

def cm_el(list1, list2):
    common = False
    for element in list1 :
        if element in list2 :
            common = True
            break
    return common

def clean_groups(groups):
    if type(groups) == pygame.sprite.Group :
        for object in groups : pygame.sprite.Sprite.kill(object)
    else :
        for group in groups.values():
            for object in group : pygame.sprite.Sprite.kill(object)

def merge_groups(groups):
    new_group = pygame.sprite.Group()
    for group in groups.values() :
        for element in group :
            new_group.add(element)
    return new_group

def length_to_angle(dx, dy):
    angle = None
    if dx == 0 :
        if dy > 0 : angle = math.pi/2
        if dy < 0 : angle = -math.pi/2
    elif dx > 0 :
        angle = math.atan(-dy/dx)
    else :
        if dy < 0 : angle = math.pi + math.atan(-dy/dx)
        else : angle = -math.pi + math.atan(-dy / dx)
    return angle%(2*math.pi)

def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def norm(vector):
    return math.sqrt(vector[0]**2+vector[1]**2)

def rect_in_map(rect, pos=None):
    if pos : return pos[0] >= 0 and pos[1] >= 0 and pos[0] + rect.width <= border_size[0] and pos[1] + rect.height <= border_size[1]
    return rect.x >= 0 and rect.y >= 0 and rect.x + rect.width <= border_size[0] and rect.y + rect.height <= border_size[1]

def point_in_rect(point, rect) :
    return point[0]>rect.x and point[1]>rect.y and point[0]<rect.x+rect.width and point[1]<rect.y+rect.height

def Xor(booleans):
    score = 0
    for boolean in booleans :
        if boolean : score += 1
    if score == 1 : return True
    return False

def len_groups(groups):
    len_groups = 0
    for group in groups :
        len_groups += len(group)
    return len_groups

def sort_groups(area=None, groups=("character", "background", "item", "effect")):
    group_characters = pygame.sprite.Group()
    group_background = pygame.sprite.Group()
    group_items = pygame.sprite.Group()
    group_effects = pygame.sprite.Group()
    if area==None :
        for line in common.grid_objects :
            for column in line :
                for key in column.keys():
                    if key in groups :
                        for object in column[key] :
                            if key == "character":
                                if not object in group_characters : group_characters.add(object)
                            elif key == "background":
                                if not object in group_background : group_background.add(object)
                            elif key == "item":
                                if not object in group_items : group_items.add(object)
                            elif key == "effect":
                                if not object in group_effects : group_effects.add(object)
    else:
        for i in range(area[2], area[3], 1):
            for j in range(area[0], area[1], 1):
                if i >= 0 and j >= 0 and i < len(common.grid_objects) and j < len(common.grid_objects[i]):
                    for key in common.grid_objects[i][j].keys():
                        if key in groups :
                            for object in common.grid_objects[i][j][key] :
                                if key == "character":
                                    if not object in group_characters: group_characters.add(object)
                                elif key == "background":
                                    if not object in group_background: group_background.add(object)
                                elif key == "item":
                                    if not object in group_items: group_items.add(object)
                                elif key == "effect":
                                    if not object in group_effects: group_effects.add(object)
    return {"characters": group_characters, "background": group_background, "items": group_items, "effects": group_effects}

def write(text, size=20, color=(0, 0, 0), font="Arial", angle=0):
    if type(text) != str : text = str(text)
    font = pygame.font.SysFont(font, size)
    text_image = font.render(text, 1, color)
    if angle != 0 :
        image = text_image.copy()
        text_image = pygame.transform.rotozoom(image, angle, 1)
    return text_image
