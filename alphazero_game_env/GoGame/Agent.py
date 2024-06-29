#!/usr/bin/env python
# -*- coding: utf-8 -*-


""" Import libraries Original """
from AlphaZeroCode import Agent

# @title Agent
class Agent(Agent):
    # Override
    def human(self, node, env):
        state = node.states[0]
        self.util.show_legal_actions(self.env)

        while True:
            x = input('横,縦')
            try:
                x1, x2 = x.split(',')
                x1, x2 = int(x1), int(x2)
                if state[x2][x1] == 0:
                    break
                else:
                    break
                show_board(state)
            except:
                pass

        if x1 == -1:
            # action = self.CFG.action_size
            action = self.env.width * self.env.width
        else:
            # 縦横入れ替え
            action = x2 * self.env.width + x1

        next_node = self.mcts.human_play(node, action, env) #fix

        # return action
        return next_node

def show_board(state):
    print()
    for row in state:
        print(row)
