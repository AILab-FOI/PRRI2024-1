import pygame
import random
import os
import csv

pygame.init()

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) #game window size
pygame.display.set_caption('Igrica')

#max frame rate
clock = pygame.time.Clock()
fps = 60

#game variables
GRAVITY = 0.70
ROWS = 20
COLUMNS = 30
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 4 #number of different tiles ------------------------------- CHANGE
level = 1 #level 1, level 2...


#player variables
moving_left = False
moving_right = False
shoot = False

#images
#tiles in list
tile_image_list = []
for x in range(TILE_TYPES):
	image = pygame.image.load(f'../images/Background/{x}.png')
	image = pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))
	tile_image_list.append(image)

#bullet
bullet_image = pygame.image.load('../images/Player/Weapon/Bullet.png').convert_alpha()
bullet_image = pygame.transform.scale(bullet_image, (12, 12))
#items
health_box_image = pygame.image.load('../images/Icons/health.png').convert_alpha()
ammo_box_image = pygame.image.load('../images/Icons/ammo.png').convert_alpha()

item_boxes = { #dictionary
	'Health'	: health_box_image,
	'Ammo'	: ammo_box_image
}

font = pygame.font.SysFont('Helvetica', 15)

background_color = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def draw_Background():
	screen.fill(background_color)
	pygame.draw.line(screen, GREEN, (0, 300), (SCREEN_WIDTH, 300)) # ------temporary floor

def draw_information(text, font, color, x, y):
	img = font.render(text, True, color)
	screen.blit(img, (x, y))

class Level():
	def __init__(self):
		self.obstacle_list = []

	def process_data(self, data):
		for y, row in enumerate(data):
			for x, tile in enumerate(row):
				if tile >= 0:
					image = tile_image_list[tile]
					image_rect = image.get_rect()
					image_rect.x = x * TILE_SIZE
					image_rect.y = y * TILE_SIZE
					tile_data = (image, image_rect)
					if tile >= 0 and tile <= 2: #if its dirt or a box
						self.obstacle_list.append(tile_data)
					elif tile == 3: #if its water
						water = Water(image, x * TILE_SIZE, y * TILE_SIZE)
						water_group.add(water)
					else: #in the future if there'll be more tiles
						pass
	
	def draw(self):
		for tile in self.obstacle_list:
			screen.blit(tile[0], tile[1])

class Water(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height())) 

class Character(pygame.sprite.Sprite):
	def __init__(self, character_type, x, y, scale, speed, ammo): #constructor	
		pygame.sprite.Sprite.__init__(self)
		self.alive = True
		self.character_type = character_type
		self.speed = speed #in pixels
		self.ammo = ammo #gun amunition
		self.start_ammo = ammo
		self.shooting_cooldown = 0
		self.health = 100 #health = health for different enemy health
		self.max_health = self.health
		self.direction = 1
		self.velocity_y = 0
		self.jump = False
		self.in_jump_state = True
		self.flip = False
		self.animation_list = []
		self.frame_index = 0
		self.action = 0 #0 idle, 1 run
		self.update_time = pygame.time.get_ticks()#to track the time
		#AI variables
		self.moving_counter = 0
		self.vision = pygame.Rect(0, 0, 150, 20) #how far the enemies can look
		self.idle = False
		self.idle_counter = 0
		
		animation_types = ['Idle', 'Run', 'Jump', 'Die', 'Hurt', 'Shot'] #idle, walk dead etc
		for animation in animation_types:
			temp_list = []
			#check number of items in folder
			number_of_files = len(os.listdir(f'../images/{self.character_type}/{animation}'))

			for i in range(number_of_files):
				playerImg = pygame.image.load(f'../images/{self.character_type}/{animation}/{i}.png').convert_alpha() #loading the character image (player, soldier...)
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
		
		if self.jump == True and self.in_jump_state == False:
			self.velocity_y = -11 #how high player jumps
			self.jump = False
			self.in_jump_state = True
		
		#gravity
		self.velocity_y += GRAVITY
		if self.velocity_y > 10:
			self.velocity_y = 10
		dy += self.velocity_y

		#check collision with floor --- temporary
		if self.rect.bottom + dy > 300:
			dy = 300 - self.rect.bottom
			self.in_jump_state = False

		#change player position
		self.rect.x += dx
		self.rect.y += dy

	def update(self):
		self.update_animation()
		self.check_alive()
		if self.shooting_cooldown > 0:
			self.shooting_cooldown -= 1 #cooldown
		
		if not self.alive:
			self.move(False, False)


	def shooting(self):
		if self.shooting_cooldown == 0 and self.ammo > 0:
			self.shooting_cooldown = 45
			bullet = Bullet(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction), self.rect.centery - (-0.2 * self.rect.size[1]), self.direction)
			bullet_group.add(bullet)
			self.ammo -= 1

	def ai(self):
		if self.alive and player.alive:
			if self.idle == False and random.randint(1, 200) == 1:
				self.update_action(0)
				self.idle = True
				self.idle_counter = 50
			#if the enemy sees player
			if self.vision.colliderect(player.rect):
				self.update_action(0) #go idle and shoot
				self.shooting()
			else:
				if self.idle == False:
					if self.direction == 1:
						ai_moving_right = True
					else:
						ai_moving_right = False
					ai_moving_left = not ai_moving_right
					self.move(ai_moving_left, ai_moving_right)
					self.update_action(1) #when running = run animation
					self.moving_counter += 1
					self.vision.center = (self.rect.centerx + 75 * self.direction, self.rect.centery) #so the vision moves with the enemy
					pygame.draw.rect(screen, RED, self.vision) #visualize enemy vision
					if self.moving_counter > TILE_SIZE:
						self.direction *= -1
						self.moving_counter *= -1
				else:
					self.idle_counter -= 1
					if self.idle_counter <= 0:
						self.idle = False

	def update_animation(self):
		ANIMATION_COOLDOWN = 80 #speed of animation
		self.playerImg = self.animation_list[self.action][self.frame_index]
		if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
			self.update_time = pygame.time.get_ticks()
			self.frame_index += 1
		#reset back to index 1
		if self.frame_index >= len(self.animation_list[self.action]):
			if self.action == 3: #if animation is dead
				self.frame_index = len(self.animation_list[self.action]) - 1
			else:	
				self.frame_index = 0

	def update_action(self, new_action):
		if new_action != self.action:
			self.action = new_action
			self.frame_index = 0
			self.update_time = pygame.time.get_ticks()

	def check_alive(self):
		if self.health <= 0:
			self.health = 0
			self.speed = 0
			self.alive = False
			self.update_action(3)   

	def draw(self):
		screen.blit(pygame.transform.flip(self.playerImg,  self.flip, False), self.rect)
		pygame.draw.rect(screen, GREEN, self.rect, 1) #collide box

class Items(pygame.sprite.Sprite):
	def __init__(self, item_type, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.item_type = item_type
		self.image = item_boxes[self.item_type]
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self):
		#collision
		if pygame.sprite.collide_rect(self, player): #what happens when collecting certain items
			if self.item_type == 'Health' and player.health < 100:
				player.health += 25
				self.kill()
				if player.health > player.max_health:
					player.health = player.max_health
			if self.item_type == 'Ammo':
				player.ammo += 10
				self.kill()
			#detele item

class Bullet(pygame.sprite.Sprite):
	def __init__(self, x, y, direction):
		pygame.sprite.Sprite.__init__(self)
		self.speed = 10
		self.image = bullet_image
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.direction = direction

	def update(self):
		#bullet travel
		self.rect.x += (self.direction * self.speed)
		#bullet out of bounds (screen)
		if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
			self.kill
		
		#check bullet hit charactersdokill
		if pygame.sprite.spritecollide(player, bullet_group, False):
			if player.alive:
				player.health -= 25
				self.kill()
		
		for enemy in enemy_group:
			if pygame.sprite.spritecollide(enemy, bullet_group, False):
				if enemy.alive:
					enemy.health -= 50
					self.kill()

class HealthBar():
	def __init__(self, x, y, health, max_health):
		self.x = x
		self.y = y
		self.health = health
		self.max_health = max_health

	def draw(self, health):
		self.health = health
		#calculate health
		ratio = self.health / self.max_health
		pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
		pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
		pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))

#sprite groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()

#temporary creation of items
item_box = Items('Health', 300, 270)
item_box_group.add(item_box)

item_box = Items('Ammo', 450, 270)
item_box_group.add(item_box)

#create characters
player = Character('player', 50, 250, 0.10, 5, 20)
health_bar = HealthBar(10, 10, player.health, player.health)

enemy = Character('enemy_alien', 600, 250, 0.10, 2, 20)
enemy2 = Character('enemy_alien', 700, 250, 0.10, 2, 20)
enemy_group.add(enemy)
enemy_group.add(enemy2)

#CREATE TILE LIST
world_data = []
for row in range(ROWS):
	r = [-1] * COLUMNS #row with 150 negative columns, -1 means a empty tile
	world_data.append(r)
#load level data
with open(f'../levels/level{level}.csv', newline='') as csvfile:
	reader = csv.reader(csvfile, delimiter=',')
	for x, row in enumerate(reader):
		for y, tile in enumerate(row):
			world_data[x][y] = int(tile)

level = Level()
level.process_data(world_data)

run = True
while run: #loop for running the game

	clock.tick(fps)
	
	draw_Background()
	level.draw()

	draw_information(f'Ammo: {player.ammo}', font, WHITE, 10, 40) #show left ammo

	player.update()
	player.draw()
	health_bar.draw(player.health)
	draw_information(f'{player.health}', font, WHITE, 75, 10) #show left HP
	#enemy.update_animation()
	for enemy in enemy_group:
		enemy.update()
		enemy.draw()
		enemy.ai()
	#update sprite groups
	bullet_group.update()
	bullet_group.draw(screen)
	item_box_group.update()
	item_box_group.draw(screen)
	water_group.update()
	water_group.draw(screen)

	if player.alive:
		#shoot
		if shoot:
			player.shooting()
		if player.in_jump_state:
			player.update_action(2)
		#change animation if moving left or right
		elif moving_left or moving_right:
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
			if event.key == pygame.K_SPACE:
				shoot = True
			if event.key == pygame.K_ESCAPE:
				run = False
		
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_a:
				moving_left = False
			if event.key == pygame.K_d:
				moving_right = False
			if event.key == pygame.K_SPACE:
				shoot = False
			

	pygame.display.update()

pygame.quit()