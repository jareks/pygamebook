import pygame as pg
from pathlib import Path
from abc import ABC, abstractmethod

WHITE = (255,255,255)
FPS = 60

class Gamebook(ABC):
    def __init__(self, X = 1920, Y = 1080):
        self.X = X
        self.Y = Y
        self.screen = pg.display.set_mode((X, Y)) # TODO: pg.FULLSCREEN
        self.scene = None

    def run(self):
        pg.init()
        self.clock = pg.time.Clock()
        self.setup()
        self.event_loop()

    def event_loop(self):
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    return

            # all_group.clear(screen, background)
            #self.all_group.update()
            #pg.display.update(dirty)

            self.scene.render(self.screen)
            pg.display.flip()
            self.clock.tick(FPS)

    def set_scene(self, scene):
        if self.scene:
            self.scene.teardown()

        scene.setup()
        self.scene = scene

    @abstractmethod
    def setup(self):
        pass

class GuessGame(Gamebook):
    def setup(self):
        self.set_scene(Scene())

class Scene():
    def __init__(self):
        self.actors = []
        self.sprites_group = pg.sprite.Group() # pg.sprite.RenderUpdates()

    def add_actor(self, actor):
        actor.add(self.sprites_group)
        self.actors.append(actor)

    def render(self, screen):
        for actor in self.actors:
            actor.update()

        # Doesnt seem neccessary with display flip?
        #self.sprites_group.update()

        self.sprites_group.draw(screen)
        for actor in self.actors:
            actor.draw_dialogs(screen)
        
    def setup(self):
        robot1 = Actor('crocodile')
        robot1.set_position(250, 450)
        self.add_actor(robot1)


class Actor():
    ASSETS_DIR = 'assets'
    DEFAULT = 'default'
    DIALOG_FONT = None
    ORIENTATION_LEFT = 'left'
    ORIENTATION_RIGHT = 'right'

    def __init__(self, name, orientation = ORIENTATION_RIGHT):
        if not Actor.DIALOG_FONT:
            Actor.DIALOG_FONT = pg.font.SysFont(None, 40)

        self.images = {}
        self.name = name
        self.orientation = orientation
        self.state = Actor.DEFAULT
        self.frame = 0
        self.dialog = 'Bazinga'

        # Main actor's sprite
        self.actor_sprite = pg.sprite.Sprite()
        self.load_images()
        self._set_image(self.images[self.state][0])
        self.actor_sprite.rect = self.actor_sprite.image.get_rect()

    def add(self, group):
        self.actor_sprite.add(group)

    def set_position(self, x, y):
        self.actor_sprite.rect.center = (x, y)

    def set_dialog(self, dialog):
        self.dialog = dialog

    def load_images(self):
        asset_dir = Path(Actor.ASSETS_DIR) / self.name
        for d in Path(asset_dir).glob('*'):
            self.images[d.name] = [pg.image.load(img) for img in d.glob('*.png')]

    def update(self):
        self.frame += 1
        if self.frame >= FPS:
            self.frame = 0

        state_images = self.images[self.state]
        self._set_image(state_images[self.frame // (FPS // len(state_images))])

    def draw_dialogs(self, screen):
        if self.dialog:
            dialog_surface = Actor.DIALOG_FONT.render(self.dialog, True, WHITE)
            x, y = self.actor_sprite.rect.center
            if self.orientation == Actor.ORIENTATION_LEFT:
                x -= 160
            else:
                x += 160
            screen.blit(dialog_surface, (x, y))



    def _set_image(self, image):
        self.actor_sprite.image = image

def gamebook_main():
    GuessGame().run()

if __name__ == '__main__':
    gamebook_main()

