from math import pi
import pygame
import keyboard
from random import randint, uniform, choice
from time import time, sleep
from numpy import exp, sin, cos, tan, arctan, arctan2
from pygame.constants import BLEND_ADD, BLEND_MULT, BLEND_RGBA_MULT, BLEND_RGBA_SUB
from thread6 import run_threaded
from multiprocessing import Process, Value
import os
import DialogueList

#OS varibale
#os.environ["runningBlend"] = "0"
#Init Pygame
pygame.font.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(40)
pygame.display.init()
#Loading ressources
SHOTSOUND0 = pygame.mixer.Sound('res/Laser7.wav')
PISTOLSHOTSOUND = pygame.mixer.Sound('res/Pistolet Magnum.wav')
PISTOLEQUIPSOUND = pygame.mixer.Sound('res/Pistol Equip1.wav')
hitSound = pygame.mixer.Sound('res/Hit.wav')
#Const and global variables
TEMPTXTANIMBUFF = [0]
COMBOMETERANIMBUFF = [1,2]

WHITE = (255,255,255)
ORANGE = (255,165,0)
RED = (255, 0, 0)
BLUE = (0,0,255)
BLACK = (0,0,0)
YELLOW = (255, 255, 0)
PINK = (255,0,230)
GREEN = (0,255,0)

DEFAULTFONT = pygame.font.SysFont('Comic Sans MS', 30) #430
COMICFONT = pygame.font.Font("res/Font Styles/BADABB__.TTF", 530)
WIDTH = 1440
HEIGHT = 720
SOUNDON = True
SHOOTWORDS = ["BOOOOM!", "SPLAAASH!", "POOOOOF!"]
COMBOWORDS = ["Good combo!", "Nice!", "bloodthirsty!", "ruthless killer!", "Daemon!", "God of War!"]
MAXFPS = 400
fps = 60 
deltaTime = 1/fps
#Gameplay Variables
GAMEBULLETS = 30
COLORCHANGEDURATION = 0.07
PLAYERSPEED = 1000
moveX,moveY = 0,0           #Taking -1, 0, or 1 as values of player Move
ennemy1Spd = 1000

#Light system variables
AMBIENTLIGHT = (20,20,20)
usingLightSystem = True
#-----
ennemyMove = 50
pushForce = 0      #Number of pixels of moving when touched by a bullet
shootFrequency = 0
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
    7:[],}
#Class Definition

class Gun:
    def __init__(self, shootFrequency, bulletPerShot = 1, btSpd = 1000, btDmg = 1, 
                btScale = 10, btColor = WHITE, btLifeTime = 4, btLifeDistance = -1,
                 isOwnerPlayer = True, btPreExpMul=0, btPreExp=1, btLinear=100, minRandom = 0, maxRandom = 0, shotSound = SHOTSOUND0):
        self.shootFrequency = shootFrequency
        self.bulletPerShot = bulletPerShot
        self.minRandom = minRandom
        self.maxRandom = maxRandom
        self.isOwnerPlayer = isOwnerPlayer

        self.btSpd = btSpd
        self.btDmg = btDmg
        self.btColor = btColor
        self.btScale = btScale
        self.btLifeTime = btLifeTime
        self.btLifeDistance = btLifeDistance
        self.btPreExpMul = btPreExpMul
        self.btPreExp = btPreExp
        self.btLinear = btLinear
        self.shotSound = shotSound



class Bullet:
    def __init__(self, x, y, spd, dmg, direction, 
                scale = 1, associatedGun = None, color = WHITE, constLt = 0.5, constLD = -1, isActive = False,  
                shotByPlayer = False, preExpMul = 1, preExp = 1, linear = 1):
        #If the variable shotByPlayer is False it means the bullet should hit the player
        self.x = x
        self.y = y
        self.spd = spd
        self.dmg = dmg
        self.color = color
        self.scale = scale
        self.constLT = constLt
        self.lifeTime = constLt     #How much time before the bullet disappears (in seconds here)
        self.lifeDistance = constLD
        self.isActive = isActive
        self.direction = direction
        self.initialX, self.initialY = 0,0 #Newly added to handle exponential speed
        self.preExp = preExp
        self.preExpMul = preExpMul
        self.linear = linear
    
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
        
    def Instantiate(self, x, y, direction, associatedGun:Gun): #Instatiate a FREE bullet
        bullet = self.pool[self.current]
        bullet.associatedGun = associatedGun
        bullet.shotByPlayer = associatedGun.isOwnerPlayer
        bullet.isActive = True 
        bullet.x = x 
        bullet.y = y
        bullet.initialX = x
        bullet.initialY = y
        bullet.spd = associatedGun.btSpd
        bullet.dmg = associatedGun.btDmg
        bullet.scale = associatedGun.btScale
        bullet.color = associatedGun.btColor
        bullet.direction = direction
        bullet.lifeTime = associatedGun.btLifeTime
        bullet.lifeDistance = associatedGun.btLifeDistance
        bullet.preExp = associatedGun.btPreExp
        bullet.preExpMul = associatedGun.btPreExpMul
        bullet.linear = associatedGun.btLinear
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



class CoroutinesManager:
    def __init__(self,maxCoroutines):
        self.coroutines = []
        self.infoDic = {}
        for i in range(maxCoroutines):
            self.coroutines.append(None)
    def startCoroutine(self, generator, *args, idd = None, info = ""):
        if idd == None:
            for i in range(len(self.coroutines)):
                if self.coroutines[i] == None:
                    idd = i    #Picking up free coroutine
                    break
            if idd == None:
                print("Warning: coroutine array size exceeded. Array was appended")
                idd = len(self.coroutines)
                self.coroutines.append(None)

        self.coroutines[idd] = generator(idd,*args)
        
        if info!="":
            self.infoDic[info] = idd
        return (idd,info)


    def getIddByInfo(self, info):
        if info in self.infoDic:
            return  self.infoDic[info]
        return None
    def stopCoroutine(self, idd):
        self.coroutines[idd] = None 
    
    def stopCoroutineWithInfo(self,info):
        for i in self.coroutines:
            co = self.coroutines[i]
            if co[1] == info:
                self.coroutines[i] = None

coManager = CoroutinesManager(0)


class Text:
    def __init__(self, text, fontPath, fontSize, position = (0,0),color = WHITE, alpha = 255, rotation = 0, 
                isBold = False, isItalic = False, antialias = True,isActive = False, shakeFrequency = 0, shakeAmplitude = 0, shakeOffset = 0):
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
        self.antialias = True
        self.textSurface = self.font.render(self.text, antialias, self.color)
        self.sizeAnimRun,self.rotAnimRun,self.transAnimRun,self.alphaAnimRun = 0,0,0,0 #Obsolete but still make multithreading animations work
        self.shakeAmplitude = shakeAmplitude
        self.shakeFrequency = shakeFrequency
        self.shakeOffset = shakeOffset
        self.temp = self.position[1]

    def Resize(self, newSize):
        if newSize != self.fontSize:
            self.fontSize = int(newSize)
            self.font = pygame.font.Font(self.fontPath, self.fontSize)
            self.textSurface = self.font.render(self.text, self.antialias, self.color)
    
    def ChangeFont(self,newFontPath, newSize = -1):
        self.fontPath = newFontPath
        if newSize != -1:
            self.fontSize = newSize
        self.font = pygame.font.Font(self.fontPath, self.fontSize)
        self.textSurface = self.font.render(self.text, self.antialias, self.color)
    
    def UseSysFont(self, newFontPath, newSize):
        fontPath = newFontPath
        if newSize != -1:
            self.fontSize = newSize
        self.font = pygame.font.SysFont(self.fontPath, self.fontSize)
        self.textSurface = self.font.render(self.text, self.antialias, self.color)
    
    def Display(self, window, antialias = False):
        self.textSurface = self.font.render(self.text, antialias, self.color)
        self.antialias = antialias
        if self.rotation != 0:
            self.textSurface = pygame.transform.rotate(self.textSurface, self.rotation)
        self.textSurface.set_alpha(self.alpha)
        window.blit(self.textSurface, self.position)






class TextManager:
    def __init__(self, tempTxtCapacity, permTxtCapacity):
        '''The logic here is that there is "permanent" and temporary text buffer, permanent text buffer is dialogues one for example or tutorial
        text, this buffer does not change to do another thing. Meanwhile, temporary buffer text changes continually;it may be used to show a score
        bonus when carachter kills an ennemy for example
        '''
        self.tempTxtPool = []
        self.permText = []
        self.dialogueText = []    #Each letter should be a  surface
        self.curTempIndex = 0         #Current temp index

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
            
            targetedList[index].position = (eTransPos, eTransPosY)
            targetedList[index].transAnimRun = False

            if (t:=targetedList[index]).sizeAnimRun + t.rotAnimRun + t.transAnimRun + t.alphaAnimRun == 0:
                if endTxtOff != -1:
                    sleep(endTxtOff)
                    targetedList[index].isActive = False

        #TODO: Fix this rotation which sucks
        def rotAnimation():
            targetedList[index].rotAnimRun = True
            targetedList[index].rotation = sRotAngle
            for i in range(sizeSteps):
                targetedList[index].rotation = sRotAngle + i*deltaAngle
                sleep(deltaTime)

            targetedList[index].rotation = eRotAngle
            targetedList[index].rotAnimRun = False

            if (t:=targetedList[index]).sizeAnimRun + t.rotAnimRun + t.transAnimRun + t.alphaAnimRun == 0:
                if endTxtOff != -1:
                    sleep(endTxtOff)
                    targetedList[index].isActive = False


        def sizeAnimation():
            targetedList[index].sizeAnimRun = True
            targetedList[index].Resize(sSize)
            for i in range(sizeSteps):
                targetedList[index].Resize(sSize + i*deltaSize)
                sleep(deltaTime)

            targetedList[index].Resize(eSize)
            targetedList[index].sizeAnimRun = False

            if(t:=targetedList[index]).sizeAnimRun + t.rotAnimRun + t.transAnimRun + t.alphaAnimRun == 0:
                if endTxtOff != -1:
                    sleep(endTxtOff)
                    targetedList[index].isActive = False
        

        def alphaAnimation():
            targetedList[index].alphaAnimRun = True
            targetedList[index].alpha = sAlpha
            for i in range(alphaSteps):
                targetedList[index].alpha = sAlpha + i*deltaAlpha
                sleep(deltaTime)

            targetedList[index].alpha = eAlpha
            targetedList[index].alphaAnimRun = False
            if(t:=targetedList[index]).sizeAnimRun + t.rotAnimRun + t.transAnimRun + t.alphaAnimRun == 0:
                if endTxtOff != -1:
                    sleep(endTxtOff)
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
        



def GaddToArray(idd, string, interval, array, x, y, space, verticalSpace, letterPerInterval, dia):
    wait = waitForSeconds(interval)
    current = 0
    currentX = x
    currentY = y
    color = WHITE
    fontSize = 20
    fontName = "res/Font Styles/Vogue.ttf"
    a,b,c = "","",""
    text = Text("A", fontName, 25, position=(currentX,currentY))
    
    while current < len(string):
        while not next(wait):
            yield
        else:
            #Appending array
            bonusWait = 0
            for l in range(letterPerInterval):
                if current >=len(string): break
                info = ""
                value = [""]

                #Captures tags and ignore that text while displaying
                while string[current] == "<":
                    info = ""
                    value = [""]
                    current +=1
                    while string[current]!=":":
                        info += string[current]
                        current +=1

                    current +=1
                    while string[current]!= ">":
                        if string[current] == ",":
                            value.append("")
                            current +=1
                        value[-1] += string[current]
                        current +=1
                    current +=1
                    #Apply captured tags
                    if info == "COLOR":
                        if (value[0] == "BLUE"): color = BLUE
                        elif (value[0] == "RED"): color = RED
                        elif (value[0] == "WHITE"): color = WHITE
                        elif (value[0] == "YELLOW"): color = YELLOW
                        elif (value[0] == "PINK"): color = PINK
                        elif (value[0] == "GREEN"): color = GREEN
                    elif info == "SIZE":
                        fontSize = int(value)
                    elif info == "S":
                        a,b,c = value[0], value[1], value[2]
                    elif info == "FONT":
                        if value[0] == "Alice": fontName = "res/Font Styles/Fresh Lychee.ttf"
                        if value[0] == "Vogue": fontName = "res/Font Styles/Champagne & Limousines.ttf"

                    elif info == "W": 
                        bonusWait = float(value[0])
                #Order is important
                if string[current] == '\n':  
                    current += 1
                    currentY += (text.textSurface.get_size())[1] + verticalSpace
                    currentX = x
                    continue
                #Setting Text object parameters
                text = Text(string[current], fontName, fontSize, position=(currentX,currentY))
                #print(text.textSurface.get_size()[1]) Text surface of aiwl is bigger than vogue??Nani?? TODO:Fix this dynamic box issue
                
                if a != "":
                    text.shakeFrequency = float(b)  
                    text.shakeAmplitude = float(a)
                    text.shakeOffset = float(c)
                text.temp = text.position[1]
                text.color = color
                currentX += (text.textSurface.get_size())[0] + space
                current += 1
                array.append(text)
            wait = waitForSeconds(interval + bonusWait)
            yield 
    else:
        coManager.coroutines[idd] = None
        dia.isBusy = False
        yield

class Dialogue:
    def __init__(self):
        self.dialogueText = []
        self.isBusy = False

    def displayDialogue(self, string, interval, x, y, space = 2, verticalSpace=2, letterPerInterval = 1):
        self.isBusy = True
        coManager.startCoroutine(GaddToArray,string, interval, self.dialogueText, x, y, space, verticalSpace, letterPerInterval, self)
    def Clean(self):
        self.dialogueText = []

def GwaitForInput():
    while not (keyboard.is_pressed('return')):
        yield False
    yield True

def GdisplaySet(idd,theSet, interval, waitForInput, dialogue:Dialogue, x, y):
    wait = waitForSeconds(interval)
    inputWait = GwaitForInput()
    currentString = 0
    string = theSet[currentString] 
    dialogue.Clean()
    dialogue.displayDialogue(string,0.0, x, y)
    while currentString<len(theSet):
        while dialogue.isBusy:
            yield
        else:
            if not waitForInput:
                while not next(wait):
                    yield
            else:
                while not next(inputWait):
                    yield
                inputWait = GwaitForInput()
            wait = waitForSeconds(interval)
            currentString += 1
            if (currentString<=len(theSet)-1):
                string = theSet[currentString] 
                dialogue.Clean()
                dialogue.displayDialogue(string, 0.0, x, y)
            yield
    else:
        dialogue.Clean()
        coManager.coroutines[idd] = None
        yield
        
        
class DialogueManager:
    def __init__(self):
        self.dialogues = [] #array of arrays
        self.minBoxX = 10000
        self.maxBoxX = 0
        self.minBoxY = 10000
        self.maxBoxY = 0
        self.boxColor = BLUE
    def Add(self, dialogue:Dialogue):
        self.dialogues.append(dialogue)
    def displaySetOfSentences(self, theSet, interval, waitForInput, x = 0, y = 0,index = 0):
        coManager.startCoroutine(GdisplaySet, theSet, interval, waitForInput, self.dialogues[index], x, y)
    def DisplayDynamicBox(self, window,offsetX, offsetY, index = 0):
        for letter in self.dialogues[index].dialogueText:
            if (letter.position)[0]< self.minBoxX: self.minBoxX = (letter.position)[0] 
            if (letter.position)[1]< self.minBoxY: self.minBoxY = (letter.position)[1]
            if (letter.position)[0]> self.maxBoxX: self.maxBoxX = (letter.position)[0] + letter.textSurface.get_size()[0]
            if (letter.position)[1]> self.maxBoxY: self.maxBoxY = (letter.position)[1] + letter.textSurface.get_size()[1]
        width = self.maxBoxX - self.minBoxX
        height = self.maxBoxY - self.minBoxY
        rect = pygame.Rect(self.minBoxX-offsetX, self.minBoxY-offsetY, width + offsetX, height + offsetY)
        pygame.draw.rect(window, self.boxColor, rect)

        #TODO: Optimize this function





class Game:
    def __init__(self, width, height, fullScreen = False):
        self.width = width
        self.height = height
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
            deltaX = (newX - self.x*deltaTime)/interpolationTime
            deltaY = (newY - self.y)/(interpolationTime*fps)
            steps = int(interpolationTime*fps)
            for i in range(steps):
                self.x += deltaX
                self.y += deltaY
                sleep(deltaTime)
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


class SpotLight:
    def __init__(self,color = WHITE,x = 0, y = 0):
        self.x = x
        self.y = y
        self.color = color
        self.isActive = True
        self.gradient = SPOTLIGHT.copy()
    def rescale(self, size):
        pygame.transform.scale(self.gradient,size)


class LightingSystem:
    def __init__(self, capacity):
        self.capacity = capacity
        self.spotLights = [SpotLight() for x in range(capacity)]
    def add(self, color = WHITE, x = 0, y = 0):
        self.capacity += 1
        self.spotLights.append(SpotLight(x=x, y=y, color=color))

    
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


#Init class objects
player = Player(20,20, 10,PLAYERSPEED, 3, WHITE, 20)
ennemyManager = EnnemyManager(1, 500, 500, areAlive=True)
bulletManager = BulletManager(GAMEBULLETS)
imaginaryBulletManager= BulletManager(GAMEBULLETS) #Maybe temporary solution I don't know how much this is optimized
textManager = TextManager(20,1)
game = Game(WIDTH, HEIGHT)
levelManager = LevelManager(0,0)
levelManager.walls = [Wall(1440/2,700, BLUE, 1440/2,20), 
                      Wall(1420, 350, BLUE, 20, 300)]
scoreManager = ScoreManager()

SPOTLIGHT = pygame.image.load("res/Textures/SpotLight1.png").convert_alpha()
lightingSystem = LightingSystem(2)
#Init info arrays
#I found out that class objects are passed by reference to an array, it allows me to do a lot of abstraction
staticObjects = []
dynamicObjects = [player, ennemyManager.pool]
attachedToCam = [textManager.permText]
nonAttachedToCam = [player, ennemyManager.pool]
cam = Camera(nonAttachedToCam)
dm = DialogueManager()
#Gun list--------------------------------------------------------
gun_Pistol = Gun(1, 1, shotSound=PISTOLSHOTSOUND)
gun_MachineGun = Gun(0.1, 3, minRandom=0,maxRandom=8, btScale=5)

currentGun = gun_Pistol
#----------------------------------------------------------------
#Coroutines generators
def waitForSeconds(seconds):
    awaitTime = seconds
    while awaitTime>0:
        awaitTime -= deltaTime
        yield False
    yield True

def GprintAfter(idd,text,time):         #My first generator; it's an example
    wait = waitForSeconds(time)
    while not next(wait):
       #Write the code executed at each frame here
       yield
    else:
        #Write the code executed after "time" has passed here
        coManager.coroutines[idd] = None
        yield

def GInterpolateObjectValue(idd, obj, att:str, value, time):
    wait = waitForSeconds(time)
    startValue = getattr(obj, att)
    while not next(wait):
       deltaValue = (deltaTime/time)*value
       current = getattr(obj, att)
       setattr(obj, att, current + deltaValue)
       yield
    else:
        #Write the code executed after "time" has passed here
        coManager.coroutines[idd] = None
        setattr(obj, att, startValue + value)
        yield

def GchangeObjBoolean(idd, obj, att, value, time):
    wait = waitForSeconds(time)
    while not next(wait):
       #Write the code executed at each frame here
       yield
    else:
        #Write the code executed after "time" has passed here
        coManager.coroutines[idd] = None
        setattr(obj, att, value)
        yield


def Blend(game, filter):
    global runningBlend
    game.window.blit(filter, (0,0), special_flags=BLEND_RGBA_MULT)
    runningBlend = False
    
#Update and game logic
filter = pygame.surface.Surface((game.width, game.height), pygame.SRCALPHA, 32).convert_alpha()
forbidden = (None,None,None,None)
running = True
dia = Dialogue()
dm.Add(dia)
dm.displaySetOfSentences(DialogueList.SET1TEST, 0.1,True,250, 250, 0)
#displayDialogue(string = "Hello traveller. Is you another one who is Looking for adventure is the dangeon?", interval = 0.1, space = 2, letterPerInterval = 1)
if __name__ == '__main__':
    runningBlend = False
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
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_0:
                    if currentGun == gun_Pistol:
                        currentGun = gun_MachineGun
                        shootFrequency = 0.2
                        PISTOLEQUIPSOUND.play()
                    else:
                        currentGun = gun_Pistol
                        shootFrequency = 0.2
                        PISTOLEQUIPSOUND.play()

        if keyboard.is_pressed("E"):
            deltaTime=0
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
        player.x += moveX*player.spd*deltaTime
        player.y += moveY*player.spd*deltaTime
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
                bullet.x += (bullet.direction[0]*bullet.spd*(bullet.preExp + 
                            bullet.preExpMul*exp(-abs(bullet.initialX-bullet.x)/bullet.linear)))*deltaTime
                bullet.y += (bullet.direction[1]*bullet.spd*(bullet.preExp + 
                                bullet.preExpMul*exp(-abs(bullet.initialY-bullet.y)/bullet.linear)))*deltaTime
                if bullet.lifeTime != -1:
                    bullet.lifeTime -= deltaTime
                    if bullet.lifeTime<=0:
                        bullet.lifeTime = bullet.constLT
                        bullet.isActive = False
                if bullet.lifeDistance!= -1:
                    if CalculateMagnitude(  (bullet.x-bullet.initialX, bullet.y-bullet.initialY) )>=bullet.lifeDistance :
                        bullet.isActive = False
                        pass
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
                        textManager.permText[0].alphaAnimRun = False
        
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
                        textManager.permText[0].color = (min(255,200+score),0,0)
                        textManager.permText[0].isActive = True
                        textManager.permText[0].alpha = 255
                        coManager.startCoroutine(GInterpolateObjectValue, textManager.permText[0], "alpha", -255, 1.5, idd = coManager.getIddByInfo("Combo1Anim"), info = "Combo1Anim")
                        coManager.startCoroutine(GchangeObjBoolean, textManager.permText[0], "isActive", False, 1.5, idd = coManager.getIddByInfo("Combo2Anim"), info = "Combo2Anim")

                        #textManager.AnimateText(textManager.permText, 0, animationState=1-anim, sAlpha = 255, eAlpha = 0, alphaTime= comboTime, endTxtOff=0)
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
                bullet.x += (bullet.direction[0]*bullet.spd*(bullet.preExp + bullet.preExpMul*exp(-abs(bullet.initialX-bullet.x)/bullet.linear)))*deltaTime
                bullet.y += (bullet.direction[1]*bullet.spd*(bullet.preExp + bullet.preExpMul*exp(-abs(bullet.initialY-bullet.y)/bullet.linear)))*deltaTime
                bullet.lifeTime -= deltaTime
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
                shootFrequency = currentGun.shootFrequency
                for i in range(currentGun.bulletPerShot):
                    #Randomize shot direction
                    percent = randint(currentGun.minRandom, currentGun.maxRandom)*choice([-1,1])*pi/180
                    angle = pi/2
                    signX = bulletDirection[0]
                    signY = bulletDirection[1]
                    if bulletDirection[0]: angle = arctan2(bulletDirection[1],bulletDirection[0])
                    bulletDirection = (cos(angle+percent), sin(angle+percent))
                    #Instantiate Bullet
                    bulletManager.Instantiate(player.x, player.y, associatedGun=currentGun, direction = bulletDirection)

                    # imaginaryBulletManager.Instantiate(player.x, player.y, spd = BULLETSPD*2, dmg = BULLETDAMAGE,scale = BULLETSCALE, color = (randint(50,255),
                    #         randint(50,255),randint(50,255)), direction = bulletDirection, shotByPlayer = True)
                if SOUNDON:
                    currentGun.shotSound.play()
            

                index = textManager.activateFreeTxt()
                textManager.tempTxtPool[index].text = ""
                textManager.tempTxtPool[index].ChangeFont(choice(["res/Font Styles/BADABB__.TTF", "res/Font Styles/Cocola.ttf", "res/Font Styles/Fresh Lychee.ttf"]))
                textManager.tempTxtPool[index].rotation = randint(-45,45)
                textManager.tempTxtPool[index].text = choice(SHOOTWORDS)
                textManager.tempTxtPool[index].color = (255,randint(0,255), 0)
                textManager.AnimateText(textManager.tempTxtPool, index,sTransPos = player.x-cam.x, eTransPos = player.x-cam.x + randint(-80,80),
                                        eTransPosY = player.y-cam.y + randint(-80,80), sTransPosY = player.y-cam.y, sAlpha = 255, eAlpha = 0, alphaTime=0.5,
                                        transTime = 0.1, endTxtOff = 0.5, sSize= 0, eSize = randint(20,40), sizeTime = 0.1)

        #Advancing coroutines 
        for co in coManager.coroutines:
            if co != None:
                next(co)
            
        #Drawing shapes
        for key in drawDic:
            for args in drawDic[key]:
                if args[0] == "c":
                    pygame.draw.circle(*args[1]) #For now there are just circles
                if args[0] == "r":
                    pygame.draw.rect(*args[1])


        #Appliying light 
        if  usingLightSystem:
            filter.fill(AMBIENTLIGHT)
            light = lightingSystem.spotLights[0]
            light.x = player.x    #pygame.mouse.get_pos()[0]
            light.y = player.y    #pygame.mouse.get_pos()[1]
            light.gradient = pygame.transform.scale(light.gradient, (1000,1000))
            filter.blit(light.gradient, (light.x-light.gradient.get_size()[0]//2, 
                        light.y-light.gradient.get_size()[1]//2))

            a,b =pygame.mouse.get_pos()
            if  not runningBlend:
                runningBlend = True
                run_threaded(Blend, game, filter)

            #Process(target=Blend, args=(game,filter, (a,b), runningBlend)).start()
            #Calling Blend Function here causes a drop of fps until it reaches 15-20fps; I think the blend is done 
            #cpu iterating over pixels... I'm trying to make this in another process
            #doing it in a thread does not change any
            #TODO: Fix this
        #Drawing temporary text
        for i in range(len(textManager.tempTxtPool)):
            if textManager.tempTxtPool[i].isActive:
                textManager.tempTxtPool[i].Display(game.window, antialias = True)
        #Drawing permanent text
        for i in range(len(textManager.permText)):
            if textManager.permText[i].isActive:
                textManager.permText[i].Display(game.window, antialias = True)
        #Drawing dialgoues
        if dia.dialogueText != []:
            dm.DisplayDynamicBox(game.window, 10,10,0)
        i = 0
        for txt in dia.dialogueText:
            i+=1
            txt.position = (txt.position[0],txt.temp + txt.shakeAmplitude*cos(time()*2*pi*txt.shakeFrequency+txt.shakeOffset)) 
            txt.Display(game.window)
        #Display fps
        game.window.blit(DEFAULTFONT.render(str(fps),False, BLUE), (0,0))
        #Updating shapes
        pygame.display.flip()
        #Calculating fps
        fps = int(clock.get_fps())
        if fps < 5:
            fps = 60
        #Updating time variables
        shootFrequency = max(0, shootFrequency - deltaTime)
        deltaTime = 1/fps

        clock.tick(MAXFPS)
    pygame.quit()

    #Text animation know can run in threads or in coroutines; for instance, here there is the combometer animation which runs in coroutine
    #which compulsory since it needs to suspend it activity when game is paused. Meanwhile the cartoon anatimion when you shoot runs 
    #in threads, they are temporary, and just for fun don't need them to stop when game is paused
    #Threads run independently and trying to stop them causes a mess in the code