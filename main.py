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
width = 900
height = 700

# resolution tuple
res = (width, height)

firstEntry = True

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


# Joystick init
p1Pad = pygame.joystick.Joystick(0)
p1Pad.init()

# text and screen background
BG = (52, 164, 235)
BG2 = (100, 100, 255)

# Invisible mouse
pygame.mouse.set_visible(False)

# Initial Player speed
PSD = 3

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
				self.image = pygame.image.load('platforms/platform_' + str(random.randint(0, 5)) + '.png')
			else:
				self.image = pygame.image.load('badObjects/badplat' + str(random.randint(0,2))+'.png')
		else:
			self.image = pygame.image.load(image)

		# General settings
		self.rect = self.image.get_rect()
		self.rect.center = (random.randrange(width * 1.25, width * 2), random.randrange(height * 8//12, height * 5//6))
		self.pos = vec((self.rect.center))

# Seagulls class
class Seagull(pygame.sprite.Sprite):
	# initial settings
	def __init__(self):
		super().__init__()

		self.image = pygame.image.load('badObjects/seagull.png')

		self.rect = self.image.get_rect()
		self.rect.center = (random.randint(width, width * 2), random.randint(0, height * 5//24))

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

# Player class
class Player(pygame.sprite.Sprite):
	# initial settings
	def __init__(self):
		super().__init__()

		self.image = pygame.image.load("player.png")
		self.image = pygame.transform.scale(self.image, (40, 40))

		self.rect = self.image.get_rect()

		self.rect.center = (width//2, 0)

		self.acc = 0
		self.relpos = vec(self.rect.center)

		self.jumpstate = True

	# Jump mechanism
	def jump(self):

		x, y = self.rect.center


		# key mapping
		keys = pygame.key.get_pressed()
		mkeys = pygame.mouse.get_pressed()


		# Event handling
		if keys[K_SPACE] or mkeys[0] or p1Pad.get_button(0):

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
			self.acc += 0.5

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

	bg = pygame.image.load("backgrounds/bg" + str(random.randint(1,5)) + ".png")

	bg = pygame.transform.scale(bg, res)
	bgRect = bg.get_rect()

	bgRect = (0, 0)

	random.seed(datetime.now())

	# choosing random background song.
	pygame.mixer.music.load('songs/song-' + str(random.randint(0, 5)) +'.ogg')
	sleep(0.5)
	for i in range(8):
		random.seed(datetime.now())
		pygame.mixer.music.queue('songs/song-' + str(random.randint(0, 5)) +'.ogg')

	# Creating background clouds
	for i in range(20):
		new_cloud = Clouds((random.randrange(0, width), random.randrange(0, height)))

		if not pygame.sprite.spritecollide(new_cloud, clouds, False):
			clouds.add(new_cloud)
			all_sprites.add(new_cloud)

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
	plat1 = Platform(True, 'platforms/platform_5.png')

	# Customizing platform
	plat1.image = pygame.transform.scale(plat1.image, (plat1.image.get_width()*2, plat1.image.get_height()*2))
	plat1.rect = plat1.image.get_rect()
	plat1.rect.topleft = (0, height * 5//6 + 3)


	plat2 = Platform(True, 'platforms/platform_0.png')

	plat2.rect.center = (width * 1.25, height * 4//6)

	# Add initial platform to groups
	platforms.add(plat1)
	all_sprites.add(plat1)

	platforms.add(plat2)
	all_sprites.add(plat2)

	# loop the background music
	pygame.mixer.music.play(0, 0)


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

		# Seagull spawning after player distance 500
		if p1.relpos.x > 50000:
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

		if p1.relpos.x % (60 * 100) == 0 and p1.relpos.x != 0:
			PlayerSpeed += 1

		# 1/chancenumber divided by 105/100
			CHANCE //=1.05


		# Updating scoreline
		scoreLine.rect.center = (scoreLine.x, height//2)


		# Updating sprite groups
		clouds.update()
		seagulls.update()
		p1.update()

		screen.blit(bg, bgRect)

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

		# Fixed Frame rate 110 recommended unless old computer
		clock.tick(FPS)

	pygame.mixer.music.unload()

def helpScreen():
	pygame.mixer.music.load('songs/help.ogg')

	header = pygame.font.Font('fonts/pixelart.ttf', 50)
	sub = pygame.font.Font('fonts/pixelart.ttf', 20)

	title = header.render('Instructions and Details', BG, (230, 230, 230))
	l1 = sub.render("Your goal is too avoid the obstacles in your path by skipping them.", BG, (230, 230, 230))
	l2 = sub.render("Spacebar to jump.", BG, (230, 230, 230))
	l3 = sub.render("You can land on the clouds but not the ones with thunder.", BG, (230, 230, 230))
	l4 = sub.render("During your journey you will encounter lavablocks.", BG, (230, 230, 230))
	l5 = sub.render("You can't land on those", BG, (230, 230, 230))
	l6 = sub.render("You will also find seagulls.", BG, (230, 230, 230))
	l7 = sub.render("Just don't hit any of them, they're very angry", BG, (230, 230, 230))

	titleRect = title.get_rect()

	l1Rect = l1.get_rect()
	l2Rect = l2.get_rect()
	l3Rect = l3.get_rect()

	l1Rect = (width * 1//64, height * 7//32)
	l2Rect = (width * 1//64, height * 9//32)
	l3Rect = (width * 1//64, height * 11//32)
	l4Rect = (width * 1//64, height * 13//32)
	l5Rect = (width * 1//64, height * 15//32)
	l6Rect = (width * 1//64, height * 17//32)
	l7Rect = (width * 1//64, height * 19//32)

	titleRect = (width * 1//32, height* 1//16)

	bg = pygame.image.load("backgrounds/bg1.png")
	bg = pygame.transform.scale(bg, res)

	bgRect = bg.get_rect()

	bgRect = (0, 0)


	pygame.mixer.music.play(0, 0)

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit(0)
			if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
				pygame.mixer.music.stop()
				startScreen()


		screen.blit(bg, bgRect)

		screen.blit(title, titleRect)

		screen.blit(l1, l1Rect)
		screen.blit(l2, l2Rect)
		screen.blit(l3, l3Rect)
		screen.blit(l4, l4Rect)
		screen.blit(l5, l5Rect)
		screen.blit(l6, l6Rect)
		screen.blit(l7, l7Rect)

		clock.tick(FPS-10)
		pygame.display.update()

def startScreen():

	COLOR = (245, 245, 245)

	bg = pygame.image.load("backgrounds/startbg.png")
	bg = pygame.transform.scale(bg, res)

	pygame.mixer.music.load('songs/startup.ogg')

	alphaVal = 0

	bgRect = bg.get_rect()
	bgRect.center = (width//2, height//2)

	header = pygame.font.Font('fonts/pixelart.ttf', 50)
	sub = pygame.font.Font('fonts/pixelart.ttf', 25)

	title = header.render(name, BG2, COLOR)
	start = sub.render('Start', BG2, COLOR)
	help = sub.render('Help', BG2, COLOR)
	exit = sub.render('Quit', BG2, COLOR)

	cursor = sub.render('->', BG2, (100, 255, 100))

	titleRect = title.get_rect()

	startRect = start.get_rect()
	helpRect = help.get_rect()
	exitRect = exit.get_rect()

	cursorRect = cursor.get_rect()

	titleRect.center = (width/2, height * 1//3)

	startRect.center = (width/2, height * 1//2 - 10)
	helpRect.center = (width/2, height * 1//2 + 10)
	exitRect.center = (width/2, height * 1//2 + 30)

	cursorRect.center = (width//2 - 50, height * 1//2 - 10)

	x, y = cursorRect.center

	sx, sy = startRect.center
	hx, hy = helpRect.center
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

	global firstEntry

	pygame.mixer.music.play(-1, 0)
	while True:
		if firstEntry:
			if alphaVal < 255:
				alphaVal += 1
		else:
			alphaVal = 255

		for event in pygame.event.get():
			key = pygame.key.get_pressed()
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == KEYDOWN or event.type == JOYBUTTONDOWN or event.type == JOYAXISMOTION:

				if key[K_UP] or p1Pad.get_axis(0) > 0.1:
					y -= 20
				if key[K_DOWN] or p1Pad.get_axis(0) < -0.1:
					y += 20

				if key[K_SPACE] or key[K_RETURN] or p1Pad.get_button(0):
					if y == ey:
						pygame.mixer.music.stop()
						pygame.quit()
						sys.exit()
					elif y == hy:
						pygame.mixer.music.stop()
						firstEntry = False
						helpScreen()
						startScreen()
					elif y == sy:
						pygame.mixer.music.stop()
						firstEntry = False
						main()
						break

				if y > ey:
					y = sy
				if y < sy:
					y = ey






		cursorRect.center = (x, y)

		screen.fill((124, 169, 242))

		cloudsGroup1.draw(screen)
		cloudsGroup1.update()

		screen.blit(bg, bgRect)

		bg.set_alpha(alphaVal)

		screen.blit(title, titleRect)
		screen.blit(start, startRect)
		screen.blit(exit, exitRect)
		screen.blit(help, helpRect)
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

	screen.fill(BG)

	screen.blit(text, textRect)
	screen.blit(score, scoreRect)
	screen.blit(text2, text2Rect)

	pygame.mixer.music.play(0, 0)
	pygame.display.flip()
	sleep(3)


	while True:
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
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
