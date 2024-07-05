import pygame

pygame.init()


SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) #game window size
pygame.display.set_caption('Igrica')

#max frame rate
clock = pygame.time.Clock()
fps = 60

#game variables
GRAVITY = 0.70

#player variables
moving_left = False
moving_right = False

background_color = (0, 255, 255)
GREEN = (255, 0, 0)

def draw_Background():
	screen.fill(background_color)
	pygame.draw.line(screen, GREEN, (0, 300), (SCREEN_WIDTH, 300))
	
class Character(pygame.sprite.Sprite):
	def __init__(self, character_type, x, y, scale, speed): #constructor	
		pygame.sprite.Sprite.__init__(self)
		self.alive = True
		self.character_type = character_type
		self.speed = speed #in pixels
		self.direction = 1
		self.velocity_y = 0
		self.jump = False
		self.flip = False
		self.animation_list = []
		self.frame_index = 0
		self.action = 0 #0 idle, 1 run
		self.update_time = pygame.time.get_ticks()#to track the time
		temp_list = []
		#idle animation
		for i in range(10):
			playerImg = pygame.image.load(f'../images/{self.character_type}/Idle/{i}.png') #loading the character image (player, soldier...)
			playerImg = pygame.transform.scale(playerImg, (int(playerImg.get_width() * scale), (int(playerImg.get_height() * scale))))
			temp_list.append(playerImg)
		self.animation_list.append(temp_list)
		temp_list = []
		#walking animation
		for i in range(10):
			playerImg = pygame.image.load(f'../images/{self.character_type}/Run/{i}.png') #loading the character image (player, soldier...)
			playerImg = pygame.transform.scale(playerImg, (int(playerImg.get_width() * scale), (int(playerImg.get_height() * scale))))
			temp_list.append(playerImg)
		self.animation_list.append(temp_list)
		
		self.playerImg = self.animation_list[self.action][self.frame_index]
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
		
		if self.jump == True:
			self.velocity_y = -11 #how high player jumps
			self.jump = False
		
		#gravity
		self.velocity_y += GRAVITY
		if self.velocity_y > 10:
			self.velocity_y = 10
		dy += self.velocity_y

		#change player position
		self.rect.x += dx
		self.rect.y += dy

	def update_animation(self):
		ANIMATION_COOLDOWN = 80 #speed of animation
		self.playerImg = self.animation_list[self.action][self.frame_index]
		if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
			self.update_time = pygame.time.get_ticks()
			self.frame_index += 1
		#reset back to index 1
		if self.frame_index >= len(self.animation_list[self.action]):
			self.frame_index = 0

	def update_action(self, new_action):
		if new_action != self.action:
			self.action = new_action
			self.frame_index = 0
			self.update_time = pygame.time.get_ticks()

	def draw(self):
		screen.blit(pygame.transform.flip(self.playerImg,  self.flip, False), self.rect)


player = Character('player', 200, 200, 0.15, 5)

run = True
while run: #loop for running the game

	clock.tick(fps)
	
	draw_Background()

	player.update_animation()
	player.draw()

	if player.alive:
		#change animation if moving left or right
		if moving_left or moving_right:
			player.update_action(1)
		else:
			player.update_action(0)

		player.move(moving_left, moving_right)

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_a:
				moving_left = True
			if event.key == pygame.K_d:
				moving_right = True
			if event.key == pygame.K_w and player.alive:
				player.jump = True
			if event.key == pygame.K_ESCAPE:
				run = False
		
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_a:
				moving_left = False
			if event.key == pygame.K_d:
				moving_right = False
			

	pygame.display.update()

pygame.quit()