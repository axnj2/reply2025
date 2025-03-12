INPUT_DIR = "inputs/"
file_name = "0-demo.txt"

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

print(resources)
print(turns)

def save_solution(turns, file_name):
    with open(file_name, "w") as f:
        for ii, activated_resources in enumerate(turns):
            f.write(str(ii) + " " + str(len(activated_resources)) + " " + " ".join(map(str, activated_resources)) + "\n")

