#!/usr/bin/env python3

from random import randint
from typing import List, Optional, Tuple

from safehouse.events import sdk as events_sdk


events = events_sdk.init(origin='game')
game_id = randint(0, 1000000)


class Board:
    def __init__(self):
        self.rows = [
            [' ', ' ', ' '],
            [' ', ' ', ' '],
            [' ', ' ', ' '],
        ]

    def __str__(self):
        s = '-------\n'
        for row in self.rows:
            s += self.render(row)
            s += '-------\n'
        return s

    @property
    def empty_spaces(self) -> List[Tuple[int,int]]:
        empty_spaces = []
        for row in range(0, 3):
            for col in range( 0, 3):
                if self.rows[row][col] == ' ':
                    empty_spaces.append([row, col])
        return empty_spaces
    
    @property
    def is_finished(self) -> bool:
        return self.winner or len(self.empty_spaces) == 0

    def computer_move(self):
        choices = self.empty_spaces
        num_choices = len(choices)
        if num_choices == 0:
            raise Exception("no choices left")
        choice = choices[randint(0, num_choices-1)]
        self.move('o', choice[1], choice[0])

    def get_player_move(self) -> Tuple[int, int]:
        print("Choose a square using (row,column) coordinates (upper left is 1,1)")
        choice = input()
        tokens = choice.split(',')
        if len(tokens) != 2:
            raise Exception(f"invalid move '{choice}', should be of the form <x>,<y>")
        x = int(tokens[0]) -1
        y = int(tokens[1]) -1
        return x, y

    def move(self, side: str, column: int, row: int) -> Tuple[bool, Optional[str]]:
        if column < 0 or column > 3:
            return False, f"column {column} is out of range"
        if row < 0 or row > 3:
            return False, f"row {row} is out of range"
        if self.rows[row][column] != ' ':
            return False, "already occupied"
        self.rows[row][column] = side
        events.move.send(game_id=game_id, side=side, row=row, column=column)
        return True, None

    def play(self):
        events.game_start.send(game_id=game_id, side='x')
        while not self.is_finished:
            print(self)
            try:
                x, y = self.get_player_move()
            except Exception as e:
                print(f"OOPS: {e}")
                continue
            success, message = self.player_move(y, x)
            if not success:
                print(f"OOPS: {message}")
                continue
            if not self.is_finished:
                self.computer_move()
            winner = self.winner
            if winner:
                print(f"{winner}'s won!!")
                break

    def player_move(self, column: int, row: int) -> Tuple[bool, Optional[str]]:
        return self.move('x', column, row)
        
    def render(self, row):
        return f"|{row[0]}|{row[1]}|{row[2]}|\n"

    @property
    def winner(self) -> str:
        for winning_set in (
            ((0, 0), (0, 1), (0, 2)), # top row
            ((1, 0), (1, 1), (1, 2)), # middle row
            ((2, 0), (2, 1), (2, 2)), # bottom row
            ((0, 0), (1, 0), (2, 0)), # left column
            ((0, 1), (1, 1), (2, 1)), # middle column
            ((0, 2), (1, 2), (2, 2)), # right column
            ((0, 0), (1, 1), (2, 2)), # diagonal left->right
            ((0, 2), (1, 1), (2, 0)), # diagonal right->left
        ):
            x_count = 0
            y_count = 0
            for position in winning_set:
                owner = self.rows[position[0]][position[1]]
                if owner == 'x':
                    x_count += 1
                elif owner == 'y':
                    y_count += 1
            if x_count == 3:
                return 'x'
            if y_count == 3:
                return 'y'
        return ''


def run():
    try:
        board = Board()
        board.play()
        print(board)
        events.game_end.send(game_id=game_id, result='completed', winner=board.winner)
    except Exception as e:
        events.game_end.send(game_id=game_id, result='aborted', winner='none')

if __name__ == "__main__":
    run()
    
