# full imports
import pygame, sys, random

# import specific methods
from pygame.locals import *
from datetime import datetime
from time import sleep, time
from os import remove
from warnings import filterwarnings

# filter warning
filterwarnings('ignore', category=DeprecationWarning)

# initiate sound and graphics
pygame.init()
pygame.mixer.init()

# Create FPS handler
clock = pygame.time.Clock()

# Resolution
width = 800
height = 600

# resolution tuple
res = (width, height)

# Game name
name = 'Sky Dash'

# Setting up window
screen = pygame.display.set_mode(res)
pygame.display.set_caption(name)

# Sprite Groups
clouds = pygame.sprite.Group()
platforms = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
danger = pygame.sprite.Group()
players = pygame.sprite.Group()
seagulls = pygame.sprite.Group()
planes = pygame.sprite.Group()


# text and screen background
BG = (52, 164, 235)
BG2 = (100, 100, 255)

# Invisible mouse
pygame.mouse.set_visible(False)

# Initial Player speed
PSD = 4

# player speed
PlayerSpeed = PSD

CHANCE = 256
# 1/256 = 0.25% chance of lava block

FPS = 110

# Calculating Players position relative to start
vec = pygame.math.Vector2
highscore = vec(0, 0)

# Clouds Class
class Clouds(pygame.sprite.Sprite):
	# General settings
	def __init__(self, pos):
		super().__init__()

		self.image = pygame.image.load('backgroundObjects/cloud.png')
		self.rect = self.image.get_rect()

		self.rect.center = pos

	# Make them move in the air
	def update(self):
		x, y = self.rect.center

		# if out of window then respawn ahead of widthspan
		if x < -self.image.get_width() - 10:
			random.seed(datetime.now())
			x = width + self.image.get_width() + 10
			y = random.randrange(0, height)

		# slowly drift backwards creating virtual effect
		x-=1

		self.rect.center = (x, y)

# platform mechanism
class Platform(pygame.sprite.Sprite):
	# initial settings
	# asking Program if landable
	def __init__(self, Landable, image=None):
		super().__init__()

		# if there is no specific image then use random
		# if not landable then use lava block image.
		if image == None:
			if Landable:
				self.image = pygame.image.load('platforms/platform_' + str(random.randint(0, 2)) + '.png')
			else:
				self.image = pygame.image.load('badObjects/lavablock.png')
		else:
			self.image = pygame.image.load(image)

		# General settings
		self.rect = self.image.get_rect()
		self.rect.center = (random.randrange(width * 1.25, width * 2.5), random.randrange(height * 8//12, height * 5//6))
		self.pos = vec((self.rect.center))

# Seagulls class
class Seagull(pygame.sprite.Sprite):
	# initial settings
	def __init__(self):
		super().__init__()

		self.image = pygame.image.load('badObjects/seagull.png')

		self.rect = self.image.get_rect()
		self.rect.center = (random.randrange(width, width * 2), random.randrange(height * 1//6, height * 5//24))

		self.x, self.y = self.rect.center

	# Update mechanism
	def update(self):
		self.x -= PlayerSpeed * 1.15
		self.rect.center = (self.x, self.y)

		# if seagull out of screen then kill it
		if self.x < 0:
			all_sprites.remove(self)
			danger.remove(self)
			seagulls.remove(self)

			self.kill()

# Planes Class
class Plane(pygame.sprite.Sprite):
	# Initial settings
	def __init__(self, alpha):
		super().__init__()

		self.image = pygame.image.load('backgroundObjects/planes-' + str(random.randrange(0, 1)) + '.png')

		self.image.set_alpha(alpha)

		self.rect = self.image.get_rect()
		self.rect.center = (random.randrange(width * 1.5, width * 2.5), random.randrange(0, height * 2//3))

		self.x, self.y = self.rect.center

	def update(self, speed):
		self.x -= speed

		if self.x < 0 - self.image.get_width():
			random.seed(datetime.now())
			self.x = width + self.image.get_width()
			self.y = random.randrange(0, height * 2//3)


		self.rect.center = (self.x, self.y)


# Player class
class Player(pygame.sprite.Sprite):
	# initial settings
	def __init__(self):
		super().__init__()

		self.image = pygame.Surface((40, 40))
		self.image.fill((120, 255, 120))

		self.rect = self.image.get_rect()

		self.rect.center = (width//2, 0)

		self.acc = 1
		self.relpos = vec(self.rect.center)


		self.jumpstate = True

	# Jump mechanism
	def jump(self):

		x, y = self.rect.center


		# key mapping
		keys = pygame.key.get_pressed()
		mkeys = pygame.mouse.get_pressed()


		# Event handling
		if keys[K_SPACE] or mkeys[0]:

			# jumping
			y -= 20

		# Updating position
		self.rect.center = (x, y)

	# Gravity mechanism
	def gravity(self):

		x, y = self.rect.center

		# checking for collision
		# If not then continue falling and updating position
		if not pygame.sprite.spritecollide(self, platforms, False):
			y += self.acc
			self.acc += 0.4

			self.rect.center = (x, y)
		# else stop and update position
		else:
			self.acc = 0
			self.rect.center = (x, y)



	# The Update mechanism
	def update(self):

		x, y = self.rect.midtop

		# Creating bounding box
		if x > width * 2//3:
			x = width * 2//3

		# Updating Position
		self.rect.midtop = (x, y)


		# Checking for collision
		if pygame.sprite.spritecollide(self, platforms, False):

			plats = pygame.sprite.spritecollide(self, platforms, False)
			plat = plats[-1]
			platx, platy = plat.rect.midtop

			plat_w = plat.image.get_width()
			plat_h = plat.image.get_height()

			# If player collides with platform and is deep in the block
			# Then stop all motion except for jumping mechanism
			if y > platy and x > (platx + plat_w * 1//3) and x < (platx + plat_w * 2//3):
				self.jumpstate = False
				self.rect.midtop = (platx, y)
			else:
				self.jumpstate = True


		# Updating relative position
		self.relpos.x += PlayerSpeed

		# If not in air allow jump mechanism
		if self.jumpstate:
			self.jump()

		# Running virtual gravity method
		self.gravity()

# ScoreLine class
class HighScoreLine(Player):
	def __init__(self):
		super().__init__()

		self.image = pygame.Surface((20, height))
		self.image.fill((10, 10, 255))

		self.image.set_alpha(50)

		self.rect = self.image.get_rect()
		self.rect.center = (highscore.x, height/2)
		self.x, self.y = self.rect.center

def main():
	# choosing random background song.
	pygame.mixer.music.load('songs/song-' + str(random.randint(0, 5)) +'.ogg')
	sleep(0.25)
	for i in range(8):
		pygame.mixer.music.queue('songs/song-' + str(random.randint(0, 5)) +'.ogg')

	# planes in the background
	for i in range(2):
		new_plane = Plane(random.randrange(200, 255))

		if not pygame.sprite.spritecollide(new_plane, planes, False):
			planes.add(new_plane)
			all_sprites.add(new_plane)

	# Creating background clouds
	for i in range(20):
		new_cloud = Clouds((random.randrange(0, width), random.randrange(0, height)))

		if not pygame.sprite.spritecollide(new_cloud, clouds, False):
			clouds.add(new_cloud)
			all_sprites.add(new_cloud)

	for i in range(2):
		new_plane = Plane(random.randrange(200, 255))

		if not pygame.sprite.spritecollide(new_plane, planes, False):
			planes.add(new_plane)
			all_sprites.add(new_plane)

	# Importing global variables
	global highscore
	global PlayerSpeed
	global CHANCE

	# Creating scoreLine
	scoreLine = HighScoreLine()
	all_sprites.add(scoreLine)

	# defining player
	p1 = Player()
	all_sprites.add(p1)
	players.add(p1)

	# Defining ground platform
	plat1 = Platform(True, 'platforms/platform_0.png')

	# Customizing platform
	plat1.image = pygame.transform.scale(plat1.image, (width, plat1.image.get_height()))
	plat1.rect = plat1.image.get_rect()
	plat1.rect.topleft = (0, height * 5//6 + 3)

	# Add initial platform to groups
	platforms.add(plat1)
	all_sprites.add(plat1)

	# loop the background music
	pygame.mixer.music.play(0, 0)


	# Creating Fixed Plane speed
	PlaneSpeed = random.randrange(2, 4)

	# Creating font object
	sub = pygame.font.Font('fonts/pixelart.ttf', 25)

	while True:

		# PlayerSpeed Text
		ps1 = sub.render('Player Speed:', BG2, (55, 55, 255))
		ps2 = sub.render(str(PlayerSpeed), BG2, (55, 55, 255))

		# Rectangle
		ps1Rect = ps1.get_rect()
		ps2Rect = ps2.get_rect()

		# Position
		ps1Rect.center = (width * 6//16, ps1.get_height()*3)
		ps2Rect.center = (width * 11//16, ps2.get_height()*3)

		# HUD highscore text
		hs1 = sub.render('Current Highscore: ', BG2, (55,55,255))
		hs2 = sub.render(str(highscore.x//100), BG2, (55, 55, 255))

		# text rectangle
		hs1Rect = hs1.get_rect()
		hs2Rect = hs2.get_rect()

		# Positioning text
		hs1Rect.center = (width * 6//16, hs1.get_height())
		hs2Rect.center = (width * 11//16, hs2.get_height())



		# HUD Player text
		score1 = sub.render('Player Score', BG2, (55,55,255))
		score2 = sub.render(str(p1.relpos.x//100), BG2, (55,55,255))

		# text rectangle
		score1Rect = score1.get_rect()
		score2Rect = score2.get_rect()

		# Positioning text
		score1Rect.center = (width * 6//16, score1.get_height()*2)
		score2Rect.center = (width  * 11//16, score2.get_height()*2)

		# Window event handler
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()


		screen.fill(BG)

		x, y = p1.rect.center

		# Making the platforms move to create an illusion
		# That the player is moving
		for plat in platforms:
			px, py = plat.rect.center
			px -= PlayerSpeed
			plat.rect.center = (px, py)


		# if player's x is greater than highscore bar's x
		# Then update it
		if x > scoreLine.x:
			scoreLine.x -= PlayerSpeed


		# Put in for loop for user to increase game intensity
		for i in range(1):
			# randomizing chance
			# same logic as the seagull (l. 399) but with lava blocks
			# but not dependent on distance
			random.seed(datetime.now())

			choice = random.randint(0, CHANCE)

			if choice == 0:
				new_plat = Platform(False)
				danger.add(new_plat)
			else :
				new_plat = Platform(True)


			# if platforms overlap
			# remove them
			if not pygame.sprite.spritecollide(new_plat, platforms, False):
				platforms.add(new_plat)
				all_sprites.add(new_plat)
			else:
				new_plat.kill()

		# checking if the player died
		# If it happened then reset settings and run gameOver method
		if y > height * 2 or pygame.sprite.spritecollide(p1, danger, False) or x < 0:
			PlayerSpeed = PSD
			CHANCE = 128
			gameOver(p1, highscore)

		# if platform is out of screen or if there are more than 10 platforms then destroy
		i = 0
		for plat in platforms:
			i+=1
			px, py = plat.rect.topright
			if px <= 0 or i > 10:
				plat.kill()

		# Seagull will most likely spawn after player score is 30. May not happen at 30 due to chance of spawn
		if p1.relpos.x > 15000:
			# Chance of a seagull spawning
			choice = random.randint(0, CHANCE)

			# If true then spawn
			if choice == 0:
				for i in range(random.randrange(0, 3)):
					new_seagull = Seagull()

					if not pygame.sprite.spritecollide(new_seagull, seagulls, False):
						seagulls.add(new_seagull)
						all_sprites.add(new_seagull)
						danger.add(new_seagull)

		# Checking if player's relative position greater then highscore position
		# If yes then update
		if p1.relpos.x >= highscore.x:
			highscore.x = p1.relpos.x
			scoreLine.x = x
		else:
			scoreLine.x = highscore.x

		# When players score divided by 100 gives a remainder of 0.
		# And if player score not zero its self

		if p1.relpos.x % 2000 == 0 and p1.relpos.x != 0:
			PlayerSpeed += 1

		# 1/chancenumber divided by 105/100
			CHANCE //=1.05


		# Updating scoreline
		scoreLine.rect.center = (scoreLine.x, height//2)


		# Updating sprite groups
		planes.update(PlaneSpeed)
		clouds.update()
		seagulls.update()
		p1.update()

		# Drawing all sprites to screen
		all_sprites.draw(screen)

		# Sending Highscore and player score data to screen
		screen.blit(hs1, hs1Rect)
		screen.blit(hs2, hs2Rect)

		screen.blit(score1, score1Rect)
		screen.blit(score2, score2Rect)

		screen.blit(ps1, ps1Rect)
		screen.blit(ps2, ps2Rect)

		# Refreshing screen
		pygame.display.update()

		# Fixed Frame rate 120 recommended unless old computer
		clock.tick(FPS)

	pygame.mixer.music.unload()

def startScreen():

	pygame.mixer.music.load('songs/startup.ogg')

	header = pygame.font.Font('fonts/pixelart.ttf', 50)
	sub = pygame.font.Font('fonts/pixelart.ttf', 25)

	title = header.render(name, BG, (230, 230, 230))
	start = sub.render('Start', BG, (230, 230, 230))
	exit = sub.render('Quit', BG, (230, 230, 230))

	cursor = sub.render('->', BG, (100, 255, 100))

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

	cloudsGroup1 = pygame.sprite.Group()
	cloudsGroup2 = pygame.sprite.Group()

	for i in range(30):
		new_cloud = Clouds((random.randrange(0, width), random.randrange(0, height)))

		if not pygame.sprite.spritecollide(new_cloud, cloudsGroup1, False):
			cloudsGroup1.add(new_cloud)

	sleep(0.125)

	for i in range(10):
		new_cloud = Clouds((random.randrange(0, width), random.randrange(0, height)))

		if not pygame.sprite.spritecollide(new_cloud, cloudsGroup2, False):
			cloudsGroup2.add(new_cloud)

	pygame.mixer.music.play(-1, 0)
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
				if key[K_p]:
					pygame.mixer.quit()
				if key[K_u]:
					pygame.mixer.init()


				if key[K_RETURN]:
					if y == ey:
						pygame.mixer.music.stop()
						pygame.quit()
						sys.exit()
					elif y == sy:
						pygame.mixer.music.stop()
						main()
						break

				if y > ey:
					y = sy
				if y < sy:
					y = ey






		cursorRect.center = (x, y)

		screen.fill(BG)

		cloudsGroup1.draw(screen)
		cloudsGroup1.update()

		screen.blit(title, titleRect)
		screen.blit(start, startRect)
		screen.blit(exit, exitRect)
		screen.blit(cursor, cursorRect)

		cloudsGroup2.draw(screen)
		cloudsGroup2.update()


		pygame.display.update()
		clock.tick(FPS)


def gameOver(p1, highscore):


	pygame.mixer.music.load('sounds/gameOver.ogg')
	if p1.relpos.x >= highscore.x:
		highscore.x = p1.relpos.x


	pygame.mixer.music.stop()

	header = pygame.font.Font('fonts/pixelart.ttf', 40)
	sub = pygame.font.Font('fonts/pixelart.ttf', 20)

	text = header.render('Game Over: ' + str(p1.relpos.x//100), BG, (255, 255, 255))
	text2 = sub.render('Press anything to continue', BG, (255, 255, 255))
	score = sub.render('Current Highscore: ' + str(highscore.x//100), BG, (255, 255, 255))

	textRect = text.get_rect()
	text2Rect = text2.get_rect()
	scoreRect = score.get_rect()

	textRect.midbottom = (width // 2, height//3)
	text2Rect.midbottom = (width // 2, height * 3//6)
	scoreRect.midbottom = (width // 2, height * 3//12)

	screen.blit(text, textRect)
	screen.blit(score, scoreRect)
	screen.blit(text2, text2Rect)

	pygame.mixer.music.play(0, 0)
	pygame.display.flip()
	sleep(0.75)


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
