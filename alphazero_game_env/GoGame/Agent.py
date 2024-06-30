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
        is_pass = False

        while True:
            x = input('横,縦 ')
            
            # Pass 判定
            if x == 'pass' or x == 'p' or x == '-1':
                is_pass = True
                break

            try:
                x = x.replace(',',' ')
                x1, x2 = x.split()
                x1, x2 = int(x1), int(x2)
                
                if state[x2][x1] == 0:
                    break
                else:
                    continue
            except:
                continue

        if is_pass:
            action = self.CFG.pass_action
        else:
            # 縦横入れ替えて行動のインデックスを計算
            action = x2 * self.env.width + x1

        next_node = self.mcts.human_play(node, action, env) #fix

        # return action
        return next_node

def show_board(state):
    print()
    for row in state:
        print(row)
