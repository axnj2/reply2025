class Resource:
    def __init__(self, ri, ra, rp, rw, rm, rl, ru, rt, re, state):
        self.ri = ri  # Resource ID
        self.ra = ra  # Activation cost
        self.rp = rp  # Periodic cost
        self.rw = rw  # Number of active turns
        self.rm = rm  # Number of downtime turns
        self.rl = rl  # Total lifecycle
        self.ru = ru  # Number of buildings powered
        self.rt = rt  # Special effect type
        self.re = re  # Special effect percentage or value

        self.state = state  # 0: inactive, 1: active, 2:maintenace, 3: dead
        # example : 0, 1, 2, 1 ,2, 3 and you can't use it anymore
        self.active_until = None
        self.alive_until = None
    
    def activate(self, turn_number):
        self.state = 1
        self.active_until = turn_number + self.rw
        self.alive_until = turn_number + self.rl

        

    



class PowerGrid:
    def __init__(self, resources : list[Resource], turns: list[dict], inital_budget: int):
        self.budget = inital_budget
        self.resources = resources
        self.turns = turns
        self.current_turn = 0

        self.score = 0

        self.actions = []


    def step_forward(self, selected_resources):
        current_action = []
        for resource in selected_resources:
            if resource.ra > self.budget:
                raise ValueError("Not enough budget")
            
            if resource.state == 0:
                resource.activate()
            self.budget -= resource.ra

            current_action.append(resource.ri)
        self.actions.append(current_action)
        
        for ressource in self.resources:
            if ressource.state == 1:
                
        
        
        self.current_turn += 1
        
    def get_available_resources(self):
        available_resources = []
        for resource in self.resources:
            if resource.state == 0 and resource.ra <= self.budget:
                available_resources.append(resource)
        return available_resources
        

INPUT_DIR = "inputs/"
file_name = "0-demo.txt"



def parse_input():
    with open(INPUT_DIR + file_name, "r") as f:
    D, R, T = map(int, f.readline().split())

    resources = []
    for i in range(R):
        raw_line = f.readline().split()
        standart_param = list(map(int, raw_line[0:7]))
        resource = {
            "identifier": standart_param[0],  # RI unique identifier of the resource
            "activation cost": standart_param[1],  # RA cost to activate the resource
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
        }
        if raw_line[7] == "X":
            resource["special type"] = None
            resource["special param"] = None
        elif raw_line[7] == "A":
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

def save_solution(turns, file_name):
    with open(file_name, "w") as f:
        for ii, activated_resources in enumerate(turns):
            f.write(str(ii) + " " + str(len(activated_resources)) + " " + " ".join(map(str, activated_resources)) + "\n")
