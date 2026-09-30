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
  "resectionShowHead": 2.0,
  "resectionDissectHead": 6.0,
  "resectionHideHead": 2.0,
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
  "graftingShowLeg": 2.0,
  "graftingDissectLeg": 6.0,
  "graftingHideLeg": 2.0,
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

# Caption shown at the bottom of the view while the fibula planes are shown and the fibula guide is hidden
VSP_ANIMATION_OSTEOTOMIES_CAPTION = "Protect the vessels while doing the osteotomies"
VSP_ANIMATION_CAPTION_FONT_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Resources", "Fonts", "OpenSans-Bold.ttf")
VSP_ANIMATION_CAPTION_FADE_SECONDS = 0.5
# Fractions of the view size
VSP_ANIMATION_CAPTION_WIDTH_FRACTION = 0.9
VSP_ANIMATION_CAPTION_HEIGHT_FRACTION = 0.05
VSP_ANIMATION_CAPTION_BOTTOM_FRACTION = 0.05
VSP_ANIMATION_CAPTION_BACKGROUND_OPACITY = 0.6

# The schematic mode shows the plan models as they are, the realistic mode adds the operating room background,
# the bone and vessel textures, and the head and leg dissections
VSP_ANIMATION_SCHEMATIC_MODE = "Schematic"
VSP_ANIMATION_REALISTIC_MODE = "Realistic"

# The mandible view looks at the face from the front
VSP_ANIMATION_MANDIBLE_CAMERA_DIRECTION = [0.0, -1.0, 0.0]
VSP_ANIMATION_MANDIBLE_VIEW_UP_DIRECTION = [0.0, 0.0, 1.0]

# Each dissection carves a CT (head or leg), resampled into a grid aligned with its view,
# from the skin down to the target models (the mandible, or the fibula and the vessels)
VSP_ANIMATION_DISSECTION_SPACING_MM = 0.6
# Region of the CT kept around the target models
VSP_ANIMATION_DISSECTION_VIEW_MARGIN_MM = 80.0
# How far the dissection opening extends past the outline of the target models
VSP_ANIMATION_DISSECTION_OPENING_MARGIN_MM = 10.0
# The leg is only opened over the fibula pieces and this far past them, like the fibula harvest
# keeps the ends of the fibula covered
VSP_ANIMATION_DISSECTION_HARVEST_MARGIN_MM = 15.0
VSP_ANIMATION_DISSECTION_SKIN_THICKNESS_MM = 2.0
VSP_ANIMATION_DISSECTION_SKIN_HU = 80
VSP_ANIMATION_DISSECTION_AIR_HU = -1024
VSP_ANIMATION_DISSECTION_MAXIMUM_HU = 3071
VSP_ANIMATION_DISSECTION_BODY_THRESHOLD_HU = -400
# Only soft tissue is dissected, other bones stay
VSP_ANIMATION_DISSECTION_BONE_THRESHOLD_HU = 250
# Parts of the target models behind this thickness of other bones are not dissected
VSP_ANIMATION_DISSECTION_HIDING_BONE_MM = 2.0
# The skin voxels are mirrored below the air values (skin value = mirror - HU) so the skin gets its own
# color while the values stay continuous with the air in front of the skin
VSP_ANIMATION_DISSECTION_SKIN_MIRROR_VALUE = 2 * VSP_ANIMATION_DISSECTION_AIR_HU
# The skin opens along the middle of the target outline first and reaches the opening margin at this time
VSP_ANIMATION_DISSECTION_LATERAL_WEIGHT = 0.35
# The dissection reaches the target models inside this fraction of the opening and gets shallower up to its margin
VSP_ANIMATION_DISSECTION_FULL_DEPTH_LATERAL = 0.7
# Voxels fade into air while the carved surface is within this many voxels, so the carved surfaces are smooth.
# The fade lasts between the minimum and maximum fractions of the dissection
VSP_ANIMATION_DISSECTION_SOFTNESS_VOXELS = 2.0
VSP_ANIMATION_DISSECTION_MINIMUM_SOFTNESS = 0.02
VSP_ANIMATION_DISSECTION_MAXIMUM_SOFTNESS = 0.2
VSP_ANIMATION_DISSECTION_NOISE_WEIGHT = 0.08
VSP_ANIMATION_DISSECTION_NOISE_CELL_MM = 6.0
# Transfer functions of the dissected head or leg: mirrored skin, air, fat, muscle, bone and enamel
VSP_ANIMATION_DISSECTION_COLOR_POINTS = [
  [-2300.0, 0.86, 0.64, 0.53],
  [-1650.0, 0.86, 0.64, 0.53],
  [-1024.0, 0.0, 0.0, 0.0],
  [-300.0, 0.93, 0.80, 0.42],
  [-60.0, 0.93, 0.80, 0.42],
  [0.0, 0.62, 0.16, 0.14],
  [80.0, 0.55, 0.12, 0.11],
  [200.0, 0.93, 0.89, 0.80],
  [1500.0, 0.97, 0.96, 0.92],
  [3071.0, 0.97, 0.96, 0.92],
]
# Fat and muscle are translucent so the thin layers crossed at the carved surfaces do not tint them
VSP_ANIMATION_DISSECTION_OPACITY_POINTS = [
  [-2300.0, 1.0],
  [-1750.0, 1.0],
  [-1650.0, 0.0],
  [-300.0, 0.0],
  [-150.0, 0.35],
  [80.0, 0.4],
  [250.0, 1.0],
  [3071.0, 1.0],
]

# Wet bone sheen under the MultiLamp lighting
VSP_ANIMATION_BONE_MATERIAL = {
  "Specular": 0.25,
  "Power": 20.0,
}
# Glossier sheen of the wet vessel walls
VSP_ANIMATION_VESSEL_MATERIAL = {
  "Specular": 0.5,
  "Power": 40.0,
}
# A cut plane that never matches any position
VSP_ANIMATION_NO_CUT_PLANE = [0.0, 0.0, 0.0, 1.0]

# The tissue textures (bone and vessels) are computed per pixel from the model coordinates
# (a solid texture), so the models need no texture coordinates and the texture moves with each piece.
# The model coordinates are computed from the view coordinates because the vertex buffer
# coordinates (vertexMC) are shifted and scaled by VTK
VSP_ANIMATION_TISSUE_FRAGMENT_SHADER_DECLARATIONS = """//VTK::Normal::Dec
float tissueHash(vec3 cell)
{
  // Wrap the lattice so the hash stays precise at scene coordinates of hundreds of millimeters
  cell = mod(cell, 289.0);
  return fract(sin(dot(cell, vec3(12.9898, 78.233, 37.719))) * 43758.5453);
}

float tissueNoise(vec3 position)
{
  vec3 cell = floor(position);
  vec3 fraction = fract(position);
  fraction = fraction * fraction * (3.0 - 2.0 * fraction);
  float noise00 = mix(tissueHash(cell), tissueHash(cell + vec3(1.0, 0.0, 0.0)), fraction.x);
  float noise10 = mix(tissueHash(cell + vec3(0.0, 1.0, 0.0)), tissueHash(cell + vec3(1.0, 1.0, 0.0)), fraction.x);
  float noise01 = mix(tissueHash(cell + vec3(0.0, 0.0, 1.0)), tissueHash(cell + vec3(1.0, 0.0, 1.0)), fraction.x);
  float noise11 = mix(tissueHash(cell + vec3(0.0, 1.0, 1.0)), tissueHash(cell + vec3(1.0, 1.0, 1.0)), fraction.x);
  return mix(mix(noise00, noise10, fraction.y), mix(noise01, noise11, fraction.y), fraction.z);
}

float tissueFbm(vec3 position)
{
  float value = 0.0;
  float amplitude = 0.5;
  for (int octave = 0; octave < 4; octave++)
  {
    value += amplitude * tissueNoise(position);
    position = position * 2.03 + vec3(17.1, 31.7, 11.3);
    amplitude *= 0.5;
  }
  return value / 0.9375;
}

float tissueCutFactor(vec4 cutPlane, vec3 position)
{
  return 1.0 - smoothstep(0.05, 0.3, abs(dot(cutPlane.xyz, position) - cutPlane.w));
}
"""

# Screen space derivatives (dFdx) are only valid before any fragment is discarded (e.g. by depth peeling)
VSP_ANIMATION_BONE_FRAGMENT_SHADER_UNIFORM_FLOW = """//VTK::UniformFlow::Impl
  vec3 bonePosition = vec3(
    dot(tissueViewToModelRow0, vertexVC),
    dot(tissueViewToModelRow1, vertexVC),
    dot(tissueViewToModelRow2, vertexVC));
  float boneMottling = tissueFbm(bonePosition * 0.15);
  float bonePatches = tissueFbm(bonePosition * 0.06 + vec3(41.0, 7.0, 23.0));
  float bonePores = tissueFbm(bonePosition * 2.2);
  float boneMarrow = tissueFbm(bonePosition * 2.5 + vec3(5.0, 59.0, 13.0));
  float boneCut = max(tissueCutFactor(tissueCutPlane0, bonePosition), tissueCutFactor(tissueCutPlane1, bonePosition));
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
  "//VTK::Normal::Dec": VSP_ANIMATION_TISSUE_FRAGMENT_SHADER_DECLARATIONS,
  "//VTK::UniformFlow::Impl": VSP_ANIMATION_BONE_FRAGMENT_SHADER_UNIFORM_FLOW,
  "//VTK::Normal::Impl": VSP_ANIMATION_BONE_FRAGMENT_SHADER_IMPLEMENTATION,
}

VSP_ANIMATION_VESSEL_FRAGMENT_SHADER_UNIFORM_FLOW = """//VTK::UniformFlow::Impl
  vec3 vesselPosition = vec3(
    dot(tissueViewToModelRow0, vertexVC),
    dot(tissueViewToModelRow1, vertexVC),
    dot(tissueViewToModelRow2, vertexVC));
  float vesselBlood = tissueFbm(vesselPosition * 0.1);
  float vesselAdventitia = tissueFbm(vesselPosition * 0.15 + vec3(29.0, 3.0, 47.0));
  // Isolines of the noise (ridges) branch like small vessels, and a coarser noise keeps them sparse
  float vesselCapillaries = 1.0 - abs(2.0 * tissueFbm(vesselPosition * 0.9 + vec3(13.0, 71.0, 5.0)) - 1.0);
  float vesselCapillariesWidth = fwidth(vesselCapillaries);
  float vesselCapillariesMask = smoothstep(0.4, 0.6, tissueFbm(vesselPosition * 0.2 + vec3(61.0, 19.0, 37.0)));
  float vesselCapillariesLine = vesselCapillariesMask * smoothstep(0.9 - vesselCapillariesWidth, 0.95 + vesselCapillariesWidth, vesselCapillaries);
  float vesselWrinkles = tissueFbm(vesselPosition * 3.0);
  float vesselCut = max(tissueCutFactor(tissueCutPlane0, vesselPosition), tissueCutFactor(tissueCutPlane1, vesselPosition));
  float vesselHeight = (0.03 * vesselCapillariesLine + 0.015 * vesselWrinkles) * (1.0 - vesselCut);
  vec3 vesselPositionDx = dFdx(vertexVC.xyz);
  vec3 vesselPositionDy = dFdy(vertexVC.xyz);
  float vesselHeightDx = dFdx(vesselHeight);
  float vesselHeightDy = dFdy(vesselHeight);
"""

VSP_ANIMATION_VESSEL_FRAGMENT_SHADER_IMPLEMENTATION = """//VTK::Normal::Impl
  // Crimson arterial wall that turns purple where venous blood shows through
  vec3 vesselColor = mix(vec3(0.62, 0.11, 0.12), vec3(0.36, 0.08, 0.17), smoothstep(0.35, 0.65, vesselBlood));
  // Pale adventitia with the vasa vasorum running over it
  vesselColor = mix(vesselColor, vec3(0.85, 0.72, 0.68), 0.2 * smoothstep(0.45, 0.8, vesselAdventitia));
  vesselColor = mix(vesselColor, vec3(0.42, 0.03, 0.05), 0.7 * vesselCapillariesLine);
  // The thin wall lets light through near the silhouette
  float vesselRim = 1.0 - abs(normalVCVSOutput.z);
  vesselColor = mix(vesselColor, vec3(0.80, 0.25, 0.25), 0.3 * vesselRim * vesselRim);
  // Transected ends show dark clotted blood
  vec3 vesselCutColor = mix(vec3(0.14, 0.01, 0.02), vec3(0.24, 0.02, 0.04), smoothstep(0.3, 0.7, vesselWrinkles));
  vesselColor = mix(vesselColor, vesselCutColor, vesselCut);
  diffuseColor = diffuseIntensity * vesselColor;
  ambientColor = ambientIntensity * vesselColor;
  // Bump the normal along the vasa vasorum and wrinkles (surface gradient bump mapping)
  vec3 vesselR1 = cross(vesselPositionDy, normalVCVSOutput);
  vec3 vesselR2 = cross(normalVCVSOutput, vesselPositionDx);
  float vesselDeterminant = dot(vesselPositionDx, vesselR1);
  vec3 vesselSurfaceGradient = sign(vesselDeterminant) * (vesselHeightDx * vesselR1 + vesselHeightDy * vesselR2);
  normalVCVSOutput = normalize(max(abs(vesselDeterminant), 1e-10) * normalVCVSOutput - vesselSurfaceGradient);
"""

VSP_ANIMATION_VESSEL_FRAGMENT_SHADER_REPLACEMENTS = {
  "//VTK::Normal::Dec": VSP_ANIMATION_TISSUE_FRAGMENT_SHADER_DECLARATIONS,
  "//VTK::UniformFlow::Impl": VSP_ANIMATION_VESSEL_FRAGMENT_SHADER_UNIFORM_FLOW,
  "//VTK::Normal::Impl": VSP_ANIMATION_VESSEL_FRAGMENT_SHADER_IMPLEMENTATION,
}

# Both tissue shaders replace the same shader tags and use the same uniforms
VSP_ANIMATION_TISSUE_FRAGMENT_SHADER_TAGS = [
  "//VTK::Normal::Dec",
  "//VTK::UniformFlow::Impl",
  "//VTK::Normal::Impl",
]

VSP_ANIMATION_TISSUE_FRAGMENT_SHADER_UNIFORMS = [
  "tissueCutPlane0",
  "tissueCutPlane1",
  "tissueViewToModelRow0",
  "tissueViewToModelRow1",
  "tissueViewToModelRow2",
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
    self.realisticMode = False
    self.animationStepsList = []
    self.currentAnimationStep = None
    self.currentAnimationStepStartedAt = 0.0
    self.displayNodesState = {}
    self.camerasState = {}
    self.lightingState = {}
    self.viewNodesState = {}
    self.volumeRenderingDisplayNodesState = {}
    self.multiLampLightKit = vtk.vtkLightKit()
    self.multiLampLightKit.MaintainLuminanceOn()
    self.tissueTexturesDict = {}
    self.tissueTexturesViewsList = []
    self.captionViewsList = []
    self.initiallyMaximizedViewNodesList = []
    self.currentMaximizedViewNode = None
    self.temporaryTransformsList = []
    self.graftPieceTransformNodeIDsList = []
    self.graftJointsList = []
    self.dissectionsDict = {}
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

    self.realisticMode = self.logic.getParameterNode().GetParameter("vspAnimationMode") == VSP_ANIMATION_REALISTIC_MODE
    validationError = self._collectAnimationNodes()
    if validationError:
      slicer.util.errorDisplay(validationError)
      return False
    if self.animationWarningsList:
      slicer.util.warningDisplay("\n".join(self.animationWarningsList))

    try:
      self._setUpScene()
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
    self._removeCaptions()
    if restore and self.displayNodesState:
      self._restoreState()
    self._removeTemporaryTransforms()
    self._removeDissectionVolumes()
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

    self.realisticMode = self.logic.getParameterNode().GetParameter("vspAnimationMode") == VSP_ANIMATION_REALISTIC_MODE
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
      self._setUpScene()
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
    self.animationNodes["headCT"] = None
    self.animationNodes["legsCT"] = None
    missingOptionalNodesList = []
    # The dissections are only shown in the realistic mode
    if self.realisticMode:
      self.animationNodes["headCT"] = self._dissectionCTVolume("headCT", self.animationNodes["mandible"])
      self.animationNodes["legsCT"] = self._dissectionCTVolume("legsCT", self.animationNodes["fibula"])
      if self.animationNodes["headCT"] is None:
        missingOptionalNodesList.append("head CT volume")
      if self.animationNodes["legsCT"] is None:
        missingOptionalNodesList.append("leg CT volume")
    if self.animationNodes["mandibleGuide"] is None:
      missingOptionalNodesList.append("mandible surgical guide")
    if self.animationNodes["fibulaGuide"] is None:
      missingOptionalNodesList.append("fibula surgical guide")
    if missingOptionalNodesList:
      self.animationWarningsList.append(
        "The following nodes are missing and their animation scenes will be skipped: %s."
        % ", ".join(missingOptionalNodesList)
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

  def _dissectionCTVolume(self, ctReferenceRole, boneModel):
    """
    Get the CT (head or legs) used to segment the bone model, or None if it is not available.
    """
    parameterNode = self.logic.getParameterNode()
    ctVolume = parameterNode.GetNodeReference(ctReferenceRole)
    if ctVolume is not None and ctVolume.GetImageData() is not None:
      return ctVolume

    # The CT is only referenced when the automatic segmentation was used,
    # otherwise use the current volume if it contains the bone model
    currentScalarVolume = parameterNode.GetNodeReference("currentScalarVolume")
    if currentScalarVolume is None or currentScalarVolume.GetImageData() is None:
      return None
    rasToIJKMatrix = vtk.vtkMatrix4x4()
    currentScalarVolume.GetRASToIJKMatrix(rasToIJKMatrix)
    boneCentroidIJK = self._transformPoint(rasToIJKMatrix, getCentroid(boneModel))
    dimensions = currentScalarVolume.GetImageData().GetDimensions()
    for index in range(3):
      if boneCentroidIJK[index] < -0.5 or boneCentroidIJK[index] > dimensions[index] - 0.5:
        return None
    return currentScalarVolume

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

  def _setUpScene(self):
    """
    Save the scene state and set up the lighting, views, and models of the animation mode.
    """
    self._saveState()
    self._setMultiLampLighting()
    self._hideVolumeRenderings()
    self._hideMandiblePlanesNames()
    self._createCaptions()
    if self.realisticMode:
      self._hideBoxAndAxisLabels()
      self._setOperatingRoomBackground()
      self._setTissueTextures()
      self._createDissectionVolumes()
    self._createTemporaryGraftTransforms()

  def _saveState(self):
    """
    Save model, markup (including name label), camera, transform, lighting, background, 3D cube, 3D axis label, and maximized-view states.
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
      if hasattr(displayNode, "GetPropertiesLabelVisibility"):
        displayNodeState["propertiesLabelVisibility"] = displayNode.GetPropertiesLabelVisibility()
      self.displayNodesState[node.GetID()] = displayNodeState

    self.volumeRenderingDisplayNodesState = {}
    volumeRenderingDisplayNodesList = slicer.util.getNodesByClass("vtkMRMLVolumeRenderingDisplayNode")
    for volumeRenderingDisplayNode in volumeRenderingDisplayNodesList:
      self.volumeRenderingDisplayNodesState[volumeRenderingDisplayNode.GetID()] = volumeRenderingDisplayNode.GetVisibility()

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
    self.viewNodesState = {}
    layoutManager = slicer.app.layoutManager()
    for index in range(layoutManager.threeDViewCount):
      threeDView = layoutManager.threeDWidget(index).threeDView()
      viewNode = threeDView.mrmlViewNode()
      self.viewNodesState[viewNode.GetID()] = {
        "boxVisible": viewNode.GetBoxVisible(),
        "axisLabelsVisible": viewNode.GetAxisLabelsVisible(),
      }
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
      if "propertiesLabelVisibility" in displayNodeState:
        displayNode.SetPropertiesLabelVisibility(displayNodeState["propertiesLabelVisibility"])

    for volumeRenderingDisplayNodeID, visibility in self.volumeRenderingDisplayNodesState.items():
      volumeRenderingDisplayNode = slicer.mrmlScene.GetNodeByID(volumeRenderingDisplayNodeID)
      if volumeRenderingDisplayNode is not None:
        volumeRenderingDisplayNode.SetVisibility(visibility)

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
    self._removeTissueTextures()

    for viewNodeID, viewNodeState in self.viewNodesState.items():
      viewNode = slicer.mrmlScene.GetNodeByID(viewNodeID)
      if viewNode is None:
        continue
      viewNode.SetBoxVisible(viewNodeState["boxVisible"])
      viewNode.SetAxisLabelsVisible(viewNodeState["axisLabelsVisible"])

    self._restoreMaximizedViews()
    if self.displayNodesState:
      slicer.util.forceRenderAllViews()
    self.displayNodesState = {}
    self.volumeRenderingDisplayNodesState = {}
    self.camerasState = {}
    self.lightingState = {}
    self.viewNodesState = {}
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

  def _hideBoxAndAxisLabels(self):
    """
    Hide the 3D cube and the 3D axis labels of the 3D views during the animation.
    """
    for viewNodeID in self.viewNodesState:
      viewNode = slicer.mrmlScene.GetNodeByID(viewNodeID)
      if viewNode is None:
        continue
      viewNode.SetBoxVisible(False)
      viewNode.SetAxisLabelsVisible(False)

  def _hideVolumeRenderings(self):
    """
    Hide the volume renderings of the scene during the animation.
    """
    for volumeRenderingDisplayNodeID in self.volumeRenderingDisplayNodesState:
      volumeRenderingDisplayNode = slicer.mrmlScene.GetNodeByID(volumeRenderingDisplayNodeID)
      if volumeRenderingDisplayNode is not None:
        volumeRenderingDisplayNode.SetVisibility(False)

  def _hideMandiblePlanesNames(self):
    """
    Hide the name labels of the mandibular planes during the animation.
    """
    for planeNode in self.animationNodes["mandiblePlanes"]:
      displayNode = planeNode.GetDisplayNode()
      if displayNode is not None:
        displayNode.SetPropertiesLabelVisibility(False)

  def _createCaptions(self):
    """
    Add a hidden caption at the bottom of each 3D view.
    """
    self.captionViewsList = []
    layoutManager = slicer.app.layoutManager()
    for index in range(layoutManager.threeDViewCount):
      threeDView = layoutManager.threeDWidget(index).threeDView()
      viewNode = threeDView.mrmlViewNode()
      if viewNode.GetID() not in self.viewNodesState:
        continue
      textActor = vtk.vtkTextActor()
      textProperty = textActor.GetTextProperty()
      if os.path.isfile(VSP_ANIMATION_CAPTION_FONT_FILE_PATH):
        textProperty.SetFontFamily(vtk.VTK_FONT_FILE)
        textProperty.SetFontFile(VSP_ANIMATION_CAPTION_FONT_FILE_PATH)
      else:
        textProperty.SetFontFamilyToArial()
        textProperty.BoldOn()
      textProperty.SetColor(1.0, 1.0, 1.0)
      textProperty.SetBackgroundColor(0.0, 0.0, 0.0)
      textProperty.SetJustificationToCentered()
      textProperty.SetVerticalJustificationToBottom()
      textActor.SetTextScaleModeToNone()
      textActor.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
      textActor.SetPosition(0.5, VSP_ANIMATION_CAPTION_BOTTOM_FRACTION)
      textActor.VisibilityOff()
      renderer = threeDView.renderWindow().GetRenderers().GetFirstRenderer()
      renderer.AddActor2D(textActor)
      self.captionViewsList.append({
        "viewNodeID": viewNode.GetID(),
        "renderer": renderer,
        "textActor": textActor,
      })

  def _showCaption(self, text, opacity):
    """
    Show the caption on the maximized view with the given opacity, hiding it when the opacity is zero.
    """
    for captionView in self.captionViewsList:
      textActor = captionView["textActor"]
      visible = (
        opacity > 0.0 and
        self.currentMaximizedViewNode is not None and
        captionView["viewNodeID"] == self.currentMaximizedViewNode.GetID()
      )
      if visible:
        textActor.SetInput(text)
        # Fit the text to the current size of the view, which may change between play and export
        rendererSize = captionView["renderer"].GetSize()
        textActor.SetConstrainedFontSize(
          captionView["renderer"],
          int(rendererSize[0] * VSP_ANIMATION_CAPTION_WIDTH_FRACTION),
          int(rendererSize[1] * VSP_ANIMATION_CAPTION_HEIGHT_FRACTION)
        )
        textActor.GetTextProperty().SetOpacity(opacity)
        textActor.GetTextProperty().SetBackgroundOpacity(VSP_ANIMATION_CAPTION_BACKGROUND_OPACITY * opacity)
      textActor.SetVisibility(visible)

  def _captionOpacity(self, progress, duration, fadingIn, fadingOut):
    """
    Get the caption opacity fading in at the start and fading out at the end of the shot.
    """
    elapsedTime = progress * duration
    opacity = 1.0
    if fadingIn:
      opacity = min(opacity, elapsedTime / VSP_ANIMATION_CAPTION_FADE_SECONDS)
    if fadingOut:
      opacity = min(opacity, (duration - elapsedTime) / VSP_ANIMATION_CAPTION_FADE_SECONDS)
    return min(1.0, max(0.0, opacity))

  def _removeCaptions(self):
    for captionView in self.captionViewsList:
      captionView["renderer"].RemoveActor2D(captionView["textActor"])
    self.captionViewsList = []

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
      # Only views showing the operating room background (realistic mode) are oriented
      if "operatingRoomSkybox" not in self.lightingState.get(viewNode.GetID(), {}):
        continue
      renderer = threeDView.renderWindow().GetRenderers().GetFirstRenderer()
      renderer.SetEnvironmentUp(viewUpDirection[0], viewUpDirection[1], viewUpDirection[2])
      renderer.SetEnvironmentRight(environmentRight[0], environmentRight[1], environmentRight[2])

  def _setTissueTextures(self):
    """
    Make the bone and vessel models look like real tissue during the animation.
    """
    self.tissueTexturesDict = {}
    self._addBoneTextures()
    self._addVesselTextures()

    # The shader is added and updated right before each render of the 3D views
    self.tissueTexturesViewsList = []
    layoutManager = slicer.app.layoutManager()
    for index in range(layoutManager.threeDViewCount):
      threeDView = layoutManager.threeDWidget(index).threeDView()
      modelDisplayableManager = threeDView.displayableManagerByClassName("vtkMRMLModelDisplayableManager")
      if modelDisplayableManager is None:
        continue
      renderer = threeDView.renderWindow().GetRenderers().GetFirstRenderer()
      observerTag = renderer.AddObserver(vtk.vtkCommand.StartEvent, self._onTissueTexturesRendererStart)
      self.tissueTexturesViewsList.append({
        "renderer": renderer,
        "modelDisplayableManager": modelDisplayableManager,
        "observerTag": observerTag,
        "actorsList": [],
      })
      threeDView.scheduleRender()

  def _addBoneTextures(self):
    """
    Texture the bone models as real bone, with sawn bone on the osteotomy faces.
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

    for index in range(len(boneModelsList)):
      self._addTissueTexture(
        boneModelsList[index],
        cutPlanesListsList[index],
        VSP_ANIMATION_BONE_MATERIAL,
        VSP_ANIMATION_BONE_FRAGMENT_SHADER_REPLACEMENTS
      )

  def _addVesselTextures(self):
    """
    Texture the vessel models as a dissected vascular pedicle, with clotted blood on the transected ends.
    """
    vesselsModel = self.animationNodes["vessels"]
    if vesselsModel is None:
      return

    noCutPlanesList = [VSP_ANIMATION_NO_CUT_PLANE, VSP_ANIMATION_NO_CUT_PLANE]
    vesselModelsList = [vesselsModel]
    cutPlanesListsList = [noCutPlanesList]

    # Each vessels piece is cut with the same planes as its fibula piece
    fibulaPlanesList = self.animationNodes["fibulaPlanes"]
    cutVesselsList = self.animationNodes["cutVessels"]
    transformedVesselsList = self.animationNodes["transformedVessels"]
    fibulaToMandibleMatricesList = self.animationNodes["graftTransformMatrices"]
    for pieceIndex in range(len(cutVesselsList)):
      cutVessel = cutVesselsList[pieceIndex]
      pieceCutPlanesList = [
        self._planeInModelCoordinates(fibulaPlanesList[2 * pieceIndex], cutVessel),
        self._planeInModelCoordinates(fibulaPlanesList[2 * pieceIndex + 1], cutVessel),
      ]
      vesselModelsList.append(cutVessel)
      cutPlanesListsList.append(pieceCutPlanesList)
      # Transformed vessels pieces are copies of the cut vessels with the fibula to mandible transform hardened
      if pieceIndex < len(transformedVesselsList):
        vesselModelsList.append(transformedVesselsList[pieceIndex])
        cutPlanesListsList.append([
          self._transformPlane(fibulaToMandibleMatricesList[pieceIndex], pieceCutPlanesList[0]),
          self._transformPlane(fibulaToMandibleMatricesList[pieceIndex], pieceCutPlanesList[1]),
        ])

    for index in range(len(vesselModelsList)):
      self._addTissueTexture(
        vesselModelsList[index],
        cutPlanesListsList[index],
        VSP_ANIMATION_VESSEL_MATERIAL,
        VSP_ANIMATION_VESSEL_FRAGMENT_SHADER_REPLACEMENTS
      )

  def _addTissueTexture(self, modelNode, cutPlanesList, material, fragmentShaderReplacements):
    """
    Set the material of the model and register its tissue shader.
    """
    if modelNode is None:
      return
    displayNode = modelNode.GetDisplayNode()
    if displayNode is None:
      return
    # The shader modifies the Gouraud lighting inputs so PBR is not used during the animation
    displayNode.SetInterpolation(slicer.vtkMRMLDisplayNode.GouraudInterpolation)
    displayNode.SetSpecular(material["Specular"])
    displayNode.SetPower(material["Power"])
    self.tissueTexturesDict[displayNode.GetID()] = {
      "cutPlanesList": cutPlanesList,
      "fragmentShaderReplacements": fragmentShaderReplacements,
    }

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

  def _onTissueTexturesRendererStart(self, renderer, event):
    """
    Add the tissue texture shaders to the bone and vessel model actors of the view and update
    the transform from view to model coordinates for the current camera.
    """
    for tissueTexturesView in self.tissueTexturesViewsList:
      if tissueTexturesView["renderer"] != renderer:
        continue
      modelToViewMatrix = vtk.vtkMatrix4x4()
      worldToViewMatrix = renderer.GetActiveCamera().GetModelViewTransformMatrix()
      for displayNodeID, tissueTexture in self.tissueTexturesDict.items():
        # A model may get its actor only after it is shown for the first time
        actor = tissueTexturesView["modelDisplayableManager"].GetActorByID(displayNodeID)
        if actor is None or not actor.IsA("vtkActor"):
          continue
        fragmentUniforms = actor.GetShaderProperty().GetFragmentCustomUniforms()
        if actor not in tissueTexturesView["actorsList"]:
          for originalValue, replacementValue in tissueTexture["fragmentShaderReplacements"].items():
            actor.GetShaderProperty().AddFragmentShaderReplacement(originalValue, True, replacementValue, False)
          fragmentUniforms.SetUniform4f("tissueCutPlane0", tissueTexture["cutPlanesList"][0])
          fragmentUniforms.SetUniform4f("tissueCutPlane1", tissueTexture["cutPlanesList"][1])
          tissueTexturesView["actorsList"].append(actor)
        vtk.vtkMatrix4x4.Multiply4x4(worldToViewMatrix, actor.GetMatrix(), modelToViewMatrix)
        viewToModelMatrix = vtk.vtkMatrix4x4()
        vtk.vtkMatrix4x4.Invert(modelToViewMatrix, viewToModelMatrix)
        for row in range(3):
          viewToModelRow = [0.0, 0.0, 0.0, 0.0]
          for column in range(4):
            viewToModelRow[column] = viewToModelMatrix.GetElement(row, column)
          fragmentUniforms.SetUniform4f("tissueViewToModelRow%d" % row, viewToModelRow)

  def _removeTissueTextures(self):
    """
    Remove the tissue texture shaders from all actors that received them.
    """
    for tissueTexturesView in self.tissueTexturesViewsList:
      tissueTexturesView["renderer"].RemoveObserver(tissueTexturesView["observerTag"])
      for actor in tissueTexturesView["actorsList"]:
        shaderProperty = actor.GetShaderProperty()
        for originalValue in VSP_ANIMATION_TISSUE_FRAGMENT_SHADER_TAGS:
          shaderProperty.ClearFragmentShaderReplacement(originalValue, True)
        for uniformName in VSP_ANIMATION_TISSUE_FRAGMENT_SHADER_UNIFORMS:
          shaderProperty.GetFragmentCustomUniforms().RemoveUniform(uniformName)
    self.tissueTexturesViewsList = []
    self.tissueTexturesDict = {}

  def _createDissectionVolumes(self):
    """
    Create the volume renderings of the dissections: the head down to the mandible, and the leg
    down to the fibula and the vessels over the fibula pieces.
    """
    self.dissectionsDict = {}
    self._createDissectionVolume(
      "head",
      self.animationNodes["headCT"],
      [self.animationNodes["mandible"]],
      "mandible",
      None
    )
    self._createDissectionVolume(
      "leg",
      self.animationNodes["legsCT"],
      self._fibulaAndVesselsList(),
      "fibula",
      self.animationNodes["fibulaPieces"]
    )

  def _createDissectionVolume(self, dissectionName, ctVolume, targetModelsList, viewName, exposureNodesList):
    """
    Create the volume rendering of a dissection: a copy of the CT resampled into a grid aligned
    with the view, and the order in which its soft tissue is carved from the skin down to the target models.
    If exposureNodesList is given, the target models are only exposed across those nodes along the view.
    """
    if ctVolume is None:
      return

    import scipy.ndimage
    from vtk.util.numpy_support import vtk_to_numpy
    qt.QApplication.setOverrideCursor(qt.Qt.WaitCursor)
    try:
      spacing = VSP_ANIMATION_DISSECTION_SPACING_MM
      cameraDirection, viewUpDirection = self._viewDirections(viewName)
      # Grid axes: right and up of the view, and depth from the camera
      gridAxesList = [np.cross(cameraDirection, viewUpDirection), viewUpDirection, cameraDirection]

      # The target models were segmented from the CT, so the CT is placed with the parent transform
      # of the first target model (e.g. the fibula normalization transform)
      ctRASToWorldMatrix = vtk.vtkMatrix4x4()
      parentTransformNode = targetModelsList[0].GetParentTransformNode()
      if parentTransformNode is not None:
        parentTransformNode.GetMatrixTransformToWorld(ctRASToWorldMatrix)
      ctIJKToRASMatrix = vtk.vtkMatrix4x4()
      ctVolume.GetIJKToRASMatrix(ctIJKToRASMatrix)
      ctIJKToWorldMatrix = vtk.vtkMatrix4x4()
      vtk.vtkMatrix4x4.Multiply4x4(ctRASToWorldMatrix, ctIJKToRASMatrix, ctIJKToWorldMatrix)
      ctDimensions = ctVolume.GetImageData().GetDimensions()
      ctMinimumsList = [np.inf, np.inf, np.inf]
      ctMaximumsList = [-np.inf, -np.inf, -np.inf]
      for i in (0, ctDimensions[0] - 1):
        for j in (0, ctDimensions[1] - 1):
          for k in (0, ctDimensions[2] - 1):
            corner = self._transformPoint(ctIJKToWorldMatrix, [i, j, k])
            for axisIndex in range(3):
              coordinate = np.dot(corner, gridAxesList[axisIndex])
              ctMinimumsList[axisIndex] = min(ctMinimumsList[axisIndex], coordinate)
              ctMaximumsList[axisIndex] = max(ctMaximumsList[axisIndex], coordinate)

      targetPolyDatasList = []
      targetMinimumsList = [np.inf, np.inf, np.inf]
      targetMaximumsList = [-np.inf, -np.inf, -np.inf]
      for targetModel in targetModelsList:
        targetPolyData = self._polyDataInWorldCoordinates(targetModel)
        if targetPolyData is None or targetPolyData.GetNumberOfPoints() == 0:
          continue
        targetPolyDatasList.append(targetPolyData)
        targetPointsArray = vtk_to_numpy(targetPolyData.GetPoints().GetData())
        for axisIndex in range(3):
          targetCoordinatesArray = targetPointsArray.dot(gridAxesList[axisIndex])
          targetMinimumsList[axisIndex] = min(targetMinimumsList[axisIndex], targetCoordinatesArray.min())
          targetMaximumsList[axisIndex] = max(targetMaximumsList[axisIndex], targetCoordinatesArray.max())
      if len(targetPolyDatasList) == 0:
        return
      # Only the region of the CT around the target models is kept
      gridMinimumsList = []
      gridMaximumsList = []
      for axisIndex in range(3):
        gridMinimumsList.append(max(ctMinimumsList[axisIndex], targetMinimumsList[axisIndex] - VSP_ANIMATION_DISSECTION_VIEW_MARGIN_MM))
        gridMaximumsList.append(min(ctMaximumsList[axisIndex], targetMaximumsList[axisIndex] + VSP_ANIMATION_DISSECTION_VIEW_MARGIN_MM))
        if gridMaximumsList[axisIndex] <= gridMinimumsList[axisIndex]:
          logging.warning("The %s dissection target is outside the CT. The VSP animation will skip the %s dissection." % (dissectionName, dissectionName))
          return
      gridDimensionsList = []
      gridOrigin = np.zeros(3)
      for axisIndex in range(3):
        gridDimensionsList.append(int(np.floor((gridMaximumsList[axisIndex] - gridMinimumsList[axisIndex]) / spacing)) + 1)
        gridOrigin = gridOrigin + gridAxesList[axisIndex] * gridMinimumsList[axisIndex]
      gridIJKToRASMatrix = vtk.vtkMatrix4x4()
      for axisIndex in range(3):
        for row in range(3):
          gridIJKToRASMatrix.SetElement(row, axisIndex, gridAxesList[axisIndex][row] * spacing)
        gridIJKToRASMatrix.SetElement(axisIndex, 3, gridOrigin[axisIndex])

      # Resample the CT into the grid
      worldToCTIJKMatrix = vtk.vtkMatrix4x4()
      vtk.vtkMatrix4x4.Invert(ctIJKToWorldMatrix, worldToCTIJKMatrix)
      gridToCTIJKMatrix = vtk.vtkMatrix4x4()
      vtk.vtkMatrix4x4.Multiply4x4(worldToCTIJKMatrix, gridIJKToRASMatrix, gridToCTIJKMatrix)
      ctImageData = vtk.vtkImageData()
      ctImageData.ShallowCopy(ctVolume.GetImageData())
      ctImageData.SetOrigin(0.0, 0.0, 0.0)
      ctImageData.SetSpacing(1.0, 1.0, 1.0)
      reslice = vtk.vtkImageReslice()
      reslice.SetInputData(ctImageData)
      reslice.SetResliceAxes(gridToCTIJKMatrix)
      reslice.SetInterpolationModeToLinear()
      reslice.SetOutputSpacing(1.0, 1.0, 1.0)
      reslice.SetOutputOrigin(0.0, 0.0, 0.0)
      reslice.SetOutputExtent(0, gridDimensionsList[0] - 1, 0, gridDimensionsList[1] - 1, 0, gridDimensionsList[2] - 1)
      reslice.SetOutputScalarType(vtk.VTK_SHORT)
      reslice.SetBackgroundLevel(VSP_ANIMATION_DISSECTION_AIR_HU)
      reslice.Update()
      # Array indices are [depth, up, right] so each [:, up, right] column goes from the camera into the body
      arrayShape = (gridDimensionsList[2], gridDimensionsList[1], gridDimensionsList[0])
      ctArray = vtk_to_numpy(reslice.GetOutput().GetPointData().GetScalars()).reshape(arrayShape).copy()
      np.clip(ctArray, VSP_ANIMATION_DISSECTION_AIR_HU, VSP_ANIMATION_DISSECTION_MAXIMUM_HU, out = ctArray)

      # Voxelize the target models into the grid. Each model is voxelized on its own because
      # overlapping surfaces (the fibula and the vessels) would cancel each other in a single stencil
      gridToWorldTransform = vtk.vtkTransform()
      gridToWorldTransform.SetMatrix(gridIJKToRASMatrix)
      targetMask = np.zeros(arrayShape, dtype = bool)
      for targetPolyData in targetPolyDatasList:
        worldToGridTransformFilter = vtk.vtkTransformPolyDataFilter()
        worldToGridTransformFilter.SetInputData(targetPolyData)
        worldToGridTransformFilter.SetTransform(gridToWorldTransform.GetInverse())
        polyDataToImageStencil = vtk.vtkPolyDataToImageStencil()
        polyDataToImageStencil.SetInputConnection(worldToGridTransformFilter.GetOutputPort())
        polyDataToImageStencil.SetOutputOrigin(0.0, 0.0, 0.0)
        polyDataToImageStencil.SetOutputSpacing(1.0, 1.0, 1.0)
        polyDataToImageStencil.SetOutputWholeExtent(0, gridDimensionsList[0] - 1, 0, gridDimensionsList[1] - 1, 0, gridDimensionsList[2] - 1)
        stencilToImage = vtk.vtkImageStencilToImage()
        stencilToImage.SetInputConnection(polyDataToImageStencil.GetOutputPort())
        stencilToImage.SetInsideValue(1)
        stencilToImage.SetOutsideValue(0)
        stencilToImage.SetOutputScalarTypeToUnsignedChar()
        stencilToImage.Update()
        targetMask |= vtk_to_numpy(stencilToImage.GetOutput().GetPointData().GetScalars()).reshape(arrayShape) > 0
      if not targetMask.any():
        logging.warning("The %s dissection target is outside the CT. The VSP animation will skip the %s dissection." % (dissectionName, dissectionName))
        return

      # Only the columns across the exposure nodes along the view (the fibula pieces along the leg) are exposed
      exposureColumnsMask = np.ones(arrayShape[1:], dtype = bool)
      if exposureNodesList is not None:
        exposureBounds = self._unionBounds(exposureNodesList)
        if exposureBounds is not None:
          exposureMinimum = np.inf
          exposureMaximum = -np.inf
          for xIndex in range(2):
            for yIndex in range(2):
              for zIndex in range(2):
                corner = np.array([exposureBounds[xIndex], exposureBounds[2 + yIndex], exposureBounds[4 + zIndex]])
                coordinate = np.dot(corner, gridAxesList[0])
                exposureMinimum = min(exposureMinimum, coordinate)
                exposureMaximum = max(exposureMaximum, coordinate)
          rightCoordinatesArray = gridMinimumsList[0] + spacing * np.arange(arrayShape[2])
          exposureColumnsMask[:] = (
            (rightCoordinatesArray >= exposureMinimum - VSP_ANIMATION_DISSECTION_HARVEST_MARGIN_MM) &
            (rightCoordinatesArray <= exposureMaximum + VSP_ANIMATION_DISSECTION_HARVEST_MARGIN_MM)
          )[np.newaxis]

      bodyMask = ctArray > VSP_ANIMATION_DISSECTION_BODY_THRESHOLD_HU
      # Objects around the body (the scanner table, positioning pads, sheets) are turned into air. They are the parts
      # of the body mask that are not connected to the target models once their thin contacts are eroded,
      # which is done on a grid of half the resolution to be fast. The body cut by the grid border is not eroded,
      # and the connected parts grow back far enough to keep thin tissue like the eyelids
      coarseBodyMask = scipy.ndimage.binary_erosion(bodyMask[::2, ::2, ::2], border_value = 1)
      coarseLabelsArray, numberOfCoarseLabels = scipy.ndimage.label(coarseBodyMask)
      targetLabelsArray = np.unique(coarseLabelsArray[targetMask[::2, ::2, ::2] & coarseBodyMask])
      targetLabelsArray = targetLabelsArray[targetLabelsArray > 0]
      if len(targetLabelsArray) > 0:
        coarseConnectedMask = scipy.ndimage.binary_dilation(np.isin(coarseLabelsArray, targetLabelsArray), iterations = 3)
        connectedMask = coarseConnectedMask.repeat(2, axis = 0).repeat(2, axis = 1).repeat(2, axis = 2)
        connectedMask = connectedMask[:arrayShape[0], :arrayShape[1], :arrayShape[2]]
        ctArray[bodyMask & ~connectedMask] = VSP_ANIMATION_DISSECTION_AIR_HU
        bodyMask &= connectedMask
      # Thin bright objects lying on the skin (plastic sheets, electrodes) are made as dense as the skin, otherwise
      # they look like bone over the skin. Turning them into air would leave a stepped skin surface. They are found
      # next to the air in front of the body along the view, so thick bright structures (teeth) and the thin bones
      # around the airways and sinuses are kept
      depthIndicesArray = np.arange(arrayShape[0]).reshape(-1, 1, 1)
      outsideAirMask = (
        ~bodyMask.any(axis = 0)[np.newaxis] |
        (depthIndicesArray < np.argmax(bodyMask, axis = 0)[np.newaxis])
      )
      nearOutsideAirMask = scipy.ndimage.binary_dilation(outsideAirMask, iterations = 2)
      brightMask = ctArray >= VSP_ANIMATION_DISSECTION_BONE_THRESHOLD_HU
      surfaceObjectsMask = brightMask & ~scipy.ndimage.binary_opening(brightMask, iterations = 2) & nearOutsideAirMask
      # Their partially bright border voxels too
      surfaceObjectsMask = scipy.ndimage.binary_dilation(surfaceObjectsMask) & nearOutsideAirMask & bodyMask
      ctArray[surfaceObjectsMask] = np.minimum(ctArray[surfaceObjectsMask], VSP_ANIMATION_DISSECTION_SKIN_HU)

      # First voxel of the body in each column, ignoring isolated noise voxels in the air
      solidBodyMask = bodyMask.copy()
      solidBodyMask[:-2] = bodyMask[:-2] & bodyMask[1:-1] & bodyMask[2:]
      bodyColumnsMask = solidBodyMask.any(axis = 0)
      skinFrontArray = np.argmax(solidBodyMask, axis = 0)
      # Voxels around the target models, where their bone (or contrast filled vessels) in the CT is
      targetVoidMask = scipy.ndimage.binary_dilation(targetMask, iterations = 2)
      sortedCarveIndices, sortedCarveTimes, sortedCarveSoftness = self._dissectionCarveOrder(
        ctArray, targetMask, targetVoidMask, bodyColumnsMask, skinFrontArray, exposureColumnsMask
      )
      if len(sortedCarveIndices) == 0:
        logging.warning("No tissue to carve in front of the %s dissection target. The VSP animation will skip the %s dissection." % (dissectionName, dissectionName))
        return

      # The skin, and the air in front of it, are mirrored into their own band of values so the skin gets the skin color.
      # Columns beside deeper skin (the sides of the face or the leg) get deeper skin too
      skinThicknessVoxels = max(1, int(round(VSP_ANIMATION_DISSECTION_SKIN_THICKNESS_MM / spacing)))
      shellFrontArray = scipy.ndimage.maximum_filter(np.where(bodyColumnsMask, skinFrontArray, arrayShape[0]), size = 3)
      skinMask = (
        bodyColumnsMask[np.newaxis] &
        (ctArray < VSP_ANIMATION_DISSECTION_BONE_THRESHOLD_HU) &
        (depthIndicesArray < shellFrontArray[np.newaxis] + skinThicknessVoxels)
      )
      ctArray[skinMask] = VSP_ANIMATION_DISSECTION_SKIN_MIRROR_VALUE - ctArray[skinMask]

      # The bone (or contrast filled vessels) of the target models in the CT is always removed so it does not cover the models.
      # It fades into air along the blurred target models so the tissue around them has a smooth surface
      targetBoxSlicesList = []
      for axisIndex in range(3):
        otherAxesList = []
        for otherAxisIndex in range(3):
          if otherAxisIndex != axisIndex:
            otherAxesList.append(otherAxisIndex)
        axisIndicesArray = np.nonzero(targetVoidMask.any(axis = tuple(otherAxesList)))[0]
        targetBoxSlicesList.append(slice(
          max(0, axisIndicesArray.min() - 4),
          min(arrayShape[axisIndex], axisIndicesArray.max() + 5)
        ))
      targetBoxSlices = tuple(targetBoxSlicesList)
      blurredTargetArray = scipy.ndimage.gaussian_filter(targetMask[targetBoxSlices].astype(np.float32), 1.5)
      voidFractionArray = np.clip((blurredTargetArray - 0.03) / 0.13, 0.0, 1.0)
      ctBoxArray = ctArray[targetBoxSlices]
      ctBoxArray[:] = np.round(ctBoxArray + (VSP_ANIMATION_DISSECTION_AIR_HU - ctBoxArray) * voidFractionArray)

      dissectionVolume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode", "VSP animation %s dissection" % dissectionName)
      dissectionVolume.SetHideFromEditors(True)
      dissectionVolume.SetIJKToRASMatrix(gridIJKToRASMatrix)
      slicer.util.updateVolumeFromArray(dissectionVolume, ctArray)
      volumeRenderingDisplayNode = slicer.modules.volumerendering.logic().CreateDefaultVolumeRenderingNodes(dissectionVolume)
      volumeRenderingDisplayNode.SetVisibility(False)
      volumeRenderingDisplayNode.AddViewNodeID(self._viewNode(viewName).GetID())
      volumeRenderingDisplayNode.SetCroppingEnabled(False)
      volumeProperty = volumeRenderingDisplayNode.GetVolumePropertyNode().GetVolumeProperty()
      colorTransferFunction = volumeProperty.GetRGBTransferFunction()
      colorTransferFunction.RemoveAllPoints()
      for colorPoint in VSP_ANIMATION_DISSECTION_COLOR_POINTS:
        colorTransferFunction.AddRGBPoint(colorPoint[0], colorPoint[1], colorPoint[2], colorPoint[3])
      volumeProperty.SetInterpolationTypeToLinear()
      volumeProperty.ShadeOn()
      volumeProperty.SetAmbient(0.4)
      volumeProperty.SetDiffuse(0.8)
      volumeProperty.SetSpecular(0.15)
      volumeProperty.SetSpecularPower(20.0)
      volumeProperty.DisableGradientOpacityOn()
      volumeProperty.SetScalarOpacityUnitDistance(spacing)

      self.dissectionsDict[dissectionName] = {
        "volumeNodeID": dissectionVolume.GetID(),
        "volumeRenderingDisplayNodeID": volumeRenderingDisplayNode.GetID(),
        "viewName": viewName,
        # The volume array is carved in place
        "flatArray": slicer.util.arrayFromVolume(dissectionVolume).reshape(-1),
        "originalFlatArray": ctArray.reshape(-1),
        "sortedCarveIndices": sortedCarveIndices,
        "sortedCarveTimes": sortedCarveTimes,
        "sortedCarveSoftness": sortedCarveSoftness,
        "carvedCount": 0,
        "carvingCount": 0,
      }
      self._setDissectionOpacity(dissectionName, 1.0)
    finally:
      qt.QApplication.restoreOverrideCursor()

  def _polyDataInWorldCoordinates(self, modelNode):
    polyData = modelNode.GetPolyData()
    parentTransformNode = modelNode.GetParentTransformNode()
    if parentTransformNode is None:
      return polyData
    modelToWorldTransform = vtk.vtkGeneralTransform()
    parentTransformNode.GetTransformToWorld(modelToWorldTransform)
    transformFilter = vtk.vtkTransformPolyDataFilter()
    transformFilter.SetInputData(polyData)
    transformFilter.SetTransform(modelToWorldTransform)
    transformFilter.Update()
    return transformFilter.GetOutput()

  def _dissectionCarveOrder(self, ctArray, targetMask, targetVoidMask, bodyColumnsMask, skinFrontArray, exposureColumnsMask):
    """
    Get the soft tissue voxels in front of the target models sorted by the time they are carved.
    The skin opens along the middle of the target outline first, then the opening widens
    and deepens layer by layer until the target models are reached at time 1.
    """
    import scipy.ndimage
    spacing = VSP_ANIMATION_DISSECTION_SPACING_MM
    columnsShape = ctArray.shape[1:]
    depthIndicesArray = np.arange(ctArray.shape[0]).reshape(-1, 1, 1)
    targetFrontArray = np.argmax(targetMask, axis = 0)
    # Only the parts of the target models that are not hidden behind other bones (teeth, maxilla, zygoma)
    # and are inside the exposure columns are dissected
    otherBoneInFrontCountArray = np.count_nonzero(
      (ctArray >= VSP_ANIMATION_DISSECTION_BONE_THRESHOLD_HU) &
      ~targetVoidMask &
      (depthIndicesArray < targetFrontArray[np.newaxis]),
      axis = 0
    )
    hidingBoneVoxels = max(1, int(round(VSP_ANIMATION_DISSECTION_HIDING_BONE_MM / spacing)))
    silhouetteMask = targetMask.any(axis = 0) & (otherBoneInFrontCountArray < hidingBoneVoxels) & exposureColumnsMask

    # The same seed gives the same dissection in every play and video
    randomGenerator = np.random.default_rng(0)
    noiseArraysList = []
    for noiseIndex in range(2):
      coarseShape = (
        max(2, int(round(columnsShape[0] * spacing / VSP_ANIMATION_DISSECTION_NOISE_CELL_MM))),
        max(2, int(round(columnsShape[1] * spacing / VSP_ANIMATION_DISSECTION_NOISE_CELL_MM))),
      )
      noiseArray = scipy.ndimage.zoom(
        randomGenerator.random(coarseShape),
        (columnsShape[0] / coarseShape[0], columnsShape[1] / coarseShape[1]),
        order = 3
      )
      noiseArray = np.pad(
        noiseArray,
        ((0, max(0, columnsShape[0] - noiseArray.shape[0])), (0, max(0, columnsShape[1] - noiseArray.shape[1]))),
        mode = "edge"
      )
      noiseArraysList.append(noiseArray[:columnsShape[0], :columnsShape[1]])
    marginNoiseArray = noiseArraysList[0]
    timeNoiseArray = noiseArraysList[1]

    # Signed distance to the outline of the target models as seen from the camera, negative inside
    outsideDistanceArray = scipy.ndimage.distance_transform_edt(~silhouetteMask, sampling = spacing)
    insideDistanceArray = scipy.ndimage.distance_transform_edt(silhouetteMask, sampling = spacing)
    signedDistanceArray = outsideDistanceArray - insideDistanceArray
    # Smooth depth of the target models, filled around their outline, so the dissection does not step from column to column.
    # Columns next to the outline are dissected as deep as the target models beside them
    silhouetteWeightsArray = silhouetteMask.astype(float)
    fillSigma = VSP_ANIMATION_DISSECTION_OPENING_MARGIN_MM / spacing / 2.0
    smoothTargetFrontArray = (
      scipy.ndimage.gaussian_filter(targetFrontArray * silhouetteWeightsArray, fillSigma) /
      np.maximum(scipy.ndimage.gaussian_filter(silhouetteWeightsArray, fillSigma), 1e-6)
    )
    # Deepest voxel of each column that may be carved: the front of the target models, or a few voxels past the smooth
    # depth next to it so the carve times give the bottom of the wound a smooth surface
    softnessVoxels = int(np.ceil(2.0 * VSP_ANIMATION_DISSECTION_SOFTNESS_VOXELS))
    columnCarveBottomArray = np.where(
      silhouetteMask, targetFrontArray, np.ceil(smoothTargetFrontArray) + softnessVoxels
    ).astype(int)
    bodyWeightsArray = bodyColumnsMask.astype(float)
    smoothSkinFrontArray = (
      scipy.ndimage.gaussian_filter(skinFrontArray * bodyWeightsArray, 1.5) /
      np.maximum(scipy.ndimage.gaussian_filter(bodyWeightsArray, 1.5), 1e-6)
    )
    openingMarginArray = VSP_ANIMATION_DISSECTION_OPENING_MARGIN_MM * (0.6 + 0.8 * marginNoiseArray)
    # Lateral position in the opening: 0 in the middle of the target outline and 1 at the opening margin
    minimumSignedDistance = signedDistanceArray.min()
    lateralArray = (signedDistanceArray - minimumSignedDistance) / (openingMarginArray - minimumSignedDistance)
    # Time when the skin of each column opens
    columnOpeningTimeArray = VSP_ANIMATION_DISSECTION_LATERAL_WEIGHT * lateralArray
    # Fraction of the depth down to the target models that is dissected, so the wound walls slope near the margin.
    # It gets negative past the margin so the carve times keep growing there
    columnMaximumDepthArray = np.minimum(
      (1.0 - lateralArray) / (1.0 - VSP_ANIMATION_DISSECTION_FULL_DEPTH_LATERAL), 1.0
    )
    # The margin columns are included too so the rim of the opening fades smoothly
    candidateColumnsMask = (
      bodyColumnsMask &
      (lateralArray < 1.2) &
      (columnCarveBottomArray > skinFrontArray)
    )
    candidateUpIndicesArray, candidateRightIndicesArray = np.nonzero(candidateColumnsMask)
    if len(candidateUpIndicesArray) == 0:
      return np.zeros(0, dtype = np.int64), np.zeros(0, dtype = np.float32), np.zeros(0, dtype = np.float32)

    # Carve times are computed for every voxel of the box around the opening so their gradient is known
    upSlice = slice(candidateUpIndicesArray.min(), candidateUpIndicesArray.max() + 1)
    rightSlice = slice(candidateRightIndicesArray.min(), candidateRightIndicesArray.max() + 1)
    depthSlice = slice(
      int(skinFrontArray[candidateColumnsMask].min()),
      min(ctArray.shape[0], int(columnCarveBottomArray[candidateColumnsMask].max()) + 1)
    )
    boxDepthIndicesArray = np.arange(depthSlice.start, depthSlice.stop, dtype = np.float32).reshape(-1, 1, 1)
    boxSkinFrontArray = smoothSkinFrontArray[upSlice, rightSlice][np.newaxis]
    boxTargetFrontArray = smoothTargetFrontArray[upSlice, rightSlice][np.newaxis]
    # Depth fraction from the outer side of the skin voxel (0) to the target models (1)
    boxDepthFractionArray = (
      (boxDepthIndicesArray - boxSkinFrontArray + 1.0) /
      np.maximum(boxTargetFrontArray - boxSkinFrontArray + 1.0, 1.0)
    )
    # The target models themselves are exposed however deep their smooth depth says they are
    boxDepthFractionArray = np.where(
      silhouetteMask[upSlice, rightSlice][np.newaxis],
      np.minimum(boxDepthFractionArray, 1.0),
      boxDepthFractionArray
    )
    boxOpeningTimeArray = columnOpeningTimeArray[upSlice, rightSlice][np.newaxis]
    # Each column is dissected from the time its skin opens until time 1, and the sloped wound walls are reached last
    boxDissectionTimesArray = np.maximum(
      boxOpeningTimeArray + (1.0 - boxOpeningTimeArray) * np.clip(boxDepthFractionArray, 0.0, 1.0),
      1.0 + boxDepthFractionArray - columnMaximumDepthArray[upSlice, rightSlice][np.newaxis]
    )
    # The voxels inside the wound have faded into air by time 1, even with noise
    boxCarveTimesArray = (
      (1.0 - 0.5 * VSP_ANIMATION_DISSECTION_MAXIMUM_SOFTNESS - VSP_ANIMATION_DISSECTION_NOISE_WEIGHT) * boxDissectionTimesArray +
      VSP_ANIMATION_DISSECTION_NOISE_WEIGHT * np.clip(timeNoiseArray[upSlice, rightSlice], 0.0, 1.0)[np.newaxis]
    ).astype(np.float32)
    # Each voxel fades into air while the carved surface crosses it, which takes about the same number
    # of voxels everywhere, so the carved surfaces are smooth
    gradientArraysList = np.gradient(boxCarveTimesArray)
    boxSoftnessArray = VSP_ANIMATION_DISSECTION_SOFTNESS_VOXELS * np.sqrt(
      gradientArraysList[0] ** 2 + gradientArraysList[1] ** 2 + gradientArraysList[2] ** 2
    )
    boxSoftnessArray = np.clip(
      boxSoftnessArray, VSP_ANIMATION_DISSECTION_MINIMUM_SOFTNESS, VSP_ANIMATION_DISSECTION_MAXIMUM_SOFTNESS
    )

    carveMask = (
      candidateColumnsMask[upSlice, rightSlice][np.newaxis] &
      (ctArray[depthSlice, upSlice, rightSlice] < VSP_ANIMATION_DISSECTION_BONE_THRESHOLD_HU) &
      (boxDepthIndicesArray >= skinFrontArray[upSlice, rightSlice][np.newaxis]) &
      (boxDepthIndicesArray <= columnCarveBottomArray[upSlice, rightSlice][np.newaxis]) &
      (boxCarveTimesArray < 1.0 + 0.5 * boxSoftnessArray)
    )
    depthIndexArray, upIndexArray, rightIndexArray = np.nonzero(carveMask)
    carveTimesArray = boxCarveTimesArray[carveMask]
    carveSoftnessArray = boxSoftnessArray[carveMask]
    carveIndicesArray = np.ravel_multi_index(
      (depthIndexArray + depthSlice.start, upIndexArray + upSlice.start, rightIndexArray + rightSlice.start),
      ctArray.shape
    )
    carveOrderArray = np.argsort(carveTimesArray, kind = "stable")
    return carveIndicesArray[carveOrderArray], carveTimesArray[carveOrderArray], carveSoftnessArray[carveOrderArray]

  def _removeDissectionVolumes(self):
    for dissection in self.dissectionsDict.values():
      volumeRenderingDisplayNode = slicer.mrmlScene.GetNodeByID(dissection["volumeRenderingDisplayNodeID"])
      if volumeRenderingDisplayNode is not None:
        volumePropertyNode = volumeRenderingDisplayNode.GetVolumePropertyNode()
        roiNode = volumeRenderingDisplayNode.GetMarkupsROINode()
        slicer.mrmlScene.RemoveNode(volumeRenderingDisplayNode)
        if volumePropertyNode is not None:
          slicer.mrmlScene.RemoveNode(volumePropertyNode)
        if roiNode is not None:
          slicer.mrmlScene.RemoveNode(roiNode)
      volumeNode = slicer.mrmlScene.GetNodeByID(dissection["volumeNodeID"])
      if volumeNode is not None:
        slicer.mrmlScene.RemoveNode(volumeNode)
    self.dissectionsDict = {}

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
    ]
    if "head" in self.dissectionsDict:
      animationStepsList.extend([
        (animationDurationsDict["resectionShowHead"], lambda progress: self._showDissection("head", [self.animationNodes["mandible"]])),
        (animationDurationsDict["resectionDissectHead"], lambda progress: self._dissect("head", progress)),
        (animationDurationsDict["resectionHideHead"], lambda progress: self._hideDissection("head", progress)),
      ])
    animationStepsList.append(
      (animationDurationsDict["resectionMandibleOnly"], lambda progress: self._showOnly([self.animationNodes["mandible"]]))
    )
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
    ])
    if "leg" in self.dissectionsDict:
      animationStepsList.extend([
        (animationDurationsDict["graftingShowLeg"], lambda progress: self._showDissection("leg", self._fibulaAndVesselsList())),
        (animationDurationsDict["graftingDissectLeg"], lambda progress: self._dissect("leg", progress)),
        (animationDurationsDict["graftingHideLeg"], lambda progress: self._hideDissection("leg", progress)),
      ])
    # In the realistic mode the dissected vessels stay visible until the fibula is exchanged for the pieces
    if self.realisticMode:
      fibulaOnlyNodesList = self._fibulaAndVesselsList()
    else:
      fibulaOnlyNodesList = [self.animationNodes["fibula"]]
    animationStepsList.extend([
      (animationDurationsDict["graftingFibulaOnly"], lambda progress: self._showOnly(fibulaOnlyNodesList)),
      (animationDurationsDict["graftingZoomFibula"], self._zoomIntoFibula),
    ])
    if self.animationNodes["fibulaGuide"] is not None:
      animationStepsList.append(
        (animationDurationsDict["graftingShowGuide"], lambda progress: self._fadeNodes([self.animationNodes["fibulaGuide"]], progress, True))
      )
    # The osteotomies caption stays on from the first fibula plane until the fibula guide is hidden
    animationStepsList.append(
      (fibulaPlaneDuration, lambda progress: self._showFibulaPlanesWithCaption(progress, fibulaPlaneDuration, self.animationNodes["fibulaGuide"] is None))
    )
    if self.animationNodes["fibulaGuide"] is not None:
      animationStepsList.append(
        (animationDurationsDict["graftingHideGuide"], lambda progress: self._hideFibulaGuideWithCaption(progress, animationDurationsDict["graftingHideGuide"]))
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
    cameraDirection, viewUpDirection = self._viewDirections(viewName)
    if viewName == "mandible":
      modelNode = self.animationNodes["mandible"]
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

  def _viewDirections(self, viewName):
    """
    Return the camera and view up directions of the mandible view (front of the face)
    or of the fibula view (lateral side of the donor leg).
    """
    if viewName == "mandible":
      return np.array(VSP_ANIMATION_MANDIBLE_CAMERA_DIRECTION), np.array(VSP_ANIMATION_MANDIBLE_VIEW_UP_DIRECTION)
    donorLeg = self.logic.getParameterNode().GetParameter("donorLeg")
    cameraDirection = np.array([-1.0, 0.0, 0.0]) if donorLeg == "Right" else np.array([1.0, 0.0, 0.0])
    return cameraDirection, np.array([0.0, 1.0, 0.0])

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

  def _fibulaAndVesselsList(self):
    fibulaAndVesselsList = [self.animationNodes["fibula"]]
    if self.animationNodes["vessels"] is not None:
      fibulaAndVesselsList.append(self.animationNodes["vessels"])
    return fibulaAndVesselsList

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

  def _showDissection(self, dissectionName, visibleNodesList):
    """
    Show the intact head or leg in front of the target models before the dissection.
    """
    self._showOnly(visibleNodesList)
    self._carveDissection(dissectionName, 0.0)
    self._setDissectionOpacity(dissectionName, 1.0)
    self._setDissectionVisible(dissectionName, True)
    if dissectionName in self.dissectionsDict:
      # The clipping range was reset by the view setup while nothing was shown yet
      viewNode = self._viewNode(self.dissectionsDict[dissectionName]["viewName"])
      slicer.modules.cameras.logic().GetViewActiveCameraNode(viewNode).ResetClippingRange()

  def _dissect(self, dissectionName, progress):
    """
    Carve the head or leg from the skin down to the target models.
    """
    easedProgress = progress * progress * (3.0 - 2.0 * progress)
    self._carveDissection(dissectionName, easedProgress)

  def _hideDissection(self, dissectionName, progress):
    """
    Fade out the dissected head or leg so only the target models remain.
    """
    # The opacity of the volume adds up along the tissue depth so it has to drop faster than linearly
    self._setDissectionOpacity(dissectionName, (1.0 - progress) ** 3)
    self._setDissectionVisible(dissectionName, progress < 1.0)

  def _carveDissection(self, dissectionName, carveProgress):
    """
    Turn into air the voxels whose carve time has passed, fading the ones the carved surface is crossing.
    """
    if dissectionName not in self.dissectionsDict:
      return
    dissection = self.dissectionsDict[dissectionName]
    sortedCarveIndices = dissection["sortedCarveIndices"]
    sortedCarveTimes = dissection["sortedCarveTimes"]
    originalFlatArray = dissection["originalFlatArray"]
    flatArray = dissection["flatArray"]
    # Voxels before carvedCount are air, voxels up to carvingCount may be fading
    if carveProgress <= 0.0:
      carvedCount = 0
      carvingCount = 0
    else:
      halfMaximumSoftness = 0.5 * VSP_ANIMATION_DISSECTION_MAXIMUM_SOFTNESS
      carvedCount = int(np.searchsorted(sortedCarveTimes, carveProgress - halfMaximumSoftness, side = "right"))
      carvingCount = int(np.searchsorted(sortedCarveTimes, carveProgress + halfMaximumSoftness, side = "right"))
    previousCarvedCount = dissection["carvedCount"]
    previousCarvingCount = dissection["carvingCount"]
    if carvedCount == previousCarvedCount and carvingCount == previousCarvingCount and carvedCount == carvingCount:
      return

    if carvedCount > previousCarvedCount:
      flatArray[sortedCarveIndices[previousCarvedCount:carvedCount]] = VSP_ANIMATION_DISSECTION_AIR_HU
    carvingIndices = sortedCarveIndices[carvedCount:carvingCount]
    # Half faded when the carved surface is on the voxel
    carvingFractions = np.clip(
      0.5 + (carveProgress - sortedCarveTimes[carvedCount:carvingCount]) /
      dissection["sortedCarveSoftness"][carvedCount:carvingCount],
      0.0, 1.0
    )
    originalValues = originalFlatArray[carvingIndices]
    flatArray[carvingIndices] = np.round(
      originalValues + (VSP_ANIMATION_DISSECTION_AIR_HU - originalValues) * carvingFractions
    )
    # Going back in time restores the voxels that are not carved anymore
    if previousCarvingCount > carvingCount:
      restoredIndices = sortedCarveIndices[carvingCount:previousCarvingCount]
      flatArray[restoredIndices] = originalFlatArray[restoredIndices]
    dissection["carvedCount"] = carvedCount
    dissection["carvingCount"] = carvingCount
    slicer.util.arrayFromVolumeModified(slicer.mrmlScene.GetNodeByID(dissection["volumeNodeID"]))

  def _setDissectionOpacity(self, dissectionName, opacityFactor):
    if dissectionName not in self.dissectionsDict:
      return
    volumeRenderingDisplayNode = slicer.mrmlScene.GetNodeByID(self.dissectionsDict[dissectionName]["volumeRenderingDisplayNodeID"])
    scalarOpacity = volumeRenderingDisplayNode.GetVolumePropertyNode().GetVolumeProperty().GetScalarOpacity()
    scalarOpacity.RemoveAllPoints()
    for opacityPoint in VSP_ANIMATION_DISSECTION_OPACITY_POINTS:
      scalarOpacity.AddPoint(opacityPoint[0], opacityPoint[1] * opacityFactor)

  def _setDissectionVisible(self, dissectionName, visible):
    if dissectionName not in self.dissectionsDict:
      return
    volumeRenderingDisplayNode = slicer.mrmlScene.GetNodeByID(self.dissectionsDict[dissectionName]["volumeRenderingDisplayNodeID"])
    volumeRenderingDisplayNode.SetVisibility(visible)

  def _showFibulaPlanesWithCaption(self, progress, duration, captionFadingOut):
    self._showSequentially(self.animationNodes["fibulaPlanes"], progress)
    self._showCaption(VSP_ANIMATION_OSTEOTOMIES_CAPTION, self._captionOpacity(progress, duration, True, captionFadingOut))

  def _hideFibulaGuideWithCaption(self, progress, duration):
    self._fadeNodes([self.animationNodes["fibulaGuide"]], progress, False)
    self._showCaption(VSP_ANIMATION_OSTEOTOMIES_CAPTION, self._captionOpacity(progress, duration, False, True))

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