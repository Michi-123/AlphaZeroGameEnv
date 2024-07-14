#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @title SemiSelfPlay

import copy
""" Import libraries Original """
from AlphaZeroCode import SelfPlay

class SemiSelfPlay(SelfPlay):

    def play(self, node, play_count=1, human=1):

        """ 探索の実行 """
        self.util.indicator(play_count)

        if human == 1:
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
            stone = "●" if self.env.player == 1 else "○"
            result = 'Win' if reward == 1 else 'Lose' if reward == -1 else 'Draw'
            print('Done', stone, result)
            # 引き分けは  0
            # 勝った時は +1
            # 負けた時は -1
            v = -reward

        else:
            """ 再帰的に自己対局 """
            v = -self.play(next_node, play_count + 1, -human)

        # debug
        if 0:
            print('Backup-----------')
            show_board(node.states[0]) # このhuman node のn が間違っている.
            # 訪問回数n でpi を求めている
            print('a:',node.action, ' n:',node.n, ' p:', node.p, ' Q:', node.Q, ' v:', v )

        """ 履歴データを追加 """
        self.backup(node, action, v, human)

        """ 符号を反転させて返却 """
        return v

    # オーバーライドしてhumanプレイの場合も対応
    def backup(self, node, action, v, human):
        """ 履歴データの設定 """
        states = copy.deepcopy(node.states)
        input_features = copy.deepcopy(node.input_features).tolist()[0]

        if human == 1:
            pi = [0] * self.env.action_size  # 適切な長さのゼロベクトル
            pi[action] = 1  # 人間の行動に対応するインデックスを1に設定
        else:
            pi = self.util.probability_distribution(node)

        plain = { # for debug
                 'state': states[0],
                 'pi': pi,
                 'z': v,
                 'states': states,
                 'player': node.player,
                 'action': action,
                 }

        """ データセットに経験データを追加 """
        data = []
        data.append(input_features)
        data.append(pi)
        data.append([v])
        data.append(plain)
        self.dataset.append(data)

def show_board(state):
    print()
    for row in state:
        print(row)



