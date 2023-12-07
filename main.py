# Em resumo:
# Estagios do game: init > preparing > go > round started > round won
#                                                         > round lost (game over)
#                                                         > game over (todos concluidos)
# Main loop: input (verifica as entradas) > update (faz a maioria dos calculos) > render (atualiza o grafico)
#
# Como funciona o jogo:
# 1 card revelado no comeco, 60 segundos para tentar adivinhar o nome da pessoa
# A cada 15 segundos (45, 30, 15) e revelado um card
# O player pode clicar no botao de revelar um card, com o custo de 10 pontos perdidos na rodada
# Somente uma resposta certa (nao tem autocorretor)
# Caso o player acerte ele pode ir pra proxima rodada
# Caso o tempo acabe, e fim de jogo







# IMPORTS

import pygame as pg
import random


# FUNCOES DE SETUP DO PYGAME

pg.init()
pg.font.init()
pg.key.set_repeat(300, 50)


# VARIAVEIS AUXILIARES

window_width = 1440 # largura da janela
window_height = 900 # altura da janela
person_img_width = 640 # largura da imagem da pessoa
person_img_height = 640 # altura da imagem da pessoa
background_color = (255, 189, 163) # cor do plano de fundo
# coordenadas para desenhar os cartoes de interrogacao
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

puzzle_list = None # lista com os numeros de referencia para cada par imagem + resposta
answers_list = None # lista com as respostas

running = True # variavel auxiliar para o main loop
counter = 0 # contador auxiliar para o efeito de fade
card_positions = None # lista com os cartoes atualmente renderizadas
current_time = None # variavel auxiliar do tempo (em segundos)
game_status = 'init' # estagio atual do game
start_t = 0 # variavel para armazenar o tick inicial de um contador
previous_time = 0 # armazena o tempo (segundos) do frame anterior
remove_card_index = 0 # armazena o indice do proximo card a ser removido
fade_position = 999 # mesma coisa do remove_card_index, porem e menos volatil
input_string = '' # string que armazena o buffer de entrada do usuario
check_string = False # variavel auxiliar para checar se o enter foi pressionada (para testar a resposta)
correct_answer = None # variavel que vai armazenar a string da resposta certa do round atual
person_img = None # surface que vai conter a imagem da pessoa do round atual
chosen_puzzle = None # vai conter o indice auxiliar que define o par imagem + resposta
cursor_position = None # contem a posicao atual do cursor na janela
total_points = 0 # pontos totais acumulados durante as rodadas
round_points = 0 # pontos marcados na rodada atual
times_card_button_was_pressed = None # contador de quantas vezes o usuario clicou para revelar 1 cartao na rodada atual



# DEFINICAO DE FUNCOES

# gerador da lista de todas as possiveis pessoas (ela tem que ser recriada sempre que o jogo recomeca)
def gen_puzzle_list():
    global puzzle_list, answers_list
    answers_file = open('answers.txt', 'r')
    answers_raw = answers_file.read()
    answers_list = answers_raw.split("\n")
    puzzle_list = list(range(0, (len(answers_list))))
    answers_file.close()
    #print(puzzle_list)
    #print(answers_list)


# carrega e cria a sufrace da imagem da pessoa escolihda (a imagem sempre esta no formato 'indice.jpg')
def load_person_img(img):
    path = './images/' + img
    img = pg.image.load(path).convert()
    img = pg.transform.scale(img, (person_img_width, person_img_height))
    return img


# faz o blit (renderiza) a foto da pessoa na tela
def draw_person_img(person_img):
    position_x = int((window_width - person_img_width) / 2)
    position_y = int((window_height - person_img_height) / 2)
    screen.blit(person_img, (position_x, position_y))


# cria a surface do cartao
def load_card():
    card = pg.image.load('./images/card.jpg').convert()
    card = pg.transform.scale(card, (person_img_width / 3, person_img_height / 3))
    return card


# renderiza o cartao na tela
def draw_card(surf, position, opacity=255):
    surf.set_alpha(opacity)
    screen.blit(surf, card_coordinates[position])


# efeito grafico de fade out do cartao quando ele some
def fade_card(surf, position):
    global counter
    op = 255 - 15*counter
    if counter < 18:
        draw_card(surf, position, op)
    counter += 1


# renderiza o titulo na tela
def draw_title():
    font = pg.font.SysFont('Comic Sans MS', 64)
    text = font.render('Quem é esse Pokémon?', True, (255, 90, 90))
    screen.blit(text,(int(0.5 * window_width - text.get_width() / 2), int(0.07 * window_height - text.get_height() / 2)))


# renderiza um texto no topo da tela (o draw title ja tinha sido feito quando essa funcao foi pensada)
def write_text_top(general_string, color):
    font = pg.font.SysFont('Comic Sans MS', 64)
    text = font.render(general_string, True, color)
    screen.blit(text,(int(0.5 * window_width - text.get_width() / 2), int(0.07 * window_height - text.get_height() / 2)))


# renderiza um texto na parte de baixo da tela
def write_text_bottom(general_string, color):
    font = pg.font.SysFont('Comic Sans MS', 64)
    text = font.render(general_string, True, color)
    screen.blit(text,(int(0.5 * window_width - text.get_width() / 2), int(0.92 * window_height - text.get_height() / 2)))


# renderiza o cronometro regressivo na direita da tela
def draw_timer(current_time):
    font = pg.font.SysFont('Comic Sans MS', 128)
    text = font.render(str(current_time), True, (255, 255, 255))
    screen.blit(text, (int(0.85 * window_width - text.get_width()/2), int(0.3 * window_height - text.get_height()/2)))


# marca determinado tempo como referencia inicial de tempo
def start_timer():
    return pg.time.get_ticks()


# converte o tempo de ticks para segundos
def get_time_sec(start_ticks):
    return int((pg.time.get_ticks() - start_ticks)/1000)


# renderiza a caixa de texto de entrada + o texto que o usuario esta digitando
def draw_textbox(color = (0, 0, 0)):
    bound_rect = pg.Rect(int(0.2 * window_width), int(0.88 * window_height-10), int(0.6*window_width), int(0.10*window_height))
    pg.draw.rect(screen, background_color, bound_rect)
    pg.draw.rect(screen, (255, 255, 255), bound_rect, width=5)
    font = pg.font.SysFont('Comic Sans MS', 64)
    text = font.render(input_string, True, color)
    screen.blit(text, (int(0.5 * window_width - text.get_width() / 2), int(0.88 * window_height-10)))


# remove um cartao aleatorio dos cartoes que estao atualmente renderizadas
def remove_card():
    global remove_card_index, fade_position, card_positions, counter
    if len(card_positions) > 0:
        remove_card_index = random.randrange(len(card_positions))
        fade_position = card_positions[remove_card_index]
        card_positions.pop(remove_card_index)
        counter = 0


# testa se o cursor esta sobre o botao de proximo round (e o de jogar novamente)
def hover_next_round_button():
    if int(0.75 * window_width) < cursor_position[0] < int(0.98 * window_width) and int(0.7 * window_height) < cursor_position[1] < int(0.8 * window_height):
        return True
    else:
        return False


# testa se o cursor esta sobre o botao de pedir para revelar uma carta
def hover_request_button():
    if int(0.02 * window_width) < cursor_position[0] < int(0.25 * window_width) and int(0.7 * window_height) < cursor_position[1] < int(0.8 * window_height):
        return True
    else:
        return False


# renderiza o botao de ir para o proximo round
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


# renderiza o botao de jogar novamente
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


# renderiza o botao de pedir para revelar um cartao
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


# renderiza o texto de fim de jogo (no caso do usuario 'zerar' o jogo)
def draw_game_over():
    font = pg.font.SysFont('Comic Sans MS', 44)
    text = font.render('Fim de jogo!', True, (0x3C, 0xB0, 0x43))
    screen.blit(text, (int(0.865 * window_width - text.get_width() / 2), int(0.60 * window_height)))


# renderiza as pontuacoes (round atual e total) na tela
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


# testa se a string recebida pelo usuario e igual a resposta correta
def check_answer():
    if input_string == correct_answer:
        return True

    return False


# rotina de input
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


# rotina de calculos
def update():
    global chosen_puzzle, correct_answer, person_img, start_t, current_time, game_status, card_positions, previous_time, counter, remove_card_index, fade_position, check_string, input_string, puzzle_list, total_points, round_points, times_card_button_was_pressed

    if game_status == 'init':
        current_time = 3
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


# rotina de renderizacao grafica
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
        draw_game_over()
        draw_play_again_button()
        draw_points()

    pg.display.flip()


# CHAMADA FUNCOES DE SETUP PREVIO

screen = pg.display.set_mode([window_width, window_height]) # cria a janela com a resolucao escolihda
pg.display.set_caption('Quem é esse Pokémon?')
clock = pg.time.Clock() # cria um objeto de relogio auxiliar
gen_puzzle_list() # cria a lista de puzzles baseado no arquivo answers.txt
card = load_card() # cria o objeto de cartao

while running:
    screen.fill(background_color) # limpa a tela (desenha o background por cima)
    clock.tick(30) # limita a taxa de frames para 30
    input()
    update()
    render()

pg.quit()
