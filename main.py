import cv2
import numpy
import os
import random
from datetime import datetime

sample_Files = os.listdir("mapSamples")

SAMPLE_SIZE = 10
MAP_WIDTH = 10
MAP_HEIGHT = 10

SAMPLE_LAST_INDEX = SAMPLE_SIZE -1

samples = []
for filename in sample_Files:
    sample = cv2.imread(f"mapSamples/{filename}",cv2.IMREAD_GRAYSCALE).astype("uint8")
    
    if sample.shape[0] != SAMPLE_SIZE: continue
    if sample.shape[1] != SAMPLE_SIZE: continue

    samples.append(sample)
    
    top = sample[0,:].tostring()
    botton = sample[SAMPLE_LAST_INDEX,:].tostring()
    left = sample[:,0].tostring()
    right = sample[:,SAMPLE_LAST_INDEX].tostring()

    if (top != left) or (top != right) or (botton != left) or (botton != right):
        samples.append(cv2.rotate(sample,cv2.ROTATE_90_CLOCKWISE))
        samples.append(cv2.rotate(sample,cv2.ROTATE_90_COUNTERCLOCKWISE))
    
    if (top != botton):
        samples.append(cv2.rotate(sample,cv2.ROTATE_180))
        samples.append(cv2.flip(sample,0))
        if (top != left) or (top != right) or (botton != left) or (botton != right):
            samples.append(cv2.rotate(cv2.flip(sample,0),cv2.ROTATE_90_CLOCKWISE))
            samples.append(cv2.rotate(cv2.flip(sample,0),cv2.ROTATE_90_COUNTERCLOCKWISE))

    if (left != right):
        samples.append(cv2.rotate(sample,cv2.ROTATE_180))
        samples.append(cv2.flip(sample,1))
        if (top != left) or (top != right) or (botton != left) or (botton != right):
            samples.append(cv2.rotate(cv2.flip(sample,1),cv2.ROTATE_90_CLOCKWISE))
            samples.append(cv2.rotate(cv2.flip(sample,1),cv2.ROTATE_90_COUNTERCLOCKWISE))

map = []
for i in range(MAP_HEIGHT):
    row = []
    for j in range(MAP_WIDTH):
        row.append(samples[0])
    map.append(row)

def getFittingTile(i,j):
    for candidate in samples[1:]:
        if i == 0 and candidate[0,:].sum() > 0: continue #check top row
        if i == MAP_HEIGHT-1 and candidate[SAMPLE_LAST_INDEX,:].sum() > 0: continue #check bottom row

        if j == 0 and candidate[:,0].sum() > 0: continue #check left column
        if j == MAP_WIDTH-1 and candidate[:,SAMPLE_LAST_INDEX].sum() > 0: continue #check right column

        # if (j > 0 or i > 0) and (candidate[:,0].sum() + candidate[0,:].sum() == 0): continue

        if j > 0:
            leftTile = map[i][j-1]
            leftTile_right = leftTile[:,SAMPLE_LAST_INDEX].tostring()
            candidate_left = candidate[:,0].tostring()
            if (leftTile_right != candidate_left): continue

        if i > 0:
            upperTile = map[i-1][j]
            upperTile_bottom = upperTile[SAMPLE_LAST_INDEX,:].tostring()
            candidate_top = candidate[0,:].tostring()
            if (upperTile_bottom != candidate_top): continue
        return candidate
    return samples[0]

def getTile(i,j):
    count = 0
    while True:
        count+=1
        if count > 1000: return getFittingTile(i,j)
        candidate = random.choice(samples)
        if i == 0 and candidate[0,:].sum() > 0: continue #check top row
        if i == MAP_HEIGHT-1 and candidate[SAMPLE_LAST_INDEX,:].sum() > 0: continue #check bottom row

        if j == 0 and candidate[:,0].sum() > 0: continue #check left column
        if j == MAP_WIDTH-1 and candidate[:,SAMPLE_LAST_INDEX].sum() > 0: continue #check right column

        # if (j > 0 or i > 0) and (candidate[:,0].sum() + candidate[0,:].sum() == 0): continue

        if j > 0:
            leftTile = map[i][j-1]
            leftTile_right = leftTile[:,SAMPLE_LAST_INDEX].tostring()
            candidate_left = candidate[:,0].tostring()
            if not (leftTile_right == candidate_left): continue

        if i > 0:
            upperTile = map[i-1][j]
            upperTile_bottom = upperTile[SAMPLE_LAST_INDEX,:].tostring()
            candidate_top = candidate[0,:].tostring()
            if not (upperTile_bottom == candidate_top): continue
        return candidate

covered = numpy.zeros((MAP_HEIGHT,MAP_WIDTH))
for i in range(MAP_HEIGHT):
    for j in range(MAP_WIDTH):
        map[i][j] = getTile(i,j)
        covered[i,j] = 1
        os.system("cls")
        print(f"Generating map from samples: ({(covered.sum() / (MAP_HEIGHT*MAP_WIDTH)) * 100}% completed)")
        print("Map Coverage Table of the generation process:")
        print(covered)

connected = numpy.zeros((MAP_HEIGHT,MAP_WIDTH))
connected[(int(MAP_HEIGHT/2)),int(MAP_WIDTH/2)] = 1

scanForConnections = True
print("scaning connected tiles...")
while scanForConnections:
    changes = 0
    for i in range(MAP_HEIGHT):
        for j in range(MAP_WIDTH):
            currentTile = map[i][j]
            top = currentTile[0,:]
            botton = currentTile[SAMPLE_LAST_INDEX,:]
            left = currentTile[:,0]
            right = currentTile[:,SAMPLE_LAST_INDEX]
            if i > 0:
                upperTile = map[i-1][j]
                upperTile_bottom = upperTile[SAMPLE_LAST_INDEX,:]
                if (connected[i,j] == 0 and connected[i-1,j]==1 and upperTile_bottom.sum() + top.sum() >0):
                    connected[i,j] = 1
                    changes+=1
            if j > 0:
                leftTile = map[i][j-1]
                leftTile_right = leftTile[:,SAMPLE_LAST_INDEX]
                if (connected[i,j] == 0 and connected[i,j-1]==1) and leftTile_right.sum() + left.sum() > 0:
                    connected[i,j] = 1
                    changes+=1
            if i < MAP_HEIGHT-1:
                lowerTile = map[i+1][j]
                lowerTile_top = lowerTile[0,:]
                if (connected[i,j] == 0 and connected[i+1,j]==1) and lowerTile_top.sum() + botton.sum() > 0:
                    connected[i,j] = 1
                    changes+=1
            if j < MAP_WIDTH-1:
                rightTile = map[i][j+1]
                rightTile_left = rightTile[:,0]
                if(connected[i,j] == 0 and connected[i,j+1] == 1) and rightTile_left.sum() + right.sum() > 0:
                    connected[i,j]=1
                    changes+=1
    if changes == 0:
        scanForConnections=False
    print(f"{connected.sum()} tiles connected")

print("Connection matrix: ")
print(connected)
print("proceeding into cleaning unconnected tiles")
for i in range(MAP_HEIGHT):
    for j in range(MAP_WIDTH):
        if connected[i,j] == 0: map[i][j] = samples[0]

print("proceeding into creating map preview")

PREVIEW_HEIGT = MAP_HEIGHT * SAMPLE_SIZE
PREVIEW_WIDTH = MAP_WIDTH * SAMPLE_SIZE

preview = numpy.zeros((PREVIEW_HEIGT, PREVIEW_WIDTH),dtype="uint8")
for i in range(MAP_HEIGHT):
    for j in range(MAP_WIDTH):
        y0 = i * SAMPLE_SIZE
        y1 = (i+1) * SAMPLE_SIZE
        x0 = j * SAMPLE_SIZE
        x1 = (j+1) * SAMPLE_SIZE
        preview[y0:y1 , x0:x1] = map[i][j]

genDate = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
cv2.imwrite(f"previews/preview{genDate}.png",preview)

tile = cv2.imread("tiles/tile.png")
wall = cv2.imread("tiles/wall.png")
corner = cv2.imread("tiles/corner.png")

TILE_HEIGHT = tile.shape[0]
TILE_WIDTH =  tile.shape[1]

RENDER_HEIGTH = MAP_HEIGHT * SAMPLE_SIZE * TILE_HEIGHT
RENDER_WIDTH = MAP_WIDTH * SAMPLE_SIZE * TILE_WIDTH

finalMap = numpy.zeros((RENDER_HEIGTH,RENDER_WIDTH,3))

for i in range(PREVIEW_HEIGT):
    for j in range(PREVIEW_WIDTH):
        
        y0 = i * TILE_HEIGHT
        y1 = (i+1) * TILE_HEIGHT
        x0 = j * TILE_WIDTH
        x1 = (j+1) * TILE_WIDTH

        if(preview[i,j] > 0):
            finalMap[y0:y1, x0:x1] = tile
        else:
            if i > 0  and preview[i-1,j] > 0 :
                finalMap[y0:y1, x0:x1] += cv2.rotate(wall,cv2.ROTATE_90_CLOCKWISE) /2
            if i < PREVIEW_HEIGT-1 and preview[i+1,j] > 0 :
                finalMap[y0:y1, x0:x1] += cv2.rotate(wall,cv2.ROTATE_90_COUNTERCLOCKWISE) /2
            if j > 0 and preview[i,j-1] > 0 :
                finalMap[y0:y1, x0:x1] += wall /2
            if j < PREVIEW_WIDTH-1 and preview[i,j+1] > 0 :
                finalMap[y0:y1, x0:x1] += cv2.flip(wall,1) /2

            if i > 0 and j > 0 and preview[i-1,j-1] > 0 and preview[i-1,j] == 0 and preview[i,j-1] == 0:
                finalMap[y0:y1, x0:x1] += corner
            if i > 0 and j < PREVIEW_WIDTH-1 and preview[i-1,j+1] > 0 and preview[i-1,j] == 0 and preview[i,j+1] == 0:
                finalMap[y0:y1, x0:x1] += cv2.rotate(corner, cv2.ROTATE_90_CLOCKWISE)
            if i <PREVIEW_HEIGT-1 and j < PREVIEW_WIDTH-1 and preview[i+1,j+1] > 0 and preview[i+1, j] == 0 and preview[i,j+1] == 0:
                finalMap[y0:y1, x0:x1] += cv2.rotate(corner,cv2.ROTATE_180)
            if i <PREVIEW_HEIGT-1 and j > 0 and preview[i+1,j-1] > 0 and preview[i+1,j]==0 and preview[i,j-1]==0:
                finalMap[y0:y1, x0:x1] += cv2.rotate(corner, cv2.ROTATE_90_COUNTERCLOCKWISE)

cv2.imwrite(f"finalMaps/finalMap{genDate}.png",finalMap)