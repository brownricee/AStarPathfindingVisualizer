import pygame, sys
import tkinter as tk
from tkinter import messagebox


class Button:
    def __init__(self, x, y, image, scale):
        # This will be used to scale an image in case it's too big.
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.clicked = False
    def draw(self, surface):
        # Getting the position of the mouse cursor to detect if it's clicked the button
        pos = pygame.mouse.get_pos()
        action = False
        if self.rect.collidepoint(pos):
            # Self.clicked == false is used to make sure the button doesn't trigger multiple times 
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True
            if pygame.mouse.get_pressed()[0] == 0:
               self.clicked = False
        surface.blit(self.image, (self.rect.x, self.rect.y))
        return action

def show_error_window(message):
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Error", message)
