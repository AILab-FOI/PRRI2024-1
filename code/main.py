import pygame

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Igrica')


class Player(pygame.sprite.Sprite):
	def __init__(self, x, y, scale): #constructor	
		pygame.sprite.Sprite.__init__(self)
		playerImg = pygame.image.load('../images/Player/Idle/E_E_Gun__Idle_000.png') #loading the player image
		self.playerImg = pygame.transform.scale(playerImg, (int(playerImg.get_width() * scale), (int(playerImg.get_height() * scale))))
		self.rect = self.playerImg.get_rect() #rectangle for player character
		self.rect.center = (x, y) #position the character on a certain position of the game window

	def draw(self):
		screen.blit(self.playerImg, self.rect)

player = Player(200, 200, 0.15)

run = True
while run: #loop for running the game

	player.draw()
	
	key = pygame.key.get_pressed() #checking if a button is pressed
	if key[pygame.K_a] == True:
		playerImg.move_ip(-1, 0)
	elif key[pygame.K_d] == True:
		playerImg.move_ip(1, 0)
	elif key[pygame.K_w] == True:
		playerImg.move_ip(0, -1)
	elif key[pygame.K_s] == True:
		playerImg.move_ip(0, 1)
	
	if key[pygame.K_ESCAPE] == True: #quiting the game with ESC button
		pygame.quit()

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False

	pygame.display.update()

pygame.quit()