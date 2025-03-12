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

    def __str__(self):
        return f"Resource {self.ri}: Cost={self.ra}, Periodic={self.rp}, Power={self.ru}, Effect={self.rt}"

# Turn class removed

def parse_input(file_path):
    with open(file_path, 'r') as f:
        initial_cap, num_resources, num_turns = map(int, f.readline().split())
        resources = []
        for i in range(num_resources):
            line = f.readline().strip().split()
            
            if len(line) < 9:
                line.extend(['0'] * (9 - len(line)))
            
            int_values = list(map(int, line[:7]))

            rt = line[7]
            re = int(line[8]) if len(line) > 8 else 0
            
            resource = Resource(*int_values, rt, re)
            resources.append(resource)
        
        turns = []
        for i in range(num_turns):
            line = f.readline().strip().split()
            tm, tx, tr = map(int, line)
            turns.append({
                'tm': tm,  # Minimum buildings to power
                'tx': tx,  # Maximum buildings to power
                'tr': tr   # Profit per building
            })
            
    return initial_cap, resources, turns

def play_game(initial_cap, resources, turns):
    budget = initial_cap
    active_resources = []
    result = []

    for turn_index, turn in enumerate(turns):
        selected_resources = []
        total_cost = 0
        for resource in resources:
            if total_cost + resource.ra <= budget:  #
                selected_resources.append(resource)
                total_cost += resource.ra
        
        buildings_powered = sum(resource.ru for resource in selected_resources)
        if buildings_powered >= turn['tm']:  # Use dictionary access
            profit = min(buildings_powered, turn['tx']) * turn['tr']  # Use dictionary access
        else:
            profit = 0
        
        budget = budget - total_cost + profit - sum(resource.rp for resource in selected_resources)

        if selected_resources:
            result.append(f"{turn_index} {len(selected_resources)} " + " ".join(str(resource.ri) for resource in selected_resources))

    return result

def main():
    input_file = '0-demo.txt'
    initial_cap, resources, turns = parse_input(input_file)
    result = play_game(initial_cap, resources, turns)

    with open("output.txt", 'w') as f:
        for line in result:
            f.write(line + "\n")

if __name__ == "__main__":
    main()