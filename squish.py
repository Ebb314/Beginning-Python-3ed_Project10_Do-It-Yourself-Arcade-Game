import os
import pygame
import sys

from pygame.locals import *

import config
import objects

"This module contains the main game logic of the Squish game."


class State:

    """
    A generic game state class that can handle events and display
    itself on a given surface.
    """

    def handle(self, event):
        """
        Default event handling only deals with quitting.
        """
        if event.type == QUIT:
            sys.exit()
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            sys.exit()

    def first_display(self, screen):
        """
        Used to display the State for the first time. Fills the screen
        with the background color.
        """
        screen.fill(config.background_color)
        # Remember to call flip, to make the changes visible:
        pygame.display.flip()

    def display(self, screen):
        """
        Used to display the State after it has already been displayed
        once. The default behavior is to do nothing.
        """
        pass


class Paused(State):
    """
    A simple, paused game state, which may be broken out of by pressing
    either a keyboard key or the mouse button.
    """

    finished = 0  # Has the user ended the pause?
    image = None  # Set this to a file name if you want an image
    text = ''    # Set this to some informative text

    def handle(self, event):
        """
        Handles events by delegating to State (which handles quitting
        in general) and by reacting to key presses and mouse
        clicks. If a key is pressed or the mouse is clicked,
        self.finished is set to true.
        """
        State.handle(self, event)
        if event.type in [MOUSEBUTTONDOWN, KEYDOWN]:
            self.finished = 1

    def update(self, game):
        """
        Update the level. If a key has been pressed or the mouse has
        been clicked (i.e., self.finished is true), tell the game to
        move to the state represented by self.next_state() (should be
        implemented by subclasses).
        """
        if self.finished:
            game.next_state = self.next_state()

    def first_display(self, screen):
        """
        The first time the Paused state is displayed, draw the image
        (if any) and render the text.
        """
        # First, clear the screen by filling it with the background color:
        screen.fill(config.background_color)

        # Create a Font object that uses an exogenous font and a specified font size:
        font = pygame.font.Font(config.font_path, config.font_size)

        # Get the lines of text in self.text, ignoring empty lines at
        # the top or bottom:
        lines = self.text.strip().splitlines()

        # Calculate the height of the text (using font.get_linesize()
        # to get the height of each line of text):
        height = len(lines) * font.get_linesize()

        # Calculate the placement of the text (centered on the screen):
        center, top = screen.get_rect().center
        top -= height // 2

        # If there is an image to display...
        if self.image:
            # load it:
            image = pygame.image.load(self.image).convert()
            # get its rect:
            r = image.get_rect()
            # move the text down by half the image height:
            top += r.height // 2
            # place the image 20 pixels above the text:
            r.midbottom = center, top - 20
            # blit the image to the screen:
            screen.blit(image, r)

        antialias = True   # Smooth the text
        black = 0, 0, 0  # Render it as black

        # Render all the lines, starting at the calculated top, and
        # move down font.get_linesize() pixels for each line:
        for line in lines:
            text = font.render(line.strip(), antialias, black)
            r = text.get_rect()
            r.midtop = center, top
            screen.blit(text, r)
            top += font.get_linesize()

        # Display all the changes:
        pygame.display.flip()

    def next_state(self):
        pass


class StartUp(Paused):
    """
    A paused state that allows the player to select a game mode - in a
    banana mode, where the goal is to avoid collisions with the weights,
    or in a basket mode with the aim of catching all the falling eggs.
    """

    image = config.splash_image

    def __init__(self):
        self.next_state = None
        self.btn_x1, self.btn_y1, self.btn_x2, self.btn_y2 = 200, 500, 620, 500
        self.btn_w, self.btn_h = 200, 50

    def display(self, screen):

        font = pygame.font.Font(config.font_path, 30)

        pygame.draw.rect(screen, config.btn1_color, (self.btn_x1, self.btn_y1, self.btn_w, self.btn_h))
        pygame.draw.rect(screen, config.btn2_color, (self.btn_x2, self.btn_y2, self.btn_w, self.btn_h))
        text1 = font.render("Banana Mode", True, (255, 255, 255))
        text2 = font.render("Basket Mode", True, (255, 255, 255))
        tw1, th1 = text1.get_size()
        tw2, th2 = text2.get_size()
        tx1 = self.btn_x1 + self.btn_w / 2 - tw1 / 2
        ty1 = self.btn_y1 + self.btn_h / 2 - th1 / 2
        screen.blit(text1, (tx1, ty1))
        tx2 = self.btn_x2 + self.btn_w / 2 - tw2 / 2
        ty2 = self.btn_y2 + self.btn_h / 2 - th2 / 2
        screen.blit(text2, (tx2, ty2))

        pygame.display.update()
        pygame.display.flip()

    def handle(self, event):
        super().handle(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            if self.btn_x1 <= mouse_x <= self.btn_x1 + self.btn_w and \
                    self.btn_y1 <= mouse_y <= self.btn_y1 + self.btn_h:
                pygame.mouse.set_visible(False)
                self.next_state = Banana_StartUp
            elif self.btn_x2 <= mouse_x <= self.btn_x2 + self.btn_w and \
                    self.btn_y2 <= mouse_y <= self.btn_y2 + self.btn_h:
                pygame.mouse.set_visible(False)
                self.next_state = Basket_StartUp
            else:
                self.next_state = StartUp


class BananaLevel(State):
    """
    A game level. Takes care of counting how many weights have been
    dropped, moving the sprites around, and other tasks relating to
    game logic.
    """

    def __init__(self, mode=0, number=1, score=0, lives=5):

        self.crashsound = None

        self.mode = mode  # 0 for banana mode, 1 for basket mode
        # Default weight initial falling speed auxiliary parameter
        self.number = number
        # Score of 0 in the preliminary examination
        self.score = score
        # Initial lives for player
        self.lives = lives
        # How many weights remain to dodge in this level?
        self.remaining = config.weights_per_level

        #  Default weight falling speed initial increment parameter
        speed = config.drop_speed
        # One speed_increase added for each level above 1:
        speed += (self.number-1) * config.speed_increase
        # Create the weight and banana:
        self.weight1 = objects.Weight1(speed)
        self.weight2 = objects.Weight2(speed)
        self.banana = objects.Banana()
        sprites_container = self.weight1, self.weight2,  self.banana  # This could contain more sprites...
        self.sprites = pygame.sprite.RenderUpdates(sprites_container)

    def update(self, game):
        """
        Updates the game state from the previous frame.
        """
        # Update all sprites:
        self.sprites.update()
        # If the banana touches the weight, tell the game to switch to
        # a GameOver state:
        if self.banana.touches(self.weight1) or self.banana.touches(self.weight2):
            self.crashsound = pygame.mixer.Sound(config.crash_sound)
            self.crashsound.play()

            if self.banana.touches(self.weight1):
                self.lives -= 2
                self.weight1.reset()
            elif self.banana.touches(self.weight2):
                self.lives -= 1
                self.weight2.reset()

            if self.lives <= 0:
                game.next_state = GameOver(mode=self.mode)

        # Otherwise, if the weight has landed, reset it. If all the
        # weights of this level have been dodged, tell the game to
        # switch to a LevelCleared state:
        elif self.weight1.landed or self.weight2.landed:

            if self.weight1.landed:
                self.score += config.score_for_weight16
                self.weight1.reset()
                self.remaining -= 1

            if self.weight2.landed:
                self.score += config.score_for_weight8
                self.weight2.reset()
                self.remaining -= 1

            if self.remaining == 0:
                game.next_state = LevelCleared(mode=self.mode, number=self.number, score=self.score)

    def display(self, screen):
        """
        Displays the state after the first display (which simply wipes
        the screen). As opposed to firstDisplay, this method uses
        pygame.display.update with a list of rectangles that need to
        be updated, supplied from self.sprites.draw.
        """
        screen.fill(config.background_color)
        updates = self.sprites.draw(screen)
        pygame.display.update(updates)

        #  Show score
        draw_score(screen, "Score:" + str(self.score), config.score_x, config.score_y)

        # Show lives left
        draw_lives(screen, self.lives, config.life_x, config.life_y, config.healthbar_image)

        pygame.display.flip()


class BasketLevel(State):
    """
    A game level. Takes care of counting how many weights have been
    dropped, moving the sprites around, and other tasks relating to
    game logic.
    """

    def __init__(self, mode=1, number=1, score=0, lives=5):

        self.crashsound = None

        self.mode = mode  # mode = 1
        # Default weight initial falling speed auxiliary parameter
        self.number = number
        # Score of 0 in the preliminary examination
        self.score = score
        # Initial lives for player
        self.lives = lives
        # How many weights remain to dodge in this level?
        self.remaining = config.weights_per_level

        #  Default weight falling speed initial increment parameter
        speed = config.drop_speed
        # One speed_increase added for each level above 1:
        speed += (self.number - 1) * config.speed_increase

        all_sprites = pygame.sprite.Group()
        # Create the eggs and the bucket:
        self.eggs = [objects.Egg(speed) for _ in range(config.egg_number)]
        self.basket = objects.Basket()
        all_sprites.add(self.basket)
        for egg in self.eggs:
            all_sprites.add(egg)
        self.sprites = pygame.sprite.RenderUpdates(all_sprites)
        # self.weight1 = objects.Weight1(speed)
        # self.weight2 = objects.Weight2(speed)
        # self.banana = objects.Banana()
        # sprites_container = self.weight1, self.weight2, self.banana  # This could contain more sprites...
        # self.sprites = pygame.sprite.RenderUpdates(sprites_container)

    def update(self, game):
        """
        Updates the game state from the previous frame.
        """
        # Update all sprites:
        self.sprites.update()
        # If the basket catches an egg, get 1 score and reset the egg
        for egg in self.eggs:
            if self.basket.touches(egg):
                self.score += 1
                self.remaining -= 1
                egg.reset()

                if self.remaining == 0:
                    game.next_state = LevelCleared(mode=self.mode, number=self.number, score=self.score)

            if egg.landed:
                self.crashsound = pygame.mixer.Sound(config.crash_sound)
                self.crashsound.play()
                self.lives -= 1
                egg.reset()

                if self.lives <= 0:
                    game.next_state = GameOver(self.mode)

    def display(self, screen):

        screen.fill(config.background_color)
        updates = self.sprites.draw(screen)
        pygame.display.update(updates)

        #  Show score
        draw_score(screen, "Score:" + str(self.score), config.score_x, config.score_y)

        # Show lives left
        draw_lives(screen, self.lives, config.life_x, config.life_y, config.healthbar_image)

        pygame.display.flip()


class Banana_Info(Paused):

    """
    A simple paused state that displays some information about the
    game. It is followed by a BananaLevel state (the first level).
    """

    next_state = BananaLevel
    text = '''
    In this game you are a banana,
    trying to survive a course in
    self-defense against fruit, where the
    participants will "defend" themselves
    against you with a 16 ton weight.'''


class Basket_Info(Paused):

    """
    A simple paused state that displays some information about the
    game. It is followed by a BasketLevel state (the first level).
    """

    next_state = BasketLevel
    text = '''
    In this game you are a basket, 
    attempting to catch eggs that are 
    being released or thrown from a source. 
    The objective is to catch 
    as many eggs as possible 
    without missing any or allowing 
    them to fall to the ground or 
    otherwise go uncaught.'''


class Banana_StartUp(Paused):

    """
    A paused state that displays a splash image and a welcome
    message. It is followed by a Banana_Info state.
    """

    next_state = Banana_Info
    image = config.splash_image
    text = '''
    Welcome to Squish,
    the game of Fruit Self-Defense'''


class Basket_StartUp(Paused):

    """
    A paused state that displays a splash image and a welcome
    message. It is followed by a Basket_Info state.
    """

    next_state = Basket_Info
    image = config.splash_image
    text = '''
    Welcome to Squish,
    the game of Egg Catcher'''


class LevelCleared(Paused):
    """
    A paused state that informs the user that he or she has cleared a
    given level. It is followed by the next level state.
    """

    def __init__(self, mode, number, score):
        self.level_up_sound = pygame.mixer.Sound(config.level_up_sound)
        self.level_up_sound.play()

        self.mode = mode
        self.number = number
        self.score = score
        self.text = '''Level {} cleared
        Click or press any key to start next level'''.format(self.number)

    def next_state(self):
        if self.mode == 0:
            return BananaLevel(self.mode, self.number + 1, self.score)
        elif self.mode == 1:
            return BasketLevel(self.mode, self.number + 1, self.score)


class GameOver(Paused):
    """
    A state that informs the user that he or she has lost the
    game. It is followed by the first level.
    """
    def __init__(self, mode):
        self.failsound = pygame.mixer.Sound(config.fail_sound)
        self.failsound.play()
        self.mode = mode

        if self.mode == 0:
            self.next_state = BananaLevel
        elif self.mode == 1:
            self.next_state = BasketLevel

    text = '''
    Game Over
    Click or press any key to Restart, Esc to Quit'''


def draw_score(surf, text: str, x, y):
    """
    Display the score in real time,
    the score will be added when the difficulty level increases,
    if the player dies, the score will be cleared.
    """
    font = pygame.font.Font(config.font_path, config.score_font_size)
    text_surface = font.render(text, True, config.font_color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def draw_lives(surf, live, x, y, img):
    """
    Show how many lives the player has left.
    """
    healthbar_img = pygame.image.load(img).convert()
    healthbar_img = pygame.transform.scale(healthbar_img, (25, 25))
    healthbar_img.set_colorkey((255, 255, 255))  # Transparent background colour (white here)
    if live > 0:
        for i in range(live):
            img_rect = healthbar_img.get_rect()
            img_rect.x = x + 30 * i
            img_rect.y = y
            surf.blit(healthbar_img, img_rect)
    else:
        pass


class Game:

    """
    A game object that takes care of the main event loop, including
    changing between the different game states.
    """

    def __init__(self, *args):
        # Get the directory where the game and the images are located:
        path = os.path.abspath(args[0])
        directory = os.path.split(path)[0]
        # Move to that directory (so that the image files may be
        # opened later on):
        os.chdir(directory)
        # Start with no state:
        self.state = None
        # Move to StartUp in the first event loop iteration:
        self.next_state = StartUp()

    def run(self):
        """
        This method sets things in motion. It performs some vital
        initialization tasks, and enters the main event loop.
        """
        pygame.init()  # This is needed to initialize all the pygame modules
        pygame.mixer.init()
        pygame.time.delay(1000)  # Wait 1 second for mixer to complete initialization
        # Decide whether to display the game in a window or to use the
        # full screen:
        flag = 0                  # Default (window) mode

        if config.full_screen:
            flag = FULLSCREEN     # Full screen mode
        screen_size = config.screen_size
        screen = pygame.display.set_mode(screen_size, flag)

        pygame.display.set_caption('Squish')
        clock = pygame.time.Clock()
        pygame.mouse.set_visible(True)

        # The main loop:
        while True:
            # (1) If nextState has been changed, move to the new state, and
            #     display it (for the first time):
            if self.state != self.next_state:
                self.state = self.next_state
                self.state.first_display(screen)
            # (2) Delegate the event handling to the current state:
            for event in pygame.event.get():
                self.state.handle(event)
            # (3) Update the current state:
            self.state.update(self)
            # (4) Display the current state:
            self.state.display(screen)
            clock.tick(config.FPS)


if __name__ == '__main__':
    squish = Game(*sys.argv)
    squish.run()
