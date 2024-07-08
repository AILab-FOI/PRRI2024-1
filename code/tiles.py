import pygame, csv, os

class Tile(pygame.sprite.Sprite):
    def __init__(self, image, x, y, spritesheet):
        pygame.sprite.Sprite.__init__(self)
        self.image = spritesheet.parse_sprite(image)

        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))
    
class TileMap():
    def __init__(self, filename, spriteSheet):
        self.tile_size = 16
        self.start_x, self.start_y = 0, 0
        self.spritesheet = spritesheet
        self.tiles = self.load_tiles(filename)
        self.map_surface = pygame.Surface((self.map_w, self.map_h))
        self.map_surface.set_colorkey((0, 0, 0))
        self.load_map()

    def draw_map(self, surface):
        surface.blit(self.map_surface, (0, 0))

    def load_map(self):
        for tile in self.tiles:
            tile.draw(self.map_surface)

    def read_csv(self, filename):
        map = []
        with open(os.path.join(filename)) as data:
            data = csv.reader(data, delimiter = ',')
            for row in data:
                map.append(list(row))
            return map
    
    def load_tiles(self, filename):
        tiles = []
        map = self.read_csv(filename)
        x, y = 0, 0
        for row in map:
            x = 0
            for tile in row:
                if tile == '0':
                    tiles.apend(Tile('../images/Background/grass.png', x * self.title_size, y * self.title_size))
                elif tile == '1':
                    tiles.apend(Tile('../images/Background/dirt.png', x * self.title_size, y * self.title_size))
                elif tile == '2':
                    tiles.apend(Tile('../images/Background/box.png', x * self.title_size, y * self.title_size))
                elif tile == '3':
                    tiles.apend(Tile('../images/Background/health.png', x * self.title_size, y * self.title_size))
                elif tile == '4':
                    tiles.apend(Tile('../images/Background/grass_top.png', x * self.title_size, y * self.title_size))
                    #move to next tile in current row
                x += 1
                #move to next row
            y += 1

        self.map_w, self.map_h = x * self.title_size, y * self.title_size
        return tiles