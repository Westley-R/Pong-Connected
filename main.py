import pygame as pg
import numpy as np
import random

from math import sin, cos, radians, degrees, atan2

pg.init()

# USER VARIABLES!!!

# Assuming 1px = 1mm
MAX_ACCEL = 100 # mm/s sq
MAX_VEL = 10    # mm/s

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

PADDLE_HEIGHT = 100
PADDLE_WIDTH = 10
BALL_RADIUS = 12

# END OF USER VARIABLES!!!

# Chaos pong: 2 pong balls, going different directions; 4 players

# This code snippet was grabbed from my Python Raytracing project @ <https://github.com/Westley-R/Python-Raytracing/tree/main/dev/2d%20rotation/main.py> lines 4-10
# I find its easier to create functions to do vector math for me, then work with "vectors" instead of X, Y cordinate pairs.
def rotate_point(point: tuple[float, float], angle: float, center_point: tuple[float, float] = (0, 0)) -> tuple[float, float]:
    angle_rad = radians(angle % 360)
    new_point = (point[0] - center_point[0], point[1] - center_point[1])
    new_point = (new_point[0] * cos(angle_rad) - new_point[1] * sin(angle_rad),
                 new_point[0] * sin(angle_rad) + new_point[1] * cos(angle_rad))
    new_point = (new_point[0] + center_point[0], new_point[1] + center_point[1])
    return new_point

def get_dist_from_line(point: np.ndarray, line: np.array) -> float:
    return np.cross(line[1] - line[0], point - line[0]) / np.linalg.norm(line[1] - line[0])

def get_dist_from_line_segment(point: np.ndarray, line: np.array) -> float:
    segVec = line[1] - line[0]    
    segLen = np.dot(segVec, segVec)
    projection = 0 if segLen == 0 else np.clip(np.dot(point - line[0], segVec) / segLen, 0, 1)
    return np.linalg.norm(point - (line[0] + projection * segVec))

def get_line_angle(p1: np.ndarray, p2: np.ndarray) -> float:
    return abs(degrees(atan2(p2[1] - p1[1], p2[0] - p1[0])) % 360)

def gen_rect_polygon(center: tuple[float, float], width: int, height: int, rotation: float = 0) -> list:
    return [
        rotate_point((center[0] - width/2, center[1] - height/2), rotation, center),
        rotate_point((center[0] + width/2, center[1] - height/2), rotation, center),
        rotate_point((center[0] + width/2, center[1] + height/2), rotation, center),
        rotate_point((center[0] - width/2, center[1] + height/2), rotation, center)
    ]

# Made using https://stackoverflow.com/questions/3252194/numpy-and-line-intersections 2nd top answer (honestly, I just dont understand vector math all that much)
def get_intersect(a1: tuple[float, float], a2: tuple[float, float], b1: tuple[float, float], b2: tuple[float, float]) -> tuple[float, float]:
    """ 
    Returns the point of intersection of the lines passing through a2,a1 and b2,b1.
    a1: [x, y] a point on the first line
    a2: [x, y] another point on the first line
    b1: [x, y] a point on the second line
    b2: [x, y] another point on the second line
    """
    s = np.vstack([a1, a2, b1, b2])
    h = np.hstack((s, np.ones((4, 1))))
    l1 = np.cross(h[0], h[1])
    l2 = np.cross(h[2], h[3])
    x, y, z = np.cross(l1, l2)
    
    if z == 0: 
        return (float('inf'), float('inf'))
    
    return (x/z, y/z)
# End of code snippet!    
    
if __name__ == "__main__":
    w, h = (SCREEN_WIDTH, SCREEN_HEIGHT)
    screen = pg.display.set_mode((w, h))
    clock = pg.time.Clock()
    
    walls = [
        [(0, 0), (0, h)],
        [(0, h), (w, h)],
        [(w, h), (w, 0)],
        [(w, 0), (0, 0)]
    ]
    
    paddles = [
        {"pos": [50, (h / 2) - (PADDLE_HEIGHT / 2)], "vel": 0, "angle": 0},
        {"pos": [w - 50, (h / 2) - (PADDLE_HEIGHT / 2)], "vel": 0, "angle": 180}
    ]
    
    balls = [
        {"pos": [w / 2, h / 2], "vel": 60, "angle": random.randint(-89, 89)}
    ]
    
    keyDict = {}

    while True:
        screen.fill("black")
        breakFlag = False
        
        dt = clock.tick(60)

        for event in pg.event.get():
            match event.type:
                case pg.QUIT:
                    breakFlag = True
                case pg.KEYDOWN:
                    keyDict[event.dict['unicode']] = 1
                case pg.KEYUP:
                    try:
                        del keyDict[event.dict['unicode']]
                    except:
                        pass
        
        if '\x1b' in keyDict.keys():
            breakFlag = True
            
        if 'w' in keyDict.keys():
            paddles[0]["vel"] = max((-30 * dt / 1000) + paddles[0]["vel"], -MAX_VEL)
        elif 's' in keyDict.keys():
            paddles[0]["vel"] = min((30 * dt / 1000) + paddles[0]["vel"], MAX_VEL)
        else:
            paddles[0]["vel"] = max(abs(paddles[0]["vel"]) - (30 * dt / 1000), 0) * np.sign(paddles[0]["vel"])
        
        for paddle in paddles:
            paddle["pos"][1] += paddle["vel"]
            
        for ball in balls:
            ball["vel"] = min((15 * dt / 1000) + ball["vel"], MAX_VEL)
            ball["pos"] = rotate_point([ball["pos"][0] + ball["vel"], ball["pos"][1]], ball["angle"], ball["pos"])
        
        for wall in walls:
            for ball in balls:
                if get_dist_from_line(np.array(ball["pos"]), np.array(wall)) > -12:
                    ball["angle"] = 2 * get_line_angle(wall[0], wall[1]) - ball["angle"]
                
            for paddle in paddles:
                dist = get_dist_from_line(np.array(paddle["pos"]), np.array(wall))
                if dist > -PADDLE_HEIGHT/2:
                    paddle["pos"] = list(get_intersect(wall[0], wall[1], paddle["pos"], rotate_point((paddle["pos"][0], paddle["pos"][1] + 10), paddle["angle"], paddle["pos"])))
                    pos = list(rotate_point((paddle["pos"][0], paddle["pos"][1] + (dist + (PADDLE_HEIGHT+.1 / 2))), paddle["angle"], paddle["pos"]))
                    neg = list(rotate_point((paddle["pos"][0], paddle["pos"][1] - (dist + (PADDLE_HEIGHT+.1 / 2))), paddle["angle"], paddle["pos"]))
                    paddle["pos"] = pos if get_dist_from_line(np.array(pos), np.array(wall)) < get_dist_from_line(np.array(neg), np.array(wall)) else neg
                    
                    paddle["vel"] = 0
        
        for paddle in paddles:
            paddle["polygon"] = gen_rect_polygon(paddle["pos"], PADDLE_WIDTH, PADDLE_HEIGHT, paddle["angle"])
        
        for ball in balls:
            for paddle in paddles:
                center = paddle["pos"]
                paddle_front = np.array(paddle["polygon"][1:3])
                
                if abs(get_dist_from_line_segment(np.array(ball["pos"]), paddle_front)) < 12:
                    ball["angle"] = 2 * get_line_angle(paddle["pos"], rotate_point((paddle["pos"][0], paddle["pos"][1] + 10), paddle["angle"], paddle["pos"])) - ball["angle"]
        
        if breakFlag:
            break
            
        for paddle in paddles:
            pg.draw.polygon(screen, "white", paddle["polygon"])
        for ball in balls:
            pg.draw.circle(screen, "white", tuple(ball["pos"]), 12)
        
        pg.display.update()

    pg.quit()