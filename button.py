import pygame, common

pygame.init()

class Button(pygame.sprite.Sprite):
    def __init__(self, text=None, symbol=None, rect=(0, 0, 200, 50), bg_color=(255, 255, 255), text_color=(0, 0, 0), selected=False, max_font_size=0, border=(0, 0, 0, 0)):
        super().__init__()
        self.rect = pygame.Rect(rect[0], rect[1], rect[2], rect[3])
        self.bg_color = bg_color
        self.text_color = text_color
        self.is_selected = selected
        self.max_font_size = max_font_size
        if text == None: self.text = ""
        else : self.text = text
        if symbol == None: self.symbol = None
        else : self.symbol = pygame.image.load("resources/icons/"+symbol+".png")
        self.border = border
        self.update_image()
        self.left_click = 0

    def display(self, mouse_pos, mouse_pressed):
        common.screen.blit(self.image, self.rect)
        if mouse_pos[0] > self.rect.x and mouse_pos[0] < self.rect.x+self.rect.width and mouse_pos[1] > self.rect.y and mouse_pos[1] < self.rect.y + self.rect.height :
            if self.left_click == 0 and not mouse_pressed[0] : self.left_click = 1
            elif self.left_click == 1 and mouse_pressed[0] : self.left_click = 2
            elif self.left_click == 2 and not mouse_pressed[0] : self.left_click = 3
            elif self.left_click == 3 : self.left_click = 0
        else : self.left_click = 0
        return self.left_click

    def update_image(self):
        self.image = pygame.Surface((self.rect.width, self.rect.height))
        self.image.fill(self.bg_color)
        if self.symbol : self.image.blit(self.symbol, (0, 0))
        self.font_size = min(int(2 * (self.rect.width-self.border[0]-self.border[2])/ len(self.text+" ")), int((self.rect.height-self.border[1]-self.border[3]) * 0.8))
        if self.max_font_size != 0 and self.font_size>self.max_font_size : self.font_size = self.max_font_size
        self.font = pygame.font.SysFont("Arial", self.font_size)
        self.text_image = self.font.render(self.text, 1, self.text_color)
        self.text_rect = self.text_image.get_rect()
        self.image.blit(self.text_image, (int((self.rect.width + self.border[0] - self.border[2]- self.text_rect.width) / 2), int((self.rect.height +self.border[1]-self.border[3]- self.text_rect.height) / 2)))
        self.left_click = 0
        self.right_click = 0
