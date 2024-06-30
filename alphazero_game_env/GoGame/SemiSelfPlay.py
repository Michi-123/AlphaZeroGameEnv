#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @title SemiSelfPlay

import copy
from tqdm import tqdm
""" Import libraries Original """
from AlphaZeroCode import SelfPlay

class SemiSelfPlay(SelfPlay):

    def play(self, node, play_count=1, human=1):

        """ 探索の実行 """
        self.util.indicator(play_count)

        if human==1:
            env = copy.deepcopy(self.env)
            next_node = self.go_agent.human(node, env) #fix
        else:
            """ AlphaZero player """
            next_node = self.go_agent.alpha_zero(node, play_count) #fix

        action = next_node.action #fix

        """ ゲームの実行 """
        _next_state, reward, done = self.env.step(action)

        self.env.show_board()

        if done:
            stone =  "●" if self.env.player == 1 else "○"
            win_lose = 'win' if reward == 1 else 'lose' if reward == -1 else 'draw'
            print('Done', stone, win_lose)
            # 引き分けは  0
            # 勝った時は +1
            # 負けた時は -1
            v = -reward

        else:
            """ 再帰的に自己対局 """
            v = -self.play(next_node, play_count + 1, -human)

        """ 履歴データを追加 """
        if 0: # debug
            print('Backup-----------')
            show_board(node.states[0]) # このhuman node のn が間違っている.
            # 訪問回数n でpi を求めている
            print('a',node.action, 'n',node.n, 'p', node.p, 'Q', node.Q, 'v', v )

        self.backup(node, action, v) #

        """ 符号を反転させて返却 """
        return v

def show_board(state):
    print()
    for row in state:
        print(row)
