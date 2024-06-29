# @title SimpleGame
class SimpleGame:
    def __init__(self, CFG):
        self.width = CFG.board_width
        self.state = None
        self.action_size = CFG.action_size
        self.player = None
        self.reward = None
        self.done = None
        self.reset()

    def reset(self):
        self.state = [[0 for col in range(self.width)] for row in range(self.width)]
        self.player = -1
        self.reward = 0
        self.done = False
        return self.state

    def show_board(self):
        for row in self.state:
            print(row)

    def step(self, a, is_pass=False):

        self.done = False
        self.reward = 0

        x, y = (a // self.width), (a % self.width)

        if is_pass:
            self.done = True
            self.reward = -1

        elif  self.state[x][y] != 0:
            self.done = True
            self.reward = -1

        self.state[x][y] = self.player
        self.player = -self.player

        return self.state, self.reward, self.done

    def get_legal_actions(self):
        state = np.array(self.state).reshape(-1)
        return np.where(state == 0)[0]
