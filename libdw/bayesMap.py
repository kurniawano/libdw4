from . import dist
from . import util
from . import colors
from . import ssm
from . import seFast
from . import dynamicGridMap

falsePos = 0.3
falseNeg = 0.3

initPOcc = 0.1
occThreshold = 0.8

#!
# Define the stochastic state-machine model for a given cell here.

# Observation model:  P(obs | state)
def oGivenS(s):
#!    pass    
    if s == 'empty':
        return dist.DDist({'hit': falsePos, 'free': 1 - falsePos})
    else: # occ
        return dist.DDist({'hit': 1 - falseNeg, 'free': falseNeg})
#!
# Transition model: P(newState | s | a)
def uGivenAS(a):
#!     pass    
    return lambda s: dist.DDist({s: 1.0})
#!
#!cellSSM = None   # Your code here
cellSSM = ssm.StochasticSM(dist.DDist({'occ': initPOcc, 'empty': 1 - initPOcc}),
                           uGivenAS, oGivenS)

#!

class BayesGridMap(dynamicGridMap.DynamicGridMap):

    def squareColor(self, xxx_todo_changeme):
        (xIndex, yIndex) = xxx_todo_changeme
        p = self.occProb((xIndex, yIndex))
        if self.robotCanOccupy((xIndex,yIndex)):
            return colors.probToMapColor(p, colors.greenHue)
        elif self.occupied((xIndex, yIndex)):
            return 'black'
        else:
            return 'red'
        
    def occProb(self, xxx_todo_changeme1):
#!        pass        
        (xIndex, yIndex) = xxx_todo_changeme1
        return self.grid[xIndex][yIndex].state.prob('occ')
#!
    def makeStartingGrid(self):
#!        pass        
        def makeEstimator(ix, iy):
            m = seFast.StateEstimator(cellSSM)
            m.start()
            return m
        return util.make2DArrayFill(self.xN, self.yN, makeEstimator)
#!
    def setCell(self, xxx_todo_changeme2):
#!        pass        
        
        (xIndex, yIndex) = xxx_todo_changeme2
        self.grid[xIndex][yIndex].step(('hit', None))
        self.drawSquare((xIndex, yIndex))
#!        
    def clearCell(self, xxx_todo_changeme3):
#!        pass        
        (xIndex, yIndex) = xxx_todo_changeme3
        self.grid[xIndex][yIndex].step(('free', None))
        self.drawSquare((xIndex, yIndex))
#!
    def occupied(self, xxx_todo_changeme4):
#!        pass        
        (xIndex, yIndex) = xxx_todo_changeme4
        return self.occProb((xIndex, yIndex)) > occThreshold

    def explored(self, xxx_todo_changeme5):
        (xIndex, yIndex) = xxx_todo_changeme5
        p = self.grid[xIndex][yIndex].state.prob('occ')
        return p > 0.8 or p < 0.1

    def cost(self, xxx_todo_changeme6):
        (xIndex, yIndex) = xxx_todo_changeme6
        cost = 0
        for dx in range(0, self.growRadiusInCells + 1):
            for dy in range(0, self.growRadiusInCells + 1):
                xPlus = util.clip(xIndex+dx, 0, self.xN-1)
                xMinus = util.clip(xIndex-dx, 0, self.xN-1)
                yPlus = util.clip(yIndex+dy, 0, self.yN-1)
                yMinus = util.clip(yIndex-dy, 0, self.yN-1)
                cost = max(cost, self.cost1((xPlus, yPlus)),
                           self.cost1((xPlus,yMinus)),
                           self.cost1((xMinus, yPlus)),
                           self.cost1((xMinus, yMinus)))
        return cost

    def cost1(self, xxx_todo_changeme7):
        (xIndex, yIndex) = xxx_todo_changeme7
        return self.grid[xIndex][yIndex].state.prob('occ')
#!

mostlyHits = [('hit', None), ('hit', None), ('hit', None), ('free', None)]
mostlyFree = [('free', None), ('free', None), ('free', None), ('hit', None)]

def testCellDynamics(cellSSM, input):
    se = seFast.StateEstimator(cellSSM)
    return se.transduce(input)

