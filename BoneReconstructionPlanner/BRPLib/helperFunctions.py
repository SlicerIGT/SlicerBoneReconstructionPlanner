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

  return points[maxDotIndex[0]]

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
      translateRandomly = 3,
      triangulateInputs = False
    ):
    """
    Run the processing algorithm.
    Can be used without GUI widget.
    Primary implementation: the "BooleanOperation" (CGAL) CLI of the
    SlicerVESPA extension. It is an executable-only CLI so it runs in a
    separate process and exchanges data through files, keeping GPL-licensed
    CGAL/VESPA code out of the Slicer process (and out of this extension's
    BSD-3 licensing). Falls back to the CombineModels module (vtkbool, from
    SlicerSandbox) when SlicerVESPA is not installed or its CLI fails.
    :param inputModelA: first input model node
    :param inputModelB: second input model node
    :param outputModel: result model node, if empty then a new output node will be created
    :param operation: union, intersection, difference, difference2
    :param numberOfRetries: number of retries if operation fails (vtkbool fallback only)
    :param translateRandomly: order of magnitude of the random translation (vtkbool fallback only)
    :param triangulateInputs: triangulate input models before boolean operation
      (vtkbool fallback only; the VESPA CLI repairs its inputs instead)
    """

    if hasattr(slicer.modules, 'vespabooleanoperation'):
      try:
        combineModelsRobustLogic.processWithVESPA(
          inputModelA, inputModelB, outputModel, operation)
        return
      except Exception as e:
        logging.exception(
          "VESPA (CGAL) boolean operation failed, falling back to CombineModels (vtkbool): "
          + str(e))

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

  # The VESPA CLI only implements difference, intersection and union, and its
  # difference is firstPoly minus secondPoly (CGAL corefine_and_compute_difference),
  # so difference2 is the same operation with the operands swapped
  VESPA_OPERATIONS = {
    "union": ("union", False),
    "intersection": ("intersection", False),
    "difference": ("difference", False),
    "difference2": ("difference", True),
  }

  def processWithVESPA(
      inputModelA,
      inputModelB,
      outputModel,
      operation,
      repairInputs = True
    ):
    """
    Run one boolean operation with the SlicerVESPA CLI (separate process).
    Raises RuntimeError if the CLI does not complete successfully.
    :param repairInputs: let the CLI rebuild both operands into closed,
      non-self-intersecting 2-manifolds first. CGAL corefinement fails on
      invalid inputs, so only disable this for meshes known to be valid.
    """
    if operation not in combineModelsRobustLogic.VESPA_OPERATIONS:
      raise ValueError("Invalid operation: " + operation)
    cliOperation, swapOperands = combineModelsRobustLogic.VESPA_OPERATIONS[operation]

    # The CLI reads each node's stored mesh, ignoring parent transform nodes,
    # so bake the transform of each input into the output model's frame first
    # (same semantics as the CombineModels module)
    temporaryInputModels = []
    cliNode = None
    try:
      cliInputModels = []
      for inputModel in [inputModelA, inputModelB]:
        transformToOutput = vtk.vtkGeneralTransform()
        slicer.vtkMRMLTransformNode.GetTransformBetweenNodes(
          inputModel.GetParentTransformNode(), outputModel.GetParentTransformNode(),
          transformToOutput)
        transformerToOutput = vtk.vtkTransformPolyDataFilter()
        transformerToOutput.SetTransform(transformToOutput)
        transformerToOutput.SetInputData(inputModel.GetPolyData())
        transformerToOutput.Update()
        temporaryInputModel = slicer.mrmlScene.AddNewNodeByClass(
          'vtkMRMLModelNode', slicer.mrmlScene.GetUniqueNameByString('temp_' + inputModel.GetName()))
        temporaryInputModel.SetHideFromEditors(True)
        temporaryInputModel.SetAndObservePolyData(transformerToOutput.GetOutput())
        temporaryInputModels.append(temporaryInputModel)
        cliInputModels.append(temporaryInputModel)

      # Empty inputs would make the CLI fail; resolve those cases directly
      # (same rules as the CombineModels module)
      polydataA = cliInputModels[0].GetPolyData()
      polydataB = cliInputModels[1].GetPolyData()
      modelAEmpty = polydataA.GetNumberOfPoints() == 0
      modelBEmpty = polydataB.GetNumberOfPoints() == 0
      if modelAEmpty or modelBEmpty:
        if operation == "union":
          result = vtk.vtkPolyData()
          if not modelAEmpty:
            result.DeepCopy(polydataA)
          elif not modelBEmpty:
            result.DeepCopy(polydataB)
        elif operation == "intersection":
          result = vtk.vtkPolyData()
        elif operation == "difference":
          result = vtk.vtkPolyData()
          if not modelAEmpty and modelBEmpty:
            result.DeepCopy(polydataA)
        elif operation == "difference2":
          result = vtk.vtkPolyData()
          if not modelBEmpty and modelAEmpty:
            result.DeepCopy(polydataB)
        outputModel.SetAndObservePolyData(result)
        if outputModel.GetDisplayNode() is None:
          outputModel.CreateDefaultDisplayNodes()
        return

      if swapOperands:
        cliInputModels.reverse()

      parameters = {
        "firstPoly": cliInputModels[0],
        "secondPoly": cliInputModels[1],
        "output": outputModel,
        "operation": cliOperation,
        "repairInputs": repairInputs,
      }
      cliNode = slicer.cli.runSync(slicer.modules.vespabooleanoperation, None, parameters)
      if cliNode.GetStatus() & cliNode.ErrorsMask:
        errorText = cliNode.GetErrorText()
        raise RuntimeError("VESPA BooleanOperation CLI failed: " + errorText)
    finally:
      if cliNode is not None:
        slicer.mrmlScene.RemoveNode(cliNode)
      for temporaryInputModel in temporaryInputModels:
        slicer.mrmlScene.RemoveNode(temporaryInputModel)
    # Callers use the display node right after process(); the CombineModels
    # module guaranteed one, so keep that behavior
    if outputModel.GetDisplayNode() is None:
      outputModel.CreateDefaultDisplayNodes()

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
    "Fibula Segments Lengths center2center",
    "Fibula Segments Lengths proximal2proximal",
    "Fibula Segments Lengths distal2distal",
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
    "fibulaTextLabels Models",
    "sawBoxTextLabels Models",
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

def ensureExplicitCellArraysStorage(polyData):
  # VTK >= 9.6 may store cell arrays with implicit ("fixed-size") offsets, and
  # vtkClipClosedSurface never finishes on such inputs (spins forever in
  # vtkContourTriangulator); force explicit offsets before clipping.
  # No-op on older VTK and on already-explicit arrays.
  for cells in (polyData.GetVerts(), polyData.GetLines(),
                polyData.GetPolys(), polyData.GetStrips()):
    if (
      cells is not None
      and hasattr(cells, "IsStorageFixedSize")
      and cells.IsStorageFixedSize()
    ):
      cells.ConvertToDefaultStorage()

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

# A single isolated segment editor widget, created on first use and kept alive
# for the rest of the Slicer session. createHollowWithMargin needs its own
# editor (so it never disturbs the module's shared GUI editor or its node), but
# it must NOT create-and-destroy one per call: destroying a
# qMRMLSegmentEditorWidget garbage-collects every effect it instantiated,
# including the AutoComplete effects (Grow from seeds / Fill between slices).
# Their __del__ calls observeSegmentation(False), which unconditionally calls
# scriptedEffect.parameterSetNode() before any guard, and by then the backing
# C++ qSlicerSegmentEditorScriptedEffect is already destroyed, raising
# "Exception ignored in __del__ ... destroyed qSlicerSegmentEditorScriptedEffect".
# Reusing one persistent widget means those effects are never destroyed, so the
# faulty __del__ never runs. See https://github.com/Slicer/Slicer/issues/7392
_reusableSegmentEditorWidget = None

def _getReusableSegmentEditorWidget():
  global _reusableSegmentEditorWidget
  if _reusableSegmentEditorWidget is None:
    widget = slicer.qMRMLSegmentEditorWidget()
    widget.setMRMLScene(slicer.mrmlScene)
    _reusableSegmentEditorWidget = widget
  return _reusableSegmentEditorWidget

def createHollowWithMargin(
    segmentationNode,
    fibulaSegmentName,
    marginSizeMm,
    vesselThicknessMm,
    clippingPlanes=None
):
  seg = segmentationNode
  seg.GetSegmentation().CreateRepresentation(slicer.vtkSegmentationConverter.GetSegmentationClosedSurfaceRepresentationName())
  fibulaSegmentID = getSegmentIDWithName(fibulaSegmentName, segmentationNode)
  if fibulaSegmentID is None:
    fibulaSegmentID = seg.GetSegmentation().GetNthSegmentID(0)
  
  hollowSegmentName = fibulaSegmentName + "_Hollow"
  hollowSegmentID = hollowSegmentName

  if marginSizeMm == 0.0:
    # No margin requested: keep the original behavior, which copies the fibula
    # straight onto the caller's segmentation node and hollows it in place. The
    # fine-grid machinery below only exists to resolve a sub-voxel margin, so it
    # is pointless (and slower) when there is no margin to render.
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

  # --- Fill the hollow segment with the fibula, resampled onto a fine grid ---
  # The Margin/Hollow effects measure distances in mm but snap them to whole
  # voxels of the labelmap they operate on. The fibula segmentation can be
  # coarse (e.g. a few mm in slice direction), so a 0.5mm margin would round up
  # to a full voxel (~the observed ~4mm error). We therefore rebuild the hollow
  # segment's labelmap on a fine isotropic grid that the effects then edit.
  #
  # OOM is bounded two ways: the grid covers only the fibula bounding box
  # (plus a pad), and a hard voxel budget caps the total size; if honoring the
  # margin would exceed the budget we coarsen the spacing and warn instead.
  MAX_LABELMAP_VOXELS = 200_000_000   # ~200 MB uint8 budget; tune as needed

  fibulaLabelmap = slicer.vtkOrientedImageData()
  slicer.vtkSlicerSegmentationsModuleLogic.GetSegmentBinaryLabelmapRepresentation(
      segmentationNode, fibulaSegmentID, fibulaLabelmap)
  originalSpacing = min(fibulaLabelmap.GetSpacing())

  # fibula bounding box in RAS (closed surface representation created above)
  fibulaPoly = vtk.vtkPolyData()
  slicer.vtkSlicerSegmentationsModuleLogic.GetSegmentClosedSurfaceRepresentation(
      segmentationNode, fibulaSegmentID, fibulaPoly)
  # restrict the grid to the region the guide base actually uses (between the
  # bounding planes) so the whole-bone extent never has to be allocated
  boundsPoly = fibulaPoly
  if clippingPlanes is not None:
    ensureExplicitCellArraysStorage(fibulaPoly)
    clipper = vtk.vtkClipClosedSurface()
    clipper.SetInputData(fibulaPoly)
    clipper.SetClippingPlanes(clippingPlanes)
    clipper.InsideOutOff()
    clipper.Update()
    if clipper.GetOutput().GetNumberOfPoints() > 0:
      boundsPoly = clipper.GetOutput()
  bounds = [0.0] * 6
  boundsPoly.GetBounds(bounds)

  pad = marginSizeMm + vesselThicknessMm + 2.0 * marginSizeMm
  extentMm = [(bounds[2 * i + 1] - bounds[2 * i]) + 2.0 * pad for i in range(3)]

  # finest isotropic spacing we can afford within the voxel budget,
  # but no finer than needed to resolve the smallest feature the effects must
  # render (margin and/or shell thickness both snap to voxels)
  affordableSpacing = (
      extentMm[0] * extentMm[1] * extentMm[2] / MAX_LABELMAP_VOXELS
  ) ** (1.0 / 3.0)
  features = [f for f in (marginSizeMm, vesselThicknessMm) if f > 0]
  desiredSpacing = (min(features) / 2.0) if features else originalSpacing
  # never coarsen below the native spacing (no benefit, only lost detail)
  desiredSpacing = min(desiredSpacing, originalSpacing)
  fineSpacing = max(desiredSpacing, affordableSpacing)

  if marginSizeMm > 0 and fineSpacing > marginSizeMm:
    logging.warning(
        f"createHollowWithMargin: margin {marginSizeMm}mm cannot be represented "
        f"within the {MAX_LABELMAP_VOXELS} voxel budget for this geometry; "
        f"using {fineSpacing:.3f}mm spacing (margin will be coarse).")

  dims = [max(1, int(np.ceil(extentMm[i] / fineSpacing))) for i in range(3)]

  # axis-aligned (identity-direction) fine geometry in RAS, as an
  # image-to-world matrix (spacing on the diagonal, grid origin in translation)
  imageToWorld = vtk.vtkMatrix4x4()
  imageToWorld.SetElement(0, 0, fineSpacing)
  imageToWorld.SetElement(1, 1, fineSpacing)
  imageToWorld.SetElement(2, 2, fineSpacing)
  imageToWorld.SetElement(0, 3, bounds[0] - pad)
  imageToWorld.SetElement(1, 3, bounds[2] - pad)
  imageToWorld.SetElement(2, 3, bounds[4] - pad)

  # Rasterize the SMOOTH fibula closed surface directly onto the fine grid,
  # instead of nearest-neighbor upsampling the coarse binary labelmap. NN
  # upsampling cannot add detail: it bakes the original ~1mm voxel steps into
  # the fine grid as sharp flat faces, so the margined surface comes out
  # visibly staircased. Rasterizing the surface yields steps at the fine
  # spacing (sub-visible) and matches the fibula surface used elsewhere.
  # the fine grid has identity directions (axis-aligned in RAS), so the
  # surface can be voxelized with a plain image stencil in RAS coordinates.
  origin = (bounds[0] - pad, bounds[2] - pad, bounds[4] - pad)
  whiteImage = vtk.vtkImageData()
  whiteImage.SetExtent(0, dims[0] - 1, 0, dims[1] - 1, 0, dims[2] - 1)
  whiteImage.SetSpacing(fineSpacing, fineSpacing, fineSpacing)
  whiteImage.SetOrigin(*origin)
  whiteImage.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)
  whiteImage.GetPointData().GetScalars().Fill(1)

  pol2stenc = vtk.vtkPolyDataToImageStencil()
  pol2stenc.SetInputData(fibulaPoly)
  pol2stenc.SetOutputOrigin(origin)
  pol2stenc.SetOutputSpacing(fineSpacing, fineSpacing, fineSpacing)
  pol2stenc.SetOutputWholeExtent(whiteImage.GetExtent())
  pol2stenc.Update()

  imgstenc = vtk.vtkImageStencil()
  imgstenc.SetInputData(whiteImage)
  imgstenc.SetStencilConnection(pol2stenc.GetOutputPort())
  imgstenc.ReverseStencilOff()
  imgstenc.SetBackgroundValue(0)
  imgstenc.Update()

  resampledFibula = slicer.vtkOrientedImageData()
  resampledFibula.DeepCopy(imgstenc.GetOutput())
  resampledFibula.SetGeometryFromImageToWorldMatrix(imageToWorld)

  # --- Run the Margin/Hollow effects on a temporary segmentation node whose
  # own geometry IS the fine grid. The segment editor applies its effects on a
  # single reference geometry; with no source volume that geometry is taken
  # from the segmentation node. If we edited the caller's node directly, the
  # reference geometry would be its coarse spacing (e.g. 1mm), so a sub-voxel
  # margin like 0.2mm would round to 0 voxels and silently do nothing. Editing
  # a node that holds only the fine labelmap forces the effects to resolve
  # sub-voxel features. ---
  tempSegmentationNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentationNode")
  tempSegmentationNode.CreateDefaultDisplayNodes()
  tempSegmentationNode.GetSegmentation().AddEmptySegment(hollowSegmentID, hollowSegmentID)
  slicer.vtkSlicerSegmentationsModuleLogic.SetBinaryLabelmapToSegment(
      resampledFibula, tempSegmentationNode, hollowSegmentID,
      slicer.vtkSlicerSegmentationsModuleLogic.MODE_REPLACE)

  # Pin the geometry the Margin/Hollow effects operate on to our fine ISOTROPIC
  # grid. The effects resolve their working geometry via
  # GetReferenceImageGeometryStringFromSegmentation(): if the "reference image
  # geometry" conversion parameter is set it is used, otherwise the geometry is
  # derived from DetermineCommonLabelmapGeometry(), which is not guaranteed to
  # stay isotropic. Both effects threshold an ITK SignedMaurer distance map that
  # honors the grid spacing, so an anisotropic working grid yields a shell whose
  # wall thickness varies with direction (the observed non-uniform thickness).
  # Setting the parameter to the isotropic grid forces a uniform wall.
  tempSegmentationNode.GetSegmentation().SetConversionParameter(
      slicer.vtkSegmentationConverter.GetReferenceImageGeometryParameterName(),
      slicer.vtkSegmentationConverter.SerializeImageGeometry(resampledFibula))

  # set up a standalone segment editor on the fine temporary node. We use our
  # own qMRMLSegmentEditorWidget (not the module's shared GUI editor) so that
  # deleting the temporary nodes below cannot crash Slicer by pulling them out
  # from under the live GUI editor, and so the user's editor state is left
  # untouched. The widget is created once and cached for the session (never
  # destroyed) to avoid the AutoComplete-effect __del__ crash described in
  # _getReusableSegmentEditorWidget.
  segmentEditorWidget = _getReusableSegmentEditorWidget()
  segmentEditorNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentEditorNode")
  segmentEditorWidget.setMRMLSegmentEditorNode(segmentEditorNode)
  segmentEditorWidget.setSegmentationNode(tempSegmentationNode)
  segmentEditorNode.SetOverwriteMode(slicer.vtkMRMLSegmentEditorNode.OverwriteNone)
  segmentEditorNode.SetMaskMode(slicer.vtkMRMLSegmentationNode.EditAllowedEverywhere)
  segmentEditorNode.SetSourceVolumeIntensityMask(False)
  segmentEditorNode.SetSelectedSegmentID(hollowSegmentID)

  segmentEditorWidget.setCurrentSegmentID(hollowSegmentID)
  segmentEditorWidget.setActiveEffectByName("Margin")
  effect = segmentEditorWidget.activeEffect()
  effect.setParameter("MarginSizeMm", str(marginSizeMm)) # positive = grow
  effect.self().onApply()

  segmentEditorWidget.setCurrentSegmentID(hollowSegmentID)
  segmentEditorWidget.setActiveEffectByName("Hollow")
  effect = segmentEditorWidget.activeEffect()
  effect.setParameter("ShellMode", "INSIDE_SURFACE") # grown surface stays the inner wall
  effect.setParameter("ShellThicknessMm", str(vesselThicknessMm))
  effect.self().onApply()
  segmentEditorWidget.setActiveEffectByName("None")

  # Build the fine closed surface in the temporary node before copying the
  # segment back. The caller's segmentation is coarse, so the copied binary
  # labelmap of this segment may be resampled to that coarse spacing, but the
  # closed surface representation is not re-voxelized and so keeps the
  # sub-voxel margin. The caller consumes the closed surface.
  tempSegmentationNode.GetSegmentation().CreateRepresentation(
      slicer.vtkSegmentationConverter.GetSegmentationClosedSurfaceRepresentationName())

  # move the finished segment into the caller's segmentation node, replacing
  # any segment left over from a previous run
  existingHollowSegmentID = getSegmentIDWithName(hollowSegmentName, segmentationNode)
  if existingHollowSegmentID:
    seg.GetSegmentation().RemoveSegment(existingHollowSegmentID)
  seg.GetSegmentation().CopySegmentFromSegmentation(
      tempSegmentationNode.GetSegmentation(), hollowSegmentID, False)

  # cleanup: detach the reusable editor widget from the nodes it referenced
  # BEFORE removing them, so removing the temporary nodes cannot pull them out
  # from under the widget. The widget itself is intentionally kept alive (see
  # _getReusableSegmentEditorWidget): destroying it would garbage-collect its
  # AutoComplete effects, whose __del__ then dereferences an already-destroyed
  # qSlicerSegmentEditorScriptedEffect. See
  # https://github.com/Slicer/Slicer/issues/7392
  segmentEditorWidget.setActiveEffectByName("None")
  segmentEditorWidget.setSegmentationNode(None)
  segmentEditorWidget.setMRMLSegmentEditorNode(None)
  slicer.mrmlScene.RemoveNode(segmentEditorNode)
  slicer.mrmlScene.RemoveNode(tempSegmentationNode)

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



import vtk

def _importMatplotlibTextPath():
    # matplotlib is not bundled with Slicer and is only needed for the text
    # labels of the surgical guides, so it is imported (and installed) on first
    # use: importing it at module load time would prevent the whole extension
    # from loading on installs that do not have it
    try:
      from matplotlib.textpath import TextPath
      from matplotlib.font_manager import FontProperties
    except ImportError:
      logging.info("matplotlib is needed to create the text labels, installing it")
      slicer.util.pip_install("matplotlib")
      from matplotlib.textpath import TextPath
      from matplotlib.font_manager import FontProperties
    return TextPath, FontProperties

def text_to_polydata(text, ttf_path, size=10.0):
    TextPath, FontProperties = _importMatplotlibTextPath()

    fp = FontProperties(fname=ttf_path)
    # to_polygons() flattens the curves into line segments per closed contour
    tp = TextPath((0, 0), text, size=size, prop=fp)

    points = vtk.vtkPoints()
    lines  = vtk.vtkCellArray()

    for contour in tp.to_polygons(closed_only=True):
        # to_polygons() repeats the first point at the end of each contour; skip
        # it so closing the loop below does not create a zero-length segment
        # (zero-length segments extrude into zero-area triangles that break the
        # boolean operations of the surgical guides)
        if np.allclose(contour[0], contour[-1]):
            contour = contour[:-1]
        n = len(contour)
        if n < 3:
            continue
        start = points.GetNumberOfPoints()
        for x, y in contour:
            points.InsertNextPoint(x, y, 0.0)
        # closed polyline loop
        lines.InsertNextCell(n + 1)
        for i in range(n):
            lines.InsertCellPoint(start + i)
        lines.InsertCellPoint(start)  # close it

    loops = vtk.vtkPolyData()
    loops.SetPoints(points)
    loops.SetLines(lines)

    tri = vtk.vtkContourTriangulator()
    tri.SetInputData(loops)
    tri.Update()
    return tri.GetOutput()   # filled vtkPolyData, holes respected
