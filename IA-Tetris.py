##########################################################
# Règles spécifiques à ce jeu:                           #
# -----------------------------                          #
#                                                        #
# - Il est possible de faire 5 actions avant que le bloc #
#   ne descende de force.                                #
# - L'action "DOWN" reset le compteur: on peut de        #
#   nouveau faire 5 actions                              #
# - L'action "ROTATION" est propre à ce jeu: ce n'est    #
#   pas la même rotation que dans un jeu tetris basique  #
# - Score: il n'y a pas de différents niveaux, mais un   #
#   nombre de points fixe suivant le nombre de lignes    #
#   enlevées                                             #
##########################################################

import os
import random
import time
import neat

#########################################################
# Variables d'initialisation                            #
#########################################################
GRID_WIDTH = 10
GRID_HEIGHT = 20
SCORES = [40, 100, 300, 1200]

#########################################################
# Création de la grille initiale                        #
#########################################################

empty_grid = []

for _ in range(GRID_HEIGHT):
    empty_grid.append(["."] * GRID_WIDTH)

##################################################################################
# Grille personnalisée pour les tests (enlever les commentaires pour l'utiliser) #
##################################################################################
'''
grid = [
['.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
['.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
['.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
['.', '.', '.', '.', '.', '.', '.', '.', '.', '.'],
['.', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X', 'X'],
['.', 'X', 'X', '.', '.', '.', '.', '.', '.', '.'],
['.', 'X', 'X', '.', '.', '.', '.', '.', '.', '.'],
['.', 'X', 'X', '.', '.', '.', '.', '.', '.', '.'],
['.', 'X', 'X', '.', '.', '.', '.', '.', '.', '.'],
['.', 'X', 'X', '.', '.', '.', '.', '.', '.', '.'],
['.', 'X', 'X', '.', '.', '.', '.', '.', '.', '.'],
['.', 'X', 'X', '.', '.', '.', '.', '.', '.', '.'],
['.', 'X', 'X', '.', '.', '.', '.', '.', '.', '.'],
['.', 'X', 'X', '.', '.', '.', '.', '.', '.', '.'],
['.', 'X', 'X', '.', '.', '.', '.', '.', '.', '.'],
['.', 'X', 'X', '.', '.', '.', '.', '.', '.', '.'],
['.', 'X', 'X', '.', '.', '.', '.', '.', '.', '.'],
['.', 'X', 'X', '.', '.', '.', '.', '.', '.', '.'],
['.', 'X', 'X', '.', '.', '.', '.', '.', '.', '.'],
['.', 'X', 'X', '.', '.', '.', '.', '.', '.', '.']]
'''


#########################################################
# Fonction permettant d'enlever tous les affichages     #
#########################################################
def clear():
    os.system("clear" if os.name != "nt" else 'cls')


#########################################################
# Fonction permettant l'affichage de la grille Tetris   #
#########################################################
def print_grid(grid, score):
    clear()
    print()
    print("SCORE: {} points".format(score))
    print()
    print("  ", end="")
    print("-" * (GRID_WIDTH + 2))
    for i, line in enumerate(grid):
        if len(str(i)) == 1:
            i = " " + str(i)
        print(str(i) + "|", end="")
        for colonne in line:
            print(str(colonne), end="")
        print("|")
    print("  ", end="")
    print("-" * (GRID_WIDTH + 2))


#########################################################
# Création des différents blocs de tetris               #
#########################################################
blocks_struct_rotations = {
    "1": {
        "Carre": [(1, 1), (1, 1)],
        "T": [(".", 1, "."), (1, 1, 1)],
        "Line": [(1, "."), (1, "."), (1, "."), (1, ".")],
        "L_gauche": [(1, 1), (".", 1), (".", 1)],
        "L_droite": [(1, 1), (1, "."), (1, ".")],
        "Z_droite": [(".", 1), (1, 1), (1, ".")],
        "Z_gauche": [(1, "."), (1, 1), (".", 1)]
    },
    "2": {
        "Carre": [(1, 1), (1, 1)],
        "T": [(1, "."), (1, 1), (1, ".")],
        "Line": [(1, 1, 1, 1)],
        "L_gauche": [(1, 1, 1), (1, ".", ".")],
        "L_droite": [(1, 1, 1), (".", ".", 1)],
        "Z_droite": [(1, 1, "."), (".", 1, 1)],
        "Z_gauche": [(".", 1, 1), (1, 1, ".")]
    },
    "3": {
        "Carre": [(1, 1), (1, 1)],
        "T": [(1, 1, 1), (".", 1, ".")],
        "Line": [(1, "."), (1, "."), (1, "."), (1, ".")],
        "L_gauche": [(1, "."), (1, "."), (1, 1)],
        "L_droite": [(".", 1), (".", 1), (1, 1)],
        "Z_droite": [(".", 1), (1, 1), (1, ".")],
        "Z_gauche": [(1, "."), (1, 1), (".", 1)]
    },
    "4": {
        "Carre": [(1, 1), (1, 1)],
        "T": [(".", 1), (1, 1), (".", 1)],
        "Line": [(1, 1, 1, 1)],
        "L_gauche": [(".", ".", 1), (1, 1, 1)],
        "L_droite": [(1, ".", "."), (1, 1, 1)],
        "Z_droite": [(1, 1, "."), (".", 1, 1)],
        "Z_gauche": [(".", 1, 1), (1, 1, ".")]
    },
}
blocks_names = [
    "Carre", "T", "Line", "L_droite", "L_gauche", "Z_gauche", "Z_droite"
]


#################################################################################
# Fonction permettant de nettoyer la grille entre chaque descente               #
#################################################################################
def clear_grid(grid):
    grid_ = []
    for line in grid:
        part = []
        for col in line:
            if str(col) in ["1", "."]:
                part.append(".")
            else:
                part.append(col)
        grid_.append(part)
    return grid_


#########################################################
# Geler les blocs qui ne bougent plus                   #
#########################################################


def replace_ones_with_Xs(grid):
    grid_ = []
    for line in grid:
        part = []
        for col in line:
            if str(col) == "1":
                part.append("X")
            else:
                part.append(col)
        grid_.append(part)
    return grid_


#########################################################
# Créer le bloc à un endroit possible, sinon game over  #
#########################################################
def get_possible_start_position(grid, block_to_move):
    needToChange = False
    for block in block_to_move:
        if grid[block[0]][block[1]] == "X":
            needToChange = True
    if needToChange:
        x, y = get_leftest_block(block_to_move)
        new_block = []
        for block in block_to_move:
            new_block.append((block[0], block[1] - x))
        block_to_move = [i for i in new_block]
        new_block = []
        for i in range(0, GRID_WIDTH):
            for block in block_to_move:
                new_block.append((block[0], block[1] + i))
            for block in new_block:
                if block[1] >= GRID_WIDTH:
                    return False
                if grid[block[0]][block[1]] == "X":
                    new_block = []
                    break
            if new_block:
                return new_block
        return False
    return block_to_move


#########################################################
# Créer un nouveau bloc                                 #
#########################################################


def create_blocks(grid):
    name = random.choice(blocks_names)
    block_to_create = blocks_struct_rotations["1"][name]
    x, y = int(GRID_WIDTH / 2) - len(block_to_create), 0
    block_to_move = []
    for i, el in enumerate(block_to_create):
        if el[0] != ".":
            block_to_move.append((y + i, x))
        if el[1] != ".":
            block_to_move.append((y + i, x + 1))
        if len(el) == 3:
            if el[2] != ".":
                block_to_move.append((y + i, x + 2))
    block_to_move = get_possible_start_position(grid, block_to_move)
    if block_to_move == False:
        return grid, block_to_move, name, 1, "PERDU"
    for block in block_to_move:
        grid[block[0]][block[1]] = "1"
    return grid, block_to_move, name, 1, ""


#########################################################
# Regarder si le déplacement provoque une collision     #
#########################################################


def isCollinding_with_next_move(block_to_move, grid, direction):
    for block in block_to_move:
        if direction == "DOWN" and (block[0] + 1 >= GRID_HEIGHT
                                    or grid[block[0] + 1][block[1]] == "X"):
            return False
        if direction == "RIGHT" and (block[1] + 1 >= GRID_WIDTH
                                     or grid[block[0]][block[1] + 1] == "X"):
            return False
        if direction == "LEFT" and (block[1] - 1 < 0
                                    or grid[block[0]][block[1] - 1] == "X"):
            return False
    return True


#########################################################
# On gèle le bloc qui est arrivé en bas                 #
#########################################################


def freeze_current_block(grid):
    grid = replace_ones_with_Xs(grid)
    return grid


#########################################################
# On affiche le bloc principal                          #
#########################################################
def show_block_to_move(block_to_show, grid):
    for block in block_to_show:
        grid[block[0]][block[1]] = "1"
    return grid


#########################################################
# Fonction de déplacement                              #
#########################################################
def move_block_with_direction(block_to_move, grid, direction):
    directions = {"RIGHT": (0, 1), "DOWN": (1, 0), "LEFT": (0, -1)}
    if isCollinding_with_next_move(block_to_move, grid, direction):
        new_block = []
        for block in block_to_move:
            new_block.append((block[0] + directions[direction][0],
                              block[1] + directions[direction][1]))
        grid = clear_grid(grid)
        grid = show_block_to_move(new_block, grid)
        block_to_move = new_block
        return grid, new_block, False
    elif direction == "DOWN":
        return grid, False, True
    else:
        return grid, block_to_move, False


#########################################################
# Récupérer le mini-bloc le plus haut du bloc qui bouge #
#########################################################
def highest_block(block_to_move):
    y = GRID_HEIGHT + 1
    for b in block_to_move:
        if b[0] < y:
            y = b[0]
            x = b[1]
    return y, x


#############################################################
# Récupérer le mini-bloc le plus à gauche du bloc principal #
#############################################################
def get_leftest_block(block_to_move):
    x = GRID_WIDTH + 1
    for b in block_to_move:
        if b[1] < x:
            y = b[0]
            x = b[1]
    return y, x


#########################################################
# Effectuer une rotation                                #
#########################################################
def block_rotation(grid, rotation, name, block_to_move):
    rotation = str((int(rotation) + 1))
    if rotation == "5":
        rotation = "1"
    next_rotation = blocks_struct_rotations[rotation][name]
    new_block = []
    max_block, x = highest_block(block_to_move)
    for i, line in enumerate(next_rotation):
        for j, block in enumerate(line):
            if block != ".":
                new_block.append((max_block + i, x + j))
    grid = clear_grid(grid)
    block_to_display = new_block
    for block in new_block:
        if block[0] < 0 or block[1] >= GRID_WIDTH or block[1] < 0 or block[
                0] >= GRID_WIDTH or grid[block[0] + 1][block[1]] == "X":
            block_to_display = block_to_move
            break
    grid = show_block_to_move(block_to_display, grid)
    return grid, block_to_display, rotation


#########################################################
# Enlever les lignes complètes et compter le score      #
#########################################################
def clear_full_lines(grid, score, fitness_calc):
    score_ = -1
    for i, line in enumerate(grid):
        if line == ["X"] * GRID_WIDTH:
            score_ += 1
            del grid[i]
            grid.insert(0, ["."] * GRID_WIDTH)
    if score_ != -1:
        score += SCORES[score_]
        if SCORES[score_] == 40:
            fitness_calc += 0.5
        elif SCORES[score_] == 100:
            fitness_calc += 1
        elif SCORES[score_] == 300:
            fitness_calc += 3
        elif SCORES[score_] == 1200:
            fitness_calc += 5
    return grid, score, fitness_calc

#########################################################
# Calcul-fitness pour bloc le plus haut                 #
#########################################################


def calc_fit_highest(grid):
    fit = 0
    verification_in_line = True
    for line in reversed(grid):
        for chr in line:
            if chr == "X" and verification_in_line == True:
                fit += 0.01
                verification_in_line = False
    return fit


#########################################################
# fonction de fitness+boucle principale                 #
#########################################################


def eval_genomes(genomes, config):
    nets = []
    ges = []
    grids = []
    timers = []
    scores = []
    isAlives = []
    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0
        ges.append(genome)
        grids.append(empty_grid)
        timers.append(0)
        scores.append(0)
        isAlives.append(True)

#    output = net.activate(grid)
#    takeClosest = lambda num, collection: min(collection,
#                                              key=lambda x: abs(x - num))
#    if takeClosest(output, [0, 0.33, 0.66, 1]) == 0:
#      action = "RIGHT"
#    elif takeClosest(output, [0, 0.33, 0.66, 1]) == 0.33:
#      action = "LEFT"
#    elif takeClosest(output, [0, 0.33, 0.66, 1]) == 0.66:
#      action = "DOWN"
#    elif takeClosest(output, [0, 0.33, 0.66, 1]) == 1:
#      action = "ROTATION"
    run = True
    block_to_move = False

    while run:
        if not any(isAlives):
            run = False
            break
        
        for timer in timers:
            timer += 1
        for nu, grid in enumerate(grids):
            ges[nu].fitness -= calc_fit_highest(grids[nu])

            if block_to_move == False:
                grids[nu], block_to_move, name, rotation, state = create_blocks(grids[nu])
                freeze_next = False
            if state == "PERDU":
                isAlives[nu] = False

            imp_grid=[]
            for line in grids[nu]:
                for chr in line:
                    if chr == ".":
                        imp_grid.append(0)
                    elif chr == "X":
                        imp_grid.append(-1)
                    elif chr == "1":
                        imp_grid.append(1)
            
            output_list_shape = nets[nu].activate(imp_grid)
            output = output_list_shape[0]
            def takeClosest(num, collection): return min(
                collection, key=lambda x: abs(x - num))
            if takeClosest(output, [0, 0.33, 0.66, 1]) == 0:
                action = "RIGHT"
            elif takeClosest(output, [0, 0.33, 0.66, 1]) == 0.33:
                action = "LEFT"
            elif takeClosest(output, [0, 0.33, 0.66, 1]) == 0.66:
                action = "DOWN"
            elif takeClosest(output, [0, 0.33, 0.66, 1]) == 1:
                action = "ROTATION"

            if isAlives[nu]:

                print_grid(grids[nu], scores[nu])
                if action in ["RIGHT", "LEFT", "DOWN"]:
                    grids[nu], block_to_move, freeze_next = move_block_with_direction(
                        block_to_move, grids[nu], action)
                if action == "DOWN":
                    timers[nu] = 0
                if action == "ROTATION":
                    grids[nu], block_to_move, rotation = block_rotation(grids[nu], rotation, name,
                                                                   block_to_move)

                if timers[nu] == 5 and not freeze_next:
                    grids[nu], block_to_move, freeze_next = move_block_with_direction(
                        block_to_move, grids[nu], "DOWN")
                    timers[nu] = 0

                if freeze_next:
                    grids[nu] = freeze_current_block(grid)

                grids[nu], scores[nu], ges[nu].fitness = clear_full_lines(
                    grids[nu], scores[nu], ges[nu].fitness)


def run(config_path):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(eval_genomes, 50)


local_dir = os.path.dirname(__file__)
config_path = os.path.join(local_dir, "config-feedforward.txt")
run(config_path)
