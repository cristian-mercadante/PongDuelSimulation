import gym
import ma_gym
from q_agent import QAgent

from ma_gym.wrappers import Monitor


def convert_one_hot(obs):
    ret = []
    ret.append(obs[0])
    ret.extend(obs[2:4])
    oh = obs[4:10]
    tail = obs[10]
    val = 0
    for i, e in enumerate(oh):
        if e == 1:
            val = i
            break
    ret.append(val)
    ret.append(tail)
    return ret


def denormalize(obs):
    obs[0] = round(obs[0] * 40)
    obs[1] = round(obs[1] * 40)
    obs[2] = round(obs[2] * 30)
    obs[4] = round(obs[4] * 40)
    return obs


def get_obs_tuples(obs):
    obs_0, obs_1 = obs[0], obs[1]
    obs_0.extend(obs_1[0:2])
    obs_1.extend(obs_0[0:2])
    obs_0, obs_1 = convert_one_hot(obs_0), convert_one_hot(obs_1)
    obs_0, obs_1 = denormalize(obs_0), denormalize(obs_1)
    # ADD ENEMY POS
    #
    state_0, state_1 = tuple(obs_0), tuple(obs_1)
    return state_0, state_1


if __name__ == '__main__':
    env_name = "PongDuel-v0"
    num_episodes = 10000
    num_steps = 1000

    agent_args = {
        "n_agent_y": 40,
        "n_ball_y": 40,
        "n_ball_x": 30,
        "n_dir": 6,
        "n_actions": 3,
        "n_enemy_y": 40,
        "epsilon": 0.1
    }

    env = gym.make(env_name)
    agent_0 = QAgent(**agent_args)
    #agent_1 = QAgent(**agent_args)

    for e in range(num_episodes):
        cumulative_reward = 0

        obs = env.reset()

        # reinforcement loop
        # while True:
        for _ in range(num_steps):
            state_0, state_1 = get_obs_tuples(obs)
            a_0_y, b_0_y, b_0_x, d_0, e_0_y, = state_0[0], state_0[1], state_0[2], state_0[3], state_0[4]
            #a_1_y, b_1_y, b_1_x, d_1, e_1_y, = state_1[0], state_1[1], state_1[2], state_1[3], state_1[4]
            action_0 = agent_0.get_action_eps_greedy(a_0_y, b_0_y, b_0_x, d_0, e_0_y)
            #action_1 = agent_1.get_action_eps_greedy(a_1_y, b_1_y, b_1_x, d_1, e_1_y)
            action_1 = env.action_space.sample()[1]
            action = []
            action.append(action_0)
            action.append(action_1)
            obs, reward, done, info = env.step(action)

            new_state_0, new_state_1 = get_obs_tuples(obs)

            agent_0.update_Q(state_0, action_0, reward[0], new_state_0)
            #agent_1.update_Q(state_1, action_1, reward[1], new_state_1)
            cumulative_reward += reward[0]
            cumulative_reward += reward[1]
            if all(done):
                break
        print('Episode: {:03d} - Cumulative reward this episode: {}'.format(e, cumulative_reward))

    input('End of training. \n\nPress `ENTER` to start testing.')

    env = Monitor(env, directory="recordings", video_callable=lambda episode_id: True, force=True)
    obs = env.reset()
    # while True:
    for _ in range(num_steps):
        env.render()
        state_0, state_1 = get_obs_tuples(obs)
        a_0_y, b_0_y, b_0_x, d_0, e_0_y, = state_0[0], state_0[1], state_0[2], state_0[3], state_0[4]
        #a_1_y, b_1_y, b_1_x, d_1, e_1_y, = state_1[0], state_1[1], state_1[2], state_1[3], state_1[4]
        action_0 = agent_0.get_action_greedy(a_0_y, b_0_y, b_0_x, d_0, e_0_y)
        #action_1 = agent_1.get_action_greedy(a_1_y, b_1_y, b_1_x, d_1, e_1_y)
        action_1 = env.action_space.sample()[1]
        action = []
        action.append(action_0)
        action.append(action_1)
        obs, reward, done, info = env.step(action)
        if all(done):
            break

    env.close()
