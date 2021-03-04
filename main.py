import sys
import pygame
import numpy as np
from enum import Enum

pygame.init()


class Color(Enum):
    EMPTY = 'empty'
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)


def draw_lines(screen, board_size, offset, w, h):
    for i in range(1, board_size + 1):
        # draws horizontal lines
        pygame.draw.line(screen, (0, 0, 0), start_pos=(offset, offset * i), end_pos=(w - offset, offset * i))

        # draws vertical lines
        pygame.draw.line(screen, (0, 0, 0), start_pos=(offset * i, offset), end_pos=(offset * i, h - offset))


def draw_coords(screen, board_size, o, w, h):
    letters = 'ABCDEFGHJ'
    numbers = '123456789'[::-1]

    font = pygame.font.SysFont('Comic Sans MS', 15)
    for i in range(1, board_size + 1):

        # drawing vertical letters up/down
        text = font.render(letters[i - 1], True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (o * i, o / 3)
        screen.blit(text, text_rect)

        text_rect.center = (o * i, h - o / 3)
        screen.blit(text, text_rect)

        # drawing horizontal numbers left/right
        number = font.render(numbers[i - 1], True, (0, 0, 0))
        number_rect = number.get_rect()
        number_rect.center = (o / 3, o * i)
        screen.blit(number, number_rect)

        number_rect.center = (w - o / 3, o * i)
        screen.blit(number, number_rect)


def draw_interest_points(screen, o):
    circle_centers = [(3, 3), (7, 3), (5, 5), (3, 7), (7, 7)]

    for center in circle_centers:
        pygame.draw.circle(screen, (0, 0, 0), (center[0] * o, center[1] * o), 5.5)


def draw_stones(screen, board, o):
    for i in range(board.shape[0]):
        for j in range(board.shape[1]):
            if board[i, j] != Color.EMPTY:
                pygame.draw.circle(screen, board[i, j].value, ((j + 1) * o,  (i + 1) * o), o / 2 - 1)


def draw_board(screen, board, board_size, o, w, h):
    draw_lines(screen, board_size, o, w, h)
    draw_coords(screen, board_size, o, w, h)
    draw_interest_points(screen, o)
    draw_stones(screen, board, o)


# draws both currently placed stone on click and the preview of the stone
def draw_current_stone(screen, surface, board, is_preview, o, turn, x, y, width, height):
    surface.fill((0, 0, 0, 0))

    if is_preview:
        if not (x < 0 or x > 8 or y < 0 or y > 8) and board[x, y] == Color.EMPTY:
            screen.fill([221, 174, 105])
            draw_board(screen, board, 9, o, width, height)
            pygame.draw.circle(surface, turn.value + (100,), ((y + 1) * o, (x + 1) * o), o / 2 - 1)
            screen.blit(surface, (0, 0))
    else:
        if not (x < 0 or x > 8 or y < 0 or y > 8) and board[x, y] == Color.EMPTY:
            screen.fill([221, 174, 105])
            board[x, y] = turn
            draw_board(screen, board, 9, o, width, height)
            turn = Color.WHITE if turn == Color.BLACK else Color.BLACK
    return turn


def convert_to_board_coords(mouse_coords, o):
    return int(np.floor((mouse_coords[1] + o / 2) / o) - 1), int(np.floor((mouse_coords[0] + o / 2) / o) - 1)


def calculate_liberties(board, x, y):
    # we only look at up, down, left, right neighbours
    neighbours = [(x - 1, y), (x, y - 1), (x + 1, y), (x, y + 1)]
    liberties = 0
    for stone in neighbours:
        try:
            if board[stone] == Color.EMPTY:
                liberties += 1
        except IndexError:
            continue


def check_dead_stones(board, turn, x, y):
    # we need more than one liberty, i.e. liberties >= 2 because the stone to be placed is considered not placed yet

    already_checked_stones = [(x, y)]
    already_checked_liberties = []


def main():

    size = width, height = 600, 600
    offset = 60

    screen = pygame.display.set_mode(size)
    surface = pygame.Surface(size, pygame.SRCALPHA)
    pygame.display.set_caption("Sam's Go")
    screen.fill([221, 174, 105])

    board = np.full((9, 9), fill_value=Color.EMPTY)
    draw_board(screen, board, 9, offset, *size)

    turn = Color.BLACK

    while True:
        mouse_pos = pygame.mouse.get_pos()
        x, y = convert_to_board_coords(mouse_pos, offset)
        draw_current_stone(screen, surface, board, True, offset, turn, x, y, *size)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                x, y = convert_to_board_coords(mouse_pos, offset)

                calculate_liberties(board, x, y)
                turn = draw_current_stone(screen, surface, board, False, offset, turn, x, y, *size)

        pygame.display.flip()


if __name__ == '__main__':
    main()
