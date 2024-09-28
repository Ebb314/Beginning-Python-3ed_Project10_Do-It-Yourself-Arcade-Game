# Configuration file for Squish
# -----------------------------

# Feel free to modify the configuration variables below to taste.
# If the game is too fast or too slow, try to modify the speed
# variables.

# Images in the game:
banana_image = 'banana.png'
weight16_image = 'weight1.png'
weight8_image = 'weight2.png'
splash_image = 'game_cover.png'
healthbar_image = 'healthbar.png'
basket_image = 'basket.png'
egg_image = 'egg.png'

font_path = 'font.ttf'

# General appearance:
screen_size = 1024, 768
background_color = 255, 255, 255
margin = 30
full_screen = 0
font_size = 48
score_font_size = 24
font_color = 0, 0, 0
score_x = 60
score_y = 20
life_x = 850
life_y = 20
btn1_color = 255, 0, 0  # red
btn2_color = 0, 255, 0  # green
btn1_pos_size = 300, 500, 100, 50
btn2_pos_size = 600, 500, 100, 50

# These affect the behavior of the game:
drop_speed = 1
banana_speed = 10
speed_increase = 1
weights_per_level = 10
banana_pad_top = 10
banana_pad_side = 10
basket_pad_top = 5
basket_pad_side = 5
score_for_weight16 = 2
score_for_weight8 = 1
FPS = 240
egg_number = 5

# Sounds in the game:
crash_sound = 'crash.wav'
fail_sound = 'fail.wav'
level_up_sound = 'levelup.wav'
