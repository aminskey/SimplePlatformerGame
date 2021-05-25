import pygame, sys, random

from pygame.locals import *
from datetime import datetime

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
	def __init__(self):
		super().__init__()

		self.image = pygame.image.load('platform.png')

		self.rect = self.image.get_rect()
		self.rect.topleft = (random.randrange(width, width * 1.25), random.randrange(height * 1//3, height))


class Player(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__()

		self.image = pygame.Surface((20, 40))
		self.image.fill((0, 255, 0))

		self.rect = self.image.get_rect()

		self.acc = 2

		self.jumping = 0

	def move(self):

		x, y = self.rect.center

		keys = pygame.key.get_pressed()

		if pygame.sprite.spritecollide(self, platforms, False):
			plat = pygame.sprite.spritecollide(self, platforms, False)
			px, py = plat[0].rect.topleft

			if y <= py:
				if keys[K_LEFT]:
					x -= PlayerSpeed
				if keys[K_RIGHT]:
					x+=PlayerSpeed
		else:
			if keys[K_LEFT]:
				x -= PlayerSpeed
			if keys[K_RIGHT]:
				x+=PlayerSpeed


		self.rect.center = (x, y)

	def jump(self):

		x, y = self.rect.center


		keys = pygame.key.get_pressed()

		if keys[K_SPACE]:
			y -= 15

		self.rect.center = (x, y)

	def gravity(self):
		x, y = self.rect.midbottom

		if not pygame.sprite.spritecollide(self, platforms, False):
			y += self.acc
			self.acc += 0.5

			self.rect.midbottom = (x, y)
		else:
			self.acc = 0
			self.rect.midbottom = (x, y)


	def update(self):

		x, y = self.rect.center

		if x > width * 2//3:
			x = width * 2//3
		if x < width * 1//3:
			x = width * 1//3

		self.rect.center = (x, y)

		self.move()
		self.jump()
		self.gravity()

		if pygame.sprite.spritecollide(self, platforms, False):
			self.jumping = 0



pygame.init()
clock = pygame.time.Clock()

width = 800
height = 600

res = (width, height)

screen = pygame.display.set_mode(res)
pygame.display.set_caption('Test Game')

clouds = pygame.sprite.Group()
platforms = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

BG = (52, 164, 235)

PlayerSpeed = 5

FPS = 120

def main():

	for i in range(40):
		new_cloud = Clouds((random.randrange(0, width), random.randrange(0, height * 1//2)))
		if not pygame.sprite.spritecollide(new_cloud, clouds, False):
			clouds.add(new_cloud)
			all_sprites.add(new_cloud)




	# defining player
	p1 = Player()
	all_sprites.add(p1)
	# flag = Goal()

	# Defining ground platform
	plat1 = Platform()

	plat1.image = pygame.transform.scale(plat1.image, (width, plat1.image.get_height()))
	plat1.rect = plat1.image.get_rect()
	plat1.rect.topleft = (0, height * 5//6 + 3)

	platforms.add(plat1)
	all_sprites.add(plat1)

	'''
	platforms.add(flag)
	all_sprites.add(flag)
	'''

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()


		screen.fill(BG)

		x, y = p1.rect.center

		if x > width * 2//3:
			for plat in platforms:
				px, py = plat.rect.center
				px -= PlayerSpeed
				plat.rect.center = (px, py)

			for i in range(2):
				new_plat = Platform()
				if not pygame.sprite.spritecollide(new_plat, platforms, False):
					platforms.add(new_plat)
					all_sprites.add(new_plat)
				else:
					new_plat.kill()


		if x < width * 1//3:
			for plat in platforms:
				px, py = plat.rect.center
				px += PlayerSpeed
				plat.rect.center = (px, py)


		if y > height:
			gameOver()

		i = 0
		for plat in platforms:
			i+=1
			px, py = plat.rect.topright
			if px <= 0 or i > 10:
				plat.kill()

		clouds.update()
		p1.update()

		all_sprites.draw(screen)

		pygame.display.update()
		clock.tick(FPS)

def gameOver():
	header = pygame.font.Font('pixelart.ttf', 40)
	sub = pygame.font.Font('pixelart.ttf', 20)

	text = header.render('Game Over', BG, (255, 255, 255))
	text2 = sub.render('Press anything to continue', BG, (255, 255, 255))

	textRect = text.get_rect()
	text2Rect = text.get_rect()

	textRect.midbottom = (width // 2, height//3)
	text2Rect.midbottom = (width // 2, height * 2//3)

	screen.blit(text, textRect)
	screen.blit(text2, text2Rect)

	while True:
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				for sprite in all_sprites:
					sprite.kill()
				main()
				break
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()

		pygame.display.flip()

main()
