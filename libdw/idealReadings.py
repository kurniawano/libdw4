"""
Utility for computing ideal sonar readings
"""

from . import util
from . import sonarDist
from . import soarWorld

######################################################################
###      Compute ideal readings
######################################################################

def computeIdealReadings(worldPath, x_min, x_max, y, numStates, numObs):
    """
    :param worldPath: string naming file to read the world description from
    :param x_min: minimum x coordinate for center of robot
    :param x_max: maximum x coordinate for center of robot
    :param y: constant y coordinate for center of robot
    :param numStates: number of discrete states into which to divide
     the range of x coordinates
    :param numObs: number of discrete observations into which to
     divide the range of good sonar observations, between 0 and ``goodSonarRange``
    :returns: list of ``numStates`` values, each of which is between 0
     and ``numObs-1``, which lists the ideal discretized sonar reading
     that the robot would receive if it were at the midpoint of each of
     the x bins.
    """
    # read obstacles from the map
    world = soarWorld.SoarWorld(worldPath)

    xStep = (x_max - x_min) / float(numStates)
    readings = []
    # Start in the middle of the first box
    x = x_min + (xStep / 2.0)  
    for ix in range(numStates):
        # left-hand sonar reading assuming we're heading to the right
        readings.append(discreteSonarValue(\
                            idealSonarReading(util.Pose(x, y, 0),
                                              sonarDist.sonarPoses[0], world),
                            numObs))
        x = x + xStep
    return readings
            
def idealSonarReading(robotPose, sensorPose, world):
    """
    :param robotPose: ``util.Pose`` representing pose of robot in world
    :param sensorPose: c{util.Pose} representing pose of sonar sensor
     with respect to the robot
    :param world: ``soarWorld.SoarWorld`` representing obstacles in the world
    :returns: length of ideal sonar reading;  if the distance is
     longer than ``sonarDist.sonarMax`` or there is no hit at all, then
     ``sonarDist.sonarMax`` is returned. 
    """
    sensorOriginPoint = sonarDist.sonarHit(0, sensorPose, robotPose)
    sonarRay = util.LineSeg(sensorOriginPoint,
                            sonarDist.sonarHit(sonarDist.sonarMax,
                                               sensorPose, robotPose))
    hits = [(seg.intersection(sonarRay), seg) for seg in world.wallSegs]
    distances = [sensorOriginPoint.distance(hit) for (hit,seg) in hits if hit]
    distances.append(sonarDist.sonarMax)
    return min(distances)

def discreteSonar(d, numBins):
    """
    :param d: value of a sonar reading
    :param numBins: number of bins into which to divide the interval
     between 0 and ``sonardist.sonarMax``
    :returns: number of the bin into which this sonar reading should
     fall;  any reading greater than or equal to c{sonarDist.sonarMax}
     is put into bin ``numBins - 1``.
    """
    binSize = sonarDist.sonarMax / numBins
    return min(int(d / binSize), numBins - 1)

# Old name, defined here in case somebody depends on it...
discreteSonarValue = discreteSonar
