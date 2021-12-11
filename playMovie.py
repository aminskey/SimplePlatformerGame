import pygame
import cv2

from pygame.locals import *

def playMovie(movie_name, surf, fps_rate=30):

	clock = pygame.time.Clock()

	movie = cv2.VideoCapture("movies/" + movie_name + ".mp4")
	shape = movie.read()[1].shape[1::-1]


	pygame.mixer.music.load("movies/" + movie_name + ".ogg")
	pygame.mixer.music.play(0, 0)
	ret = True

	while ret:
		ret, frame = movie.read()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				ret = False
			if event.type == pygame.KEYDOWN:
				keys = pygame.key.get_pressed()

				if keys[K_ESCAPE]:
					ret = False
					break
		if ret == False:
			continue

		img = pygame.image.frombuffer(frame.tobytes(), shape, "BGR")
		img = pygame.transform.scale(img, surf.get_size())

		surf.blit(img, (0, 0))

		pygame.display.update()
		clock.tick(fps_rate)

	pygame.mixer.music.stop()
	pygame.mixer.music.unload()
