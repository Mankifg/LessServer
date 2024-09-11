import game_utils


def convert_to_url(b10_board, lbp, base_url):
    b10_board_list = list(map(str, b10_board))
    b10_board_list = ",".join(b10_board_list)
    return base_url + f"/image?nums={b10_board_list}&lbp={lbp}"


def is_valid_cords(x: int, y: int, max_x=5, max_y=5) -> bool:
    return (x >= 0 and x <= max_x) and (y >= 0 and y <= max_y)


def what_is_here(board, x, y):
    return board[y][x]


def blockiy_positon(lbp):
    for i in range(2, 10):
        lbp = lbp.replace(str(i), "0" * i)

    lbp = lbp.split("/")

    # w white, b black, 0 empty

    arry = []
    for x in range(0, int(len(lbp)), 2):
        a2 = []

        upper_row = lbp[x]
        lower_row = lbp[x + 1]

        len_row = len(upper_row)

        for y in range(0, len_row, 2):

            block = [[upper_row[y], upper_row[y + 1]], [lower_row[y], lower_row[y + 1]]]
            lbp[x] = lbp[x][:-2]
            lbp[x + 1] = lbp[x + 1][:-2]

            a2.append(block)
        arry.append(a2)
    return arry


def boardify(lbp):
    for i in range(1, 10):
        lbp = lbp.replace(str(i), "0" * i)
    lbp = lbp.split("/")
    for i in range(len(lbp)):
        lbp[i] = list(lbp[i])
    return lbp


def reverse(ar2d):
    for i in range(len(ar2d)):
        ar2d[i] = "".join(ar2d[i])

    # print(ar2d)
    lbp = "/".join(ar2d)

    for i in range(10, 1, -1):
        lbp = lbp.replace("0" * i, str(i))

    return lbp


def convert_to_binary_len12(dec: int) -> str:
    b = bin(dec)
    b = str(b)[2::]
    added_0 = (12 - len(b)) * "0"
    b = added_0 + b
    return b


"""def filter_moves_out_of_bound(arry_of_moves):
    new_moves = []
    for move in arry_of_moves:
        #move = [x1, y1,x2, y2]

        m1,m2 = move
        print(m1,m2)
        if is_valid_cords(m1[0], m1[1]) and is_valid_cords(m2[0], m2[1]):
            new_moves.append(move)

    return new_moves"""


def moves_in_tile(x, y):
    # print("running",x,y)
    offsets = [
        # 1. row
        [0, -1, 0, 0],
        [1, -1, 1, 0],
        # 2.
        [-1, 0, 0, 0],
        [0, 0, 1, 0],
        [1, 0, 2, 0],
        # 3.
        [0, 0, 0, 1],
        [1, 0, 1, 1],
        # 4.
        [-1, 1, 0, 1],
        [0, 1, 1, 1],
        [1, 1, 2, 1],
        # 5.
        [0, 1, 0, 2],
        [1, 1, 1, 2],
    ]

    returning_offsets = offsets[:]
    for i in range(len(returning_offsets)):

        returning_offsets[i][0] += x
        returning_offsets[i][2] += x

        returning_offsets[i][1] += y
        returning_offsets[i][3] += y
        """for z in range(len(returning_offsets[i][j])):
                if z % 2 == 0: # x
                    returning_offsets[i][j][z] = returning_offsets[i][j][z] + x
                else:
                    returning_offsets[i][j][z] = returning_offsets[i][j][z] + y """
    return returning_offsets


def moves_that_cost_in_tile(arry_of_corrds, b10_num):
    binary_num = convert_to_binary_len12(b10_num)

    good_connections = []

    for i in range(len(arry_of_corrds)):
        current_bin = binary_num[i]
        current_connections = arry_of_corrds[i]
        if int(current_bin) == 1:
            good_connections.append(current_connections)

    return good_connections


"""def every_absolute_moves():
    moves = []
    for x in range(0,6,2):
        for y in range(0,6,2):
            ot_moves = moves_in_tile(x,y)  # one tile move
            filter_out_of_boud = filter_moves_out_of_bound(ot_moves)
            moves = moves + filter_out_of_boud

    return moves"""


"""def moves_that_cost_all(arry_of_nums):
    all_moves = []

    for i in range(len(arry_of_nums)):
        b10_num = arry_of_nums[i]
        # ? b10_num = num given in main

        x = int(i / 3)
        y = int(i % 3)

        moves = moves_in_tile(x, y)
        moves = moves_that_cost_in_tile(moves, b10_num)

        all_moves = all_moves + moves

    return all_moves
"""


def start_end_flip(moves: list) -> list:
    # [x,y,a,b] -> [a,b,x,y]
    return [moves[2], moves[3], moves[0], moves[1]]


def get_wall_moves(b10_board):
    normal_wall_moves = []

    for i in range(len(b10_board)):
        # print("H"*10,i)
        b10_num = b10_board[i]
        # ? b10_num = num given in main

        y = int(i / 3) * 2
        x = int(i % 3) * 2

        all_moves_in_tile = moves_in_tile(x, y)
        # print(len(all_moves_in_tile),all_moves_in_tile)
        moves = moves_that_cost_in_tile(all_moves_in_tile, b10_num)
        # print(len(moves),moves)

        normal_wall_moves = normal_wall_moves + moves

    # print(f"{normal_wall_moves=}")
    # print(len(normal_wall_moves))

    walls = []

    for i in range(len(normal_wall_moves)):
        w = normal_wall_moves[i]
        walls.append([w, 1])

        """if not ([w, 1] in walls or [start_end_flip(w), 1] in w):
            walls.append([w, 1])
        else:
            walls.remove([w, 1])
            walls.append([w, 2])"""

    # print("."*10)
    # print(walls)
    # print(len(walls))

    new_moves = []
    for move, value in walls:

        if is_valid_cords(move[0], move[1]) and is_valid_cords(move[2], move[3]):
            new_moves.append([move, value])

    # print(f"Wall moves: {len(new_moves)}")#,{new_moves}")

    walls = []

    for i in range(len(new_moves)):
        c = new_moves[i][0]
        if [c, 1] in walls:
            # print(1)
            walls.remove([c, 1])
            walls.append([c, 2])

        elif [start_end_flip(c), 1] in walls:
            # print(1)
            walls.remove([start_end_flip(c), 1])
            walls.append([start_end_flip(c), 2])
        else:

            walls.append([c, 1])

    return walls


def every_one_step_move(x: int, y: int):
    """every move from x,y
    Args:
        x (int): x
        y (int): y
    Returns:
        list [ [x,y,nx,ny],... ]:
    """
    moves = []
    stor = [[-1, 0], [1, 0], [0, -1], [0, 1]]
    for dx, dy in stor:
        nx = x + dx
        ny = y + dy

        if is_valid_cords(nx, ny):
            moves.append([x, y, nx, ny])

    return moves


def filter_double_moves_from(board, b10_board, x, y):
    # print("seartch ard",x,y)
    wall_moves = get_wall_moves(b10_board)

    double_step = []

    double_offsets = [
        [-2, 0],
        [2, 0],
        [0, -2],
        [0, 2],
    ]
    where_is_piece = [
        [-1, 0],
        [1, 0],
        [0, -1],
        [0, 1],
    ]

    for i in range(len(double_offsets)):
        dx, dy = double_offsets[i]

        nx = x + dx
        ny = y + dy

        # normal filter out of bound
        if not is_valid_cords(nx, ny):
            continue

        # jump only if piece
        piece_dx, piece_dy = where_is_piece[i]

        piece_dx, piece_dy = x + piece_dx, y + piece_dy

        piece = what_is_here(board, piece_dx, piece_dy)
        if not (piece in ["w", "b"]):
            continue

        # check for wall
        checking_moves = [
            [x, y, piece_dx, piece_dy],
            [piece_dx, piece_dy, x, y],
            [piece_dx, piece_dy, nx, ny],
            [nx, ny, piece_dx, piece_dy],
        ]

        only_walls = [el[0] for el in wall_moves]

        isGood = True
        for cm in checking_moves:  # check move
            if cm in only_walls:
                isGood = False

        if isGood:
            double_step.append([x, y, nx, ny])

    return double_step


def filter_one_step_moves(board, b10_board, x, y):
    # wall_moves = get_wall_moves(b10_board)
    one_step = every_one_step_move(x, y)

    moves = []
    # print("move handle 1 step")
    for move in one_step:
        m1, m2 = move[0:2], move[2:4]

        # cant be same / just in case
        if m1 == m2:
            continue

        # is empty
        piece = what_is_here(board, m2[0], m2[1])
        # print(piece,m1)
        if piece in ["b", "w"]:  # if NOT empty
            continue

        moves.append(move)
    return moves


def legal_moves_from_xy(board, b10_board, x, y):
    # print("#" * 10)
    all_moves = []

    one_step = filter_one_step_moves(board, b10_board, x, y)

    double_step = filter_double_moves_from(board, b10_board, x, y)

    # print(f"single step {x},{y}",one_step)
    # print(f"double step {x},{y}",double_step)

    all_moves = one_step + double_step

    return all_moves


def all_cords_that_match(board, piece):
    cords = []

    for y in range(len(board)):
        for x in range(len(board[y])):
            if board[y][x] == piece:
                cords.append([x, y])

    return cords


def legal_moves_for_color(lbp, b10_board, color):
    board = boardify(lbp)
    legal_moves = []
    cords = all_cords_that_match(board, color)

    for cord in cords:
        legal = legal_moves_from_xy(board, b10_board, cord[0], cord[1])
        legal_moves += legal

    return legal_moves


def singe_move_cost(walls, move):
    for m, cost in walls:
        # print(m,cost)
        if m == move or start_end_flip(m) == move:
            return cost
    return 0


def exatct(walls, move):
    for m, cost in walls:
        # print(m,cost)
        if m == move:  # or start_end_flip(m) == move:
            return cost
    return 0


def cost_of_moves(current_pos, b10_board, color):
    moves = legal_moves_for_color(current_pos, b10_board, color)
    print("-- legal")
    for m in moves:
        print(game_utils.from_arry_notation(m))
    print("-- end")

    wall_moves = get_wall_moves(b10_board)
    cost_moves = []

    for move in moves:
        c = singe_move_cost(wall_moves, move)
        cost_moves.append([move, c + 1])

    return cost_moves


def push_move(lbp, ary_move):
    b = boardify(lbp)
    x1, y1, x2, y2 = ary_move

    save = b[y1][x1]
    b[y1][x1] = "0"
    b[y2][x2] = save

    new_lbp = reverse(b)
    print(f"{game_utils.from_arry_notation(ary_move)}: {lbp} -> {new_lbp}")
    return new_lbp
