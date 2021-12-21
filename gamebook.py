import pygame as pg
from pathlib import Path

WHITE = (255,255,255)
BLACK = (0,0,0)
FPS = 60
TIME_STEP = 0.1

GlobalGame = None
class Gamebook():
    TIMER_EVENT = pg.USEREVENT

    def __init__(self, X = 1920, Y = 1080):
        self.X = X
        self.Y = Y
        self.screen = pg.display.set_mode((X, Y)) # TODO: pg.FULLSCREEN
        self.scene = None
        self.time = 0.0
        pg.init()

        global GlobalGame
        if GlobalGame:
            raise RuntimeError("Game is already initialized")
        GlobalGame = self

    def run(self):
        self.clock = pg.time.Clock()
        self.event_loop()

    def advance_time(self, time):
        self.time += time
        self.scene.advance_time(time)

    def event_loop(self):
        pg.time.set_timer(Gamebook.TIMER_EVENT, round(TIME_STEP * 1000))
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    return
                if event.type == Gamebook.TIMER_EVENT:
                    self.advance_time(TIME_STEP)

            self.screen.fill(BLACK)
            self.scene.render(self.screen)
            pg.display.update()
            self.clock.tick(FPS)

    def set_scene(self, scene):
        if self.scene:
            self.scene.teardown()

        scene.setup()
        self.scene = scene

class Event:
    def __init__(self, time, action, *args):
        self.time = time
        self.action = action
        self.args = args

    def is_between(self, start, stop):
        return start <= self.time and self.time <= stop

class Schedule:
    def __init__(self):
        self.events = []
        self.next_event = 0.0

    def run_events(self, start, stop, actor):
        for event in self.events:
            if event.is_between(start, stop):
                getattr(actor, event.action)(*event.args)

    def add_event(self, action, *args):
        event = Event(self.next_event, action, *args)
        self.events.append(event)

    def wait(self, time):
        self.next_event += time

class Actor():
    ASSETS_DIR = 'assets'
    DEFAULT = 'default'
    DIALOG_FONT = None
    ORIENTATION_LEFT = 'left'
    ORIENTATION_RIGHT = 'right'

    def __init__(self, name, orientation = ORIENTATION_RIGHT, hidden = False):
        if not Actor.DIALOG_FONT:
            Actor.DIALOG_FONT = pg.font.SysFont(None, 40)

        self.images = {}
        self.flipped_images = {}
        self.schedule = Schedule()
        self.name = name
        self.orientation = orientation
        self.hidden = hidden
        self.state = Actor.DEFAULT
        self.frame = 0
        self.dialog = None

        # Main actor's sprite
        self.actor_sprite = pg.sprite.Sprite()
        self.load_images()
        self._set_image(self.images[self.state][0])
        self.actor_sprite.rect = self.actor_sprite.image.get_rect()

    def add(self, group):
        self.actor_sprite.add(group)

    def remove(self, group):
        self.actor_sprite.remove(group)

    def set_position(self, x, y):
        self.schedule.add_event('_set_position', x, y)

    def _set_position(self, x, y):
        self.actor_sprite.rect.center = (x, y)

    def set_dialog(self, dialog):
        self.schedule.add_event('_set_dialog', dialog)

    def _set_dialog(self, dialog):
        self.dialog = dialog

    def set_hidden(self, hidden):
        self.schedule.add_event('_set_hidden', hidden)

    def _set_hidden(self, hidden):
        self.hidden = hidden

    def load_images(self):
        asset_dir = Path(Actor.ASSETS_DIR) / self.name
        for d in Path(asset_dir).glob('*'):
            self.images[d.name] = [pg.image.load(img) for img in d.glob('*.png')]
            self.flipped_images[d.name] = [pg.transform.flip(img, True, False) for img in self.images[d.name]]

    def update(self):
        if self.hidden:
            return

        self.frame += 1
        if self.frame >= FPS:
            self.frame = 0

        state_images = self.images[self.state] if self.orientation == Actor.ORIENTATION_RIGHT else self.flipped_images[self.state]
        image_frame = self.frame // (FPS // len(state_images))
        self._set_image(state_images[image_frame])

    def draw_dialogs(self, screen):
        if self.dialog:
            dialog_surface = Actor.DIALOG_FONT.render(self.dialog, True, WHITE)
            x, y = self.actor_sprite.rect.center
            if self.orientation == Actor.ORIENTATION_LEFT:
                x -= 500
            else:
                x += 160
            screen.blit(dialog_surface, (x, y))

    def wait(self, time):
        self.schedule.wait(time)

    def _set_image(self, image):
        self.actor_sprite.image = image


class Scene():
    def __init__(self):
        self.actors = []
        self.schedule = Schedule()
        self.time = 0.0
        self.sprites_group = pg.sprite.Group()

    def new_actor(self, actor_name, hidden=False, orientation=Actor.ORIENTATION_RIGHT):
        actor = Actor(actor_name, hidden=hidden, orientation=orientation)
        actor.add(self.sprites_group) 
        self.actors.append(actor)
        return actor

    def advance_time(self, time):
        start = self.time
        self.time = start + time
        self.schedule.run_events(start, self.time, self)
        for actor in self.actors:
            actor.schedule.run_events(start, self.time, actor)

    def render(self, screen):
        for actor in self.actors:
            actor.update()
            if actor.hidden:
                actor.remove(self.sprites_group)
            else:
                actor.add(self.sprites_group)

        # Doesnt seem neccessary with display flip?
        #self.sprites_group.update()

        self.sprites_group.draw(screen)
        for actor in self.actors:
            actor.draw_dialogs(screen)

    def setup(self): pass

    def teardown(self): pass

