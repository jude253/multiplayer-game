""" pygame.examples.aliens

Shows a mini game where you have to defend against aliens.

What does it show you about pygame?

* pg.sprite, the difference between Sprite and Group.
* dirty rectangle optimization for processing for speed.
* music with pg.mixer.music, including fadeout
* sound effects with pg.Sound
* event processing, keyboard handling, QUIT handling.
* a main loop frame limited with a game clock from pg.time.Clock
* fullscreen switching.


Controls
--------

* Left and right arrows to move.
* Space bar to shoot
* f key to toggle between fullscreen.

--------
NOTE: Ported from pygame.examples.aliens
"""

import random
from typing import List

# import basic pygame modules
from pydantic import BaseModel, ConfigDict
import pydantic
import pygame as pg
from pygame import examples as main_dir
from importlib.resources import as_file, files

# see if we can load more than standard BMP
if not pg.image.get_extended():
    raise SystemExit("Sorry, extended image module required")


# game constants
MAX_SHOTS = 2  # most player bullets onscreen
ALIEN_ODDS = 22  # chances a new alien appears
BOMB_ODDS = 60  # chances a new bomb will drop
ALIEN_RELOAD = 12  # frames between new aliens
SCREENRECT = pg.Rect(0, 0, 640, 480)
SCORE = 0


def get_file(file):
    examples_dir_files = files(main_dir)
    with as_file(examples_dir_files) as examples_dir:
        data_dir_filepath = examples_dir.joinpath("data")
        file = data_dir_filepath.joinpath(file)
    return file


def load_image(file):
    """loads an image, prepares it for play"""
    file = get_file(file)
    try:
        surface = pg.image.load(file)
    except pg.error:
        raise SystemExit(f'Could not load image "{file}" {pg.get_error()}')
    return surface.convert()


def load_sound(file):
    """because pygame can be compiled without mixer."""
    if not pg.mixer:
        return None
    file = get_file(file)
    try:
        sound = pg.mixer.Sound(file)
        return sound
    except pg.error:
        print(f"Warning, unable to load, {file}")
    return None


# Each type of game object gets an init and an update function.
# The update function is called once per frame, and it is when each object should
# change its current position and state.
#
# The Player object actually gets a "move" function instead of update,
# since it is passed extra information about the keyboard.


class Player(pg.sprite.Sprite):
    """Representing the player as a moon buggy type car."""

    speed = 10
    bounce = 24
    gun_offset = -11
    images: List[pg.Surface] = []

    def __init__(self, *groups):
        pg.sprite.Sprite.__init__(self, *groups)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=SCREENRECT.midbottom)
        self.reloading = 0
        self.origtop = self.rect.top
        self.facing = -1

    def move(self, direction):
        if direction:
            self.facing = direction
        self.rect.move_ip(direction * self.speed, 0)
        self.rect = self.rect.clamp(SCREENRECT)
        if direction < 0:
            self.image = self.images[0]
        elif direction > 0:
            self.image = self.images[1]
        self.rect.top = self.origtop - (self.rect.left // self.bounce % 2)

    def gunpos(self):
        pos = self.facing * self.gun_offset + self.rect.centerx
        return pos, self.rect.top


class Alien(pg.sprite.Sprite):
    """An alien space ship. That slowly moves down the screen."""

    speed = 13
    animcycle = 12
    images: List[pg.Surface] = []

    def __init__(self, *groups):
        pg.sprite.Sprite.__init__(self, *groups)
        self.image = self.images[0]
        self.rect = self.image.get_rect()
        self.facing = random.choice((-1, 1)) * Alien.speed
        self.frame = 0
        if self.facing < 0:
            self.rect.right = SCREENRECT.right

    def update(self, *args, **kwargs):
        self.rect.move_ip(self.facing, 0)
        if not SCREENRECT.contains(self.rect):
            self.facing = -self.facing
            self.rect.top = self.rect.bottom + 1
            self.rect = self.rect.clamp(SCREENRECT)
        self.frame = self.frame + 1
        self.image = self.images[self.frame // self.animcycle % 3]


class Explosion(pg.sprite.Sprite):
    """An explosion. Hopefully the Alien and not the player!"""

    defaultlife = 12
    animcycle = 3
    images: List[pg.Surface] = []

    def __init__(self, actor, *groups):
        pg.sprite.Sprite.__init__(self, *groups)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=actor.rect.center)
        self.life = self.defaultlife

    def update(self, *args, **kwargs):
        """called every time around the game loop.

        Show the explosion surface for 'defaultlife'.
        Every game tick(update), we decrease the 'life'.

        Also we animate the explosion.
        """
        self.life = self.life - 1
        self.image = self.images[self.life // self.animcycle % 2]
        if self.life <= 0:
            self.kill()


class Shot(pg.sprite.Sprite):
    """a bullet the Player sprite fires."""

    speed = -11
    images: List[pg.Surface] = []

    def __init__(self, pos, *groups):
        pg.sprite.Sprite.__init__(self, *groups)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=pos)

    def update(self, *args, **kwargs):
        """called every time around the game loop.

        Every tick we move the shot upwards.
        """
        self.rect.move_ip(0, self.speed)
        if self.rect.top <= 0:
            self.kill()


class Bomb(pg.sprite.Sprite):
    """A bomb the aliens drop."""

    speed = 9
    images: List[pg.Surface] = []

    def __init__(self, alien, explosion_group, *groups):
        pg.sprite.Sprite.__init__(self, *groups)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=alien.rect.move(0, 5).midbottom)
        self.explosion_group = explosion_group

    def update(self, *args, **kwargs):
        """called every time around the game loop.

        Every frame we move the sprite 'rect' down.
        When it reaches the bottom we:

        - make an explosion.
        - remove the Bomb.
        """
        self.rect.move_ip(0, self.speed)
        if self.rect.bottom >= 470:
            Explosion(self, self.explosion_group)
            self.kill()


class Score(pg.sprite.Sprite):
    """to keep track of the score."""

    def __init__(self, *groups, game=None):
        pg.sprite.Sprite.__init__(self, *groups)
        self.game = game
        self.font = pg.font.Font(None, 20)
        self.font.set_italic(1)
        self.color = "white"
        self.lastscore = -1
        self.update()
        self.rect = self.image.get_rect().move(10, 450)

    def update(self, *args, **kwargs):
        """We only update the score in update() when it has changed."""
        if self.game.score != self.lastscore:
            self.lastscore = self.game.score
            msg = f"Score: {self.game.score}"
            self.image = self.font.render(msg, 0, self.color)


class Game(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    fullscreen: bool
    winstyle: int
    bestdepth: int
    screen: pg.Surface
    bgdtile: pg.Surface
    background: pg.Surface
    boom_sound: pg.mixer.Sound
    shoot_sound: pg.mixer.Sound
    aliens: pg.sprite.Group
    shots: pg.sprite.Group
    bombs: pg.sprite.Group
    all: pg.sprite.RenderUpdates
    lastalien: pg.sprite.GroupSingle
    alienreload: int
    clock: pg.time.Clock
    score: int
    player: Player

    def create_new_alien(self):
        if self.alienreload:
            self.alienreload = self.alienreload - 1
        elif not int(random.random() * ALIEN_ODDS):
            Alien(
                self.aliens, self.all, self.lastalien
            )  # note, this 'lives' because it goes into a sprite group
            self.alienreload = ALIEN_RELOAD


def create_game(winstyle=0):
    # Initialize pygame
    if pg.get_sdl_version()[0] == 2:
        pg.mixer.pre_init(44100, 32, 2, 1024)
    pg.init()
    if pg.mixer and not pg.mixer.get_init():
        print("Warning, no sound")
        pg.mixer = None

    fullscreen = False
    # Set the display mode
    winstyle = 0  # |FULLSCREEN
    bestdepth = pg.display.mode_ok(SCREENRECT.size, winstyle, 32)
    screen = pg.display.set_mode(SCREENRECT.size, winstyle, bestdepth)

    # Load images, assign to sprite classes
    # (do this before the classes are used, after screen setup)
    img = load_image("player1.gif")
    Player.images = [img, pg.transform.flip(img, 1, 0)]
    img = load_image("explosion1.gif")
    Explosion.images = [img, pg.transform.flip(img, 1, 1)]
    Alien.images = [load_image(im) for im in ("alien1.gif", "alien2.gif", "alien3.gif")]
    Bomb.images = [load_image("bomb.gif")]
    Shot.images = [load_image("shot.gif")]

    # decorate the game window
    icon = pg.transform.scale(Alien.images[0], (32, 32))
    pg.display.set_icon(icon)
    pg.display.set_caption("Pygame Aliens")
    pg.mouse.set_visible(0)

    # create the background, tile the bgd image
    bgdtile = load_image("background.gif")
    background = pg.Surface(SCREENRECT.size)
    for x in range(0, SCREENRECT.width, bgdtile.get_width()):
        background.blit(bgdtile, (x, 0))
    screen.blit(background, (0, 0))
    pg.display.flip()

    # load the sound effects
    boom_sound = load_sound("boom.wav")
    shoot_sound = load_sound("car_door.wav")
    if pg.mixer:
        music = get_file("house_lo.wav")
        pg.mixer.music.load(music)
        pg.mixer.music.play(-1)

    # Initialize Game Groups
    aliens = pg.sprite.Group()
    shots = pg.sprite.Group()
    bombs = pg.sprite.Group()
    all = pg.sprite.RenderUpdates()
    lastalien = pg.sprite.GroupSingle()

    # Create Some Starting Values
    alienreload = ALIEN_RELOAD
    clock = pg.time.Clock()

    # initialize our starting sprites
    score = SCORE
    player = Player(all)

    game = Game(
        fullscreen=fullscreen,
        winstyle=winstyle,
        bestdepth=bestdepth,
        screen=screen,
        bgdtile=bgdtile,
        background=background,
        boom_sound=boom_sound,
        shoot_sound=shoot_sound,
        aliens=aliens,
        shots=shots,
        bombs=bombs,
        all=all,
        lastalien=lastalien,
        alienreload=alienreload,
        clock=clock,
        score=score,
        player=player,
    )

    if pg.font:
        all.add(Score(all, game=game))
    return game


def main(winstyle=0):
    game = create_game(winstyle=0)
    print(game.model_dump(include=["shots"]))
    # Run our main loop whilst the player is alive.
    while game.player.alive():
        # get input
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                return
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_f:
                    if not game.fullscreen:
                        print("Changing to FULLSCREEN")
                        screen_backup = game.screen.copy()
                        game.screen = pg.display.set_mode(
                            SCREENRECT.size, winstyle | pg.FULLSCREEN, game.bestdepth
                        )
                        game.screen.blit(screen_backup, (0, 0))
                    else:
                        print("Changing to windowed mode")
                        screen_backup = game.screen.copy()
                        game.screen = pg.display.set_mode(
                            SCREENRECT.size, winstyle, game.bestdepth
                        )
                        game.screen.blit(screen_backup, (0, 0))
                    pg.display.flip()
                    game.fullscreen = not game.fullscreen

        keystate = pg.key.get_pressed()

        # clear/erase the last drawn sprites
        game.all.clear(game.screen, game.background)

        # update all the sprites
        game.all.update()

        # handle player input
        direction = keystate[pg.K_RIGHT] - keystate[pg.K_LEFT]
        game.player.move(direction)
        firing = keystate[pg.K_SPACE]
        if not game.player.reloading and firing and len(game.shots) < MAX_SHOTS:
            Shot(game.player.gunpos(), game.shots, game.all)
            if pg.mixer and game.shoot_sound is not None:
                game.shoot_sound.play()
        game.player.reloading = firing

        # Create new alien
        game.create_new_alien()

        # Drop bombs
        if game.lastalien and not int(random.random() * BOMB_ODDS):
            Bomb(game.lastalien.sprite, game.all, game.bombs, game.all)

        # Detect collisions between aliens and players.
        for alien in pg.sprite.spritecollide(game.player, game.aliens, 1):
            if pg.mixer and game.boom_sound is not None:
                game.boom_sound.play()
            Explosion(alien, game.all)
            Explosion(game.player, game.all)
            game.score = game.score + 1
            game.player.kill()

        # See if shots hit the aliens.
        for alien in pg.sprite.groupcollide(game.aliens, game.shots, 1, 1).keys():
            if pg.mixer and game.boom_sound is not None:
                game.boom_sound.play()
            Explosion(alien, game.all)
            game.score = game.score + 1

        # See if alien bombs hit the player.
        for bomb in pg.sprite.spritecollide(game.player, game.bombs, 1):
            if pg.mixer and game.boom_sound is not None:
                game.boom_sound.play()
            Explosion(game.player, game.all)
            Explosion(bomb, game.all)
            game.player.kill()

        # draw the scene
        dirty = game.all.draw(game.screen)
        pg.display.update(dirty)

        # cap the framerate at 40fps. Also called 40HZ or 40 times per second.
        game.clock.tick(40)

    if pg.mixer:
        pg.mixer.music.fadeout(1000)
    pg.time.wait(1000)


# call the "main" function if running this script
if __name__ == "__main__":
    main()
    pg.quit()
