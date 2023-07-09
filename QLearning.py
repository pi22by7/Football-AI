import pickle
import random


class QLearningPlayer:
    def __init__(self, actions, learning_rate=0.1, discount_factor=0.9, exploration_rate=0.8):
        self.actions = actions
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.q_table = {}

    def get_state_key(self, state):
        return tuple(state)

    def get_action(self, state):
        state_key = self.get_state_key(state)
        if random.random() < self.exploration_rate:
            # Explore - choose a random action
            action = random.choice(self.actions)
        else:
            # Exploit - choose the action with the highest Q-value
            q_values = self.q_table.get(state_key, {a: 0 for a in self.actions})
            max_q_value = max(q_values.values())
            best_actions = [a for a, q_value in q_values.items() if q_value == max_q_value]
            action = random.choice(best_actions)
        return action

    def update_q_value(self, state, action, next_state, reward):
        state_key = self.get_state_key(state)
        next_state_key = self.get_state_key(next_state)
        q_values = self.q_table.get(state_key, {a: 0 for a in self.actions})
        max_next_q_value = max(self.q_table.get(next_state_key, {a: 0 for a in self.actions}).values())
        q_values[action] = (1 - self.learning_rate) * q_values[action] + self.learning_rate * \
                           (reward + self.discount_factor * max_next_q_value)
        self.q_table[state_key] = q_values

    def save_q_values(self, filename):
        with open(filename, 'wb') as f:
            pickle.dump(self.q_table, f)

    def load_q_values(self, filename):
        with open(filename, 'rb') as f:
            q_values = pickle.load(f)
        return q_values

# Other utility functions or classes for training, saving/loading Q-table, etc.
