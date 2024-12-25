import pygame, sys
import tkinter as tk
from tkinter import messagebox

pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
font = pygame.font.Font('font/Kanit-Light.ttf', 29)
secondaryFont = pygame.font.Font('font/Kanit-Light.ttf', 25)
bodyFont = pygame.font.Font('font/Roboto-Regular.ttf', 16)
text_col = '#2b2d42'
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

start_img = pygame.image.load('graphics/startbutton.png').convert_alpha()
exit_img = pygame.image.load('graphics/exitbutton.png').convert_alpha()
tutorial_img = pygame.image.load('graphics/tutorialbutton.png').convert_alpha()
start_maze_img = pygame.image.load('graphics/startbutton.png').convert_alpha()
clear_maze_img = pygame.image.load('graphics/clearbutton.png').convert_alpha()
preset_maze_img = pygame.image.load('graphics/presetbutton.png').convert_alpha()

menu_state = "main"

class Button:
    def __init__(self, x, y, image, scale):
        # This will be used to scale an image in case it's too big.
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.clicked = False
    def draw(self):
        # Getting the position of the mouse cursor to detect if it's clicked the button
        pos = pygame.mouse.get_pos()
        action = False
        if self.rect.collidepoint(pos):
            # Self.clicked == false is used to make sure the button doesn't trigger multiple times 
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True
            if pygame.mouse.get_pressed()[0] == 0:
               self.clicked = False
        screen.blit(self.image, (self.rect.x, self.rect.y))
        return action

def show_error_window(message):
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Error", message)

class Grid:
    def __init__(self, layout):
        self.layout = layout
        self.startingNodeCoordinates = None
        self.endNodeCoordinates = None
    def isWall(self, row, col):
        try:
            if self.layout[row][col] == '#':
                return True
            else:
                return False
        except IndexError:
            print("The number(s) you entered were too large.")
    def startNodeCoords(self):
        for i in range(len(self.layout)):
            for j in range(len(self.layout[i])):
                if self.layout[i][j] == 'S':
                    self.startingNodeCoordinates = (i, j)
                    return i, j
    def endNodeCoords(self):
        for i in range(len(self.layout)):
            for j in range(len(self.layout[i])):
                if self.layout[i][j] == 'X':
                    self.endNodeCoordinates = (i, j)
                    return i, j

# NodesToSearch is a list that contains surrounding nodes to the current position and will be filtered out constantly, and SearchedNodes is just a list that contains all nodes that have been searched
class AStarSearch(Grid):
    def __init__(self, layout):
        super().__init__(layout)
        self.startNodeCoords()
        self.endNodeCoords()
        self.nodesToSearch = []
        self.searchedNodes = []
    def calculate_f_cost(self, row, col):
        currentX = row
        currentY = col
        # First we calculate the distance between the starting node coords and current node to get the G cost
        GxDistance = abs(self.startingNodeCoordinates[0] - currentX)
        GyDistance = abs(self.startingNodeCoordinates[1] - currentY)
        gCost = GxDistance + GyDistance
        # We then calculate the H cost as well
        HxDistance = abs(self.endNodeCoordinates[0] - currentX)
        HyDistance = abs(self.endNodeCoordinates[1] - currentY)
        hCost = HxDistance + HyDistance
        # This is the F Cost (the sum of both H and G costs)
        fCost = hCost + gCost
        return fCost
    def tie_breaker(self, row1, row2, col1, col2):
        HCost1 = abs(self.endNodeCoordinates[0] - row1) + abs(self.endNodeCoordinates[1] - col1)
        HCost2 = abs(self.endNodeCoordinates[0] - row2) + abs(self.endNodeCoordinates[1] - col2)
        # H Cost 1 will be the current smallest node and coordinates, 
        # And H cost 2 will be whatever the next contender is 
        return HCost1 < HCost2
    def search(self):
        blockSize = 50
        parents = {}
        solved = False
        self.nodesToSearch.append(self.startingNodeCoordinates)
        if self.startingNodeCoordinates == self.endNodeCoordinates:
            return
        elif self.startingNodeCoordinates == None or self.endNodeCoordinates == None:
            show_error_window("You did not place a start/end node on the grid.")
            return
        while len(self.nodesToSearch) != 0:
            smallest_f_cost = 99999
            smallest_node = ()
            for i in range(len(self.nodesToSearch)):
                # Calculates the F cost of each node. ([i][0] = row and [i][1] = column)
                f_cost = self.calculate_f_cost(self.nodesToSearch[i][0], self.nodesToSearch[i][1])
                if f_cost < smallest_f_cost:
                    smallest_f_cost = f_cost
                    smallest_node = self.nodesToSearch[i]
                elif f_cost == smallest_f_cost:
                    # Tie breaker will be dependent on the H cost
                    if self.tie_breaker(smallest_node[0], self.nodesToSearch[i][0], smallest_node[1], self.nodesToSearch[i][1]):
                        pass
                    else:
                        smallest_f_cost = f_cost
                        smallest_node = self.nodesToSearch[i]
                else:
                    pass
            if gridMaze[smallest_node[0]][smallest_node[1]] not in ('S', 'X'):
                gridMaze[smallest_node[0]][smallest_node[1]] = 'D'
            drawGrid(blockSize, gridMaze)
            pygame.display.update()
            pygame.time.delay(50)
            self.nodesToSearch.remove(smallest_node)
            self.searchedNodes.append(smallest_node)
            if smallest_node == self.endNodeCoordinates:
                # Here we generate the path we took to get here in the first place
                currentNode = self.endNodeCoordinates
                while currentNode != self.startingNodeCoordinates:
                    x,y = currentNode
                    if gridMaze[x][y] != 'S' and gridMaze[x][y] != 'X':
                        gridMaze[x][y] = '*'
                    currentNode = parents[currentNode]
                solved = True
                break
            else:
                # Generate neighbouring nodes and find all the costs - Up, down, left, and right from the current position (aka the Smallest Node.)
                Smallest_x_coordinate = smallest_node[0]
                Smallest_y_coordinate = smallest_node[1]
                # Calculate 'up'
                up_node = (Smallest_x_coordinate-1, Smallest_y_coordinate)
                if Smallest_x_coordinate-1 >= 0 and not self.isWall(Smallest_x_coordinate-1, Smallest_y_coordinate) and up_node not in self.searchedNodes and up_node not in self.nodesToSearch:
                    self.nodesToSearch.append(up_node)
                    parents[up_node] = smallest_node
                # Calculate 'down'
                down_node = (Smallest_x_coordinate+1, Smallest_y_coordinate)
                # This is really just us saying 'is it greater than the number of rows we have?
                if Smallest_x_coordinate+1 <= 11 and not self.isWall(Smallest_x_coordinate+1, Smallest_y_coordinate) and down_node not in self.searchedNodes and down_node not in self.nodesToSearch:
                    self.nodesToSearch.append(down_node)
                    parents[down_node] = smallest_node
                # Calculate 'right'
                right_node = (Smallest_x_coordinate, Smallest_y_coordinate+1)
                # This is us saying is the y-coordinate greater than the number of columns we have?
                if Smallest_y_coordinate+1 <= 15 and not self.isWall(Smallest_x_coordinate, Smallest_y_coordinate+1) and right_node not in self.searchedNodes and right_node not in self.nodesToSearch:
                    self.nodesToSearch.append(right_node)
                    parents[right_node] = smallest_node
                # Calculate 'left'
                left_node = (Smallest_x_coordinate, Smallest_y_coordinate-1)
                if Smallest_y_coordinate-1 >= 0 and not self.isWall(Smallest_x_coordinate, Smallest_y_coordinate-1) and left_node not in self.searchedNodes and left_node not in self.nodesToSearch:
                    self.nodesToSearch.append(left_node)
                    parents[left_node] = smallest_node
        if not solved:
            show_error_window("No solution to the maze.")
               

def draw_text(text, font, text_colour, x, y):
    # This function will be used to create text and ensure it's centered.
    image = font.render(text, True, text_colour)
    text_rect = image.get_rect(center=(x, y))
    screen.blit(image, text_rect)

def main_menu():
    global menu_state
    run = True
    start_button = Button(SCREEN_WIDTH // 2, 325, start_img, 0.97)
    tutorial_button = Button(SCREEN_WIDTH // 2, 450, tutorial_img, 0.97)
    while run:
        screen.fill('#f4f4f9')
        draw_text("A* Pathfinding Visualizer", font, text_col, SCREEN_WIDTH // 2, 100)
        draw_text('By Ryaan Khawaja', secondaryFont, text_col, SCREEN_WIDTH // 2, 150)
        if menu_state == "main":
            # Draws the buttons on the main screen.
            pygame.display.set_caption("Main Menu")
            if start_button.draw():
                menu_state = "visualizer"
            if tutorial_button.draw():
                menu_state = "tutorial"
        if menu_state == "visualizer":
            visualizerPage()
        if menu_state == "tutorial":
            tutorialPage()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        pygame.display.update()

nodes = ['S', 'X']
gridMaze = [[' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
[' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
[' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
[' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
[' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
[' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
[' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
[' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
[' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
[' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
[' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
[' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ']]

presetMaze = [
    ['S', '#', ' ', ' ', '#', ' ', '#', ' ', '#', ' ', ' ', '#', '#', ' ', '#', ' '],
    [' ', ' ', ' ', ' ', '#', '#', '#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#', ' '],
    ['#', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', '#', '#', ' ', ' ', ' ', '#', ' '],
    [' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', ' ', '#', '#'],
    [' ', '#', ' ', ' ', ' ', '#', '#', ' ', ' ', '#', ' ', '#', ' ', ' ', ' ', ' '],
    [' ', ' ', '#', ' ', ' ', ' ', '#', ' ', '#', '#', ' ', ' ', ' ', ' ', ' ', ' '],
    ['#', ' ', ' ', '#', ' ', '#', ' ', '#', ' ', '#', '#', ' ', '#', ' ', ' ', ' '],
    ['#', ' ', '#', ' ', '#', '#', ' ', ' ', '#', ' ', '#', ' ', '#', '#', '#', '#'],
    ['#', ' ', ' ', ' ', ' ', ' ', '#', '#', '#', '#', ' ', '#', '#', ' ', '#', ' '],
    [' ', ' ', ' ', '#', ' ', '#', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '#', ' '],
    [' ', ' ', '#', '#', ' ', ' ', ' ', ' ', '#', ' ', '#', ' ', '#', '#', '#', ' '],
    [' ', '#', ' ', '#', ' ', ' ', ' ', ' ', ' ', ' ', '#', ' ', ' ', ' ', ' ', 'X']
]


action_executed = False

def visualizerPage():
    global menu_state, nodes, action_executed
    pygame.display.set_caption("A* Pathfinding Visualizer")
    exit_button = Button(150, 50, exit_img, 0.6)
    start_maze = Button(225, SCREEN_HEIGHT - 50, start_maze_img, 0.6)
    clear_maze = Button(500, SCREEN_HEIGHT - 50, clear_maze_img, 0.6)
    preset_maze = Button(785, SCREEN_HEIGHT - 50, preset_maze_img, 0.6)
    screen.fill("#f4f4f9")
    blockSize = 50
    drawGrid(blockSize, gridMaze)
    if start_maze.draw():
        if not action_executed:
            searchMaze = AStarSearch(gridMaze)
            searchMaze.search()
            action_executed = True
    if exit_button.draw():
        menu_state = "main"
    if clear_maze.draw():
        for i in range(len(gridMaze)):
            for j in range(len(gridMaze[i])):
                gridMaze[i][j] = ' '
                nodes = ['S', 'X']
        action_executed = False
    if preset_maze.draw():
        for i in range(len(gridMaze)):
            for j in range(len(gridMaze[i])):
                gridMaze[i][j] = presetMaze[i][j]
        nodes = []
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Get the position of the mouse and find out what row/column it falls under by first subtracting it by 100 (offset since we moved it to be more centered)
            # Then divide by the blocksize to get its row/column
            pos = pygame.mouse.get_pos()
            grid_x = pos[0] - 100
            grid_y = pos[1] - 100
            row = grid_y // blockSize
            column = grid_x // blockSize
            # check if row/column exists in grid maze
            try:
                if event.button == 1:
                    if row >= 0 and column >= 0:
                        # If there is already a block just left click again and it will be deleted
                        if gridMaze[row][column] == "#":
                            gridMaze[row][column] = ' '
                        elif gridMaze[row][column] == 'S':
                            gridMaze[row][column] = ' '
                            nodes.insert(0, 'S')
                        elif gridMaze[row][column] == 'X':
                            gridMaze[row][column] = ' '
                            nodes.append('X')
                        else:
                            gridMaze[row][column] = '#'
                    else:
                        pass
                elif event.button == 3:
                    # Here we are placing the nodes down (first start then end by right clicking).
                    if not nodes:
                        pass
                    elif row >=0 and column >= 0:
                        if gridMaze[row][column] == ' ':
                            gridMaze[row][column] = nodes[0]
                            nodes.pop(0)
            except IndexError:
                pass
                
    pygame.display.update()

def drawGrid(blockSize, gridMaze):
    # Creating the grid, filling out squares if there is a wall or any other object
    for x in range(100, SCREEN_WIDTH-100, blockSize):
        for y in range(100, SCREEN_HEIGHT-100, blockSize):
            rect = pygame.Rect(x, y, blockSize, blockSize)
            if gridMaze[(y-100)//blockSize][(x-100)//blockSize] == ' ':
                color = (0, 0, 0)
            elif gridMaze[(y-100)//blockSize][(x-100)//blockSize] == '#': 
                color = (0, 0, 0)
                pygame.draw.rect(screen, color, rect)
            elif gridMaze[(y-100)//blockSize][(x-100)//blockSize] == 'S': 
                color = (0, 255, 0)
                pygame.draw.rect(screen, color, rect)
            elif gridMaze[(y-100)//blockSize][(x-100)//blockSize] == 'D':
                color = (255, 255, 0)
                pygame.draw.rect(screen, color, rect)
            elif gridMaze[(y-100)//blockSize][(x-100)//blockSize] == '*':
                color = (255, 0, 0)
                pygame.draw.rect(screen, color, rect)
            else:
                color = (0, 0, 255)
                pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (0, 0, 0), rect, 1)
def tutorialPage():
    global menu_state
    pygame.display.set_caption("Tutorial")
    exit_button = Button(150, 50, exit_img, 0.6)
    screen.fill("#f4f4f9")
    draw_text("How does the A* Pathfinding Visualizer actually work?", secondaryFont, text_col, SCREEN_WIDTH // 2, 100)
    lines = ['A* is a search algorithm that helps find the shortest path on a grid.', 'It knows roughly where the end goal is, making it faster than other search algorithms.', 'To do this, it needs to be able to calculate the distance from one point to another.']
    lineheight = bodyFont.get_linesize()
    for i in range(len(lines)):
        draw_text(lines[i], bodyFont, text_col, SCREEN_WIDTH // 2, 250 + i * lineheight)
    lines2 = ['One way to do this is by calculating the number of steps it takes to get from one point to another.', 'This can be done by adding the x-coordinates of the current position and subtracting it from the x-coordinates of the other point.', 'Then, just repeat this step for the y-coordinates and add them together. Make sure your answer is positive!', 'Now, we need to calculate the distance from the starting point to your current position (known as the G-Cost).', 'We must do the same for the end-goal (known as the H cost)', 'Once both of these are found, we simply add them up to get the F-Cost.']
    for i in range(len(lines2)):
        draw_text(lines2[i], bodyFont, text_col, SCREEN_WIDTH // 2, 350 + i * lineheight)
    lines3 = ['Now the algorithm works like this:', '1. Start at your position.', '2. Look at all the nearby spots you can move to.', '3. Calculate their F-costs. Pick the spot with the smallest F-cost to move to next.', '4. If two spots have the same F-cost, choose the one that looks closer to the goal. (Whichever one has a lower G-cost)', '5. Keep repeating until you reach the goal. That\'s it!']
    for i in range(len(lines3)):
        draw_text(lines3[i], bodyFont, text_col, SCREEN_WIDTH // 2, 500 + i * lineheight)
    if exit_button.draw():
        menu_state = "main"
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
    pygame.display.update()


main_menu()
pygame.quit()
