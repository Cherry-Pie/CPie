import pygame
import pygame._view
from pygame import *

WIN_WIDTH = 800
WIN_HEIGHT = 480
HALF_WIDTH = int(WIN_WIDTH / 2)
HALF_HEIGHT = int(WIN_HEIGHT / 2)

DISPLAY = (WIN_WIDTH, WIN_HEIGHT)
DEPTH = 32
FLAGS = 0
FPS = 60
CAMERA_SLACK = 30

BG_MUSIC = 'data/mus/e65769b361688d.mp3'
BG_IMAGE = pygame.image.load('data/img/bg.png')

FISH_EVENT = pygame.USEREVENT+2

def main():
    global cameraX, cameraY
    pygame.init()
    screen = pygame.display.set_mode(DISPLAY, FLAGS, DEPTH)
    pygame.display.set_caption("HROMD")
    timer = pygame.time.Clock()

    screen.fill((51,51,51))
    MENU = True
    menu = Menu()#necessary
    #menu.set_colors((255,255,255), (0,0,255), (0,0,0))#optional
    #menu.set_fontsize(64)#optional
    #menu.set_font('data/couree.fon')#optional
    #menu.move_menu(100, 99)#optional
    menu.init(['Start','Options','Quit'], screen)#necessary
    #menu.move_menu(0, 0)#optional
    menu.draw()#necessary

    mixer.music.load(BG_MUSIC)
    mixer.music.play(0,0.0)

    up = down = left = right = running = False
    bg = BG_IMAGE
    bg.convert()
    #bg.fill(Color("#000000"))
    entities = pygame.sprite.Group()
    player = Player(32, 32)
    platforms = []

    x = y = 0
    level = [
        "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",
        "P                                          P",
        "P                                          P",
        "P                                          P",
        "P                                          P",
        "P                                          P",
        "P                                          P",
        "P                                          P",
        "P                                          P",
        "P                     P                    P",
        "P               P              P           P",
        "P       P                            P     P",
        "P                                          P",
        "P                                         EP",
        "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",]
    # build the level
    for row in level:
        for col in row:
            if col == "P":
                p = Platform(x, y)
                platforms.append(p)
                entities.add(p)
            if col == "E":
                e = ExitBlock(x, y)
                platforms.append(e)
                entities.add(e)
            x += 32
        y += 32
        x = 0

    total_level_width  = len(level[0])*32
    total_level_height = len(level)*32
    camera = Camera(complex_camera, total_level_width, total_level_height)
    entities.add(player)

    while 1:
        milliseconds = timer.tick(FPS)  # milliseconds passed since last frame
        timedelta = milliseconds / 1000.0 # seconds passed since last frame (float)
        #print timedelta

        for e in pygame.event.get():
            if (MENU):
                if e.type == KEYDOWN:
                    if e.key == K_UP:
                        menu.draw(-1) #here is the Menu class function
                    if e.key == K_DOWN:
                        menu.draw(1) #here is the Menu class function
                    if e.key == K_RETURN:
                        print menu.get_position()
                        if menu.get_position() == 0:#here is the Menu class function
                            MENU = False
                        if menu.get_position() == 2:#here is the Menu class function
                            pygame.display.quit()
                    if e.key == K_ESCAPE:
                        pygame.quit()
                if e.type == QUIT:
                    pygame.quit()
            else:
                if e.type == FISH_EVENT:
                    font = pygame.font.Font(None, 76)
                    text = font.render("YUMMY :3", 1, (123, 204, 201))
                    textpos = text.get_rect(centerx=bg.get_width()/2, centery=100)
                    newBg = pygame.image.load('data/img/bg2.png')
                    bg.blit(newBg, (0,0))
                    bg.blit(text, textpos)
                if e.type == QUIT:
                    pygame.quit()
                if e.type == KEYDOWN and e.key == K_ESCAPE:
                    pygame.quit()
                if e.type == KEYDOWN and e.key == K_UP:
                    up = True
                if e.type == KEYDOWN and e.key == K_DOWN:
                    down = True
                if e.type == KEYDOWN and e.key == K_LEFT:
                    left = True
                if e.type == KEYDOWN and e.key == K_RIGHT:
                    right = True
                if e.type == KEYDOWN and e.key == K_SPACE:
                    running = True

                if e.type == KEYUP and e.key == K_UP:
                    up = False
                if e.type == KEYUP and e.key == K_DOWN:
                    down = False
                if e.type == KEYUP and e.key == K_RIGHT:
                    right = False
                if e.type == KEYUP and e.key == K_LEFT:
                    left = False
                if e.type == KEYUP and e.key == K_RIGHT:
                    right = False

        # draw background
        #for y in range(32):
        #    for x in range(32):
        #        screen.blit(bg, (x * 32, y * 32))
        if not(MENU):
            screen.blit(bg, (0, 0))
            camera.update(player)

            # update player, draw everything else
            player.update(up, down, left, right, running, platforms, timedelta)
            for e in entities:
                screen.blit(e.image, camera.apply(e))



        pygame.display.update()

class Camera(object):
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = Rect(0, 0, width, height)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)

def simple_camera(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    return Rect(-l+HALF_WIDTH, -t+HALF_HEIGHT, w, h)

def complex_camera(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t, _, _ = -l+HALF_WIDTH, -t+HALF_HEIGHT, w, h

    l = min(0, l)                           # stop scrolling at the left edge
    l = max(-(camera.width-WIN_WIDTH), l)   # stop scrolling at the right edge
    t = max(-(camera.height-WIN_HEIGHT), t) # stop scrolling at the bottom
    t = min(0, t)                           # stop scrolling at the top
    return Rect(l, t, w, h)

class Entity(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

class Player(Entity):
    def __init__(self, x, y):
        Entity.__init__(self)
        self.xvel = 0
        self.yvel = 0
        self.onGround = False
        self.onCeilHit = False
        self.image = Surface((32,32))
        #self.image.fill(Color("#0000FF"))
        self.image = pygame.image.load('data/img/kpl.png')
        self.image = pygame.transform.scale(self.image,(32,32))
        self.image.convert()
        self.rect = Rect(x, y, 32, 32)

    def update(self, up, down, left, right, running, platforms, timedelta):
        if self.onCeilHit:
            self.yvel = 0
            print 'head BANG'
        if up:
            # only jump if on the ground
            if self.onGround: self.yvel -= 10
        if down:
            pass
        if running:
            self.xvel = 16
        if left:
            self.xvel = -5
        if right:
            self.xvel = 5
        if not self.onGround:
            # only accelerate with gravity if in the air
            self.yvel += 0.3
            # max falling speed
            if self.yvel > 100: self.yvel = 100
        if not(left or right):
            self.xvel = 0
        # increment in x direction
        self.rect.left += self.xvel
        # do x-axis collisions
        self.collide(self.xvel, 0, platforms)
        # increment in y direction
        self.rect.top += self.yvel
        # assuming we're in the air
        self.onGround = False;
        self.onCeilHit = False;
        # do y-axis collisions
        self.collide(0, self.yvel, platforms)

    def collide(self, xvel, yvel, platforms):
        for p in platforms:
            if pygame.sprite.collide_rect(self, p):
                if isinstance(p, ExitBlock):
                    event = pygame.event.Event(FISH_EVENT)
                    pygame.event.post(event)
                if xvel > 0:
                    self.rect.right = p.rect.left
                    print "collide right"
                if xvel < 0:
                    self.rect.left = p.rect.right
                    print "collide left"
                if yvel > 0:
                    self.rect.bottom = p.rect.top
                    self.onGround = True
                    self.yvel = 0
                if yvel < 0:
                    self.rect.top = p.rect.bottom
                    self.onGround = False
                    self.onCeilHit = True
                    print "collide top"


class Platform(Entity):
    def __init__(self, x, y):
        Entity.__init__(self)
        self.image = Surface((32, 32))
        self.image.set_alpha(255)
        self.image.fill((55,55,55))
        self.image.convert()
        self.rect = Rect(x, y, 32, 32)

    def update(self):
        pass

class ExitBlock(Platform):
    def __init__(self, x, y):
        Entity.__init__(self)
        #self.image.fill(Color("#0033FF"))
        self.image = pygame.image.load('data/img/fish.png')
        self.image = pygame.transform.scale(self.image,(32,32))
        self.image.convert()
        self.rect = Rect(x, y, 32, 32)

class Menu:
    lista = []
    pola = []
    rozmiar_fontu = 32
    font_path = 'data/font/coders_crux.ttf'
    font = pygame.font.Font
    dest_surface = pygame.Surface
    ilosc_pol = 0
    kolor_tla = (51,51,51)
    kolor_tekstu =  (255, 255, 153)
    kolor_zaznaczenia = (153,102,255)
    pozycja_zaznaczenia = 0
    pozycja_wklejenia = (0,0)
    menu_width = 0
    menu_height = 0

    class Pole:
        tekst = ''
        pole = pygame.Surface
        pole_rect = pygame.Rect
        zaznaczenie_rect = pygame.Rect

    def move_menu(self, top, left):
        self.pozycja_wklejenia = (top,left)

    def set_colors(self, text, selection, background):
        self.kolor_tla = background
        self.kolor_tekstu =  text
        self.kolor_zaznaczenia = selection

    def set_fontsize(self,font_size):
        self.rozmiar_fontu = font_size

    def set_font(self, path):
        self.font_path = path

    def get_position(self):
        return self.pozycja_zaznaczenia

    def init(self, lista, dest_surface):
        self.lista = lista
        self.dest_surface = dest_surface
        self.ilosc_pol = len(self.lista)
        self.stworz_strukture()

    def draw(self,przesun=0):
        if przesun:
            self.pozycja_zaznaczenia += przesun
            if self.pozycja_zaznaczenia == -1:
                self.pozycja_zaznaczenia = self.ilosc_pol - 1
            self.pozycja_zaznaczenia %= self.ilosc_pol
        menu = pygame.Surface((self.menu_width, self.menu_height))
        menu.fill(self.kolor_tla)
        zaznaczenie_rect = self.pola[self.pozycja_zaznaczenia].zaznaczenie_rect
        pygame.draw.rect(menu,self.kolor_zaznaczenia,zaznaczenie_rect)

        for i in xrange(self.ilosc_pol):
            menu.blit(self.pola[i].pole,self.pola[i].pole_rect)
        self.dest_surface.blit(menu,self.pozycja_wklejenia)
        return self.pozycja_zaznaczenia

    def stworz_strukture(self):
        przesuniecie = 0
        self.menu_height = 0
        self.font = pygame.font.Font(self.font_path, self.rozmiar_fontu)
        for i in xrange(self.ilosc_pol):
            self.pola.append(self.Pole())
            self.pola[i].tekst = self.lista[i]
            self.pola[i].pole = self.font.render(self.pola[i].tekst, 1, self.kolor_tekstu)

            self.pola[i].pole_rect = self.pola[i].pole.get_rect()
            przesuniecie = int(self.rozmiar_fontu * 0.2)

            height = self.pola[i].pole_rect.height
            self.pola[i].pole_rect.left = przesuniecie
            self.pola[i].pole_rect.top = przesuniecie+(przesuniecie*2+height)*i

            width = self.pola[i].pole_rect.width+przesuniecie*2
            height = self.pola[i].pole_rect.height+przesuniecie*2
            left = self.pola[i].pole_rect.left-przesuniecie
            top = self.pola[i].pole_rect.top-przesuniecie

            self.pola[i].zaznaczenie_rect = (left,top ,width, height)
            if width > self.menu_width:
                    self.menu_width = width
            self.menu_height += height
        x = self.dest_surface.get_rect().centerx - self.menu_width / 2
        y = self.dest_surface.get_rect().centery - self.menu_height / 2
        mx, my = self.pozycja_wklejenia
        self.pozycja_wklejenia = (x+mx, y+my)

if __name__ == "__main__":
    main()
