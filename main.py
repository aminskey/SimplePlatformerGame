import pygame, sys, random

from pygame.locals import *
from datetime import datetime
from time import sleep
from os import remove




pygame.init()
pygame.mixer.init

clock = pygame.time.Clock()

width = 800
height = 600


res = (width, height)

screen = pygame.display.set_mode(res)
pygame.display.set_caption('Test Game')

clouds = pygame.sprite.Group()
platforms = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
danger = pygame.sprite.Group()

BG = (52, 164, 235)

PlayerSpeed = 6

FPS = 120

vec = pygame.math.Vector2
highscore = vec(0, 0)

pygame.mixer.music.load('bgmusic.ogg')

class Clouds(pygame.sprite.Sprite):
	def __init__(self, pos):
		super().__init__()

		self.image = pygame.image.load('cloud.png')
		self.rect = self.image.get_rect()

		self.rect.center = pos

	def update(self):
		x, y = self.rect.center

		if x < -self.image.get_width() - 10:
			random.seed(datetime.now())
			x = width + self.image.get_width() + 10
			y = random.randrange(0, height//2)

		x-=1

		self.rect.center = (x, y)

class Platform(pygame.sprite.Sprite):
	def __init__(self, Landable):
		super().__init__()

		if Landable:
			self.image = pygame.image.load('platform_' + str(random.randint(0, 1)) + '.png')
		else:
			self.image = pygame.image.load('death.png')

		self.rect = self.image.get_rect()
		self.rect.center = (random.randrange(width * 1.25, width * 2), random.randrange(height * 1//3, height))
		self.pos = vec((self.rect.center))


class Player(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__()

		self.image = pygame.Surface((40, 40))
		self.image.fill((0, 255, 0))

		self.rect = self.image.get_rect()

		self.rect.center = (width//2, 0)

		self.acc = 2
		self.relpos = vec(self.rect.center)

		self.sound = pygame.mixer.Sound('jump.ogg')

		pygame.mixer.Sound.set_volume(self.sound, 0.04)


		self.jumpstate = False

	def move(self):

		x, y = self.rect.center

		keys = pygame.key.get_pressed()

		if pygame.sprite.spritecollide(self, platforms, False):
			plat = pygame.sprite.spritecollide(self, platforms, False)
			px, py = plat[0].rect.topleft

			if y <= py:
				x+=PlayerSpeed
				self.relpos.x += PlayerSpeed
		else:
			x+=PlayerSpeed
			self.relpos.x += PlayerSpeed

		self.rect.center = (x, y)

	def jump(self):

		x, y = self.rect.center


		keys = pygame.key.get_pressed()


		if keys[K_SPACE]:
			self.sound.play()
			y -= 20

		self.rect.center = (x, y)

	def gravity(self):

		x, y = self.rect.center

		if not pygame.sprite.spritecollide(self, platforms, False):
			y += self.acc
			self.acc += 0.5

			self.rect.center = (x, y)
		else:
			self.sound.stop()
			self.acc = 0
			self.rect.center = (x, y)


	def update(self):

		x, y = self.rect.topright

		if x > width * 2//3:
			x = width * 2//3

		self.rect.topright = (x, y)


		if pygame.sprite.spritecollide(self, platforms, False):
			plats = pygame.sprite.spritecollide(self, platforms, False)
			plat = plats[-1]
			platx, platy = plat.rect.midtop

			if y > platy:
				self.rect.topright = (platx, y)


		self.relpos.x += PlayerSpeed


#		self.move()
		self.jump()
		self.gravity()


class HighScoreLine(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__()

		self.image = pygame.Surface((20, height))
		self.image.fill((50, 50, 255))

		self.rect = self.image.get_rect()
		self.rect.center = (highscore.x, height/2)
		self.x, self.y = self.rect.center


def main():

	for i in range(40):
		new_cloud = Clouds((random.randrange(0, width), random.randrange(0, height * 1//2)))
		if not pygame.sprite.spritecollide(new_cloud, clouds, False):
			clouds.add(new_cloud)
			all_sprites.add(new_cloud)


	global highscore


	scoreLine = HighScoreLine()
	all_sprites.add(scoreLine)

	# defining player
	p1 = Player()
	all_sprites.add(p1)

	# Defining ground platform
	plat1 = Platform(True)

	plat1.image = pygame.transform.scale(plat1.image, (width, plat1.image.get_height()))
	plat1.rect = plat1.image.get_rect()
	plat1.rect.topleft = (0, height * 5//6 + 3)

	platforms.add(plat1)
	all_sprites.add(plat1)

	platx, platy = plat1.rect.center

	p1.start = vec(platx, platy)

	pygame.mixer.music.play(-1, 0)

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()


		screen.fill(BG)

		x, y = p1.rect.center

		for plat in platforms:
			px, py = plat.rect.center
			px -= PlayerSpeed
			plat.rect.center = (px, py)

		if x > scoreLine.x:
			scoreLine.x -= PlayerSpeed

		for i in range(1):
			random.seed(datetime.now())

			choice = random.randint(0, 8)

			if choice == 0:
				new_plat = Platform(False)
				danger.add(new_plat)
			else :
				new_plat = Platform(True)



			if not pygame.sprite.spritecollide(new_plat, platforms, False):
				platforms.add(new_plat)
				all_sprites.add(new_plat)
			else:
				new_plat.kill()


		if y > height * 2 or pygame.sprite.spritecollide(p1, danger, False) or x < 0:
			gameOver(p1, highscore)

		i = 0
		for plat in platforms:
			i+=1
			px, py = plat.rect.topright
			if plat == plat1:
				continue
			elif px <= 0 or i > 10:
				plat.kill()

		if p1.relpos.x >= highscore.x:
			highscore.x = p1.relpos.x
			scoreLine.x = x
		else:
			scoreLine.x = highscore.x

		scoreLine.rect.center = (scoreLine.x, height//2)

		clouds.update()
		p1.update()

		all_sprites.draw(screen)

		pygame.display.update()
		clock.tick(FPS)

def startScreen():

	header = pygame.font.Font('pixelart.ttf', 50)
	sub = pygame.font.Font('pixelart.ttf', 25)

	title = header.render('Simple Platformer', BG, (255, 255, 255))

	start = sub.render('Start', BG, (255, 255, 255))
	exit = sub.render('Quit', BG, (255, 255, 255))

	cursor = sub.render('->', BG, (155, 255, 200))

	titleRect = title.get_rect()

	startRect = start.get_rect()
	exitRect = exit.get_rect()

	cursorRect = cursor.get_rect()

	titleRect.center = (width/2, height * 1//3)

	startRect.center = (width/2, height * 1//2 - 10)
	exitRect.center = (width/2, height * 1//2 + 10)

	cursorRect.center = (width//2 - 50, height * 1//2 - 10)

	x, y = cursorRect.center

	sx, sy = startRect.center
	ex, ey = exitRect.center

	while True:

		for event in pygame.event.get():
			key = pygame.key.get_pressed()
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == KEYDOWN:

				if key[K_UP]:
					y -= 20
				if key[K_DOWN]:
					y += 20

				if key[K_RETURN]:
					if y == ey:
						pygame.mixer.music.unload()
						pygame.quit()
						sys.exit()
					elif y == sy:
						main()
					break

				if y > ey:
					y = sy
				if y < sy:
					s = ey






		cursorRect.center = (x, y)

		screen.fill(BG)

		screen.blit(title, titleRect)
		screen.blit(start, startRect)
		screen.blit(exit, exitRect)
		screen.blit(cursor, cursorRect)

		pygame.display.update()


def gameOver(p1, highscore):
	sleep(0.25)

	pygame.mixer.music.stop()

	header = pygame.font.Font('pixelart.ttf', 40)
	sub = pygame.font.Font('pixelart.ttf', 20)

	text = header.render('Game Over: ' + str(p1.relpos.x), BG, (255, 255, 255))
	text2 = sub.render('Press anything to continue', BG, (255, 255, 255))
	score = sub.render('Current Highscore: ' + str(highscore.x), BG, (255, 255, 255))

	textRect = text.get_rect()
	text2Rect = text2.get_rect()
	scoreRect = score.get_rect()

	textRect.midbottom = (width // 2, height//3)
	text2Rect.midbottom = (width // 2, height * 3//6)
	scoreRect.midbottom = (width // 2, height * 3//12)

	screen.blit(text, textRect)
	screen.blit(score, scoreRect)
	screen.blit(text2, text2Rect)

	while True:
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				sleep(0.25)
				for sprite in all_sprites:
					sprite.kill()
				startScreen()
				break
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()

		pygame.display.flip()

startScreen()
