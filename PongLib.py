from math import sin, cos, radians, atan2, degrees
import pygame as pg
import numpy as np
import re

# USER VARIABLES!!!

# Assuming 1px = 1mm
MAX_ACCEL = 30 # mm/s sq
MAX_VEL = 15    # mm/s

# END OF USER VARIABLES!!!

def rotate_point(point: tuple[float, float], angle: float, center_point: tuple[float, float] = (0, 0)) -> tuple[float, float]:
    angle_rad = radians(angle % 360)
    new_point = (point[0] - center_point[0], point[1] - center_point[1])
    new_point = (new_point[0] * cos(angle_rad) - new_point[1] * sin(angle_rad),
                 new_point[0] * sin(angle_rad) + new_point[1] * cos(angle_rad))
    new_point = (new_point[0] + center_point[0], new_point[1] + center_point[1])
    return new_point

class TextBox:
    def __init__(self, font: pg.font.Font, text: str, center: pg.Vector2, padding: int = 4, text_color: pg.Color = pg.Color("white"), box_color: pg.Color = pg.Color("white")):
        self._font = font
        self._text = text

        self._rect = pg.Rect(0, 0, font.size(text)[0] + (padding*2), font.size(text)[1] + (padding*2))
        self._rect.center = center
        self._padding = padding
        
        self._text_color = text_color
        self._box_color = box_color
        
    def setText(self, text: str):
        c = self._rect.center
        
        self._text = text
        self._rect = pg.Rect(0, 0, self._font.size(text)[0] + (self._padding*2), self._font.size(text)[1] + (self._padding*2))
        self._rect.center = c

    def draw(self, screen: pg.Surface) -> None:
        font_surf = self._font.render(self._text, True, self._text_color)        
        screen.blit(font_surf, self._rect.topleft + pg.Vector2(self._padding, self._padding))
        pg.draw.rect(screen, self._box_color, self._rect, 1, 1)

class Button:
    def __init__(self, font: pg.font.Font, text: str, center: pg.Vector2, padding: int = 4, passive_color: pg.Color = pg.Color("grey"), active_color: pg.Color = pg.Color("white")):
        self._font = font
        self._padding = padding
        self._pcolor = passive_color
        self._acolor = active_color
        self._text = text
        
        self._rect = pg.Rect(0, 0, font.size(text)[0] + (padding*2), font.size(text)[1] + (padding*2))
        self._rect.center = center
        
        self._color = self._pcolor
        self._active = False
        
        self._pressed = False
        
    def _activate(self) -> None:
        self._color = self._acolor
        self._active = True
    
    def _deactivate(self) -> None:
        self._color = self._pcolor
        self._active = False
    
    def handle_event(self, event: pg.event.Event) -> None:
        match event.type:
            case pg.MOUSEMOTION:
                if self._rect.collidepoint(event.dict['pos']):
                    self._activate()
                else:
                    self._deactivate()
            case pg.MOUSEBUTTONDOWN:
                if self._rect.collidepoint(event.dict['pos']):
                    self._pressed = True
            case pg.MOUSEBUTTONUP:
                self._pressed = False
                    
    def getPressed(self) -> bool:
        return self._pressed
    
    def draw(self, screen: pg.Surface) -> None:
        font_surf = self._font.render(self._text, True, self._color)
        screen.blit(font_surf, self._rect.topleft + pg.Vector2(self._padding, self._padding))
        pg.draw.rect(screen, self._color, self._rect, 1, 1)

class TextInput:
    def __init__(self, font: pg.font.Font, placeholder: str, center: pg.Vector2, width: int = 200, padding: int = 4, passive_color: pg.Color = pg.Color("grey"), active_color: pg.Color = pg.Color("white")):
        self._font = font
        self._padding = padding
        self._pcolor = passive_color
        self._acolor = active_color
        self._text = placeholder
        self._placeholder = placeholder
        
        self._rect = pg.Rect(0, 0, width, font.size("")[1] + (padding*2))
        self._rect.center = center
        self._min_width = width
        self._center = center
        
        self._color = self._pcolor
        self._active = False
        
    def activate(self) -> None:
        if self._text == self._placeholder:
            self._text = ""
        self._color = self._acolor
        self._active = True
    
    def deactivate(self) -> None:
        self._color = self._pcolor
        self._active = False
    
    def handle_event(self, event: pg.event.Event) -> None:
        match event.type:
            case pg.KEYDOWN:
                if self._active:
                    if event.dict['key'] == pg.K_BACKSPACE:
                        self._text = self._text[:-1]
                    elif re.fullmatch("[A-Za-z0-9_\-]", str(event.dict['unicode']), re.A):
                        self._text += event.dict['unicode']
            case pg.MOUSEBUTTONDOWN:
                if self._rect.collidepoint(event.dict['pos']):
                    self.activate()
                else:
                    self.deactivate()
                    
    def getText(self) -> str:
        return self._text
    
    def draw(self, screen: pg.Surface) -> None:
        font_surf = self._font.render(self._text, True, self._color)
        self._rect.width = max(font_surf.get_size()[0] + (self._padding*2), self._min_width)
        
        while self._rect.width > screen.get_width():
            self._text = self._text[:-1]
            font_surf = self._font.render(self._text, True, self._color)
            self._rect.width = max(font_surf.get_size()[0] + (self._padding*2), self._min_width)
        self._rect.center = self._center
        
        screen.blit(font_surf, self._rect.topleft + pg.Vector2(self._padding, self._padding))
        pg.draw.rect(screen, self._color, self._rect, 1, 1)
        

class Paddle:
    def __init__(self, rect: pg.Rect, velocity: float = 0, angle: float = 0, flip: bool = False):
        self._rect = rect
        self._collision_rect = pg.Rect(rect.left - rect.height + rect.width, rect.top, rect.height, rect.height)
        if flip:
            self._rect.left = self._rect.right
            self._collision_rect.left = self._collision_rect.right
        self._traj = pg.math.Vector2(0, velocity).rotate(angle)
        self._velocity = velocity
        self._angle = angle
        
    def update(self, screen: pg.Surface, keyDict: dict, dt: float) -> None: 
        if 'w' in keyDict.keys():
            self._velocity = max((-MAX_ACCEL * dt / 1000) + self._velocity, -MAX_VEL)
        elif 's' in keyDict.keys():
            self._velocity = min((MAX_ACCEL * dt / 1000) + self._velocity, MAX_VEL)
        else:
            self._velocity = max(abs(self._velocity) - (30 * dt / 1000), 0) * np.sign(self._velocity)
            
        self._traj = pg.math.Vector2(0, self._velocity).rotate(self._angle)
        
        self._rect.center += self._traj
        
        clamp = self._rect.clamp(screen.get_rect())
        if clamp != self._rect:
            self._velocity = 0
        self._rect.center = clamp.center
        self._collision_rect.top = self._rect.top
        
    def draw(self, screen: pg.Surface, color: str|tuple[int, int, int]) -> pg.Rect:
        return pg.draw.rect(screen, color, self._rect)
            
    def getRect(self) -> pg.Rect:
        return self._rect

class Ball:
    def __init__(self, center: pg.math.Vector2, raduis: int, velocity: float, motion_angle: float):
        self._cpt = center
        self._rad = raduis
        self._traj = pg.math.Vector2(0, velocity).rotate(motion_angle)

    # Created using examples from https://github.com/Rabbid76/PyGameExamplesAndAnswers/blob/master/documentation/pygame/pygame_collision_and_intesection.md  
    def colliderect(self, screen: pg.Surface, rect: pg.Rect) -> None:
        ball_rect = pg.Rect((0, 0), (self._rad*2, self._rad*2))
        ball_rect.center = self._cpt
        
        if rect.colliderect(ball_rect):
            dx = self._cpt.x - rect.centerx
            dy = self._cpt.y - rect.centery
            
            if abs(dx) > abs(dy):
                if (dx < 0 and self._traj[0] > 0) or (dx > 0 and self._traj[0] < 0):
                    self._traj.reflect_ip(pg.math.Vector2(1, 0))
            else:
                if dy < 0:
                    ballPosY = max(rect.top - self._rad, self._rad + 0) 
                    rect.top = int(ballPosY) + self._rad
                else:
                    ballPosY = min(rect.bottom + self._rad, screen.get_height() - self._rad)
                    rect.bottom = int(ballPosY) - self._rad
                ballPosY = rect.top - self._rad if dy < 0 else rect.bottom + self._rad
                if (dy < 0 and self._traj[1] > 0) or (dy > 0 and self._traj[1] < 0):
                    self._traj.reflect_ip(pg.math.Vector2(0, 1))
                    
    def collidepaddle(self, screen: pg.Surface, paddle: Paddle) -> None:
        self.colliderect(screen, paddle._collision_rect)

    def update(self, dt: float) -> None:
        self._traj = pg.Vector2(0, min((.1 * dt / 1000) + self._traj.magnitude(), MAX_VEL)).rotate(-degrees(atan2(self._traj.x, self._traj.y)))
        self._cpt += self._traj
    
    def draw(self, screen: pg.Surface, color: str|tuple[int, int, int]) -> pg.Rect:
        return pg.draw.circle(screen, color, self._cpt, self._rad)
    
    def getTrajectory(self) -> pg.math.Vector2:
        return self._traj
    
    def setTrajectory(self, trajectory: pg.math.Vector2) -> None:
        self._traj = trajectory
    
    def getCenter(self) -> pg.math.Vector2:
        return self._cpt
    
    def setCenter(self, center: pg.math.Vector2) -> None:
        self._cpt = center