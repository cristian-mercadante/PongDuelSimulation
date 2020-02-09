import gym
import ma_gym
from ma_gym.wrappers import Monitor

from models import registered_models, AutoLoadModel


class Tester():
    def __init__(self, models, env_name="PongDuel-v0", render=True, video=True, step_number=1000, log_after_steps=200, log_on_win=True):
        self._models = models  # list of model id to test. If "all", test "all"
        if "all" in self._models:
            self._models = [i for i in registered_models["all"]]
        self._render = render
        self._video = video
        self._step_number = step_number
        self._log_after_steps = log_after_steps
        self._log_on_win = log_on_win
        self._env_name = env_name
        self._env = None

    def log_score(self, step, score, msg=""):
        print("Step: {0:05d} Score: {1}".format(step, score), end="")
        if msg != "":
            print(" [{}]".format(msg))
        else:
            print("")

    def run_tests(self):
        print("Running tests for model IDs: {}".format(self._models))
        print("-" * 10)
        models_score_summary = {}

        for model_id in self._models:
            print("Selected model_id: {}".format(model_id))
            model = AutoLoadModel(model_id)

            score = {"agent_0": {"moves": 0,
                                 "wins": 0},
                     "agent_1": {"moves": 0,
                                 "wins": 0}}
            self._env = gym.make(self._env_name)
            if self._video:
                if type(model_id) is list:
                    model_id = "{}_VS_{}".format(model_id[0], model_id[1])
                output_directory = "recordings/{}".format(model_id)
                self._env = Monitor(self._env, directory=output_directory, video_callable=lambda episode_id: True, force=True)
            obs_n = self._env.reset()

            for _ in range(self._step_number):

                # render env
                if self._render:
                    self._env.render()

                # select actions
                actions, actions_as_list = model.get_agents_actions(obs_n)

                # update moves counter
                for an in ["agent_0", "agent_1"]:
                    if actions[an] in [1, 2]:
                        score[an]["moves"] += 1

                # execute actions
                obs_n, reward_n, done_n, info = self._env.step(actions_as_list)

                # update score
                if any(reward_n):
                    score["agent_0"]["wins"] += reward_n[0]
                    score["agent_1"]["wins"] += reward_n[1]
                    if self._log_on_win == True:
                        self.log_score(_, score, "win")
                models_score_summary[model_id] = score
                if _ % self._log_after_steps == 0:
                    self.log_score(_, score)

                if all(done_n):
                    break

            self.log_score(_, score, "end")
            print("-" * 10)
            self._env.close()

        # Score summary
        print("Summary:")
        for k, v in models_score_summary.items():
            n_moves = 0
            n_wins = 0
            print("Model{}:".format(k))
            for a, b in v.items():
                print(a, b)
                n_moves += b["moves"]
                n_wins += b["wins"]
            print("Average move count: {}".format(n_moves / 2))
            print("Total move count: {}".format(n_moves))
            print("Total win count: {}".format(n_wins))
            print("")


def simple_model_list():
    models = ["comp_0{}".format(i) for i in range(1, 5)]
    models.extend(["coop_0{}".format(i) for i in range(1, 5)])
    return models


def all_comp_vs_coop_model_list():
    models = []
    for i in range(1, 5):
        for j in range(1, 5):
            models.append(["comp_0{}".format(i), "coop_0{}".format(j)])
    return models


def all_vs_model_list_type(m_type):
    if m_type not in ["comp", "coop"]:
        raise ValueError("m_type must be either \'comp\' or \'coop\'")
    models = []
    for i in range(1, 5):
        for j in range(1, 5):
            if j > i:
                models.append(["{}_0{}".format(m_type, i), "{}_0{}".format(m_type, j)])
    return models


def all_vs_model_list():
    models = []
    for m_type in ["comp", "coop"]:
        models.extend(all_vs_model_list_type(m_type))
    return models


if __name__ == "__main__":
    #models = simple_model_list()
    #models = all_comp_vs_coop_model_list()
    models = all_vs_model_list()
    tester = Tester(models=models)
    tester.run_tests()
