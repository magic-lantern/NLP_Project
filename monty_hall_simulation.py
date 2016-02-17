import random
from copy import deepcopy

doors = ['A', 'B', 'C']
door_tracker = {}
for door in doors:
    door_tracker[door] = 0
wins = 0
losses = 0
tests = 1000

for _ in range(tests):
    winning_door = random.choice(doors)
    door_tracker[winning_door] += 1
    picked_door = random.choice(doors)
    print('Picked door: ', picked_door)
    empty_door = ''
    for door in doors:
        if (door != winning_door and door != picked_door):
            empty_door = door
    remaining_doors = deepcopy(doors)
    remaining_doors.remove(empty_door)
    print('Door', empty_door, 'is revealed as being empty.')
    #print('Remaining doors: ', remaining_doors)

    # change mind
    remaining_doors.remove(picked_door)
    picked_door = remaining_doors[0]
    print('Changed to: ', picked_door)
    # end change mind section

    if picked_door == winning_door:
        wins += 1
    else:
        losses += 1
    print('Winning door: ', winning_door)
    print('-------end round------')


print('Winning door history: ', door_tracker)
print('Wins: ', wins, '(percent: {0:.2f})'.format(float(wins/tests) * 100))
print('Losses: ', losses, '(percent: {0:.2f})'.format(float(losses/tests) * 100))