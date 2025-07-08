import sys

import pygame as pg

pg.init()

if __name__ == "__main__":
    screen = pg.display.set_mode((800, 600))

    while True:
        breakFlag = False

        for event in pg.event.get():
            match event.type:
                case pg.QUIT:
                    breakFlag = True
                case pg.KEYDOWN:
                    if event.dict['unicode'] == '\x1b':
                        breakFlag = True

        if breakFlag:
            break

        pg.display.update()

    pg.quit()