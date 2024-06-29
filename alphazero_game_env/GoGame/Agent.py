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
            x = input('横,縦')
            
            if x == 'pass' or x == 'p':
                is_pass = True
                break

            x = x.replace(',',' ')

            try:
                x1, x2 = x.split()
                x1, x2 = int(x1), int(x2)
                
                if x1 == -1:
                    is_pass = True
                    break
                
                if state[x2][x1] == 0:
                    break
                else:
                    break
                show_board(state)
            except:
                pass

        if is_pass:
            action = self.CFG.pass_action
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
