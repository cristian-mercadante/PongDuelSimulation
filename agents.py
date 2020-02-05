from abc import ABC, abstractmethod

NOOP = 0
UP = 1
DOWN = 2


class Agent(ABC):
    # Abstract class for creating agents

    def get_ball_dir(self, ball_dir_list):
        if ball_dir_list[0] == 1:
            return "NW"
        elif ball_dir_list[1] == 1:
            return "W"
        elif ball_dir_list[2] == 1:
            return "SW"
        elif ball_dir_list[3] == 1:
            return "SE"
        elif ball_dir_list[4] == 1:
            return "E"
        elif ball_dir_list[5] == 1:
            return "NE"

    def see(self, obs):
        self._grid_y = 40
        self._grid_x = 30
        self._agent_y = obs[0]
        self._agent_x = obs[1]
        self._ball_y = obs[2]
        self._ball_x = obs[3]
        self._ball_dir_list = obs[4:10]
        self._ball_dir = self.get_ball_dir(self._ball_dir_list)
        self._enemy_y = obs[10]
        self._enemy_x = obs[11]
        self._player_number = 0 if self._agent_x < 0.5 else 1
        self._selected_hit_direction = None

    def go_to_pos(self, pos):
        if self._agent_y > pos:
            return UP
        elif self._agent_y < pos:
            return DOWN
        else:
            return NOOP
        return NOOP

    def idle(self):
        return self.go_to_pos(0.5)

    def chase_ball(self):
        if self._agent_y > self._ball_y:
            return UP
        elif self._agent_y < self._ball_y:
            return DOWN
        return NOOP

    def chase_ball_direction(self):
        if self._agent_y > self._ball_y:
            if self._ball_dir in ["NW", "W", "NE", "E"]:
                return UP
            elif self._ball_dir in ["SW", "SE"]:
                return NOOP
        elif self._agent_y < self._ball_y:
            if self._ball_dir in ["SW", "W", "SE", "E"]:
                return DOWN
            elif self._ball_dir in ["NW", "NE"]:
                return NOOP
        else:
            return NOOP

    def is_defending(self):
        if (any(self._ball_dir_list[0:3]) and self._player_number == 0) or \
                (any(self._ball_dir_list[3:]) and self._player_number == 1):
            return True
        else:
            return False

    def chase_ball_only_defense(self):
        if self.is_defending():
            return self.chase_ball()
        return NOOP

    def go_to_ball_destination(self):
        pos = self.calculate_ball_destination()
        return self.go_to_pos(pos)

    def hit_up(self):
        self._selected_hit_direction = "up"
        self._agent_y = round(self._agent_y * self._grid_y)
        self._agent_y -= 2
        self._agent_y /= self._grid_y

    def hit_down(self):
        self._selected_hit_direction = "down"
        self._agent_y = round(self._agent_y * self._grid_y)
        self._agent_y += 2
        self._agent_y /= self._grid_y

    def hit_straight(self):
        self._selected_hit_direction = "straight"

    def calculate_ball_destination(self, pred_ball_x=None, pred_ball_y=None, direction=None):
        pred_ball_x = pred_ball_x if pred_ball_x else self._ball_x
        pred_ball_y = pred_ball_y if pred_ball_y else self._ball_y
        ball_y = round(pred_ball_y * self._grid_y)
        ball_x = round(pred_ball_x * self._grid_x)
        # ball_dir = direction if direction else self._ball_dir
        bounced = False
        HIT_SPACING = 2

        delta_p = 1
        loop_range = self._grid_x - HIT_SPACING
        wall = 0

        if not direction:
            # simple case: ball goes straight and doesn't bounce
            if self._ball_dir in ["E", "W"]:
                return self._ball_y

            # SET LOOP RANGE: ball goes east
            if self._ball_dir in ["NE", "SE"]:
                loop_range = self._grid_x - HIT_SPACING - ball_x - 1
            # SET LOOP RANGE: ball goes west
            elif self._ball_dir in ["NW", "SW"]:
                loop_range = ball_x - HIT_SPACING

            # SET POSITION VARIATION AND WALL: ball goes north
            if self._ball_dir in ["NE", "NW"]:
                delta_p = -1
                wall = 0
            # SET POSITION VARIATION AND WALL: ball goes south
            elif self._ball_dir in ["SE", "SW"]:
                delta_p = 1
                wall = self._grid_y - 1
        else:
            loop_range = self._grid_x - HIT_SPACING
            if direction == "N":
                delta_p = -1
                wall = 0
            elif direction == "S":
                deltap_p = 1
                wall = self._grid_y - 1

        for i in range(int(loop_range)):
            if ball_y == wall:
                bounced = True
            if not bounced:
                ball_y += delta_p
            else:
                ball_y -= delta_p
        return ball_y / self._grid_y

    def get_hit_destinations(self, pos_impact):
        # [hit_up, hit_down, hit_straight]
        final_y = []
        # if hit_up
        final_y.append(self.calculate_ball_destination(pred_ball_x=self._agent_x, pred_ball_y=pos_impact, direction="N"))
        # if hit_down
        final_y.append(self.calculate_ball_destination(pred_ball_x=self._agent_x, pred_ball_y=pos_impact, direction="S"))
        # if hit_straight
        final_y.append(self._agent_y)
        return final_y

    def select_best_hit(self, pos_impact, intention):
        final_y = self.get_hit_destinations(pos_impact)
        final_y = [i - self._enemy_y for i in final_y]
        final_y = [abs(i) for i in final_y]
        if intention == "coop":
            max_value = min(final_y)
        elif intention == "comp":
            max_value = max(final_y)
        best_hit = 0
        for count, element in enumerate(final_y):
            if element == max_value:
                best_hit = count
                break
        if best_hit == 0:
            self.hit_up()
            return
        elif best_hit == 1:
            self.hit_down()
            return
        else:
            self.hit_straight()
        return

    def predict_enemy_target(self, intention):
        pos_impact = self.calculate_ball_destination()
        targets = []
        for i in ["N", "S"]:
            targets.append(self.calculate_ball_destination(pred_ball_x=self._enemy_x, pred_ball_y=pos_impact, direction=i))
        targets.append(pos_impact)

        enemy_decisions = targets.copy()
        enemy_decisions = [i - self._agent_y for i in enemy_decisions]
        enemy_decisions = [abs(i) for i in enemy_decisions]

        if intention == "comp":
            enemy_decision = max(enemy_decisions)
        elif intention == "coop":
            enemy_decision = min(enemy_decisions)

        dest = 0
        for count, element in enumerate(enemy_decisions):
            if element == enemy_decision:
                dest = targets[count]
                break
        return dest

    @abstractmethod
    def act(self, obs):
        pass


class Agent00(Agent):
    def act(self, obs):
        self.see(obs)
        return self.idle()


class Agent01(Agent):
    def act(self, obs):
        self.see(obs)
        return self.chase_ball()


class Agent02(Agent):
    def act(self, obs):
        self.see(obs)
        return self.chase_ball_only_defense()


class Agent03(Agent):
    def act(self, obs):
        self.see(obs)
        return self.chase_ball_direction()


class Agent04(Agent):
    def act(self, obs):
        self.see(obs)
        self.hit_down()
        return self.chase_ball()


class Agent05(Agent):
    def act(self, obs):
        self.see(obs)
        tactic = "coop"
        if self.is_defending():
            pos_impact = self.calculate_ball_destination()
            self.select_best_hit(pos_impact, tactic)
            return self.go_to_pos(pos_impact)

        else:
            # return NOOP
            # return self.idle()
            return self.chase_ball()
            # dest = self.predict_enemy_target(tactic)
            # return self.go_to_pos(dest)


class AgentComp01(Agent):
    def act(self, obs):
        self.see(obs)
        tactic = "comp"
        if self.is_defending():
            pos_impact = self.calculate_ball_destination()
            self.select_best_hit(pos_impact, tactic)
            return self.go_to_pos(pos_impact)
        else:
            return NOOP


class AgentComp02(Agent):
    def act(self, obs):
        self.see(obs)
        tactic = "comp"
        if self.is_defending():
            pos_impact = self.calculate_ball_destination()
            self.select_best_hit(pos_impact, tactic)
            return self.go_to_pos(pos_impact)
        else:
            return self.idle()


class AgentComp03(Agent):
    def act(self, obs):
        self.see(obs)
        tactic = "comp"
        if self.is_defending():
            pos_impact = self.calculate_ball_destination()
            self.select_best_hit(pos_impact, tactic)
            return self.go_to_pos(pos_impact)
        else:
            return self.chase_ball()


class AgentComp04(Agent):
    def act(self, obs):
        self.see(obs)
        tactic = "comp"
        if self.is_defending():
            pos_impact = self.calculate_ball_destination()
            self.select_best_hit(pos_impact, tactic)
            return self.go_to_pos(pos_impact)
        else:
            dest = self.predict_enemy_target(tactic)
            return self.go_to_pos(dest)


class AgentCoop01(Agent):
    def act(self, obs):
        self.see(obs)
        tactic = "coop"
        if self.is_defending():
            pos_impact = self.calculate_ball_destination()
            self.select_best_hit(pos_impact, tactic)
            return self.go_to_pos(pos_impact)
        else:
            return NOOP


class AgentCoop02(Agent):
    def act(self, obs):
        self.see(obs)
        tactic = "coop"
        if self.is_defending():
            pos_impact = self.calculate_ball_destination()
            self.select_best_hit(pos_impact, tactic)
            return self.go_to_pos(pos_impact)
        else:
            return self.idle()


class AgentCoop03(Agent):
    def act(self, obs):
        self.see(obs)
        tactic = "coop"
        if self.is_defending():
            pos_impact = self.calculate_ball_destination()
            self.select_best_hit(pos_impact, tactic)
            return self.go_to_pos(pos_impact)
        else:
            return self.chase_ball()


class AgentCoop04(Agent):
    def act(self, obs):
        self.see(obs)
        tactic = "coop"
        if self.is_defending():
            pos_impact = self.calculate_ball_destination()
            self.select_best_hit(pos_impact, tactic)
            return self.go_to_pos(pos_impact)
        else:
            dest = self.predict_enemy_target(tactic)
            return self.go_to_pos(dest)
