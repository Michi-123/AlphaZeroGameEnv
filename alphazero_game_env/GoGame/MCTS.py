#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
""" Import libraries Original """
from AlphaZeroCode import Node, MCTS

# @title MCTS
class MCTS(MCTS):
    # Add
    def human_play(self, node, action, env):

        """
        AlphaZeroの学習用の入力特徴をnodeに作成します。
        戻り値はここでは使用しません。
        """
        _features = self.util.state2feature(node)

        """ add_child_nodes()の子ノードの生成処理を変形させた処理 """
        states = self.util.get_next_states(node.states, action, node.player, env)
        actions = self.util.get_next_actions(node.actions, action)

        T = 0.3 # 行動選択の温度パラメータ(過剰適合防止のため)
        
        next_node = Node(self.CFG)
        next_node.p = 1.0 * T
        next_node.action = action
        next_node.actions = actions
        next_node.states = states
        next_node.player = -node.player
        next_node.n = 1000
        next_node.w = 0
        next_node.Q = 0

        return next_node
