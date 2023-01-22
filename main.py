import copy
import argparse

# 画像から問題読み取り -> 外部APIがよさそう？
def recognize_sudoku_pazzle(input_filename):
    # input_file = __9_3__2_
    #              4___68___
    #              _8_2_____
    #              615______
    #              __7__5__8
    #              ___7___63
    #              _2_3___8_
    #              ___187_36
    #              __6___4__
    # input_lines = [[0, 0, 9, 0, 3, 0, 0, 2, 0],
    #                [4, 0, 0, 0, 6, 8, 0, 0, 0],
    #                [0, 8, 0, 2, 0, 0, 0, 0, 0],
    #                [6, 1, 5, 0, 0, 0, 0, 0, 0],
    #                [0, 0, 7, 0, 0, 5, 0, 0, 8],
    #                [0, 0, 0, 7, 0, 0, 0, 6, 3],
    #                [0, 2, 0, 3, 0, 0, 0, 8, 0],
    #                [0, 0, 0, 1, 8, 7, 0, 3, 6],
    #                [0, 0, 6, 0, 0, 0, 4, 0, 0]]

    with open (input_filename, 'r') as f:
        input_lines = f.readlines()
    
    input_lines = [list(input.replace('_', '0').replace('\n', '')) for input in input_lines]
    input_lines = [[int(input) for input in lines] for lines in input_lines]

    return input_lines


def reflect_fixed_to_possible(current, possible):
    # TODO: リスト内包表記とかに書き換える
    for i, current_row in enumerate(current):
        for j, current_value in enumerate(current_row):
            if current_value != 0:
                possible[i][j] = [current_value]

    return possible


def check_which_range(target):
    if target <= 2:
        target_range = range(0, 3)
    elif target <= 5:
        target_range = range(3, 6)
    else:
        target_range = range(6, 9)
    
    return target_range  


def relfect_possible_to_fixed(current, possible):
    # TODO: リスト内包表記とかに書き換える
    for i, possible_row in enumerate(possible):
        for j, possible_value in enumerate(possible_row):
            if len(possible_value) == 1 and current[i][j] == 0:
                current[i][j] = possible_value[0]

    return current


def remove_number_in_row(column, value, possible):
    # possibleの同じrowの各候補からvalueをremove
    # TODO: リスト内包表記とかに書き換える
    for i in range(0, 9): 
        if len(possible[column][i]) > 1 and value in possible[column][i]:
            possible[column][i].remove(value)
    return possible


def remove_number_in_column(row, value, possible):
    # possibleの同じcolumnの各候補からvalueをremove
    # TODO: リスト内包表記とかに書き換える
    for i in range(0, 9): 
        if len(possible[i][row]) > 1 and value in possible[i][row]:
            possible[i][row].remove(value)
    return possible


def remove_number_in_square(column, row, value, possible):
    column_range = check_which_range(column)
    row_range = check_which_range(row)

    for i in column_range:
        for j in row_range:
            if len(possible[i][j]) > 1 and value in possible[i][j]:
                possible[i][j].remove(value)

    return possible


def scan_possible_number(current, possible):
    for i, current_row in enumerate(current):
        for j, current_value in enumerate(current_row):
            if current_value != 0:
                possible = remove_number_in_row(i, current_value, possible)
                possible = remove_number_in_column(j, current_value, possible)
                possible = remove_number_in_square(i, j, current_value, possible)
    return possible


def fix_no_other_number_in_row(column, current, possible):
    # rowのpossibleの中で1つしか出てこない数字を確定させる
    # TODO: リスト内包表記とかに書き換える
    targets = list(range(1, 10))
    for curr in current[column]:
        if curr != 0:
            targets.remove(curr)

    row_flatten = sum(possible[column], [])
    unique_numbers = []

    # column全体 = row_flattenの中にtargetが1つならunique_numbersにピックアップ
    # possible[column]からunique_numbersにある数字を見つけたら候補をそれだけにする
    for target in targets:
        if row_flatten.count(target) == 1:
            unique_numbers.append(target)
    
    for i, possible_arr in enumerate(possible[column]):
        for unique_num in unique_numbers:
            if unique_num in possible_arr:
                possible[column][i] = [unique_num]

    return possible


def fix_no_other_number_in_column(row, current, possible):
    # columnのpossibleの中で1つしか出てこない数字を確定させる
    # TODO: リスト内包表記とかに書き換える
    targets = list(range(1, 10))
    possible_column = []
    for i in range(0, 9):
        possible_column.append(possible[i][row])
        focus = current[i][row]
        if focus != 0:
            targets.remove(focus)

    column_flatten = sum(possible_column, [])
    unique_numbers = []

    for target in targets:
        if column_flatten.count(target) == 1:
            unique_numbers.append(target)
    
    for i, possible_arr in enumerate(possible):
        for unique_num in unique_numbers:
            if unique_num in possible_arr[row]:
                possible[i][row] = [unique_num]
    
    return possible


def fix_no_other_number_in_square(column, row, current, possible):
    # 3*3のpossibleの中で1つしか出てこない数字を確定させる
    column_range = []
    row_range = []
    if column == 0 or column == 3 or column == 6:
        column_range = check_which_range(column)
    if row == 0 or row == 3 or row == 6:
        row_range = check_which_range(row)

    # 3*3で1回やればいいので枝刈り
    # TODO: 枝刈りのタイミングほんとにここでOK?
    if len(column_range) == 3 and len(row_range) == 3:
        pass
    else:
        return possible

    targets = list(range(1, 10))
    possible_square = []
    for i in column_range:
        for j in row_range:
            possible_square.append(possible[i][j])
            focus = current[i][j]
            if focus != 0:
                targets.remove(focus)

    column_flatten = sum(possible_square, [])
    unique_numbers = []

    for target in targets:
        if column_flatten.count(target) == 1:
            unique_numbers.append(target)
    
    for i in column_range:
        for j in row_range:
            for unique_num in unique_numbers:
                if unique_num in possible[i][j]:
                    possible[i][j] = [unique_num]

    return possible


def scan_no_other_number(current, possible):
    for i, current_row in enumerate(current):
        for j, current_value in enumerate(current_row):
            if current_value != 0:
                possible = fix_no_other_number_in_row(i, current, possible)
                possible = fix_no_other_number_in_column(j, current, possible)
                possible = fix_no_other_number_in_square(i, j, current, possible)
    return possible


# 数独を解く
def solve_sudoku(init_board, possible_board):
    # 数独を解く基本方針：深さ優先探索 + 枝刈り
    current_board = init_board
    prev_board = []
    while True:
        # 1. 最初に入っている数字を埋める
        prev_board = copy.deepcopy(current_board)
        possible_board = reflect_fixed_to_possible(current_board, possible_board)

        # 2. 空いているマスに対して入れられる数字の候補を出し、候補が1つのマスを確定させる
        #   - 入れられない条件：3*3、縦列、横列に同じ数字がある
        possible_board = scan_possible_number(current_board, possible_board) 
        current_board = relfect_possible_to_fixed(current_board, possible_board)

        # 4. 3*3、縦列、横列で既にそのマス以外の候補がない数字を確定させる
        possible_board = scan_no_other_number(current_board, possible_board)
        current_board = relfect_possible_to_fixed(current_board, possible_board)
        
        # 一通りやって前の週と結果が変わらな（= この方法では盤面が進まない）ければ次の手だてに移る
        if current_board == prev_board:
            break
    
    print(possible_board)
    
    # TODO: 5. 場合分けして探索
    #   - このタイミングでresultが確定していない場合、
    #   - 数字の候補が一番少ない（2以上）のマスのうち1つを仮置き
    #   - 2. の方法で確定マスを埋める
    #   - 継続 or 次に移動の判定
    #     - conflictしていれば仮定が間違いなので、仮置きした数字を候補から消す
    #     - conflictしておらず全てのマスが確定していれば、それが正解 -> 解としてoutput
    #     - conflictしておらず全てのマスが確定していなければ、今の仮定はそのままにして別の数字を仮置き -> 3.を再帰呼び出し？
    
    result = current_board

    return result

# 各マスの数字の候補を扱うarrayを初期化
def init_possible_board():
    init_state = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    # possible_board = np.full((9, 9, 9), init_state)
    possible_board = [[list(range(1, 10)) for i in range(9)] for j in range(9)] 
    
    return possible_board


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_txt', help='Text file with 9 lines of Sudoku puzzles.')
    args = parser.parse_args()
    input_filename = args.input_txt

    init_board = recognize_sudoku_pazzle(input_filename)
    print(init_board)
    possible_board = init_possible_board()
    
    result = solve_sudoku(init_board, possible_board)
    print(result)
    # いい感じに表示 -> 表示はアプリに任せる？
