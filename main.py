# full imports
import pygame, sys, random, os
from pygame.locals import *

# initiate pygame library
pygame.init()

# Create FPS handler
clock = pygame.time.Clock()
FPS = 60

# resolution tuple
res = (800, 430)
width, height = res

# Game name
name = 'Sky Dash'
ver = '1.8.3'

# Setting up window
screen = pygame.display.set_mode(res, SCALED | FULLSCREEN)
pygame.display.set_caption(name)

# get working directory
cwd = os.getcwd()

# Sprite Groups
clouds = pygame.sprite.Group()
cloudsGroup1 = pygame.sprite.Group()
cloudsGroup2 = pygame.sprite.Group()
platforms = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
danger = pygame.sprite.Group()
players = pygame.sprite.Group()
seagulls = pygame.sprite.Group()

# text and screen background
BG = (52, 164, 235)
BG2 = (100, 100, 255)
WHITE = (255, 255, 255)
GREY = (150, 150, 150)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
DARK_BLUE = (55,55,255)

# Invisible mouse
#pygame.mouse.set_visible(False)

# Initial Player speed
PSD = 8

# player speed
PlayerSpeed = PSD

RATE = 124
# 1/256 = 0.25% chance of lava block

# Calculating Players position relative to start
vec = pygame.math.Vector2
highscore = vec(0, 0)

# Are you playing the game for the first time?!?!?
firstTime = True

# Clouds Class
class Clouds(pygame.sprite.Sprite):
	# General settings
	def __init__(self, image="backgroundObjects/cloud.png", pos=(0, 0)):
		super().__init__()

		self.image = pygame.image.load(f"{cwd}/{image}")
		self.rect = self.image.get_rect()

		self.rect.center = pos
		self.min = 0
		self.max = height

	# Make them move in the air
	def update(self, speed=1):

		# if out of window then respawn ahead of widthspan
		if self.rect.midright[0] < 0:
			self.rect.midleft = (width, random.randrange(self.min, self.max))

		# slowly drift backwards creating virtual effect
		self.rect.x -= speed

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
				self.image = pygame.image.load(f'{cwd}/platforms/platform_' + str(random.randint(0, 2)) + '.png')
			else:
				self.image = pygame.image.load(f'{cwd}/badObjects/lavablock.png')
		else:
			self.image = pygame.image.load(image)

		# General settings
		self.rect = self.image.get_rect()
		self.rect.midleft = (screen.get_width(), random.randrange(height * 8//12, height * 5//6))
		self.pos = vec((self.rect.center))

# Seagulls class
class Seagull(pygame.sprite.Sprite):
	# initial settings
	def __init__(self):
		super().__init__()

		self.image = pygame.image.load(f'{cwd}/badObjects/seagull.png')

		self.rect = self.image.get_rect()
		self.rect.topleft = (random.randrange(width, width * 2), random.randrange(0, height//6))

	# Update mechanism
	def update(self):
		self.rect.x -= PlayerSpeed * 1.15
		# if seagull out of screen then kill it
		if self.rect.midleft[0] < 0:
			all_sprites.remove(self)
			danger.remove(self)
			seagulls.remove(self)

			self.kill()

# Button Class
class Button(pygame.sprite.Sprite):
	def __init__(self, image, pos=(0, 0)):
		self.image = pygame.image.load(f"{cwd}/{image}")
		self.rect = self.image.get_rect()

		self.rect.center = pos
class Option(Button):
	def __init__(self, text, script, col, func, pos=(0, 0), *ops):
		self.text = Text(text, script, col)
		self.image = pygame.transform.scale(pygame.image.load(f"{cwd}/misc/op_btn.png"), (self.text.image.get_width() * 3, self.text.image.get_height()*2))
		self.rect = self.image.get_rect()
		self.rect.center = pos

		self.text.rect.topleft = (self.text.image.get_width(), self.text.image.get_height() * 1//2)
		self.image.blit(self.text.image, self.text.rect)

		self.func = func
		self.ops = ops
	def activate(self):
		self.func(*self.ops)

# Player class
class Player(pygame.sprite.Sprite):
	# initial settings
	def __init__(self):
		super().__init__()

		self.image = pygame.Surface((40, 40))
		self.image.fill((120, 255, 120))

		self.rect = self.image.get_rect()
		self.rect.center = (width//2, 0)

		self.acc = 1.75
		self.vel_y = 0
		self.relpos = vec(self.rect.center)

		self.jumpstate = True
		self.isStuck = False

	# Jump mechanism
	def jump(self, jumpSpeed = 25):
		self.vel_y = -jumpSpeed
	# Gravity mechanism
	def gravity(self):
		# checking for collision
		# If not then continue falling and updating position
		if self.vel_y < 15:
			self.vel_y += self.acc


	# The Update mechanism
	def update(self):
		self.rect.y += self.vel_y

		# Checking for collision
		if pygame.sprite.spritecollideany(self, platforms):
			if self.jumpstate:
				self.vel_y = 0
			self.jumpstate = False

			plat = pygame.sprite.spritecollideany(self, platforms)
			# If player collides with platform and is deep in the block
			# Then stop all motion except for jumping mechanism
			if self.rect.centery < plat.rect.midbottom[1] and self.rect.centery > plat.rect.midtop[1]:
				self.rect.x -= PlayerSpeed
				self.isStuck = True
		else:
			self.gravity()
			self.jumpstate = True
			self.isStuck = False

		if not self.isStuck:
			# if the player is not at the center of the screen
			# Then move it towards the center
			if screen.get_rect().centerx - self.rect.centerx > 0:
				self.rect.centerx += 2

		# Updating relative position
		self.relpos.x += PlayerSpeed


# ScoreLine class
class HighScoreLine(pygame.sprite.Sprite):
	def __init__(self):
		super().__init__()

		self.image = pygame.Surface((20, height))
		self.image.fill((10, 10, 255))

		self.image.set_alpha(50)

		self.rect = self.image.get_rect()
		self.rect.center = (highscore.x, height/2)
		self.x, self.y = self.rect.center

class Text(pygame.sprite.Sprite):
	def __init__(self, msg, script, col, pos=(0, 0), shadow=None):
		super().__init__()
		if not isinstance(shadow, tuple):
			self.image = script.render(msg, None, col)
		else:
			tmp = script.render(msg, None, col)
			s_text = script.render(msg, None, BLACK)
			self.image = pygame.Surface((tmp.get_width() + shadow[0], tmp.get_height() + shadow[1]))
			self.image.fill((1, 0, 2))
			self.image.set_colorkey((1, 0, 2))

			self.image.blit(s_text, shadow)
			self.image.blit(tmp, (0, 0))

		self.rect = self.image.get_rect()

		self.rect.center = pos

def pause():
	shade = pygame.Surface(screen.get_size())
	shade.fill(BLACK)
	shade.set_alpha(200)

	title = pygame.font.Font(f"{cwd}/fonts/pixelart.ttf", 55)
	subfont = pygame.font.Font(f"{cwd}/fonts/pixelart.ttf", 35)

	pauseMsg = Text("Paused", title, GREEN, shadow=(3, 1))
	subtitle = Text("Press to continue", subfont, GREEN, shadow=(3, 1))

	pauseMsg.rect.midbottom = screen.get_rect().center
	subtitle.rect.midtop = pauseMsg.rect.midbottom

	screen.blit(shade, (0, 0))
	screen.blit(pauseMsg.image, pauseMsg.rect)
	screen.blit(subtitle.image, subtitle.rect)

	i=0
	pygame.event.clear()
	while True:
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				exit()
			if event.type == MOUSEBUTTONUP:
				if i > FPS//4:
					return
		i += 1
		clock.tick(FPS)
		pygame.display.update()

def main():
	fgClouds = pygame.sprite.Group()

	# Importing global variables
	global highscore
	global PlayerSpeed
	global firstTime

	CHANCE = RATE

	# Creating scoreLine
	scoreLine = HighScoreLine()
	if not firstTime:
		all_sprites.add(scoreLine)

	# defining player
	p1 = Player()
	all_sprites.add(p1)
	players.add(p1)

	# Defining ground platform
	plat1 = Platform(True, f'{cwd}/platforms/platform_0.png')

	# Customizing platform
	plat1.image = pygame.transform.scale(plat1.image, (width, plat1.image.get_height()))
	plat1.rect = plat1.image.get_rect()
	plat1.rect.topleft = (0, height * 5//6 + 3)

	# Add initial platform to groups
	platforms.add(plat1)
	all_sprites.add(plat1)

	# Creating font object
	sub = pygame.font.Font(f'{cwd}/fonts/pixelart.ttf', 25)

	# choosing random background song.
	pygame.mixer.music.load(f'{cwd}/BGM/main.ogg')
	pygame.mixer.music.play(-1)

	# frameCounter
	count = 0

	# Pause Button
	pause_btn = Button("misc/pause_btn.png")
	pause_btn.rect.topright = screen.get_rect().topright

	# Generating foreground and background clouds
	for i in range(random.randint(7, 30)):
		if i < 5:
			tmp = Clouds(f"platforms/platform_2.png")
			tmp.rect.midleft = (random.randrange(width, width*2), random.randrange(height//2, height))
			tmp.image.set_alpha(25)

			tmp.min = height//2
			tmp.max = height * 3//4

			fgClouds.add(tmp)
			clouds.add(tmp)
		else:
			tmp = Clouds(pos=(random.randrange(0, width), random.randrange(0, height)))
			if i % 2 == 0:
				tmp.image.set_alpha(150)
				cloudsGroup1.add(tmp)
			else:
				cloudsGroup2.add(tmp)
			clouds.add(tmp)


	while True:

		pSpeed = Text(f"Player Speed: {PlayerSpeed}", sub, DARK_BLUE, shadow=(3, 2))
		pScore = Text(f"Player Score: {int(p1.relpos.x//100)}", sub, DARK_BLUE, shadow=(3, 2))
		curr_Score = Text(f"Current Highscore: {int(highscore.x//100)}", sub, DARK_BLUE, shadow=(3, 2))

		curr_Score.rect.midtop = screen.get_rect().midtop
		pScore.rect.midtop = curr_Score.rect.midbottom
		pSpeed.rect.midtop = pScore.rect.midbottom


		# Window event handler
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.MOUSEBUTTONDOWN:
				point = pygame.mouse.get_pos()
				if pause_btn.rect.collidepoint(point):
					pause()
					break
				if not p1.jumpstate:
					p1.jump()
				break

		screen.fill(BG)

		x, y = p1.rect.center

		# Making the platforms move to create an illusion
		# That the player is moving
		for plat in platforms:
			plat.rect.centerx -= PlayerSpeed

		# if player's x is greater than highscore bar's x
		# Then update it
		if x > scoreLine.x:
			scoreLine.x -= PlayerSpeed


		# Put in for loop for user to increase game intensity
		if count % random.randint(3, 6) == 0:
			# randomizing chance
			# same logic as the seagull (l. 399) but with lava blocks
			# but not dependent on distance
			choice = random.randint(0, CHANCE)

			if choice == 0:
				new_plat = Platform(False)
				danger.add(new_plat)
			else:
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
			if firstTime:
				firstTime = False

			pygame.event.clear()
			for sprite in all_sprites.sprites():
				sprite.kill()
			for sprite in clouds.sprites():
				sprite.kill()
			for sprite in fgClouds.sprites():
				sprite.kill()

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

		if p1.relpos.x % 1000 == 0 and p1.relpos.x != 0:
			PlayerSpeed += 1

			# 1/chancenumber divided by 105/100
			CHANCE //=1.05


		# Updating scoreline
		scoreLine.rect.center = (scoreLine.x, height//2)


		# Updating sprite groups
		clouds.update()
		fgClouds.update(PlayerSpeed + 1)
		seagulls.update()
		p1.update()

		# Drawing all sprites to screen
		cloudsGroup1.draw(screen)
		cloudsGroup2.draw(screen)
		all_sprites.draw(screen)
		fgClouds.draw(screen)

		# Sending Highscore and player score data to screen
		screen.blit(pSpeed.image, pSpeed.rect)
		screen.blit(pScore.image, pScore.rect)
		screen.blit(curr_Score.image, curr_Score.rect)

		# Printing pause button
		screen.blit(pause_btn.image, pause_btn.rect)

		# Refreshing screen
		pygame.display.update()

		# Fixed Frame rate 120 recommended unless old computer
		clock.tick(FPS)
		count += 1

def startScreen():

	global highscore
	global firstTime

	pygame.mixer.music.load(f'{cwd}/BGM/startup.ogg')
	header = pygame.font.Font(f'{cwd}/fonts/pixelart.ttf', 50)
	sub = pygame.font.Font(f'{cwd}/fonts/pixelart.ttf', 25)
	h2 = pygame.font.Font(f'{cwd}/fonts/pixelart.ttf', 30)


	title = Text(name, header, WHITE, (screen.get_rect().centerx, screen.get_height()//3), (2, 3))
	subtitle = Text(ver, h2, WHITE)
	start = Text("Press to Start", sub, WHITE, screen.get_rect().center + vec(0, 10), (2, 3))
	reset = Text("Reset Highscore", sub, WHITE, shadow=(2, 3))
	resetClicked = Text("Reset Highscore", sub, GREY)

	reset.rect.midtop = start.rect.midbottom + vec(0, 3)
	resetClicked.rect.center = reset.rect.center
	subtitle.rect.midtop = title.rect.midbottom

	hasReset = False
	for i in range(30):
		new_cloud = Clouds(pos=(random.randrange(0, width), random.randrange(0, height)))

		if not pygame.sprite.spritecollideany(new_cloud, cloudsGroup1):
			if i % 2 == 0:
				new_cloud.image.set_alpha(100)
				cloudsGroup1.add(new_cloud)
			else:
				new_cloud.image.set_alpha(200)
				cloudsGroup2.add(new_cloud)
			clouds.add(new_cloud)

	pygame.mixer.music.play(-1, 0)
	while True:

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.MOUSEBUTTONUP:
				p = pygame.mouse.get_pos()
				if start.rect.collidepoint(p):
					if hasReset:
						firstTime = True
					main()
					exit()
				elif reset.rect.collidepoint(p):
					pygame.mixer.Sound(f"{cwd}/sounds/gameOver.wav").play()
					highscore = vec(0, 0)
					hasReset = True
					break

		screen.fill(BG)

		cloudsGroup1.update(2)
		cloudsGroup2.update(2)

		cloudsGroup1.draw(screen)
		screen.blit(title.image, title.rect)
		screen.blit(subtitle.image, subtitle.rect)
		screen.blit(start.image, start.rect)
		if not firstTime:
			if not hasReset:
				screen.blit(reset.image, reset.rect)
			else:
				screen.blit(resetClicked.image, resetClicked.rect)
		cloudsGroup2.draw(screen)
		#screen.blit(play_btn.image, play_btn.rect)

		pygame.display.update()
		clock.tick(FPS)


def gameOver(p1, highscore):
	if p1.relpos.x >= highscore.x:
		highscore.x = p1.relpos.x


	pygame.mixer.music.stop()

	header = pygame.font.Font(f'{cwd}/fonts/pixelart.ttf', 40)
	sub = pygame.font.Font(f'{cwd}/fonts/pixelart.ttf', 20)

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

	pygame.display.flip()

	pygame.mixer.Sound(f"{cwd}/sounds/gameOver.wav").play()

	while True:
		for event in pygame.event.get():
			if event.type == pygame.MOUSEBUTTONUP:
				for sprite in all_sprites:
					sprite.kill()
				startScreen()
				break
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
if __name__ == "__main__":
	startScreen()
