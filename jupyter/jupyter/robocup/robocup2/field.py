scale = 500
scale_field = 1/(scale + 0.01) * 50

x = 1820
y = 2340
goal_wx = 10
goal_wy = 10
field = [
    [0, 0, 0, 2340],
    [0, 0, 1820, 0],
    [0, 2340, 1820, 2340],
    [1820, 0, 1820, 2340],    
]

goal = [
    [610-goal_wx, 246-goal_wy, 610+goal_wx+600, 246-goal_wy],
    [610-goal_wx, 246-goal_wy, 610-goal_wx, 320],
    [610-goal_wx, 320, 610, 320],
    [610, 320, 610, 246],
    [610, 246, 1210, 246],
    [1210, 246, 1210, 320],
    [1210, 320, 1210+goal_wx, 320],
    [1210+goal_wx, 320, 1210+goal_wx, 246-goal_wy]
]

for s in goal:
    field.append(s)    
    
goal2 = []
for l in goal:
    l2 = []
    for i in range (len(l)):
        l2.append(l[i])
    l2[1] = 2340 - l2[1]
    l2[3] = 2340 - l2[3]
    goal2.append(l2 )

for s in goal2:
    field.append(s)
    
field_t = []

for i in range (len(field)):
    a = []
    field_t.append(a)
    for j in range (len(field[i])):
        field_t[i].append(int(field[i][j] * scale_field))
 