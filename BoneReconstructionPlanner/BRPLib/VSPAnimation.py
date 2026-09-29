import logging
import os
import shutil
import tempfile
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
  "graftingFibulaOnly": 0.5,
  "graftingZoomFibula": 2.0,
  "graftingShowGuide": 3.0,
  "graftingShowEachPlane": 1.0,
  "graftingHideGuide": 3.0,
  "graftingShowEachPiecePair": 1.0,
  "graftingHidePlanes": 3.0,
  "graftingRotateView": 3.0,
  "graftingJoinPieces": 5.0,
  "graftingHidePieces": 0.0,
  # Reconstruction animation
  "reconstructionSetView": 0.0,
  "reconstructionShowGraft": 5.0,
  "reconstructionRotateView": 3.0,
  "reconstructionPause": 3.0,
  "reconstructionRestoreState": 0.0,
}

VSP_ANIMATION_VIDEO_FRAME_RATE = 30
VSP_ANIMATION_VIDEO_OPTIONS = "-codec libx264 -preset slower -pix_fmt yuv420p"

# Wet bone sheen under the MultiLamp lighting
VSP_ANIMATION_BONE_MATERIAL = {
  "Specular": 0.25,
  "Power": 20.0,
}
# A cut plane that never matches any position
VSP_ANIMATION_NO_CUT_PLANE = [0.0, 0.0, 0.0, 1.0]

# The bone texture is computed per pixel from the model coordinates (a solid texture),
# so the models need no texture coordinates and the texture moves with each bone piece.
# The model coordinates are computed from the view coordinates because the vertex buffer
# coordinates (vertexMC) are shifted and scaled by VTK
VSP_ANIMATION_BONE_FRAGMENT_SHADER_DECLARATIONS = """//VTK::Normal::Dec
float boneHash(vec3 cell)
{
  // Wrap the lattice so the hash stays precise at scene coordinates of hundreds of millimeters
  cell = mod(cell, 289.0);
  return fract(sin(dot(cell, vec3(12.9898, 78.233, 37.719))) * 43758.5453);
}

float boneNoise(vec3 position)
{
  vec3 cell = floor(position);
  vec3 fraction = fract(position);
  fraction = fraction * fraction * (3.0 - 2.0 * fraction);
  float noise00 = mix(boneHash(cell), boneHash(cell + vec3(1.0, 0.0, 0.0)), fraction.x);
  float noise10 = mix(boneHash(cell + vec3(0.0, 1.0, 0.0)), boneHash(cell + vec3(1.0, 1.0, 0.0)), fraction.x);
  float noise01 = mix(boneHash(cell + vec3(0.0, 0.0, 1.0)), boneHash(cell + vec3(1.0, 0.0, 1.0)), fraction.x);
  float noise11 = mix(boneHash(cell + vec3(0.0, 1.0, 1.0)), boneHash(cell + vec3(1.0, 1.0, 1.0)), fraction.x);
  return mix(mix(noise00, noise10, fraction.y), mix(noise01, noise11, fraction.y), fraction.z);
}

float boneFbm(vec3 position)
{
  float value = 0.0;
  float amplitude = 0.5;
  for (int octave = 0; octave < 4; octave++)
  {
    value += amplitude * boneNoise(position);
    position = position * 2.03 + vec3(17.1, 31.7, 11.3);
    amplitude *= 0.5;
  }
  return value / 0.9375;
}

float boneCutFactor(vec4 cutPlane, vec3 position)
{
  return 1.0 - smoothstep(0.05, 0.3, abs(dot(cutPlane.xyz, position) - cutPlane.w));
}
"""

# Screen space derivatives (dFdx) are only valid before any fragment is discarded (e.g. by depth peeling)
VSP_ANIMATION_BONE_FRAGMENT_SHADER_UNIFORM_FLOW = """//VTK::UniformFlow::Impl
  vec3 bonePosition = vec3(
    dot(boneViewToModelRow0, vertexVC),
    dot(boneViewToModelRow1, vertexVC),
    dot(boneViewToModelRow2, vertexVC));
  float boneMottling = boneFbm(bonePosition * 0.15);
  float bonePatches = boneFbm(bonePosition * 0.06 + vec3(41.0, 7.0, 23.0));
  float bonePores = boneFbm(bonePosition * 2.2);
  float boneMarrow = boneFbm(bonePosition * 2.5 + vec3(5.0, 59.0, 13.0));
  float boneCut = max(boneCutFactor(boneCutPlane0, bonePosition), boneCutFactor(boneCutPlane1, bonePosition));
  float boneHeight = 0.06 * (0.5 * boneMottling - bonePores) * (1.0 - boneCut);
  vec3 bonePositionDx = dFdx(vertexVC.xyz);
  vec3 bonePositionDy = dFdy(vertexVC.xyz);
  float boneHeightDx = dFdx(boneHeight);
  float boneHeightDy = dFdy(boneHeight);
"""

VSP_ANIMATION_BONE_FRAGMENT_SHADER_IMPLEMENTATION = """//VTK::Normal::Impl
  // Ivory cortical bone with blood tinted patches and small dark pores
  vec3 boneColor = mix(vec3(0.80, 0.72, 0.58), vec3(0.93, 0.89, 0.80), smoothstep(0.3, 0.7, boneMottling));
  boneColor = mix(boneColor, vec3(0.83, 0.60, 0.53), 0.4 * smoothstep(0.55, 0.75, bonePatches));
  boneColor *= 1.0 - 0.18 * smoothstep(0.62, 0.82, bonePores);
  // Osteotomy faces show pale sawn bone with red marrow speckles
  vec3 boneCutColor = mix(vec3(0.92, 0.86, 0.80), vec3(0.62, 0.18, 0.15), smoothstep(0.6, 0.8, boneMarrow));
  boneColor = mix(boneColor, boneCutColor, boneCut);
  diffuseColor = diffuseIntensity * boneColor;
  ambientColor = ambientIntensity * boneColor;
  // Bump the normal along the pores (surface gradient bump mapping)
  vec3 boneR1 = cross(bonePositionDy, normalVCVSOutput);
  vec3 boneR2 = cross(normalVCVSOutput, bonePositionDx);
  float boneDeterminant = dot(bonePositionDx, boneR1);
  vec3 boneSurfaceGradient = sign(boneDeterminant) * (boneHeightDx * boneR1 + boneHeightDy * boneR2);
  normalVCVSOutput = normalize(max(abs(boneDeterminant), 1e-10) * normalVCVSOutput - boneSurfaceGradient);
"""

VSP_ANIMATION_BONE_FRAGMENT_SHADER_REPLACEMENTS = {
  "//VTK::Normal::Dec": VSP_ANIMATION_BONE_FRAGMENT_SHADER_DECLARATIONS,
  "//VTK::UniformFlow::Impl": VSP_ANIMATION_BONE_FRAGMENT_SHADER_UNIFORM_FLOW,
  "//VTK::Normal::Impl": VSP_ANIMATION_BONE_FRAGMENT_SHADER_IMPLEMENTATION,
}

VSP_ANIMATION_BONE_FRAGMENT_SHADER_UNIFORMS = [
  "boneCutPlane0",
  "boneCutPlane1",
  "boneViewToModelRow0",
  "boneViewToModelRow1",
  "boneViewToModelRow2",
]


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
    self.lightingState = {}
    self.multiLampLightKit = vtk.vtkLightKit()
    self.multiLampLightKit.MaintainLuminanceOn()
    self.boneTexturesDict = {}
    self.boneTexturesViewsList = []
    self.initiallyMaximizedViewNodesList = []
    self.currentMaximizedViewNode = None
    self.temporaryTransformsList = []
    self.graftPieceTransformNodeIDsList = []
    self.graftJointsList = []
    self.animationNodes = {}
    self.animationWarningsList = []
    self.mandibleViewCamera = None
    self.fibulaFullViewCamera = None
    self.fibulaZoomedViewCamera = None
    self.fibulaAssemblyViewCamera = None

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
      self._setMultiLampLighting()
      self._setOperatingRoomBackground()
      self._setBoneTextures()
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
    self.mandibleViewCamera = None
    self.fibulaFullViewCamera = None
    self.fibulaZoomedViewCamera = None
    self.fibulaAssemblyViewCamera = None
    if restore and self.displayNodesState:
      self._restoreState()
    self._removeTemporaryTransforms()
    if wasPlaying:
      self._notifyStateChanged()

  def exportVideo(self, videoFilePath):
    """
    Render the Virtual Surgical Plan animation frame by frame and save it as a video.
    """
    if self.playing:
      return False

    import ScreenCapture
    screenCaptureLogic = ScreenCapture.ScreenCaptureLogic()
    if not screenCaptureLogic.isFfmpegPathValid():
      screenCaptureLogic.findFfmpeg()
    if not screenCaptureLogic.isFfmpegPathValid() and os.name == "nt":
      if slicer.util.confirmOkCancelDisplay(
        "Video encoder not detected on your system. Download ffmpeg video encoder?",
        windowTitle = "Download confirmation"
      ):
        if not screenCaptureLogic.ffmpegDownload():
          slicer.util.errorDisplay("ffmpeg download failed")
    if not screenCaptureLogic.isFfmpegPathValid():
      slicer.util.errorDisplay(
        "Cannot export the VSP animation because the ffmpeg video encoder was not found. "
        "Install ffmpeg and set its path in the Screen Capture module (Advanced section)."
      )
      return False

    validationError = self._collectAnimationNodes()
    if validationError:
      slicer.util.errorDisplay(validationError)
      return False
    if self.animationWarningsList:
      slicer.util.warningDisplay("\n".join(self.animationWarningsList))

    framesDirectory = tempfile.mkdtemp(prefix = "BRPVSPAnimation-", dir = slicer.app.temporaryPath)
    # JPEG frames are written many times faster than PNG frames
    frameFileNamePattern = "frame-%05d.jpg"
    progressDialog = None
    try:
      self._saveState()
      self._setMultiLampLighting()
      self._setOperatingRoomBackground()
      self._setBoneTextures()
      self._createTemporaryGraftTransforms()
      self.animationStepsList = self._createSteps()
      progressDialog = slicer.util.createProgressDialog(
        windowTitle = "Exporting VSP animation",
        labelText = "Rendering animation frames...",
        value = 0,
        maximum = self._numberOfVideoFrames(),
        windowModality = qt.Qt.WindowModal,
        autoClose = False,
        autoReset = False,
      )
      self.playing = True
      self._notifyStateChanged()

      numberOfCapturedFrames = 0
      frameSize = None
      while self.playing and self.animationStepsList:
        self.currentAnimationStep = self.animationStepsList.pop(0)
        duration, update = self.currentAnimationStep
        if duration <= 0.0:
          update(1.0)
          continue
        update(0.0)
        numberOfStepFrames = self._numberOfStepVideoFrames(duration)
        for stepFrameIndex in range(numberOfStepFrames):
          if not self.playing:
            break
          update((stepFrameIndex + 1) / numberOfStepFrames)
          frameFilePath = os.path.join(framesDirectory, frameFileNamePattern % numberOfCapturedFrames)
          view = screenCaptureLogic.viewFromNode(self.currentMaximizedViewNode)
          screenCaptureLogic.captureImageFromView(view, frameFilePath)
          if frameSize is None:
            frameSize = self._imageFileSize(frameFilePath)
          numberOfCapturedFrames += 1
          progressDialog.value = numberOfCapturedFrames
          if progressDialog.wasCanceled:
            self.stop(restore = True)

      canceled = progressDialog.wasCanceled
      self.stop(restore = True)
      if canceled or numberOfCapturedFrames == 0:
        logging.info("VSP animation export canceled")
        return False

      progressDialog.labelText = "Encoding video..."
      slicer.app.processEvents()
      ffmpegParametersList = [
        screenCaptureLogic.getFfmpegPath(),
        "-nostdin",
        "-y",
        "-r", str(VSP_ANIMATION_VIDEO_FRAME_RATE),
        "-start_number", "0",
        "-i", os.path.join(framesDirectory, frameFileNamePattern),
      ]
      ffmpegParametersList.extend(VSP_ANIMATION_VIDEO_OPTIONS.split(" "))
      # Scale every frame to the size of the first one because the encoder needs a constant size
      ffmpegParametersList.extend(["-vf", "scale=%d:%d" % (frameSize[0], frameSize[1])])
      ffmpegParametersList.append(videoFilePath)
      # Slicer library paths can break a system ffmpeg, so launch it with the startup environment
      ffmpegProcess = slicer.util.launchConsoleProcess(ffmpegParametersList, useStartupEnvironment = True)
      slicer.util.logProcessOutput(ffmpegProcess)
      logging.info("VSP animation exported to %s" % videoFilePath)
      return True
    except Exception as exc:
      logging.exception("Unable to export VSP animation")
      self.stop(restore = True)
      slicer.util.errorDisplay("Unable to export VSP animation: %s" % exc)
      return False
    finally:
      if progressDialog is not None:
        progressDialog.close()
      shutil.rmtree(framesDirectory, ignore_errors = True)

  def _numberOfStepVideoFrames(self, duration):
    return max(1, int(round(duration * VSP_ANIMATION_VIDEO_FRAME_RATE)))

  def _numberOfVideoFrames(self):
    numberOfFrames = 0
    for duration, update in self.animationStepsList:
      if duration > 0.0:
        numberOfFrames += self._numberOfStepVideoFrames(duration)
    return numberOfFrames

  def _imageFileSize(self, imageFilePath):
    reader = vtk.vtkJPEGReader()
    reader.SetFileName(imageFilePath)
    reader.Update()
    dimensions = reader.GetOutput().GetDimensions()
    return dimensions[0], dimensions[1]

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
    Save model, markup, camera, transform, lighting, background, and maximized-view states.
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
      if hasattr(displayNode, "GetInterpolation"):
        displayNodeState["interpolation"] = displayNode.GetInterpolation()
      if hasattr(displayNode, "GetSpecular"):
        displayNodeState["specular"] = displayNode.GetSpecular()
      if hasattr(displayNode, "GetPower"):
        displayNodeState["power"] = displayNode.GetPower()
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

    self.lightingState = {}
    layoutManager = slicer.app.layoutManager()
    for index in range(layoutManager.threeDViewCount):
      threeDView = layoutManager.threeDWidget(index).threeDView()
      viewNode = threeDView.mrmlViewNode()
      renderer = threeDView.renderWindow().GetRenderers().GetFirstRenderer()
      lightsList = []
      for lightIndex in range(renderer.GetLights().GetNumberOfItems()):
        lightsList.append(renderer.GetLights().GetItemAsObject(lightIndex))
      environmentUp = [0.0, 0.0, 0.0]
      renderer.GetEnvironmentUp(environmentUp)
      environmentRight = [0.0, 0.0, 0.0]
      renderer.GetEnvironmentRight(environmentRight)
      viewLightingState = {
        "lightsList": lightsList,
        "environmentUp": environmentUp,
        "environmentRight": environmentRight,
      }
      if hasattr(viewNode, "GetShadowsVisibility"):
        viewLightingState["shadowsVisibility"] = viewNode.GetShadowsVisibility()
      self.lightingState[viewNode.GetID()] = viewLightingState

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
      if "interpolation" in displayNodeState:
        displayNode.SetInterpolation(displayNodeState["interpolation"])
      if "specular" in displayNodeState:
        displayNode.SetSpecular(displayNodeState["specular"])
      if "power" in displayNodeState:
        displayNode.SetPower(displayNodeState["power"])

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

    layoutManager = slicer.app.layoutManager()
    for index in range(layoutManager.threeDViewCount):
      threeDView = layoutManager.threeDWidget(index).threeDView()
      viewNode = threeDView.mrmlViewNode()
      if viewNode.GetID() not in self.lightingState:
        continue
      viewLightingState = self.lightingState[viewNode.GetID()]
      renderer = threeDView.renderWindow().GetRenderers().GetFirstRenderer()
      renderer.RemoveAllLights()
      for light in viewLightingState["lightsList"]:
        renderer.AddLight(light)
      if "operatingRoomSkybox" in viewLightingState:
        renderer.RemoveActor(viewLightingState["operatingRoomSkybox"])
      renderer.SetEnvironmentUp(viewLightingState["environmentUp"])
      renderer.SetEnvironmentRight(viewLightingState["environmentRight"])
      if "shadowsVisibility" in viewLightingState:
        viewNode.SetShadowsVisibility(viewLightingState["shadowsVisibility"])
    self._removeBoneTextures()

    self._restoreMaximizedViews()
    if self.displayNodesState:
      slicer.util.forceRenderAllViews()
    self.displayNodesState = {}
    self.camerasState = {}
    self.lightingState = {}
    self.initiallyMaximizedViewNodesList = []

  def _setMultiLampLighting(self):
    """
    Light the 3D views like the "MultiLamp" lighting mode: a light kit without shadows.
    """
    layoutManager = slicer.app.layoutManager()
    for index in range(layoutManager.threeDViewCount):
      threeDView = layoutManager.threeDWidget(index).threeDView()
      viewNode = threeDView.mrmlViewNode()
      if viewNode.GetID() not in self.lightingState:
        continue
      renderer = threeDView.renderWindow().GetRenderers().GetFirstRenderer()
      renderer.RemoveAllLights()
      self.multiLampLightKit.AddLightsToRenderer(renderer)
      if hasattr(viewNode, "SetShadowsVisibility"):
        viewNode.SetShadowsVisibility(False)
      threeDView.scheduleRender()

  def _operatingRoomImageFilePath(self):
    """
    Return the operating room panorama of the Lights module (Sandbox extension) or None if not available.
    """
    if not hasattr(slicer.modules, "lights"):
      return None
    imageFilePath = os.path.join(os.path.dirname(slicer.modules.lights.path), "Resources", "hospital_room.jpg")
    if not os.path.exists(imageFilePath):
      return None
    return imageFilePath

  def _setOperatingRoomBackground(self):
    """
    Show the operating room panorama of the Lights module behind the models of the 3D views.
    """
    imageFilePath = self._operatingRoomImageFilePath()
    if imageFilePath is None:
      logging.warning("Operating room image of the Lights module not found. The VSP animation will keep the view background.")
      return
    imageReader = vtk.vtkJPEGReader()
    imageReader.SetFileName(imageFilePath)
    layoutManager = slicer.app.layoutManager()
    for index in range(layoutManager.threeDViewCount):
      threeDView = layoutManager.threeDWidget(index).threeDView()
      viewNode = threeDView.mrmlViewNode()
      if viewNode.GetID() not in self.lightingState:
        continue
      if viewNode.GetRenderMode() == slicer.vtkMRMLViewNode.Orthographic:
        # The skybox is only drawn correctly with perspective projection
        continue
      # Each view has its own OpenGL context so it needs its own texture
      texture = vtk.vtkTexture()
      texture.SetInputConnection(imageReader.GetOutputPort())
      texture.SetColorModeToDirectScalars()
      texture.InterpolateOn()
      skybox = vtk.vtkSkybox()
      skybox.SetTexture(texture)
      # The image is an equirectangular panorama
      skybox.SetProjectionToSphere()
      renderer = threeDView.renderWindow().GetRenderers().GetFirstRenderer()
      renderer.AddActor(skybox)
      self.lightingState[viewNode.GetID()]["operatingRoomSkybox"] = skybox
      threeDView.scheduleRender()

  def _orientOperatingRoomBackground(self, viewNode, cameraDirection, viewUpDirection):
    """
    Keep the floor of the operating room down on the screen and the operating lamp side of the room behind the models.
    """
    environmentRight = np.cross(cameraDirection, viewUpDirection)
    layoutManager = slicer.app.layoutManager()
    for index in range(layoutManager.threeDViewCount):
      threeDView = layoutManager.threeDWidget(index).threeDView()
      if threeDView.mrmlViewNode() != viewNode:
        continue
      renderer = threeDView.renderWindow().GetRenderers().GetFirstRenderer()
      renderer.SetEnvironmentUp(viewUpDirection[0], viewUpDirection[1], viewUpDirection[2])
      renderer.SetEnvironmentRight(environmentRight[0], environmentRight[1], environmentRight[2])

  def _setBoneTextures(self):
    """
    Make the bone models look like real bone during the animation, with sawn bone on the osteotomy faces.
    """
    noCutPlanesList = [VSP_ANIMATION_NO_CUT_PLANE, VSP_ANIMATION_NO_CUT_PLANE]
    boneModelsList = [self.animationNodes["mandible"], self.animationNodes["fibula"]]
    cutPlanesListsList = [noCutPlanesList, noCutPlanesList]

    resectedMandible = self.animationNodes["resectedMandible"]
    resectionPlanesList = self.animationNodes["resectionPlanes"]
    boneModelsList.append(resectedMandible)
    cutPlanesListsList.append([
      self._planeInModelCoordinates(resectionPlanesList[0], resectedMandible),
      self._planeInModelCoordinates(resectionPlanesList[1], resectedMandible),
    ])

    fibulaPlanesList = self.animationNodes["fibulaPlanes"]
    fibulaPiecesList = self.animationNodes["fibulaPieces"]
    transformedFibulaPiecesList = self.animationNodes["transformedFibulaPieces"]
    fibulaToMandibleMatricesList = self.animationNodes["graftTransformMatrices"]
    for pieceIndex in range(len(fibulaPiecesList)):
      fibulaPiece = fibulaPiecesList[pieceIndex]
      pieceCutPlanesList = [
        self._planeInModelCoordinates(fibulaPlanesList[2 * pieceIndex], fibulaPiece),
        self._planeInModelCoordinates(fibulaPlanesList[2 * pieceIndex + 1], fibulaPiece),
      ]
      boneModelsList.append(fibulaPiece)
      cutPlanesListsList.append(pieceCutPlanesList)
      # Transformed fibula pieces are copies of the fibula pieces with the fibula to mandible transform hardened
      boneModelsList.append(transformedFibulaPiecesList[pieceIndex])
      cutPlanesListsList.append([
        self._transformPlane(fibulaToMandibleMatricesList[pieceIndex], pieceCutPlanesList[0]),
        self._transformPlane(fibulaToMandibleMatricesList[pieceIndex], pieceCutPlanesList[1]),
      ])

    self.boneTexturesDict = {}
    for index in range(len(boneModelsList)):
      displayNode = boneModelsList[index].GetDisplayNode()
      if displayNode is None:
        continue
      # The shader modifies the Gouraud lighting inputs so PBR is not used during the animation
      displayNode.SetInterpolation(slicer.vtkMRMLDisplayNode.GouraudInterpolation)
      displayNode.SetSpecular(VSP_ANIMATION_BONE_MATERIAL["Specular"])
      displayNode.SetPower(VSP_ANIMATION_BONE_MATERIAL["Power"])
      self.boneTexturesDict[displayNode.GetID()] = cutPlanesListsList[index]

    # The shader is added and updated right before each render of the 3D views
    self.boneTexturesViewsList = []
    layoutManager = slicer.app.layoutManager()
    for index in range(layoutManager.threeDViewCount):
      threeDView = layoutManager.threeDWidget(index).threeDView()
      modelDisplayableManager = threeDView.displayableManagerByClassName("vtkMRMLModelDisplayableManager")
      if modelDisplayableManager is None:
        continue
      renderer = threeDView.renderWindow().GetRenderers().GetFirstRenderer()
      observerTag = renderer.AddObserver(vtk.vtkCommand.StartEvent, self._onBoneTexturesRendererStart)
      self.boneTexturesViewsList.append({
        "renderer": renderer,
        "modelDisplayableManager": modelDisplayableManager,
        "observerTag": observerTag,
        "actorsList": [],
      })
      threeDView.scheduleRender()

  def _planeInModelCoordinates(self, planeNode, modelNode):
    """
    Return the plane as [normalX, normalY, normalZ, offset] in the coordinates of the model points.
    """
    origin = np.zeros(3)
    planeNode.GetOriginWorld(origin)
    normal = np.zeros(3)
    planeNode.GetNormalWorld(normal)
    worldToModelMatrix = vtk.vtkMatrix4x4()
    parentTransformNode = modelNode.GetParentTransformNode()
    if parentTransformNode is not None:
      parentTransformNode.GetMatrixTransformFromWorld(worldToModelMatrix)
    modelOrigin = self._transformPoint(worldToModelMatrix, origin)
    modelNormal = self._transformPoint(self._rotationOnlyMatrix(worldToModelMatrix), normal)
    modelNormal = modelNormal / np.linalg.norm(modelNormal)
    return [modelNormal[0], modelNormal[1], modelNormal[2], np.dot(modelNormal, modelOrigin)]

  def _transformPlane(self, matrix, plane):
    """
    Return the [normalX, normalY, normalZ, offset] plane moved by a rigid transform matrix.
    """
    normal = np.array(plane[:3])
    if np.linalg.norm(normal) == 0.0:
      return plane
    origin = normal * plane[3]
    transformedOrigin = self._transformPoint(matrix, origin)
    transformedNormal = self._transformPoint(self._rotationOnlyMatrix(matrix), normal)
    transformedNormal = transformedNormal / np.linalg.norm(transformedNormal)
    return [transformedNormal[0], transformedNormal[1], transformedNormal[2], np.dot(transformedNormal, transformedOrigin)]

  def _onBoneTexturesRendererStart(self, renderer, event):
    """
    Add the bone texture shader to the bone model actors of the view and update
    the transform from view to model coordinates for the current camera.
    """
    for boneTexturesView in self.boneTexturesViewsList:
      if boneTexturesView["renderer"] != renderer:
        continue
      modelToViewMatrix = vtk.vtkMatrix4x4()
      worldToViewMatrix = renderer.GetActiveCamera().GetModelViewTransformMatrix()
      for displayNodeID, cutPlanesList in self.boneTexturesDict.items():
        # A model may get its actor only after it is shown for the first time
        actor = boneTexturesView["modelDisplayableManager"].GetActorByID(displayNodeID)
        if actor is None or not actor.IsA("vtkActor"):
          continue
        fragmentUniforms = actor.GetShaderProperty().GetFragmentCustomUniforms()
        if actor not in boneTexturesView["actorsList"]:
          for originalValue, replacementValue in VSP_ANIMATION_BONE_FRAGMENT_SHADER_REPLACEMENTS.items():
            actor.GetShaderProperty().AddFragmentShaderReplacement(originalValue, True, replacementValue, False)
          fragmentUniforms.SetUniform4f("boneCutPlane0", cutPlanesList[0])
          fragmentUniforms.SetUniform4f("boneCutPlane1", cutPlanesList[1])
          boneTexturesView["actorsList"].append(actor)
        vtk.vtkMatrix4x4.Multiply4x4(worldToViewMatrix, actor.GetMatrix(), modelToViewMatrix)
        viewToModelMatrix = vtk.vtkMatrix4x4()
        vtk.vtkMatrix4x4.Invert(modelToViewMatrix, viewToModelMatrix)
        for row in range(3):
          viewToModelRow = [0.0, 0.0, 0.0, 0.0]
          for column in range(4):
            viewToModelRow[column] = viewToModelMatrix.GetElement(row, column)
          fragmentUniforms.SetUniform4f("boneViewToModelRow%d" % row, viewToModelRow)

  def _removeBoneTextures(self):
    """
    Remove the bone texture shader from all actors that received it.
    """
    for boneTexturesView in self.boneTexturesViewsList:
      boneTexturesView["renderer"].RemoveObserver(boneTexturesView["observerTag"])
      for actor in boneTexturesView["actorsList"]:
        shaderProperty = actor.GetShaderProperty()
        for originalValue in VSP_ANIMATION_BONE_FRAGMENT_SHADER_REPLACEMENTS:
          shaderProperty.ClearFragmentShaderReplacement(originalValue, True)
        for uniformName in VSP_ANIMATION_BONE_FRAGMENT_SHADER_UNIFORMS:
          shaderProperty.GetFragmentCustomUniforms().RemoveUniform(uniformName)
    self.boneTexturesViewsList = []
    self.boneTexturesDict = {}

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
      (animationDurationsDict["graftingZoomFibula"], self._zoomIntoFibula),
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
    ])
    if len(self.graftJointsList) > 0:
      animationStepsList.append(
        (animationDurationsDict["graftingRotateView"], self._rotateIntoFibulaAssemblyView)
      )
    animationStepsList.extend([
      (animationDurationsDict["graftingJoinPieces"], self._joinGraft),
      (animationDurationsDict["graftingHidePieces"], lambda progress: self._hideNodes(self.animationNodes["fibulaPieces"] + self.animationNodes["cutVessels"])),
      (animationDurationsDict["reconstructionSetView"], lambda progress: self._prepareReconstructionView()),
      (animationDurationsDict["reconstructionShowGraft"], lambda progress: self._fadeNodes(self.animationNodes["transformedFibulaPieces"] + self.animationNodes["transformedVessels"], progress, True)),
    ])
    if len(self.animationNodes["transformedVessels"]) > 0:
      animationStepsList.append(
        (animationDurationsDict["reconstructionRotateView"], self._rotateIntoAnteriorInferiorView)
      )
    animationStepsList.extend([
      (animationDurationsDict["reconstructionPause"], lambda progress: None),
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

    cameraNode = slicer.modules.cameras.logic().GetViewActiveCameraNode(viewNode)
    if viewName == "mandible":
      modelNode = self.animationNodes["mandible"]
      cameraDirection = np.array([0.0, -1.0, 0.0])
      viewUpDirection = np.array([0.0, 0.0, 1.0])
      centroid = getCentroid(modelNode)
      position = centroid - cameraDirection * 300.0
      self.mandibleViewCamera = {
        "position": position,
        "focalPoint": centroid,
        "cameraDirection": cameraDirection,
        "viewUpDirection": viewUpDirection,
      }
      cameraNode.SetPosition(position)
      cameraNode.SetFocalPoint(centroid)
      cameraNode.SetViewUp(viewUpDirection)
      cameraNode.ResetClippingRange()
      self._orientOperatingRoomBackground(viewNode, cameraDirection, viewUpDirection)
      return

    donorLeg = self.logic.getParameterNode().GetParameter("donorLeg")
    cameraDirection = np.array([-1.0, 0.0, 0.0]) if donorLeg == "Right" else np.array([1.0, 0.0, 0.0])
    viewUpDirection = np.array([0.0, 1.0, 0.0])
    fibulaBounds = [0.0] * 6
    self.animationNodes["fibula"].GetRASBounds(fibulaBounds)
    # Fit the whole fibula so both epiphyses are visible
    position, focalPoint, parallelScale = self._cameraPoseFittingBounds(
      cameraNode, fibulaBounds, cameraDirection, 1.05
    )
    self.fibulaFullViewCamera = {
      "position": position,
      "focalPoint": focalPoint,
      "parallelScale": parallelScale,
      "cameraDirection": cameraDirection,
    }
    self.fibulaZoomedViewCamera = None
    self.fibulaAssemblyViewCamera = None
    cameraNode.SetPosition(position)
    cameraNode.SetFocalPoint(focalPoint)
    cameraNode.SetViewUp(viewUpDirection)
    cameraNode.SetParallelScale(parallelScale)
    cameraNode.ResetClippingRange()
    self._orientOperatingRoomBackground(viewNode, cameraDirection, viewUpDirection)

  def _cameraPoseFittingBounds(self, cameraNode, bounds, cameraDirection, margin):
    """
    Return the camera position, focal point, and parallel scale that fit
    the bounding sphere of bounds when looking along cameraDirection.
    """
    center = np.array([
      (bounds[0] + bounds[1]) / 2.0,
      (bounds[2] + bounds[3]) / 2.0,
      (bounds[4] + bounds[5]) / 2.0,
    ])
    diagonal = np.array([
      bounds[1] - bounds[0],
      bounds[3] - bounds[2],
      bounds[5] - bounds[4],
    ])
    radius = 0.5 * np.linalg.norm(diagonal) * margin
    viewAngle = cameraNode.GetViewAngle()
    if viewAngle <= 0.0:
      viewAngle = 30.0
    distance = radius / np.sin(np.radians(viewAngle) / 2.0)
    position = center - cameraDirection * distance
    return position, center, radius

  def _unionBounds(self, nodesList):
    unionBounds = None
    for node in nodesList:
      if node is None:
        continue
      bounds = [0.0] * 6
      node.GetRASBounds(bounds)
      if bounds[0] > bounds[1]:
        continue
      if unionBounds is None:
        unionBounds = list(bounds)
        continue
      for index in range(3):
        unionBounds[2 * index] = min(unionBounds[2 * index], bounds[2 * index])
        unionBounds[2 * index + 1] = max(unionBounds[2 * index + 1], bounds[2 * index + 1])
    return unionBounds

  def _zoomIntoFibula(self, progress):
    """
    Zoom slightly from the whole fibula view into the region of the graft pieces.
    """
    if self.fibulaFullViewCamera is None:
      return
    cameraNode = slicer.modules.cameras.logic().GetViewActiveCameraNode(self._viewNode("fibula"))
    startPosition = self.fibulaFullViewCamera["position"]
    startFocalPoint = self.fibulaFullViewCamera["focalPoint"]
    startParallelScale = self.fibulaFullViewCamera["parallelScale"]
    cameraDirection = self.fibulaFullViewCamera["cameraDirection"]

    if self.fibulaZoomedViewCamera is None:
      maximumZoomFactor = 2
      startDistance = np.linalg.norm(startFocalPoint - startPosition)
      piecesBounds = self._unionBounds(self.animationNodes["fibulaPieces"])
      if piecesBounds is None:
        targetFocalPoint = startFocalPoint
        targetDistance = startDistance / maximumZoomFactor
        targetParallelScale = startParallelScale / maximumZoomFactor
      else:
        piecesPosition, targetFocalPoint, piecesParallelScale = self._cameraPoseFittingBounds(
          cameraNode, piecesBounds, cameraDirection, 1.15
        )
        piecesDistance = np.linalg.norm(targetFocalPoint - piecesPosition)
        targetDistance = min(startDistance, max(piecesDistance, startDistance / maximumZoomFactor))
        targetParallelScale = min(startParallelScale, max(piecesParallelScale, startParallelScale / maximumZoomFactor))
      self.fibulaZoomedViewCamera = {
        "position": targetFocalPoint - cameraDirection * targetDistance,
        "focalPoint": targetFocalPoint,
        "parallelScale": targetParallelScale,
      }

    easedProgress = progress * progress * (3.0 - 2.0 * progress)
    targetPosition = self.fibulaZoomedViewCamera["position"]
    targetFocalPoint = self.fibulaZoomedViewCamera["focalPoint"]
    targetParallelScale = self.fibulaZoomedViewCamera["parallelScale"]
    cameraNode.SetPosition(startPosition + (targetPosition - startPosition) * easedProgress)
    cameraNode.SetFocalPoint(startFocalPoint + (targetFocalPoint - startFocalPoint) * easedProgress)
    cameraNode.SetParallelScale(startParallelScale + (targetParallelScale - startParallelScale) * easedProgress)
    cameraNode.ResetClippingRange()

  def _rotateIntoAnteriorInferiorView(self, progress):
    """
    Rotate the camera around the reconstructed mandible from the anterior view
    into an anterior-inferior view so the transformed vessels pieces are visible.
    """
    if self.mandibleViewCamera is None:
      return
    cameraNode = slicer.modules.cameras.logic().GetViewActiveCameraNode(self._viewNode("mandible"))
    startPosition = self.mandibleViewCamera["position"]
    focalPoint = self.mandibleViewCamera["focalPoint"]
    cameraDirection = self.mandibleViewCamera["cameraDirection"]
    startViewUpDirection = self.mandibleViewCamera["viewUpDirection"]
    anteriorInferiorAngleDegrees = 45.0

    easedProgress = progress * progress * (3.0 - 2.0 * progress)
    # Rotating around the horizontal axis of the view moves the camera inferiorly
    rotationAxis = np.cross(cameraDirection, startViewUpDirection)
    rotationTransform = vtk.vtkTransform()
    rotationTransform.RotateWXYZ(anteriorInferiorAngleDegrees * easedProgress, rotationAxis)
    cameraOffset = np.array(rotationTransform.TransformVector(startPosition - focalPoint))
    cameraNode.SetPosition(focalPoint + cameraOffset)
    cameraNode.SetFocalPoint(focalPoint)
    cameraNode.SetViewUp(rotationTransform.TransformVector(startViewUpDirection))
    cameraNode.ResetClippingRange()

  def _graftMovementBounds(self, numberOfSamples):
    """
    Get the bounds that contain the fibula pieces during the whole joining movement.
    """
    fibulaPiecesList = self.animationNodes["fibulaPieces"]
    cutVesselsList = self.animationNodes["cutVessels"]
    pieceBoundsList = []
    for pieceIndex in range(len(fibulaPiecesList)):
      pieceNodesList = [fibulaPiecesList[pieceIndex]]
      if pieceIndex < len(cutVesselsList):
        pieceNodesList.append(cutVesselsList[pieceIndex])
      pieceBoundsList.append(self._unionBounds(pieceNodesList))

    movementBounds = None
    for sampleIndex in range(numberOfSamples + 1):
      pieceMatricesList = self._graftPieceMatricesList(sampleIndex / numberOfSamples)
      for pieceIndex in range(len(pieceMatricesList)):
        pieceBounds = pieceBoundsList[pieceIndex]
        if pieceBounds is None:
          continue
        for xIndex in range(2):
          for yIndex in range(2):
            for zIndex in range(2):
              corner = [pieceBounds[xIndex], pieceBounds[2 + yIndex], pieceBounds[4 + zIndex]]
              transformedCorner = self._transformPoint(pieceMatricesList[pieceIndex], corner)
              if movementBounds is None:
                movementBounds = [
                  transformedCorner[0], transformedCorner[0],
                  transformedCorner[1], transformedCorner[1],
                  transformedCorner[2], transformedCorner[2],
                ]
                continue
              for index in range(3):
                movementBounds[2 * index] = min(movementBounds[2 * index], transformedCorner[index])
                movementBounds[2 * index + 1] = max(movementBounds[2 * index + 1], transformedCorner[index])
    return movementBounds

  def _fibulaAssemblyViewCamera(self, cameraNode):
    """
    Compute a camera that looks perpendicular to the plane where the graft bends
    and fits the fibula pieces during the whole joining movement.
    """
    startPosition = np.array(cameraNode.GetPosition())
    startFocalPoint = np.array(cameraNode.GetFocalPoint())
    startViewUpDirection = np.array(cameraNode.GetViewUp())
    startParallelScale = cameraNode.GetParallelScale()
    startDistance = np.linalg.norm(startFocalPoint - startPosition)
    startCameraDirection = (startFocalPoint - startPosition) / startDistance

    # Cap centers of the assembled graft define the plane where it bends
    fibulaPlanesList = self.animationNodes["fibulaPlanes"]
    finalPieceMatricesList = self._graftPieceMatricesList(1.0)
    capCentersList = []
    for pieceIndex in range(len(finalPieceMatricesList)):
      for planeIndex in (2 * pieceIndex, 2 * pieceIndex + 1):
        capCenter = np.zeros(3)
        fibulaPlanesList[planeIndex].GetOrigin(capCenter)
        capCentersList.append(self._transformPoint(finalPieceMatricesList[pieceIndex], capCenter))
    capCentersArray = np.array(capCentersList)
    centeredCapCentersArray = capCentersArray - capCentersArray.mean(axis=0)
    _, singularValues, rightSingularVectors = np.linalg.svd(centeredCapCentersArray)
    targetCameraDirection = startCameraDirection
    if singularValues[1] > 1e-3 * singularValues[0]:
      targetCameraDirection = rightSingularVectors[2] / np.linalg.norm(rightSingularVectors[2])
      if np.dot(targetCameraDirection, startCameraDirection) < 0:
        targetCameraDirection = -targetCameraDirection

    rotationAxis = np.cross(startCameraDirection, targetCameraDirection)
    rotationAngleDegrees = np.degrees(np.arccos(np.clip(np.dot(startCameraDirection, targetCameraDirection), -1.0, 1.0)))
    if np.linalg.norm(rotationAxis) < 1e-6:
      rotationAxis = startViewUpDirection
      rotationAngleDegrees = 0.0

    targetFocalPoint = startFocalPoint
    targetDistance = startDistance
    targetParallelScale = startParallelScale
    movementBounds = self._graftMovementBounds(20)
    if movementBounds is not None:
      targetPosition, targetFocalPoint, targetParallelScale = self._cameraPoseFittingBounds(
        cameraNode, movementBounds, targetCameraDirection, 1.05
      )
      targetDistance = np.linalg.norm(targetFocalPoint - targetPosition)

    return {
      "startFocalPoint": startFocalPoint,
      "startDistance": startDistance,
      "startParallelScale": startParallelScale,
      "startCameraDirection": startCameraDirection,
      "startViewUpDirection": startViewUpDirection,
      "targetCameraDirection": targetCameraDirection,
      "targetFocalPoint": targetFocalPoint,
      "targetDistance": targetDistance,
      "targetParallelScale": targetParallelScale,
      "rotationAxis": rotationAxis,
      "rotationAngleDegrees": rotationAngleDegrees,
    }

  def _rotateIntoFibulaAssemblyView(self, progress):
    """
    Rotate the camera around the fibula pieces until it looks perpendicular to
    the plane where the graft bends so the assembling of the pieces is visible.
    """
    cameraNode = slicer.modules.cameras.logic().GetViewActiveCameraNode(self._viewNode("fibula"))
    if self.fibulaAssemblyViewCamera is None:
      self.fibulaAssemblyViewCamera = self._fibulaAssemblyViewCamera(cameraNode)
    startFocalPoint = self.fibulaAssemblyViewCamera["startFocalPoint"]
    startDistance = self.fibulaAssemblyViewCamera["startDistance"]
    startParallelScale = self.fibulaAssemblyViewCamera["startParallelScale"]
    targetFocalPoint = self.fibulaAssemblyViewCamera["targetFocalPoint"]
    targetDistance = self.fibulaAssemblyViewCamera["targetDistance"]
    targetParallelScale = self.fibulaAssemblyViewCamera["targetParallelScale"]

    easedProgress = progress * progress * (3.0 - 2.0 * progress)
    rotationTransform = vtk.vtkTransform()
    rotationTransform.RotateWXYZ(
      self.fibulaAssemblyViewCamera["rotationAngleDegrees"] * easedProgress,
      self.fibulaAssemblyViewCamera["rotationAxis"]
    )
    cameraDirection = np.array(rotationTransform.TransformVector(self.fibulaAssemblyViewCamera["startCameraDirection"]))
    focalPoint = startFocalPoint + (targetFocalPoint - startFocalPoint) * easedProgress
    distance = startDistance + (targetDistance - startDistance) * easedProgress
    cameraNode.SetFocalPoint(focalPoint)
    cameraNode.SetPosition(focalPoint - cameraDirection * distance)
    cameraNode.SetViewUp(rotationTransform.TransformVector(self.fibulaAssemblyViewCamera["startViewUpDirection"]))
    cameraNode.SetParallelScale(startParallelScale + (targetParallelScale - startParallelScale) * easedProgress)
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

  def _graftPieceMatricesList(self, progress):
    """
    Get the matrix of each fibula piece at the given progress of the graft joining.
    """
    numberOfJoints = len(self.graftJointsList)
    firstPieceMatrix = vtk.vtkMatrix4x4()
    firstPieceMatrix.Identity()
    pieceMatricesList = [firstPieceMatrix]
    for pieceIndex in range(1, len(self.graftPieceTransformNodeIDsList)):
      jointProgress = min(1.0, max(0.0, progress * numberOfJoints - (pieceIndex - 1)))
      jointMatrix = self._graftJointMatrix(
        self.graftJointsList[pieceIndex - 1],
        jointProgress
      )
      pieceMatrix = vtk.vtkMatrix4x4()
      vtk.vtkMatrix4x4.Multiply4x4(pieceMatricesList[pieceIndex - 1], jointMatrix, pieceMatrix)
      pieceMatricesList.append(pieceMatrix)
    return pieceMatricesList

  def _joinGraft(self, progress):
    if len(self.graftJointsList) == 0:
      return

    pieceMatricesList = self._graftPieceMatricesList(progress)
    for pieceIndex in range(1, len(self.graftPieceTransformNodeIDsList)):
      for transformNodeID in self.graftPieceTransformNodeIDsList[pieceIndex]:
        transformNode = slicer.mrmlScene.GetNodeByID(transformNodeID)
        if transformNode is not None:
          transformNode.SetMatrixTransformToParent(pieceMatricesList[pieceIndex])