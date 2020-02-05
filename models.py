from abc import ABC, abstractmethod

import importlib

registered_models = {
    "all": {
        "00": {
            "model": "Model00",
            "agent": "Agent00",
            "description": "Passive agents",
        },
        "01": {
            "model": "Model01",
            "agent": "Agent01",
            "description": "Agents follow ball position",
        },
        "02": {
            "model": "Model02",
            "agent": "Agent02",
            "description": "Agents move only if the ball is directed towards them",
        },
        "03": {
            "model": "Model03",
            "agent": "Agent03",
            "description": "Agents moves only if not in ball range. Sometimes fails...",
        },
        "04": {
            "model": "Model04",
            "agent": "Agent04",
            "description": "Agents can give direction to ball on hit",
        },
        "05": {
            "model": "Model05",
            "agent": "Agent05",
            "description": "Agents send the ball far or close from/to enemy",
        },
        "comp_01": {
            "model": "ModelComp01",
            "agent": "AgentComp01",
            "description": "Competitive agent that doesn't move after hit",
        },
        "comp_02": {
            "model": "ModelComp02",
            "agent": "AgentComp02",
            "description": "Competitive agent that stands in the middle",
        },
        "comp_03": {
            "model": "ModelComp03",
            "agent": "AgentComp03",
            "description": "Competitive agent that chases the ball",
        },
        "comp_04": {
            "model": "ModelComp04",
            "agent": "AgentComp04",
            "description": "Competitive agent that predicts enemy target",
        },
        "coop_01": {
            "model": "ModelCoop01",
            "agent": "AgentCoop01",
            "description": "Collaborative agent that doesn't move after hit",
        },
        "coop_02": {
            "model": "ModelCoop02",
            "agent": "AgentCoop02",
            "description": "Collaborative agent that stands in the middle",
        },
        "coop_03": {
            "model": "ModelCoop03",
            "agent": "AgentCoop03",
            "description": "Collaborative agent that chases the ball",
        },
        "coop_04": {
            "model": "ModelCoop04",
            "agent": "AgentCoop04",
            "description": "Collaborative agent that predicts enemy target",
        },

    }
}


class Model(ABC):
    # Abstract class for creating models

    @abstractmethod
    def get_agents(self):
        # Returns a couple of agents
        return {"agent_0": Agent00(), "agent_1": Agent00()}

    @abstractmethod
    def get_agents_actions(self):
        # Returns actions from agents
        return {"agent_0": 0, "agent_1": 1}


class AutoLoadModel(Model):
    def __init__(self, model_id):
        # model_id must be a string with 2 numbers,
        # like "00", "01", etc.
        self._n_agents = 2
        self._agent_type = registered_models["all"][model_id]["agent"]
        getattr(importlib.import_module("agents"), self._agent_type)
        self._agents = {
            # NB: without the 2 () at the end we wouldn't create an obj,
            # but a reference to the class
            ("agent_{}".format(i)): getattr(importlib.import_module("agents"), self._agent_type)()
            for i in range(self._n_agents)
        }

    def get_agents(self):
        return self._agents

    def get_agents_actions(self, obs):

        # include enemy position in observations
        obs[0].extend(obs[1][0:2])
        obs[1].extend(obs[0][0:2])

        actions = {}
        actions_as_list = []
        for i in range(self._n_agents):
            agent_id = "agent_{}".format(i)
            act = self._agents[agent_id].act(obs[i])
            actions[agent_id] = act
            actions_as_list.append(act)
        return actions, actions_as_list


# module level test
if __name__ == '__main__':
    print("test")
    model = AutoLoadModel("02")
    print(model._agents)
    print("endtest")
