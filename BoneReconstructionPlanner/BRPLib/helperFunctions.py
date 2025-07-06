#
#   helperFunctions.py: Stores functions used on multiple modules of this extension
#

from __main__ import vtk, slicer
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
  pd = model.GetPolyData().GetPoints().GetData()
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
  miterBox.SetPolyDataConnection(adaptiveSubdivisionFilter.GetOutputPort())
  return miterBox

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
      numberOfRetries = 2, 
      translateRandomly = 4, 
      triangulateInputs = True
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

    if not inputModelA or not inputModelB or not outputModel:
      raise ValueError("Input or output model nodes are invalid")

    import time
    startTime = time.time()
    logging.info('Processing started')

    import vtkSlicerCombineModelsModuleLogicPython as vtkbool

    combine = vtkbool.vtkPolyDataBooleanFilter()

    if operation == 'union':
      combine.SetOperModeToUnion()
    elif operation == 'intersection':
      combine.SetOperModeToIntersection()
    elif operation == 'difference':
      combine.SetOperModeToDifference()
    elif operation == 'difference2':
      combine.SetOperModeToDifference2()
    else:
      raise ValueError("Invalid operation: "+operation)

    transformToOutput = vtk.vtkGeneralTransform()
    slicer.vtkMRMLTransformNode.GetTransformBetweenNodes(inputModelA.GetParentTransformNode(), outputModel.GetParentTransformNode(), transformToOutput)
    if transformToOutput is None:
      transformToOutput = vtk.vtkTransform()
    transformerA = vtk.vtkTransformPolyDataFilter()
    transformerA.SetTransform(transformToOutput)
    transformerA.SetInputData(inputModelA.GetPolyData())
    transformerA.Update()
    combine.SetInputData(0, transformerA.GetOutput())

    transformToOutput = vtk.vtkGeneralTransform()
    slicer.vtkMRMLTransformNode.GetTransformBetweenNodes(inputModelB.GetParentTransformNode(), outputModel.GetParentTransformNode(), transformToOutput)
    if transformToOutput is None:
      transformToOutput = vtk.vtkTransform()
    preTransformerB = vtk.vtkTransformPolyDataFilter()
    preTransformerB.SetTransform(transformToOutput)
    preTransformerB.SetInputData(inputModelB.GetPolyData())
    preTransformerB.Update()
    identityTransform = vtk.vtkTransform()
    transformerB = vtk.vtkTransformPolyDataFilter()
    transformerB.SetTransform(identityTransform)
    transformerB.SetInputData(preTransformerB.GetOutput())
    transformerB.Update()
    combine.SetInputData(1, transformerB.GetOutput())

    # first handle cases where inputs are not valid otherwise the boolean filter will crash
    preBooleanOperationHandlingDone = False

    modelAIsValid = transformerA.GetOutput().GetNumberOfPoints() != 0
    modelBIsValid = transformerB.GetOutput().GetNumberOfPoints() != 0
    modelAIsEmpty = not modelAIsValid
    modelBIsEmpty = not modelBIsValid
    bothModelsAreEmpty = modelAIsEmpty and modelBIsEmpty
    onlyModelAIsValid = modelAIsValid and not modelBIsValid
    onlyModelBIsValid = modelBIsValid and not modelAIsValid

    if (
      bothModelsAreEmpty or
      ((operation == 'union') and onlyModelBIsValid) or
      ((operation == 'union') and onlyModelAIsValid)
    ):
      appendFilter = vtk.vtkAppendPolyData()
      appendFilter.AddInputData(transformerA.GetOutput())
      appendFilter.AddInputData(transformerB.GetOutput())
      combine = appendFilter
      preBooleanOperationHandlingDone = True
    elif (
      (
        (operation == 'intersection') and 
        (onlyModelAIsValid or onlyModelBIsValid)
      ) or
      (
        (operation == 'difference') and 
        (onlyModelBIsValid)
      ) or
      (
        (operation == 'difference2') and 
        (onlyModelAIsValid)
      )
    ):
      # return empty model
      appendFilter = vtk.vtkAppendPolyData()
      emptyPolyData = vtk.vtkPolyData()
      appendFilter.AddInputData(emptyPolyData)
      combine = appendFilter
      preBooleanOperationHandlingDone = True
    elif (
      (operation == 'difference') and 
      (onlyModelAIsValid)
    ):
      combine = transformerA
      preBooleanOperationHandlingDone = True
    elif (
      (operation == 'difference2') and 
      (onlyModelBIsValid)
    ):
      combine = transformerB
      preBooleanOperationHandlingDone = True
    # else:
    #   combine is a vtkPolyDataBooleanFilter
    

    # These parameters might be useful to expose:
    # combine.MergeRegsOn()  # default off
    # combine.DecPolysOff()  # default on
    combine.Update()

    collisionDetectionFilter = vtk.vtkCollisionDetectionFilter()
    collisionDetectionFilter.SetInputData(0, transformerA.GetOutput())
    collisionDetectionFilter.SetInputData(1, transformerB.GetOutput())
    identityMatrix = vtk.vtkMatrix4x4()
    collisionDetectionFilter.SetMatrix(0,identityMatrix)
    collisionDetectionFilter.SetMatrix(1,identityMatrix)
    collisionDetectionFilter.SetCollisionModeToFirstContact()

    combineFilterSuccessful = combine.GetOutput().GetNumberOfPoints() != 0
    if not combineFilterSuccessful and not preBooleanOperationHandlingDone:
      for retry in range(numberOfRetries+1):
        if (
          operation == 'union'
        ):
          if retry == 0:
            # check if the models are already intersecting
            collisionDetectionFilter.Update()
          if collisionDetectionFilter.GetNumberOfContacts() == 0:
            # models do not touch so we append them
            appendFilter = vtk.vtkAppendPolyData()
            appendFilter.AddInputData(transformerA.GetOutput())
            appendFilter.AddInputData(transformerB.GetOutput())
            appendFilter.Update()
            combine = appendFilter
            break

        if (
          operation == 'intersection'
        ):
          if retry == 0:
            # check if the models are already intersecting
            collisionDetectionFilter.Update()
          if collisionDetectionFilter.GetNumberOfContacts() == 0:
            # models do not touch so we return an empty model
            break
        
        if (
          operation == 'difference'
        ):
          if retry == 0:
            # check if the models are already intersecting
            collisionDetectionFilter.Update()
          if collisionDetectionFilter.GetNumberOfContacts() == 0:
            # models do not touch so we return modelA
            combine = transformerA
            break

        if (
          operation == 'difference2'
        ):
          if retry == 0:
            # check if the models are already intersecting
            collisionDetectionFilter.Update()
          if collisionDetectionFilter.GetNumberOfContacts() == 0:
            # models do not touch so we return modelB
            combine = transformerB
            break

        if retry == 0 and triangulateInputs:
          # in case inputs are not triangulated, triangulate them
          triangulatedInputModelA = vtk.vtkTriangleFilter()
          triangulatedInputModelA.SetInputData(inputModelA.GetPolyData())
          # make strips valid
          triangulatedInputModelA.PassLinesOff()
          triangulatedInputModelA.Update()
          transformerA.SetInputData(triangulatedInputModelA.GetOutput())
          transformerA.Update()
          triangulatedInputModelB = vtk.vtkTriangleFilter()
          triangulatedInputModelB.SetInputData(inputModelB.GetPolyData())
          # make strips valid
          triangulatedInputModelB.PassLinesOff()
          triangulatedInputModelB.Update()
          preTransformerB.SetInputData(triangulatedInputModelB.GetOutput())
          preTransformerB.Update()
          transformerB.SetInputData(preTransformerB.GetOutput())

        # retry with random translation if boolean operation fails
        logging.info(f"Retrying boolean operation with random translation (retry {retry+1})")
        transform = vtk.vtkTransform()
        unitaryVector = [vtk.vtkMath.Random()-0.5 for _ in range(3)]
        vtk.vtkMath.Normalize(unitaryVector)
        import numpy as np
        translationVector = np.array(unitaryVector) * (10**-translateRandomly)
        transform.Translate(translationVector)
        transformerB.SetTransform(transform)
        transformerB.Update()
        # recalculate the boolean operation
        combine.SetInputData(1, transformerB.GetOutput())
        combine.Update()

    outputModel.SetAndObservePolyData(combine.GetOutput())
    outputModel.CreateDefaultDisplayNodes()
    # The filter creates a few scalars, don't show them by default, as they would be somewhat distracting
    outputModel.GetDisplayNode().SetScalarVisibility(False)

    stopTime = time.time()
    logging.info('Processing completed in {0:.2f} seconds'.format(stopTime-startTime))

def saveExecutedMethodWithTelemetry(method):
    PREVIEW_RELEASE_OCTOBER_6TH_2024 = 33047
    def decorated_method(self, *args, **kwargs):
        result = method(self, *args, **kwargs)
        if int(slicer.app.revision) >= PREVIEW_RELEASE_OCTOBER_6TH_2024:
          slicer.app.logUsageEvent("BoneReconstructionPlanner", method.__name__)
        #print("Saved method name: " + method.__name__)
        return result

    return decorated_method