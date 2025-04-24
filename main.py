import cv2
import numpy
import os
import random
from datetime import datetime

sample_Files = os.listdir("mapSamples")

samples = []
for filename in sample_Files:
    sample = cv2.imread(f"mapSamples/{filename}",cv2.IMREAD_GRAYSCALE)
    samples.append(sample)
    if (sample[0,:].sum() != sample[:,0].sum()) or (sample[9,:].sum() != sample[:,9].sum()):
        samples.append(cv2.rotate(sample,cv2.ROTATE_90_CLOCKWISE))
        samples.append(cv2.rotate(sample,cv2.ROTATE_90_COUNTERCLOCKWISE))
        samples.append(cv2.rotate(sample,cv2.ROTATE_180))

    if (sample[0,:].sum() != sample[9,:].sum()):
        samples.append(cv2.flip(sample,0))
        if (sample[0,:].sum() != sample[:,0].sum()) or (sample[9,:].sum() != sample[:,9].sum()):
            samples.append(cv2.rotate(cv2.flip(sample,0),cv2.ROTATE_90_CLOCKWISE))
            samples.append(cv2.rotate(cv2.flip(sample,0),cv2.ROTATE_90_COUNTERCLOCKWISE))

    if (sample[:,0].sum() != sample[:,9].sum()):
        samples.append(cv2.flip(sample,1))
        if (sample[0,:].sum() != sample[:,0].sum()) or (sample[9,:].sum() != sample[:,9].sum()):
            samples.append(cv2.rotate(cv2.flip(sample,1),cv2.ROTATE_90_CLOCKWISE))
            samples.append(cv2.rotate(cv2.flip(sample,1),cv2.ROTATE_90_COUNTERCLOCKWISE))
        


map = []
for i in range(10):
    row = []
    for j in range(10):
        row.append(samples[0])
    map.append(row)

covered = numpy.zeros((10,10))

def getFittingTile(i,j):
    for candidate in samples:
        if i == 0 and candidate[0,:].sum() > 0: continue #check top row
        if i == 9 and candidate[9,:].sum() > 0: continue #check bottom row

        if j == 0 and candidate[:,0].sum() > 0: continue #check left column
        if j == 9 and candidate[:,9].sum() > 0: continue #check right column

        if j > 0:
            leftTile = map[i][j-1]
            leftTileRightColumn = leftTile[:,9].tostring()
            candidateLeftColumn = candidate[:,0].tostring()
            if not (leftTileRightColumn == candidateLeftColumn): continue

        if i > 0:
            upperTile = map[i-1][j]
            upperTileBottomRow = upperTile[9,:].tostring()
            candidateTopRow = candidate[0,:].tostring()
            if not (upperTileBottomRow == candidateTopRow): continue
        return candidate
    return samples[0]

def getTile(i,j):
    count = 0
    while True:
        count+=1
        if count > 1000: return getFittingTile(i,j)
        candidate = random.choice(samples)
        if i == 0 and candidate[0,:].sum() > 0: continue #check top row
        if i == 9 and candidate[9,:].sum() > 0: continue #check bottom row

        if j == 0 and candidate[:,0].sum() > 0: continue #check left column
        if j == 9 and candidate[:,9].sum() > 0: continue #check right column

        if j > 0:
            leftTile = map[i][j-1]
            leftTileRightColumn = leftTile[:,9].tostring()
            candidateLeftColumn = candidate[:,0].tostring()
            if not (leftTileRightColumn == candidateLeftColumn): continue

        if i > 0:
            upperTile = map[i-1][j]
            upperTileBottomRow = upperTile[9,:].tostring()
            candidateTopRow = candidate[0,:].tostring()
            if not (upperTileBottomRow == candidateTopRow): continue
        return candidate

for i in range(10):
    for j in range(10):
        map[i][j] = getTile(i,j)
        covered[i,j] = 1
        os.system("cls")
        print(covered)

preview = numpy.zeros((100,100))
for i in range(10):
    for j in range(10):
        preview[i*10:i*10+10,j*10:j*10+10] = map[i][j]

genDate = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
cv2.imwrite(f"previews/preview{genDate}.png",preview)

tile = cv2.imread("tiles/tile.png")
wall = cv2.imread("tiles/wall.png")
corner = cv2.imread("tiles/corner.png")

finalMap = numpy.zeros((1600,1600,3))
for i in range(100):
    for j in range(100):
        if(preview[i,j] > 0):
            finalMap[i*16:i*16+16,j*16:j*16+16] = tile
        else:
            if i > 0  and preview[i-1,j] >0 : finalMap[i*16:i*16+16,j*16:j*16+16] += cv2.rotate(wall,cv2.ROTATE_90_CLOCKWISE) /2
            if i < 99 and preview[i+1,j] >0 : finalMap[i*16:i*16+16,j*16:j*16+16] += cv2.rotate(wall,cv2.ROTATE_90_COUNTERCLOCKWISE) /2
            if j > 0 and preview[i,j-1] >0 : finalMap[i*16:i*16+16,j*16:j*16+16] += wall /2
            if j < 99 and preview[i,j+1] >0 : finalMap[i*16:i*16+16,j*16:j*16+16] += cv2.flip(wall,1) /2

            if i > 0 and j > 0 and preview[i-1,j-1] > 0 and preview[i-1,j] == 0 and preview[i,j-1] == 0: finalMap[i*16:i*16+16,j*16:j*16+16] += corner
            if i > 0 and j < 99 and preview[i-1,j+1] > 0 and preview[i-1,j] == 0 and preview[i,j+1] == 0: finalMap[i*16:i*16+16,j*16:j*16+16] += cv2.rotate(corner, cv2.ROTATE_90_CLOCKWISE)
            if i <99 and j < 99 and preview[i+1,j+1] > 0 and preview[i+1, j] == 0 and preview[i,j+1] == 0: finalMap[i*16:i*16+16,j*16:j*16+16] += cv2.rotate(corner,cv2.ROTATE_180)
            if i <99 and j > 0 and preview[i+1,j-1] > 0 and preview[i+1,j]==0 and preview[i,j-1]==0: finalMap[i*16:i*16+16,j*16:j*16+16] += cv2.rotate(corner, cv2.ROTATE_90_COUNTERCLOCKWISE)
cv2.imwrite(f"finalMaps/finalMap{genDate}.png",finalMap)