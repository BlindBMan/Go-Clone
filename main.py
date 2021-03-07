import sys
import pygame
import numpy as np
from enum import Enum
import time


pygame.init()

liberties = []
liberties_to_draw = []
checked_stones_draw = []


class Color(Enum):
    EMPTY = 'empty'
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)


score = {
    Color.WHITE: 0,
    Color.BLACK: 0
}


# class Stone:
#     def __init__(self, board, color, group, x, y):
#         self.board = board
#         self.x = x
#         self.y = y
#         self.color = color
#         self.group = group
#         self.liberties = 0
#
#     def calculate_liberties(self):
#         neighbours = [(self.x - 1, self.y), (self.x, self.y - 1), (self.x + 1, self.y), (self.x, self.y + 1)]
#         liberties = 0
#         groups_to_connect = []
#
#         for stone in neighbours:
#             try:
#                 if self.board[stone] == Color.EMPTY:
#                     liberties += 1
#                 elif self.board[stone] == self.color:
#                     groups_to_connect.extend(self.board[stone].group)
#
#             except IndexError:
#                 continue
#
#         groups_to_connect = self.eliminate_duplicates(groups_to_connect)
#
#         for group in groups_to_connect:
#             self.connect_groups(self, group)
#
#     @staticmethod
#     def eliminate_duplicates(stone_list):
#         stones_to_pop = []
#         for i in range(len(stone_list)):
#             for j in range(i, len(stone_list)):
#                 if stone_list[i].group == stone_list[j].group:
#                     stones_to_pop.extend([j])
#         for stone in stones_to_pop:
#             stone_list.pop(stone)
#
#         return stone_list
#
#     @staticmethod
#     def connect_groups(group_a, group_b):
#


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


def draw_liberties(screen, o):
    global liberties_to_draw

    for liberty in liberties_to_draw:
        pygame.draw.circle(screen, (255, 0, 0), ((liberty[1] + 1) * o, (liberty[0] + 1) * o), 5.5)


def draw_checked_stones(screen, o):
    global checked_stones_draw

    for stone in checked_stones_draw:
        pygame.draw.circle(screen, (0, 0, 255), ((stone[1] + 1) * o, (stone[0] + 1) * o), 5.5)


def draw_board(screen, board, board_size, should_draw_liberties, o, w, h):
    global liberties
    draw_lines(screen, board_size, o, w, h)
    draw_coords(screen, board_size, o, w, h)
    draw_interest_points(screen, o)
    draw_stones(screen, board, o)

    if should_draw_liberties:
        draw_liberties(screen, o)


# draws both currently placed stone on click and the preview of the stone
def draw_current_stone(screen, surface, board, is_preview, should_draw_liberties, o, turn, x, y, width, height):
    surface.fill((0, 0, 0, 0))

    if is_preview:
        if not is_out_of_bounds(9, x, y) and board[x, y] == Color.EMPTY:
            screen.fill([221, 174, 105], rect=(0, 0, width, height))
            draw_board(screen, board, 9, should_draw_liberties, o, width, height)
            pygame.draw.circle(surface, turn.value + (100,), ((y + 1) * o, (x + 1) * o), o / 2 - 1)
            screen.blit(surface, (0, 0))
    else:

        if not is_out_of_bounds(9, x, y) and board[x, y] == Color.EMPTY:
            screen.fill([221, 174, 105], rect=(0, 0, width, height))
            board[x, y] = turn
            draw_board(screen, board, 9, should_draw_liberties, o, width, height)
            turn = Color.WHITE if turn == Color.BLACK else Color.BLACK

    return turn


def draw_suicide_move_text(screen, width, height):
    font = pygame.font.SysFont('Comic Sans MS', 25)

    text = font.render(f'Poor stone committed suicide', True, (0, 0, 0))
    text_rect = text.get_rect()
    text_rect.center = (width / 2, height / 2)
    screen.blit(text, text_rect)


def draw_text(screen, text, center, color, font_size):
    font = pygame.font.SysFont('Comic Sans MS', font_size)
    text = font.render(text, True, color)
    text_rect = text.get_rect()
    text_rect.center = (center[0], center[1] - 15)
    screen.blit(text, text_rect)


def draw_players(screen, highlighted_player, size, right_menu_width):
    global score
    local_offset = 70

    screen.fill([46, 44, 56], rect=(size[0], 0, right_menu_width, size[1]))

    black_rect = pygame.Rect([size[0] + local_offset, local_offset, local_offset + 50, local_offset])
    white_rect = pygame.Rect([size[0] + local_offset * 3, local_offset, local_offset + 50, local_offset])
    turn_rect = pygame.Rect([size[0] + local_offset * 2, local_offset * 2.5, local_offset + 50, local_offset / 2])

    # black player
    pygame.draw.rect(screen, (12, 12, 12),
                     black_rect,
                     border_radius=15)
    draw_text(screen, 'Black', (black_rect.centerx, black_rect.centery - 5), (255, 255, 255), 16)
    draw_text(screen, f'{score[Color.BLACK]} captures', (black_rect.centerx, black_rect.centery + 35),
              (255, 255, 255), 16)

    # white player
    pygame.draw.rect(screen, (239, 239, 239),
                     white_rect,
                     border_radius=15)
    draw_text(screen, 'White', (white_rect.centerx, white_rect.centery - 5), (0, 0, 0), 16)
    draw_text(screen, f'{score[Color.WHITE]} captures', (white_rect.centerx, white_rect.centery + 35), (0, 0, 0), 16)

    # turn
    draw_text(screen, f'{highlighted_player.name} to move', turn_rect.center, (255, 255, 255), 20)


def convert_to_board_coords(mouse_coords, o):
    return int(np.floor((mouse_coords[1] + o / 2) / o) - 1), int(np.floor((mouse_coords[0] + o / 2) / o) - 1)


def is_out_of_bounds(board_size, x, y):
    return x < 0 or x > board_size - 1 or y < 0 or y > board_size - 1


def calculate_liberties(board, turn, already_checked, x, y):
    global checked_stones_draw

    # we only look at up, down, left, right neighbours
    neighbours = [(x - 1, y), (x, y - 1), (x + 1, y), (x, y + 1)]
    liberties_lst = []
    already_checked += [(x, y)]
    for stone in neighbours:
        if not is_out_of_bounds(9, *stone):
            if board[stone] == Color.EMPTY and stone not in liberties_lst:
                liberties_lst += [stone]
            elif board[stone] == turn and stone not in already_checked:
                already_checked += [stone]
                checked_stones_draw += [stone]
                curr_liberties_lst, curr_checked = calculate_liberties(board, turn, already_checked, *stone)
                liberties_lst += curr_liberties_lst
                already_checked += curr_checked

    return liberties_lst, already_checked


def check_neighbours(board, turn, x, y):
    """
    :param board: array with board state
    :param turn: Black or White
    :param x: x coord of stone to be played
    :param y: y coord of stone to be played
    :return: True if the move is suicidal, False if not and removes captured stones
    """

    # we need more than one liberty, i.e. liberties >= 2 because the stone to be placed is considered not placed yet
    global liberties, liberties_to_draw, checked_stones_draw
    neigh = [(x - 1, y), (x, y - 1), (x + 1, y), (x, y + 1)]

    already_checked_stones = [(x, y)]
    checked_stones_draw = [(x, y)]
    turn_for_capture = Color.BLACK if turn == Color.WHITE else Color.WHITE

    # check for capture
    captured_something = False
    liberties = []
    liberties_to_draw = []
    for neighbour in neigh:
        if not is_out_of_bounds(9, *neighbour):
            if board[neighbour] == turn_for_capture:
                curr_liberties, curr_checked = \
                    calculate_liberties(board, turn_for_capture, already_checked_stones, *neighbour)
                liberties += curr_liberties
                already_checked_stones += curr_checked
                liberties = list(dict.fromkeys(liberties))
                if (x, y) in liberties:
                    liberties.remove((x, y))
                liberties_to_draw += liberties

                already_checked_stones = list(dict.fromkeys(already_checked_stones))
                if (x, y) in already_checked_stones:
                    already_checked_stones.remove((x, y))

                # remove captured stones
                if len(liberties) == 0:
                    captured_something = True
                    score[turn] += len(already_checked_stones)
                    for stone in already_checked_stones:
                        board[stone] = Color.EMPTY

                liberties = []
                already_checked_stones = []

    # check for suicide
    already_checked_stones = []

    if captured_something is False:
        if not is_out_of_bounds(9, x, y):
            curr_liberties, curr_checked = \
                calculate_liberties(board, turn, already_checked_stones, x, y)
            liberties += curr_liberties
            already_checked_stones += curr_checked
            liberties = list(dict.fromkeys(liberties))
            if (x, y) in liberties:
                liberties.remove((x, y))
            liberties_to_draw += liberties

            # remove captured stones
            if len(liberties) == 0:
                return True
    return False


def main():

    size = 600, 600
    window_size = 1000, 600
    offset = 60
    right_menu_width = window_size[0] - size[0]
    turn = Color.BLACK

    should_draw_liberties = False

    screen = pygame.display.set_mode(window_size)
    surface = pygame.Surface(size, pygame.SRCALPHA)
    pygame.display.set_caption("Sam's Go")
    screen.fill([221, 174, 105], rect=(0, 0, *size))
    screen.fill([46, 44, 56], rect=(size[0], 0, right_menu_width, window_size[1]))

    board = np.full((9, 9), fill_value=Color.EMPTY)
    draw_board(screen, board, 9, should_draw_liberties, offset, *size)

    draw_players(screen, turn, size, right_menu_width)

    while True:
        mouse_pos = pygame.mouse.get_pos()
        x, y = convert_to_board_coords(mouse_pos, offset)
        draw_current_stone(screen, surface, board, True, should_draw_liberties, offset, turn, x, y, *size)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                x, y = convert_to_board_coords(mouse_pos, offset)

                is_suicide = check_neighbours(board, turn, x, y)
                if is_suicide:
                    draw_suicide_move_text(screen, *size)
                    pygame.display.flip()
                    time.sleep(1)
                else:
                    turn = \
                        draw_current_stone(screen,
                                           surface,
                                           board,
                                           False,
                                           should_draw_liberties,
                                           offset,
                                           turn,
                                           x, y,
                                           *size)
                    draw_players(screen, turn, size, right_menu_width)

        pygame.display.flip()


if __name__ == '__main__':
    main()
