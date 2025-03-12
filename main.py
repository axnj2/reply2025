import copy
import itertools

INPUT_DIR = "inputs/"
file_name = "0-demo.txt"



class Resource:
    def __init__(self, ri, ra, rp, rw, rm, rl, ru, rt, re):
        self.ri = ri  # Resource ID
        self.ra = ra  # Activation cost
        self.rp = rp  # Periodic cost
        self.rw = rw  # Number of active turns
        self.rm = rm  # Number of downtime turns
        self.rl = rl  # Total lifecycle
        self.ru = ru  # Number of buildings powered
        self.rt = rt  # Special effect type
        self.re = re  # Special effect percentage or value

        self.state = 0  # 0: inactive, 1: active, 2:maintenace, 3: dead
        # example : 0, 1, 2, 1 ,2, 3 and you can't use it anymore
        self.active_until = None
        self.reactivate_on = None
        self.alive_until = None
        self.life_extension = 0

    def activate(self, turn_number: int, life_extension: int):
        if self.state == 0:
            self.life_extension = life_extension
            self.state = 1
            self.active_until = turn_number + int(
                self.rw * (1 + self.life_extension / 100)
            )
            self.alive_until = turn_number + int(
                self.rl * (1 + self.life_extension / 100)
            )
        else:
            raise ValueError("Resource is not inactive")

    def reactivate(self, turn_number: int):
        self.state = 1
        self.active_until = turn_number + int(self.rw * (1 + self.life_extension))

    def deactivate(self, turn_number: int):
        self.state = 2
        self.reactivate_on = turn_number + int(self.rm * (1 + self.life_extension))

    def kill(self):
        self.state = 3

    def special_effect(self, resources):
        if self.rt == "A":
            self.ru = int(self.ru * (1 + self.re / 100))
        if self.rt == "B":
            if self.re > 0:
                for resource in resources:
                    resource.rm = int(resource.rm * (1 + self.re / 100))
                    resource.rw = int(resource.rw * (1 + self.re / 100))
            else:
                for resource in resources:
                    resource.rm = int(resource.rm * (1 - self.re / 100))
                    resource.rw = int(resource.rw * (1 - self.re / 100))
        if self.rt == "C":
            if self.re > 0:
                for resource in resources:
                    resource.rl = int(resource.rl * (1 + self.re / 100))
            else:
                for resource in resources:
                    resource.rl = int(resource.rl * (1 - self.re / 100))
        if self.rt == "D":
            if self.re > 0:
                self.re = int(self.re * (1 + self.re / 100))


class PowerGrid:
    def __init__(
        self, resources: list[Resource], turns: list[dict], inital_budget: int
    ):
        self.budget = inital_budget
        self.resource_types = resources
        self.turns = turns

        self.current_turn = 0
        self.current_ressources = []
        self.score = 0
        self.accumulator_storage = 0
        self.actions = []

    

    def step_forward(self, selected_resources: list[int]):
        total_cost = sum(
            self.resource_types[resource_id].ra for resource_id in selected_resources
        )
        if total_cost > self.budget:
            return -1

        # Clean up resources and updates their states
        for ressource in self.current_ressources:
            if ressource.state == 1 or ressource.state == 2:
                if ressource.alive_until == self.current_turn:
                    ressource.kill()

            if ressource.state == 1:
                if ressource.active_until == self.current_turn:
                    ressource.deactivate(self.current_turn)

            elif ressource.state == 2:
                if ressource.reactivate_on == self.current_turn:
                    ressource.reactivate(self.current_turn)

        power_modifier = (
            0  # A pourcentage increase or decrease in number of buildings powered
        )
        min_max_building_modifier = 0  # B pourcentage increase or decrease in min and max number of buildings powered
        life_extension_modifier = (
            0  # C pourcentage increase or decrease in life time of build building
        )
        profit_modifier = 0  # D pourcentage increase or decrease in profit per building
        accumulator_capacity = 0  # E maximum capacity of the accumulator

        # calculate the modifiers
        for ressource in self.current_ressources:
            if ressource.state == 1:
                if ressource.rt == "A":
                    power_modifier += ressource.re
                if ressource.rt == "B":
                    min_max_building_modifier += ressource.re
                if ressource.rt == "C":
                    life_extension_modifier += ressource.re
                if ressource.rt == "D":
                    profit_modifier += ressource.re
                if ressource.rt == "E":
                    accumulator_capacity += ressource.re
    
        for ressource_id in selected_resources:
            ressource = self.resource_types[ressource_id]
            if ressource.rt == "A":
                power_modifier += ressource.re
            if ressource.rt == "B":
                min_max_building_modifier += ressource.re
            if ressource.rt == "C":
                life_extension_modifier += ressource.re
            if ressource.rt == "D":
                profit_modifier += ressource.re
            if ressource.rt == "E":
                accumulator_capacity += ressource.re
            
        
        self.accumulator_storage = min(self.accumulator_storage, accumulator_capacity)

        # apply the limit to the modifiers
        if power_modifier < 0:
            power_modifier = 0
        if min_max_building_modifier < 0:
            min_max_building_modifier = 0
        if life_extension_modifier < 1:
            life_extension_modifier = 1
        if profit_modifier < 0:
            profit_modifier = 0


        current_action = []
        for resource_id in selected_resources:
            if self.resource_types[resource_id].ra > self.budget:
                return -1

            self.current_ressources.append(
                copy.deepcopy(self.resource_types[resource_id])
            )
            self.current_ressources[-1].activate(
                self.current_turn, life_extension_modifier
            )
            self.budget -= self.resource_types[resource_id].ra

            current_action.append(self.resource_types[resource_id].ri)
        self.actions.append(current_action)

        buildings_powered: int = int(
            sum(
                resource.ru
                for resource in self.current_ressources
                if resource.state == 1
            )
            * (1 + power_modifier / 100)
        )

        min_powered: int = int(
            self.turns[self.current_turn]["minimum powered"]
            * (1 + min_max_building_modifier / 100)
        )
        max_powered: int = int(
            self.turns[self.current_turn]["maximum powered"]
            * (1 + min_max_building_modifier / 100)
        )

        if buildings_powered >= min_powered:
            profit = min(buildings_powered, max_powered) * (
                self.turns[self.current_turn]["profit per building"]
                * (1 + profit_modifier / 100)
            )
        else:
            profit = 0

        self.budget += profit
        self.budget -= sum(
            resource.rp for resource in self.current_ressources if resource.state == 1
        )
        if buildings_powered > max_powered:
            self.accumulator_storage += buildings_powered - max_powered
        self.accumulator_storage = min(self.accumulator_storage, accumulator_capacity)

        self.current_turn += 1
        self.score += profit

        print(self.score)

        return self.score

    def get_available_resources(self):
        available_resources = []
        for resource in self.resource_types:
            if resource.ra <= self.budget:
                available_resources.append(copy.deepcopy(resource))
        return available_resources
    
    
    

    
    

def parse_input():
    with open(INPUT_DIR + file_name, "r") as f:
        D, R, T = map(int, f.readline().split())

        resources = []
        for i in range(R):
            raw_line = f.readline().split()
            standart_param = list(map(int, raw_line[0:7]))
            resource = {
                "identifier": standart_param[0],  # RI unique identifier of the resource
                "activation cost": standart_param[
                    1
                ],  # RA cost to activate the resource
                "maintenance cost": standart_param[2],  # RP cost per turn when alive
                "active period": standart_param[
                    3
                ],  # RW number of turn it will be active for
                "maintenance period": standart_param[
                    4
                ],  # RM number of turn before it is active again
                "life time": standart_param[
                    5
                ],  # RL number of turn  active + unactive before the resource is destroyed
                "number powered": standart_param[
                    6
                ],  # RU number of buildings the resource can power
                "special type": None,
                "special param": None,
            }
            if raw_line[7] == "A":
                resource["special"] = "A"
                resource["special param"] = int(raw_line[8])
            elif raw_line[7] == "B":
                resource["special"] = "B"
                resource["special param"] = int(raw_line[8])
            elif raw_line[7] == "C":
                resource["special"] = "C"
                resource["special param"] = int(raw_line[8])
            elif raw_line[7] == "D":
                resource["special"] = "D"
                resource["special param"] = int(raw_line[8])
            elif raw_line[7] == "E":
                resource["special"] = "E"
                resource["special param"] = int(raw_line[8])
            resources.append(resource)

        turns = []
        for i in range(T):
            raw_line = f.readline().split()
            turn = {
                "minimum powered": int(raw_line[0]),  # TM
                "maximum powered": int(raw_line[1]),  # TX
                "profit per building": int(raw_line[2]),  # TP
            }
            turns.append(turn)

    return D, resources, turns


def save_solution(turns, file_name):
    with open(file_name, "w") as f:
        for ii, activated_resources in enumerate(turns):
            f.write(
                str(ii)
                + " "
                + str(len(activated_resources))
                + " "
                + " ".join(map(str, activated_resources))
                + "\n"
            )


def main():
    intitial_cap, resources, turns = parse_input()

    # initialize the resources
    resources = [
        Resource(
            resource["identifier"],
            resource["activation cost"],
            resource["maintenance cost"],
            resource["active period"],
            resource["maintenance period"],
            resource["life time"],
            resource["number powered"],
            resource["special type"],
            resource["special param"],
        )
        for resource in resources
    ]

    starting_power_grid = PowerGrid(resources, turns, intitial_cap)

 

    number_of_resources = len(resources)
    all_possible_actions :list = []
    for nn in range(1, number_of_resources +1):
        all_possible_actions.extend(itertools.combinations(range(number_of_resources), nn))

    current_candidate = starting_power_grid
    for ii in range(len(turns)):
        print(all_possible_actions)
        best_action = max(all_possible_actions, key=lambda x: copy.deepcopy(current_candidate).step_forward(x))
        current_candidate.step_forward(best_action)

        print(current_candidate.score)
    
    save_solution(current_candidate.actions, "output.txt")


main()
