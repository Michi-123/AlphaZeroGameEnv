"""# GoGame"""
# @title GoGame

import numpy as np
import copy

# @title __init__
class GoGame:
    def __init__(self, CFG):
        # Board
        self.CFG = CFG
        self.width = CFG.board_width
        self.state = None
        #self.previous_state = None
        self.kou_history = None # Kou
        self.black = -1
        self.white = 1
        self.empty = 0
        # Action
        self.action_size = CFG.board_width * CFG.board_width + 1 # including pass
        self.pass_action = CFG.board_width * CFG.board_width
        # Buffer
        self.buffered_x = None
        self.buffered_y = None
        # Agent
        self.player = None
        self.captured_stones_dict = None
        self.pass_count = 0
        # Return
        self.reward = None
        self.done = None
        # Simulation
        self.simulation = False
        # Reset
        self.reset()

# @title reset
class GoGame(GoGame):
    def reset(self):
        self.state = [[0 for col in range(self.width)] for row in range(self.width)]
        #self.previous_state = self.state.copy()
        self.buffered_x = None
        self.buffered_y = None
        self.captured_stones_dict = {self.black: 0, self.white: 0}
        self.pass_count = 0
        self.kou_history = [[-9 for col in range(self.width)]] * 2 # Kou

        self.player = self.black
        self.reward = 0
        self.done = False

        return self.state

# @title step
class GoGame(GoGame):
    def step(self, a, is_pass=False):

        self.done = False
        self.reward = 0

        if is_pass or a == self.pass_action:
            self.pass_count += 1

            if self.pass_count >= 2:
                # 連続でパス
                self.done = True # 終了
                self.reward = self.count_reward()
            else:
                # 初回のパス
                self.reward = -1
                self.change_turn()

            return self.state, self.reward, self.done

        x, y = (a // self.width), (a % self.width)
        try:
            if not self.is_valid_move(x, y):
                self.reward = -1
                self.done = True # 終了
                return self.state, self.reward, self.done

            if self.is_suicide(x, y):
                self.reward = -1
                self.done = True # 終了
                return self.state, self.reward, self.done

            captured_stones, is_valid_move = self.search(x, y)

            if not is_valid_move:
                self.reward = -1
                self.done = True # 終了
                return self.state, self.reward, self.done

        except Exception as e:
            print('action', a)
            print('x,y', x), y
            raise

        #self.previous_state = self.state.copy()
        if captured_stones > 0:
            self.reward = 1

        self.captured_stones_dict[self.player] += captured_stones
        self.kou_history = [self.kou_history[1], copy.deepcopy(self.state)]
        self.change_turn()
        self.pass_count = 0

        return self.state, self.reward, self.done

# @title change_turn
class GoGame(GoGame):
    def change_turn(self):
        self.player = -self.player

# @title get_legal_actions
class GoGame(GoGame):
    def get_legal_actions(self):
        state = np.array(self.state).reshape(-1)
        return np.where(state == 0)[0]

# @title search
class GoGame(GoGame):
    def search(self, x, y):
        """
        指定された座標 (x, y) に石を置き、相手の石が取れるかどうかを確認し、
        取れる場合はその石を取り除く。
        :return: 取れた石の数、自殺点ではないかのブール値
        """
        # 取れた石の数
        captured_stones = 0

        board = copy.deepcopy(self.state)

        # 一時的に石を置く
        board[x][y] = self.player

        # 相手の石の種類
        opponent_stone = self.black if self.player == self.white else self.white

        # 隣接する相手の石のグループをチェック
        size = self.width
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < size and 0 <= ny < size and board[nx][ny] == opponent_stone:
                group, liberties = self.get_group(board, nx, ny)
                if liberties == 0:
                    # 相手の石のグループを取り除く
                    for gx, gy in group:
                        board[gx][gy] = 0
                    captured_stones += len(group)

        # 自分の石のグループを取得して自由度を確認
        _, liberties = self.get_group(board, x, y)

        # 自殺点の判定
        # if (liberties == 0 and captured_stones == 0) or self.is_kou(board):
        if (liberties == 0 ) or self.is_kou(board):

            # 自殺点の場合、石を元に戻す
            is_valid_move = False
            captured_stones = 0
        else:
            is_valid_move = True
            self.state = copy.deepcopy(board)  # 更新

        return captured_stones, is_valid_move

# @title is_kou
class GoGame(GoGame):
    def is_kou(self, board):
        if self.kou_history[0] == board:
            print('Kou------')
            print('state',board)
            print('history 0',self.kou_history[0])
            print('history 1',self.kou_history[1])
            print('Kou------')
            return True
        return False

# @title get_group
class GoGame(GoGame):
    def get_group(self, board, x, y):
        """
        座標 (x, y) から始まる石のグループとその自由度を取得する。

        :param board: 盤面を表す2次元リスト
        :param x: 盤上の x 座標
        :param y: 盤上の y 座標
        :return: グループの座標リストと自由度（隣接する空き交点の数）を含むタプル (group, liberties)
        """
        visited = set()  # 訪問済みの座標を記録するセット（重複訪問を防ぐため）
        stack = [(x, y)]  # 深さ優先探索（DFS）のためのスタック、初期位置として (x, y) を設定
        group = []  # 石のグループを記録するリスト
        liberties = 0  # 自由度（隣接する空き交点の数）をカウントする変数

        while stack:
            # スタックから現在の座標を取得
            cx, cy = stack.pop()

            # 現在の座標が既に訪問済みの場合、次のループへ
            if (cx, cy) in visited:
                continue

            # 現在の座標を訪問済みとしてマーク
            visited.add((cx, cy))
            # 現在の座標をグループに追加
            group.append((cx, cy))

            # 上下左右の隣接座標をチェック
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = cx + dx, cy + dy

                # 隣接座標が盤面内かどうかを確認
                if 0 <= nx < len(board) and 0 <= ny < len(board[0]):
                    # 隣接座標が空き（0）の場合、自由度を1増やす
                    if board[nx][ny] == 0:
                        liberties += 1
                    # 隣接座標が同じ色の石の場合、スタックに追加
                    elif board[nx][ny] == board[cx][cy]:
                        stack.append((nx, ny))

        # 石のグループと自由度を返す
        return group, liberties

# @title count_territory
class GoGame(GoGame):
    def count_territory(self, stone):
        """
        Count the territory controlled by the specified stone (black or white) on a Go board.

        :param board: 2D list representing the Go board (0: empty, 1: black, 2: white)
        :param stone: Integer representing the stone type to count the territory for (1: black, 2: white)
        :return: Integer count of the territory controlled by the specified stone
        """
        def dfs(board, x, y, visited):

            if x < 0 or y < 0 or x >= len(board) or y >= len(board[0]) or visited[x][y]:
                return 0, True
            if board[x][y] == stone:
                return 0, True
            if board[x][y] != 0:
                return 0, False

            visited[x][y] = True
            count = 1
            is_territory = True

            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                cnt, territory = dfs(board, x + dx, y + dy, visited)
                count += cnt
                is_territory = is_territory and territory

            return count, is_territory

        board = self.state

        total_territory = 0
        visited = [[False] * len(board[0]) for _ in range(len(board))]

        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[i][j] == 0 and not visited[i][j]:
                    count, is_territory = dfs(board, i, j, visited)
                    if is_territory:
                        total_territory += count

        return total_territory

# @title show_board
class GoGame(GoGame):
    def show_board(self):

        # アルファベット
        print("    ", end="")
        for i in range(ord('A'), ord('A') + self.width):
            print(f"{chr(i)}", end="  ")
        print()

        # 列のインデックスを表示
        print("    ", end="")
        for i in range(self.width):
            axis = str(i).zfill(2)
            print(f"{str(i).zfill(2)} ", end="")
        print()

        # 盤面
        for i in range(len(self.state)):
            print(str(i).zfill(2), end='  ')
            for j in range(len(self.state[0])):
                if self.state[i][j] == 0:
                    print('__', end=' ')
                elif self.state[i][j] == -1:
                    print('○', end=' ')
                else:
                    print('●', end=' ')
            print()

# @title count_reward
class GoGame(GoGame):
    def count_reward(self):
        # count Winner
        black_territory = self.count_territory(self.CFG.black)
        white_territory = self.count_territory(self.CFG.white)

        if 0: # not self.simulation:
            print('black', black_territory, '  white', white_territory)
            print(self.captured_stones_dict)

        black_captured_stones = env.captured_stones_dict[CFG.black]
        white_captured_stones = env.captured_stones_dict[CFG.white]

        black = black_territory + black_captured_stones
        white = white_territory + white_captured_stones

        if white < black:
            if self.player == self.CFG.black:
                return 1
            else:
                return -1
        elif black < white:
            if self.player == self.CFG.white:
                return 1
            else:
                return -1
        else:
            return 0

# @title is_valid_move
class GoGame(GoGame):
    def is_valid_move(self, x, y):
        if self.state[x][y] != self.empty:
            return False
        self.state[x][y] = self.player
        if self.has_liberties(x, y):
            self.state[x][y] = self.empty
            return True
        self.state[x][y] = self.empty
        return False

    def is_suicide(self, x, y):
        self.state[x][y] = self.player
        if not self.has_liberties(x, y):
            self.state[x][y] = self.empty
            return True
        self.state[x][y] = self.empty
        return False

    def has_liberties(self, x, y):
        visited = set()
        return self.check_liberties(x, y, visited)

    def check_liberties(self, x, y, visited):
        if (x, y) in visited:
            return False
        visited.add((x, y))
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.width:
                if self.state[nx][ny] == self.empty:
                    return True
                if self.state[nx][ny] == self.player and self.check_liberties(nx, ny, visited):
                    return True
        return False

# @title has_good_moves
class GoGame(GoGame):
    def has_good_moves(self):
        for x in range(self.width):
            for y in range(self.width):
                if self.state[x][y] == self.empty:
                    if self.is_valid_move(x, y) and not self.is_suicide(x, y):
                        return True
        return False
