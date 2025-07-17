from PongLib import *
import pygame as pg
import numpy as np
import random, os

pg.init()

# USER VARIABLES!!!
# Note: There are some user vars in Shapes.py

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

PADDLE_HEIGHT = 100
PADDLE_WIDTH = 10

BALL_RADIUS = 12
NUMBER_BALLS = 1 # Somehow, yes, this does work

# END OF USER VARIABLES!!!

# Idea; Chaos pong: 2 pong balls, going different directions; 4 players

def distance_point_line(pt: pg.Vector2, l1: pg.Vector2, l2: pg.Vector2):
    return abs(pg.Vector2(l1[1] - l2[1], l2[0] - l1[0]).normalize().dot(pt - l1))

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
    
    return (x/z, y/z)
# End of code snippet!

def game(screen: pg.Surface, clock: pg.time.Clock):
    w, h = screen.get_width(), screen.get_height()
    
    paddles = [
        Paddle(pg.Rect(50, (h / 2) - (PADDLE_HEIGHT / 2), PADDLE_WIDTH, PADDLE_HEIGHT)),
        Paddle(pg.Rect(w - (50 + PADDLE_WIDTH), (h / 2) - (PADDLE_HEIGHT / 2), PADDLE_WIDTH, PADDLE_HEIGHT), flip=True)
    ]
    
    bots = [1] # For use later, when I eventually get more than 2 paddles working properly
    # The goal is to dynamically create a shape that works with whatever number of paddles is set, then create some control scheme that works with all of those paddles
    # (I'll probable just add controller support and do 1 paddle per controller)
    
    balls = [Ball(pg.math.Vector2(w/2, h/2), 12, 5, random.randrange(30, 150, 5) * (-1 if random.randint(0, 1) else 1)) for i in range(NUMBER_BALLS)]
    
    keyDict = {}
    
    p1ScoreDisp = TextBox(pg.font.Font(None, 60), str(0), pg.Vector2(80, 50), box_color=pg.Color("Black"))
    p2ScoreDisp = TextBox(pg.font.Font(None, 60), str(0), pg.Vector2(w-80, 50), box_color=pg.Color("Black"))
    p1Score = 0
    p2Score = 0

    while True:
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
        
        for i in range(len(paddles)):
            if i not in bots:
                paddles[i].update(screen, keyDict, dt)
            
        for botNum in bots:
            paddle = paddles[botNum]
            
            closest = {"ball": balls[0], "dist": np.inf}
            for ball in balls:
                dist = distance_point_line(ball.getCenter(), paddle.getRect().midtop, paddle.getRect().midbottom)
                newdist = distance_point_line(ball.getCenter() + ball.getTrajectory(), paddle.getRect().midtop, paddle.getRect().midbottom)
                if dist < closest["dist"] and dist > newdist:
                    closest = {"ball": ball, "dist": dist}
            
            ball = closest["ball"]

            target = get_intersect(paddle.getRect().midtop, paddle.getRect().midbottom, ball.getCenter(), ball.getCenter() + ball.getTrajectory())
            if target[1] + (PADDLE_HEIGHT/3) < paddle.getRect().centery:
                paddle.update(screen, {"w": 0}, dt)
            elif target[1] - (PADDLE_HEIGHT/3) > paddle.getRect().centery:
                paddle.update(screen, {"s": 0}, dt)
            else:
                paddle.update(screen, {}, dt)
            
        for ball in balls:
            for paddle in paddles:
                ball.collidepaddle(screen, paddle)
            
            clampRect = screen.get_rect().inflate(-24, -24)
            if max(clampRect.top, min(clampRect.bottom, ball.getCenter().y)) != ball.getCenter().y:
                ball.setTrajectory(ball.getTrajectory().reflect((0, 1)))
            
            elif min(clampRect.right, ball.getCenter().x) != ball.getCenter().x:
                p1Score += 1
                ball.setCenter(pg.math.Vector2(w/2, h/2))
                ball.setTrajectory(pg.math.Vector2(0, 5).rotate(random.randrange(30, 150, 5) * (-1 if random.randint(0, 1) else 1)))
            elif max(clampRect.left, min(clampRect.right, ball.getCenter().x)) != ball.getCenter().x:
                p2Score += 1
                ball.setCenter(pg.math.Vector2(w/2, h/2))
                ball.setTrajectory(pg.math.Vector2(0, 5).rotate(random.randrange(30, 150, 5) * (-1 if random.randint(0, 1) else 1)))

            ball.update(dt)
        
        if breakFlag:
            break
            
        screen.fill("black")
        for paddle in paddles:
            paddle.draw(screen, "white")
        for ball in balls:
            ball.draw(screen, "white")
        
        p1ScoreDisp.setText(str(p1Score))
        p2ScoreDisp.setText(str(p2Score))
        
        p1ScoreDisp.draw(screen)
        p2ScoreDisp.draw(screen)
        
        pg.display.update()
        
    return p1Score, p2Score
    
def mainMenu(screen: pg.Surface, clock: pg.time.Clock):
    w, h = screen.get_width(), screen.get_height()
    nameInput = TextInput(pg.font.Font(None, 32), "NAME", pg.Vector2(w/2, (h/2) - 20))
    startButton = Button(pg.font.Font(None, 32), "START", pg.Vector2(w/2, h/2 + 20))
    
    breakFlag = False
    name = None

    while True:
        dt = clock.tick(60)

        for event in pg.event.get():
            nameInput.handle_event(event)
            startButton.handle_event(event)
            
            match event.type:
                case pg.QUIT:
                    breakFlag = True
                case pg.KEYDOWN:
                    if event.dict['unicode'] == '\x1b':
                        breakFlag = True
        
        if breakFlag:
            break
        
        if startButton.getPressed():
            name = nameInput.getText() if nameInput.getText() != "" else "Player1"
            break
            
        screen.fill("black")
        nameInput.draw(screen)
        startButton.draw(screen)
        
        pg.display.update()
        
    return name

def saveScreen(screen: pg.Surface, clock: pg.time.Clock, name: str, p1Score: int, p2Score: int):
    w, h = screen.get_width(), screen.get_height()
    nameInput = TextBox(pg.font.Font(None, 32), "Would you like to save your score?", pg.Vector2(w/2, (h/2) - 20), box_color=pg.Color("black"))
    
    yes = Button(pg.font.Font(None, 32), "YES", pg.Vector2(w/2, h/2 + 20))
    yes._rect.midright = yes._rect.center - pg.Vector2(5, 0)
    
    no = Button(pg.font.Font(None, 32), "NO", pg.Vector2(w/2, h/2 + 20))
    no._rect.midleft = no._rect.center + pg.Vector2(5, 0)
    
    breakFlag = False

    while True:
        dt = clock.tick(60)

        for event in pg.event.get():
            yes.handle_event(event)
            no.handle_event(event)
            
            match event.type:
                case pg.QUIT:
                    breakFlag = True
                case pg.KEYDOWN:
                    if event.dict['unicode'] == '\x1b':
                        breakFlag = True
        
        if breakFlag or no.getPressed():
            break
        
        if yes.getPressed():
            if not os.path.exists("leaderboard.csv"):
                with open("leaderboard.csv", "w") as file:
                    file.write("name,P1Score,P2Score,P1/P2")
            with open("leaderboard.csv", "a") as file:
                file.write(f"\n{name},{p1Score},{p2Score},{p1Score/p2Score if (p1Score != 0 and p2Score != 0) else 0}")
            break
            
        screen.fill("black")
        nameInput.draw(screen)
        yes.draw(screen)
        no.draw(screen)
        
        pg.display.update()
        
    return name

if __name__ == "__main__":
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pg.time.Clock()
    
    name = mainMenu(screen, clock)
    if name is not None:
        p1, p2 = game(screen, clock)
        saveScreen(screen, clock, name, p1, p2)

    pg.quit()