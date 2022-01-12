#
#   helperFunctions.py: Stores functions used on multiple modules of this extension
#

from __main__ import vtk, slicer
import numpy as np

def getIntersectionBetweenModelAnd1Plane(modelNode,planeNode,intersectionModel):
  plane = vtk.vtkPlane()
  origin = [0,0,0]
  normal = [0,0,0]
  planeNode.GetOrigin(origin)
  planeNode.GetNormal(normal)
  plane.SetOrigin(origin)
  plane.SetNormal(normal)

  cutter = vtk.vtkCutter()
  cutter.SetInputData(modelNode.GetPolyData())
  cutter.SetCutFunction(plane)
  cutter.Update()

  intersectionModel.SetAndObservePolyData(cutter.GetOutput())

def getNearestIntersectionBetweenModelAnd1Plane(modelNode,planeNode,intersectionModel):
  plane = vtk.vtkPlane()
  origin = [0,0,0]
  normal = [0,0,0]
  planeNode.GetOrigin(origin)
  planeNode.GetNormal(normal)
  plane.SetOrigin(origin)
  plane.SetNormal(normal)

  cutter = vtk.vtkCutter()
  cutter.SetInputData(modelNode.GetPolyData())
  cutter.SetCutFunction(plane)
  cutter.Update()

  connectivityFilter = vtk.vtkConnectivityFilter()
  connectivityFilter.SetInputData(cutter.GetOutput())
  connectivityFilter.SetClosestPoint(origin)
  connectivityFilter.SetExtractionModeToClosestPointRegion()
  connectivityFilter.Update()

  intersectionModel.SetAndObservePolyData(connectivityFilter.GetOutput())

def getIntersectionBetweenModelAnd1PlaneWithNormalAndOrigin_2(modelNode,normal,origin,intersectionModel):
  plane = vtk.vtkPlane()
  plane.SetOrigin(origin)
  plane.SetNormal(normal)

  cutter = vtk.vtkCutter()
  cutter.SetInputData(modelNode.GetPolyData())
  cutter.SetCutFunction(plane)
  cutter.Update()

  intersectionModel.SetAndObservePolyData(cutter.GetOutput())

def getIntersectionBetweenModelAnd1PlaneWithNormalAndOrigin(modelNode,normal,origin,intersectionModel):
  plane = vtk.vtkPlane()
  plane.SetOrigin(origin)
  plane.SetNormal(normal)

  clipper = vtk.vtkClipPolyData()
  clipper.SetInputData(modelNode.GetPolyData())
  clipper.SetClipFunction(plane)
  clipper.Update()

  intersectionModel.SetAndObservePolyData(clipper.GetOutput())

def getIntersectionBetweenModelAnd1TransformedPlane(modelNode,transform,planeNode,intersectionModel):
  plane = vtk.vtkPlane()
  origin = [0,0,0]
  normal = [0,0,0]
  transformedOrigin = [0,0,0]
  transformedNormal = [0,0,0]
  planeNode.GetOrigin(origin)
  planeNode.GetNormal(normal)
  transform.TransformPoint(origin,transformedOrigin)
  transform.TransformNormal(normal,transformedNormal)
  plane.SetOrigin(transformedOrigin)
  plane.SetNormal(transformedNormal)

  cutter = vtk.vtkCutter()
  cutter.SetInputData(modelNode.GetPolyData())
  cutter.SetCutFunction(plane)
  cutter.Update()

  intersectionModel.SetAndObservePolyData(cutter.GetOutput())

def getAverageNormalFromModel(model):
  pointsOfModel = slicer.util.arrayFromModelPoints(model)
  normalsOfModel = slicer.util.arrayFromModelPointData(model, 'Normals')
  modelMesh = model.GetMesh()

  averageNormal = np.array([0,0,0])
  for pointID in range(len(pointsOfModel)):
    normalAtPointID = normalsOfModel[pointID]
    averageNormal = averageNormal + normalAtPointID
  
  averageNormal = averageNormal/len(pointsOfModel)

  return averageNormal

def getAverageNormalFromModelPoint(model,point):
  normalsOfModel = slicer.util.arrayFromModelPointData(model, 'Normals')
  
  modelMesh = model.GetMesh()
  pointID = modelMesh.FindPoint(point)
  normalAtPointID = normalsOfModel[pointID]

  cylinder = vtk.vtkCylinder()
  cylinder.SetRadius(3)
  cylinder.SetCenter(point)
  cylinder.SetAxis(normalAtPointID)

  clipper = vtk.vtkClipPolyData()
  clipper.SetInputData(model.GetPolyData())
  clipper.InsideOutOn()
  clipper.SetClipFunction(cylinder)
  clipper.Update()

  connectivityFilter = vtk.vtkConnectivityFilter()
  connectivityFilter.SetInputData(clipper.GetOutput())
  connectivityFilter.SetClosestPoint(point)
  connectivityFilter.SetExtractionModeToClosestPointRegion()
  connectivityFilter.Update()

  cylinderIntersectionModel = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','cylinderIntersection')
  cylinderIntersectionModel.CreateDefaultDisplayNodes()
  cylinderIntersectionModel.SetAndObservePolyData(connectivityFilter.GetOutput())

  averageNormal = getAverageNormalFromModel(cylinderIntersectionModel)

  slicer.mrmlScene.RemoveNode(cylinderIntersectionModel)

  return averageNormal

def getCentroid(model):
  pd = model.GetPolyData().GetPoints().GetData()
  from vtk.util.numpy_support import vtk_to_numpy
  return np.average(vtk_to_numpy(pd), axis=0)

def getPointOfATwoPointsModelThatMakesLineDirectionSimilarToVector(twoPointsModel,vector,isPolydata=False):
  if not isPolydata:
    pointsData = twoPointsModel.GetPolyData().GetPoints().GetData()
  else:
    pointsData = twoPointsModel.GetPoints().GetData()
  from vtk.util.numpy_support import vtk_to_numpy

  points = vtk_to_numpy(pointsData)

  pointsVector = (points[1]-points[0])/np.linalg.norm(points[1]-points[0])

  if vtk.vtkMath.Dot(pointsVector, vector) > 0:
    return points[1]
  else:
    return points[0]

def getPointOfArrayNearestToTestPoint(arrayOfPoints, testPoint):
    pointsAndDistancesList = []
    for i in range(len(arrayOfPoints)):
      distance = np.linalg.norm(arrayOfPoints[i]-testPoint)
      pointsAndDistancesList.append([arrayOfPoints[i],i,distance])
    
    pointsAndDistancesList.sort(key = lambda item : item[2])
    return pointsAndDistancesList[0][0], pointsAndDistancesList[0][1]

def getPointOfAThatMakesLineDirectionSimilarToVectorAndItIsNearest(twoPointsModel,nearPoint,vector,isPolydata=False):
  if not isPolydata:
    pointsData = twoPointsModel.GetPolyData().GetPoints().GetData()
  else:
    pointsData = twoPointsModel.GetPoints().GetData()
  from vtk.util.numpy_support import vtk_to_numpy

  points = vtk_to_numpy(pointsData)

  if len(points) > 2:
    pointsAndDistancesList = []
    for i in range(len(points)):
      distance = np.linalg.norm(points[i]-nearPoint)
      pointsAndDistancesList.append([points[i],distance])
    
    pointsAndDistancesList.sort(key = lambda item : item[1])

    firstTwoPointsInCrescentDistanceOrder = []
    for i in range(0,2):
      firstTwoPointsInCrescentDistanceOrder.append(pointsAndDistancesList[i][0])
    
    points = firstTwoPointsInCrescentDistanceOrder

  pointsVector = (points[1]-points[0])/np.linalg.norm(points[1]-points[0])

  if vtk.vtkMath.Dot(pointsVector, vector) > 0:
    return points[1]
  else:
    return points[0]

def getLineNorm(line):
  lineStartPos = np.array([0,0,0])
  lineEndPos = np.array([0,0,0])
  line.GetNthControlPointPositionWorld(0, lineStartPos)
  line.GetNthControlPointPositionWorld(1, lineEndPos)
  return np.linalg.norm(lineEndPos-lineStartPos)

def createBox(X, Y, Z, name):
  miterBox = slicer.mrmlScene.CreateNodeByClass('vtkMRMLModelNode')
  miterBox.SetName(slicer.mrmlScene.GetUniqueNameByString(name))
  slicer.mrmlScene.AddNode(miterBox)
  miterBox.CreateDefaultDisplayNodes()
  miterBoxSource = vtk.vtkCubeSource()
  miterBoxSource.SetXLength(X)
  miterBoxSource.SetYLength(Y)
  miterBoxSource.SetZLength(Z)
  triangleFilter = vtk.vtkTriangleFilter()
  triangleFilter.SetInputConnection(miterBoxSource.GetOutputPort())
  triangleFilter.Update()
  miterBox.SetAndObservePolyData(triangleFilter.GetOutput())
  return miterBox

def createCylinder(name,R,H=50):
  cylinder = slicer.mrmlScene.CreateNodeByClass('vtkMRMLModelNode')
  cylinder.SetName(slicer.mrmlScene.GetUniqueNameByString(name))
  slicer.mrmlScene.AddNode(cylinder)
  cylinder.CreateDefaultDisplayNodes()
  lineSource = vtk.vtkLineSource()
  lineSource.SetPoint1(0, 0, H/2)
  lineSource.SetPoint2(0, 0, -H/2)
  tubeFilter = vtk.vtkTubeFilter()
  tubeFilter.SetInputConnection(lineSource.GetOutputPort())
  tubeFilter.SetRadius(R)
  tubeFilter.SetNumberOfSides(50)
  tubeFilter.CappingOn()
  tubeFilter.Update()
  cylinder.SetAndObservePolyData(tubeFilter.GetOutput())
  cylinder.SetAttribute('radius',str(R))
  cylinder.SetAttribute('height',str(H))
  return cylinder

def getBestFittingPlaneNormalFromPoints(points):
  """Code: https://math.stackexchange.com/questions/99299/best-fitting-plane-given-a-set-of-points"""
  #convert points to form [Xdata,Ydata,Zdata]
  points = np.array(points).T
  
  # now find the best-fitting plane for the test points
  # subtract out the centroid and take the SVD
  svd = np.linalg.svd(points - np.mean(points, axis=1, keepdims=True))

  # Extract the left singular vectors
  left = svd[0]

  # the corresponding left singular vector is the normal vector of the best-fitting plane
  return left[:, -1]

def digits(number, base=10):
    assert number >= 0
    if number == 0:
        return [0]
    l = []
    while number > 0:
        l.append(number % base)
        number = number // base
    return l

def distanceToSegment(point0, linePointA, linePointB):
  vectorAB = linePointB - linePointA
  vectorA0 = point0 - linePointA
  #
  if (vectorA0 @ vectorAB.T) <= 0.0:
    return np.linalg.norm(vectorA0)
  #
  vectorB0 = point0 - linePointB
  #
  if (vectorB0 @ vectorAB.T) >= 0.0:
    return np.linalg.norm(vectorB0)
  #
  cross = [0,0,0]
  vtk.vtkMath.Cross(vectorAB, vectorA0, cross)
  return np.linalg.norm(cross)/np.linalg.norm(vectorAB)

def distanceToSegmentAndSegmentLength(point0, linePointA, linePointB):
  vectorAB = linePointB - linePointA
  segmentABLength = np.linalg.norm(vectorAB)
  vectorA0 = point0 - linePointA
  #
  if (vectorA0 @ vectorAB.T) <= 0.0:
    return np.linalg.norm(vectorA0), segmentABLength
  #
  vectorB0 = point0 - linePointB
  #
  if (vectorB0 @ vectorAB.T) >= 0.0:
    return np.linalg.norm(vectorB0), segmentABLength
  #
  cross = [0,0,0]
  vtk.vtkMath.Cross(vectorAB, vectorA0, cross)
  distance = np.linalg.norm(cross)/segmentABLength
  return distance, segmentABLength

def validDistancesBetweenPointsOfIndices(indices,minimalDistance,pointToPointDistanceMatrix):
  for i in range(len(indices)-1):
    distanceOfPointToNextOne = pointToPointDistanceMatrix[indices[i]][indices[i+1]]
    if distanceOfPointToNextOne < minimalDistance:
      return False
  #
  return True

def calculateMetricsForPolyline(curvePoints,indices):
  indices_np = np.array(indices)
  polyLine = curvePoints[indices_np]
  #
  maxL1Distance = 1e5
  meanL1Distance = 0
  meanL2Distance = 0
  distances = []
  for i in range(len(curvePoints)):
    distanceOfPointToSegments = 1e5
    currentDistance = 0
    for j in range(len(polyLine)-1):
      currentDistance = distanceToSegment(curvePoints[i],polyLine[j],polyLine[j+1])
      if currentDistance < distanceOfPointToSegments:
        distanceOfPointToSegments = currentDistance
    #
    distances.append(distanceOfPointToSegments)
  #
  for i in range(len(curvePoints)):
    meanL1Distance += abs(distances[i])
    meanL2Distance += distances[i]**2
  #
  meanL1Distance = meanL1Distance/len(curvePoints)
  meanL2Distance = meanL2Distance/len(curvePoints)
  #
  distances.sort(reverse=True)
  maxL1Distance = distances[0]
  #
  return maxL1Distance, meanL1Distance, meanL2Distance

def calculateMetricsForPolylineV2(normalDistanceMetricsTensor,indices):
  maxL1Distance = 1e5
  meanL1Distance = 0
  meanL2Distance = 0
  distances = []
  for i in range(len(normalDistanceMetricsTensor)):
    distanceOfPointToSegments = 1e5
    currentDistance = 0
    for j in range(len(indices)-1):
      currentDistance = normalDistanceMetricsTensor[i][indices[j]][indices[j+1]-indices[j]]
      if currentDistance < distanceOfPointToSegments:
        distanceOfPointToSegments = currentDistance
    #
    distances.append(distanceOfPointToSegments)
  #
  for i in range(len(normalDistanceMetricsTensor)):
    meanL1Distance += abs(distances[i])
    meanL2Distance += distances[i]**2
  #
  meanL1Distance = meanL1Distance/len(normalDistanceMetricsTensor)
  meanL2Distance = meanL2Distance/len(normalDistanceMetricsTensor)
  #
  distances.sort(reverse=True)
  maxL1Distance = distances[0]
  #
  return maxL1Distance, meanL1Distance, meanL2Distance

def calculateMetricsForPolylineV3(normalDistanceMetricsTensor,indices):
  maxL1Distance = 1e5
  meanL1Distance = 0
  meanL2Distance = 0
  distances = []
  for i in range(len(normalDistanceMetricsTensor)):
    distanceOfPointToSegments = 1e5
    for j in range(len(indices)-1):
      if indices[j] <= i <= indices[j+1]:
        distanceOfPointToSegments = normalDistanceMetricsTensor[i][indices[j]][indices[j+1]]
    #
    distances.append(distanceOfPointToSegments)
  #
  for i in range(len(normalDistanceMetricsTensor)):
    meanL1Distance += abs(distances[i])
    meanL2Distance += distances[i]**2
  #
  meanL1Distance = meanL1Distance/len(normalDistanceMetricsTensor)
  meanL2Distance = meanL2Distance/len(normalDistanceMetricsTensor)
  #
  distances.sort(reverse=True)
  maxL1Distance = distances[0]
  #
  return maxL1Distance, meanL1Distance, meanL2Distance

def calculateMetricsForPolylineV4(normalDistanceMetricsTensor,indices):
  maxL1Distance = 1e5
  meanL1Distance = 0
  meanL2Distance = 0
  distances = []
  for j in range(len(indices)-1):
    for i in range(indices[j],indices[j+1]):
      distanceOfPointToSegments = normalDistanceMetricsTensor[i][indices[j]][indices[j+1]]
      distances.append(distanceOfPointToSegments)

  distanceOfPointToSegments = normalDistanceMetricsTensor[indices[-1]][indices[-2]][indices[-1]]
  distances.append(distanceOfPointToSegments)
  #
  for i in range(len(normalDistanceMetricsTensor)):
    meanL1Distance += abs(distances[i])
    meanL2Distance += distances[i]**2
  #
  meanL1Distance = meanL1Distance/len(normalDistanceMetricsTensor)
  meanL2Distance = meanL2Distance/len(normalDistanceMetricsTensor)
  #
  distances.sort(reverse=True)
  maxL1Distance = distances[0]
  #
  return maxL1Distance, meanL1Distance, meanL2Distance

def calculateMaxDistanceMetricForPolyline(normalDistanceMetricsTensor,indices):
  maxL1Distance = 0
  distances = []
  for j in range(len(indices)-1):
    for i in range(indices[j],indices[j+1]):
      distanceOfPointToSegments = normalDistanceMetricsTensor[i][indices[j]][indices[j+1]]
      if distanceOfPointToSegments > maxL1Distance:
        maxL1Distance = distanceOfPointToSegments

  distanceOfPointToSegments = normalDistanceMetricsTensor[indices[-1]][indices[-2]][indices[-1]]
  if distanceOfPointToSegments > maxL1Distance:
        maxL1Distance = distanceOfPointToSegments

  return maxL1Distance

def calculateMeanDistanceMetricForPolyline(normalDistanceMetricsTensor,indices):
  meanL1Distance = 0
  for j in range(len(indices)-1):
    for i in range(indices[j],indices[j+1]):
      distanceOfPointToSegments = normalDistanceMetricsTensor[i][indices[j]][indices[j+1]]
      meanL1Distance += distanceOfPointToSegments

  distanceOfPointToSegments = normalDistanceMetricsTensor[indices[-1]][indices[-2]][indices[-1]]
  meanL1Distance += distanceOfPointToSegments
  
  meanL1Distance = meanL1Distance/len(normalDistanceMetricsTensor)

  return meanL1Distance

def calculateNormalDistanceMetricsTensor(curvePoints):
  normalDistanceMetricsTensor = []
  for i in range(len(curvePoints)):
    normalDistanceMetricsMatrix = []
    for j in range(len(curvePoints)-1):
      normalDistanceMetricsVector = []
      for k in range(j,len(curvePoints)):
        distance = distanceToSegment(curvePoints[i],curvePoints[j],curvePoints[k])
        #normalDistanceMetricsVector.append([distance,i,j,k])
        normalDistanceMetricsVector.append(distance)
      normalDistanceMetricsMatrix.append(normalDistanceMetricsVector)
    normalDistanceMetricsTensor.append(normalDistanceMetricsMatrix)

  return normalDistanceMetricsTensor

def calculateNormalDistanceMetricsTensorAndNotMinimumDistancesVector(
    curvePoints,minimunDistanceBetweenSegments
  ):
  normalDistanceMetricsTensor = []
  indicesOfNotMinimumDistanceVector = []
  for i in range(len(curvePoints)):
    normalDistanceMetricsMatrix = []
    for j in range(len(curvePoints)-1):
      normalDistanceMetricsVector = []
      for k in range(len(curvePoints)):
        if k > j:
          distance,segmentLength = distanceToSegmentAndSegmentLength(curvePoints[i],curvePoints[j],curvePoints[k])
          if i == 0:
            if segmentLength < minimunDistanceBetweenSegments:
              indicesOfNotMinimumDistanceVector.append([j,k])
          
          normalDistanceMetricsVector.append(distance)
        else:
          normalDistanceMetricsVector.append(1e5)
      
      normalDistanceMetricsMatrix.append(normalDistanceMetricsVector)
    
    normalDistanceMetricsTensor.append(normalDistanceMetricsMatrix)

  return normalDistanceMetricsTensor, indicesOfNotMinimumDistanceVector

def getUnitNormalVectorsOfCurveNode(curveNode):
  a = slicer.util.arrayFromMarkupsCurvePoints(curveNode)
  
  dx_dt = np.gradient(a[:, 0])
  dy_dt = np.gradient(a[:, 1])
  dz_dt = np.gradient(a[:, 2])
  velocity = np.array([ [dx_dt[i], dy_dt[i], dz_dt[i]] for i in range(dx_dt.size)])

  ds_dt = np.sqrt(dx_dt * dx_dt + dy_dt * dy_dt + dz_dt * dz_dt)

  tangent = np.array([1/ds_dt] * 3).transpose() * velocity

  #check
  np.sqrt(tangent[:,0] * tangent[:,0] + tangent[:,1] * tangent[:,1] + tangent[:,2] * tangent[:,2])

  tangent_x = tangent[:, 0]
  tangent_y = tangent[:, 1]
  tangent_z = tangent[:, 2]

  deriv_tangent_x = np.gradient(tangent_x)
  deriv_tangent_y = np.gradient(tangent_y)
  deriv_tangent_z = np.gradient(tangent_z)

  dT_dt = np.array([ [deriv_tangent_x[i], deriv_tangent_y[i], deriv_tangent_z[i]] for i in range(deriv_tangent_x.size)])

  length_dT_dt = np.sqrt(deriv_tangent_x * deriv_tangent_x + deriv_tangent_y * deriv_tangent_y + deriv_tangent_z * deriv_tangent_z)

  normal = np.array([1/length_dT_dt] * 3).transpose() * dT_dt

  return normal

def generateIndicesArrayUsingHammingWeights(numberOfCurvePoints,numberOfSegments):
  import operator as op
  from functools import reduce

  def ncr(n, r):
      r = min(r, n-r)
      numer = reduce(op.mul, range(n, n-r, -1), 1)
      denom = reduce(op.mul, range(1, r+1), 1)
      return numer // denom  # or / in Python 2


  numberOfSameHammingWeightNumbers = ncr(numberOfCurvePoints-2,numberOfSegments-1)
  sameHammingWeightNumber = 0
  sameHammingWeightNumbersList = [0]*numberOfSameHammingWeightNumbers
  #initialize it
  for i in range(numberOfSegments-1):
    sameHammingWeightNumber += 2**i

  sameHammingWeightNumbersList[0] = sameHammingWeightNumber

  for i in range(1,numberOfSameHammingWeightNumbers):
    #calculate next one:
    c = sameHammingWeightNumber & -sameHammingWeightNumber
    r = sameHammingWeightNumber + c
    sameHammingWeightNumber = int(((r^sameHammingWeightNumber) >> 2) / c) | r
    #
    #and save it
    sameHammingWeightNumbersList[i] = sameHammingWeightNumber

  sameHammingWeightNumbers_array = np.array(sameHammingWeightNumbersList)
 
  def unpackbits(x, num_bits):
      if np.issubdtype(x.dtype, np.floating):
          raise ValueError("numpy data type needs to be int-like")
      xshape = list(x.shape)
      x = x.reshape([-1, 1])
      mask = 2**np.arange(num_bits, dtype=x.dtype).reshape([1, num_bits])
      myresult = np.zeros(xshape + [num_bits],dtype=np.int8)
      for i in range(myresult.shape[0]):
        tempResult = (x[i] & mask).astype(bool)
        myresult[i] = tempResult
      return myresult

  binaryMask = unpackbits(sameHammingWeightNumbers_array,numberOfCurvePoints-2)

  generatorArray = np.array(list(range(1, numberOfCurvePoints-1)),dtype=np.int8)

  middleIndicesOfCurve = np.ones([numberOfSameHammingWeightNumbers,numberOfSegments-1],dtype=np.int8)
  for i in range(middleIndicesOfCurve.shape[0]):
    middleIndicesOfCurve[i] = generatorArray[binaryMask[i]==1]

  appendStart = np.pad(middleIndicesOfCurve, [(0, 0), (1, 0)], mode='constant', constant_values=0)
  appendEnd = np.pad(appendStart, [(0, 0), (0, 1)], mode='constant', constant_values=(numberOfCurvePoints-1))
  
  return appendEnd

def generateFilteredIndicesArrayUsingHammingWeightsAndNotMinimumDistanceArray(
    numberOfCurvePoints,numberOfSegments,notMinimumDistanceIndicesVector
):
  import operator as op
  from functools import reduce

  def ncr(n, r):
      r = min(r, n-r)
      numer = reduce(op.mul, range(n, n-r, -1), 1)
      denom = reduce(op.mul, range(1, r+1), 1)
      return numer // denom  # or / in Python 2


  numberOfSameHammingWeightNumbers = ncr(numberOfCurvePoints-2,numberOfSegments-1)
  sameHammingWeightNumber = 0
  sameHammingWeightNumbersList = [0]*numberOfSameHammingWeightNumbers
  #initialize it
  for i in range(numberOfSegments-1):
    sameHammingWeightNumber += 2**i

  sameHammingWeightNumbersList[0] = sameHammingWeightNumber

  for i in range(1,numberOfSameHammingWeightNumbers):
    #calculate next one:
    c = sameHammingWeightNumber & -sameHammingWeightNumber
    r = sameHammingWeightNumber + c
    sameHammingWeightNumber = int(((r^sameHammingWeightNumber) >> 2) / c) | r
    #
    #and save it
    sameHammingWeightNumbersList[i] = sameHammingWeightNumber

  sameHammingWeightNumbers_array = np.array(sameHammingWeightNumbersList)

  sameHammingWeightNumbers_array = (sameHammingWeightNumbers_array << 1) + 1 + 2**(numberOfCurvePoints-1)
  
  #for i in range(100):
  #  print(sameHammingWeightNumbers_array[i])

  for i in range(len(notMinimumDistanceIndicesVector)):
    indicesToFilterConvertedToDecimal = (
      2**notMinimumDistanceIndicesVector[i][0] + 2**notMinimumDistanceIndicesVector[i][1]
      )
    sameHammingWeightNumbers_array = (
      sameHammingWeightNumbers_array[
        np.logical_not((sameHammingWeightNumbers_array & indicesToFilterConvertedToDecimal) == indicesToFilterConvertedToDecimal)
      ]
    )
    #print(notMinimumDistanceIndicesVector[i][0],notMinimumDistanceIndicesVector[i][1])

  filteredSameHammingWeightNumbers_array = sameHammingWeightNumbers_array
  #print('filtered array length')
  #print(len(filteredSameHammingWeightNumbers_array))
  #for i in range(len(filteredSameHammingWeightNumbers_array)):
  #  print(filteredSameHammingWeightNumbers_array[i])

  def unpackbits(x, num_bits):
      if np.issubdtype(x.dtype, np.floating):
          raise ValueError("numpy data type needs to be int-like")
      xshape = list(x.shape)
      x = x.reshape([-1, 1])
      mask = 2**np.arange(num_bits, dtype=x.dtype).reshape([1, num_bits])
      myresult = np.zeros(xshape + [num_bits],dtype=np.int8)
      for i in range(myresult.shape[0]):
        tempResult = (x[i] & mask).astype(bool)
        myresult[i] = tempResult
      return myresult

  binaryMask = unpackbits(filteredSameHammingWeightNumbers_array,numberOfCurvePoints)

  #for i in range(100):
  #  print(binaryMask[i]==1)
  #print('separator')
  generatorArray = np.array(list(range(0, numberOfCurvePoints)),dtype=np.int8)

  indicesOfCurve = np.ones([(filteredSameHammingWeightNumbers_array.shape[0]),numberOfSegments+1],dtype=np.int8)
  for i in range(indicesOfCurve.shape[0]):
    #print(generatorArray[binaryMask[i]==1])
    indicesOfCurve[i] = generatorArray[binaryMask[i]==1]

  return indicesOfCurve

def generateIndicesArrayRecursivelyUsingNonMinimumDistanceRanges(
  numberOfPointsOfCurve,numberOfSegments,notMinimumDistancesRangesVector_np,
  notMinimumDistanceRangesVectorReversed_np
):

  indicesArray = []
  global oneIndicesArray
  oneIndicesArray = [0,]

  nextPossiblePointBackwardList = []
  for rootCrescentLevel in range(numberOfSegments,2-1,-1):
    nextPossiblePointBackward = getNextPossiblePointBackward(
      numberOfPointsOfCurve-1,
      numberOfSegments - (numberOfSegments-rootCrescentLevel+1),
      notMinimumDistanceRangesVectorReversed_np
    )
    nextPossiblePointBackwardList.append(nextPossiblePointBackward)
  
  def recursiveIndicesArrayCreationFunction(index,rootCrescentLevel):
    global oneIndicesArray
    nextPossiblePointForward = getNextPossiblePointForward(
      index,
      1,
      notMinimumDistancesRangesVector_np
    )
    nextPossiblePointBackward = nextPossiblePointBackwardList[
      numberOfSegments-rootCrescentLevel
    ]
    #print(nextPossiblePointForward,nextPossiblePointBackward)
    if rootCrescentLevel == 2:
      for i in range(nextPossiblePointForward,nextPossiblePointBackward+1):
        oneIndicesArray.append(i)
        oneIndicesArray.append(numberOfPointsOfCurve-1)
        indicesArray.append(oneIndicesArray)
        oneIndicesArray = oneIndicesArray[0:-2]
      return
    
    for i in range(nextPossiblePointForward,nextPossiblePointBackward+1):
      oneIndicesArray.append(i)
      recursiveIndicesArrayCreationFunction(i,rootCrescentLevel-1)
      oneIndicesArray = oneIndicesArray[0:-1]

  recursiveIndicesArrayCreationFunction(0,numberOfSegments)

  return indicesArray

def getNextPossiblePointForward(curvePointIndex,order,notMinimumDistancesRangesVector):
  result = curvePointIndex
  for i in range(order):
    if result >= notMinimumDistancesRangesVector[-1][0]:
      return notMinimumDistancesRangesVector[-1][1]
    currentCurvePointIndex = notMinimumDistancesRangesVector[result][1]
    result = currentCurvePointIndex + 1
  return result

def getNextPossiblePointBackward(curvePointIndex,order,notMinimumDistanceRangesVectorReversed):
  result = curvePointIndex - notMinimumDistanceRangesVectorReversed[0][1]
  currentCurvePointIndex = curvePointIndex
  for i in range(order):
    if currentCurvePointIndex <= notMinimumDistanceRangesVectorReversed[0][1]:
      return 0
    currentCurvePointIndex = notMinimumDistanceRangesVectorReversed[result][0] -1
    result = currentCurvePointIndex - notMinimumDistanceRangesVectorReversed[0][1]
  return currentCurvePointIndex

def makePointToPointDistancesMatrix(points0,points1):
  point0ToPoint1DistancesMatrix = []
  
  for i in range(len(points0)):
    point0ToPoint1DistancesVector = []
    
    for j in range(len(points1)):
      point0ToPoint1DistancesVector.append([np.linalg.norm(points0[i]-points1[j]),i,j])
    
    point0ToPoint1DistancesMatrix.append(point0ToPoint1DistancesVector)
  
  return point0ToPoint1DistancesMatrix

def getListOfPointPairsOfLeastDistanceGivenAMetricsMatrix(metricsMatrix,points0,points1):
  #get every point pair of least distance
  pointPairsList = []
  
  for i in range(len(metricsMatrix)):
    metricsMatrix[i].sort(key = lambda item : item[0])
    
    point0index = metricsMatrix[i][0][1]
    point1index = metricsMatrix[i][0][2]
    
    pointPair = [points0[point0index],points1[point1index]]
    pointPairsList.append(pointPair)

  return pointPairsList

def getPointPairFromListWithMostSimilarDirection(pointPairsList,direction):
  maximumDotProduct = 0
  maximumDotProductPointPair = []

  for i in range(len(pointPairsList)):
    pointPairDirectionLine = (
      (pointPairsList[i][1]-pointPairsList[i][0])
      /np.linalg.norm(pointPairsList[i][1]-pointPairsList[i][0])
    )

    dotProduct = vtk.vtkMath.Dot(pointPairDirectionLine, direction)
    if  dotProduct > maximumDotProduct:
      maximumDotProduct = dotProduct
      maximumDotProductPointPair = pointPairsList[i]
  
  return maximumDotProductPointPair

def rotation_from_matrix(matrix):
  """Return rotation angle and axis from rotation matrix.

  >>> angle = (random.random() - 0.5) * (2*math.pi)
  >>> direc = np.random.random(3) - 0.5
  >>> point = np.random.random(3) - 0.5
  >>> R0 = rotation_matrix(angle, direc, point)
  >>> angle, direc, point = rotation_from_matrix(R0)
  >>> R1 = rotation_matrix(angle, direc, point)
  >>> is_same_transform(R0, R1)
  True

  """
  import math
  R = np.array(matrix, dtype=np.float64, copy=False)
  R33 = R[:3, :3]
  # direction: unit eigenvector of R33 corresponding to eigenvalue of 1
  l, W = np.linalg.eig(R33.T)
  i = np.where(abs(np.real(l) - 1.0) < 1e-8)[0]
  if not len(i):
      raise ValueError("no unit eigenvector corresponding to eigenvalue 1")
  direction = np.real(W[:, i[-1]]).squeeze()
  # point: unit eigenvector of R33 corresponding to eigenvalue of 1
  l, Q = np.linalg.eig(R)
  i = np.where(abs(np.real(l) - 1.0) < 1e-8)[0]
  if not len(i):
      raise ValueError("no unit eigenvector corresponding to eigenvalue 1")
  point = np.real(Q[:, i[-1]]).squeeze()
  point /= point[3]
  # rotation angle depending on direction
  cosa = (np.trace(R33) - 1.0) / 2.0
  if abs(direction[2]) > 1e-8:
      sina = (R[1, 0] + (cosa - 1.0) * direction[0] * direction[1]) / direction[2]
  elif abs(direction[1]) > 1e-8:
      sina = (R[0, 2] + (cosa - 1.0) * direction[0] * direction[2]) / direction[1]
  else:
      sina = (R[2, 1] + (cosa - 1.0) * direction[1] * direction[2]) / direction[0]
  angle = math.atan2(sina, cosa)
  return angle, direction, point