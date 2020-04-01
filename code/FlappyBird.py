import random, pygame, sys, time
from pygame.locals import *

FPS = 30
# Kích thước cửa sổ game
WINDOWWIDTH = 600 
WINDOWHEIGHT = 600


SIZE_BIRD = (50, 40) # Kích thước chim (x, y)
TIME_CHANGE_BIRD = 4 # Thời gian thay đổi ảnh chim
SPEED_BIRD_FLY = -15 # Tốc độ mỗi lần chim bay lên
IMG_BIRD_1 = pygame.image.load('img/bird1.png') # Ảnh chim 1
IMG_BIRD_2 = pygame.image.load('img/bird2.png') # Ảnh chim 2
IMG_COT = pygame.image.load('img/column.png') # Ảnh cột
GRAVITATION = 1.25 # Gia tốc rơi

# màu      R    B    G
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
GREY  = (200, 200, 200)

SIZE_COLUMN = 70 # Bề rộng cột
SIZE_BLANK = 200 # Độ rộng khoảng trống giữa cột
DISTANCE_COLUMN = 225 # Khoảng cách 2 cột kế tiếp
SPEED_COLUMN = 5 # Tốc độ di chuyển của cột

TIME_CHANGE_COLOR_TEXT = 9 # Thời gian thay đổi màu chữ (chữ nhấp nháy)

class Bird(): # Chim
    def __init__(self, y = WINDOWHEIGHT/2 - SIZE_BIRD[1]/2, speed = 0, status = 1):
        self.x = WINDOWWIDTH/2 - SIZE_BIRD[0]/2
        self.y = y
        self.speed = speed 
        self.status = status # Trạng thái chim (ảnh 1 hoặc 2)
    
    def draw(self):
        # Dựa vào status để vẽ ảnh phù hợp
        if self.status <= TIME_CHANGE_BIRD:
            DISPLAYSURF.blit(IMG_BIRD_1, (self.x, self.y))
        else:
            DISPLAYSURF.blit(IMG_BIRD_2, (self.x, self.y))
    
    def update(self, fly, speed_bird_fly = SPEED_BIRD_FLY):
        if fly == True: # Chim bay lên
            self.speed = speed_bird_fly
        # rơi theo gia tốc
        self.y += self.speed + GRAVITATION/2
        self.speed += GRAVITATION
        # Xác định trạng thái
        if self.status > TIME_CHANGE_BIRD*2:
            self.status = 1
        else:
            self.status += 1

class Column():
    def __init__(self, x, y = 'default'): # x, y là vị trí phía trên bên trái của khoảng trống
        self.x = x
        self.y = random.randrange(80, WINDOWHEIGHT - SIZE_BLANK - 100, 5) # lấy y ngẫu nhiên
        if y != 'default': # Trường hợp xác định cụ thể y
            self.y = y

    def draw(self):
        # Dùng 1 ảnh vẽ 2 vị trí khác nhau
        DISPLAYSURF.blit(IMG_COT, (self.x, self.y - 600))
        DISPLAYSURF.blit(IMG_COT, (self.x, self.y + SIZE_BLANK))
    
    def update(self):
        self.x -= SPEED_COLUMN

class Columns():
    def __init__(self):
        self.listColumn = []
        # 3 cột là đủ cho màn hình
        for i in range(3):
            self.listColumn.append(Column(( DISTANCE_COLUMN*i) + WINDOWWIDTH))

    # Tạo list cột mới khi vào game
    def makeNewListColumn(self):
        self.listColumn = []
        for i in range(3):
            self.listColumn.append(Column(( DISTANCE_COLUMN*i) + WINDOWWIDTH))
    def draw(self):
        for i in range(len(self.listColumn)):
            self.listColumn[i].draw()
    
    def update(self):
        for i in range(len(self.listColumn)):
            self.listColumn[i].update()
        # Xoá cột bên trái khi qua hết màn hình, tạo thêm cột tiếp theo
        if self.listColumn[0].x < -SIZE_COLUMN:
            self.listColumn.pop(0)
            self.listColumn.append(Column(self.listColumn[1].x + DISTANCE_COLUMN))
    
class Scenes():
    def __init__(self, option = 1):
        self.option = option # Dựa vào option để vẽ màn hình game (1: gameStart, 2: gamePlay, 3: gameOver)
    
    def gameStart(self, bird):
        bird.y = WINDOWHEIGHT/2 - SIZE_BIRD[1]/2
        bird.speed = 0
        clickToStart = ClickToST('Click to start')
        headingFlappyBird = Heading('FLAPPY BIRD')
        while True:
            DISPLAYSURF.blit(IMG_BG, (0, 0))
            mouseClick = False # Kiểm tra click chuột
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                if event.type == MOUSEBUTTONUP:
                    mouseClick = True
            if mouseClick == True:
                break
            isFly = False
            if bird.y > WINDOWHEIGHT/2:
                isFly = True
            bird.draw()
            bird.update(isFly, -10)
            clickToStart.draw()
            clickToStart.update()
            headingFlappyBird.update()
            headingFlappyBird.draw()
            pygame.display.update()
            FPSCLOCK.tick(FPS)
        self.option = 2
    def gamePlay(self, bird, columns, score):
        score.text = '0'
        columns.makeNewListColumn()
        bird.speed = SPEED_BIRD_FLY
        
        while True:
            DISPLAYSURF.blit(IMG_BG, (0, 0))
            mouseClick = False # Kiểm tra click chuột
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                if event.type == MOUSEBUTTONUP:
                    mouseClick = True

            bird.draw()
            bird.update(mouseClick)

            columns.draw()
            columns.update()
            
            # Cộng thêm điểm
            if GameControl.isAddScore(columns) == True:
                score.update()
            score.draw()

            # Kiểm tra va chạm
            isCollide = GameControl.isCollide(bird, columns)
            if isCollide == True:
                break

            pygame.display.update()
            FPSCLOCK.tick(FPS)
        self.option = 3
    def gameOver(self, bird, columns, score):
        bird.speed = 0
        headingGameOver = Heading('GAMEOVER')
        birdStatus = bird.status
        isBirdAminationFinish = False # Kiểm tra chim rơi xuống
        inHeadingAminationFinish = False # Kiểm tra chữ rơi xuống
        while True:
            DISPLAYSURF.blit(IMG_BG, (0, 0))
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
            
            columns.draw()
            bird.draw()
            bird.update(False)
            bird.status = birdStatus
            if bird.y >= WINDOWHEIGHT - SIZE_BIRD[1]:
                bird.y = WINDOWHEIGHT - SIZE_BIRD[1]
                bird.speed = 0
                isBirdAminationFinish = True
            headingGameOver.draw()
            headingGameOver.update()
            
            if headingGameOver.y >= WINDOWHEIGHT/2 - 90:
                headingGameOver.y = WINDOWHEIGHT/2 - 90
                headingGameOver.speed = 0
                inHeadingAminationFinish = True

            if isBirdAminationFinish == True and inHeadingAminationFinish == True:
                break

            pygame.display.update()
            FPSCLOCK.tick(FPS)
        clickToReplay = ClickToST('Click to replay')
        while True:
            scoreText = Text('Score: '+ score.text, WINDOWWIDTH/2 - len('Score: '+ score.text)/2, WINDOWHEIGHT/2, 50, BLACK)

            DISPLAYSURF.blit(IMG_BG, (0, 0))
            mouseClick = False
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                if event.type == MOUSEBUTTONUP:
                    mouseClick = True
            if mouseClick == True:
                break
            columns.draw()
            bird.draw()
            headingGameOver.draw()
            clickToReplay.draw()
            clickToReplay.update()
            scoreText.draw()
            pygame.display.update()
            FPSCLOCK.tick(FPS)
        self.option = 1           

class Text():
    def __init__(self, text, x, y, size, color):
        self.text = text
        self.x = x
        self.y = y
        self.size = size
        self.color = color
    
    def draw(self):
        fontObj = pygame.font.SysFont('Comic Sans MS', self.size)
        textSurfaceObj = fontObj.render(self.text, False, self.color)
        textRectObj = textSurfaceObj.get_rect()
        textRectObj.center = (self.x, self.y)
        DISPLAYSURF.blit(textSurfaceObj, textRectObj)

class Score(Text):
    def __init__(self, text,x = WINDOWWIDTH/2, y = WINDOWHEIGHT/6, size = 50, color = BLACK):
        super().__init__(text, x, y, size, color)

    def update(self):
        self.text = str(int(self.text) + 1)

class ClickToST(Text): # Chữ nhấp nháy
    def __init__(self, text, y = WINDOWHEIGHT*0.6, size = 40, color = BLACK):
        super().__init__(text, WINDOWWIDTH/2 - len(text)/2, y, size, color)
        self.status = 1
    
    def update(self):
        # Chọn màu dựa vào status
        if self.status <= TIME_CHANGE_COLOR_TEXT:
            self.color = BLACK
        else:
            self.color = GREY
        if self.status > TIME_CHANGE_COLOR_TEXT*2:
            self.status = 1
        else:
            self.status += 1

class Heading(Text): # Tiêu đề (chữ to)
    def __init__(self, text, y = -100, size = 90, color = BLACK):
        super().__init__(text, WINDOWWIDTH/2 - len(text)/2, y, size, color)
        self.speed = 0
    
    def update(self):
        # Rơi theo gia tốc đến vị trí xác định
        self.y += self.speed + GRAVITATION/2
        self.speed += GRAVITATION
        if self.y >= WINDOWHEIGHT/2 - 90:
            self.y = WINDOWHEIGHT/2 - 90

class GameControl():
    def isCollide(bird, columns): # Kiểm tra va chạm
        def isCollide1Column(bird, column):
            # Các giới hạn chim
            limitBirdTop = bird.y
            limitBirdBottom = bird.y + SIZE_BIRD[1]
            limitBirdLeft = bird.x
            limitBirdRight = bird.x + SIZE_BIRD[0]
            # Các giới hạn cột
            limitColumnLeft = column.x
            limitColumnRight = column.x + SIZE_COLUMN
            limitColumnTop = column.y
            limitColumnBottom = column.y + SIZE_BLANK 
            # Kiểm tra va chạm
            if limitBirdLeft > limitColumnRight - SIZE_COLUMN/4:
                return False
            if (limitBirdRight - limitColumnLeft) > 0 and (limitColumnTop - limitBirdTop) > 0:
                return True
            if  (limitBirdBottom - limitColumnBottom) > 0 and (limitBirdRight - limitColumnLeft) > 0:
                return True
            if  limitBirdBottom >= WINDOWHEIGHT or limitBirdTop < -100:
                return True
            return False
        # Kiểm tra va chạm cho tất cả các cột
        for i in range(len(columns.listColumn)):
            if isCollide1Column(bird, columns.listColumn[i]):
                return True
        return False
    def isAddScore(columns): # Cộng thêm điểm
        midWindow = WINDOWWIDTH/2
        # Cột đến giữa màn hình thì cộng điểm
        for i in range(len(columns.listColumn)):
            midColumn = columns.listColumn[i].x + SIZE_COLUMN/2
            if abs(midWindow - midColumn) <= SPEED_COLUMN/2:
                return True
        return False

def main():
    global FPSCLOCK, DISPLAYSURF, IMG_BG
    pygame.init()
    pygame.display.set_caption('FLAPPY BIRD')
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

    logo = pygame.image.load('img/logo.png')
    pygame.display.set_icon(logo)
    IMG_BG = pygame.image.load('img/bg.bmp').convert()
    scene = Scenes()
    bird = Bird()
    columns = Columns()
    score = Score('0')
    while True:
        if scene.option == 1:
            scene.gameStart(bird)
        elif scene.option == 2:
            scene.gamePlay(bird, columns, score)
        elif scene.option == 3:
            scene.gameOver(bird, columns, score)

if __name__ == '__main__':
    main()