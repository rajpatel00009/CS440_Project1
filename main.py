import random
import time
from collections import deque
import matplotlib.pyplot as plt
import copy
import time
import heapq

# Raj Patel netid: rap378



# Yug Patel netid: yp517





"""
Who worked on what:

Raj:
Placing the bot, button, and fire on three different open cells
Fire mechanism: the fire formula, checking only cells near the fire
BFS pathfinding shared search function for Bots 1, 2, and 3
Bot 4 idea and code: the cost formula, the fire distance BFS, and Dijkstra
Making the success rate graphs and the failure reasons graph
Write-up: Introduction and Section 2
Write-up: explaining Bot 4

Yug:
Ship generation: making the grid
Bot 4 idea and code, the cost formula, the fire distance BFS, and Dijkstra
Running the experiments looping over q values and trials.
Tracking why bots fail by recording the failure reason for every run
Fixing bugs: printing the grid to watch the bot, and fixing the dead-end, and start cell bug
Write-up: results and graphs
Write-up: why the bots fail and conclusion

"""


start_time = time.perf_counter()

backtracked = set() 

# * is closed
# . is open
# b is bot
# s is switch
# f is fire 

stack = deque()
visited = set() 

GRID_SIZE = 30

# intial grid with all open cells
grid = [['*' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

bot_cell = ()
switch_cell = ()

# to generate new ship before going to next trial 
def reset_grid():
    global grid
    grid = [['*' for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

#  find valid dead ends and add to list 
def update_dead_ends(dead_ends):
    for grid_row, row in enumerate(grid):
        for grid_column, val in enumerate(row):           
            r = (grid_row, grid_column)
            neighbors2 = get_neighbors(r)
            opened_neighbors = sum(
                1
                for r, c in neighbors2.values()
                if(grid[r][c] == '.')
            )
            if (opened_neighbors == 1) and (grid[grid_row][grid_column] == '.'):
                dead_ends.append((grid_row, grid_column))


def setup_grid():

    # the first cell to open
    open_cell = (random.randint(1, GRID_SIZE - 2), random.randint(1, GRID_SIZE - 2))
    row, column = open_cell
    grid[row][column] = '.' 

    # list of all cells which are valid and we can open (with exectly one neighbor)
    valid_cells = []
    valid_cells_set = set()
    for neighbor in get_neighbors(open_cell).values():
        valid_cells.append(neighbor)

    # look through each valid cell and randomlly open cell 
    while valid_cells:
        rand = random.randint(0, len(valid_cells) - 1)

        valid_cell_to_open = valid_cells.pop(rand)

        valid_cell_row, valid_cell_column = valid_cell_to_open

        if(grid[valid_cell_row][valid_cell_column] == '.'):
            continue

        neighbors = get_neighbors(valid_cell_to_open)
        opened_neighbors = sum(
            1
            for r, c in neighbors.values()
            if(grid[r][c] == '.')
        )

        if(opened_neighbors != 1):
            continue

        # open the selected cell
        grid[valid_cell_row][valid_cell_column] = '.'

        # add blocked neighbors as possible candidates
        for n in neighbors.values():
            r, c = n
            if(grid[r][c] == '*' and n not in valid_cells_set): 
                valid_cells.append(n)
                valid_cells_set.add(n)

    dead_ends = []
    update_dead_ends(dead_ends)
    dead_ends = set(dead_ends)

    to_remove = len(dead_ends) // 2
    while len(dead_ends) > to_remove:

        cell = random.choice(tuple(dead_ends))
        closed_neighbors = [] 
        for n in get_neighbors(cell).values():
            row = n[0]
            col = n[1]
            if (grid[row][col] == '*'):
                closed_neighbors.append(n)
        
        opened = random.choice(closed_neighbors)
        r, c = opened
        grid[r][c] = '.'
        changed = [opened, *get_neighbors(opened).values()]

        for i in changed:
            r1, c1 = i
            dead_ends.discard(i)
            if (grid[r1][c1] != '.'):
                continue
            open_count = sum (
                grid[nr][nc] == '.'
                for nr, nc in get_neighbors(i).values()
            )
            if(open_count == 1): 
                dead_ends.add(i)

# getting neighbots of given cell 
def get_neighbors(pos):
    x, y = pos
    neighbors = {}
    if x > 0: neighbors["top"] = (x - 1, y)
    if x < GRID_SIZE - 1: neighbors["bottom"] = (x + 1, y)
    if y > 0: neighbors["left"] = (x, y - 1)
    if y < GRID_SIZE - 1: neighbors["right"] = (x, y + 1)

    return neighbors

setup_grid()
fringe = deque()

# looking for shortest path from cell to swich usign bfs
def find_best_path(b_cell, s_cell, isbot3, ):
    global visited
    visited = set()
    fringe = deque()
    r1, c1 = b_cell
    r2, c2 = s_cell
    fringe.append((b_cell, [b_cell]))
    visited.add(b_cell) 

    while fringe:
        f, current_path = fringe.popleft()

        if (f == s_cell):
            return current_path

        all_neighbors = get_neighbors(f)

        for neighbor in all_neighbors.values():
            r3, c3 = neighbor

            if(isbot3 == True):
                if(grid[r3][c3] == '.' or grid[r3][c3] == 's'):
                    if neighbor not in visited:
                        neighbor_of_neighbor = get_neighbors(neighbor)
                        is_cell_safe = True
                        for n in neighbor_of_neighbor.values():
                            r4, c4 = n 
                            if(grid[r4][c4] == 'f'):
                                is_cell_safe = False
                                break

                        if is_cell_safe:
                            new_path = current_path + [neighbor]
                            fringe.append((neighbor, new_path))
                            visited.add(neighbor)

            elif(grid[r3][c3] == '.' or grid[r3][c3] == 's'):
                if neighbor not in visited:
                    new_path = current_path + [neighbor]
                    fringe.append((neighbor, new_path))
                    visited.add(neighbor)
            
    return None 

# running bot 1 to 3 which will be ran with one fire movemenet
def run_bot(bot_number, q, bot_cell, switch_cell):

    isbot3 = False
    
    if(bot_number == 3):
        isbot3 = True

    init_path = find_best_path(bot_cell, switch_cell, False)
    if init_path is None:
        return "no_path"

    current_path = init_path

    i = 0

    while True:
        sr, sc = switch_cell
        if grid[sr][sc] == 'f':
            return "button_burned"

        if (i > len(init_path) - 1):
            return "other"
        
        if (bot_cell == -1):
            return "other"
        

        if (bot_number == 3):
            current_path = find_best_path(bot_cell, switch_cell, True)
            if current_path is None:
                current_path = find_best_path(bot_cell, switch_cell, False)
                
            if current_path is None:
                return "no_path"
            bot_cell = current_path[1]

            if(bot_cell == -1):
                return "other"
        elif(bot_number == 2):
            current_path = find_best_path(bot_cell, switch_cell, False)
            if current_path is None:
                return "no_path"
            bot_cell = current_path[1]

        elif(bot_number == 1):
            i += 1

            if(i >= len(init_path)):
                return "other"

            bot_cell = init_path[i]

            if(bot_cell == switch_cell):
                return "success"


        if (bot_cell == switch_cell):
            return "success"
        
        r7, c7 = bot_cell

        if (grid[r7][c7] == 's'):
            return "success"


        if(grid[r7][c7] == 'f'):
            return "walked_into_fire"


        if(grid[r7][c7] != '.'):
            return "other"


        temp_fire_cells = []
        visited_neighbors = set()

        for r in fire_cells:
            fire_cell_neighbors = get_neighbors(r)
            for n in fire_cell_neighbors.values():
                if n not in visited_neighbors:
                    visited_neighbors.add(n)
                    r4, c4 = n
                    if(grid[r4][c4] != '.'):
                        continue
                    r4, c4 = n
                    neighbors_of_cell_to_fire = get_neighbors(n)

                    k = 0
                    for l in neighbors_of_cell_to_fire.values():
                        r5, c5 = l
                        if(grid[r5][c5] == 'f'):
                            k = k + 1
                    
                    flammability = random.random()
                    probability = 1 - (1 - q) ** k
                    if(probability > flammability):
                        r, c = n
                        if(grid[r][c] == '.'):
                            if n not in temp_fire_cells:
                                temp_fire_cells.append(n)
                    visited_neighbors.add(n)

        for n in temp_fire_cells:
            r5, c5 = n 
            if(grid[r5][c5] != 'f' and grid[r5][c5] != 'b' and grid[r5][c5] != 's'):
                
                grid[r5][c5] = 'f'
                if bot_cell in fire_cells:
                    return "fire_reached_bot"
                fire_cells.append(n)
                
        if(grid[r7][c7] == 'f'):
            return "fire_reached_bot"

# BFS measures shortest hallway distance from any burning cell, respecting walls.
def fire_distance():

    fire_distances = {}
    q = deque()

    for f in fire_cells:
        fire_distances[f] = 0
        q.append(f)

    while q: 
        cell = q.popleft()
        for n in get_neighbors(cell).values():

            r, c = n
            if(grid[r][c] == '*'):
                continue

            if n not in fire_distances:
                fire_distances[n] = fire_distances[cell] + 1
                q.append(n)

    return fire_distances

# Dijkstra searches for best path 
def find_best_path_bot4(bot_cell, switch_cell, q):

    pq = []
    fire_distances = fire_distance()
    heapq.heappush(pq, (0, bot_cell, [bot_cell]))

    visited_cost = {}
  
    while pq:
        total_cost, current, path = heapq.heappop(pq)
        if(current == switch_cell):
            return path

        if (current in visited_cost) and (total_cost >= visited_cost[current]):
            continue
        
        visited_cost[current] = total_cost
        
        for candidate in get_neighbors(current).values():

            r, c = candidate

            if(grid[r][c] != '.' and grid[r][c] != 's'):
                continue

            normal_cost = 1

            neighbors = get_neighbors(candidate)

            neighbors_on_fire = 0
            for adjacent in neighbors.values():

                r, c = adjacent
                if(grid[r][c] == 'f'):
                    neighbors_on_fire += 1
            
            probability = 1 - (1 - q) ** neighbors_on_fire

            cell_fire_risk = probability
            distance_from_fire = fire_distances.get(candidate, float('inf'))

            risk_weight = 5
            distance_weight = 5

            fire_distance_penalty = distance_weight / (distance_from_fire + 1)

            cell_cost = normal_cost + risk_weight * cell_fire_risk + fire_distance_penalty
            
            new_cost = total_cost + cell_cost
            new_path = path + [candidate]

            heapq.heappush(pq, (new_cost, candidate, new_path))

    return None

# for bot4 replaning with Dijkstra adter every fire spread 
def run_bot4(q, bot_cell, switch_cell):

    while True:
        sr, sc = switch_cell
        if(grid[sr][sc] == 'f'):
            return "button_burned"

        dijkstra_path = find_best_path_bot4(bot_cell, switch_cell, q)

        if(dijkstra_path is None):
            return "no_path"
        if(bot_cell == switch_cell):
            return "success"

        if(len(dijkstra_path) < 2):
            return "other"
        bot_cell = dijkstra_path[1]
        if(bot_cell == switch_cell):
            return "success"
        
        r, c = bot_cell

        if(grid[r][c] == 'f'):
            return "walked_into_fire"
        
        if(grid[r][c] != '.' and grid[r][c] != 's' and grid[r][c] != 'b'):
            return "other"
        
        temp = []
        visited = set()

        for fire_cell in fire_cells:
            fire_cell_neighbors = get_neighbors(fire_cell)
            for n in fire_cell_neighbors.values():
                if n in visited:
                    continue
                r4, c4 = n

                if(grid[r4][c4] == 'b' or grid[r4][c4] == 's'):
                    visited.add(n)
                    continue

                neighbors_of_cell_to_fire = get_neighbors(n)
                k = 0

                for l in neighbors_of_cell_to_fire.values():
                    r5, c5 = l
                    if(grid[r5][c5] == 'f'):
                        k += 1

                probability = 1 - (1 - q) ** k
                flammability = random.random()

                if(probability > flammability):
                    if(grid[r4][c4] == '.'):
                        temp.append(n)
                visited.add(n)

        for n in temp:
            r5, c5 = n
            if(grid[r5][c5] not in ('f', 'b', 's')):
                grid[r5][c5] = 'f'
                fire_cells.append(n)

        if bot_cell in fire_cells:
            return "fire_reached_bot"

# chose open cells for bot button and intial fire (all disticnt)
def setup_simulation():
    global bot_cell, switch_cell, fire_cells

    open_cells = [
        (r_idx, c_idx) 
        for r_idx, row in enumerate(grid) 
        for c_idx, val in enumerate(row) 
        if val == '.'
    ]

    closed_cells = [
        (r_idx, c_idx) 
        for r_idx, row in enumerate(grid) 
        for c_idx, val in enumerate(row) 
        if val == '*'
    ]

    r1 = random.randint(0, len(open_cells) - 1)
    bot_cell =  open_cells[r1]
    bot_row, bot_column = bot_cell
    grid[bot_row][bot_column] = 'b'

    r2 = random.choice(list(range(0, r1)) + list(range(r1 + 1, len(open_cells))))
    switch_cell = open_cells[r2]
    switch_row, switch_column = switch_cell
    grid[switch_row][switch_column] = 's'

    for n in range(GRID_SIZE):
        for l in range(GRID_SIZE):
            if(grid[n][l] == 'b'):
                bot_cell = (n, l)
            if(grid[n][l] == 's'):
                switch_cell = (n, l)

    r3 = random.randint(0, len(open_cells) - 1)
    init_fire_cell = open_cells[r3]
    init_fire_cell_row, init_fire_cell_column = init_fire_cell

    while (grid[init_fire_cell_row][init_fire_cell_column] != '.'):
        r3 = random.randint(0, len(open_cells) - 1)
        init_fire_cell = open_cells[r3]
        init_fire_cell_row, init_fire_cell_column = init_fire_cell


    grid[init_fire_cell_row][init_fire_cell_column] = 'f'
    fire_cells = []
    fire_cells.append((init_fire_cell_row, init_fire_cell_column))
    grid[init_fire_cell_row][init_fire_cell_column] = 'f'
    fire_cells = []
    fire_cells.append((init_fire_cell_row, init_fire_cell_column))

    grid[bot_row][bot_column] = '.'
    grid[switch_row][switch_column] = '.'


bot1 = False
bot2 = False
bot3 = False

# all bot's sucess rate
bot1_results = {}
bot2_results = {}
bot3_results = {}
bot4_results = {}

# test q from 0 to 0.6 steps of 0.05 and then from 0.7 to 1.0 in steps  of 0.1
q_values1 = [x / 20 for x in range(13)]
q_values2 = [x / 10 for x in range(7, 11)]

q_values = q_values1 + q_values2

# Number of independent ship setups tested for each q value
num_trials = 100

# store failure counts by reason and q to plot graph
bot1_failures = {}
bot2_failures = {}
bot3_failures = {}
bot4_failures = {}


# reset outcome counters for each flammability
for q in q_values:

    success_count1 = 0
    success_count2 = 0
    success_count3 = 0
    success_count4 = 0

    button_burned_1 = 0
    button_burned_2 = 0
    button_burned_3 = 0
    button_burned_4 = 0

    no_path1 = 0
    no_path2 = 0
    no_path3 = 0
    no_path4 = 0

    walked_into_fire1 = 0
    walked_into_fire2 = 0
    walked_into_fire3 = 0
    walked_into_fire4 = 0

    fire_reached_bot1 = 0
    fire_reached_bot2 = 0
    fire_reached_bot3 = 0
    fire_reached_bot4 = 0

    fire_reached_bot1 = 0
    fire_reached_bot2 = 0
    fire_reached_bot3 = 0
    fire_reached_bot4 = 0

    other1 = 0
    other2 = 0
    other3 = 0
    other4 = 0


    for r in range(num_trials):

        reset_grid()
        setup_grid()
        setup_simulation()

        original_grid = copy.deepcopy(grid)
        original_fire = fire_cells.copy()
        
        grid = [row[:] for row in original_grid]
        fire_cells = original_fire.copy()
        res1 = run_bot(1, q, bot_cell, switch_cell)

        grid = [row[:] for row in original_grid]
        fire_cells = original_fire.copy()
        res2 = run_bot(2, q, bot_cell, switch_cell)

        grid = [row[:] for row in original_grid]
        fire_cells = original_fire.copy()
        res3 = run_bot(3, q, bot_cell, switch_cell)

        grid = [row[:] for row in original_grid]
        fire_cells = original_fire.copy()
        res4 = run_bot4(q, bot_cell, switch_cell)
        
        match res1:
            case 'success':
                success_count1 += 1
            case 'button_burned':
                button_burned_1 += 1
            case 'walked_into_fire':
                walked_into_fire1 += 1
            case 'fire_reached_bot':
                fire_reached_bot1 += 1
            case 'no_path':
                no_path1 += 1
            case 'other':
                other1 += 1

        match res2:
            case 'success':
                success_count2 += 1
            case 'button_burned':
                button_burned_2 += 1
            case 'walked_into_fire':
                walked_into_fire2 += 1
            case 'fire_reached_bot':
                fire_reached_bot2 += 1
            case 'no_path':
                no_path2 += 1
            case 'other':
                other2 += 1

        match res3:
            case 'success':
                success_count3 += 1
            case 'button_burned':
                button_burned_3 += 1
            case 'walked_into_fire':
                walked_into_fire3 += 1
            case 'fire_reached_bot':
                fire_reached_bot3 += 1
            case 'no_path':
                no_path3 += 1
            case 'other':
                other3 += 1

        match res4:
            case 'success':
                success_count4 += 1
            case 'button_burned':
                button_burned_4 += 1
            case 'walked_into_fire':
                walked_into_fire4 += 1
            case 'fire_reached_bot':
                fire_reached_bot4 += 1
            case 'no_path':
                no_path4 += 1
            case 'other':
                other4 += 1

    
    bot1_results[q] = success_count1 / num_trials
    bot2_results[q] = success_count2 / num_trials
    bot3_results[q] = success_count3 / num_trials
    bot4_results[q] = success_count4 / num_trials

    bot1_failures[q] = {
        "button_burned": button_burned_1,
        "no_path": no_path1,
        "walked_into_fire": walked_into_fire1,
        "fire_reached_bot": fire_reached_bot1,
        "other": other1,
    }

    bot2_failures[q] = {
        "button_burned": button_burned_2,
        "no_path": no_path2,
        "walked_into_fire": walked_into_fire2,
        "fire_reached_bot": fire_reached_bot2,
        "other": other1,
    }

    bot3_failures[q] = {
        "button_burned": button_burned_3,
        "no_path": no_path3,
        "walked_into_fire": walked_into_fire3,
        "fire_reached_bot": fire_reached_bot3,
        "other": other3,
    }

    bot4_failures[q] = {
        "button_burned": button_burned_4,
        "no_path": no_path4,
        "walked_into_fire": walked_into_fire4,
        "fire_reached_bot": fire_reached_bot4,
        "other": other4,
    }

print(f'the result for bot 1')
print(bot1_results)
print(f'the result for bot 2')
print(bot2_results)
print(f'the result for bot 3')
print(bot3_results)
print(f'the result for bot 4')
print(bot4_results)

# Compare the four bots' success rates as flammability increases.
plt.plot(bot1_results.keys(), bot1_results.values(), marker='o', label='Bot 1')
plt.plot(bot2_results.keys(), bot2_results.values(), marker='o', label='Bot 2')
plt.plot(bot3_results.keys(), bot3_results.values(), marker='o', label='Bot 3')
plt.plot(bot4_results.keys(), bot4_results.values(), marker='o', label='Bot 4')

end_time = time.perf_counter()

elapsed_time = end_time - start_time
print(f"Elapsed time: {elapsed_time:.6f} seconds")

# ploting graph starts here 


plt.xlabel("Flammability (q)")
plt.ylabel("Success Rate")
plt.title("Bot Success Rate vs Flammability")

# add grid sie and number of trials to the success graph caption
plt.figtext(
    0.5, 0.01,
    f"Grid Size: {GRID_SIZE} × {GRID_SIZE} | Trials per q: {num_trials}",
    ha="center"
)

plt.xticks(sorted(set(q_values)), rotation=45)
plt.grid(True, axis='both', linestyle='--', alpha=0.4)
plt.tight_layout()


plt.legend()
plt.grid()

plt.xticks(sorted(set(q_values)), rotation=45)

plt.grid(True, axis='both', linestyle='--', alpha=0.4)


plt.legend()
plt.tight_layout()


failure_results = [
    bot1_failures,
    bot2_failures,
    bot3_failures,
    bot4_failures,
]

reasons = {
    "button_burned": "Button burned",
    "no_path": "No path",
    "walked_into_fire": "Walked into fire",
    "fire_reached_bot": "Fire reached bot",
    "other": "Other",
}

fig, axes = plt.subplots(
    2, 2, figsize=(12, 8), sharex=True, sharey=True
)

for bot_number, (ax, results) in enumerate(
    zip(axes.flat, failure_results), start=1
):
    qs = sorted(results)

    for reason, label in reasons.items():
        rates = [
            results[q][reason] / num_trials
            for q in qs
        ]

        ax.plot(qs, rates, marker="o", label=label)

    ax.set_title(f"Bot {bot_number}")
    ax.set_xlabel("Flammability (q)")
    ax.set_ylabel("Fraction of all trials")
    ax.set_ylim(0, 1)
    ax.grid(True, linestyle="--", alpha=0.4)

handles, labels = axes[0, 0].get_legend_handles_labels()
fig.legend(handles, labels, loc="upper center", ncol=3)

fig.tight_layout(rect=[0, 0, 1, 0.90])
fig.savefig("bot_failure_reasons.png", dpi=300)

plt.show()  


plt.close()
