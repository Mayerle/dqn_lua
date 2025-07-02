

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

class SimpleDQN(nn.Module):
    def __init__(self, n_observations, n_actions):
        super(SimpleDQN, self).__init__()
        self.net1 = nn.Sequential(
            nn.Linear(n_observations, 512),
            nn.ReLU(),
            nn.Linear(512, 1024),
            nn.ReLU(),
            nn.Linear(1024, 1024),
            nn.ReLU(),
            nn.Linear(1024, 512),
            nn.ReLU(),
            nn.Linear(512, n_actions)
        )

    def forward(self, x):
        return self.net1(x)