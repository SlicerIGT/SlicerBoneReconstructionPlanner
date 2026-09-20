import logging
import time
import numpy as np
import qt
import slicer
import vtk

from .helperFunctions import createListFromFolderName, getCentroid


VSP_ANIMATION_DURATIONS_SECONDS = {
  # Resection animation
  "resectionSaveState": 0.0,
  "resectionSetView": 0.0,
  "resectionMandibleOnly": 3.0,
  "resectionShowGuide": 3.0,
  "resectionShowPlanes": 5.0,
  "resectionHideGuide": 3.0,
  "resectionExchangeMandible": 3.0,
  "resectionRestoreColor": 3.0,
  "resectionHidePlanes": 3.0,
  "resectionPause": 3.0,
  # Grafting animation
  "graftingSetView": 0.0,
  "graftingFibulaOnly": 3.0,
  "graftingShowGuide": 3.0,
  "graftingShowEachPlane": 1.0,
  "graftingHideGuide": 3.0,
  "graftingShowEachPiecePair": 1.0,
  "graftingHidePlanes": 3.0,
  "graftingJoinPieces": 5.0,
  "graftingHidePieces": 0.0,
  # Reconstruction animation
  "reconstructionSetView": 0.0,
  "reconstructionShowGraft": 5.0,
  "reconstructionRestoreState": 0.0,
}


class VirtualSurgicalPlanAnimation:
  """
  Play and stop the Virtual Surgical Plan animation.
  """

  FRAME_INTERVAL_MS = 33

  def __init__(self, logic, stateChangedCallback = None):
    """
    Initialize the animation controller.
    """
    self.logic = logic
    self.stateChangedCallback = stateChangedCallback
    self.timer = qt.QTimer()
    self.timer.setInterval(self.FRAME_INTERVAL_MS)
    self.timer.connect("timeout()", self._onTimer)
    self.playing = False
    self.animationStepsList = []
    self.currentAnimationStep = None
    self.currentAnimationStepStartedAt = 0.0
    self.displayNodesState = {}
    self.camerasState = {}
    self.initiallyMaximizedViewNodesList = []
    self.currentMaximizedViewNode = None
    self.temporaryTransformsList = []
    self.graftPieceTransformNodeIDsList = []
    self.graftJointsList = []
    self.animationNodes = {}
    self.animationWarningsList = []

  def play(self):
    """
    Validate the Virtual Surgical Plan and play its animation.
    """
    if self.playing:
      return True

    validationError = self._collectAnimationNodes()
    if validationError:
      slicer.util.errorDisplay(validationError)
      return False
    if self.animationWarningsList:
      slicer.util.warningDisplay("\n".join(self.animationWarningsList))

    try:
      self._saveState()
      self._createTemporaryGraftTransforms()
      self.animationStepsList = self._createSteps()
      self.playing = True
      self._notifyStateChanged()
      self._startNextStep()
      return True
    except Exception as exc:
      logging.exception("Unable to start VSP animation")
      self.stop(restore=True)
      slicer.util.errorDisplay("Unable to start VSP animation: %s" % exc)
      return False

  def stop(self, restore = True):
    """
    Stop the animation and optionally restore the initial scene state.
    """
    self.timer.stop()
    wasPlaying = self.playing
    self.playing = False
    self.currentAnimationStep = None
    self.animationStepsList = []
    if restore and self.displayNodesState:
      self._restoreState()
    self._removeTemporaryTransforms()
    if wasPlaying:
      self._notifyStateChanged()

  def _notifyStateChanged(self):
    if self.stateChangedCallback:
      self.stateChangedCallback(self.playing)

  def _collectAnimationNodes(self):
    """
    Collect and validate all nodes needed for the animation.
    """
    parameterNode = self.logic.getParameterNode()
    self.animationWarningsList = []
    if parameterNode.GetParameter("lockVSP") != "True":
      return "Lock the Virtual Surgical Plan before playing its animation."

    mandiblePlanesList = createListFromFolderName("Mandibular planes")
    fibulaPlanesList = createListFromFolderName("Fibula planes")
    cutBonesList = createListFromFolderName("Cut Bones")
    resectedMandible = None
    fibulaPiecesList = []
    for cutBone in cutBonesList:
      if cutBone.GetAttribute("isResectedMandibleModel") == "True":
        resectedMandible = cutBone
      else:
        fibulaPiecesList.append(cutBone)

    self.animationNodes = {
      "mandible": self.logic.getCurrentMandibleModel(),
      "fibula": self.logic.getCurrentFibulaModel(),
      "vessels": self.logic.getCurrentVesselsModel(),
      "mandibleGuide": parameterNode.GetNodeReference("mandibleSurgicalGuidePrototypeModel"),
      "fibulaGuide": parameterNode.GetNodeReference("fibulaSurgicalGuidePrototypeModel"),
      "mandiblePlanes": mandiblePlanesList,
      "resectionPlanes": [mandiblePlanesList[0], mandiblePlanesList[-1]] if len(mandiblePlanesList) >= 2 else [],
      "fibulaPlanes": fibulaPlanesList,
      "fibulaPieces": fibulaPiecesList,
      "cutVessels": createListFromFolderName("Cut Vessels"),
      "resectedMandible": resectedMandible,
      "transformedFibulaPieces": createListFromFolderName("Transformed Fibula Pieces"),
      "transformedVessels": createListFromFolderName("Transformed Vessels Pieces"),
    }

    requiredNodesDict = {
      "mandible model": self.animationNodes["mandible"],
      "fibula model": self.animationNodes["fibula"],
      "resected mandible": self.animationNodes["resectedMandible"],
    }
    missingNodesList = []
    for nodeName, node in requiredNodesDict.items():
      if node is None:
        missingNodesList.append(nodeName)
    if missingNodesList:
      return "Cannot play the VSP animation. Missing: %s." % ", ".join(missingNodesList)
    missingGuidesList = []
    if self.animationNodes["mandibleGuide"] is None:
      missingGuidesList.append("mandible surgical guide")
    if self.animationNodes["fibulaGuide"] is None:
      missingGuidesList.append("fibula surgical guide")
    if missingGuidesList:
      self.animationWarningsList.append(
        "The following models are missing and their animation scenes will be skipped: %s."
        % ", ".join(missingGuidesList)
      )
    if len(mandiblePlanesList) < 2 or len(fibulaPlanesList) == 0 or len(fibulaPiecesList) == 0:
      return "Cannot play the VSP animation because the plan results are incomplete."
    if len(fibulaPlanesList) != 2 * len(fibulaPiecesList):
      return "Cannot play the VSP animation because fibula cutting planes are incomplete."
    if len(self.animationNodes["transformedFibulaPieces"]) != len(fibulaPiecesList):
      return "Cannot play the VSP animation because transformed fibula pieces are incomplete."

    includeVessels = parameterNode.GetParameter("includeVesselsOnPlan") == "True"
    if includeVessels and self.animationNodes["vessels"] is None:
      return "Cannot play the VSP animation because the vessels model is missing."
    if includeVessels and len(self.animationNodes["cutVessels"]) != len(fibulaPiecesList):
      return "Cannot play the VSP animation because cut vessel pieces are incomplete."
    if includeVessels and len(self.animationNodes["transformedVessels"]) != len(fibulaPiecesList):
      return "Cannot play the VSP animation because transformed vessel pieces are incomplete."
    if not includeVessels:
      self.animationNodes["vessels"] = None
      self.animationNodes["cutVessels"] = []
      self.animationNodes["transformedVessels"] = []

    transformMatricesList = self._graftTransformMatrices()
    if len(transformMatricesList) != len(fibulaPiecesList):
      return "Cannot play the VSP animation because fibula piece transforms are incomplete."
    self.animationNodes["graftTransformMatrices"] = transformMatricesList
    return None

  def _graftTransformMatrices(self):
    """
    Get the transforms from the fibula pieces to the reconstructed mandible.
    """
    mandibleToFibulaMatricesList = self.logic.mandibleToFibulaRegistrationTransformMatricesList
    if len(mandibleToFibulaMatricesList) == len(self.animationNodes["fibulaPieces"]):
      fibulaToMandibleMatricesList = []
      for matrix in mandibleToFibulaMatricesList:
        inverseMatrix = vtk.vtkMatrix4x4()
        vtk.vtkMatrix4x4.Invert(matrix, inverseMatrix)
        fibulaToMandibleMatricesList.append(inverseMatrix)
      return fibulaToMandibleMatricesList

    transformNodesList = createListFromFolderName("Bone Pieces Transforms")
    fibulaToMandibleMatricesList = []
    for transformNode in transformNodesList:
      matrix = vtk.vtkMatrix4x4()
      transformNode.GetMatrixTransformToParent(matrix)
      fibulaToMandibleMatricesList.append(matrix)
    return fibulaToMandibleMatricesList

  def _saveState(self):
    """
    Save model, markup, camera, transform, and maximized-view states.
    """
    self.displayNodesState = {}
    for index in range(slicer.mrmlScene.GetNumberOfNodes()):
      node = slicer.mrmlScene.GetNthNode(index)
      if not (node.IsA("vtkMRMLModelNode") or node.IsA("vtkMRMLMarkupsNode")):
        continue
      displayNode = node.GetDisplayNode()
      if displayNode is None:
        continue
      displayNodeState = {
        "visibility": displayNode.GetVisibility(),
        "transformNodeID": node.GetTransformNodeID(),
      }
      if hasattr(displayNode, "GetVisibility2D"):
        displayNodeState["visibility2D"] = displayNode.GetVisibility2D()
      if hasattr(displayNode, "GetVisibility3D"):
        displayNodeState["visibility3D"] = displayNode.GetVisibility3D()
      if hasattr(displayNode, "GetOpacity"):
        displayNodeState["opacity"] = displayNode.GetOpacity()
      if hasattr(displayNode, "GetColor"):
        displayNodeState["color"] = tuple(displayNode.GetColor())
      self.displayNodesState[node.GetID()] = displayNodeState

    self.camerasState = {}
    for singletonTag in (slicer.MANDIBLE_VIEW_SINGLETON_TAG, slicer.FIBULA_VIEW_SINGLETON_TAG):
      viewNode = slicer.mrmlScene.GetSingletonNode(singletonTag, "vtkMRMLViewNode")
      cameraNode = slicer.modules.cameras.logic().GetViewActiveCameraNode(viewNode)
      self.camerasState[viewNode.GetID()] = {
        "position": tuple(cameraNode.GetPosition()),
        "focalPoint": tuple(cameraNode.GetFocalPoint()),
        "viewUp": tuple(cameraNode.GetViewUp()),
        "parallelScale": cameraNode.GetParallelScale(),
      }

    self.initiallyMaximizedViewNodesList = self._getMaximizedViewNodes()

  def _restoreState(self):
    """
    Restore all scene states saved before starting the animation.
    """
    for nodeID, displayNodeState in self.displayNodesState.items():
      node = slicer.mrmlScene.GetNodeByID(nodeID)
      if node is None:
        continue
      node.SetAndObserveTransformNodeID(displayNodeState["transformNodeID"])
      displayNode = node.GetDisplayNode()
      if displayNode is None:
        continue
      displayNode.SetVisibility(displayNodeState["visibility"])
      if "visibility2D" in displayNodeState:
        displayNode.SetVisibility2D(displayNodeState["visibility2D"])
      if "visibility3D" in displayNodeState:
        displayNode.SetVisibility3D(displayNodeState["visibility3D"])
      if "opacity" in displayNodeState:
        displayNode.SetOpacity(displayNodeState["opacity"])
      if "color" in displayNodeState:
        displayNode.SetColor(displayNodeState["color"])

    for viewNodeID, state in self.camerasState.items():
      viewNode = slicer.mrmlScene.GetNodeByID(viewNodeID)
      if viewNode is None:
        continue
      cameraNode = slicer.modules.cameras.logic().GetViewActiveCameraNode(viewNode)
      cameraNode.SetPosition(state["position"])
      cameraNode.SetFocalPoint(state["focalPoint"])
      cameraNode.SetViewUp(state["viewUp"])
      cameraNode.SetParallelScale(state["parallelScale"])
      cameraNode.ResetClippingRange()

    self._restoreMaximizedViews()
    if self.displayNodesState:
      slicer.util.forceRenderAllViews()
    self.displayNodesState = {}
    self.camerasState = {}
    self.initiallyMaximizedViewNodesList = []

  def _getMaximizedViewNodes(self):
    layoutManager = slicer.app.layoutManager()
    try:
      maximizedViewNodes = layoutManager.maximizedViewNodes
      if callable(maximizedViewNodes):
        maximizedViewNodes = maximizedViewNodes()
      return list(maximizedViewNodes)
    except (AttributeError, TypeError):
      return []

  def _restoreMaximizedViews(self):
    layoutManager = slicer.app.layoutManager()
    if self.currentMaximizedViewNode is not None and int(slicer.app.revision) >= 31524:
      layoutManager.removeMaximizedViewNode(self.currentMaximizedViewNode)
    elif int(slicer.app.revision) < 31524:
      layoutManager.setMaximizedViewNode(None)
    self.currentMaximizedViewNode = None
    for viewNode in self.initiallyMaximizedViewNodesList:
      if int(slicer.app.revision) >= 31524:
        layoutManager.addMaximizedViewNode(viewNode)
      else:
        layoutManager.setMaximizedViewNode(viewNode)
        break

  def _createTemporaryGraftTransforms(self):
    """
    Create temporary transforms and collision-free waypoints to assemble the graft.
    """
    fibulaToMandibleMatricesList = self.animationNodes["graftTransformMatrices"]
    mandibleToFirstFibulaMatrix = vtk.vtkMatrix4x4()
    vtk.vtkMatrix4x4.Invert(fibulaToMandibleMatricesList[0], mandibleToFirstFibulaMatrix)

    relativeMatricesList = []
    for matrix in fibulaToMandibleMatricesList:
      relativeMatrix = vtk.vtkMatrix4x4()
      vtk.vtkMatrix4x4.Multiply4x4(mandibleToFirstFibulaMatrix, matrix, relativeMatrix)
      relativeMatricesList.append(relativeMatrix)

    self.temporaryTransformsList = []
    self.graftPieceTransformNodeIDsList = []
    for index, fibulaPiece in enumerate(self.animationNodes["fibulaPieces"]):
      pieceTransformNodeIDsList = [self._addTemporaryTransform(fibulaPiece)]
      if index < len(self.animationNodes["cutVessels"]):
        pieceTransformNodeIDsList.append(
          self._addTemporaryTransform(self.animationNodes["cutVessels"][index])
        )
      self.graftPieceTransformNodeIDsList.append(pieceTransformNodeIDsList)

    self.graftJointsList = []
    fibulaPlanesList = self.animationNodes["fibulaPlanes"]
    fibulaPiecesList = self.animationNodes["fibulaPieces"]
    for pieceIndex in range(1, len(fibulaPiecesList)):
      previousMatrixToFibula = vtk.vtkMatrix4x4()
      vtk.vtkMatrix4x4.Invert(relativeMatricesList[pieceIndex - 1], previousMatrixToFibula)
      targetRelativeMatrix = vtk.vtkMatrix4x4()
      vtk.vtkMatrix4x4.Multiply4x4(
        previousMatrixToFibula,
        relativeMatricesList[pieceIndex],
        targetRelativeMatrix
      )

      previousCapCenter = np.zeros(3)
      currentCapCenter = np.zeros(3)
      fibulaPlanesList[2 * pieceIndex - 1].GetOrigin(previousCapCenter)
      fibulaPlanesList[2 * pieceIndex].GetOrigin(currentCapCenter)

      sourceDirection = currentCapCenter - previousCapCenter
      sourceDistance = np.linalg.norm(sourceDirection)
      if sourceDistance > 0:
        sourceDirection = sourceDirection / sourceDistance

      targetDirection = np.zeros(3)
      fibulaPlanesList[2 * pieceIndex - 1].GetNormal(targetDirection)
      targetDirection = targetDirection / np.linalg.norm(targetDirection)
      currentPieceTargetCentroid = self._transformPoint(
        targetRelativeMatrix,
        getCentroid(fibulaPiecesList[pieceIndex])
      )
      if np.dot(currentPieceTargetCentroid - previousCapCenter, targetDirection) < 0:
        targetDirection = -targetDirection
      if sourceDistance == 0:
        sourceDirection = targetDirection.copy()

      clearanceDistance = sourceDistance

      targetRotationTransform = vtk.vtkTransform()
      targetRotationTransform.SetMatrix(self._rotationOnlyMatrix(targetRelativeMatrix))
      identityTransform = vtk.vtkTransform()
      identityTransform.Identity()
      rotationInterpolator = vtk.vtkTransformInterpolator()
      rotationInterpolator.SetInterpolationTypeToLinear()
      rotationInterpolator.AddTransform(0.0, identityTransform)
      rotationInterpolator.AddTransform(1.0, targetRotationTransform)

      self.graftJointsList.append({
        "previousCapCenter": previousCapCenter,
        "currentCapCenter": currentCapCenter,
        "sourceDirection": sourceDirection,
        "sourceDistance": sourceDistance,
        "targetDirection": targetDirection,
        "clearanceDistance": clearanceDistance,
        "targetRelativeMatrix": targetRelativeMatrix,
        "rotationInterpolator": rotationInterpolator,
        "interpolatedRotationTransform": vtk.vtkTransform(),
      })

  def _addTemporaryTransform(self, modelNode):
    transformNode = slicer.mrmlScene.AddNewNodeByClass(
      "vtkMRMLLinearTransformNode",
      "VSP animation transform",
    )
    transformNode.SetAndObserveTransformNodeID(modelNode.GetTransformNodeID())
    identityTransform = vtk.vtkTransform()
    identityTransform.Identity()
    transformNode.SetMatrixTransformToParent(identityTransform.GetMatrix())
    modelNode.SetAndObserveTransformNodeID(transformNode.GetID())
    self.temporaryTransformsList.append((modelNode.GetID(), transformNode.GetID()))
    return transformNode.GetID()

  def _removeTemporaryTransforms(self):
    for modelNodeID, transformNodeID in self.temporaryTransformsList:
      modelNode = slicer.mrmlScene.GetNodeByID(modelNodeID)
      if modelNode is not None and modelNodeID in self.displayNodesState:
        modelNode.SetAndObserveTransformNodeID(self.displayNodesState[modelNodeID]["transformNodeID"])
      transformNode = slicer.mrmlScene.GetNodeByID(transformNodeID)
      if transformNode is not None:
        slicer.mrmlScene.RemoveNode(transformNode)
    self.temporaryTransformsList = []
    self.graftPieceTransformNodeIDsList = []
    self.graftJointsList = []

  def _rotationOnlyMatrix(self, matrix):
    rotationMatrix = vtk.vtkMatrix4x4()
    rotationMatrix.Identity()
    for row in range(3):
      for column in range(3):
        rotationMatrix.SetElement(row, column, matrix.GetElement(row, column))
    return rotationMatrix

  def _transformPoint(self, matrix, point):
    transformedPoint = [0.0, 0.0, 0.0, 0.0]
    matrix.MultiplyPoint([point[0], point[1], point[2], 1.0], transformedPoint)
    return np.array(transformedPoint[:3])

  def _matrixWithMappedPoint(self, rotationMatrix, sourcePoint, targetPoint):
    matrix = vtk.vtkMatrix4x4()
    matrix.DeepCopy(rotationMatrix)
    rotatedSourcePoint = np.zeros(3)
    for row in range(3):
      rotatedSourcePoint[row] = sum(
        rotationMatrix.GetElement(row, column) * sourcePoint[column]
        for column in range(3)
      )
      matrix.SetElement(row, 3, targetPoint[row] - rotatedSourcePoint[row])
    return matrix

  def _interpolateDirections(self, startDirection, endDirection, progress):
    dotProduct = np.clip(np.dot(startDirection, endDirection), -1.0, 1.0)
    if dotProduct > 0.9995:
      direction = startDirection + progress * (endDirection - startDirection)
      return direction / np.linalg.norm(direction)
    if dotProduct < -0.9995:
      referenceDirection = np.array([1.0, 0.0, 0.0])
      if abs(startDirection[0]) > 0.9:
        referenceDirection = np.array([0.0, 1.0, 0.0])
      orthogonalDirection = np.cross(startDirection, referenceDirection)
      orthogonalDirection = orthogonalDirection / np.linalg.norm(orthogonalDirection)
      return (
        np.cos(np.pi * progress) * startDirection
        + np.sin(np.pi * progress) * orthogonalDirection
      )
    angle = np.arccos(dotProduct)
    return (
      np.sin((1.0 - progress) * angle) * startDirection
      + np.sin(progress * angle) * endDirection
    ) / np.sin(angle)

  def _graftJointMatrix(self, graftJoint, progress):
    separateEnd = 0.2
    rotateEnd = 0.65
    previousCapCenter = graftJoint["previousCapCenter"]
    currentCapCenter = graftJoint["currentCapCenter"]
    clearanceDistance = graftJoint["clearanceDistance"]

    if progress >= 1.0:
      return graftJoint["targetRelativeMatrix"]

    if progress < separateEnd:
      separateProgress = progress / separateEnd
      distance = (
        graftJoint["sourceDistance"]
        + separateProgress * (clearanceDistance - graftJoint["sourceDistance"])
      )
      targetCapCenter = previousCapCenter + graftJoint["sourceDirection"] * distance
      identityMatrix = vtk.vtkMatrix4x4()
      identityMatrix.Identity()
      return self._matrixWithMappedPoint(identityMatrix, currentCapCenter, targetCapCenter)

    if progress < rotateEnd:
      rotateProgress = (progress - separateEnd) / (rotateEnd - separateEnd)
      graftJoint["rotationInterpolator"].InterpolateTransform(
        rotateProgress,
        graftJoint["interpolatedRotationTransform"]
      )
      capDirection = self._interpolateDirections(
        graftJoint["sourceDirection"],
        graftJoint["targetDirection"],
        rotateProgress
      )
      targetCapCenter = previousCapCenter + capDirection * clearanceDistance
      return self._matrixWithMappedPoint(
        graftJoint["interpolatedRotationTransform"].GetMatrix(),
        currentCapCenter,
        targetCapCenter
      )

    approachProgress = (progress - rotateEnd) / (1.0 - rotateEnd)
    targetCapCenter = (
      previousCapCenter
      + graftJoint["targetDirection"] * clearanceDistance * (1.0 - approachProgress)
    )
    return self._matrixWithMappedPoint(
      self._rotationOnlyMatrix(graftJoint["targetRelativeMatrix"]),
      currentCapCenter,
      targetCapCenter
    )

  def _createSteps(self):
    """
    Create the ordered list of animation shots and their durations.
    """
    animationDurationsDict = VSP_ANIMATION_DURATIONS_SECONDS
    fibulaPlaneDuration = animationDurationsDict["graftingShowEachPlane"] * len(self.animationNodes["fibulaPlanes"])
    piecePairDuration = animationDurationsDict["graftingShowEachPiecePair"] * len(self.animationNodes["fibulaPieces"])
    mandibleColor = tuple(self.animationNodes["mandible"].GetDisplayNode().GetColor())
    resectedColor = self.displayNodesState[self.animationNodes["resectedMandible"].GetID()]["color"]

    animationStepsList = [
      (animationDurationsDict["resectionSaveState"], lambda progress: None),
      (animationDurationsDict["resectionSetView"], lambda progress: self._setView("mandible")),
      (animationDurationsDict["resectionMandibleOnly"], lambda progress: self._showOnly([self.animationNodes["mandible"]])),
    ]
    if self.animationNodes["mandibleGuide"] is not None:
      animationStepsList.append(
        (animationDurationsDict["resectionShowGuide"], lambda progress: self._fadeNodes([self.animationNodes["mandibleGuide"]], progress, True))
      )
    animationStepsList.append(
      (animationDurationsDict["resectionShowPlanes"], lambda progress: self._showSequentially(self.animationNodes["resectionPlanes"], progress))
    )
    if self.animationNodes["mandibleGuide"] is not None:
      animationStepsList.append(
        (animationDurationsDict["resectionHideGuide"], lambda progress: self._fadeNodes([self.animationNodes["mandibleGuide"]], progress, False))
      )
    animationStepsList.extend([
      (animationDurationsDict["resectionExchangeMandible"], lambda progress: self._exchangeMandible(progress, mandibleColor)),
      (animationDurationsDict["resectionRestoreColor"], lambda progress: self._interpolateColor(self.animationNodes["resectedMandible"], mandibleColor, resectedColor, progress)),
      (animationDurationsDict["resectionHidePlanes"], lambda progress: self._fadeNodes(self.animationNodes["resectionPlanes"], progress, False)),
      (animationDurationsDict["resectionPause"], lambda progress: None),
      (animationDurationsDict["graftingSetView"], lambda progress: self._setView("fibula")),
      (animationDurationsDict["graftingFibulaOnly"], lambda progress: self._showOnly([self.animationNodes["fibula"]])),
    ])
    if self.animationNodes["fibulaGuide"] is not None:
      animationStepsList.append(
        (animationDurationsDict["graftingShowGuide"], lambda progress: self._fadeNodes([self.animationNodes["fibulaGuide"]], progress, True))
      )
    animationStepsList.append(
      (fibulaPlaneDuration, lambda progress: self._showSequentially(self.animationNodes["fibulaPlanes"], progress))
    )
    if self.animationNodes["fibulaGuide"] is not None:
      animationStepsList.append(
        (animationDurationsDict["graftingHideGuide"], lambda progress: self._fadeNodes([self.animationNodes["fibulaGuide"]], progress, False))
      )
    animationStepsList.extend([
      (piecePairDuration, self._exchangeFibulaForPieces),
      (animationDurationsDict["graftingHidePlanes"], lambda progress: self._fadeNodes(self.animationNodes["fibulaPlanes"], progress, False)),
      (animationDurationsDict["graftingJoinPieces"], self._joinGraft),
      (animationDurationsDict["graftingHidePieces"], lambda progress: self._hideNodes(self.animationNodes["fibulaPieces"] + self.animationNodes["cutVessels"])),
      (animationDurationsDict["reconstructionSetView"], lambda progress: self._prepareReconstructionView()),
      (animationDurationsDict["reconstructionShowGraft"], lambda progress: self._fadeNodes(self.animationNodes["transformedFibulaPieces"] + self.animationNodes["transformedVessels"], progress, True)),
      (animationDurationsDict["reconstructionRestoreState"], lambda progress: self.stop(restore = True)),
    ])
    return animationStepsList

  def _startNextStep(self):
    if not self.playing:
      return
    if not self.animationStepsList:
      self.stop(restore=True)
      return

    self.currentAnimationStep = self.animationStepsList.pop(0)
    duration, update = self.currentAnimationStep
    self.currentAnimationStepStartedAt = time.monotonic()
    try:
      if duration <= 0.0:
        update(1.0)
        if self.playing:
          qt.QTimer.singleShot(0, self._startNextStep)
      else:
        update(0.0)
        self.timer.start()
    except Exception as exc:
      logging.exception("VSP animation stopped because a shot failed")
      self.stop(restore=True)
      slicer.util.errorDisplay("VSP animation stopped: %s" % exc)

  def _onTimer(self):
    if not self.playing or self.currentAnimationStep is None:
      self.timer.stop()
      return
    duration, update = self.currentAnimationStep
    progress = min(1.0, (time.monotonic() - self.currentAnimationStepStartedAt) / duration)
    try:
      update(progress)
      slicer.util.forceRenderAllViews()
    except Exception as exc:
      logging.exception("VSP animation stopped because a shot failed")
      self.stop(restore=True)
      slicer.util.errorDisplay("VSP animation stopped: %s" % exc)
      return
    if progress >= 1.0:
      self.timer.stop()
      self._startNextStep()

  def _setView(self, viewName):
    viewNode = self._viewNode(viewName)
    layoutManager = slicer.app.layoutManager()
    if int(slicer.app.revision) >= 31524:
      if self.currentMaximizedViewNode is None:
        for initiallyMaximizedViewNode in self.initiallyMaximizedViewNodesList:
          layoutManager.removeMaximizedViewNode(initiallyMaximizedViewNode)
      else:
        layoutManager.removeMaximizedViewNode(self.currentMaximizedViewNode)
      layoutManager.addMaximizedViewNode(viewNode)
    else:
      layoutManager.setMaximizedViewNode(None)
      layoutManager.setMaximizedViewNode(viewNode)
    self.currentMaximizedViewNode = viewNode

    if viewName == "mandible":
      modelNode = self.animationNodes["mandible"]
      cameraDirection = np.array([0.0, -1.0, 0.0])
      viewUpDirection = np.array([0.0, 0.0, 1.0])
    else:
      modelNode = self.animationNodes["fibula"]
      donorLeg = self.logic.getParameterNode().GetParameter("donorLeg")
      cameraDirection = np.array([-1.0, 0.0, 0.0]) if donorLeg == "Right" else np.array([1.0, 0.0, 0.0])
      viewUpDirection = np.array([0.0, 1.0, 0.0])

    centroid = getCentroid(modelNode)
    cameraNode = slicer.modules.cameras.logic().GetViewActiveCameraNode(viewNode)
    cameraNode.SetPosition(centroid - cameraDirection * 300.0)
    cameraNode.SetFocalPoint(centroid)
    cameraNode.SetViewUp(viewUpDirection)
    cameraNode.ResetClippingRange()

  def _viewNode(self, viewName):
    singletonTag = (
      slicer.MANDIBLE_VIEW_SINGLETON_TAG
      if viewName == "mandible"
      else slicer.FIBULA_VIEW_SINGLETON_TAG
    )
    return slicer.mrmlScene.GetSingletonNode(singletonTag, "vtkMRMLViewNode")

  def _showOnly(self, nodesList):
    self._hideAllModelsAndMarkups()
    for node in nodesList:
      self._setNodeVisible(node, True, self._savedOpacity(node))

  def _prepareReconstructionView(self):
    self._setView("mandible")
    self._showOnly([self.animationNodes["resectedMandible"]])

  def _hideAllModelsAndMarkups(self):
    for nodeID in self.displayNodesState:
      node = slicer.mrmlScene.GetNodeByID(nodeID)
      if node is not None and node.GetDisplayNode() is not None:
        node.GetDisplayNode().SetVisibility(False)

  def _savedOpacity(self, node):
    return self.displayNodesState.get(node.GetID(), {}).get("opacity", 1.0)

  def _setNodeVisible(self, node, visible, opacity = None):
    if node is None or node.GetDisplayNode() is None:
      return
    displayNode = node.GetDisplayNode()
    if opacity is not None and hasattr(displayNode, "SetOpacity"):
      displayNode.SetOpacity(opacity)
    displayNode.SetVisibility(visible)

  def _hideNodes(self, nodesList):
    for node in nodesList:
      self._setNodeVisible(node, False)

  def _fadeNodes(self, nodesList, progress, showing):
    for node in nodesList:
      if node is None:
        continue
      targetOpacity = self._savedOpacity(node)
      opacity = targetOpacity * (progress if showing else 1.0 - progress)
      self._setNodeVisible(node, showing or progress < 1.0, opacity)

  def _showSequentially(self, nodesList, progress):
    visibleCount = min(len(nodesList), int(progress * len(nodesList)) + (1 if progress > 0.0 else 0))
    for index, node in enumerate(nodesList):
      self._setNodeVisible(node, index < visibleCount, self._savedOpacity(node))

  def _exchangeMandible(self, progress, mandibleColor):
    resectedMandible = self.animationNodes["resectedMandible"]
    resectedMandible.GetDisplayNode().SetColor(mandibleColor)
    self._fadeNodes([resectedMandible], progress, True)
    self._fadeNodes([self.animationNodes["mandible"]], progress, False)

  def _interpolateColor(self, node, startColor, endColor, progress):
    color = [
      startColor[index] + (endColor[index] - startColor[index]) * progress
      for index in range(3)
    ]
    node.GetDisplayNode().SetColor(color)

  def _exchangeFibulaForPieces(self, progress):
    fibulaPiecesList = self.animationNodes["fibulaPieces"]
    cutVesselsList = self.animationNodes["cutVessels"]
    for index, fibulaPiece in enumerate(fibulaPiecesList):
      localProgress = min(1.0, max(0.0, progress * len(fibulaPiecesList) - index))
      fibulaPieceAndVesselList = [fibulaPiece]
      if index < len(cutVesselsList):
        fibulaPieceAndVesselList.append(cutVesselsList[index])
      self._fadeNodes(fibulaPieceAndVesselList, localProgress, True)
    self._fadeNodes([self.animationNodes["fibula"], self.animationNodes["vessels"]], progress, False)

  def _joinGraft(self, progress):
    numberOfJoints = len(self.graftJointsList)
    if numberOfJoints == 0:
      return

    currentPieceMatrix = vtk.vtkMatrix4x4()
    currentPieceMatrix.Identity()
    for pieceIndex in range(1, len(self.graftPieceTransformNodeIDsList)):
      jointProgress = min(1.0, max(0.0, progress * numberOfJoints - (pieceIndex - 1)))
      jointMatrix = self._graftJointMatrix(
        self.graftJointsList[pieceIndex - 1],
        jointProgress
      )
      nextPieceMatrix = vtk.vtkMatrix4x4()
      vtk.vtkMatrix4x4.Multiply4x4(currentPieceMatrix, jointMatrix, nextPieceMatrix)
      currentPieceMatrix = nextPieceMatrix
      for transformNodeID in self.graftPieceTransformNodeIDsList[pieceIndex]:
        transformNode = slicer.mrmlScene.GetNodeByID(transformNodeID)
        if transformNode is not None:
          transformNode.SetMatrixTransformToParent(currentPieceMatrix)