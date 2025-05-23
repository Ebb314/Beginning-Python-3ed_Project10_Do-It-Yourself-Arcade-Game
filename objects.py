from random import randrange

import config
import pygame

"This module contains the game objects of the Squish game."


class SquishSprite(pygame.sprite.Sprite):

    """
    Generic superclass for all sprites in Squish. The constructor
    takes care of loading an image, setting up the sprite rect, and
    the area within which it is allowed to move. That area is governed
    by the screen size and the margin.
    """

    def __init__(self, image):
        super().__init__()
        self.image = pygame.image.load(image).convert()
        self.image.set_colorkey((255, 255, 255))  # Transparent background colour (white here)
        self.rect = self.image.get_rect()
        screen = pygame.display.get_surface()
        shrink = -config.margin * 2
        self.area = screen.get_rect().inflate(shrink, shrink)


class Weight1(SquishSprite):

    """
    A falling weight. It uses the SquishSprite constructor to set up
    its weight image, and will fall with a speed given as a parameter
    to its constructor.
    """

    def __init__(self, speed):
        super().__init__(config.weight16_image)
        self.landed = None
        self.speed = speed
        self.reset()

    def reset(self):
        """
        Move the weight to the top of the screen (just out of sight)
        and place it at a random horizontal position.
        """
        x = randrange(self.area.left, self.area.right)
        self.rect.midbottom = x, 0 - randrange(0, 300)

    def update(self):
        """
        Move the weight vertically (downwards) a distance
        corresponding to its speed. Also set the landed attribute
        according to whether it has reached the bottom of the screen.
        """

        # Add a delay for each update to adapt to the player's reaction time,
        # and get the optimal value of 0.002 seconds after parameterization.
        self.rect.top += self.speed + 2
        self.landed = self.rect.top >= self.area.bottom


class Weight2(SquishSprite):

    """
    A falling weight. It uses the SquishSprite constructor to set up
    its weight image, and will fall with a speed given as a parameter
    to its constructor.
    """

    def __init__(self, speed):
        super().__init__(config.weight8_image)
        self.landed = None
        self.speed = speed
        self.reset()

    def reset(self):
        """
        Move the weight to the top of the screen (just out of sight)
        and place it at a random horizontal position.
        """
        x = randrange(self.area.left, self.area.right)
        self.rect.midbottom = x, 0 - randrange(0, 300)

    def update(self):
        """
        Move the weight vertically (downwards) a distance
        corresponding to its speed. Also set the landed attribute
        according to whether it has reached the bottom of the screen.
        """

        # Add a delay for each update to adapt to the player's reaction time,
        # and get the optimal value of 0.002 seconds after parameterization.
        self.rect.top += self.speed + 1
        self.landed = self.rect.top >= self.area.bottom


class Banana(SquishSprite):

    """
    A desperate banana. It uses the SquishSprite constructor to set up
    its banana image, and will stay near the bottom of the screen,
    with its horizontal position governed by the current mouse
    position (within certain limits).
    """

    def __init__(self):
        super().__init__(config.banana_image)
        self.rect.bottom = self.area.bottom
        # These paddings represent parts of the image where there is
        # no banana. If a weight moves into these areas, it doesn't
        # constitute a hit (or, rather, a squish):
        self.pad_top = config.banana_pad_top
        self.pad_side = config.banana_pad_side

    def update(self):
        """
        Set the Banana's center x-coordinate to the current mouse
        x-coordinate, and then use the rect method clamp to ensure
        that the Banana stays within its allowed range of motion.
        """
        self.rect.centerx = pygame.mouse.get_pos()[0]
        self.rect = self.rect.clamp(self.area)

    def touches(self, other):
        """
        Determines whether the banana touches another sprite (e.g., a
        Weight). Instead of just using the rect method colliderect, a
        new rectangle is first calculated (using the rect method
        inflate with the side and top paddings) that does not include
        the 'empty' areas on the top and sides of the banana.
        """
        # Deflate the bounds with the proper padding:
        bounds = self.rect.inflate(-self.pad_side, -self.pad_top)
        # Move the bounds, so they are placed at the bottom of the Banana:
        bounds.bottom = self.rect.bottom
        # Check whether the bounds intersect with the other object's rect:
        return bounds.colliderect(other.rect)


class Egg(SquishSprite):
    def __init__(self, speed):
        super().__init__(config.egg_image)
        self.landed = None
        self.speed = speed
        self.reset()

    def reset(self):
        x = randrange(self.area.left, self.area.right)
        self.rect.midbottom = x, 0 - randrange(0, 1000)

    def update(self):
        self.rect.top += self.speed
        self.landed = self.rect.top >= self.area.bottom


class Basket(SquishSprite):
    def __init__(self):
        super().__init__(config.basket_image)
        self.rect.bottom = self.area.bottom
        self.pad_top = config.basket_pad_top
        self.pad_side = config.basket_pad_side

    def update(self):
        self.rect.centerx = pygame.mouse.get_pos()[0]
        self.rect = self.rect.clamp(self.area)

    def touches(self, other):
        bounds = self.rect.inflate(-self.pad_side, -self.pad_top)
        bounds.bottom = self.rect.bottom
        return bounds.colliderect(other.rect)
