#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Import libraries Original """
from AlphaZeroCode.network import AlphaZeroNetwork, Resnet

# @title AlphaZeroNetwork
class AlphaZeroNetwork(AlphaZeroNetwork):
    # Override
    def __init__(self, CFG):
        super().__init__(CFG)
        print('override __init__')

        self.CFG = CFG
        in_channels = self.CFG.history_size * 2 + 1

        """ Convolution block """
        self.conv1 = nn.Conv2d(in_channels, self.CFG.resnet_channels, kernel_size=3,
                               stride=1, padding='same', bias=False)
        self.bn1 = nn.BatchNorm2d(self.CFG.resnet_channels)

        """ Resnet """
        resnet = []
        for _ in range(self.CFG.n_residual_block):
            resnet += [Resnet(self.CFG)]
        self.resnet = nn.Sequential(*resnet)

        """ Policy for Go """
        num_filter = 2
        self.conv_policy = nn.Conv2d(self.CFG.resnet_channels, num_filter,
                                    kernel_size=1, stride=1, padding='same',
                                    bias=False)
        self.bn_policy = nn.BatchNorm2d(num_filter)

        self.fc_policy = nn.Linear(in_features=self.CFG.board_width * self.CFG.board_width * num_filter,
                                  out_features=self.CFG.action_size)


        """ Policy for chess and shogi. fileter数と kernel サイズに注意! """
        """
        num_filter = 1
        # ResNetと同じblock
        self.conv_policy1 = nn.Conv2d(self.CFG.resnet_channels, CFG.resnet_channels,
                                    kernel_size=3, stride=1, padding='same',
                                    bias=False)
        self.bn_policy1 = nn.BatchNorm2d(CFG.resnet_channels)

        # Policy output
        num_filter =1
        self.conv_policy2 = nn.Conv2d(self.CFG.resnet_channels, num_filter,
                                    kernel_size=1, stride=1, padding='same',
                                    bias=False)
        self.bn_policy2 = nn.BatchNorm2d(num_filter)
        """

        """ State value """
        conv_value_out_channels = 1
        self.conv_value = nn.Conv2d(self.CFG.resnet_channels, conv_value_out_channels,
                                    kernel_size=1, stride=1, padding='same',
                                    bias=False)
        self.bn_value = nn.BatchNorm2d(conv_value_out_channels)

        # fc_value_in_channels = self.CFG.action_size * conv_value_out_channels
        fc_value_in_channels = self.CFG.board_width * self.CFG.board_width * conv_value_out_channels

        self.fc_value1 = nn.Linear(in_features=fc_value_in_channels,
                                    out_features=self.CFG.hidden_size)
        self.fc_value2 = nn.Linear(in_features=self.CFG.hidden_size, out_features=1)

        """ Weight initializtion """
        self._create_weights()

    # Override
    def policy_head(self, x):
        print('override policy_head')
        """
        Architecture
        The policy head applies an additional rectified, batch-normalized convolutional layer, followed by a final convolution of 73 filters for chess or 139 filters for shogi, or a linear layer of size 362 for Go, representing the logits of the respective policies described above.
        """
        x = self.conv_policy(x)
        x = self.bn_policy(x)
        x = F.relu(x, inplace=True)

        x = torch.flatten(x, start_dim=1) # バッチは除く
        x = self.fc_policy(x)
        x = F.softmax(x, dim=1)
        return x