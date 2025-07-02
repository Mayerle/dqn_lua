
import random

import numpy as np
import pandas as pd
import torch
import torch.optim as optim
import math
from collections import deque
from pathlib import Path
from core.encoders import *
from core.rlutils import ReplayMemory
from core.balnetworks import SimpleDQN
from core.rlutils import Transition

class DQNAgent:
    __DEVICE = "cuda"
    __CHECKPOINT_PATH = "weights/checkpoint"
    __CHECKPOINT_STEPS = 2500

    __REPLAY_SIZE = 2500
    __LEARNING_RATE = 1e-4

    __EPSILON_START = 0.9
    __EPSILON_END = 0.05
    __EPSILON_DECAY = 1000

    __MINIBATCH_SIZE = 256
    __SYNC_RATE = 100
    __SAVE_RATE = 100

    __DISCOUNT_FACTOR =  0.99
    __TAU = 0.005
    def __init__(self):
        self.policy_net = SimpleDQN(24, 10).to(self.__DEVICE)
        self.target_net = SimpleDQN(24, 10).to(self.__DEVICE)
        self.target_net.load_state_dict(self.policy_net.state_dict())


        self.optimizer = optim.AdamW(self.policy_net.parameters(), lr=self.__LEARNING_RATE, amsgrad=True)
        self.memory = ReplayMemory(capacity=self.__REPLAY_SIZE)


        self.last_state = None
        self.last_selected = None
        self.last_action = None
        
        self.last_score = 0
        self.steps_done = 0
        self.sync_steps = 0
        self.reward_list = []
        self.epsilon = self.__EPSILON_START
        self.epsilon_history = []


        self.loss_fn = torch.nn.MSELoss()
    def save_checkpoint(self):
        checkpoint = {
            "steps_done": self.steps_done,
            "policy_net_state_dict": self.policy_net.state_dict(),
            "target_net_state_dict": self.target_net.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "replay_memory": list(self.memory.memory),
        }
        savepath = f"{self.__CHECKPOINT_PATH}_{self.steps_done}.pth"
        Path(savepath).parent.mkdir(parents=True, exist_ok=True)
        torch.save(checkpoint, savepath)
        print(f"Checkpoint saved at step {self.steps_done} to {savepath}")

    def load_checkpoint(self, checkpoint_path):
        checkpoint = torch.load(
            checkpoint_path, map_location=self.__DEVICE, weights_only=False
        )
        self.steps_done = checkpoint.get("steps_done", 0)
        self.policy_net.load_state_dict(checkpoint["policy_net_state_dict"])
        self.target_net.load_state_dict(checkpoint["target_net_state_dict"])
        self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        replay_memory_list = checkpoint.get("replay_memory", [])
        self.memory.memory = deque(replay_memory_list, maxlen=self.memory.memory.maxlen)
        print(f"Checkpoint loaded from {checkpoint_path}")


    def select_action(self, game_state, selected, context):

        eps_threshold = self.__EPSILON_END + (self.__EPSILON_START - self.__EPSILON_END) * \
        math.exp(-1. * self.steps_done / self.__EPSILON_DECAY)
        
        self.steps_done += 1
        self.sync_steps += 1
        action = None
        if( random.random() < eps_threshold ):
            action = self.get_random_action(game_state, selected, context)  
            print("[RANDOM]")
        else:
            with torch.no_grad():
                action = self.get_policy_action(game_state, selected, context)
                print("[POLICY]")

        return action

    

    def memory_push(self, gamestate, selected, action, next_gamestate, next_selected, reward):
        state = encode_game(gamestate,selected).unsqueeze(0)
        next_state = None
        if(next_gamestate != None):
            next_state = encode_game(next_gamestate, next_selected).unsqueeze(0)

        reward = torch.tensor([reward], device=self.__DEVICE)

        self.memory.push(state, action, next_state, reward)
        


    def optimize_model(self):
        if len(self.memory) < self.__MINIBATCH_SIZE:
            return
        
        transitions = self.memory.sample(self.__MINIBATCH_SIZE)
        batch = Transition(*zip(*transitions))
        non_final_mask = torch.tensor(
            tuple(map(lambda s: s is not None, batch.next_state)),
            device=self.__DEVICE,
            dtype=torch.bool,
        )
        non_final_next_states = torch.cat(
            [s for s in batch.next_state if s is not None]
        )
        state_batch = torch.cat(batch.state)
        action_batch = torch.cat(batch.action)
        reward_batch = torch.cat(batch.reward)
        state_action_values = self.policy_net(state_batch).gather(1, action_batch)

        next_state_values = torch.zeros(self.__MINIBATCH_SIZE, device=self.__DEVICE)
     
        with torch.no_grad():
            next_state_values[non_final_mask] = self.target_net(non_final_next_states).max(1).values
       
        expected_state_action_values = (next_state_values * self.__DISCOUNT_FACTOR) + reward_batch

        criterion = torch.nn.SmoothL1Loss()
        loss = criterion(state_action_values, expected_state_action_values.unsqueeze(1))

        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_value_(self.policy_net.parameters(), 100)
        self.optimizer.step()

        target_net_state_dict = self.target_net.state_dict()
        policy_net_state_dict = self.policy_net.state_dict()
        for key in policy_net_state_dict:
            target_net_state_dict[key] = policy_net_state_dict[key]*self.__TAU + target_net_state_dict[key]*(1-self.__TAU)
        self.target_net.load_state_dict(target_net_state_dict)

        if(self.steps_done % self.__SAVE_RATE == 0):
            self.save_checkpoint()
            
    def optimize(self, mini_batch):
        current_q_list = []
        target_q_list = []

        for state, action, new_state, reward, terminated in mini_batch:

            if terminated: 
                target = torch.FloatTensor([reward])
            else:
                with torch.no_grad():
                    target = torch.FloatTensor(
                        reward + self.__DISCOUNT_FACTOR * self.target_net(new_state).max()
                    )

            current_q = self.policy_net(state)
            current_q_list.append(current_q)

            target_q = self.target_net(state) 
            target_q[action] = target
            target_q_list.append(target_q)
                
        loss = self.loss_fn(torch.stack(current_q_list), torch.stack(target_q_list))

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def leave_correct_actions(self, output, G, selected, context):
        anti_value = -100

        if(context=="Hand"):
            
            if(len(selected) == 5):
                no_select_mask = torch.tensor([
                True, True, True, True, 
                True, True, True, True,  
                False, False
            ])
                output[no_select_mask] = anti_value
            if(len(selected) == 0):
                no_select_mask = torch.tensor([
                False, False, False, False, 
                False, False, False, False, 
                True, True, 
            ])
                output[no_select_mask] = anti_value
            if(G["current_round"]["discards_left"] == 0):
                only_play_mask = torch.tensor([
                    False, False, False, False, 
                    False, False, False, False, 
                    False, True, 
                ])
                output[only_play_mask] = anti_value


            selected_mask_array=[]
            for i in range(1,8+1):
                if( i in selected or (i+1 > len(G["hand"]) ) ):
                    selected_mask_array.append(True)
                else:
                    selected_mask_array.append(False)
            selected_mask_array.extend([False, False])
            selected_mask = torch.tensor(selected_mask_array)
            output[selected_mask] = anti_value

        
        
    def get_random_action(self, G, selected, context):
        output = torch.randint(-1, 10, (10,)).cuda()
        self.leave_correct_actions(output, G, selected, context)
        return torch.argmax(output).view(1,1).cuda()
       
    def get_policy_action(self, G, selected, context):
        state_vector = encode_game(G, selected)
        output = self.policy_net(state_vector)
        self.leave_correct_actions(output,G, selected, context)
        return torch.argmax(output).view(1,1)
    