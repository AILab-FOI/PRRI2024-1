import pygame
import os
import random

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
TILE_SIZE = 30

#player variables
moving_left = False
moving_right = False
shoot = False

#images
#player bullet
bullet_image = pygame.image.load('../images/Player/Weapon/Bullet.png').convert_alpha()
bullet_image = pygame.transform.scale(bullet_image, (12, 12))

background_color = (0, 255, 255)
GREEN = (255, 0, 0)
RED = (0, 255, 0)

def draw_Background():
	screen.fill(background_color)
	pygame.draw.line(screen, GREEN, (0, 300), (SCREEN_WIDTH, 300)) # ------temporary floor

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
			self.ammo - 1

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


#sprite groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()

#create characters
player = Character('player', 200, 250, 0.15, 5, 20)

enemy = Character('enemy_alien', 600, 250, 0.20, 2, 20)
enemy2 = Character('enemy_alien', 500, 250, 0.20, 2, 20)
enemy_group.add(enemy)
enemy_group.add(enemy2)

run = True
while run: #loop for running the game

	clock.tick(fps)
	
	draw_Background()

	player.update()
	player.draw()
	#enemy.update_animation()
	for enemy in enemy_group:
		enemy.update()
		enemy.draw()
		enemy.ai()
	#update sprite groups
	bullet_group.update()
	bullet_group.draw(screen)

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