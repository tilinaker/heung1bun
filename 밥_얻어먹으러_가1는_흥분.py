import sys
import pygame
from pygame.locals import *
from moviepy.editor import VideoFileClip

BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (0, 0, 0)
SKY_BLUE = (85, 196, 255)

SCREENWIDTH = 720
SCREENHEIGHT = 405

FPS = 60


class Excitement(pygame.sprite.Sprite):
    def __init__(self, image, pos):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image)
        self.position = list(pos)

        self.gravity = 150  # 중력 가속도 양수인 이유는 파이게임에서 아래쪽으로 갈수록 Y가 커지니까
        self.yv = 0  # Y방향 속도
        self.dx = 0

        self.on_ground = False

        self.rect = self.image.get_rect()
        self.rect.center = self.position

        self.speed = 1  # pixel/frame
        self.jump_speed = -100

    def update(self, platform_list):
        self.rect = self.image.get_rect()
        self.rect.center = self.position

        # 사망 확인
        if self.rect.bottom > SCREENHEIGHT:
            return True, False
        else:
            if self.rect.right > SCREENWIDTH:
                return False, True

        # 발판에 닿았는지 확인
        self.on_ground = False
        for platform in platform_list:
            # 함정에 걸린 경우
            if ((platform.rect.left <= self.rect.left <= platform.rect.right) or
                (platform.rect.left <= self.rect.right <= platform.rect.right) or
                (self.rect.left <= platform.rect.left <= self.rect.right) or
                (self.rect.left <= platform.rect.right <= self.rect.right)) and \
                    ((platform.rect.top <= self.rect.top <= platform.rect.bottom) or
                     (platform.rect.top <= self.rect.bottom <= platform.rect.bottom) or
                     (self.rect.top <= platform.rect.top <= self.rect.bottom) or
                     (self.rect.top <= platform.rect.bottom <= self.rect.bottom)) and \
                    platform.is_trap:
                return True, False
            # 바닥에 발판이 있는 경우
            elif ((platform.rect.left <= self.rect.left <= platform.rect.right) or
                  (platform.rect.left <= self.rect.right <= platform.rect.right) or
                  (self.rect.left <= platform.rect.left <= self.rect.right) or
                  (self.rect.left <= platform.rect.right <= self.rect.right)) and \
                    (platform.rect.top < self.rect.bottom + self.yv / FPS < platform.rect.bottom):
                if self.yv > 0:
                    self.yv = 0
                self.position[1] = platform.rect.top - (self.rect.bottom - self.rect.center[1])
                self.on_ground = True
            # 위에 발판이 있는 경우
            elif ((platform.rect.left <= self.rect.left <= platform.rect.right) or
                  (platform.rect.left <= self.rect.right <= platform.rect.right) or
                  (self.rect.left <= platform.rect.left <= self.rect.right) or
                  (self.rect.left <= platform.rect.right <= self.rect.right)) and \
                    ((platform.rect.top < self.rect.top < platform.rect.bottom) or
                     (platform.rect.top < self.rect.bottom < platform.rect.bottom) or
                     (self.rect.top < platform.rect.top < self.rect.bottom) or
                     (self.rect.top < platform.rect.bottom < self.rect.bottom)):
                if self.yv < 0:
                    self.yv = 0
            # 양 옆으로 움직이지 못할 경우
            if ((platform.rect.left <= self.rect.left + self.dx <= platform.rect.right) or
                (platform.rect.left <= self.rect.right + self.dx <= platform.rect.right) or
                (self.rect.left + self.dx <= platform.rect.left <= self.rect.right + self.dx) or
                (self.rect.left + self.dx <= platform.rect.right <= self.rect.right + self.dx)) and \
                    ((platform.rect.top < self.rect.top < platform.rect.bottom) or
                     (platform.rect.top < self.rect.bottom < platform.rect.bottom) or
                     (self.rect.top < platform.rect.top < self.rect.bottom) or
                     (self.rect.top < platform.rect.bottom < self.rect.bottom)):
                self.dx = 0
                if platform.is_trap:
                    return True, False

        self.position[1] += round(self.yv / FPS)  # 적1분
        self.yv += self.gravity / FPS  # 적1분
        self.position[0] += self.dx
        self.dx = 0

        return False, False

    def move(self, amount):
        self.dx += amount

    def move_right(self):
        self.move(self.speed)

    def move_left(self):
        self.move(-self.speed)

    def jump(self):
        if self.on_ground:
            self.yv += self.jump_speed

    def reset(self, pos):
        self.position = list(pos)
        self.yv = 0


class PlatForm(pygame.sprite.Sprite):
    def __init__(self, image, pos, trap=False):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image)
        self.position = list(pos)

        self.rect = self.image.get_rect()
        self.rect.center = self.position

        self.is_trap = trap

    def update(self, *args):
        self.rect = self.image.get_rect()
        self.rect.center = self.position


class MovingPlatForm(PlatForm):
    def __init__(self, image, pos, speed, trap=False, range_width=SCREENWIDTH, range_height=SCREENHEIGHT):
        super().__init__(image, pos, trap)
        self.speed = list(speed)
        self.origin = pos

        self.range_width = range_width
        self.range_height = range_height

    def update(self, *args):
        super().update()
        self.position[0] = (self.position[0]+self.speed[0])
        self.position[1] = (self.position[1]+self.speed[1])
        if abs(self.position[0] - self.origin[0]) >= self.range_width//2:
            self.speed[0] *= - 1
        if abs(self.position[1] - self.origin[1]) >= self.range_height // 2:
                self.speed[1] *= - 1


def play_movie(name):
    clip = VideoFileClip(name).resize(width=SCREENWIDTH)
    clip.preview()


def title_screen():
    while True:
        for _event in pygame.event.get():
            if _event.type == QUIT:
                pygame.quit()
                sys.exit()

            if _event.type == KEYDOWN:
                return None

        font32 = pygame.font.Font("resources/Font/NanumBarunGothic.ttf", 32)
        font14 = pygame.font.Font("resources/Font/NanumBarunGothic.ttf", 14)

        text_surface1 = font32.render("밥 얻어먹으러 가1는 흥분", True, BLACK)
        rect1 = text_surface1.get_rect()
        rect1.center = (SCREENWIDTH // 2, SCREENHEIGHT // 2)
        screen.blit(text_surface1, rect1)

        text_surface2 = font14.render("아무 키나 눌1러서 시작하세요", True, BLACK)
        rect2 = text_surface2.get_rect()
        rect2.center = (SCREENWIDTH // 2, SCREENHEIGHT // 2 + 30)
        screen.blit(text_surface2, rect2)

        clock.tick(FPS)
        pygame.display.flip()
        screen.fill(SKY_BLUE)


def clear():
    play_movie("resources\\Video\\클리어.mp4")
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT), DOUBLEBUF)
    pygame.display.set_caption("밥얻어먹으러 가1는 흥분")

    clock = pygame.time.Clock()

    bgm = pygame.mixer.Sound("resources\\Audio\\bgm.wav")
    bgm.play(-1)

    current_lv = 0

    levels = [
        [
            PlatForm("resources\\Image\\stone.png", (100, 200)),
            PlatForm("resources\\Image\\stone.png", (220, 200)),
            PlatForm("resources\\Image\\stone.png", (340, 200)),
            PlatForm("resources\\Image\\stone.png", (460, 200)),
            PlatForm("resources\\Image\\stone.png", (580, 200)),
            PlatForm("resources\\Image\\stone.png", (700, 200)),
        ],
        [
            PlatForm("resources\\Image\\stone.png", (100, 200)),
            PlatForm("resources\\Image\\stone.png", (240, 250)),
            PlatForm("resources\\Image\\stone.png", (340, 220)),
            PlatForm("resources\\Image\\stone.png", (470, 220)),
            PlatForm("resources\\Image\\stone.png", (640, 220)),
        ],
        [
            PlatForm("resources\\Image\\잔디.png", (100, 200)),
            PlatForm("resources\\Image\\잔디.png", (220, 200)),
            PlatForm("resources\\Image\\함정.png", (250, 220), True),
            PlatForm("resources\\Image\\잔디.png", (260, 180)),
            PlatForm("resources\\Image\\잔디.png", (350, 178)),
            PlatForm("resources\\Image\\함정.png", (300, 203), True),
            PlatForm("resources\\Image\\함정.png", (398, 300), True),
            PlatForm("resources\\Image\\잔디.png", (360, 300)),
            PlatForm("resources\\Image\\stone.png", (330, 420)),
            PlatForm("resources\\Image\\stone.png", (380, 420)),
            PlatForm("resources\\Image\\stone.png", (430, 420)),
            PlatForm("resources\\Image\\stone.png", (590, 420)),
            PlatForm("resources\\Image\\stone.png", (640, 420)),
        ],
        [
            PlatForm("resources\\Image\\함정.png", (100, 200), True),
            PlatForm("resources\\Image\\stone.png", (150, 300)),
            PlatForm("resources\\Image\\돌.png", (300, 300)),
            PlatForm("resources\\Image\\stone.png", (400, 300)),
            MovingPlatForm("resources\\Image\\함정.png", (450, SCREENHEIGHT // 2), (0, 3), True),
            PlatForm("resources\\Image\\stone.png", (500, 300)),
            PlatForm("resources\\Image\\stone.png", (600, 300)),
        ],
        [
            PlatForm("resources\\Image\\stone.png", (100, 400)),
            PlatForm("resources\\Image\\stone.png", (150, 400)),
            PlatForm("resources\\Image\\stone.png", (200, 400)),
            PlatForm("resources\\Image\\stone.png", (250, 400)),
            PlatForm("resources\\Image\\함정.png", (175, 300), True),
            PlatForm("resources\\Image\\함정.png", (265, 380), True),
            PlatForm("resources\\Image\\돌.png", (270, 350)),
            PlatForm("resources\\Image\\함정.png", (340, 340), True),
            PlatForm("resources\\Image\\stone.png", (300, 350)),
            PlatForm("resources\\Image\\돌.png", (340, 305)),
            PlatForm("resources\\Image\\돌.png", (465, 315)),
            PlatForm("resources\\Image\\돌.png", (590, 325)),
        ],
        [
            PlatForm("resources\\Image\\stone.png", (100, 400)),
            MovingPlatForm("resources\\Image\\stone.png", (400, 400), (1, 0), False, 450),
            PlatForm("resources\\Image\\오1줌.png", (300, 395), True),
            PlatForm("resources\\Image\\오1줌.png", (400, 395), True),
            PlatForm("resources\\Image\\오1줌.png", (500, 395), True),
            PlatForm("resources\\Image\\오1줌.png", (600, 395), True),
            PlatForm("resources\\Image\\stone.png", (700, 400)),
        ],
        [
            PlatForm("resources\\Image\\stone.png", (100, 400)),
            PlatForm("resources\\Image\\stone.png", (150, 400)),
            PlatForm("resources\\Image\\stone.png", (200, 400)),
            PlatForm("resources\\Image\\stone.png", (250, 400)),
            PlatForm("resources\\Image\\stone.png", (300, 400)),
            PlatForm("resources\\Image\\stone.png", (350, 400)),
            PlatForm("resources\\Image\\stone.png", (400, 400)),
            PlatForm("resources\\Image\\stone.png", (450, 400)),
            PlatForm("resources\\Image\\stone.png", (500, 400)),
            PlatForm("resources\\Image\\stone.png", (550, 400)),
            PlatForm("resources\\Image\\stone.png", (600, 400)),
            PlatForm("resources\\Image\\stone.png", (650, 400)),
            PlatForm("resources\\Image\\stone.png", (700, 400)),

            ("resources\\Image\\오1줌.png", (200, SCREENHEIGHT//2), (0, 10), True),
            MovingPlatForm("resources\\Image\\오1줌.png", (300, SCREENHEIGHT // 2), (0, 10), True),
            MovingPlatForm("resources\\Image\\오1줌.png", (400, SCREENHEIGHT // 2), (0, 10), True),

            PlatForm("resources\\Image\\오1줌.png", (550, 395)),
            PlatForm("resources\\Image\\함정.png", (630, 300), True)
        ],
    ]

    title_screen()

    play_movie("resources\\Video\\오프닝.mp4")

    while True:

        bgm.play(-1)

        excitement = Excitement("resources\\Image\\캐릭터.png", (100, 100))
        excitement_group = pygame.sprite.RenderPlain(excitement)

        dead = False
        cleared = False

        map_group = pygame.sprite.RenderPlain(*(levels[current_lv]))

        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        excitement.jump()

            key = pygame.key.get_pressed()
            if key[K_a]:
                excitement.move_left()
            if key[K_d]:
                excitement.move_right()

            screen.fill(SKY_BLUE)

            dead, cleared = excitement.update(levels[current_lv])
            map_group.update()

            map_group.draw(screen)
            excitement_group.draw(screen)

            if dead:
                break
            if cleared:
                current_lv += 1

                if current_lv >= len(levels):
                    clear()
                map_group = pygame.sprite.RenderPlain(*(levels[current_lv]))

                excitement.reset((100, 100))

            clock.tick(FPS)
            pygame.display.flip()

        play_movie("resources\\Video\\사망.mp4")
        bgm.play(-1)
