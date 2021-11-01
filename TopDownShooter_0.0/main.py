from math import pi
import pygame
import keyboard
from random import randint, uniform, choice
from time import time, sleep
from numpy import exp, sin, cos, tan, arctan, arctan2
from pygame.version import SDL, SDLVersion
from thread6 import run_threaded
import threading
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
YELLOW = (255, 255, 0)
DEFAULTFONT = pygame.font.SysFont('Comic Sans MS', 30) #430
COMICFONT = pygame.font.Font("res/Font Styles/BADABB__.TTF", 530)
WIDTH = 1440
HEIGHT = 720
SOUNDON = True
SHOOTWORDS = ["BOOOOM!", "SPLAAASH!", "POOOOOF!"]
COMBOWORDS = ["Good combo!", "Nice!", "bloodthirsty!", "ruthless killer!", "Daemon!", "God of War!"]
MAXFPS = 60
fps = 60 
#Gameplay Variables
GAMEBULLETS = 30
PREEXP = 1
PREEXPMUL = 2
LINEAR = 30
SHOOTFREQUENCY = 0.1 #Second per shot
BULLETPERSHOT = 1
COLORCHANGEDURATION = 0.07
PLAYERSPEED = 1000
moveX,moveY = 0,0           #Taking -1, 0, or 1 as values of player Move
BULLETDAMAGE = 10
BULLETSCALE = 10
BULLETSPD = 1000
ennemy1Spd = 1000

shootFrequency = 0
minPercent = 0
maxPercent = 0   #For shooting randomness

ennemyMove = 50
pushForce = 20      #Number of pixels of moving when touched by a bullet

transitionTime = 0.2

comboTime = 1.5   #Time after which you cannot continue your combo
#Init clock for fps
clock = pygame.time.Clock() 
#Draw dictionary
drawDic = {
    0:[],
    1:[],
    2:[],
    3:[],
    4:[],
    5:[],
    6:[],
    7:[],
}
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
    
    def Draw(self, screen, order, camCoord:tuple = (0,0)):
        if order >= 0:
            if order not in drawDic:
                order = max(drawDic)+1
            drawDic[order].append(("c",(screen, self.color, (self.x-camCoord[0], self.y-camCoord[1]), self.scale)))
            
        
            



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
    def __init__(self, x, y, hp, spd, resistance, color, scale, isControlled = True):
        self.x = x
        self.y = y
        self.hp = hp
        self.spd = spd
        self.resistance = resistance
        self.color = color
        self.scale = scale
        self.isControlled = isControlled
    
    def Draw(self, screen, order, camCoord:tuple = (0,0)):
        if order >= 0:
            if order not in drawDic:
                order = max(drawDic)+1
            drawDic[order].append(("c",(screen, self.color, (self.x-camCoord[0], self.y-camCoord[1]), self.scale)))
        
        


class Ennemy:
    def __init__(self, x, y, hp, spd, dmg, scale, resistance, color = RED, isAlive = False, canDodge = False):
        self.x = x
        self.y = y
        self.hp = hp
        self.spd = spd
        self.dmg = dmg
        self.scale = scale
        self.resistance = resistance
        self.isAlive = isAlive
        self.color = color
        self.canDodge = canDodge

        self.colorThread = False

    def Draw(self, screen, order, camCoord:tuple = (0,0)):
        if order >= 0:
            if order not in drawDic:
                order = max(drawDic)+1
            drawDic[order].append(("c",(screen, self.color, (self.x-camCoord[0], self.y-camCoord[1]), self.scale)))
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
    def __init__(self, text, fontPath, fontSize, position = (0,0),color = WHITE, alpha = 255, rotation = 0, 
                isBold = False, isItalic = False, isActive = False):
        self.text = text
        self.fontPath = fontPath
        self.fontSize = fontSize
        self.isBold = isBold
        self.isItalic = isItalic
        self.position = position
        self.rotation = rotation                             #In degree, in trigonometric direction
        self.color = color
        self.alpha = alpha
        self.font = pygame.font.Font(fontPath, fontSize)
        self.isActive = isActive
        self.sizeAnimRun, self.rotAnimRun, self.transAnimRun, self.alphaAnimRun = False,False,False,False
        self.animInfos = [[0,0,0,0],[0,0,0,0]]
        self.currentAnimationState = 0

    def Resize(self, newSize):
        if newSize != self.fontSize:
            self.fontSize = int(newSize)
            self.font = pygame.font.Font(self.fontPath, self.fontSize)
    
    def ChangeFont(self,newFontPath, newSize = -1):
        self.fontPath = newFontPath
        if newSize != -1:
            self.fontSize = newSize
        self.font = pygame.font.Font(self.fontPath, self.fontSize)
    
    def UseSysFont(self, newFontPath, newSize):
        fontPath = newFontPath
        if newSize != -1:
            self.fontSize = newSize
        self.font = pygame.font.SysFont(self.fontPath, self.fontSize)
    
    def Display(self, window, antialias = False):
        textSurface = self.font.render(self.text, antialias, self.color)
        if self.rotation != 0:
            textSurface = pygame.transform.rotate(textSurface, self.rotation)
        textSurface.set_alpha(self.alpha)
        window.blit(textSurface, self.position)




class TextManager:
    def __init__(self, tempTxtCapacity, permTxtCapacity):
        '''The logic here is that there is "permanent" and temporary text buffer, permanent text buffer is dialogues one for example or tutorial
        text, this buffer does not change to do another thing. Meanwhile, temporary buffer text changes continually;it may be used to show a score
        bonus when carachter kills an ennemy for example
        '''
        self.tempTxtPool = []
        self.permText = []
        self.curTempIndex = 0   #Current temp index

        for i in range(tempTxtCapacity):
            self.tempTxtPool.append(Text("","res/Font Styles/BADABB__.TTF", 30, isActive = False))
        for i in range(permTxtCapacity):
            self.permText.append(Text("", "res/Font Styles/Vogue.ttf", 30, isActive = False))

    def activateFreeTxt(self):
        '''
        Make a temp text buffer active and return it's index, is all buffers are busy, it returns -1
        -1 is handled in AnimateText; it means the text would not be animated.
        '''
        for i in range(self.curTempIndex, (l :=len(self.tempTxtPool))):
            if not self.tempTxtPool[i].isActive:
                self.tempTxtPool[i].isActive = True
                self.curTempIndex = i + 1
                if self.curTempIndex>l-1:
                    self.curTempIndex = 0
                return i
        for i in range(self.curTempIndex):
            if not self.tempTxtPool[i].isActive:
                self.tempTxtPool[i].isActive = True
                self.curTempIndex = i + 1
                # if self.curTempIndex>l-1:
                #     self.curTempIndex = 0    
                return i
        return -1
        
    def AnimateText(self, targetedList, index, animationState = 0, sTransPos = -1, sTransPosY = -1, eTransPosY = -1,
                    sSize = -1, eSize = -1, sAlpha = -1, eAlpha = -1, alphaTime = 1,
                    eTransPos = -1 ,sRotPos = -1, sRotAngle =-1, eRotAngle = -1, 
                    rotTime = 1, transTime = 1, sizeTime = 1, endTxtOff = -1):
        '''
        Interpolate between two states, linearly for now. "e" stands for end, meanwhile "s" stands for start.
        SHOULD BE RAN AS THREAD!
        '''
        #TODO: Add other interpolation styles like exponential one
        deltaTime = 1/fps
        deltaSize = deltaTime*(eSize - sSize)/sizeTime
        deltaAngle = deltaTime*(eRotAngle - sRotAngle)/rotTime
        deltaTrans = deltaTime*(eTransPos - sTransPos)/transTime
        deltaTransY = deltaTime*(eTransPosY - sTransPosY)/transTime
        deltaAlpha = deltaTime*(eAlpha - sAlpha)/alphaTime
        sizeSteps, rotSteps, transSteps, alphaSteps = int(sizeTime/deltaTime), int(rotTime/deltaTime), int(transTime/deltaTime), int(alphaTime/deltaTime)
        def transAnimation():
            targetedList[index].transAnimRun = True
            targetedList[index].position = (sTransPos, sTransPosY)
            for i in range(transSteps):
                targetedList[index].position = (sTransPos+i*deltaTrans, sTransPosY + i*deltaTransY)
                sleep(deltaTime)
                if targetedList[index].animInfos[animationState] == [1,1,1,1]: return
            
            targetedList[index].position = (eTransPos, eTransPosY)
            targetedList[index].transAnimRun = False

            if (t:=targetedList[index]).sizeAnimRun + t.rotAnimRun + t.transAnimRun + t.alphaAnimRun == 0:
                if endTxtOff != -1:
                    sleep(endTxtOff)
                    if targetedList[index].animInfos[animationState] == [1,1,1,1]: return
                    targetedList[index].isActive = False

        #TODO: Fix this rotation which sucks
        def rotAnimation():
            targetedList[index].rotAnimRun = True
            targetedList[index].rotation = sRotAngle
            for i in range(sizeSteps):
                targetedList[index].rotation = sRotAngle + i*deltaAngle
                sleep(deltaTime)
                if targetedList[index].animInfos[animationState] == [1,1,1,1]:
                    return

            targetedList[index].rotation = eRotAngle
            targetedList[index].rotAnimRun = False

            if (t:=targetedList[index]).sizeAnimRun + t.rotAnimRun + t.transAnimRun + t.alphaAnimRun == 0:
                if endTxtOff != -1:
                    sleep(endTxtOff)
                    if targetedList[index].animInfos[animationState] == [1,1,1,1]:
                         return
                    targetedList[index].isActive = False


        def sizeAnimation():
            targetedList[index].sizeAnimRun = True
            targetedList[index].Resize(sSize)
            for i in range(sizeSteps):
                targetedList[index].Resize(sSize + i*deltaSize)
                sleep(deltaTime)
                if targetedList[index].animInfos[animationState] == [1,1,1,1]: return

            targetedList[index].Resize(eSize)
            targetedList[index].sizeAnimRun = False

            if(t:=targetedList[index]).sizeAnimRun + t.rotAnimRun + t.transAnimRun + t.alphaAnimRun == 0:
                if endTxtOff != -1:
                    sleep(endTxtOff)
                    if targetedList[index].animInfos[animationState] == [1,1,1,1]: return
                    targetedList[index].isActive = False
        

        def alphaAnimation():
            targetedList[index].alphaAnimRun = True
            targetedList[index].alpha = sAlpha
            for i in range(alphaSteps):
                targetedList[index].alpha = sAlpha + i*deltaAlpha
                sleep(deltaTime)
                if targetedList[index].animInfos[animationState] == [1,1,1,1]: return

            targetedList[index].alpha = eAlpha
            targetedList[index].alphaAnimRun = False
            if(t:=targetedList[index]).sizeAnimRun + t.rotAnimRun + t.transAnimRun + t.alphaAnimRun == 0:
                if endTxtOff != -1:
                    sleep(endTxtOff)
                    if targetedList[index].animInfos[animationState] == [1,1,1,1]: return
                    targetedList[index].isActive = False


        if index != -1:
            if sTransPos != -1:
                run_threaded(transAnimation)
            if sRotAngle != -1:
                run_threaded(rotAnimation)
            if sSize != -1:
                run_threaded(sizeAnimation)
            if sAlpha !=-1:
                run_threaded(alphaAnimation)
            # while (t:=targetedList[index]).sizeAnimRun + t.rotAnimRun + t.transAnimRun != 0:
            #     continue
            #I should pass this while loop to another core as the I slows the thread 
        #The text for now would stay active if all of this threads finish exactly at the same time
        



class Game:
    def __init__(self, width, height, fullScreen = False):
        if fullScreen:
            self.window = pygame.display.set_mode((width, height), flags=pygame.FULLSCREEN)
        else:
            self.window = pygame.display.set_mode((width, height))

    def SetBgColor(self, bgColor):
        self.window.fill(bgColor)




class Camera:
    def __init__(self, nonAttached):
        self.x = 0
        self.y = 0
        self.nonAttached = nonAttached
        self.isMoving = False
    
    def UpdatePosition(self,newX, newY, interpolationTime = 0):
        def interpolate():
            self.isMoving = True
            deltaX = (newX - self.x)/(interpolationTime*fps)
            deltaY = (newY - self.y)/(interpolationTime*fps)
            steps = int(interpolationTime*fps)
            for i in range(steps):
                self.x += deltaX
                self.y += deltaY
                sleep(1/fps)
            self.x = newX
            self.y = newY
            self.isMoving = False
    
        if interpolationTime > 0 and self.isMoving == False:
            run_threaded(interpolate)
        elif interpolationTime <= 0:
            self.x = newX
            self.y = newY




class Wall:
    def __init__(self, x,y, color, halfWidth, halfHeight):
        self.x = x
        self.y = y
        self.color = color
        self.hw = halfWidth
        self.hh = halfHeight
    def Draw(self, screen, order, camCoord:tuple = (0,0)):
        if order >= 0:
            if order not in drawDic:
                order = max(drawDic)+1
            rect = pygame.Rect(self.x-camCoord[0]-self.hw, self.y-camCoord[1]-self.hh, 2*self.hw, 2*self.hh)

            drawDic[order].append(("r",(screen, self.color,rect)))




class LevelManager:
    def __init__(self, x, y):
        self.x = x 
        self.y = y
        self.walls = []




class ScoreManager: 
    def __init__(self):
        self.score = 0
        self.totalHits = 0
        self.totalEnnemiesKilled = 0
        self.highestScore = 0

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
player = Player(20,20, 10,PLAYERSPEED, 3, WHITE, 20)
ennemyManager = EnnemyManager(1, 500, 500, areAlive=True)
bulletManager = BulletManager(GAMEBULLETS)
imaginaryBulletManager= BulletManager(GAMEBULLETS, scale = BULLETSCALE) #Maybe temporary solution I don't know how much this is optimized
textManager = TextManager(20,1)
game = Game(WIDTH, HEIGHT)
levelManager = LevelManager(0,0)
levelManager.walls = [Wall(1440/2,700, BLUE, 1440/2,20), 
                      Wall(1420, 350, BLUE, 20, 300)]

scoreManager = ScoreManager()
#Init info arrays
#I sound out that class objects are passed by reference to an array, it allows me to do a lot of abstraction
staticObjects = []
dynamicObjects = [player, ennemyManager.pool]
attachedToCam = [textManager.permText]
nonAttachedToCam = [player, ennemyManager.pool]

cam = Camera(nonAttachedToCam)

forbidden = (None,None,None,None)
#Update and game logic
running = True
while running:
    drawDic = {
        0:[],
        1:[],
        2:[],
        3:[],
        4:[],
        5:[],
        6:[],
        7:[],
    }
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


    #Setting background color
    game.SetBgColor(BLACK)
    #Getting move inputs
    moveX = (keyboard.is_pressed("right") or keyboard.is_pressed("D")) - (keyboard.is_pressed("left") or keyboard.is_pressed("Q"))*player.isControlled
    moveY = (keyboard.is_pressed("down") or keyboard.is_pressed("S"))- (keyboard.is_pressed("up") or keyboard.is_pressed("Z"))*player.isControlled
    # if (player.x, player.y, moveX,moveY) == forbidden:
    #     moveX,moveY = 0,0     Extra collision handler
    #Calculating shoot direction 
    mousePos = pygame.mouse.get_pos() #Gives a couple x,y
    mousePos = (mousePos[0]+cam.x, mousePos[1]+cam.y)
    bulletDirection = (mousePos[0] - player.x, mousePos[1] - player.y)
    bulletDirection = NormalizeVect(bulletDirection)
    #Move player
    player.x += moveX*player.spd/fps
    player.y += moveY*player.spd/fps
    #Handle player collision
    for wall in levelManager.walls:
        wall.Draw(game.window, 0, (cam.x,cam.y))
        if moveX != 0 or moveY != 0:
            playerMinX = player.x - player.scale
            playerMaxX = player.x + player.scale
            playerMinY,playerMaxY = player.y - player.scale, player.y + player.scale
            wallMinX,wallMaxX = wall.x - wall.hw, wall.x+wall.hw
            wallMinY, wallMaxY = wall.y - wall.hh, wall.y+wall.hh
            overlap = 0
            if (playerMinX < wallMinX) and playerMinX<wallMinX<playerMaxX:
                overlap += 1
            elif ( wallMinX < playerMinX ) and wallMinX<playerMinX<wallMaxX:
                overlap += 1
            if (playerMinY < wallMinY) and playerMinY<wallMinY<playerMaxY:
                overlap += 1
            elif (  wallMinY < playerMinY ) and wallMinY<playerMinY<wallMaxY:
                overlap += 1
            if overlap ==2:
                movX, movY = moveX, moveY
                moveX, moveY = 0,0
                while True:
                    playerMinX = player.x - player.scale
                    playerMaxX = player.x + player.scale
                    playerMinY,playerMaxY = player.y - player.scale, player.y + player.scale
                    wallMinX,wallMaxX = wall.x - wall.hw, wall.x+wall.hw
                    wallMinY, wallMaxY = wall.y - wall.hh, wall.y+wall.hh
                    overlap = 0
                    if (playerMinX < wallMinX) and playerMinX<wallMinX<playerMaxX:
                        overlap += 1
                    elif (  wallMinX < playerMinX ) and wallMinX<playerMinX<wallMaxX:
                        overlap += 1
                    if (playerMinY < wallMinY) and playerMinY<wallMinY<playerMaxY:
                        overlap += 1
                    elif (  wallMinY < playerMinY ) and wallMinY<playerMinY<wallMaxY:
                        overlap += 1
                    player.x -=2*movX
                    player.y -=2*movY
                    moveX, moveY = 0,0
                    if overlap != 2:
                        # forbidden = (player.x, player.y, movX,movY)
                        break
    #Drawing the player
    player.Draw(game.window, 1,(cam.x, cam.y))
    #Update Camera when player crosses level bounderies
    
    if (player.x >= cam.x + WIDTH) and not cam.isMoving:  #RIGHT BOUNDARY
        player.x += 1
        cam.UpdatePosition(cam.x + WIDTH, cam.y, transitionTime)
    elif (player.x <= cam.x) and not cam.isMoving:          #LEFT BOUNDARY
        player.x -= 1
        cam.UpdatePosition(cam.x - WIDTH, cam.y, transitionTime)
    elif (player.y <= cam.y)and not cam.isMoving:         #TOP BOUNDARY
        player.y -= 1
        cam.UpdatePosition(cam.x, cam.y - HEIGHT, transitionTime)          
    elif (player.y >= cam.y + HEIGHT) and not cam.isMoving:       #DOWN BOUNDARY
        player.y += 1
        cam.UpdatePosition(cam.x, cam.y + HEIGHT, transitionTime)
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
                    #Hit text effect and score
                    scoreManager.score +=1
                    score= scoreManager.score
                    highest = scoreManager.highestScore
                    scoreManager.highestScore = scoreManager.score if highest < scoreManager.score else highest
                    #TODO:Fix this mess about killing a thread, make it more general
                    anim = textManager.permText[0].currentAnimationState
                    textManager.permText[0].currentAnimationState = 1-anim
                    textManager.permText[0].alphaAnimRun = False
                    (textManager.permText[0].animInfos)[anim] = [1,1,1,1]
                    (textManager.permText[0].animInfos)[1-anim] = [0,0,0,0]
                    textManager.permText[0].ChangeFont("res/Font Styles/Alice_in_Wonderland_3.TTF", 45)
                    
                    if 0<score<10:
                        comboWord = ""
                    elif 10<=score<20:
                        comboWord = COMBOWORDS[0]
                    elif 20<=score<40:
                        comboWord = COMBOWORDS[1]
                    elif 40<=score<80:
                        comboWord = COMBOWORDS[2]
                    elif 80<=score<150:
                        comboWord = COMBOWORDS[3]
                    elif 150<=score<300:
                        comboWord = COMBOWORDS[4]
                    elif 300<=score<500:
                        comboWord = COMBOWORDS[5]

                    textManager.permText[0].text = "+ {} {}".format(scoreManager.score, comboWord)
                    textManager.permText[0].rotation = randint(-10,10)
                    pos = (1100,350)
                    if player.x-cam.x > WIDTH/2:
                        pos = (30, 350) 
                    textManager.permText[0].position = pos
                    textManager.permText[0].color = RED
                    textManager.permText[0].isActive = True
                    textManager.AnimateText(textManager.permText, 0, animationState=1-anim, sAlpha = 255, eAlpha = 0, alphaTime= comboTime, endTxtOff=0)
                    #Colorize the ennemy
                    if not  ennemyManager.pool[i].colorThread:
                        ennemyManager.pool[i].colorThread = True
                        run_threaded(ennemyManager.pool[i].ChangeColor, ennemyManager.pool[i].color, COLORCHANGEDURATION)
                        ennemyManager.pool[i].color = WHITE
                    #Pushing the ennemy
                    ennemyManager.pool[i].x += bullet.direction[0]*pushForce
                    ennemyManager.pool[i].y += bullet.direction[1]*pushForce
            bullet.Draw(game.window, 2, (cam.x, cam.y))
    #Renitialize score
    if not textManager.permText[0].isActive:
        scoreManager.score = 0
    for bullet in imaginaryBulletManager.pool:
        if bullet.isActive:
            bullet.x += (bullet.direction[0]*bullet.spd*(PREEXP + PREEXPMUL*exp(-abs(bullet.initialX-bullet.x)/LINEAR)))/fps
            bullet.y += (bullet.direction[1]*bullet.spd*(PREEXP + PREEXPMUL*exp(-abs(bullet.initialY-bullet.y)/LINEAR)))/fps
            bullet.lifeTime -= 1/fps
            if bullet.lifeTime<=0:
                    bullet.lifeTime = bullet.constLT
                    bullet.isActive = False
            for i in range(len(ennemyManager.pool)):
                ennemy = ennemyManager.pool[i]
                if ennemy.canDodge and (CalculateMagnitude((abs(ennemy.x - bullet.x), abs(ennemy.y - bullet.y))) <= ennemy.scale + bullet.scale) and bullet.shotByPlayer:
                    bullet.lifeTime = bullet.constLT
                    bullet.isActive = False
                    by = choice([-1,1])
                    newVect = (0,0)
                    if bulletDirection[1] < 0.01:
                        newVect = (0,1)
                    elif bulletDirection[0] < 0.01:
                        newVect = (1,0)
                    else:
                        newVect = NormalizeVect((-bullet.direction[1]*by/bullet.direction[0],by))
                    ennemy.x += newVect[0]*ennemyMove
                    ennemy.y  += newVect[1]*ennemyMove
        pass

    #Ennemies rendering and their behaviour
    for ennemy in ennemyManager.pool:
        if ennemy.isAlive:
            ennemy.Draw(game.window, 0, (cam.x, cam.y))
    
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
          

            index = textManager.activateFreeTxt()
            textManager.tempTxtPool[index].text = ""
            textManager.tempTxtPool[index].ChangeFont(choice(["res/Font Styles/BADABB__.TTF", "res/Font Styles/Cocola.ttf", "res/Font Styles/Fresh Lychee.ttf"]))
            textManager.tempTxtPool[index].rotation = randint(-45,45)
            textManager.tempTxtPool[index].text = choice(SHOOTWORDS)
            textManager.tempTxtPool[index].color = (255,randint(0,255), 0)
            run_threaded(textManager.AnimateText, textManager.tempTxtPool, index,sTransPos = player.x-cam.x, eTransPos = player.x-cam.x + randint(-80,80), 
                                    eTransPosY = player.y-cam.y + randint(-80,80), sTransPosY = player.y-cam.y, sAlpha = 255, eAlpha = 0, alphaTime=0.5,
                                    transTime = 0.1, endTxtOff = 0.5, sSize= 0, eSize = randint(20,40), sizeTime = 0.1)

    for key in drawDic:
        for args in drawDic[key]:
            if args[0] == "c":
              pygame.draw.circle(*args[1]) #For know there are just circles
            if args[0] == "r":
              pygame.draw.rect(*args[1])

    #Drawing temporary text
    for i in range(len(textManager.tempTxtPool)):
        if textManager.tempTxtPool[i].isActive:
            textManager.tempTxtPool[i].Display(game.window, antialias = True)
    #Drawing permanent text
    for i in range(len(textManager.permText)):
        if textManager.permText[i].isActive:
            textManager.permText[i].Display(game.window, antialias = True)

    #Display fps:
    game.window.blit(DEFAULTFONT.render(str(fps),False, BLUE), (0,0))
    #Updating shapes
    pygame.display.flip()
    #Calculating fps
    fps = int(clock.get_fps())
    clock.tick(MAXFPS)
    if fps < 5:
        fps = 60
    #Updating time variables
    shootFrequency = max(0, shootFrequency - 1/fps)


pygame.quit()