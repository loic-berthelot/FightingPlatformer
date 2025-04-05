import pygame, os, common
from game import Game
from button import Button
pygame.init()
control_keys = common.controls.copy()
file = open("controls.txt", "r")
for line in file :
    key = ""
    value = ""
    mode = 0
    for letter in line :
        if letter != "\n":
            if mode == 0 : mode = 1
            if letter == ":" : mode = 2
            elif mode == 1 : key += letter
            else : value += letter
    if mode == 2 :
        if value.startswith("mouse"): control_keys[key] = value
        else :
            try : control_keys[key] = pygame.key.key_code(value)
            except : pass
file.close()
patchnotes_list = []
file = open("patch_notes.txt")
for line in file :
    sentence = ""
    for letter in line :
        if letter == "\n":
            patchnotes_list += [sentence]
            sentence = ""
        else :
            sentence += letter
patchnotes_list += [sentence]
file.close()
clock = pygame.time.Clock()
mode = "menu_play"
buttons = {}
stopall = False
mouse_pressed = {0 : False, 1 : False, 2 : False, 3 : False, 4 : False}
mouse_pos = [0, 0]
map_selected = "test"

def create_buttons() :
    global buttons
    buttons["start"] = Button(text="START", bg_color=(0, 150, 0), text_color=(200, 200, 200), rect=(common.screen_def[0]-105, common.screen_def[1]-45, 100, 40))
    buttons["menu_play"] = Button(text="Play", rect=(10, 50, 180, 50), bg_color=(100, 100, 100))
    buttons["menu_controls"] = Button(text="Controls", rect=(10, 110, 180, 50), bg_color=(100, 100, 100))
    buttons["menu_credits"] = Button(text="Credits", rect=(10, 170, 180, 50), bg_color=(100, 100, 100))
    buttons["menu_patchnotes"] = Button(text="Patch Notes", rect=(10, 230, 180, 50), bg_color=(100, 100, 100))
    buttons["menu_editor"] = Button(text="Map editor (not available yet)", rect=(10, 290, 180, 50), bg_color=(100, 100, 100))
    buttons["menu_leave"] = Button(text="Leave game", rect=(10, common.screen_def[1]-60, 180, 50), bg_color=(100, 100, 100))
    buttons["game_settings"] = Button(symbol="gear_wheel", rect=(common.screen_def[0]-45, 5, 40, 40), bg_color=(150, 30, 0))
    buttons["game_restart"] = Button(text="Restart", rect=(common.screen_def[0] - 110, 70, 100, 40), bg_color=(150, 30, 0))
    buttons["game_leavematch"] = Button(text="Leave match", rect=(common.screen_def[0] - 110, 120, 100, 40), bg_color=(150, 30, 0))
    buttons["game_leavegame"] = Button(text="Leave game =(", rect=(common.screen_def[0] - 110, 170, 100, 40), bg_color=(150, 30, 0))
    buttons["play_again"] = Button(text="Play again", rect=(200, common.screen_def[1]-100, 200, 50), bg_color=(150, 150, 150))
    buttons["return_menu"] = Button(text="Return to Menu", rect=(common.screen_def[0] - 400, common.screen_def[1] - 100, 200, 50), bg_color=(150, 150, 150))

    i = 105
    for filename in os.listdir("maps"):
        name = filename[:len(filename) - 6]
        if filename[len(filename) - 6:] == ".wilds":
            with open(os.path.join("maps", filename), 'r') as f :
                buttons["map_"+filename] = Button(bg_color=(100, 100, 100), text=name, rect=(220, i, 200, 25))
            i += 30
    i = 50
    for key in control_keys.keys():
        buttons["control_"+key] = Button(text=key, rect=(int(common.screen_def[0]/2), i, 200, 40), bg_color=(100, 100, 100), max_font_size=20, border=(0 , 0, 100, 0))
        i += 50

def save_controls():
    file = open("controls.txt", "w")
    for key in control_keys :
        if type(control_keys[key])==str : file.write(key + ":" + control_keys[key])
        else : file.write(key+":"+pygame.key.name(control_keys[key]))
        file.write("\n")
    file.close()

def load_description():
    file = open("maps/"+map_selected+".wilds")
    description = ""
    read = -1
    for line in file :
        if line.startswith("DESCRIPTION") : read *= -1
        elif read == 1 : description += line
    file.close()
    return description

def write(text, size=20, color=(0, 0, 0), font="Arial", angle=0):
    font = pygame.font.SysFont(font, size)
    text_image = font.render(text, 1, color)
    if angle != 0 :
        image = text_image.copy()
        text_image = pygame.transform.rotozoom(image, angle, 1)
    return text_image

create_buttons()
map_description = load_description()
while not stopall :
    clock.tick(60)
    pygame.display.flip()
    mouse_pos = pygame.mouse.get_pos()
    if mode.startswith("menu") :
        common.screen.fill((180, 200, 255))
        pygame.draw.rect(common.screen, (50, 50, 50), (0, 0, 200, common.screen_def[1]))
        if buttons["menu_play"].display(mouse_pos, mouse_pressed) == 3 : mode = "menu_play"
        if buttons["menu_controls"].display(mouse_pos, mouse_pressed) == 3: mode = "menu_controls"
        if buttons["menu_credits"].display(mouse_pos, mouse_pressed) == 3: mode = "menu_credits"
        if buttons["menu_patchnotes"].display(mouse_pos, mouse_pressed) == 3: mode = "menu_patchnotes"
        buttons["menu_editor"].display(mouse_pos, mouse_pressed)
        if buttons["menu_leave"].display(mouse_pos, mouse_pressed) == 3:
            stopall = True
            pygame.quit()
            break
        for key in buttons.keys() :
            button = buttons[key]
            if key.startswith("menu_"):
                if mode == key : color = (170, 170, 170)
                else : color = (100, 100, 100)
                if button.bg_color != color:
                    button.bg_color = color
                    button.update_image()
    if mode == "menu_play":
        common.screen.blit(write("MAPS : ",  size=30), (220, 50))
        pygame.draw.rect(common.screen, (20, 20, 20), (215, 100, 210, common.screen_def[1] - 105))
        pygame.draw.rect(common.screen, (100, 100, 100), (215, 100, 210, common.screen_def[1]-105), 3)
        pygame.draw.rect(common.screen, (20, 20, 20), (440, 100, common.screen_def[0]-600, common.screen_def[1] - 300))
        pygame.draw.rect(common.screen, (100, 100, 100), (440, 100, common.screen_def[0] - 600, common.screen_def[1] - 300), 3)
        i = 120
        sentence = ""
        for letter in map_description :
            if letter == "\n" :
                common.screen.blit(write(sentence, color=(255, 255, 255), size=25), (470, i))
                i += 30
                sentence = ""
            else :
                sentence += letter
        common.screen.blit(write(sentence, color=(255, 255, 255), size=25), (470, i))
        for key in buttons.keys() :
            button = buttons[key]
            if key.startswith("map_"):
                if button.display(mouse_pos, mouse_pressed) == 3:
                    map_selected = button.text
                    map_description = load_description()
                if map_selected == button.text : color = (170, 170, 170)
                else : color = (100, 100, 100)
                if button.bg_color != color:
                    button.bg_color = color
                    button.update_image()
        if buttons["start"].display(mouse_pos, mouse_pressed) == 3 :
            mode = "game"
            game = Game(map_selected)
    elif mode == "menu_credits" :
        common.screen.blit(write("Game made by Elendil.", size=25, angle=30), (300, 60))
        common.screen.blit(write("This game is strongly inspired by wilds.io, a game by Rezoner.", size=20, angle=-5), (600, 20))
        common.screen.blit(write("Thanks to Mapetinary, Poland2020 and Jesperr for ideas.", color=(45, 115, 5)), (400, 250))
        common.screen.blit(write("Thanks to Bifur the Dwarf, Game Over and Mapetinary for drawings.", size=25, color=(45, 115, 5)), (400, 300))
        common.screen.blit(write("Say me if YOU want to participate too !", size=25, color=(200, 0, 0)), (400, 400))
    elif mode == "menu_controls":
        key_modif = None
        for key in control_keys.keys():
            rect = buttons["control_"+key].rect
            if buttons["control_"+key].display(mouse_pos, mouse_pressed) == 3 :
                buttons["control_" + key].left_click = 0
                buttons["control_" + key].bg_color = (0, 100, 0)
                buttons["control_" + key].update_image()
                buttons["control_" + key].display(mouse_pos, mouse_pressed)
                key_modif = key
                common.screen.blit(write("Press a key"), (int(common.screen_def[0]/2), 20))
            if type(control_keys[key])==str : text = control_keys[key]
            else : text = pygame.key.name(control_keys[key])
            pygame.draw.rect(common.screen, (80, 15, 0), (rect.x+117, rect.y+3, 80, rect.height-6))
            common.screen.blit(write(text, color=(255, 255, 255)), (rect.x+120, rect.y+3, 80, rect.height-6))
        if key_modif != None :
            pygame.display.flip()
            while key_modif != None:
                clock.tick(60)
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN:
                        control_keys[key_modif] = event.key
                        buttons["control_" + key_modif].bg_color = (100, 100, 100)
                        buttons["control_" + key_modif].update_image()
                        key_modif = None
                        save_controls()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        control_keys[key_modif] = "mouse" + str(event.button)
                        buttons["control_" + key_modif].bg_color = (100, 100, 100)
                        buttons["control_" + key_modif].update_image()
                        key_modif = None
                        save_controls()
    elif mode == "menu_patchnotes" :
        for i in range (len(patchnotes_list)) : common.screen.blit(write(patchnotes_list[i], size=20), (300, 50 + 25*i))
    elif mode in ["victory", "defeat"] :
        common.screen.fill((0, 0, 0))
        if mode == "victory" : text = write(text="VICTORY !", color=(255, 255, 0), size=110)
        else : text = write(text="DEFEAT", color=(200, 30, 30), size=110)
        rect = text.get_rect()
        common.screen.blit(text, (int((common.screen_def[0]-rect.width)/2), int((common.screen_def[1]-rect.height)/2)))
        if buttons["play_again"].display(mouse_pos, mouse_pressed)==3 :
            game = Game(map_selected)
            mode = "game"
        elif buttons["return_menu"].display(mouse_pos, mouse_pressed)==3 :
            game = None
            mode = "menu_play"
    elif mode == "game" :
        if not game.settings_open :
            game.controls(control_keys)
            game.manage_rolling()
            game.update_rect()
            game.interactions()
            results = game.check_end()
            if results == "victory" : mode = "victory"
            elif results == "defeat" : mode = "defeat"
            game.end_round()
        if game.character.is_alive :
            common.interface_type = "normal"
            game.display()
            game.vision_fading = 0
        else :
            common.interface_type = None
            game.display_respawn()
        game.display_interface()
        if game.controlsdown["toggle scoreboard"] : game.display_scoreboard()
        game.display_fps(clock)
        if game.settings_open :
            pygame.draw.rect(common.screen, (100, 100, 100), (common.screen_def[0]-120, 0, 120, 250))
            if buttons["game_leavematch"].display(mouse_pos, mouse_pressed) == 3:
                mode = "menu_play"
                game = None
            if buttons["game_leavegame"].display(mouse_pos, mouse_pressed) == 3:
                stopall = True
                game = pygame.quit()
                break
            if buttons["game_restart"].display(mouse_pos, mouse_pressed) == 3:
                game = None
                game = Game(map_selected)
        if buttons["game_settings"].display(mouse_pos, mouse_pressed) == 3 :
            if game.settings_open : game.settings_open = False
            else : game.settings_open = True
    for event in pygame.event.get():
        if event.type == pygame.QUIT :
            stopall = True
            pygame.quit()
        if mode == "game" :
            if event.type == pygame.KEYDOWN : game.keydown("button", event.key)
            elif event.type == pygame.KEYUP : game.keyup("button", event.key)
            if event.type == pygame.MOUSEBUTTONDOWN : game.keydown("mouse", event.button)
            if event.type == pygame.MOUSEBUTTONUP : game.keyup("mouse", event.button)
        if event.type == pygame.KEYDOWN :
            if event.key == pygame.K_ESCAPE :
                pygame.display.quit()
                pygame.display.init()
                if common.is_fullscreen :
                    common.is_fullscreen = False
                    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (common.screen_corner[0], common.screen_corner[1])
                    common.screen = pygame.display.set_mode(common.screen_def)
                else:
                    text = os.environ['SDL_VIDEO_WINDOW_POS']
                    word = ""
                    for letter in text :
                        if letter == "," :
                            common.screen_corner[0] = int(word)
                            word = ""
                        else : word += letter
                    common.screen_corner[1] = int(word)
                    common.is_fullscreen = True
                    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 0)
                    common.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        if event.type == pygame.MOUSEBUTTONDOWN : mouse_pressed[event.button - 1] = True
        if event.type == pygame.MOUSEBUTTONUP : mouse_pressed[event.button - 1] = False
