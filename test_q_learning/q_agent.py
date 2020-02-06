import numpy as np


class QAgent:
    """
    Class that models a reinforcement learning agent.
    """

    def __init__(self, n_agent_y, n_ball_y, n_ball_x, n_dir, n_enemy_y, n_actions,
                 epsilon=0.01, alpha=1, gamma=1):
        self.n_agent_y = n_agent_y
        #self.n_agent_x = n_agent_x
        self.n_ball_y = n_ball_y
        self.n_ball_x = n_ball_x
        self.n_dir = n_dir
        self.n_enemy_y = n_enemy_y
        #self.n_enemy_x = n_enemy_x
        self.n_actions = n_actions

        self.epsilon = epsilon
        self.alpha = alpha
        self.gamma = gamma

        self.Q = np.random.rand(self.n_agent_y, self.n_ball_y, self.n_ball_x, self.n_dir, self.n_enemy_y, self.n_actions)

    def get_action_eps_greedy(self, a_y, b_y, b_x, d, e_y):
        """
        Epsilon-greedy sampling of next action given the current state.

        Returns
        -------
        action: int
            Action sampled according to epsilon-greedy policy.
        """
        # pass
        return np.where(np.random.uniform(0, 1) >= self.epsilon, np.argmax(self.Q[a_y][b_y][b_x][d][e_y]), np.random.randint(0, self.n_actions))

    def get_action_greedy(self, a_y, b_y, b_x, d, e_y):
        """
        Greedy sampling of next action given the current state.

        Returns
        -------
        action: int
            Action sampled according to greedy policy.
        """
        # pass
        return np.argmax(self.Q[a_y][b_y][b_x][d][e_y])

    def update_Q(self, old_state, action, reward, new_state):
        """
        Update action-value function Q

        Parameters
        ----------
        old_state: tuple
            Previous state of the Environment
        action: int
            Action performed to go from `old_state` to `new_state`
        reward: int
            Reward got after action `action`
        new_state: tuple
            Next state of the Environment

        Returns
        -------
        None
        """
        #r, c = old_state[0], old_state[1]
        a_y = old_state[0]
        #a_x = old_state[1]
        b_y = old_state[1]
        b_x = old_state[2]
        d = old_state[3]
        e_y = old_state[4]
        #e_x = old_state[6]

        #r_new, c_new = new_state[0], new_state[1]
        new_a_y = new_state[0]
        #new_a_x = new_state[1]
        new_b_y = new_state[1]
        new_b_x = new_state[2]
        new_d = new_state[3]
        new_e_y = new_state[4]
        #new_e_x = new_state[6]

        self.Q[a_y, b_y, b_x, d, e_y, action] = self.Q[a_y, b_y, b_x, d, e_y, action] + self.alpha * (
            reward + self.gamma * self.Q[
                new_a_y, new_b_y, new_b_x, new_d, new_e_y,
                self.get_action_greedy(new_a_y, new_b_y, new_b_x, new_d, new_e_y)
            ]
            - self.Q[a_y, b_y, b_x, d, e_y, action])
