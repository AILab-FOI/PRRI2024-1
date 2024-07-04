import pygame

pygame.init()

#max frame rate
clock = pygame.time.Clock()
fps = 60

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) #game window size
pygame.display.set_caption('Igrica')

moving_left = False
moving_right = False

background_color = (0, 255, 255)

def draw_Background():
	screen.fill(background_color)

class Character(pygame.sprite.Sprite):
	def __init__(self, character_type, x, y, scale, speed): #constructor	
		pygame.sprite.Sprite.__init__(self)
		self.character_type = character_type
		self.speed = speed #in pixels
		self.direction = 1
		self.flip = False
		playerImg = pygame.image.load(f'../images/{self.character_type}/Idle/0.png') #loading the character image (player, soldier...)
		self.playerImg = pygame.transform.scale(playerImg, (int(playerImg.get_width() * scale), (int(playerImg.get_height() * scale))))
		self.rect = self.playerImg.get_rect() #rectangle for player character
		self.rect.center = (x, y) #position the character on a certain position of the game window

	def move(self, moving_left, moving_right):
		dx = 0 #change in the x position
		dy = 0 #change in the y position
		
		#move 
		if moving_left:
			dx = -self.speed
			self.flip = True
			self.direction = -1
		
		if moving_right:
			dx = self.speed
			self.flip = False
			self.direction = 1
		
		#change player position
		self.rect.x += dx
		self.rect.y += dy

	def draw(self):
		screen.blit(pygame.transform.flip(self.playerImg,  self.flip, False), self.rect)


player = Character('player', 200, 200, 0.15, 5)

run = True
while run: #loop for running the game

	clock.tick(fps)
	
	draw_Background()
	player.draw()
	player.move(moving_left, moving_right)

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_a:
				moving_left = True
			if event.key == pygame.K_d:
				moving_right = True
			if event.key == pygame.K_ESCAPE:
				run = False
		
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_a:
				moving_left = False
			if event.key == pygame.K_d:
				moving_right = False
			

	pygame.display.update()

pygame.quit()