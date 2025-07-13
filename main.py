import tkinter as tk
import math
import numpy as np
import random


# Section 0 ------------------ Settings and Constants

window = tk.Tk()

#gridsize = 11
gridwidth = 25 # number of squares across
gridheight = 25 # number of squares high
square_size = 20 # pixels
solutioncomplexity=0.14
showsolution=True
wrapvertical=False
wraphorizontal=False
splitprobability=0.1
mazepathattempts=65001


mazestart=np.array([0,0])
mazeend=np.array([4,4])

horizontalwrap=False
verticalwrap=False



def makeadjacencymatrix(gridheight, gridwidth): # make adjacency matrix
    adjacencymatrix=[]
    
    for k in range(gridheight*gridwidth):
        adjacencymatrix.append([0]*(gridwidth*gridheight)) # zeros matrix
    
    for i in range(gridheight):
        for j in range(gridwidth):
            #in each [i,j] row, attach neighbour columns
            if (j):
                #left neighbour
                adjacencymatrix[i*gridwidth+j][i*gridwidth+j-1]=1
            elif(horizontalwrap):
                adjacencymatrix[i*gridwidth+j][(i+1)*gridwidth-1]=1
            if (j!=gridwidth-1):
                #right neighbour
                adjacencymatrix[i*gridwidth+j][i*gridwidth+j+1]=1
            elif(horizontalwrap):
                adjacencymatrix[i*gridwidth+j][(i-1)*gridwidth+j+1]=1
            if(i!=0):
                #top neighbour
                adjacencymatrix[i*gridwidth+j][(i-1)*gridwidth+j]=1
            elif(verticalwrap):
                adjacencymatrix[i*gridwidth+j][(i-1)*gridwidth+j]=1
            if(i!=gridheight-1):
                #bottom neighbour
                adjacencymatrix[i*gridwidth+j][(i+1)*gridwidth+j]=1
            elif(verticalwrap):
                adjacencymatrix[i*gridwidth+j][((i+1)*gridwidth+j)%(gridwidth*gridheight)]=1
    
    return adjacencymatrix


def disconnectfromadjacencymatrix(k, adjacencymatrix):#disconnect from adjacency matrix
    for line in adjacencymatrix:
        line[k]=0#takek away all k's connections
    adjacencymatrix[k]=[0]*(gridwidth*gridheight)#disconnect everything from k
    return



def taxicab(s,f, gridwidth=gridwidth):#min distance from s to f
    if ((not horizontalwrap) and (not verticalwrap)):
        return abs((s%gridwidth)-(f%gridwidth))+abs((s//gridwidth)-(f//gridwidth))
    distfleft=abs((s%gridwidth)-(f%gridwidth-gridwidth))+abs((s//gridwidth)-(f//gridwidth))
    distfright=abs((s%gridwidth)-(f%gridwidth+gridwidth))+abs((s//gridwidth)-(f//gridwidth))
    distfup=abs((s%gridwidth)-(f%gridwidth))+abs((s//gridwidth)-(f//gridwidth-gridheight))
    distfdown=abs((s%gridwidth)-(f%gridwidth))+abs((s//gridwidth)-(f//gridwidth+gridheight))
    dist=abs((s%gridwidth)-(f%gridwidth))+abs((s//gridwidth)-(f//gridwidth))
    #make all 5 possible distances
    #return the min of the ones that are currently available
    if(not horizontalwrap):
        return min([dist, distfup, distfdown])
    elif(not verticalwrap):
        return min([dist, distfleft, distfright])
    else:
        return min([dist, distfup, distfdown, distfleft, distfright])


def coordsify(k):#change cell index to coords
    return(k//gridwidth, k%gridwidth)
    
    
def indexify(i,j):#change cell coords to index
    return(i*gridwidth+j)



def makelistofneighbours(k, adjacencymatrix):#build region containing cell k
    checkedlist=[k]
    checkedallneighbours=False
    while(not checkedallneighbours):
        print("checked ", checkedlist)
        checkedallneighbours=True
        for i in checkedlist:
            for j in getneighbours(i, adjacencymatrix):
                if(not j in checkedlist):
                    checkedallneighbours=False
                    checkedlist.append(j)
    return checkedlist


def getsubregions(region, splittingpath, adjacencymatrix):#generate list of all regions adjacent to splitting path
    subregions=[]
    for k in region:
        if all(k not in subregion for subregion in subregions):#k isnt already in subregions' regions
            subregions.append(makelistofneighbours(k, adjacencymatrix))#generate k's region
    return subregions





def getadjacents(k):#generate list of all adjacent cells (not necessarily connected)
    adjacents=[]
    if(not k<gridwidth):
        adjacents.append(k-gridwidth)
    if(not k%gridwidth==0):
        adjacents.append(k-1)
    if(not (k+1)%gridwidth==0):
        adjacents.append(k+1)
    if(not k+gridwidth<gridwidth*gridheight):
        adjacents.append(k+gridwidth)
    return adjacents
    

def getneighbours(k,adjacencymatrix):# generate list of all k's connected neighbours from adjacency matrix
    neighbours=[]
    for i in range(len(adjacencymatrix[k])):
        if(adjacencymatrix[k][i]):
            neighbours.append(i)
    return neighbours
    
    

steps=0# global var that helps bail on mazepaths if it's taking to long



def multitrymakepaths(finish, path, adjacencymatrix, maxdepth=math.floor(gridwidth*gridheight*solutioncomplexity), neighbourchecks=2, mindepth=0):
    #loop that reruns mazepaths after mazepathattempts number of tries

    global steps
    while True:
        newpath = makepaths(finish, path, adjacencymatrix, maxdepth=maxdepth, neighbourchecks=neighbourchecks, mindepth=mindepth)
        if newpath:
            return newpath
        else:
            steps=0


def makepaths(finish, path, adjacencymatrix, maxdepth=math.floor(gridwidth*gridheight*solutioncomplexity), neighbourchecks=2, mindepth=0):
    #itterative mazepath generator

    global steps
    steps+=1
    '''
    if (steps%1000==0):
        print(steps)
    '''    
    if (steps > mazepathattempts):#bail if steps is over mazepathattempts
        return []
    neighbours=getneighbours(path[-1], adjacencymatrix)
    random.shuffle(neighbours)#put neighbours in random order
    j=0
    for i in neighbours:#jump to the neighbours
        j += 1
        if (not i in path and j<neighbourchecks+1):#only check the neighbour if its in the first neighbourchecks entries
            if (i == finish):#if weve found finish just return with the end appended
                if (len(path)>mindepth):
                    return path + [i]
                
            elif(maxdepth >= taxicab(i, finish)):#if you havent found finish and its still possible to reach it
                #run makepaths with this neighbour
                pathtry=makepaths(finish, path+[i], adjacencymatrix, maxdepth-1, mindepth=mindepth)
                if(pathtry):
                   #this implies pathry succeeded in finding finish
                    return pathtry
    return []#if you get to here you went through all the neighbours
    



def flatten(xss):
    return [x for xs in xss for x in xs]#makes a list of lists just one list

def regionslice(region, bounds, adjacencymatrix, mazepaths, finish=None):
    #runs the multitrymakepaths to split region and itterates to the next subregionregions
    if(bounds):
        print("bounds:")
        randombound=flatten(bounds)
        random.shuffle(randombound)
        print(randombound)
        startpath=[]
        i=-1
        while(not startpath):
            i=i+1
            print(randombound[i])
            for a in getadjacents(randombound[i]):
                
                if(a in region):
                    startpath=[randombound[i],a]
                    #print("madeit to break")
                    break
                    
    else:
        startpath=[indexify(mazestart[0],mazestart[1])]
    if(finish is None):
        newregion=region.copy()
        newregion.remove(startpath[-1])
        if(not newregion):
            mazepaths.append(startpath)
            return mazepaths
        else:
            f=random.choice(newregion)
    else:
        f=finish
    print(coordsify(startpath[0]), coordsify(f))
    global steps
    steps=0
    if(bounds):
        splittingpath=multitrymakepaths(f, startpath, am, neighbourchecks=3)
    else:
        splittingpath=multitrymakepaths(f, startpath, am, neighbourchecks=3,maxdepth=math.floor(gridwidth*gridheight*solutioncomplexity), mindepth=math.floor(gridwidth*gridheight*solutioncomplexity*0.7))
    print(splittingpath)
    #modify adjacency matrix
    for k in splittingpath:
        disconnectfromadjacencymatrix(k, adjacencymatrix)
    
    mazepaths.append(splittingpath)
    print(mazepaths)
    newregion=region
    
    for element in splittingpath:
        if element in region: # Check to avoid ValueError if element not found
            region.remove(element)
    
    subregions=getsubregions(region, splittingpath, adjacencymatrix)
    print("subregions: ",subregions)
    for subregion in subregions:
        print("slicing region: ", subregion)
        regionslice(subregion, bounds+[splittingpath], adjacencymatrix, mazepaths)
    return mazepaths  



# Section 2 -------------------Convert to coords

def converttocoords(mazepaths):

    coordmazepaths=[]
    for path in mazepaths:
        coordpath=[]
        for k in path:
            coordpath.append(np.array(coordsify(k)))
        coordmazepaths.append(coordpath)
    #print(coordpath)
    return coordmazepaths






# Section 3 ------------------ Display Maze 

#print a matrix
'''
matrix = [[0 for _ in range(gridwidth)] for _ in range(gridheight)]#------tempdisplay

for i in range(len(matrix)):
    for j in range(len(matrix[i])):
        if indexify(i,j) in sol:
            matrix[i][j] = 8

for line in matrix:
    print(line)
'''   


def hopcell(cell,direction):
    
    newcell=np.array([-20, -20])
    
    if(direction==0):
        newcell=cell
    elif(direction == 1):
        newcell=cell + np.array([-gridheight,0])
    elif(direction == 2):
        newcell=cell + np.array([0,gridwidth])
    elif(direction == 3):
        newcell=cell + np.array([gridheight,0])
    elif(direction == 4):
        newcell=cell + np.array([0,-gridwidth])
    return newcell
    
def hopdistances(cell1, cell2):
    distance0= np.linalg.norm(cell2-cell1)
    
    distance1= np.linalg.norm(hopcell(cell2, 1)-cell1)
    distance3= np.linalg.norm(hopcell(cell2, 3)-cell1)
    
    distance2= np.linalg.norm(hopcell(cell2, 2)-cell1)
    distance4= np.linalg.norm(hopcell(cell2, 4)-cell1)
    if(wrapvertical and wraphorizontal):
        return [distance0, distance1, distance2, distance3, distance4]
    elif(wrapvertical):
        return [distance0, distance1, gridheight*gridwidth, distance3, gridheight*gridwidth]
    elif(wraphorizontal):
        return [distance0, gridheight*gridwidth, distance2, gridheight*gridwidth, distance4]
    else:
        return [distance0, gridheight*gridwidth, gridheight*gridwidth, gridheight*gridwidth, gridheight*gridwidth]
   
   

def makecellwalls(mazepaths):#build the cell walls matrix

    cellwalls = [[[1, 2, 3, 4] for _ in range(gridwidth)] for _ in range(gridheight)]
    
    for path in mazepaths:
        for i in range(len(path[1:])):
            distances=hopdistances(path[i], path[i+1])
            mindistanceindex= distances.index(min(distances))
            direction=hopcell(path[i+1],mindistanceindex)-path[i]
            if(np.array_equal(direction, np.array([0,1]))):#if path goes right
                (cellwalls[path[i][0]][path[i][1]]).remove(2)#remove right
                (cellwalls[path[i+1][0]][path[i+1][1]]).remove(4)#remove left
                
            elif(np.array_equal(direction, np.array([0,-1]))):#if path goes left
                (cellwalls[path[i][0]][path[i][1]]).remove(4)#remove left
                (cellwalls[path[i+1][0]][path[i+1][1]]).remove(2)#remove right
                
            elif(np.array_equal(direction, np.array([1,0]))):#if path goes down
                (cellwalls[path[i][0]][path[i][1]]).remove(3)#remove bottom
                (cellwalls[path[i+1][0]][path[i+1][1]]).remove(1)#remove top
                
            elif(np.array_equal(direction, np.array([-1,0]))):#if path goes up
                (cellwalls[path[i][0]][path[i][1]]).remove(1)#remove top
                (cellwalls[path[i+1][0]][path[i+1][1]]).remove(3)#remove bottom
                
            else:
                print("sumthins buggin - path jumps more than 1 manhatten")
                print(path[i],path[i+1])
                quit()
                
    return cellwalls
    
def showcellwalls(cellwalls, solution): #display walls
    for row in range(gridheight):
        for col in range(gridwidth):
            
            '''
            if((mazestart[0]==row and mazestart[1]==col) or (mazeend[0]==row and mazeend[1]==col)):
                if(row==0):
                    (cellwalls[row][col]).remove(1)#remove top    
                if(col==0):
                    (cellwalls[row][col]).remove(4)#remove left
                if(row==gridheight-1):
                    (cellwalls[row][col]).remove(3)#remove bottom
                if(col==gridwidth-1):
                    (cellwalls[row][col]).remove(2)#remove right
            '''
            
             # Add label showing (row, col)
            cell = np.array([row, col])
            
            # Create frame for each grid cell (no border)
            frame = tk.Frame(window, width=square_size, height=square_size, bg="lightgray", borderwidth=0, highlightthickness=0, relief="solid")
            frame.grid(row=row, column=col, padx=0, pady=0, sticky="nsew")
    
            # Create canvas inside the frame (no border)
            canvas = tk.Canvas(frame, width=square_size, height=square_size, bg="white", bd=0, highlightthickness=0)
            canvas.grid(row=0, column=0, sticky="nsew")
    
            # Check if the product of row and column is even or odd
            if 1 in cellwalls[row][col]:  # Even product: draw horizontal line
                canvas.create_line(0+2, 0+2, square_size-2, 0+2, fill="black")
                
            if 2 in cellwalls[row][col]:
                canvas.create_line(square_size-2, 0+2, square_size-2, square_size-2, fill="black")
                
            if 3 in cellwalls[row][col]:
                canvas.create_line(0+2, square_size-2, square_size-2, square_size-2, fill="black")
                
            if 4 in cellwalls[row][col]:
                canvas.create_line(0+2, 0+2, 0+2, square_size-2, fill="black")
            
            
            
            
            if(np.array_equal(cell, mazestart)):
                label_text = "S"
                label = tk.Label(frame, text=label_text, bg="white", font=("Arial", round(square_size/4)))
                label.place(relx=0.5, rely=0.5, anchor="center")
            elif(np.array_equal(cell, mazeend)):
                label_text = "F"
                label = tk.Label(frame, text=label_text, bg="white", font=("Arial", round(square_size/4)))
                label.place(relx=0.5, rely=0.5, anchor="center")
            elif (any(np.array_equal(cell, p) for p in solution[1:-1]) and showsolution):
                label_text = f"{row},{col}"
                label = tk.Label(frame, text=label_text, bg="white", font=("Arial", round(square_size/8)))
                label.place(relx=0.5, rely=0.5, anchor="center")
     
                    

# Make the grid cells expand with the window resizing
for r in range(gridheight):
    window.grid_rowconfigure(r, weight=1)
for c in range(gridwidth):
    window.grid_columnconfigure(c, weight=1)



# Section 4 -------------------Execute



am=makeadjacencymatrix(gridheight,gridwidth) 
#print()
allcells=makelistofneighbours(0,am)

#show only one path generation
'''
#sol=multitrymakepaths(indexify(mazeend[0],mazeend[1]), [indexify(mazestart[0],mazestart[1])], am, maxdepth=math.floor(gridwidth*gridheight*solutioncomplexity), mindepth=math.floor(gridwidth*gridheight*solutioncomplexity*0.7))
#mazepathscoords=converttocoords([sol])
#cellwalls= makecellwalls(mazepathscoords)
#showcellwalls(cellwalls, mazepathscoords[0])
'''

#generate maze
mazepaths=regionslice(allcells, [], am, [], finish=indexify(mazeend[0],mazeend[1]))
mazepathscoords=converttocoords(mazepaths)
cellwalls= makecellwalls(mazepathscoords)
showcellwalls(cellwalls, mazepathscoords[0])


window.mainloop()