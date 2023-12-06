# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import pygame as pg
import random

pg.init()
pg.font.init()
pg.key.set_repeat(300, 50)

window_width = 1440
window_height = 900
person_img_width = 640
person_img_height = 640
background_color = (255, 189, 163)
card_coordinates = {
        0: (int((window_width / 2)) - person_img_width / 2, int((window_height / 2 - person_img_height / 2))),
        1: (int((window_width / 2)) - person_img_width / 2 + person_img_width / 3, int((window_height / 2 - person_img_height / 2))),
        2: (int((window_width / 2)) - person_img_width / 2 + 2 * person_img_width / 3, int((window_height / 2 - person_img_height / 2))),
        3: (int((window_width / 2)) - person_img_width / 2, int((window_height / 2 - person_img_height / 2 + person_img_height/3))),
        4: (int((window_width / 2)) - person_img_width / 2 + person_img_width / 3, int((window_height / 2 - person_img_height / 2 + person_img_height/3))),
        5: (int((window_width / 2)) - person_img_width / 2 + 2 * person_img_width / 3, int((window_height / 2 - person_img_height / 2 + person_img_height/3))),
        6: (int((window_width / 2)) - person_img_width / 2, int((window_height / 2 - person_img_height / 2 + 2 * person_img_height/3))),
        7: (int((window_width / 2)) - person_img_width / 2 + person_img_width / 3, int((window_height / 2 - person_img_height / 2 + 2 * person_img_height/3))),
        8: (int((window_width / 2)) - person_img_width / 2 + 2 * person_img_width / 3, int((window_height / 2 - person_img_height / 2 + 2 * person_img_height/3))),
}

screen = pg.display.set_mode([window_width, window_height])
clock = pg.time.Clock()

puzzle_list = None
answers_list = None
def gen_puzzle_list():
    global puzzle_list, answers_list
    answers_file = open('answers.txt', 'r')
    answers_raw = answers_file.read()
    answers_list = answers_raw.split("\n")
    puzzle_list = list(range(0, (len(answers_list))))
    answers_file.close()
    #print(puzzle_list)
    #print(answers_list)

def load_person_img(img):
    path = './images/' + img
    img = pg.image.load(path).convert()
    img = pg.transform.scale(img, (person_img_width, person_img_height))
    return img

def draw_person_img(person_img):
    position_x = int((window_width - person_img_width) / 2)
    position_y = int((window_height - person_img_height) / 2)
    screen.blit(person_img, (position_x, position_y))

def load_card():
    card = pg.image.load('./images/card.jpg').convert()
    card = pg.transform.scale(card, (person_img_width / 3, person_img_height / 3))
    return card

def draw_card(surf, position, opacity=255):
    surf.set_alpha(opacity)
    screen.blit(surf, card_coordinates[position])

def fade_card(surf, position):
    global counter
    op = 255 - 15*counter
    if counter < 18:
        draw_card(surf, position, op)
    counter += 1

def draw_title():
    font = pg.font.SysFont('Comic Sans MS', 64)
    text = font.render('Quem é esse Pokémon?', True, (255, 90, 90))
    screen.blit(text,(int(0.5 * window_width - text.get_width() / 2), int(0.07 * window_height - text.get_height() / 2)))

def write_text_top(general_string, color):
    font = pg.font.SysFont('Comic Sans MS', 64)
    text = font.render(general_string, True, color)
    screen.blit(text,(int(0.5 * window_width - text.get_width() / 2), int(0.07 * window_height - text.get_height() / 2)))
def write_text_bottom(general_string, color):
    font = pg.font.SysFont('Comic Sans MS', 64)
    text = font.render(general_string, True, color)
    screen.blit(text,(int(0.5 * window_width - text.get_width() / 2), int(0.92 * window_height - text.get_height() / 2)))
def draw_timer(current_time):
    font = pg.font.SysFont('Comic Sans MS', 128)
    text = font.render(str(current_time), True, (255, 255, 255))
    screen.blit(text, (int(0.85 * window_width - text.get_width()/2), int(0.3 * window_height - text.get_height()/2)))

def start_timer():
    return pg.time.get_ticks()

def get_time_sec(start_ticks):
    return int((pg.time.get_ticks() - start_ticks)/1000)

def draw_textbox(color = (0, 0, 0)):
    bound_rect = pg.Rect(int(0.2 * window_width), int(0.88 * window_height-10), int(0.6*window_width), int(0.10*window_height))
    pg.draw.rect(screen, background_color, bound_rect)
    pg.draw.rect(screen, (255, 255, 255), bound_rect, width=5)
    font = pg.font.SysFont('Comic Sans MS', 64)
    text = font.render(input_string, True, color)
    screen.blit(text, (int(0.5 * window_width - text.get_width() / 2), int(0.88 * window_height-10)))

def remove_card():
    global remove_card_index, fade_position, card_positions, counter
    if len(card_positions) > 0:
        remove_card_index = random.randrange(len(card_positions))
        fade_position = card_positions[remove_card_index]
        card_positions.pop(remove_card_index)
        counter = 0

def hover_next_round_button():
    if int(0.75 * window_width) < cursor_position[0] < int(0.98 * window_width) and int(0.7 * window_height) < cursor_position[1] < int(0.8 * window_height):
        return True
    else:
        return False

def hover_request_button():
    if int(0.02 * window_width) < cursor_position[0] < int(0.25 * window_width) and int(0.7 * window_height) < cursor_position[1] < int(0.8 * window_height):
        return True
    else:
        return False

def draw_next_round_button():
    if hover_next_round_button():
        color = (255, 90, 90)
    else:
        color = (255, 127, 127)
    bound_rect = pg.Rect(int(0.75 * window_width), int(0.7 * window_height), int(0.23*window_width), int(0.1*window_height))
    pg.draw.rect(screen, color, bound_rect)
    pg.draw.rect(screen, (255, 255, 255), bound_rect, width=2)
    font = pg.font.SysFont('Comic Sans MS', 44)
    text = font.render('Próximo Round', True, (255, 255, 255))
    screen.blit(text, (int(0.865 * window_width - text.get_width() / 2), int(0.71 * window_height)))

def draw_play_again_button():
    if hover_next_round_button():
        color = (255, 90, 90)
    else:
        color = (255, 127, 127)
    bound_rect = pg.Rect(int(0.75 * window_width), int(0.7 * window_height), int(0.23*window_width), int(0.1*window_height))
    pg.draw.rect(screen, color, bound_rect)
    pg.draw.rect(screen, (255, 255, 255), bound_rect, width=2)
    font = pg.font.SysFont('Comic Sans MS', 38)
    text = font.render('Jogar Novamente', True, (255, 255, 255))
    screen.blit(text, (int(0.865 * window_width - text.get_width() / 2), int(0.715 * window_height)))

def draw_request_button():
    if hover_request_button():
        color = (255, 90, 90)
    else:
        color = (255, 127, 127)
    bound_rect = pg.Rect(int(0.02 * window_width), int(0.7 * window_height), int(0.23*window_width), int(0.1*window_height))
    pg.draw.rect(screen, color, bound_rect)
    pg.draw.rect(screen, (255, 255, 255), bound_rect, width=2)
    font = pg.font.SysFont('Comic Sans MS', 44)
    text = font.render('Mostrar +1', True, (255, 255, 255))
    screen.blit(text, (int(0.135 * window_width - text.get_width() / 2), int(0.71 * window_height)))

def draw_points():
    font = pg.font.SysFont('Comic Sans MS', 48)
    text = font.render('Pontuação total:', True, (255, 255, 255))
    screen.blit(text,(int(0.14 * window_width - text.get_width() / 2), int(0.2 * window_height - text.get_height() / 2)))


    font = pg.font.SysFont('Comic Sans MS', 128)
    text = font.render(str(total_points), True, (255, 90, 90))
    screen.blit(text,(int(0.14 * window_width - text.get_width() / 2), int(0.3 * window_height - text.get_height() / 2)))

    font = pg.font.SysFont('Comic Sans MS', 38)
    text = font.render('Pontuação do round:', True, (255, 255, 255))
    screen.blit(text,(int(0.14 * window_width - text.get_width() / 2), int(0.45 * window_height - text.get_height() / 2)))

    font = pg.font.SysFont('Comic Sans MS', 128)
    text = font.render(str(round_points), True, (255, 90, 90))
    screen.blit(text,
                (int(0.14 * window_width - text.get_width() / 2), int(0.55 * window_height - text.get_height() / 2)))

def check_answer():
    if input_string == correct_answer:
        return True

    return False

def input():
    global running, input_string, game_status, check_string, cursor_position, card_positions, total_points, times_card_button_was_pressed

    cursor_position = pg.mouse.get_pos()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if game_status == 'round started':
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_BACKSPACE:
                    input_string = input_string[:-1]
                elif event.key == pg.K_RETURN:
                    check_string = True
                elif len(input_string) <= 18:
                    input_string += event.unicode
                    input_string = input_string.upper()
            if event.type == pg.MOUSEBUTTONDOWN:
                if hover_request_button():
                    if times_card_button_was_pressed < 8:
                        times_card_button_was_pressed += 1
                        remove_card()
        if game_status == 'round won':
            if event.type == pg.MOUSEBUTTONDOWN:
                if hover_next_round_button():
                    game_status = 'init'
        if game_status == 'game over' or game_status == 'round lost':
            if event.type == pg.MOUSEBUTTONDOWN:
                if hover_next_round_button():
                    total_points = 0
                    game_status = 'init'

def update():
    global chosen_puzzle, correct_answer, person_img, start_t, current_time, game_status, card_positions, previous_time, counter, remove_card_index, fade_position, check_string, input_string, puzzle_list, total_points, round_points, times_card_button_was_pressed

    if game_status == 'init':
        times_card_button_was_pressed = 0
        round_points = 0
        input_string = ''
        chosen_puzzle = random.choice(puzzle_list)
        puzzle_list.remove(chosen_puzzle)
        person_img = load_person_img(str(chosen_puzzle) + '.jpg')
        correct_answer = answers_list[chosen_puzzle]
        #print(correct_answer)
        start_t = start_timer()
        card_positions = list(range(0, 9))
        game_status = 'preparing'

    if game_status == 'preparing':
        previous_time = current_time
        current_time = get_time_sec(start_t)
        current_time = 3 - current_time
        if current_time == 0:
            game_status = 'go'
            start_t = start_timer()

    if game_status == 'go':
        previous_time = current_time
        current_time = get_time_sec(start_t)
        if current_time - previous_time != 0:
            game_status = 'round started'
            start_t = start_timer()

    if game_status == 'round started':
        previous_time = current_time
        current_time = get_time_sec(start_t)
        current_time = 60 - current_time
        if (current_time == 60 or current_time == 45 or current_time == 30 or current_time == 15) and (current_time - previous_time != 0):
                remove_card()
        if current_time == 0:
            game_status = 'round lost'
            round_points = 0
            gen_puzzle_list()
        if check_string == True:
            if check_answer() == True:
                card_positions = []
                round_points = current_time + 80 - 10 * times_card_button_was_pressed
                total_points += round_points
                if len(puzzle_list) > 0:
                    game_status = 'round won'
                else:
                    game_status = 'game over'
                    gen_puzzle_list()
            else:
                input_string = ''
            check_string = False

def render():
    if game_status == 'init' or game_status == 'preparing' or game_status == 'go' or game_status == 'round started':
        draw_person_img(person_img)
        draw_title()
        if len(card_positions) > 0:
            for position in card_positions:
                draw_card(card, position)

    if game_status == 'preparing':
        draw_timer(current_time)

    if game_status == 'go':
        draw_timer('Vai')

    if game_status == 'round started':
        draw_timer(current_time)
        draw_textbox()
        draw_request_button()
        if fade_position != 999:
            fade_card(card, fade_position)

    if game_status == 'round lost':
        draw_person_img(person_img)
        draw_timer(0)
        write_text_top('Game Over!', (255, 0, 0))
        write_text_bottom(f'Resposta: {correct_answer}', (255, 255, 255))
        draw_play_again_button()
        draw_points()

    if game_status == 'round won':
        draw_person_img(person_img)
        write_text_top('Correto!', (0x3C, 0xB0, 0x43))
        draw_timer(current_time)
        draw_textbox((0x3C, 0xB0, 0x43))
        draw_next_round_button()
        draw_points()

    if game_status == 'game over':
        draw_person_img(person_img)
        write_text_top('Correto!', (0x3C, 0xB0, 0x43))
        draw_timer(current_time)
        draw_textbox((0x3C, 0xB0, 0x43))
        draw_play_again_button()
        draw_points()

    pg.display.flip()


running = True
card = load_card()
counter = 0
card_positions = None
current_time = 3
game_status = 'init'
start_t = 0
previous_time = 0
remove_card_index = 0
fade_position = 999
input_string = ''
check_string = False
correct_answer = None
person_img = None
chosen_puzzle = None
cursor_position = None
total_points = 0
round_points = 0
times_card_button_was_pressed = None

gen_puzzle_list()
while running:
    screen.fill(background_color)
    clock.tick(30)
    input()
    update()
    render()

pg.quit()
