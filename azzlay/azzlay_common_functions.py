# common functions 
import ctypes

item_to_url_map = {
    "circle": ('/static/images/circle_overlay.png', '/static/images/circle_overlay_2.png'),
    "triangle": ('/static/images/triangle_overlay.png', '/static/images/triangle_overlay_2.png'),
    "square": ('/static/images/square_overlay.png', '/static/images/square_overlay_2.png'),
    "quantum": ('/static/images/quantum_overlay.png', '/static/images/quantum_overlay_2.png')
}

def maxWindow():
    # This function is not needed for a web application.
    pass

def sumLists(list1, list2):
    # Be sure to use two lists of the same length
    sumList = []
    for i in range(0, len(list1)):
        sumList.append(list1[i] + list2[i])
    return sumList

def isInGrid(des, grid):
    # Returns True if the inserted coordinates are in the grid
    return des[0]>=0 and des[0]<len(grid) and des[1]>=0 and des[1]<len(grid[0])

def isPieceMovable(co, direction):
    des = sumLists(co, direction)
    return isInGrid(des)

def whatIsInCell(co, grid):
    if isInGrid(co, grid):
        return grid[co[0]][co[1]]
    else:
        return "not in grid"

def readDir(dir):
    # Reads a direction and returns the equivalent offset
    if dir == "up": 
        return [-1, 0]
    if dir == "down":       
        return [1, 0]
    if dir == "left": 
        return [0, -1]
    if dir == "right":
        return [0, 1]
