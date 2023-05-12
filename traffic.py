import pygame
import random
import time
from math import sin,cos,pi, radians, sqrt, pi

MARGIN = 4.0
LANE_WIDTH = 30.0
WIN_WIDTH = 500.0
CAR_DIM = 20
LANE_LENGTH = (WIN_WIDTH - MARGIN*6 - LANE_WIDTH*6)/2
CAR_VEL = 0.7
ANG_VEL = 0.01

pygame.init()
run = True

win = pygame.display.set_mode((WIN_WIDTH, WIN_WIDTH))

# start: 0-N, 1-E, 2-S, 3-W
# turn: 0-L, 1-S, 2-R

eps = WIN_WIDTH/2 + MARGIN/2 + LANE_WIDTH/2
eps1 = WIN_WIDTH/2 - MARGIN/2 - LANE_WIDTH/2
delta = MARGIN + LANE_WIDTH
startpos = [
	[[eps+(2*delta), 0], [eps+delta, 0], [eps, 0]],
	[[WIN_WIDTH, eps+(2*delta)], [WIN_WIDTH, eps+delta], [WIN_WIDTH, eps]],
	[[eps1-(2*delta), WIN_WIDTH], [eps1-delta, WIN_WIDTH], [eps1, WIN_WIDTH]],
	[[0, eps1-(2*delta)], [0, eps1-delta], [0, eps1]]
]
angles = [radians(270), radians(180), radians(90), radians(0)]
nextangles = [
	[radians(0), radians(270), radians(180)],
	[radians(270), radians(180), radians(90)],
	[radians(180), radians(90), radians(0)],
	[radians(90), radians(0), radians(270)]
]
nextdirs = [
	[3, 0, 1],
	[0, 1, 2],
	[1, 2, 3],
	[2, 3, 0]
]
trafficlights = [

	[[eps+(2*delta), LANE_LENGTH],[eps+delta, LANE_LENGTH],[eps, LANE_LENGTH]],
	[[WIN_WIDTH-LANE_LENGTH, eps+(2*delta)],[WIN_WIDTH-LANE_LENGTH, eps+delta],[WIN_WIDTH-LANE_LENGTH, eps]],
	[[eps1-(2*delta), WIN_WIDTH-LANE_LENGTH],[eps1-delta, WIN_WIDTH-LANE_LENGTH],[eps1, WIN_WIDTH-LANE_LENGTH]],
	[[LANE_LENGTH, eps1-(2*delta)],[LANE_LENGTH, eps1-delta],[LANE_LENGTH, eps1]]

]
turn_rads = [
	MARGIN/2 + LANE_WIDTH/2,
	0,
	MARGIN/2 + 3*LANE_WIDTH + 3*MARGIN + 0.5*LANE_WIDTH
]
turncenters = [
	[[WIN_WIDTH-LANE_LENGTH-MARGIN/2, LANE_LENGTH+MARGIN/2], [0,0], [LANE_LENGTH+MARGIN/2, LANE_LENGTH+MARGIN/2]],
	[[WIN_WIDTH-LANE_LENGTH-MARGIN/2, WIN_WIDTH-LANE_LENGTH-MARGIN/2], [0,0], [WIN_WIDTH-LANE_LENGTH-MARGIN/2, LANE_LENGTH+MARGIN/2]],
	[[LANE_LENGTH+MARGIN/2, WIN_WIDTH-LANE_LENGTH-MARGIN/2], [0,0], [WIN_WIDTH-LANE_LENGTH-MARGIN/2, WIN_WIDTH-LANE_LENGTH-MARGIN/2]],
	[[LANE_LENGTH+MARGIN/2, LANE_LENGTH+MARGIN/2], [0,0], [LANE_LENGTH+MARGIN/2, WIN_WIDTH-LANE_LENGTH-MARGIN/2]]
]
trafficswitch = [
	[1,1,1],
	[1,1,1],
	[1,1,1],
	[1,1,1]
]

def distance(x1, y1, x2, y2):
	return sqrt(((x1-x2)**2)+((y1-y2)**2))

class Car:
	def __init__(self, start, turn, prevcar):
		self.start = start
		self.turn = turn
		self.prevcar = prevcar

		self.x = 0
		self.y = 0
		

		self.x = startpos[start][turn][0]
		self.y = startpos[start][turn][1]

		self.waiting = False
		self.hasCrossed = False
		self.hasTurned = False

		
		d = [1, 0, -1]
		self.angle = angles[start] - d[turn]*radians(90)
		self.nextangle = self.angle + d[turn] * radians(90)
		self.nextdir = nextdirs[start][turn]
		self.turn_rad = turn_rads[turn]

		self.trafficpos = trafficlights[start][turn]
		self.turncenter = turncenters[start][turn]

	def draw(self):
		pygame.draw.circle(win, (255,0,0), (self.x, self.y), CAR_DIM/2)

	def move(self):
		d = [
			[0,1], [-1,0], [0,-1], [1,0]
		]
		if not self.hasCrossed and not self.waiting:
			if (self.prevcar == None or distance(self.x, self.y, self.prevcar.x, self.prevcar.y) > CAR_DIM+MARGIN):
				self.x += CAR_VEL*d[self.start][0]
				self.y += CAR_VEL*d[self.start][1]

			if distance(self.x, self.y, self.trafficpos[0], self.trafficpos[1]) < 1 and trafficswitch[self.start][self.turn]==-1: #at traffic light

				self.waiting = True
			elif distance(self.x, self.y, self.trafficpos[0], self.trafficpos[1]) < 1 and trafficswitch[self.start][self.turn]==1:
				self.waiting = False
				self.hasCrossed = True
				if self.turn ==1:
					self.hasTurned = True
				
		elif self.waiting and trafficswitch[self.start][self.turn]==1:

			self.hasCrossed = True
			self.waiting = False

			if self.turn == 1:
				self.hasTurned = True
		elif not self.waiting and not self.hasTurned:

			if self.turn != 1:
				d = 0
				if self.turn == 0:
					d = 1
				else:
					d = -1

				self.angle += d * ANG_VEL
				if self.angle < 0:
					self.angle += 2*pi
				elif self.angle > 2*pi:
					self.angle = 0
				self.x = self.turncenter[0] + self.turn_rad*cos(self.angle)
				self.y = self.turncenter[1] - self.turn_rad*sin(self.angle)

				if abs(self.angle-self.nextangle) < radians(10): # if reached next lane

					self.hasTurned = True

		elif not self.waiting:
			self.x += CAR_VEL*d[self.nextdir][0]
			self.y += CAR_VEL*d[self.nextdir][1]


cars = [
	[[],[],[]],
	[[],[],[]],
	[[],[],[]],
	[[],[],[]]
]
count = 0

trafficswitches = [

	[
		[-1,-1,1],
		[-1,-1,-1],
		[-1,-1,1],
		[-1,-1,-1]
	],

	[
		[-1,-1,-1],
		[-1,-1,1],
		[-1,-1,-1],
		[-1,-1,1]
	],

]
trafficswitch = trafficswitches[0]



count1 = 0
index = 0

while run:
	pygame.time.delay(10)
	count += 1
	count1 += 1
	if count % 100 == 0:
		print(trafficswitch)
		count = 0
		for i in range(4):
			for j in range(3):
				generate = random.randrange(2)
				if generate == 1:
					if len(cars[i][j]) > 0:
						car = Car(i,j,cars[i][j][-1])
					else:
						car = Car(i,j,None)
					cars[i][j].append(car)
	if count1 % 600 == 0:
		count1 = 0
		print(index)
		index = (index+1)%(len(trafficswitches))
		trafficswitch = trafficswitches[index]

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
	for i in range(4):
		for j in range(3):
			for car in cars[i][j]:
				car.move()
	#print(cars[2].angle)
	win.fill((0,0,0))




	for i in range(4):
		for j in range(3):
			for car in cars[i][j]:
				car.draw()
	for i in range(3):
		pygame.draw.circle(win, (255,0,0), (turncenters[i][0][0], turncenters[i][0][1]), 1)


	pygame.draw.line(win, (255,255,255), (0,WIN_WIDTH/2), (LANE_LENGTH, WIN_WIDTH/2))
	pygame.draw.line(win, (255,255,255), (WIN_WIDTH-LANE_LENGTH,WIN_WIDTH/2), (WIN_WIDTH, WIN_WIDTH/2))
	pygame.draw.line(win, (255,255,255), (WIN_WIDTH/2,0), (WIN_WIDTH/2, LANE_LENGTH))
	pygame.draw.line(win, (255,255,255), (WIN_WIDTH/2,WIN_WIDTH-LANE_LENGTH), (WIN_WIDTH/2, WIN_WIDTH))

	pygame.draw.line(win, (255,255,255), (0,WIN_WIDTH/2+3*LANE_WIDTH+3*MARGIN), (LANE_LENGTH, WIN_WIDTH/2+3*LANE_WIDTH+3*MARGIN))
	pygame.draw.line(win, (255,255,255), (WIN_WIDTH-LANE_LENGTH,WIN_WIDTH/2+3*LANE_WIDTH+3*MARGIN), (WIN_WIDTH, WIN_WIDTH/2+3*LANE_WIDTH+3*MARGIN))
	pygame.draw.line(win, (255,255,255), (WIN_WIDTH/2+3*LANE_WIDTH+3*MARGIN,0), (WIN_WIDTH/2+3*LANE_WIDTH+3*MARGIN, LANE_LENGTH))
	pygame.draw.line(win, (255,255,255), (WIN_WIDTH/2+3*LANE_WIDTH+3*MARGIN,WIN_WIDTH-LANE_LENGTH), (WIN_WIDTH/2+3*LANE_WIDTH+3*MARGIN, WIN_WIDTH))

	pygame.draw.line(win, (255,255,255), (0,WIN_WIDTH/2-3*LANE_WIDTH-3*MARGIN), (LANE_LENGTH, WIN_WIDTH/2-3*LANE_WIDTH-3*MARGIN))
	pygame.draw.line(win, (255,255,255), (WIN_WIDTH-LANE_LENGTH,WIN_WIDTH/2-3*LANE_WIDTH-3*MARGIN), (WIN_WIDTH, WIN_WIDTH/2-3*LANE_WIDTH-3*MARGIN))
	pygame.draw.line(win, (255,255,255), (WIN_WIDTH/2-3*LANE_WIDTH-3*MARGIN,0), (WIN_WIDTH/2-3*LANE_WIDTH-3*MARGIN, LANE_LENGTH))
	pygame.draw.line(win, (255,255,255), (WIN_WIDTH/2-3*LANE_WIDTH-3*MARGIN,WIN_WIDTH-LANE_LENGTH), (WIN_WIDTH/2-3*LANE_WIDTH-3*MARGIN, WIN_WIDTH))


	pygame.display.update()

pygame.quit()
