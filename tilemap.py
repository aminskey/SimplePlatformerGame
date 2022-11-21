import pygame
import levelClass
import csv

from os.path import join

tmp = levelClass.Level("level/lvl.conf")
basic_configs = tmp.return_dataset("basic-configurations")

tilesGroup = []
tilemapGroup = []

class Spritesheet():
	def __init__(self, filename, cropnum):
		self.spritesheet = pygame.image.load(filename)

		self.cropnum = int(cropnum)
		self.cut()

	def cut(self):
		tmpnum = 0
		for y in range(self.spritesheet.get_height()//self.cropnum):
			for x in range(self.spritesheet.get_width()//self.cropnum):
				subsurf = pygame.Surface((self.cropnum, self.cropnum))
				subsurf.blit(self.spritesheet, (0, 0), (x * self.cropnum, y * self.cropnum, self.cropnum, self.cropnum))

				tilesGroup.append(Tile(subsurf, tmpnum))
				tmpnum += 1


class Tile(pygame.sprite.Sprite):
	def __init__(self, surf, num):
		super().__init__()

		self.num = num
		self.image = surf
		self.rect = self.image.get_rect()

class Tilemap():
	def __init__(self, conf_dict):
		self.tilemap = conf_dict["level-tilemap"]
		self.offset = int(conf_dict["spritesheet-div"])
		self.map = []

		self.get_tilemap()
		self.draw_map()

	def get_tilemap(self):
		with open(join(basic_configs["level-dir"], self.tilemap), "r") as tileMap:
			tileMap = csv.reader(tileMap, delimiter=',')
			for row in tileMap:
				self.map.append(row)
	def draw_map(self):
		x, y = 0, 0
		for row in self.map:
			x = 0
			for num in row:
				# match number with tile ID
				for tile in tilesGroup:
					# if match success. Add tile to sprite list and exit matching loop
					if tile.num == int(num):
						newtile = Tile(tile.image, tile.num)
						newtile.rect.topleft = (x * self.offset, y * self.offset)
						tilemapGroup.append(newtile)
						break

				# move to next column
				x += 1

			# move to next row
			y += 1