from math import pi
from re import X
import pygame
import keyboard
from random import randint, uniform
from random import choice
from time import time, sleep
from numpy import exp, sin, cos, tan, arctan, arctan2
from thread6 import run_threaded
from datetime import datetime

#Init Pygame
pygame.font.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(40)


#Loading ressources
shotSound = pygame.mixer.Sound('res/Laser7.wav')
hitSound = pygame.mixer.Sound('res/Hit.wav')

#Const and global variables
WHITE = (255,255,255)
ORANGE = (255,165,0)
RED = (255, 0, 0)
BLUE = (0,0,255)
BLACK = (0,0,0)
DEFAULTFONT = pygame.font.SysFont('Comic Sans MS', 30) #430
COMICFONT = pygame.font.Font("res/Font Styles/BADABB__.TTF", 530)
WIDTH = 1440
HEIGHT = 720
SOUNDON = False
fps = 60 
#Gameplay Variables
GAMEBULLETS = 30
PREEXP = 1
PREEXPMUL = 2
LINEAR = 30
SHOOTFREQUENCY = 0.1 #Second per shot
BULLETPERSHOT = 6
COLORCHANGEDURATION = 0.07
PLAYERSPEED = 600
BULLETDAMAGE = 10
BULLETSCALE = 5
BULLETSPD = 1000
ennemy1Spd = 1000

shootFrequency = 0
minPercent = 2
maxPercent = 15   #For shooting randomness

ennemyMove = 50
pushForce = 20
#Class Definition



class Bullet:
    def __init__(self, x, y, spd, dmg, direction, 
                scale = 1, color = WHITE, constLt = 10, isActive = False,  
                shotByPlayer = False):
        #If the variable shotByPlayer is False it means the bullet should hit the player
        self.x = x
        self.y = y
        self.spd = spd
        self.dmg = dmg
        self.color = color
        self.scale = scale
        self.constLT = constLt
        self.lifeTime = constLt #How much time before the bullet disappears (in seconds here TODO: Add distance lifetime)
        self.isActive = isActive
        self.direction = direction
        self.initialX, self.initialY = 0,0 #Newly added to handle exponential speed
    
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.scale)





class BulletManager:
    def __init__(self, capacity, x = 0, y = 0, spd = 0, dmg = 0, scale = 1, color = WHITE):
        self.pool = []
        self.current = 0
        self.capacity = capacity
        for i in range(capacity):
            self.pool.append(Bullet(x, y, spd = spd, dmg = dmg, direction = (0,0), scale = scale, color = color)) #Instatiate pool object where there is all balls
        
    def Instantiate(self, x, y, spd, dmg, scale, color, direction, shotByPlayer): #Instatiate a FREE ball
        (self.pool[self.current]).isActive = True 
        (self.pool[self.current]).x = x 
        (self.pool[self.current]).y = y
        (self.pool[self.current]).initialX = x
        (self.pool[self.current]).initialY = y
        (self.pool[self.current]).spd = spd
        (self.pool[self.current]).dmg = dmg
        (self.pool[self.current]).scale = scale
        (self.pool[self.current]).color = color
        (self.pool[self.current]).direction = direction
        (self.pool[self.current]).shotByPlayer = shotByPlayer
        (self.pool[self.current]).lifeTime = (self.pool[self.current]).constLT

        self.current +=1
        if self.current >= self.capacity:
            self.current = 0

        

class Player:
    def __init__(self, x, y, hp, spd, resistance, color, scale):
        self.x = x
        self.y = y
        self.hp = hp
        self.spd = spd
        self.resistance = resistance
        self.color = color
        self.scale = scale
    
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.scale)
        
        

class Ennemy:
    def __init__(self, x, y, hp, spd, dmg, scale, resistance, color = RED, isAlive = False):
        self.x = x
        self.y = y
        self.hp = hp
        self.spd = spd
        self.dmg = dmg
        self.scale = scale
        self.resistance = resistance
        self.isAlive = isAlive
        self.color = color

        self.colorThread = False

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.scale)

    def ChangeColor(self, color, time):
        sleep(time)
        self.color = color
        self.colorThread = False
    

class EnnemyManager:
    def __init__(self, number, x = 0, y = 0, hp = 100, spd = 0, dmg = 0, resistance = 0, scale = 20, color = RED, areAlive = False):
        self.pool = []
        self.number = number
        self.current = 0
        for i in range(number):
            self.pool.append(Ennemy(x, y, hp, dmg = dmg, spd = spd, resistance = resistance, 
                                    scale = scale, color = color, isAlive=areAlive))
    
    def Instantiate(self, x, y, hp, spd, dmg, resistance, scale, color):
        (self.pool[self.current]).isAlive = True
        (self.pool[self.current]).x = x
        (self.pool[self.current]).y = y
        (self.pool[self.current]).hp = hp
        (self.pool[self.current]).spd = spd
        (self.pool[self.current]).dmg = dmg
        (self.pool[self.current]).resistance = resistance
        (self.pool[self.current]).scale = scale
        (self.pool[self.current]).color = color
        self.current += 1
        if self.current > self.number:
            self.current = 0



class Text:
    def __init__(self, text, fontPath, fontSize, position = (0,0),color = WHITE, rotation = 0, isBold = False, isItalic = False):
        self.text = text
        self.fontPath = fontPath
        self.fontSize = fontSize
        self.isBold = isBold
        self.isItalic = isItalic
        self.position = position
        self.rotation = rotation                             #In degree, in trigonometric direction
        self.color = color
        self.font = pygame.font.Font(fontPath, fontSize)

    def Resize(self,newSize):
        if newSize != self.fontSize:
            self.font = pygame.font.Font(self.fontPath, newSize)
    
    def Display(self, window, antialias = False):
        textSurface = self.font.render(self.text, antialias, self.color)
        if self.rotation != 0:
            textSurface = pygame.transform.rotate(textSurface)
        window.blit(textSurface, self.position)
        


class Game:
    def __init__(self, width, height):
        self.window = pygame.display.set_mode((width, height))
    def SetBgColor(self, bgColor):
        self.window.fill(bgColor)
clock = pygame.time.Clock()

#Useful functions
def clamp(minn, maxx, value):
    return max(minn, min(value, maxx))

def CalculateMagnitude(couple):
    return (couple[0]**2+couple[1]**2)**0.5

def NormalizeVect(vect):
    if len(vect) == 2:
        x = vect[0]/CalculateMagnitude(vect)
        y = vect[1]/CalculateMagnitude(vect)
        return (x,y)
#------------------




#Init class objects

player = Player(20,20, 10,PLAYERSPEED, 3, ORANGE, 20)
ennemyManager = EnnemyManager(1, 500, 500, areAlive=True)
bulletManager = BulletManager(GAMEBULLETS)
imaginaryBulletManager= BulletManager(GAMEBULLETS) #Maybe temporary solution I don't know how much this is optimized
t = Text("Comic style","res/Font Styles/BADABB__.TTF", 40)

moveX,moveY = 0,0           #Taking -1, 0, or 1 as values of player Move
game = Game(WIDTH, HEIGHT)
running = 1



#Update and game logic
while running:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    #Setting background color
    game.SetBgColor(BLACK)
    #Getting move inputs
    moveX = (keyboard.is_pressed("right") or keyboard.is_pressed("D")) - (keyboard.is_pressed("left") or keyboard.is_pressed("Q"))
    moveY = (keyboard.is_pressed("down") or keyboard.is_pressed("S"))- (keyboard.is_pressed("up") or keyboard.is_pressed("Z"))
    #Calculating shoot direction 
    mousePos = pygame.mouse.get_pos() #Gives a couple x,y
    bulletDirection = (mousePos[0] - player.x, mousePos[1] - player.y)
    magn = CalculateMagnitude(bulletDirection)
    bulletDirection = (bulletDirection[0]/magn, bulletDirection[1]/magn)   #Normalized TODO: Make this in function

    #Move player
    player.x += moveX*player.spd/fps
    player.y += moveY*player.spd/fps
    player.draw(game.window)
    #Updating bullets
    for bullet in bulletManager.pool:
        if bullet.isActive:
            bullet.x += (bullet.direction[0]*bullet.spd*(PREEXP + PREEXPMUL*exp(-abs(bullet.initialX-bullet.x)/LINEAR)))/fps
            bullet.y += (bullet.direction[1]*bullet.spd*(PREEXP + PREEXPMUL*exp(-abs(bullet.initialY-bullet.y)/LINEAR)))/fps
            bullet.lifeTime -= 1/fps
            if bullet.lifeTime<=0:
                 bullet.lifeTime = bullet.constLT
                 bullet.isActive = False
            for i in range(len(ennemyManager.pool)):
                ennemy = ennemyManager.pool[i]
                if (CalculateMagnitude((abs(ennemy.x - bullet.x), abs(ennemy.y - bullet.y))) <= ennemy.scale + bullet.scale) and bullet.shotByPlayer:
                    bullet.lifeTime = bullet.constLT
                    bullet.isActive = False
                    hitSound.play()
                    if not  ennemyManager.pool[i].colorThread:
                        ennemyManager.pool[i].colorThread = True
                        run_threaded(ennemyManager.pool[i].ChangeColor, ennemyManager.pool[i].color, COLORCHANGEDURATION)
                        ennemyManager.pool[i].color = WHITE
                    #Pushing the ennemy
                    ennemyManager.pool[i].x += bullet.direction[0]*pushForce
                    ennemyManager.pool[i].y += bullet.direction[1]*pushForce
            bullet.draw(game.window)

    for bullet in imaginaryBulletManager.pool:
        if bullet.isActive:
            bullet.x += (bullet.direction[0]*bullet.spd*(PREEXP + PREEXPMUL*exp(-abs(bullet.initialX-bullet.x)/LINEAR)))/fps
            bullet.y += (bullet.direction[1]*bullet.spd*(PREEXP + PREEXPMUL*exp(-abs(bullet.initialY-bullet.y)/LINEAR)))/fps
            bullet.lifeTime -= 1/fps
            if bullet.lifeTime<=0:
                    bullet.lifeTime = bullet.constLT
                    bullet.isActive = False
            # for i in range(len(ennemyManager.pool)):
            #     ennemy = ennemyManager.pool[i]
            #     if (CalculateMagnitude((abs(ennemy.x - bullet.x), abs(ennemy.y - bullet.y))) <= ennemy.scale + bullet.scale) and bullet.shotByPlayer:
            #         bullet.lifeTime = bullet.constLT
            #         bullet.isActive = False
            #         by = choice([-1,1])
            #         newVect = (0,0)
            #         if bulletDirection[1] < 0.01:
            #             newVect = (0,1)
            #         elif bulletDirection[0] < 0.01:
            #             newVect = (1,0)
            #         else:
            #             newVect = NormalizeVect((-bullet.direction[1]*by/bullet.direction[0],by))
            #         ennemy.x += newVect[0]*ennemyMove
            #         ennemy.y  += newVect[1]*ennemyMove

    #Ennemies rendering and their behaviour
    for ennemy in ennemyManager.pool:
        if ennemy.isAlive:
            ennemy.draw(game.window)
    
    #Player Shoot
    if (pygame.mouse.get_pressed()) == (1,0,0):
        if (shootFrequency == 0):
            shootFrequency = SHOOTFREQUENCY
            for i in range(BULLETPERSHOT):
                #Randomize shot direction
                percent = randint(minPercent, maxPercent)*choice([-1,1])*pi/180
                angle = pi/2
                signX = bulletDirection[0]
                signY = bulletDirection[1]
                if bulletDirection[0]: angle = arctan2(bulletDirection[1],bulletDirection[0])
                bulletDirection = (cos(angle+percent), sin(angle+percent))
                #Instantiate Bullet
                bulletManager.Instantiate(player.x, player.y, spd = BULLETSPD, dmg = BULLETDAMAGE,scale = BULLETSCALE, color = (randint(50,255),
                                        randint(50,255),randint(50,255)), direction = bulletDirection, shotByPlayer = True)

                imaginaryBulletManager.Instantiate(player.x, player.y, spd = BULLETSPD*2, dmg = BULLETDAMAGE,scale = BULLETSCALE, color = (randint(50,255),
                        randint(50,255),randint(50,255)), direction = bulletDirection, shotByPlayer = True)
            if SOUNDON:
                shotSound.play()



    t.Resize(int(abs(40*cos(time()))))
    
    t.Display(game.window)

    #Updating shapes
    pygame.display.flip()
    #Calculating fps
    clock.tick(60)

    #Updating time variables
    shootFrequency = max(0, shootFrequency - 1/fps)






pygame.quit()