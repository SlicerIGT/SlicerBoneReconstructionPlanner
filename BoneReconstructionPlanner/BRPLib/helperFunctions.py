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
  auxiliarFiducial.AddFiducialFromArray(point)

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
  miterBoxSource = vtk.vtkCubeSource()
  miterBoxSource.SetXLength(X)
  miterBoxSource.SetYLength(Y)
  miterBoxSource.SetZLength(Z)
  triangleFilter = vtk.vtkTriangleFilter()
  triangleFilter.SetInputConnection(miterBoxSource.GetOutputPort())
  #triangleFilter.Update()
  miterBox.SetPolyDataConnection(triangleFilter.GetOutputPort())
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
  #tubeFilter.Update()
  cylinder.SetPolyDataConnection(tubeFilter.GetOutputPort())
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