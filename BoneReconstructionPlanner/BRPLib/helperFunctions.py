#
#   helperFunctions.py: Stores functions used on multiple modules of this extension
#

from __main__ import vtk, slicer, qt
import numpy as np
import logging

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

def getFurthestIntersectionBetweenModelAnd1Plane(modelNode,planeNode,intersectionModel):
  origin = [0,0,0]
  normal = [0,0,0]
  planeNode.GetOrigin(origin)
  planeNode.GetNormal(normal)
  getIntersectionBetweenModelAnd1PlaneWithNormalAndOrigin(modelNode, normal, origin, intersectionModel)

  furthestRegionPD = extractFurthestRegion(intersectionModel.GetPolyData(),origin)

  intersectionModel.SetAndObservePolyData(furthestRegionPD)

def extractFurthestRegion(polyData, point):
    # Label all connected regions
    connectivity = vtk.vtkConnectivityFilter()
    connectivity.SetInputData(polyData)
    connectivity.SetExtractionModeToAllRegions()
    connectivity.ColorRegionsOn()
    connectivity.Update()

    numRegions = connectivity.GetNumberOfExtractedRegions()

    maxDist = -1
    furthestRegionId = 0

    for regionId in range(numRegions):
        # Extract each region individually
        regionExtractor = vtk.vtkConnectivityFilter()
        regionExtractor.SetInputData(polyData)
        regionExtractor.SetExtractionModeToSpecifiedRegions()
        regionExtractor.AddSpecifiedRegion(regionId)
        regionExtractor.Update()

        # Convert to polydata (vtkConnectivityFilter outputs vtkUnstructuredGrid)
        surfaceFilter = vtk.vtkDataSetSurfaceFilter()
        surfaceFilter.SetInputConnection(regionExtractor.GetOutputPort())
        surfaceFilter.Update()

        regionPolyData = surfaceFilter.GetOutput()
        if regionPolyData.GetNumberOfPoints() == 0:
            continue

        # Find closest point in this region to the reference point
        pointLocator = vtk.vtkPointLocator()
        pointLocator.SetDataSet(regionPolyData)
        pointLocator.BuildLocator()
        closestPointId = pointLocator.FindClosestPoint(point)
        closestPoint = regionPolyData.GetPoint(closestPointId)

        import math
        dist = math.sqrt(vtk.vtkMath.Distance2BetweenPoints(point, closestPoint))

        if dist > maxDist:
            maxDist = dist
            furthestRegionId = regionId

    # Extract the furthest region
    finalExtractor = vtk.vtkConnectivityFilter()
    finalExtractor.SetInputData(polyData)
    finalExtractor.SetExtractionModeToSpecifiedRegions()
    finalExtractor.AddSpecifiedRegion(furthestRegionId)
    finalExtractor.Update()

    toPolyData = vtk.vtkDataSetSurfaceFilter()
    toPolyData.SetInputConnection(finalExtractor.GetOutputPort())
    toPolyData.Update()

    return toPolyData.GetOutput()

def getIntersectionBetweenModelAnd1PlaneWithNormalAndOrigin(modelNode,normal,origin,intersectionModel):
  plane = vtk.vtkPlane()
  plane.SetOrigin(origin)
  plane.SetNormal(normal)

  cutter = vtk.vtkCutter()
  cutter.SetInputData(modelNode.GetPolyData())
  cutter.SetCutFunction(plane)
  cutter.Update()

  intersectionModel.SetAndObservePolyData(cutter.GetOutput())

def getCutHalfBetweenModelAnd1PlaneWithNormalAndOrigin(modelNode,normal,origin,intersectionModel):
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
  planeNode.GetOrigin(origin)
  planeNode.GetNormal(normal)

  if transform.IsA("vtkMatrix4x4"):
    transformedOrigin = [0,0,0,0]
    transformedNormal = [0,0,0,0]
    transform.MultiplyPoint(np.append(origin,1.0),transformedOrigin)
    transformedOrigin = transformedOrigin[0:3]
    transform.MultiplyPoint(np.append(normal,0.0),transformedNormal)
    transformedNormal = transformedNormal[0:3]
  else:
    transformedOrigin = [0,0,0]
    transformedNormal = [0,0,0]
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
  if model.GetMesh().GetPoints() is None:
    return None
  
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
  cylinderIntersectionModel.SetAndObservePolyData(
    calculateNormals(connectivityFilter.GetOutput())
  )

  averageNormal = getAverageNormalFromModel(cylinderIntersectionModel)

  slicer.mrmlScene.RemoveNode(cylinderIntersectionModel)

  if averageNormal is None:
    return None

  if vtk.vtkMath.Dot(averageNormal, normalAtPointID) < 0:
    averageNormal *= -1

  return averageNormal

def getAverageNormalFromModelPoint2(model,point):
  cropRadius = 2
  geodesicCropRadius = cropRadius*2

  normalsOfModel = slicer.util.arrayFromModelPointData(model, 'Normals')
  
  modelMesh = model.GetMesh()
  pointID = modelMesh.FindPoint(point)
  normalAtPointID = normalsOfModel[pointID]

  geodesicCroppedModel = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','geodesicCroppedModel')
  geodesicCroppedModel.CreateDefaultDisplayNodes()

  auxiliarFiducial = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode','auxiliarGeodesicCropFiducial')
  auxiliarFiducial.CreateDefaultDisplayNodes()
  auxiliarFiducial.AddControlPoint(point)

  dynamicModelerNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLDynamicModelerNode")
  dynamicModelerNode.SetToolName("Select by points")
  dynamicModelerNode.SetNodeReferenceID("SelectByPoints.InputModel", model.GetID())
  dynamicModelerNode.SetNodeReferenceID("SelectByPoints.InputFiducial", auxiliarFiducial.GetID())
  dynamicModelerNode.SetNodeReferenceID("SelectByPoints.SelectedFacesModel", geodesicCroppedModel.GetID())
  dynamicModelerNode.SetAttribute("SelectionDistance",str(geodesicCropRadius))
  dynamicModelerNode.SetAttribute("SelectionAlgorithm","SphereRadius")

  slicer.modules.dynamicmodeler.logic().RunDynamicModelerTool(dynamicModelerNode)

  cylinder = vtk.vtkCylinder()
  cylinder.SetRadius(cropRadius)
  cylinder.SetCenter(point)
  cylinder.SetAxis(normalAtPointID)

  clipper = vtk.vtkClipPolyData()
  clipper.SetInputData(geodesicCroppedModel.GetPolyData())
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
  cylinderIntersectionModel.SetAndObservePolyData(
    calculateNormals(connectivityFilter.GetOutput())
  )

  averageNormal = getAverageNormalFromModel(cylinderIntersectionModel)

  slicer.mrmlScene.RemoveNode(geodesicCroppedModel)
  slicer.mrmlScene.RemoveNode(auxiliarFiducial)
  slicer.mrmlScene.RemoveNode(dynamicModelerNode)
  slicer.mrmlScene.RemoveNode(cylinderIntersectionModel)

  if averageNormal is None:
    return None

  if vtk.vtkMath.Dot(averageNormal, normalAtPointID) < 0:
    averageNormal *= -1

  return averageNormal


def getClosestModelPointToPosition(model,position):
  pointsLocator = vtk.vtkPointLocator()
  pointsLocator.SetDataSet(model.GetPolyData())
  pointsLocator.BuildLocator()
  
  pointIDOfClosestPoint = pointsLocator.FindClosestPoint(position)
  result = np.array(model.GetPolyData().GetPoints().GetPoint(pointIDOfClosestPoint))
  return result

def getCentroid(model):
  try:
    pd = model.GetPolyData().GetPoints().GetData()
  except:
    return None
  from vtk.util.numpy_support import vtk_to_numpy
  return np.average(vtk_to_numpy(pd), axis=0)

def getPointOfATwoPointsModelThatMakesLineDirectionSimilarToVector(twoPointsModel,vector):
  pointsData = twoPointsModel.GetPolyData().GetPoints().GetData()
  from vtk.util.numpy_support import vtk_to_numpy

  points = vtk_to_numpy(pointsData)

  pointsVector = (points[1]-points[0])/np.linalg.norm(points[1]-points[0])

  if vtk.vtkMath.Dot(pointsVector, vector) > 0:
    return points[1]
  else:
    return points[0]

def nearestPointOverLineWithTheVectorDirection(pointsModel, vector):
  """
  Given array1 and array2 of 3D points in numpy, 
  create a matrix from substracting every ith point in array1 
  to every jth point in array2
  

  """
  pointsData = pointsModel.GetPolyData().GetPoints().GetData()
  from vtk.util.numpy_support import vtk_to_numpy
  points = vtk_to_numpy(pointsData)

  # result[i, j] = array1[i] - array2[j], shape: (N, M, 3)
  result = points[:, np.newaxis, :] - points[np.newaxis, :, :]
  
  unitVector = vector/np.linalg.norm(vector)
  
  dots = np.dot(result, unitVector)

  # find the ith and jth that maximize the dot product
  maxDotIndex = np.unravel_index(np.argmax(dots), dots.shape)
  # return points[maxDotIndex[0]], points[maxDotIndex[1]]

  if vtk.vtkMath.Dot(points[maxDotIndex[0]], unitVector) > 0:
    return points[maxDotIndex[0]]
  else:
    return points[maxDotIndex[1]]

def projectBoxesOverFibulaLine(boxesModelsList, fibulaLineMarkup):
  #fibulaLine = vtk.vtkLine()
  startPoint = np.zeros(3)
  endPoint = np.zeros(3)
  fibulaLineMarkup.GetNthControlPointPosition(0, startPoint)
  fibulaLineMarkup.GetNthControlPointPosition(1, endPoint)
  fibulaLineDirection = endPoint - startPoint
  fibulaLineDirection = fibulaLineDirection/np.linalg.norm(fibulaLineDirection)
  fibulaLineCenter = (startPoint + endPoint)/2

  startingBox = boxesModelsList[0]
  endingBox = boxesModelsList[-1]

  projectedPointsOfStartingBoxPoints = projectPolyDataPointsOntoLine(
    startingBox.GetPolyData(), 
    startPoint, 
    endPoint
  )
  projectedPointsOfEndingBoxPoints = projectPolyDataPointsOntoLine(
    endingBox.GetPolyData(), 
    startPoint, 
    endPoint
  )

  return projectedPointsOfStartingBoxPoints, projectedPointsOfEndingBoxPoints

def getMostDistantPoints(points1, points2):
  # using math to get the two most distant points between projectedPointsOfStartingBoxPoints and projectedPointsOfEndingBoxPoints
  maxDistance = -1
  for i in range(points1.GetNumberOfPoints()):
    pointOfStartingBox = points1.GetPoint(i)
    for j in range(points2.GetNumberOfPoints()):
      pointOfEndingBox = points2.GetPoint(j)
      distance = np.linalg.norm(np.array(pointOfStartingBox)-np.array(pointOfEndingBox))
      if distance > maxDistance:
        maxDistance = distance
        furthestPointOfStartingBox = pointOfStartingBox
        furthestPointOfEndingBox = pointOfEndingBox 
  
  return furthestPointOfStartingBox, furthestPointOfEndingBox

def projectPolyDataPointsOntoLine(polyData, p1, p2):
  """
  Projects each point of polyData onto the infinite line defined by p1->p2.
  Returns a new vtkPoints with the projected positions.
  """
  projectedPoints = vtk.vtkPoints()
  projectedPoints.SetNumberOfPoints(polyData.GetNumberOfPoints())

  p1, p2 = np.array(p1), np.array(p2)
  d = p2 - p1
  for i in range(polyData.GetNumberOfPoints()):
      p = np.array(polyData.GetPoint(i))
      t = np.dot(p - p1, d) / np.dot(d, d)   # no clamping
      projectedPoints.SetPoint(i, p1 + t * d)

  return projectedPoints

def getLineNorm(line):
  lineStartPos = np.array([0,0,0])
  lineEndPos = np.array([0,0,0])
  line.GetNthControlPointPosition(0, lineStartPos)
  line.GetNthControlPointPosition(1, lineEndPos)
  return np.linalg.norm(lineEndPos-lineStartPos)

def createBox(X, Y, Z, name, defaultVisible = True, highResolution = True):
  miterBox = slicer.mrmlScene.CreateNodeByClass('vtkMRMLModelNode')
  miterBox.SetName(slicer.mrmlScene.GetUniqueNameByString(name))
  slicer.mrmlScene.AddNode(miterBox)
  miterBox.CreateDefaultDisplayNodes()
  miterBox.GetDisplayNode().SetVisibility(defaultVisible)
  miterBox.GetDisplayNode().SetInterpolation(slicer.vtkMRMLModelDisplayNode.FlatInterpolation)
  #
  miterBoxSource = vtk.vtkCubeSource()
  miterBoxSource.SetXLength(X)
  miterBoxSource.SetYLength(Y)
  miterBoxSource.SetZLength(Z)
  triangleFilter = vtk.vtkTriangleFilter()
  triangleFilter.SetInputConnection(miterBoxSource.GetOutputPort())
  #
  maximumEdgeLengthMm = 1
  adaptiveSubdivisionFilter = vtk.vtkAdaptiveSubdivisionFilter()
  adaptiveSubdivisionFilter.SetInputConnection(triangleFilter.GetOutputPort())
  adaptiveSubdivisionFilter.SetMaximumEdgeLength(maximumEdgeLengthMm)
  adaptiveSubdivisionFilter.SetMaximumTriangleArea(adaptiveSubdivisionFilter.GetMaximumTriangleAreaMaxValue()) # set to infinity
  #
  if highResolution:
    miterBox.SetPolyDataConnection(adaptiveSubdivisionFilter.GetOutputPort())
  else:
    miterBox.SetPolyDataConnection(triangleFilter.GetOutputPort())

  rectanglet = slicer.mrmlScene.CreateNodeByClass('vtkMRMLModelNode')
  rectanglet.SetName(slicer.mrmlScene.GetUniqueNameByString(name + "_rectanglet"))
  slicer.mrmlScene.AddNode(rectanglet)
  rectanglet.CreateDefaultDisplayNodes()
  rectanglet.GetDisplayNode().SetVisibility(False)
  plane = vtk.vtkPlaneSource()
  plane.SetXResolution(1)
  plane.SetYResolution(1)
  plane.SetOrigin(-X/2, -Y/2, -Z/2) # first corner
  plane.SetPoint1(X/2, -Y/2, -Z/2) # second corner in x direction
  plane.SetPoint2(-X/2, -Y/2, Z/2) # third corner in z direction
  plane.Update()
  rectanglet.SetAndObservePolyData(plane.GetOutput())
  
  return miterBox, rectanglet

def createCylinder(name,R,H=50):
  cylinder = slicer.mrmlScene.CreateNodeByClass('vtkMRMLModelNode')
  cylinder.SetName(slicer.mrmlScene.GetUniqueNameByString(name))
  slicer.mrmlScene.AddNode(cylinder)
  cylinder.CreateDefaultDisplayNodes()
  #
  lineSource = vtk.vtkLineSource()
  lineSource.SetPoint1(0, 0, H/2)
  lineSource.SetPoint2(0, 0, -H/2)
  lineSource.SetUseRegularRefinement(True)
  lineSource.SetResolution(H)
  #
  tubeFilter = vtk.vtkTubeFilter()
  tubeFilter.SetInputConnection(lineSource.GetOutputPort())
  tubeFilter.SetRadius(R)
  tubeFilter.SetNumberOfSides(50)
  tubeFilter.CappingOn()
  #
  triangleFilter = vtk.vtkTriangleFilter()
  triangleFilter.SetInputConnection(tubeFilter.GetOutputPort())
  # make strips valid
  triangleFilter.PassLinesOff()
  #
  normalsFilter = vtk.vtkPolyDataNormals()
  normalsFilter.SetInputConnection(triangleFilter.GetOutputPort())
  #
  #cylinder.SetPolyDataConnection(triangleFilter.GetOutputPort())
  cylinder.SetPolyDataConnection(normalsFilter.GetOutputPort())
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

def getSegmentStatistics(segmentID, segmentationNode):
  import SegmentStatistics

  segStatLogic = SegmentStatistics.SegmentStatisticsLogic()
  segStatLogic.getParameterNode().SetParameter("Segmentation", segmentationNode.GetID())
  segStatLogic.getParameterNode().SetParameter("LabelmapSegmentStatisticsPlugin.enabled", "True")
  segStatLogic.getParameterNode().SetParameter("ScalarVolumeSegmentStatisticsPlugin.enabled", "False")
  segStatLogic.getParameterNode().SetParameter("ClosedSurfaceSegmentStatisticsPlugin.enabled", "False")
  segStatLogic.getParameterNode().SetParameter("LabelmapSegmentStatisticsPlugin.obb_origin_ras.enabled", "True")
  segStatLogic.getParameterNode().SetParameter("LabelmapSegmentStatisticsPlugin.obb_diameter_mm.enabled", "True")
  segStatLogic.getParameterNode().SetParameter("LabelmapSegmentStatisticsPlugin.principal_axis_z.enabled", "True")
  segStatLogic.computeStatistics()
  stats = segStatLogic.getStatistics()

  import numpy as np
  obbOrigin = np.array(stats[segmentID, "LabelmapSegmentStatisticsPlugin.obb_origin_ras"])
  obbDiameters = np.array(stats[segmentID, "LabelmapSegmentStatisticsPlugin.obb_diameter_mm"])
  principalZAxis = np.array(stats[segmentID, "LabelmapSegmentStatisticsPlugin.principal_axis_z"])
  return obbOrigin, obbDiameters, principalZAxis

def calculateSurfaceArea(polydata):
  triangleFilter = vtk.vtkTriangleFilter()
  triangleFilter.SetInputData(polydata)
  triangleFilter.SetPassLines(0)
  triangleFilter.Update()
  
  massProperties = vtk.vtkMassProperties()
  massProperties.SetInputData(triangleFilter.GetOutput())
  return massProperties.GetSurfaceArea()

def calculateNormals(polydata,flip=False):
  normalsFilter = vtk.vtkPolyDataNormals()
  normalsFilter.SetInputData(polydata)
  normalsFilter.AutoOrientNormalsOn()
  if flip:
    normalsFilter.FlipNormalsOn()
  normalsFilter.Update()
  return normalsFilter.GetOutput()

def getIntersectionPointsOfEachModelByMode(intersectionA,intersectionB,measurementMode):
  lineStartPos = getCentroid(intersectionA)
  lineEndPos = getCentroid(intersectionB)

  if measurementMode == "center2center":
    return lineStartPos, lineEndPos
  
  directionLine = lineEndPos-lineStartPos
  directionLine = directionLine/np.linalg.norm(directionLine)

  intersectionAPoints = slicer.util.arrayFromModelPoints(intersectionA)
  intersectionBPoints = slicer.util.arrayFromModelPoints(intersectionB)
  intersectionAtoBSimilarVectors = []
  for i in range(len(intersectionAPoints)):
    pointOfA = intersectionAPoints[i]
    intersectionAtoBVectorsArray = []
    for j in range(len(intersectionBPoints)):
      pointOfB = intersectionBPoints[j]
      directionVector = pointOfB-pointOfA
      directionNorm = np.linalg.norm(directionVector)
      directionVector = directionVector/directionNorm
      directionSimilarity = np.dot(directionLine,directionVector)
      intersectionAtoBVectorsArray.append(
        [directionSimilarity,directionNorm,pointOfA,pointOfB]
      )
    # save most similar points to vector
    intersectionAtoBVectorsArray.sort(key=lambda x: x[0],reverse=True)
    intersectionAtoBSimilarVectors.append(intersectionAtoBVectorsArray[0])
  
  # sort by norm
  intersectionAtoBSimilarVectors.sort(key=lambda x: x[1],reverse=False)
  
  if measurementMode == "proximal2proximal":
    return intersectionAtoBSimilarVectors[0][2], intersectionAtoBSimilarVectors[0][3]
  elif measurementMode == "distal2distal":
    return intersectionAtoBSimilarVectors[-1][2], intersectionAtoBSimilarVectors[-1][3]
  
class combineModelsRobustLogic:
  def process(
      inputModelA, 
      inputModelB, 
      outputModel, 
      operation, 
      numberOfRetries = 5, 
      translateRandomly = 4, 
      triangulateInputs = False
    ):
    """
    Run the processing algorithm.
    Can be used without GUI widget.
    :param inputModelA: first input model node
    :param inputModelB: second input model node
    :param outputModel: result model node, if empty then a new output node will be created
    :param operation: union, intersection, difference, difference2
    :param numberOfRetries: number of retries if operation fails
    :param translateRandomly: order of magnitude of the random translation
    :param triangulateInputs: triangulate input models before boolean operation
    """

    logic = slicer.modules.combinemodels.widgetRepresentation().self().logic
    logic.process(
      inputModelA,
      inputModelB,
      outputModel,
      operation,
      numberOfRetries,
      translateRandomly,
      triangulateInputs
    )

def saveExecutedMethodWithTelemetry(method):
    PREVIEW_RELEASE_OCTOBER_6TH_2024 = 33047
    def decorated_method(self, *args, **kwargs):
        result = method(self, *args, **kwargs)
        if int(slicer.app.revision) >= PREVIEW_RELEASE_OCTOBER_6TH_2024:
          slicer.app.logUsageEvent("BoneReconstructionPlanner", method.__name__)
        #print("Saved method name: " + method.__name__)
        return result

    return decorated_method

# read setting
def rs(parameter):
  read_value = slicer.app.settings().value(f"BoneReconstructionPlanner/{parameter}")
  return read_value

# write setting
def ws(parameter, parameterValue):
  slicer.app.settings().setValue(f"BoneReconstructionPlanner/{parameter}", str(parameterValue))

# read parameter from the parameterNode
def rp(parameterNode, parameter):
  read_value = parameterNode.GetParameter(parameter)
  return read_value

# write parameter to the parameterNode
def wp(parameterNode, parameter, parameterValue):
  parameterNode.SetParameter(parameter, str(parameterValue))

def createListFromFolderID(folderID):
  shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
  createdList = []

  if folderID != shNode.GetInvalidItemID():
    myList = vtk.vtkIdList()
    shNode.GetItemChildren(folderID,myList)
    for i in range(myList.GetNumberOfIds()):
      createdList.append(shNode.GetItemDataNode(myList.GetId(i)))
  
  return createdList

def createListFromFolderName(folderName):
  shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
  folderID = shNode.GetItemByName(folderName)
  return createListFromFolderID(folderID)

def setFolderItemVisibility(folderItemID, visibility):
  pluginHandler = slicer.qSlicerSubjectHierarchyPluginHandler().instance()
  folderPlugin = pluginHandler.pluginByName("Folder")
  folderPlugin.setDisplayVisibility(folderItemID, visibility)

def setFolderItemExpanded(folderItemID, expanded):
  shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
  shNode.SetItemExpanded(folderItemID, expanded)

# one use is to put some nodes inside a particular folder
def moveNodeToFolder(dataNode, folderID):
  shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
  dataNodeItemID = shNode.GetItemByDataNode(dataNode)
  shNode.SetItemParent(dataNodeItemID, folderID)

def removeFolder(folderID):
  # TODO: use this function where needed on the code
  shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
  if folderID:
      shNode.RemoveItem(folderID)

def renameFolder(folderID, newName):
  shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
  if folderID:
    shNode.SetItemName(folderID, newName)

def renameFolderByName(oldFolderName, newFolderName):
  """If a folder named oldFolderName exists in the scene, rename it to newFolderName.
  Used for backward compatibility with scenes created by older module versions."""
  shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
  folderID = shNode.GetItemByName(oldFolderName)
  if folderID and shNode.GetItemOwnerPluginName(folderID) == "Folder":
    shNode.SetItemName(folderID, newFolderName)

parentChildrenDict = {
  "": [
    "BoneReconstructionPlanner"
  ],
  "BoneReconstructionPlanner": [
    "Mandible reconstruction", 
    "Inverse mandible reconstruction", 
    "Dental Implants planning", 
    "Mandibular planes",
    "Mandibular planes 2",
    "Intersections For Centroid Calculation",
    "Fibula Segments Lengths",
    "Intersections For Lines Calculation",
    "Fibula planes",
    "Segmentation Models",
  ],
  "Mandible reconstruction": [
    "Mandible Planes Transforms",
    "Mandible2Fibula transforms",
    "Intersections",
    "Bone Plane Cuts",
    "Cut Bones",
    "Bone Pieces Transforms",
    "Transformed Fibula Pieces",
    "Vessels Plane Cuts",
    "Cut Vessels",
    "Transformed Vessels Pieces",
    "Vessels Pieces Transforms",
    "Duplicate Fibula Bone Pieces",
    "Duplicate Fibula Bone Pieces Transforms",
    "biggerMiterBoxes Models",
    "rectanglet Models",
    "lowResolutionBiggerMiterBoxes Models",
    "miterBoxes Models",
    "previewMiterBoxes Models",
    "miterBoxes Transforms",
    "Intersections",
    "Points Intersections",
    "Fibula Cylinders Models",
    "Cylinders Transforms",
    "Mandible Cylinders Models",
    "biggerSawBoxes Models",
    "sawBoxes Models",
    "previewSawBoxes Models",
    "sawBoxes Planes",
    "sawBoxes Transforms",
    "Points Intersections",
    "Scaled Fibula Pieces",
  ],
  "Inverse mandible reconstruction": [
    "Inverse Plane Cuts",
    "Inverse Append",
    "Cut Mandible Pieces",
    "Full Mandibles",
    "Transformed Mandible Pieces",
    "Transformed Full Mandible",
  ],
  "Dental Implants planning": [
    "Dental Implants Cylinders Fiducials",
    "Dental Implants Cylinders Models",
    "dentalImplants Planes",
    "Dental Implants Cylinders Transforms",
    "Fibula Dental Implants Cylinders Models",
    "Bigger Fibula Dental Implants Cylinders Models",
    "No Caps Transformed Fibula Pieces",
  ]
}

# improve the folders logic
def getFolder(requestedFolderName, unused = None, reset = False):
  currentFolderName = requestedFolderName
  parentFolderslist = []
  reachedSceneLevel = False
  while not reachedSceneLevel:
    foundParent = False
    for parentFolderName, childFolderNames in parentChildrenDict.items():
      if currentFolderName in childFolderNames:
        foundParent = True
        parentFolderslist.append(parentFolderName)
        currentFolderName = parentFolderName
        if currentFolderName == "":
          reachedSceneLevel = True
        break
    if not foundParent:
      raise ValueError(
        "getFolder: folder name '{0}' is not registered in parentChildrenDict; "
        "its parent hierarchy cannot be resolved.".format(currentFolderName)
      )

  #print(parentFolderslist)
  #return
  
  shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
  topLevelID = shNode.GetSceneItemID()
  requestedFolderID = shNode.GetItemByName(requestedFolderName)
  # TODO: check that there is no a dataNode with that name. E.g. use: shNode.GetItemOwnerPluginName() == "Folder"
  if reset and requestedFolderID:
    shNode.RemoveItem(requestedFolderID)
    requestedFolderID = 0
  if not requestedFolderID:
    childToParentFoldersList = [requestedFolderName] + parentFolderslist
    # create the folder hierarchy
    for i in range(len(childToParentFoldersList)-1):
      folderName = childToParentFoldersList[i]
      folderID = shNode.GetItemByName(folderName)
      if not folderID:
        folderID = shNode.CreateFolderItem(topLevelID,folderName)
      if i == 0:
        requestedFolderID = folderID
      parentFolderName = childToParentFoldersList[i+1]
      # last level, that corresponds to the scene, does not need to be created
      if parentFolderName == "":
        continue
      parentFolderID = shNode.GetItemByName(parentFolderName)
      if not parentFolderID:
        parentFolderID = shNode.CreateFolderItem(topLevelID,parentFolderName)
      shNode.SetItemParent(folderID, parentFolderID)
  return requestedFolderID

def getItem(dataNode):
  shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
  nodeItemID = shNode.GetItemByDataNode(dataNode)
  return nodeItemID

# decorator to update the GUI before and after running a method
def updateGUI(method):
  def wrapper(*args, **kwargs):
    slicer.app.processEvents()
    method(*args, **kwargs)
    slicer.app.processEvents()
  return wrapper

def areSegmentationsEqual(seg1, seg2):
    """Compare two segmentation nodes for equality"""
    
    # Check if both exist
    if seg1 is None or seg2 is None:
        return seg1 == seg2
    
    # Compare number of segments
    segmentation1 = seg1.GetSegmentation()
    segmentation2 = seg2.GetSegmentation()
    
    if segmentation1.GetNumberOfSegments() != segmentation2.GetNumberOfSegments():
        return False
    
    # Compare each segment
    for i in range(segmentation1.GetNumberOfSegments()):
        segmentID1 = segmentation1.GetNthSegmentID(i)
        segmentID2 = segmentation2.GetNthSegmentID(i)
        
        segment1 = segmentation1.GetSegment(segmentID1)
        segment2 = segmentation2.GetSegment(segmentID2)
        
        # Compare segment names
        if segment1.GetName() != segment2.GetName():
            return False
        
        # Compare segment representations (e.g., binary labelmap)
        if not compareSegmentRepresentationsV2(segment1, segment2):
            return False
    
    return True

def compareSegmentRepresentations(segment1, segment2):
    """Compare the actual segment data"""
    import numpy as np
    
    # Get binary labelmap representation
    rep1 = segment1.GetRepresentation(
        slicer.vtkSegmentationConverter.GetBinaryLabelmapRepresentationName()
    )
    rep2 = segment2.GetRepresentation(
        slicer.vtkSegmentationConverter.GetBinaryLabelmapRepresentationName()
    )
    
    if rep1 is None or rep2 is None:
        return rep1 == rep2
    
    # Convert to numpy arrays and compare
    array1 = slicer.util.arrayFromVolume(rep1)
    array2 = slicer.util.arrayFromVolume(rep2)
    
    return np.array_equal(array1, array2)

def compareSegmentRepresentationsV2(segment1, segment2):
    """Compare the actual segment data"""
    import numpy as np
    
    # Get binary labelmap representation
    rep1 = segment1.GetRepresentation(
        slicer.vtkSegmentationConverter.GetBinaryLabelmapRepresentationName()
    )
    rep2 = segment2.GetRepresentation(
        slicer.vtkSegmentationConverter.GetBinaryLabelmapRepresentationName()
    )
    
    if rep1 is None or rep2 is None:
        return rep1 == rep2
    
    # Convert vtkOrientedImageData to numpy arrays
    from vtk.util import numpy_support
    array1 = numpy_support.vtk_to_numpy(rep1.GetPointData().GetScalars())
    array2 = numpy_support.vtk_to_numpy(rep2.GetPointData().GetScalars())
    
    # Reshape arrays to match image dimensions
    dims1 = rep1.GetDimensions()
    dims2 = rep2.GetDimensions()
    
    # Check if dimensions match
    if dims1 != dims2:
        return False
    
    array1 = array1.reshape(dims1[::-1])  # VTK uses (x,y,z), numpy uses (z,y,x)
    array2 = array2.reshape(dims2[::-1])
    
    return np.array_equal(array1, array2)

def areVolumesEqual(vol1, vol2):
    """Compare two volume nodes for equality"""
    
    # Check if both exist
    if vol1 is None or vol2 is None:
        return vol1 == vol2
    
    # Compare image data dimensions
    imgData1 = vol1.GetImageData()
    imgData2 = vol2.GetImageData()
    
    if imgData1.GetDimensions() != imgData2.GetDimensions():
        return False
    
    # Compare voxel data
    array1 = slicer.util.arrayFromVolume(vol1)
    array2 = slicer.util.arrayFromVolume(vol2)
    
    return np.array_equal(array1, array2)

def getSegmentIDWithName(segmentName, segmentationNode):
    """Get a segment by name from a segmentation node"""
    if segmentationNode is None:
        return None
    
    segmentation = segmentationNode.GetSegmentation()
    
    for i in range(segmentation.GetNumberOfSegments()):
        segmentID = segmentation.GetNthSegmentID(i)
        segment = segmentation.GetSegment(segmentID)
        
        if segment.GetName() == segmentName:
            return segmentID    
    
    return None

def createHollowWithMargin(
    segmentationNode,
    fibulaSegmentName,
    marginSizeMm,
    vesselThicknessMm
):
  seg = segmentationNode
  seg.GetSegmentation().CreateRepresentation(slicer.vtkSegmentationConverter.GetSegmentationClosedSurfaceRepresentationName())
  fibulaSegmentID = getSegmentIDWithName(fibulaSegmentName, segmentationNode)
  if fibulaSegmentID is None:
    fibulaSegmentID = seg.GetSegmentation().GetNthSegmentID(0)
  
  segDisplayNode = seg.GetDisplayNode()
  segmentationVisibilityState = segDisplayNode.GetVisibility()
  segDisplayNode.SetVisibility(True)


  # set up segment editor and configure it
  segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
  segmentEditorNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentEditorNode")
  segmentEditorWidget.setMRMLSegmentEditorNode(segmentEditorNode)
  segmentEditorWidget.setSegmentationNode(segmentationNode)
  #segmentEditorWidget.setSourceVolumeNode(volumeNode)

  segmentEditorNode.SetOverwriteMode(slicer.vtkMRMLSegmentEditorNode.OverwriteNone)
  segmentEditorNode.SetMaskMode(slicer.vtkMRMLSegmentationNode.EditAllowedEverywhere)
  segmentEditorNode.SetSourceVolumeIntensityMask(False)





  # Do the margin here, needs to crop and resample the volume






  hollowSegmentName = fibulaSegmentName + "_Hollow"
  hollowSegmentID = getSegmentIDWithName(hollowSegmentName, segmentationNode)
  if not hollowSegmentID:
    hollowSegmentID = hollowSegmentName
    seg.GetSegmentation().AddEmptySegment(
      hollowSegmentID,
      hollowSegmentID
    )

  segmentEditorNode.SetSelectedSegmentID(hollowSegmentID)
  segmentEditorWidget.setActiveEffectByName("Logical operators")
  effect = segmentEditorWidget.activeEffect()
  effect.setParameter("Operation","COPY") # change the operation here
  effect.setParameter("ModifierSegmentID",fibulaSegmentID)
  effect.self().onApply()

  segmentEditorWidget.setCurrentSegmentID(hollowSegmentID)
  segmentEditorWidget.setActiveEffectByName("Hollow")
  effect = segmentEditorWidget.activeEffect()
  effect.setParameter("ShellThicknessMm", str(vesselThicknessMm))
  effect.self().onApply()

  segDisplayNode.SetVisibility(segmentationVisibilityState)
  
  return hollowSegmentID

def createAdaptedBox(X, Y, Z, name, boxX, boxZ, referenceZ, highResolution = True):
  import math

  alpha = math.acos(boxZ @ referenceZ.T)
  delta = Z*math.tan(alpha)

  comparisonVector = np.cross(boxZ, referenceZ)
  comparisonVector = comparisonVector/np.linalg.norm(comparisonVector)

  points = []
  if (comparisonVector @ boxX.T) > 0:
    points.append(np.array([X/2, Y/2 - delta, Z/2,], dtype=float))
    points.append(np.array([X/2, Y/2, -Z/2,], dtype=float))
    points.append(np.array([X/2, -Y/2, -Z/2,], dtype=float))
    points.append(np.array([X/2, -Y/2 - delta, Z/2,], dtype=float))
    
    points.append(np.array([-X/2, Y/2 - delta, Z/2,], dtype=float))
    points.append(np.array([-X/2, -Y/2 - delta, Z/2,], dtype=float))
    points.append(np.array([-X/2, -Y/2, -Z/2,], dtype=float))
    points.append(np.array([-X/2, Y/2, -Z/2,], dtype=float))
  
  else:
    points.append(np.array([X/2, Y/2, Z/2,], dtype=float))
    points.append(np.array([X/2, Y/2 - delta, -Z/2,], dtype=float))
    points.append(np.array([X/2, -Y/2 - delta, -Z/2,], dtype=float))
    points.append(np.array([X/2, -Y/2, Z/2,], dtype=float))

    points.append(np.array([-X/2, Y/2, Z/2,], dtype=float))
    points.append(np.array([-X/2, -Y/2, Z/2,], dtype=float))
    points.append(np.array([-X/2, -Y/2 - delta, -Z/2,], dtype=float))
    points.append(np.array([-X/2, Y/2 - delta, -Z/2,], dtype=float))


  points_vtk = vtk.vtkPoints()
  pointID = 0

  for i in range(len(points)):
    points_vtk.InsertNextPoint(points[i])
    pointID += 1

  cellArray = vtk.vtkCellArray()

  facesPointsIDs = []
  #X/2 Constant
  facesPointsIDs.append([0,1,2,3])
  #-X/2 face
  facesPointsIDs.append([4,5,6,7])
  #-Z/2 constant face
  facesPointsIDs.append([7,6,2,1])
  #Z/2 constant face
  facesPointsIDs.append([0,3,5,4])
  #Y/2 constant face
  facesPointsIDs.append([0,4,7,1])
  #-Y/2 constant face
  facesPointsIDs.append([6,5,3,2])

  for pointIDs in facesPointsIDs:
    polygon = vtk.vtkPolygon()
    polygon.GetPointIds().SetNumberOfIds(len(pointIDs))
    for i in range(len(pointIDs)):
        polygon.GetPointIds().SetId(i, pointIDs[i])
    cellArray.InsertNextCell(polygon)
  
  polydata = vtk.vtkPolyData()
  polydata.SetPoints(points_vtk)
  polydata.SetPolys(cellArray)

  # remove duplicate points
  cleanFilter = vtk.vtkCleanPolyData()
  cleanFilter.SetInputData(polydata)
  cleanFilter.Update()

  triangleFilter = vtk.vtkTriangleFilter()
  triangleFilter.SetInputData(cleanFilter.GetOutput())
  triangleFilter.Update()

  normalsFilter = vtk.vtkPolyDataNormals()
  normalsFilter.SetInputData(triangleFilter.GetOutput())
  normalsFilter.AutoOrientNormalsOn()
  normalsFilter.Update()


  maximumEdgeLengthMm = 1
  adaptiveSubdivisionFilter = vtk.vtkAdaptiveSubdivisionFilter()
  adaptiveSubdivisionFilter.SetInputConnection(normalsFilter.GetOutputPort())
  adaptiveSubdivisionFilter.SetMaximumEdgeLength(maximumEdgeLengthMm)
  adaptiveSubdivisionFilter.SetMaximumTriangleArea(adaptiveSubdivisionFilter.GetMaximumTriangleAreaMaxValue()) # set to infinity


  adaptedBoxModel = slicer.mrmlScene.CreateNodeByClass("vtkMRMLModelNode")
  slicer.mrmlScene.AddNode(adaptedBoxModel)
  adaptedBoxModel.SetName(slicer.mrmlScene.GetUniqueNameByString(name))
  adaptedBoxModel.CreateDefaultDisplayNodes()

  if highResolution:
    adaptedBoxModel.SetPolyDataConnection(adaptiveSubdivisionFilter.GetOutputPort())
  else:
    adaptedBoxModel.SetPolyDataConnection(normalsFilter.GetOutput())
  

  boxLowerFacePointIds = [6,5,3,2]
  rect_points_vtk = vtk.vtkPoints()
  for point_id in boxLowerFacePointIds:
    rect_points_vtk.InsertNextPoint(points_vtk.GetPoint(point_id))

  rectCellArray = vtk.vtkCellArray()
  rect_polygon = vtk.vtkPolygon()
  rect_polygon.GetPointIds().SetNumberOfIds(3)
  rect_polygon.GetPointIds().SetId(0, 0)
  rect_polygon.GetPointIds().SetId(1, 1)
  rect_polygon.GetPointIds().SetId(2, 3)
  rectCellArray.InsertNextCell(rect_polygon)
  rect_polygon = vtk.vtkPolygon()
  rect_polygon.GetPointIds().SetNumberOfIds(3)
  rect_polygon.GetPointIds().SetId(0, 3)
  rect_polygon.GetPointIds().SetId(1, 1)
  rect_polygon.GetPointIds().SetId(2, 2)
  rectCellArray.InsertNextCell(rect_polygon)

  rectpolydata = vtk.vtkPolyData()
  rectpolydata.SetPoints(rect_points_vtk)
  rectpolydata.SetPolys(rectCellArray)

  rectangletModel = slicer.mrmlScene.CreateNodeByClass("vtkMRMLModelNode")
  slicer.mrmlScene.AddNode(rectangletModel)
  rectangletModel.SetName(slicer.mrmlScene.GetUniqueNameByString(name + "_rectanglet"))
  rectangletModel.CreateDefaultDisplayNodes()
  rectangletModel.SetAndObservePolyData(rectpolydata)


  return adaptedBoxModel, rectangletModel




def build_surface_locator(surface_polydata):
  """Call once; reuse the locator across many collision checks."""
  obb_tree = vtk.vtkOBBTree()
  obb_tree.SetDataSet(surface_polydata)
  obb_tree.BuildLocator()
  return obb_tree

def rectangles_edges(rect_polydata):
  """Return (p1, p2) for each edge in the rectangle, works for both line and polygon cells."""
  extract = vtk.vtkExtractEdges()
  extract.SetInputData(rect_polydata)
  extract.Update()
  edge_poly = extract.GetOutput()
  lines = edge_poly.GetLines()
  pts = edge_poly.GetPoints()
  lines.InitTraversal()
  id_list = vtk.vtkIdList()
  edges = []
  while lines.GetNextCell(id_list):
    p1 = pts.GetPoint(id_list.GetId(0))
    p2 = pts.GetPoint(id_list.GetId(1))
    edges.append((p1, p2))
  return edges

def has_collision(rect_polydata_original, rect_matrix, surface_polydata, obb_tree):
  # transform filter
  transformFilter = vtk.vtkTransformPolyDataFilter()
  transformFilter.SetInputData(rect_polydata_original)
  transformFilter.SetTransform(rect_matrix)
  transformFilter.Update()
  rect_polydata = transformFilter.GetOutput()
  
  # 0. Quick bounding-box rejection (microseconds)
  r_bounds = rect_polydata.GetBounds()
  s_bounds = surface_polydata.GetBounds()
  for axis in range(3):
    if r_bounds[2*axis+1] < s_bounds[2*axis] or r_bounds[2*axis] > s_bounds[2*axis+1]:
      return False   # no overlap on this axis → no collision

  # 1. Edge-intersection test (each edge is O(log N) with OBBTree)
  hit_pts = vtk.vtkPoints()
  for p1, p2 in rectangles_edges(rect_polydata):
    if obb_tree.IntersectWithLine(p1, p2, hit_pts, None) > 0:
      return True

  # 2. Check if any rectangle vertex is *inside* the closed surface
  #    (handles case where rectangle is fully contained)
  enc = vtk.vtkSelectEnclosedPoints()
  enc.SetInputData(rect_polydata)
  enc.SetSurfaceData(surface_polydata)
  enc.CheckSurfaceOff()   # skip surface-integrity check for speed
  enc.Update()
  pts = rect_polydata.GetPoints()
  for i in range(pts.GetNumberOfPoints()):
    if enc.IsInside(i):
      return True

  return False

def countComponentsInPolyData(polydata):
  connectivityFilter = vtk.vtkConnectivityFilter()
  connectivityFilter.SetInputDataObject(0, polydata)
  connectivityFilter.Update()
  return connectivityFilter.GetNumberOfExtractedRegions()

def extractEachRegionAsAModel(polydata, baseName):
  connectivityFilter = vtk.vtkConnectivityFilter()
  connectivityFilter.SetInputDataObject(0, polydata)
  connectivityFilter.SetExtractionModeToAllRegions()
  connectivityFilter.ColorRegionsOn()
  connectivityFilter.Update()
  numberOfRegions = connectivityFilter.GetNumberOfExtractedRegions()

  regionModels = []
  for i in range(numberOfRegions):
    threshold = vtk.vtkThreshold()
    threshold.SetInputConnection(connectivityFilter.GetOutputPort())
    threshold.SetLowerThreshold(i-0.1)
    threshold.SetUpperThreshold(i+0.1)
    
    threshold.Update()

    geometryFilter = vtk.vtkGeometryFilter()
    geometryFilter.SetInputConnection(threshold.GetOutputPort())
    geometryFilter.Update()

    regionPolyData = geometryFilter.GetOutput()

    regionModel = slicer.mrmlScene.CreateNodeByClass("vtkMRMLModelNode")
    slicer.mrmlScene.AddNode(regionModel)
    regionModel.SetName(slicer.mrmlScene.GetUniqueNameByString(f"{baseName}_region_{i}"))
    regionModel.CreateDefaultDisplayNodes()
    regionModel.SetAndObservePolyData(regionPolyData)

    regionModels.append(regionModel)

  return regionModels
