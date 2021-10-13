import os
import unittest
import logging
import vtk, qt, ctk, slicer, math
import numpy as np
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from BRPLib.helperFunctions import *

#
# BoneReconstructionPlanner
#

SLICER_CHANGE_OF_API_REVISION = '29927'

class BoneReconstructionPlanner(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "BoneReconstructionPlanner"  # TODO: make this more human readable by adding spaces
    self.parent.categories = ["Planning"]  # TODO: set categories (folders where the module shows up in the module selector)
    self.parent.dependencies = []  # TODO: add here list of module names that this module requires
    self.parent.contributors = ["Mauro I. Dominguez, Andras Lasso, Manjula Herath"]  # TODO: replace with "Firstname Lastname (Organization)"
    # TODO: update with short description of the module and a link to online module documentation
    self.parent.helpText = """
A 3D Slicer module for virtual surgical planning of mandibular reconstruction with vascularized fibula free flap and generation of patient-specific surgical guides.
See the whole project in <a href="https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner">this link</a>.
"""
    # TODO: replace with organization, grant and thanks
    self.parent.acknowledgementText = """
Mauro I. Dominguez developed this module for his final project of engineering studies ​at FCEIA-UNR under the supervision and advice of PhD. Andras Lasso at PerkLab, and the clinical inputs of Dr. Manjula Herath.
"""

    # Additional initialization step after application startup is complete
    slicer.app.connect("startupCompleted()", registerSampleData)

#
# Register sample data sets in Sample Data module
#

def registerSampleData():
  """
  Add data sets to Sample Data module.
  """
  # It is always recommended to provide sample data for users to make it easy to try the module,
  # but if no sample data is available then this method (and associated startupCompeted signal connection) can be removed.

  import SampleData
  iconsPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons')

  # To ensure that the source code repository remains small (can be downloaded and installed quickly)
  # it is recommended to store data sets that are larger than a few MB in a Github release.

  # BoneReconstructionPlanner1
  SampleData.SampleDataLogic.registerCustomSampleDataSource(
    # Category and sample name displayed in Sample Data module
    category='BoneReconstructionPlanner',
    sampleName='FibulaCropped',
    # Thumbnail should have size of approximately 260x280 pixels and stored in Resources/Icons folder.
    # It can be created by Screen Capture module, "Capture all views" option enabled, "Number of images" set to "Single".
    thumbnailFileName=os.path.join(iconsPath, 'iconFibulaCropped.png'),
    # Download URL and target file name
    uris="https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/releases/download/TestingData/FibulaCropped.nrrd",
    fileNames='FibulaCropped.nrrd',
    # Checksum to ensure file integrity. Can be computed by this command:
    #  import hashlib; print(hashlib.sha256(open(filename, "rb").read()).hexdigest())
    checksums = 'SHA256:5febc47a8fba6b43440be2b475f9defadffe9b47b1316d04217208b4497a4f72',
    # This node name will be used when the data set is loaded
    nodeNames='FibulaCropped'
  )

  # BoneReconstructionPlanner2
  SampleData.SampleDataLogic.registerCustomSampleDataSource(
    # Category and sample name displayed in Sample Data module
    category='BoneReconstructionPlanner',
    sampleName='ResectedMandible',
    thumbnailFileName=os.path.join(iconsPath, 'iconResectedMandible.png'),
    # Download URL and target file name
    uris="https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/releases/download/TestingData/ResectedMandible.nrrd",
    fileNames='ResectedMandible.nrrd',
    checksums = 'SHA256:352aefed1905bd2ad7373972a6bb115bd494e26e4fc438d2c8679384dcfd2654',
    # This node name will be used when the data set is loaded
    nodeNames='ResectedMandible'
  )

#
# BoneReconstructionPlannerWidget
#

class BoneReconstructionPlannerWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent=None):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.__init__(self, parent)
    VTKObservationMixin.__init__(self)  # needed for parameter node observation
    self.logic = None
    self._parameterNode = None
    self._updatingGUIFromParameterNode = False

  def setup(self):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.setup(self)

    # Load widget from .ui file (created by Qt Designer).
    # Additional widgets can be instantiated manually and added to self.layout.
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/BoneReconstructionPlanner.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
    # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
    # "setMRMLScene(vtkMRMLScene*)" slot.
    uiWidget.setMRMLScene(slicer.mrmlScene)

    # Create logic class. Logic implements all computations that should be possible to run
    # in batch mode, without a graphical user interface.
    self.logic = BoneReconstructionPlannerLogic()

    # Connections

    # These connections ensure that we update parameter node when scene is closed
    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

    slicer.mrmlScene.AddObserver(slicer.mrmlScene.NodeAboutToBeRemovedEvent, self.onNodeAboutToBeRemovedEvent) 

    # These connections ensure that whenever user changes some settings on the GUI, that is saved in the MRML scene
    # (in the selected parameter node).
    self.ui.fibulaLineSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onFibulaPlanesCreationParametersChanged)
    self.ui.mandibleCurveSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.mandibularSegmentationSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.fibulaSegmentationSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.fibulaFiducialListSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.fibulaSurgicalGuideBaseSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.miterBoxDirectionLineSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.scalarVolumeSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onScalarVolumeChanged)
    self.ui.mandibleBridgeModelSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.mandibleSurgicalGuideBaseSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.mandibleFiducialListSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
   
    self.ui.initialSpinBox.valueChanged.connect(self.onFibulaPlanesCreationParametersChanged)
    self.ui.intersectionSpinBox.valueChanged.connect(self.onFibulaPlanesCreationParametersChanged)
    self.ui.betweenSpinBox.valueChanged.connect(self.onFibulaPlanesCreationParametersChanged)
    self.ui.securityMarginOfFibulaPiecesSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.miterBoxSlotWidthSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.miterBoxSlotLengthSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.miterBoxSlotHeightSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.miterBoxSlotWallSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.fibulaScrewHoleCylinderRadiusSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.clearanceFitPrintingToleranceSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.biggerMiterBoxDistanceToFibulaSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.intersectionDistanceMultiplierSpinBox.valueChanged.connect(self.onFibulaPlanesCreationParametersChanged)
    self.ui.sawBoxSlotWidthSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.sawBoxSlotLengthSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.sawBoxSlotHeightSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.sawBoxSlotWallSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.biggerSawBoxDistanceToMandibleSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.mandibleScrewHoleCylinderRadiusSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandibleButton.checkBoxToggled.connect(self.updateParameterNodeFromGUI)

    # Buttons
    self.ui.notLeftFibulaCheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)
    self.ui.addCutPlaneButton.connect('clicked(bool)',self.onAddCutPlaneButton)
    self.ui.addMandibularCurveButton.connect('clicked(bool)',self.onAddMandibularCurveButton)
    self.ui.addFibulaLineButton.connect('clicked(bool)',self.onAddFibulaLineButton)
    self.ui.makeModelsButton.connect('clicked(bool)',self.onMakeModelsButton)
    self.ui.createMiterBoxesFromFibulaPlanesButton.connect('clicked(bool)',self.onCreateMiterBoxesFromFibulaPlanesButton)
    self.ui.createFibulaCylindersFiducialListButton.connect('clicked(bool)',self.onCreateFibulaCylindersFiducialListButton)
    self.ui.createCylindersFromFiducialListAndFibulaSurgicalGuideBaseButton.connect('clicked(bool)',self.onCreateCylindersFromFiducialListAndSurgicalGuideBaseButton)
    self.ui.makeBooleanOperationsToFibulaSurgicalGuideBaseButton.connect('clicked(bool)', self.onMakeBooleanOperationsToFibulaSurgicalGuideBaseButton)
    self.ui.createMandibleCylindersFiducialListButton.connect('clicked(bool)', self.onCreateMandibleCylindersFiducialListButton)
    self.ui.createSawBoxesFromFirstAndLastMandiblePlanesButton.connect('clicked(bool)', self.onCreateSawBoxesFromFirstAndLastMandiblePlanesButton)
    self.ui.makeBooleanOperationsToMandibleSurgicalGuideBaseButton.connect('clicked(bool)', self.onMakeBooleanOperationsToMandibleSurgicalGuideBaseButton)
    self.ui.createCylindersFromFiducialListAndMandibleSurgicalGuideBaseButton.connect('clicked(bool)', self.onCreateCylindersFromFiducialListAndMandibleSurgicalGuideBaseButton)
    self.ui.generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandibleButton.connect('clicked(bool)', self.onGenerateFibulaPlanesFibulaBonePiecesAndTransformThemToMandibleButton)
    self.ui.centerFibulaLineButton.connect('clicked(bool)', self.onCenterFibulaLineButton)
    self.ui.showHideBiggerSawBoxesInteractionHandlesButton.connect('clicked(bool)', self.onShowHideBiggerSawBoxesInteractionHandlesButton)
    self.ui.showHideMandiblePlanesInteractionHandlesButton.connect('clicked(bool)', self.onShowHideMandiblePlanesInteractionHandlesButton)
    self.ui.create3DModelOfTheReconstructionButton.connect('clicked(bool)', self.onCreate3DModelOfTheReconstructionButton)
    self.ui.showHideFibulaSegmentsLengthsButton.connect('clicked(bool)', self.onShowHideFibulaSegmentsLengthsButton)
    self.ui.showHideOriginalMandibleButton.connect('clicked(bool)', self.onShowHideOriginalMandibleButton)
    self.ui.makeAllMandiblePlanesRotateTogetherCheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)
    self.ui.useMoreExactVersionOfPositioningAlgorithmCheckBox.connect('stateChanged(int)', self.onUseMoreExactVersionOfPositioningAlgorithmCheckBox)
    self.ui.useNonDecimatedBoneModelsForPreviewCheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)
    self.ui.mandiblePlanesPositioningForMaximumBoneContactCheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)
    self.ui.fixCutGoesThroughTheMandibleTwiceCheckBox.connect('stateChanged(int)', self.onFixCutGoesThroughTheMandibleTwiceCheckBox)
    self.ui.checkSecurityMarginOnMiterBoxCreationCheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)
    
    # Make sure parameter node is initialized (needed for module reload)
    self.initializeParameterNode()

  def getParentFolderItemID(self):
    shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    sceneItemID = shNode.GetSceneItemID()
    folderSubjectHierarchyID = shNode.GetItemByName("BoneReconstructionPlanner")
    if folderSubjectHierarchyID:
      return folderSubjectHierarchyID
    else:
      return shNode.CreateFolderItem(sceneItemID,"BoneReconstructionPlanner")

  def cleanup(self):
    """
    Called when the application closes and the module widget is destroyed.
    """
    self.removeObservers()

  @vtk.calldata_type(vtk.VTK_OBJECT)
  def onNodeAboutToBeRemovedEvent(self, caller, event, callData):
    if callData.GetClassName() == 'vtkMRMLMarkupsPlaneNode':
      if callData.GetAttribute("isMandibularPlane") == 'True':
        if len(self.logic.mandiblePlaneObserversAndNodeIDList) > 0:
          for i in range(len(self.logic.mandiblePlaneObserversAndNodeIDList)):
            if self.logic.mandiblePlaneObserversAndNodeIDList[i][1] == callData.GetID():
              observerIndex = i
          callData.RemoveObserver(self.logic.mandiblePlaneObserversAndNodeIDList.pop(observerIndex)[0])
        self.logic.onPlaneModifiedTimer(None,None)
      if callData.GetAttribute("isSawBoxPlane") == 'True':
        if len(self.logic.sawBoxPlaneObserversPlaneNodeIDAndTransformIDList) > 0:
          for i in range(len(self.logic.sawBoxPlaneObserversPlaneNodeIDAndTransformIDList)):
            if self.logic.sawBoxPlaneObserversPlaneNodeIDAndTransformIDList[i][1] == callData.GetID():
              observerIndex = i
          callData.RemoveObserver(self.logic.sawBoxPlaneObserversPlaneNodeIDAndTransformIDList.pop(observerIndex)[0])

  def enter(self):
    """
    Called each time the user opens this module.
    """
    # Make sure parameter node exists and observed
    self.initializeParameterNode()

    shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    segmentationModelsFolder = shNode.GetItemByName("Segmentation Models")
    fibulaPlanesFolder = shNode.GetItemByName("Fibula planes")
    cutBonesFolder = shNode.GetItemByName("Cut Bones")
    fibulaCylindersFiducialsListsFolder = shNode.GetItemByName("Fibula Cylinders Fiducials Lists")
    mandibleCylindersFiducialsListsFolder = shNode.GetItemByName("Mandible Cylinders Fiducials Lists")

    if segmentationModelsFolder:
      self.ui.generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandibleButton.enabled = True
    if fibulaCylindersFiducialsListsFolder:
      self.ui.createCylindersFromFiducialListAndFibulaSurgicalGuideBaseButton.enabled = True
    if mandibleCylindersFiducialsListsFolder:
      self.ui.createCylindersFromFiducialListAndMandibleSurgicalGuideBaseButton.enabled = True


    mandibularPlanesFolder = shNode.GetItemByName("Mandibular planes")
    mandibularPlanesList = createListFromFolderID(mandibularPlanesFolder)

    for i in range(len(mandibularPlanesList)):
      mandibularPlanesList[i].SetLocked(0)
      displayNode = mandibularPlanesList[i].GetDisplayNode()
      displayNode.HandlesInteractiveOn()
      observer = mandibularPlanesList[i].AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent,self.logic.onPlaneModifiedTimer)
      self.logic.mandiblePlaneObserversAndNodeIDList.append([observer,mandibularPlanesList[i].GetID()])

    if self.ui.scalarVolumeSelector.nodeCount() != 0 and self.ui.scalarVolumeSelector.currentNode() == None:
      self.ui.scalarVolumeSelector.setCurrentNodeIndex(0)#0 == first scalarVolume

  def exit(self):
    """
    Called each time the user opens a different module.
    """
    # Do not react to parameter node changes (GUI wlil be updated when the user enters into the module)
    self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

    shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    mandibularPlanesFolder = shNode.GetItemByName("Mandibular planes")
    mandibularPlanesList = createListFromFolderID(mandibularPlanesFolder)

    for i in range(len(mandibularPlanesList)):
      mandibularPlanesList[i].SetLocked(1)
      displayNode = mandibularPlanesList[i].GetDisplayNode()
      displayNode.HandlesInteractiveOff()
      mandibularPlanesList[i].RemoveObserver(self.logic.mandiblePlaneObserversAndNodeIDList[i][0])
    self.logic.mandiblePlaneObserversAndNodeIDList = []

  def onSceneStartClose(self, caller, event):
    """
    Called just before the scene is closed.
    """
    # Parameter node will be reset, do not use it anymore
    self.setParameterNode(None)

  def onSceneEndClose(self, caller, event):
    """
    Called just after the scene is closed.
    """
    # If this module is shown while the scene is closed then recreate a new parameter node immediately
    if self.parent.isEntered:
      self.initializeParameterNode()

  def initializeParameterNode(self):
    """
    Ensure parameter node exists and observed.
    """
    # Parameter node stores all user choices in parameter values, node selections, etc.
    # so that when the scene is saved and reloaded, these settings are restored.

    self.setParameterNode(self.logic.getParameterNode())

  def setParameterNode(self, inputParameterNode):
    """
    Set and observe parameter node.
    Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
    """

    if inputParameterNode:
      self.logic.setDefaultParameters(inputParameterNode)

    # Unobserve previously selected parameter node and add an observer to the newly selected.
    # Changes of parameter node are observed so that whenever parameters are changed by a script or any other module
    # those are reflected immediately in the GUI.
    if self._parameterNode is not None:
      self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
    self._parameterNode = inputParameterNode
    if self._parameterNode is not None:
      self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

    # Initial GUI update
    self.updateGUIFromParameterNode()

  def updateGUIFromParameterNode(self, caller=None, event=None):
    """
    This method is called whenever parameter node is changed.
    The module GUI is updated to show the current state of the parameter node.
    """

    if self._parameterNode is None or self._updatingGUIFromParameterNode:
      return

    # Make sure GUI changes do not call updateParameterNodeFromGUI (it could cause infinite loop)
    self._updatingGUIFromParameterNode = True

    # Update node selectors and sliders
    self.ui.fibulaLineSelector.setCurrentNode(self._parameterNode.GetNodeReference("fibulaLine"))
    self.ui.mandibleCurveSelector.setCurrentNode(self._parameterNode.GetNodeReference("mandibleCurve"))
    self.ui.mandibularSegmentationSelector.setCurrentNode(self._parameterNode.GetNodeReference("mandibularSegmentation"))
    self.ui.fibulaSegmentationSelector.setCurrentNode(self._parameterNode.GetNodeReference("fibulaSegmentation"))
    self.ui.fibulaFiducialListSelector.setCurrentNode(self._parameterNode.GetNodeReference("fibulaFiducialList"))
    self.ui.fibulaSurgicalGuideBaseSelector.setCurrentNode(self._parameterNode.GetNodeReference("fibulaSurgicalGuideBaseModel"))
    self.ui.miterBoxDirectionLineSelector.setCurrentNode(self._parameterNode.GetNodeReference("miterBoxDirectionLine"))
    self.ui.mandibleBridgeModelSelector.setCurrentNode(self._parameterNode.GetNodeReference("mandibleBridgeModel"))
    self.ui.mandibleSurgicalGuideBaseSelector.setCurrentNode(self._parameterNode.GetNodeReference("mandibleSurgicalGuideBaseModel"))
    self.ui.mandibleFiducialListSelector.setCurrentNode(self._parameterNode.GetNodeReference("mandibleFiducialList"))
    self.ui.scalarVolumeSelector.setCurrentNode(self._parameterNode.GetNodeReference("currentScalarVolume"))

    if self._parameterNode.GetParameter("initialSpace") != '':
      self.ui.initialSpinBox.setValue(float(self._parameterNode.GetParameter("initialSpace")))
    if self._parameterNode.GetParameter("intersectionPlaceOfFibulaPlanes") != '':
      self.ui.intersectionSpinBox.setValue(float(self._parameterNode.GetParameter("intersectionPlaceOfFibulaPlanes")))
    if self._parameterNode.GetParameter("additionalBetweenSpaceOfFibulaPlanes") != '':
      self.ui.betweenSpinBox.setValue(float(self._parameterNode.GetParameter("additionalBetweenSpaceOfFibulaPlanes")))
    if self._parameterNode.GetParameter("securityMarginOfFibulaPieces") != '':
      self.ui.securityMarginOfFibulaPiecesSpinBox.setValue(float(self._parameterNode.GetParameter("securityMarginOfFibulaPieces")))
    if self._parameterNode.GetParameter("miterBoxSlotWidth") != '':
      self.ui.miterBoxSlotWidthSpinBox.setValue(float(self._parameterNode.GetParameter("miterBoxSlotWidth")))
    if self._parameterNode.GetParameter("miterBoxSlotLength") != '':
      self.ui.miterBoxSlotLengthSpinBox.setValue(float(self._parameterNode.GetParameter("miterBoxSlotLength")))
    if self._parameterNode.GetParameter("miterBoxSlotHeight") != '':
      self.ui.miterBoxSlotHeightSpinBox.setValue(float(self._parameterNode.GetParameter("miterBoxSlotHeight")))
    if self._parameterNode.GetParameter("miterBoxSlotWall") != '':
      self.ui.miterBoxSlotWallSpinBox.setValue(float(self._parameterNode.GetParameter("miterBoxSlotWall")))
    if self._parameterNode.GetParameter("fibulaScrewHoleCylinderRadius") != '':
      self.ui.fibulaScrewHoleCylinderRadiusSpinBox.setValue(float(self._parameterNode.GetParameter("fibulaScrewHoleCylinderRadius")))
    if self._parameterNode.GetParameter("clearanceFitPrintingTolerance") != '':
      self.ui.clearanceFitPrintingToleranceSpinBox.setValue(float(self._parameterNode.GetParameter("clearanceFitPrintingTolerance")))
    if self._parameterNode.GetParameter("biggerMiterBoxDistanceToFibula") != '':
      self.ui.biggerMiterBoxDistanceToFibulaSpinBox.setValue(float(self._parameterNode.GetParameter("biggerMiterBoxDistanceToFibula")))
    if self._parameterNode.GetParameter("intersectionDistanceMultiplier") != '':
      self.ui.intersectionDistanceMultiplierSpinBox.setValue(float(self._parameterNode.GetParameter("intersectionDistanceMultiplier")))
    if self._parameterNode.GetParameter("sawBoxSlotWidth") != '':
      self.ui.sawBoxSlotWidthSpinBox.setValue(float(self._parameterNode.GetParameter("sawBoxSlotWidth")))
    if self._parameterNode.GetParameter("sawBoxSlotLength") != '':
      self.ui.sawBoxSlotLengthSpinBox.setValue(float(self._parameterNode.GetParameter("sawBoxSlotLength")))
    if self._parameterNode.GetParameter("sawBoxSlotHeight") != '':
      self.ui.sawBoxSlotHeightSpinBox.setValue(float(self._parameterNode.GetParameter("sawBoxSlotHeight")))
    if self._parameterNode.GetParameter("sawBoxSlotWall") != '':
      self.ui.sawBoxSlotWallSpinBox.setValue(float(self._parameterNode.GetParameter("sawBoxSlotWall")))
    if self._parameterNode.GetParameter("biggerSawBoxDistanceToMandible") != '':
      self.ui.biggerSawBoxDistanceToMandibleSpinBox.setValue(float(self._parameterNode.GetParameter("biggerSawBoxDistanceToMandible")))
    if self._parameterNode.GetParameter("mandibleScrewHoleCylinderRadius") != '':
      self.ui.mandibleScrewHoleCylinderRadiusSpinBox.setValue(float(self._parameterNode.GetParameter("mandibleScrewHoleCylinderRadius")))

    self.ui.notLeftFibulaCheckBox.checked = self._parameterNode.GetParameter("notLeftFibula") == "True"
    self.ui.makeAllMandiblePlanesRotateTogetherCheckBox.checked = self._parameterNode.GetParameter("makeAllMandiblePlanesRotateTogether") == "True"
    self.ui.useMoreExactVersionOfPositioningAlgorithmCheckBox.checked = self._parameterNode.GetParameter("useMoreExactVersionOfPositioningAlgorithm") == "True"
    self.ui.useNonDecimatedBoneModelsForPreviewCheckBox.checked = self._parameterNode.GetParameter("useNonDecimatedBoneModelsForPreview") == "True"
    self.ui.mandiblePlanesPositioningForMaximumBoneContactCheckBox.checked = self._parameterNode.GetParameter("mandiblePlanesPositioningForMaximumBoneContact") == "True"
    self.ui.checkSecurityMarginOnMiterBoxCreationCheckBox.checked = self._parameterNode.GetParameter("checkSecurityMarginOnMiterBoxCreation") != "False"
    if self._parameterNode.GetParameter("updateOnMandiblePlanesMovement") == "True":
      self.ui.generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandibleButton.checkState = 2
    else:
      self.ui.generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandibleButton.checkState = 0

    # All the GUI updates are done
    self._updatingGUIFromParameterNode = False

  def updateParameterNodeFromGUI(self, caller=None, event=None):
    """
    This method is called when the user makes any change in the GUI.
    The changes are saved into the parameter node (so that they are restored when the scene is saved and loaded).
    """

    if self._parameterNode is None or self._updatingGUIFromParameterNode:
      return

    wasModified = self._parameterNode.StartModify()  # Modify all properties in a single batch

    self._parameterNode.SetNodeReferenceID("mandibleCurve", self.ui.mandibleCurveSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("mandibularSegmentation", self.ui.mandibularSegmentationSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("fibulaSegmentation", self.ui.fibulaSegmentationSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("fibulaFiducialList", self.ui.fibulaFiducialListSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("fibulaSurgicalGuideBaseModel", self.ui.fibulaSurgicalGuideBaseSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("miterBoxDirectionLine", self.ui.miterBoxDirectionLineSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("mandibleBridgeModel", self.ui.mandibleBridgeModelSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("mandibleSurgicalGuideBaseModel", self.ui.mandibleSurgicalGuideBaseSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("mandibleFiducialList", self.ui.mandibleFiducialListSelector.currentNodeID)

    self._parameterNode.SetParameter("securityMarginOfFibulaPieces", str(self.ui.securityMarginOfFibulaPiecesSpinBox.value))
    self._parameterNode.SetParameter("miterBoxSlotWidth", str(self.ui.miterBoxSlotWidthSpinBox.value))
    self._parameterNode.SetParameter("miterBoxSlotLength", str(self.ui.miterBoxSlotLengthSpinBox.value))
    self._parameterNode.SetParameter("miterBoxSlotHeight", str(self.ui.miterBoxSlotHeightSpinBox.value))
    self._parameterNode.SetParameter("miterBoxSlotWall", str(self.ui.miterBoxSlotWallSpinBox.value))
    self._parameterNode.SetParameter("fibulaScrewHoleCylinderRadius", str(self.ui.fibulaScrewHoleCylinderRadiusSpinBox.value))
    self._parameterNode.SetParameter("clearanceFitPrintingTolerance", str(self.ui.clearanceFitPrintingToleranceSpinBox.value))
    self._parameterNode.SetParameter("biggerMiterBoxDistanceToFibula", str(self.ui.biggerMiterBoxDistanceToFibulaSpinBox.value))
    self._parameterNode.SetParameter("sawBoxSlotWidth", str(self.ui.sawBoxSlotWidthSpinBox.value))
    self._parameterNode.SetParameter("sawBoxSlotLength", str(self.ui.sawBoxSlotLengthSpinBox.value))
    self._parameterNode.SetParameter("sawBoxSlotHeight", str(self.ui.sawBoxSlotHeightSpinBox.value))
    self._parameterNode.SetParameter("sawBoxSlotWall", str(self.ui.sawBoxSlotWallSpinBox.value))
    self._parameterNode.SetParameter("biggerSawBoxDistanceToMandible", str(self.ui.biggerSawBoxDistanceToMandibleSpinBox.value))
    self._parameterNode.SetParameter("mandibleScrewHoleCylinderRadius", str(self.ui.mandibleScrewHoleCylinderRadiusSpinBox.value))
    

    if self.ui.notLeftFibulaCheckBox.checked:
      self._parameterNode.SetParameter("notLeftFibula","True")
    else:
      self._parameterNode.SetParameter("notLeftFibula","False")
    if self.ui.makeAllMandiblePlanesRotateTogetherCheckBox.checked:
      self._parameterNode.SetParameter("makeAllMandiblePlanesRotateTogether","True")
    else:
      self._parameterNode.SetParameter("makeAllMandiblePlanesRotateTogether","False")
    if self.ui.mandiblePlanesPositioningForMaximumBoneContactCheckBox.checked:
      self._parameterNode.SetParameter("mandiblePlanesPositioningForMaximumBoneContact","True")
    else:
      self._parameterNode.SetParameter("mandiblePlanesPositioningForMaximumBoneContact","False")
    if self.ui.useMoreExactVersionOfPositioningAlgorithmCheckBox.checked:
      self._parameterNode.SetParameter("useMoreExactVersionOfPositioningAlgorithm","True")
    else:
      self._parameterNode.SetParameter("useMoreExactVersionOfPositioningAlgorithm","False")
    if self.ui.useNonDecimatedBoneModelsForPreviewCheckBox.checked:
      self._parameterNode.SetParameter("useNonDecimatedBoneModelsForPreview","True")
    else:
      self._parameterNode.SetParameter("useNonDecimatedBoneModelsForPreview","False")
    if self.ui.checkSecurityMarginOnMiterBoxCreationCheckBox.checked:
      self._parameterNode.SetParameter("checkSecurityMarginOnMiterBoxCreation","True")
    else:
      self._parameterNode.SetParameter("checkSecurityMarginOnMiterBoxCreation","False")
    if self.ui.generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandibleButton.checkState == qt.Qt.Checked:
      self._parameterNode.SetParameter("updateOnMandiblePlanesMovement","True")
    else:
      self._parameterNode.SetParameter("updateOnMandiblePlanesMovement","False")

    self._parameterNode.EndModify(wasModified)

  def onFibulaPlanesCreationParametersChanged(self, caller=None, event=None):
    if self._parameterNode is None or self._updatingGUIFromParameterNode:
      return

    wasModified = self._parameterNode.StartModify()
    self._parameterNode.SetParameter("fibulaPlanesCreationParametersChanged", "True")
    self._parameterNode.SetParameter("initialSpace", str(self.ui.initialSpinBox.value))
    self._parameterNode.SetParameter("intersectionPlaceOfFibulaPlanes", str(self.ui.intersectionSpinBox.value))
    self._parameterNode.SetParameter("additionalBetweenSpaceOfFibulaPlanes", str(self.ui.betweenSpinBox.value))
    self._parameterNode.SetParameter("intersectionDistanceMultiplier", str(self.ui.intersectionDistanceMultiplierSpinBox.value))
    self._parameterNode.SetNodeReferenceID("fibulaLine", self.ui.fibulaLineSelector.currentNodeID)
    self._parameterNode.EndModify(wasModified)

  def onFixCutGoesThroughTheMandibleTwiceCheckBox(self):
    if self._parameterNode is None or self._updatingGUIFromParameterNode:
      return

    wasModified = self._parameterNode.StartModify()
    if self.ui.fixCutGoesThroughTheMandibleTwiceCheckBox.checked:
      self._parameterNode.SetParameter("fixCutGoesThroughTheMandibleTwice","True")
    else:
      self._parameterNode.SetParameter("fixCutGoesThroughTheMandibleTwice","False")
    self._parameterNode.SetParameter("fixCutGoesThroughTheMandibleTwiceCheckBoxChanged","True")
    self._parameterNode.EndModify(wasModified)

  def onUseMoreExactVersionOfPositioningAlgorithmCheckBox(self):
    if self._parameterNode is None or self._updatingGUIFromParameterNode:
      return

    wasModified = self._parameterNode.StartModify()
    if self.ui.useMoreExactVersionOfPositioningAlgorithmCheckBox.checked:
      self._parameterNode.SetParameter("useMoreExactVersionOfPositioningAlgorithm","True")
    else:
      self._parameterNode.SetParameter("useMoreExactVersionOfPositioningAlgorithm","False")
    self._parameterNode.SetParameter("useMoreExactVersionOfPositioningAlgorithmCheckBoxChanged","True")
    self._parameterNode.EndModify(wasModified)

  def onAddMandibularCurveButton(self):
    self.logic.addMandibularCurve()

  def onAddFibulaLineButton(self):
    self.logic.addFibulaLine()

  def onScalarVolumeChanged(self):
    if self._parameterNode is None or self._updatingGUIFromParameterNode:
      return

    self._parameterNode.SetNodeReferenceID("currentScalarVolume", self.ui.scalarVolumeSelector.currentNodeID)

    scalarVolume = self.ui.scalarVolumeSelector.currentNode()
    if scalarVolume != None:
      scalarVolumeID = scalarVolume.GetID()
      redSliceLogic = slicer.app.layoutManager().sliceWidget('Red').sliceLogic()
      redSliceLogic.GetSliceCompositeNode().SetBackgroundVolumeID(scalarVolumeID)
      greenSliceLogic = slicer.app.layoutManager().sliceWidget('Green').sliceLogic()
      greenSliceLogic.GetSliceCompositeNode().SetBackgroundVolumeID(scalarVolumeID)
      yellowSliceLogic = slicer.app.layoutManager().sliceWidget('Yellow').sliceLogic()
      yellowSliceLogic.GetSliceCompositeNode().SetBackgroundVolumeID(scalarVolumeID)

      slicer.util.resetSliceViews()

      fibulaCentroidX = self._parameterNode.GetParameter("fibulaCentroidX")
      fibulaCentroidY = self._parameterNode.GetParameter("fibulaCentroidY")
      fibulaCentroidZ = self._parameterNode.GetParameter("fibulaCentroidZ")
      mandibleCentroidX = self._parameterNode.GetParameter("mandibleCentroidX")
      mandibleCentroidY = self._parameterNode.GetParameter("mandibleCentroidY")
      mandibleCentroidZ = self._parameterNode.GetParameter("mandibleCentroidZ")
      
      if fibulaCentroidX != "":
        fibulaCentroid = np.array([float(fibulaCentroidX),float(fibulaCentroidY),float(fibulaCentroidZ)])
        mandibleCentroid = np.array([float(mandibleCentroidX),float(mandibleCentroidY),float(mandibleCentroidZ)])

        bounds = [0,0,0,0,0,0]
        scalarVolume.GetBounds(bounds)
        bounds = np.array(bounds)
        centerOfScalarVolume = np.array([(bounds[0]+bounds[1])/2,(bounds[2]+bounds[3])/2,(bounds[4]+bounds[5])/2])
      
        shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
        mandibularPlanesFolder = shNode.GetItemByName("Mandibular planes")
        fibulaPlanesFolder = shNode.GetItemByName("Fibula planes")
        biggerMiterBoxesFolder = shNode.GetItemByName("biggerMiterBoxes Models")
        cutBonesFolder = shNode.GetItemByName("Cut Bones")
        transformedFibulaPiecesFolder = shNode.GetItemByName("Transformed Fibula Pieces")
        mandibularPlanesList = createListFromFolderID(mandibularPlanesFolder)
        fibulaPlanesList = createListFromFolderID(fibulaPlanesFolder)
        biggerMiterBoxesList = createListFromFolderID(biggerMiterBoxesFolder)
        cutBonesList = createListFromFolderID(cutBonesFolder)
        transformedFibulaPiecesList = createListFromFolderID(transformedFibulaPiecesFolder)
        redSliceNode = slicer.mrmlScene.GetSingletonNode("Red", "vtkMRMLSliceNode")

        fibulaDisplayNodesWereUpdatedFlag = self._parameterNode.GetParameter("fibulaDisplayNodesWereUpdatedFlag")

        if np.linalg.norm(fibulaCentroid-centerOfScalarVolume) < np.linalg.norm(mandibleCentroid-centerOfScalarVolume):
          #When fibulaScalarVolume:
          if fibulaDisplayNodesWereUpdatedFlag == "" or fibulaDisplayNodesWereUpdatedFlag == "False":
            addIterationList = biggerMiterBoxesList + cutBonesList[0:(len(cutBonesList)-1)]
            removeIterationList = [cutBonesList[len(cutBonesList)-1]] + transformedFibulaPiecesList

            for i in range(len(addIterationList)):
              displayNode = addIterationList[i].GetDisplayNode()
              displayNode.AddViewNodeID(redSliceNode.GetID())
            
            for i in range(len(removeIterationList)):
              displayNode = removeIterationList[i].GetDisplayNode()
              displayNode.RemoveViewNodeID(redSliceNode.GetID())
            
            self._parameterNode.SetParameter("fibulaDisplayNodesWereUpdatedFlag","True")
        else:
          #When mandibleScalarVolume:
          if fibulaDisplayNodesWereUpdatedFlag == "" or fibulaDisplayNodesWereUpdatedFlag == "True":
            addIterationList = [cutBonesList[len(cutBonesList)-1]] + transformedFibulaPiecesList
            removeIterationList = biggerMiterBoxesList + cutBonesList[0:(len(cutBonesList)-1)]
            
            for i in range(len(addIterationList)):
              displayNode = addIterationList[i].GetDisplayNode()
              displayNode.AddViewNodeID(redSliceNode.GetID())
            
            for i in range(len(removeIterationList)):
              displayNode = removeIterationList[i].GetDisplayNode()
              displayNode.RemoveViewNodeID(redSliceNode.GetID())
            
            self._parameterNode.SetParameter("fibulaDisplayNodesWereUpdatedFlag","False")
    
  def onAddCutPlaneButton(self):
    self.logic.addCutPlane()

  def onMakeModelsButton(self):
    self.logic.makeModels()
    self.ui.generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandibleButton.enabled = True

  def onCreateMiterBoxesFromFibulaPlanesButton(self):
    self.logic.createMiterBoxesFromFibulaPlanes()

  def onCreateFibulaCylindersFiducialListButton(self):
    self.logic.createFibulaCylindersFiducialList()
    self.ui.createCylindersFromFiducialListAndFibulaSurgicalGuideBaseButton.enabled = True

  def onCreateCylindersFromFiducialListAndSurgicalGuideBaseButton(self):
    self.logic.createCylindersFromFiducialListAndFibulaSurgicalGuideBase()

  def onMakeBooleanOperationsToFibulaSurgicalGuideBaseButton(self):
    self.logic.makeBooleanOperationsToFibulaSurgicalGuideBase()

  def onCreateMandibleCylindersFiducialListButton(self):
    self.ui.createCylindersFromFiducialListAndMandibleSurgicalGuideBaseButton.enabled = True
    self.logic.createMandibleCylindersFiducialList()

  def onCreateSawBoxesFromFirstAndLastMandiblePlanesButton(self):
    self.logic.createSawBoxesFromFirstAndLastMandiblePlanes()

  def onMakeBooleanOperationsToMandibleSurgicalGuideBaseButton(self):
    self.logic.makeBooleanOperationsToMandibleSurgicalGuideBase()

  def onCreateCylindersFromFiducialListAndMandibleSurgicalGuideBaseButton(self):
    self.logic.createCylindersFromFiducialListAndMandibleSurgicalGuideBase()

  def onGenerateFibulaPlanesFibulaBonePiecesAndTransformThemToMandibleButton(self):
    self.logic.onGenerateFibulaPlanesTimerTimeout()

  def onCenterFibulaLineButton(self):
    self.logic.centerFibulaLine()
  
  def onShowHideBiggerSawBoxesInteractionHandlesButton(self):
    shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    sawBoxesPlanesFolder = shNode.GetItemByName("sawBoxes Planes")
    sawBoxesPlanesList = createListFromFolderID(sawBoxesPlanesFolder)

    for i in range(len(sawBoxesPlanesList)):
      displayNode = sawBoxesPlanesList[i].GetDisplayNode()
      handlesVisibility = displayNode.GetHandlesInteractive()
      displayNode.SetHandlesInteractive(not handlesVisibility)

  def onShowHideMandiblePlanesInteractionHandlesButton(self):
    shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    mandibularPlanesFolder = shNode.GetItemByName("Mandibular planes")
    mandibularPlanesList = createListFromFolderID(mandibularPlanesFolder)

    for i in range(len(mandibularPlanesList)):
      displayNode = mandibularPlanesList[i].GetDisplayNode()
      handlesVisibility = displayNode.GetHandlesInteractive()
      displayNode.SetHandlesInteractive(not handlesVisibility)

  def onShowHideFibulaSegmentsLengthsButton(self):
    shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    fibulaSegmentsLengthsFolder = shNode.GetItemByName("Fibula Segments Lengths")
    fibulaSegmentsLengthsList = createListFromFolderID(fibulaSegmentsLengthsFolder)

    for i in range(len(fibulaSegmentsLengthsList)):
      lineDisplayNode = fibulaSegmentsLengthsList[i].GetDisplayNode()
      visibility = lineDisplayNode.GetVisibility()
      lineDisplayNode.SetVisibility(not visibility)

  def onCreate3DModelOfTheReconstructionButton(self):
    self.logic.create3DModelOfTheReconstruction()

  def onShowHideOriginalMandibleButton(self):
    mandibleModelNode = self._parameterNode.GetNodeReference("mandibleModelNode")
    decimatedMandibleModelNode = self._parameterNode.GetNodeReference("decimatedMandibleModelNode")
    useNonDecimatedBoneModelsForPreviewChecked = self._parameterNode.GetParameter("useNonDecimatedBoneModelsForPreview") == "True"

    mandibleModelDisplayNode = mandibleModelNode.GetDisplayNode()
    decimatedMandibleModelDisplayNode = decimatedMandibleModelNode.GetDisplayNode()

    if mandibleModelDisplayNode.GetVisibility() or decimatedMandibleModelDisplayNode.GetVisibility():
      mandibleModelDisplayNode.SetVisibility(False)
      decimatedMandibleModelDisplayNode.SetVisibility(False)
    else:
      if useNonDecimatedBoneModelsForPreviewChecked:
        mandibleModelDisplayNode.SetVisibility(True)
      else:
        decimatedMandibleModelDisplayNode.SetVisibility(True)

    
#
# BoneReconstructionPlannerLogic
#

class BoneReconstructionPlannerLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self):
    """
    Called when the logic class is instantiated. Can be used for initializing member variables.
    """
    ScriptedLoadableModuleLogic.__init__(self)
    self.mandiblePlaneObserversAndNodeIDList = []
    self.sawBoxPlaneObserversPlaneNodeIDAndTransformIDList = []
    self.generateFibulaPlanesTimer = qt.QTimer()
    self.generateFibulaPlanesTimer.setInterval(300)
    self.generateFibulaPlanesTimer.setSingleShot(True)
    self.generateFibulaPlanesTimer.connect('timeout()', self.onGenerateFibulaPlanesTimerTimeout)

    customLayout = """
      <layout type="vertical">
      <item>
        <layout type="horizontal">
        <item>
          <view class="vtkMRMLViewNode" singletontag="1">
          <property name="viewlabel" action="default">1</property>
          </view>
        </item>
        <item>
          <view class="vtkMRMLSliceNode" singletontag="Red">
          <property name="orientation" action="default">Axial</property>
          <property name="viewlabel" action="default">R</property>
          <property name="viewcolor" action="default">#F34A33</property>
          </view>
        </item>
        </layout>
      </item>
      <item>
        <view class="vtkMRMLViewNode" singletontag="2">
        <property name="viewlabel" action="default">2</property>
        </view>
      </item>
      </layout>
    """
    # Built-in layout IDs are all below 100, so you can choose any large random number
    # for your custom layout ID.
    self.customLayoutId=101

    layoutManager = slicer.app.layoutManager()
    layoutManager.layoutLogic().GetLayoutNode().AddLayoutDescription(self.customLayoutId, customLayout)

    # Add button to layout selector toolbar for this custom layout
    viewToolBar = slicer.util.mainWindow().findChild('QToolBar', 'ViewToolBar')
    layoutMenu = viewToolBar.widgetForAction(viewToolBar.actions()[0]).menu()
    layoutSwitchActionParent = layoutMenu  # use `layoutMenu` to add inside layout list, use `viewToolBar` to add next the standard layout list
    layoutSwitchAction = layoutSwitchActionParent.addAction("BoneReconstructionPlanner") # add inside layout list
    layoutSwitchAction.setData(self.customLayoutId)
    layoutSwitchAction.setIcon(qt.QIcon(':Icons/Go.png'))
    layoutSwitchAction.setToolTip('3D Mandible View, Red Slice and 3D Fibula View')

  def setDefaultParameters(self, parameterNode):
    """
    Initialize parameter node with default settings.
    """
    if not parameterNode.GetParameter("Threshold"):
      parameterNode.SetParameter("Threshold", "100.0")
    if not parameterNode.GetParameter("Invert"):
      parameterNode.SetParameter("Invert", "false")

  def getParentFolderItemID(self):
    shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    sceneItemID = shNode.GetSceneItemID()
    folderSubjectHierarchyID = shNode.GetItemByName("BoneReconstructionPlanner")
    if folderSubjectHierarchyID:
      return folderSubjectHierarchyID
    else:
      return shNode.CreateFolderItem(sceneItemID,"BoneReconstructionPlanner")

  def getMandiblePlanesFolderItemID(self):
    shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    folderSubjectHierarchyID = shNode.GetItemByName("Mandibular planes")
    if folderSubjectHierarchyID:
      return folderSubjectHierarchyID
    else:
      return shNode.CreateFolderItem(self.getParentFolderItemID(),"Mandibular planes")

  def addMandibularCurve(self):
    curveNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLMarkupsCurveNode")
    curveNode.SetName("temp")
    slicer.mrmlScene.AddNode(curveNode)
    slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(curveNode)
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    curveNodeItemID = shNode.GetItemByDataNode(curveNode)
    shNode.SetItemParent(curveNodeItemID, self.getParentFolderItemID())
    curveNode.SetName(slicer.mrmlScene.GetUniqueNameByString("mandibularCurve"))

    displayNode = curveNode.GetDisplayNode()
    mandibleViewNode = slicer.mrmlScene.GetSingletonNode("1", "vtkMRMLViewNode")
    displayNode.AddViewNodeID(mandibleViewNode.GetID())

    #setup placement
    slicer.modules.markups.logic().SetActiveListID(curveNode)
    interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
    interactionNode.SwitchToSinglePlaceMode()

  def addFibulaLine(self):
    parameterNode = self.getParameterNode()
    scalarVolume = parameterNode.GetNodeReference("currentScalarVolume")
    fibulaCentroidX = parameterNode.GetParameter("fibulaCentroidX")
    fibulaCentroidY = parameterNode.GetParameter("fibulaCentroidY")
    fibulaCentroidZ = parameterNode.GetParameter("fibulaCentroidZ")
    mandibleCentroidX = parameterNode.GetParameter("mandibleCentroidX")
    mandibleCentroidY = parameterNode.GetParameter("mandibleCentroidY")
    mandibleCentroidZ = parameterNode.GetParameter("mandibleCentroidZ")
    
    fibulaCentroid = np.array([float(fibulaCentroidX),float(fibulaCentroidY),float(fibulaCentroidZ)])
    mandibleCentroid = np.array([float(mandibleCentroidX),float(mandibleCentroidY),float(mandibleCentroidZ)])

    bounds = [0,0,0,0,0,0]
    scalarVolume.GetBounds(bounds)
    bounds = np.array(bounds)
    centerOfScalarVolume = np.array([(bounds[0]+bounds[1])/2,(bounds[2]+bounds[3])/2,(bounds[4]+bounds[5])/2])
    

    lineNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLMarkupsLineNode")
    lineNode.SetName("temp")
    slicer.mrmlScene.AddNode(lineNode)
    slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(lineNode)
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    lineNodeItemID = shNode.GetItemByDataNode(lineNode)
    shNode.SetItemParent(lineNodeItemID, self.getParentFolderItemID())
    lineNode.SetName(slicer.mrmlScene.GetUniqueNameByString("fibulaLine"))

    displayNode = lineNode.GetDisplayNode()
    fibulaViewNode = slicer.mrmlScene.GetSingletonNode("2", "vtkMRMLViewNode")
    displayNode.AddViewNodeID(fibulaViewNode.GetID())

    if np.linalg.norm(fibulaCentroid-centerOfScalarVolume) < np.linalg.norm(mandibleCentroid-centerOfScalarVolume):
      redSliceNode = slicer.mrmlScene.GetSingletonNode("Red", "vtkMRMLSliceNode")
      displayNode.AddViewNodeID(redSliceNode.GetID())

    #setup placement
    slicer.modules.markups.logic().SetActiveListID(lineNode)
    interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
    interactionNode.SwitchToSinglePlaceMode()

  def addCutPlane(self):
    parameterNode = self.getParameterNode()

    colorIndexStr = parameterNode.GetParameter("colorIndex")
    if colorIndexStr != "":
      colorIndex = int(colorIndexStr) + 1
      parameterNode.SetParameter("colorIndex", str(colorIndex))
    else:
      colorIndex = 0
      parameterNode.SetParameter("colorIndex", str(colorIndex))

    planeNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLMarkupsPlaneNode")
    planeNode.SetName("temp")
    slicer.mrmlScene.AddNode(planeNode)
    slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(planeNode)
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    mandibularFolderID = self.getMandiblePlanesFolderItemID()
    planeNodeItemID = shNode.GetItemByDataNode(planeNode)
    shNode.SetItemParent(planeNodeItemID, mandibularFolderID)
    planeNode.SetName(slicer.mrmlScene.GetUniqueNameByString("mandibularPlane"))
    planeNode.SetAttribute("isMandibularPlane","True")

    aux = slicer.mrmlScene.GetNodeByID('vtkMRMLColorTableNodeFileMediumChartColors.txt')
    colorTable = aux.GetLookupTable()
    ind = colorIndex%8
    colorwithalpha = colorTable.GetTableValue(ind)
    color = [colorwithalpha[0],colorwithalpha[1],colorwithalpha[2]]

    #display node of the plane
    displayNode = planeNode.GetDisplayNode()
    displayNode.SetGlyphScale(2.5)
    displayNode.SetSelectedColor(color)

    mandibleViewNode = slicer.mrmlScene.GetSingletonNode("1", "vtkMRMLViewNode")
    displayNode.AddViewNodeID(mandibleViewNode.GetID())

    #conections
    self.planeNodeObserver = planeNode.AddObserver(slicer.vtkMRMLMarkupsNode.PointPositionDefinedEvent,self.onPlanePointAdded)

    #setup placement
    slicer.modules.markups.logic().SetActiveListID(planeNode)
    interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
    interactionNode.SwitchToSinglePlaceMode()

  def onPlanePointAdded(self,sourceNode,event):
    parameterNode = self.getParameterNode()
    mandibleCurve = parameterNode.GetNodeReference("mandibleCurve")

    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    mandibularPlanesFolder = shNode.GetItemByName("Mandibular planes")
    mandibularPlanesList = createListFromFolderID(mandibularPlanesFolder)

    temporalOrigin = [0,0,0]
    sourceNode.GetNthControlPointPosition(0,temporalOrigin)
    
    self.setupMandiblePlaneStraightOverMandibleCurve(sourceNode,temporalOrigin, mandibleCurve, self.planeNodeObserver)

    displayNode = sourceNode.GetDisplayNode()
    displayNode.HandlesInteractiveOn()
    for i in range(3):
      sourceNode.SetNthControlPointVisibility(i,False)
    observer = sourceNode.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent,self.onPlaneModifiedTimer)
    self.mandiblePlaneObserversAndNodeIDList.append([observer,sourceNode.GetID()])

    mandiblePlaneAndCurvePointIndexList = []
    for i in range(len(mandibularPlanesList)):
      origin = [0,0,0]
      mandibularPlanesList[i].GetNthControlPointPosition(0,origin)
      closestCurvePoint = [0,0,0]
      closestCurvePointIndex = mandibleCurve.GetClosestPointPositionAlongCurveWorld(origin,closestCurvePoint)
      mandiblePlaneAndCurvePointIndexList.append([mandibularPlanesList[i],closestCurvePointIndex])
    
    mandiblePlaneAndCurvePointIndexList.sort(key = lambda item : item[1])

    mandibularPlanesFolder2 = shNode.CreateFolderItem(self.getParentFolderItemID(),"Mandibular planes 2")
    
    for i in range(len(mandiblePlaneAndCurvePointIndexList)):
      mandiblePlane = mandiblePlaneAndCurvePointIndexList[i][0]
      mandiblePlaneItemID = shNode.GetItemByDataNode(mandiblePlane)
      shNode.SetItemParent(mandiblePlaneItemID, mandibularPlanesFolder2)

    shNode.RemoveItem(mandibularPlanesFolder)
    shNode.SetItemName(mandibularPlanesFolder2,"Mandibular planes")
  
  def onPlaneModifiedTimer(self,sourceNode,event):
    parameterNode = self.getParameterNode()
    updateOnMandiblePlanesMovementChecked = parameterNode.GetParameter("updateOnMandiblePlanesMovement") == "True"
    makeAllMandiblePlanesRotateTogetherChecked = parameterNode.GetParameter("makeAllMandiblePlanesRotateTogether") == "True"
    
    if makeAllMandiblePlanesRotateTogetherChecked and sourceNode != None:
      parameterNode.SetNodeReferenceID("mandiblePlaneOfRotation", sourceNode.GetID())

    if updateOnMandiblePlanesMovementChecked:
      self.generateFibulaPlanesTimer.start()

  def onGenerateFibulaPlanesTimerTimeout(self):
    import time
    startTime = time.time()
    logging.info('Processing started')

    shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    mandibularPlanesFolder = shNode.GetItemByName("Mandibular planes")
    mandibularPlanesList = createListFromFolderID(mandibularPlanesFolder)

    parameterNode = self.getParameterNode()
    mandiblePlanesPositioningForMaximumBoneContactChecked = parameterNode.GetParameter("mandiblePlanesPositioningForMaximumBoneContact") == "True"
    makeAllMandiblePlanesRotateTogetherChecked = parameterNode.GetParameter("makeAllMandiblePlanesRotateTogether") == "True"
    mandiblePlaneOfRotation = parameterNode.GetNodeReference("mandiblePlaneOfRotation")
    fibulaLine = parameterNode.GetNodeReference("fibulaLine")

    if len(mandibularPlanesList):
      if makeAllMandiblePlanesRotateTogetherChecked and mandiblePlanesPositioningForMaximumBoneContactChecked:
        self.removeMandiblePlanesObservers()
        self.mandiblePlanesPositioningForMaximumBoneContact()
        self.transformMandiblePlanesZRotationToBeTheSameAsInputPlane(mandiblePlaneOfRotation)
        self.addMandiblePlaneObservers()
      else:
        if mandiblePlanesPositioningForMaximumBoneContactChecked:
          self.removeMandiblePlanesObservers()
          self.mandiblePlanesPositioningForMaximumBoneContact()
          self.addMandiblePlaneObservers()
        else:
          if makeAllMandiblePlanesRotateTogetherChecked:
            self.removeMandiblePlanesObservers()
            self.transformMandiblePlanesZRotationToBeTheSameAsInputPlane(mandiblePlaneOfRotation)
            self.addMandiblePlaneObservers()

    if fibulaLine != None:
      try:
        # Compute output
        self.generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandible()

      except Exception as e:
        slicer.util.errorDisplay("Failed to compute results: "+str(e))
        import traceback
        traceback.print_exc()  

    stopTime = time.time()
    logging.info('Processing completed in {0:.2f} seconds\n'.format(stopTime-startTime))

  def transformMandiblePlanesZRotationToBeTheSameAsInputPlane(self,mandiblePlaneOfRotation):
    shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    mandibularPlanesFolder = shNode.GetItemByName("Mandibular planes")
    mandibularPlanesList = createListFromFolderID(mandibularPlanesFolder)
    mandiblePlanesTransformsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),'Mandible Planes Transforms')

    if mandiblePlaneOfRotation == None:
      mandiblePlaneOfRotation = mandibularPlanesList[0]

    mandiblePlaneOfRotationMatrix = vtk.vtkMatrix4x4()
    if int(slicer.app.revision) > int(SLICER_CHANGE_OF_API_REVISION):
      mandiblePlaneOfRotation.GetObjectToWorldMatrix(mandiblePlaneOfRotationMatrix)
    else:
      mandiblePlaneOfRotation.GetPlaneToWorldMatrix(mandiblePlaneOfRotationMatrix)
    mandiblePlaneOfRotationX = np.array([mandiblePlaneOfRotationMatrix.GetElement(0,0),mandiblePlaneOfRotationMatrix.GetElement(1,0),mandiblePlaneOfRotationMatrix.GetElement(2,0)])
    mandiblePlaneOfRotationY = np.array([mandiblePlaneOfRotationMatrix.GetElement(0,1),mandiblePlaneOfRotationMatrix.GetElement(1,1),mandiblePlaneOfRotationMatrix.GetElement(2,1)])
    mandiblePlaneOfRotationZ = np.array([mandiblePlaneOfRotationMatrix.GetElement(0,2),mandiblePlaneOfRotationMatrix.GetElement(1,2),mandiblePlaneOfRotationMatrix.GetElement(2,2)])
        
    for i in range(len(mandibularPlanesList)):
      if mandiblePlaneOfRotation.GetID() != mandibularPlanesList[i].GetID():
        mandiblePlaneMatrix = vtk.vtkMatrix4x4()
        if int(slicer.app.revision) > int(SLICER_CHANGE_OF_API_REVISION):
          mandibularPlanesList[i].GetObjectToWorldMatrix(mandiblePlaneMatrix)
        else:
          mandibularPlanesList[i].GetPlaneToWorldMatrix(mandiblePlaneMatrix)
        mandiblePlaneX = np.array([mandiblePlaneMatrix.GetElement(0,0),mandiblePlaneMatrix.GetElement(1,0),mandiblePlaneMatrix.GetElement(2,0)])
        mandiblePlaneY = np.array([mandiblePlaneMatrix.GetElement(0,1),mandiblePlaneMatrix.GetElement(1,1),mandiblePlaneMatrix.GetElement(2,1)])
        mandiblePlaneZ = np.array([mandiblePlaneMatrix.GetElement(0,2),mandiblePlaneMatrix.GetElement(1,2),mandiblePlaneMatrix.GetElement(2,2)])
        mandiblePlaneOrigin = np.array([mandiblePlaneMatrix.GetElement(0,3),mandiblePlaneMatrix.GetElement(1,3),mandiblePlaneMatrix.GetElement(2,3)])

        rotatedMandiblePlaneX = np.copy(mandiblePlaneX)
        rotatedMandiblePlaneY =  np.copy(mandiblePlaneY)
        rotatedMandiblePlaneZ = np.copy(mandiblePlaneZ)
        
        epsilon = 0.0001
        if not (vtk.vtkMath.Dot(rotatedMandiblePlaneZ, mandiblePlaneOfRotationZ) >= 1.0 - epsilon):
          angleRadians = vtk.vtkMath.AngleBetweenVectors(rotatedMandiblePlaneZ, mandiblePlaneOfRotationZ)
          rotationAxis = [0,0,0]
          vtk.vtkMath.Cross(mandiblePlaneOfRotationZ, rotatedMandiblePlaneZ, rotationAxis)
          if (vtk.vtkMath.Norm(rotationAxis) < epsilon):
            #New + old normals are facing opposite directions.
            #Find a perpendicular axis to flip around.
            vtk.vtkMath.Perpendiculars(mandiblePlaneOfRotationZ, rotationAxis, None, 0)
          rotationAxis = rotationAxis/np.linalg.norm(rotationAxis)
          finalTransform = vtk.vtkTransform()
          finalTransform.PostMultiply()
          finalTransform.RotateWXYZ(vtk.vtkMath.DegreesFromRadians(angleRadians), rotationAxis)

          finalTransform.TransformVector(mandiblePlaneOfRotationX, rotatedMandiblePlaneX)
          finalTransform.TransformVector(mandiblePlaneOfRotationY, rotatedMandiblePlaneY)

        mandiblePlaneToWorldRotationMatrix = self.getAxes1ToWorldRotationMatrix(mandiblePlaneX, mandiblePlaneY, mandiblePlaneZ)
        rotatedMandiblePlaneToWorldRotationMatrix = self.getAxes1ToWorldRotationMatrix(rotatedMandiblePlaneX, rotatedMandiblePlaneY, rotatedMandiblePlaneZ)

        mandiblePlaneToRotatedMandiblePlaneRotationMatrix = self.getAxes1ToAxes2RotationMatrix(mandiblePlaneToWorldRotationMatrix, rotatedMandiblePlaneToWorldRotationMatrix)

        transformNode = slicer.vtkMRMLLinearTransformNode()
        transformNode.SetName("temp%d" % i)
        slicer.mrmlScene.AddNode(transformNode)

        finalTransform = vtk.vtkTransform()
        finalTransform.PostMultiply()
        finalTransform.Translate(-mandiblePlaneOrigin)
        finalTransform.Concatenate(mandiblePlaneToRotatedMandiblePlaneRotationMatrix)
        finalTransform.Translate(mandiblePlaneOrigin)
        transformNode.SetMatrixTransformToParent(finalTransform.GetMatrix())

        transformNode.UpdateScene(slicer.mrmlScene)

        mandibularPlanesList[i].SetAndObserveTransformNodeID(transformNode.GetID())
        mandibularPlanesList[i].HardenTransform()
        
        transformNodeItemID = shNode.GetItemByDataNode(transformNode)
        shNode.SetItemParent(transformNodeItemID, mandiblePlanesTransformsFolder)
      
    shNode.RemoveItem(mandiblePlanesTransformsFolder)

  def addMandiblePlaneObservers(self):
    shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    mandibularPlanesFolder = shNode.GetItemByName("Mandibular planes")
    mandibularPlanesList = createListFromFolderID(mandibularPlanesFolder)

    for i in range(len(mandibularPlanesList)):
      observer = mandibularPlanesList[i].AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent,self.onPlaneModifiedTimer)
      self.mandiblePlaneObserversAndNodeIDList.append([observer,mandibularPlanesList[i].GetID()])

  def removeMandiblePlanesObservers(self):
    shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    mandibularPlanesFolder = shNode.GetItemByName("Mandibular planes")
    mandibularPlanesList = createListFromFolderID(mandibularPlanesFolder)

    for i in range(len(mandibularPlanesList)):
      mandiblePlane = slicer.mrmlScene.GetNodeByID(self.mandiblePlaneObserversAndNodeIDList[i][1])
      mandiblePlane.RemoveObserver(self.mandiblePlaneObserversAndNodeIDList[i][0])
    self.mandiblePlaneObserversAndNodeIDList = []

  def transformFibulaPlanes(self):
    parameterNode = self.getParameterNode()
    fibulaLine = parameterNode.GetNodeReference("fibulaLine")
    lastMandiblePlanesPositionCurve = parameterNode.GetNodeReference("lastMandiblePlanesPositionCurve")
    lastFibulaPlanesPositionA = parameterNode.GetNodeReference("lastFibulaPlanesPositionA")
    lastFibulaPlanesPositionB = parameterNode.GetNodeReference("lastFibulaPlanesPositionB")
    initialSpace = float(parameterNode.GetParameter("initialSpace"))
    intersectionPlaceOfFibulaPlanes = float(parameterNode.GetParameter("intersectionPlaceOfFibulaPlanes"))
    intersectionDistanceMultiplier = float(parameterNode.GetParameter("intersectionDistanceMultiplier"))
    additionalBetweenSpaceOfFibulaPlanes = float(parameterNode.GetParameter("additionalBetweenSpaceOfFibulaPlanes"))
    notLeftFibulaChecked = parameterNode.GetParameter("notLeftFibula") == "True"
    useMoreExactVersionOfPositioningAlgorithmChecked = parameterNode.GetParameter("useMoreExactVersionOfPositioningAlgorithm") == "True"
    useMoreExactVersionOfPositioningAlgorithmCheckBoxChanged = parameterNode.GetParameter("useMoreExactVersionOfPositioningAlgorithmCheckBoxChanged") == "True"
    fibulaPlanesCreationParametersChanged = parameterNode.GetParameter("fibulaPlanesCreationParametersChanged") == "True"
    fibulaModelNode = parameterNode.GetNodeReference("fibulaModelNode")
    planeList = createListFromFolderID(self.getMandiblePlanesFolderItemID())
    
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    fibulaPlanesFolder = shNode.GetItemByName("Fibula planes")
    fibulaPlanesList = createListFromFolderID(fibulaPlanesFolder)
    
    #Delete old fibulaPlanesTransforms
    mandible2FibulaTransformsFolder = shNode.GetItemByName("Mandible2Fibula transforms")
    shNode.RemoveItem(mandible2FibulaTransformsFolder)
    mandible2FibulaTransformsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Mandible2Fibula transforms")
    
    if lastMandiblePlanesPositionCurve == None:
      lastMandiblePlanesPositionCurve = self.createLastMandiblePlanesPositionCurve()
      parameterNode.SetNodeReferenceID("lastMandiblePlanesPositionCurve", lastMandiblePlanesPositionCurve.GetID())
      mandiblePlanesOriginsAreTheSame = False
    
    else:
      mandiblePlanesOriginsAreTheSame = True
      if len(planeList) != lastMandiblePlanesPositionCurve.GetNumberOfControlPoints():
        mandiblePlanesOriginsAreTheSame = False
      else:
        for mandiblePlaneIndex in range(len(planeList)):
          lastMandiblePlanePosition = np.zeros(3)
          mandiblePlanePosition = np.zeros(3)
          lastMandiblePlanesPositionCurve.GetNthControlPointPosition(mandiblePlaneIndex,lastMandiblePlanePosition)
          planeList[mandiblePlaneIndex].GetOrigin(mandiblePlanePosition)
          if np.linalg.norm(lastMandiblePlanePosition-mandiblePlanePosition) > 1e-5:
            mandiblePlanesOriginsAreTheSame = False
    
    lastFibulaPlanesPositionsExist = lastFibulaPlanesPositionA != None and lastFibulaPlanesPositionB != None
    if lastFibulaPlanesPositionsExist:
      lastFibulaPlanesPositionsExistAndIsValid = (lastFibulaPlanesPositionA.GetNumberOfControlPoints() + lastFibulaPlanesPositionB.GetNumberOfControlPoints()) == (2*len(planeList) -2)
    else:
      lastFibulaPlanesPositionsExistAndIsValid = False
    
    #This line avoids recalculating the fibulaPlanesPosition when mandiblePlanes just rotate
    if not mandiblePlanesOriginsAreTheSame or not lastFibulaPlanesPositionsExistAndIsValid or useMoreExactVersionOfPositioningAlgorithmCheckBoxChanged or fibulaPlanesCreationParametersChanged:
      #Create fibula axis:
      fibulaX, fibulaY, fibulaZ, fibulaOrigin = self.createFibulaAxisFromFibulaLineAndNotLeftChecked(fibulaLine,notLeftFibulaChecked) 
      
      fibulaZLineNorm = getLineNorm(fibulaLine)

      #NewPlanes position and distance
      self.fibulaPlanesPositionA = []
      self.fibulaPlanesPositionB = []
      boneSegmentsDistance = []

      #Set up transform for intersections to measure betweenSpace
      intersectionsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Intersections")

      fibulaToRASRotationMatrix = self.getAxes1ToWorldRotationMatrix(fibulaX,fibulaY,fibulaZ)

      intersectionsTransformNode = slicer.vtkMRMLLinearTransformNode()
      intersectionsTransformNode.SetName("intersectionsTransform")
      slicer.mrmlScene.AddNode(intersectionsTransformNode)

      intersectionsTransform = vtk.vtkTransform()
      intersectionsTransform.PostMultiply()
      intersectionsTransform.Translate(-fibulaOrigin)
      intersectionsTransform.Concatenate(fibulaToRASRotationMatrix)
      intersectionsTransform.Translate(fibulaOrigin)

      intersectionsTransformNode.SetMatrixTransformToParent(intersectionsTransform.GetMatrix())
      intersectionsTransformNode.UpdateScene(slicer.mrmlScene)

      intersectionsTransformNodeItemID = shNode.GetItemByDataNode(intersectionsTransformNode)
      shNode.SetItemParent(intersectionsTransformNodeItemID, intersectionsFolder)

      intersectionsList = []
      betweenSpace = []
      j=0

      self.mandibleAxisToFibulaRotationMatrixesList = []
      #Transform fibula planes to their final position-orientation
      for i in range(len(planeList)-1):
        mandiblePlane0 = planeList[i]
        mandiblePlane1 = planeList[i+1]
        mandiblePlane0X = [0,0,0]
        mandiblePlane0Y = [0,0,0]
        mandiblePlane0Z = [0,0,0]
        mandiblePlane0.GetAxes(mandiblePlane0X,mandiblePlane0Y,mandiblePlane0Z)
        mandiblePlane1X = [0,0,0]
        mandiblePlane1Y = [0,0,0]
        mandiblePlane1Z = [0,0,0]
        mandiblePlane1.GetAxes(mandiblePlane1X,mandiblePlane1Y,mandiblePlane1Z)
        mandiblePlane0Origin = [0,0,0]
        mandiblePlane0.GetOrigin(mandiblePlane0Origin)
        mandiblePlane1Origin = [0,0,0]
        mandiblePlane1.GetOrigin(mandiblePlane1Origin)
        fibulaPlaneA = fibulaPlanesList[2*i]
        fibulaPlaneB = fibulaPlanesList[2*i+1]
        fibulaPlaneA.SetAxes(mandiblePlane0X,mandiblePlane0Y,mandiblePlane0Z)
        fibulaPlaneA.SetOrigin(mandiblePlane0Origin)
        fibulaPlaneB.SetAxes(mandiblePlane1X,mandiblePlane1Y,mandiblePlane1Z)
        fibulaPlaneB.SetOrigin(mandiblePlane1Origin)

        #Create origin1-origin2 vector
        or0 = np.zeros(3)
        or1 = np.zeros(3)
        mandiblePlane0.GetOrigin(or0)
        mandiblePlane1.GetOrigin(or1)
        boneSegmentsDistance.append(np.linalg.norm(or1-or0))
        mandibleAxisZ = (or1-or0)/np.linalg.norm(or1-or0)
        
        #Get Y component of mandiblePlane0
        mandiblePlane0matrix = vtk.vtkMatrix4x4()
        if int(slicer.app.revision) > int(SLICER_CHANGE_OF_API_REVISION):
          mandiblePlane0.GetObjectToWorldMatrix(mandiblePlane0matrix)
        else:
          mandiblePlane0.GetPlaneToWorldMatrix(mandiblePlane0matrix)
        mandiblePlane0Y = np.array([mandiblePlane0matrix.GetElement(0,1),mandiblePlane0matrix.GetElement(1,1),mandiblePlane0matrix.GetElement(2,1)])
        
        mandibleAxisX = [0,0,0]
        vtk.vtkMath.Cross(mandiblePlane0Y, mandibleAxisZ, mandibleAxisX)
        mandibleAxisX = mandibleAxisX/np.linalg.norm(mandibleAxisX)
        mandibleAxisY = [0,0,0]
        vtk.vtkMath.Cross(mandibleAxisZ, mandibleAxisX, mandibleAxisY)
        mandibleAxisY = mandibleAxisY/np.linalg.norm(mandibleAxisY)

        mandibleAxisToWorldRotationMatrix = self.getAxes1ToWorldRotationMatrix(mandibleAxisX, mandibleAxisY, mandibleAxisZ)
        #Create fibula axis:
        fibulaX, fibulaY, fibulaZ, fibulaOrigin = self.createFibulaAxisFromFibulaLineAndNotLeftChecked(fibulaLine,notLeftFibulaChecked) 
        fibulaToWorldRotationMatrix = self.getAxes1ToWorldRotationMatrix(fibulaX, fibulaY, fibulaZ)

        mandibleAxisToFibulaRotationMatrix = self.getAxes1ToAxes2RotationMatrix(mandibleAxisToWorldRotationMatrix, fibulaToWorldRotationMatrix)

        mandiblePlane0ToIntersectionAxisTransform = vtk.vtkTransform()
        mandiblePlane0ToIntersectionAxisTransform.PostMultiply()
        mandiblePlane0ToIntersectionAxisTransform.Translate(-mandiblePlane0Origin[0], -mandiblePlane0Origin[1], -mandiblePlane0Origin[2])
        mandiblePlane0ToIntersectionAxisTransform.Concatenate(mandibleAxisToFibulaRotationMatrix)
        mandiblePlane0ToIntersectionAxisTransform.Translate(fibulaOrigin + fibulaZ*fibulaZLineNorm*intersectionPlaceOfFibulaPlanes)
        mandiblePlane1ToIntersectionAxisTransform = vtk.vtkTransform()
        mandiblePlane1ToIntersectionAxisTransform.PostMultiply()
        mandiblePlane1ToIntersectionAxisTransform.Translate(-mandiblePlane1Origin[0], -mandiblePlane1Origin[1], -mandiblePlane1Origin[2])
        mandiblePlane1ToIntersectionAxisTransform.Concatenate(mandibleAxisToFibulaRotationMatrix)
        mandiblePlane1ToIntersectionAxisTransform.Translate(fibulaOrigin + fibulaZ*fibulaZLineNorm*intersectionPlaceOfFibulaPlanes)
        
        if i==0:
          self.fibulaPlanesPositionA.append(fibulaOrigin + fibulaZ*initialSpace)
          intersectionModelB = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Intersection%d_B' % i)
          intersectionModelB.CreateDefaultDisplayNodes()
          getIntersectionBetweenModelAnd1TransformedPlane(fibulaModelNode, mandiblePlane1ToIntersectionAxisTransform, fibulaPlaneB, intersectionModelB)
          intersectionsList.append(intersectionModelB)
          intersectionsList[j].SetAndObserveTransformNodeID(intersectionsTransformNode.GetID())
          
          intersectionModelBItemID = shNode.GetItemByDataNode(intersectionModelB)
          shNode.SetItemParent(intersectionModelBItemID, intersectionsFolder)

        else:
          bounds0 = [0,0,0,0,0,0]
          bounds1 = [0,0,0,0,0,0]
          if i!=(len(planeList)-2):
            intersectionModelA = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Intersection%d_A' % i)
            intersectionModelA.CreateDefaultDisplayNodes()
            getIntersectionBetweenModelAnd1TransformedPlane(fibulaModelNode, mandiblePlane0ToIntersectionAxisTransform, fibulaPlaneA, intersectionModelA)
            intersectionsList.append(intersectionModelA)
            intersectionModelAItemID = shNode.GetItemByDataNode(intersectionModelA)
            shNode.SetItemParent(intersectionModelAItemID, intersectionsFolder)
            j=j+1
            intersectionModelB = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Intersection%d_B' % i)
            intersectionModelB.CreateDefaultDisplayNodes()
            getIntersectionBetweenModelAnd1TransformedPlane(fibulaModelNode, mandiblePlane1ToIntersectionAxisTransform, fibulaPlaneB, intersectionModelB)
            intersectionsList.append(intersectionModelB)
            intersectionModelBItemID = shNode.GetItemByDataNode(intersectionModelB)
            shNode.SetItemParent(intersectionModelBItemID, intersectionsFolder)
            j=j+1
            intersectionsList[j-1].SetAndObserveTransformNodeID(intersectionsTransformNode.GetID())
            intersectionsList[j].SetAndObserveTransformNodeID(intersectionsTransformNode.GetID())
            intersectionsList[j-2].GetRASBounds(bounds0)
            intersectionsList[(j-2)+1].GetRASBounds(bounds1)
          else:
            intersectionModelA = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Intersection%d_A' % i)
            intersectionModelA.CreateDefaultDisplayNodes()
            getIntersectionBetweenModelAnd1TransformedPlane(fibulaModelNode, mandiblePlane0ToIntersectionAxisTransform, fibulaPlaneA, intersectionModelA)
            intersectionsList.append(intersectionModelA)
            intersectionModelAItemID = shNode.GetItemByDataNode(intersectionModelA)
            shNode.SetItemParent(intersectionModelAItemID, intersectionsFolder)
            j=j+1
            intersectionsList[j].SetAndObserveTransformNodeID(intersectionsTransformNode.GetID())
            intersectionsList[j-1].GetRASBounds(bounds0)
            intersectionsList[j].GetRASBounds(bounds1)

          #calculate how much each FibulaPlaneA should be translated so that it doesn't intersect with fibulaPlaneB
          z0Sup = bounds0[5]
          z0Inf = bounds0[4]
          z1Sup = bounds1[5]
          z1Inf = bounds1[4]
          deltaZ = (z0Sup - z0Inf)/2 + (z1Sup - z1Inf)/2

          betweenSpace.append(deltaZ)

          self.fibulaPlanesPositionA.append(self.fibulaPlanesPositionB[i-1] + fibulaZ*(intersectionDistanceMultiplier*betweenSpace[i-1]+additionalBetweenSpaceOfFibulaPlanes))

        self.fibulaPlanesPositionB.append(self.fibulaPlanesPositionA[i] + boneSegmentsDistance[i]*fibulaZ)

        if not useMoreExactVersionOfPositioningAlgorithmChecked:
          self.mandibleAxisToFibulaRotationMatrixesList.append(mandibleAxisToFibulaRotationMatrix)
        else:
          intersectionsForCentroidCalculationFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Intersections For Centroid Calculation")

          lineStartPos = self.fibulaPlanesPositionA.pop()
          lineEndPos = self.fibulaPlanesPositionB.pop()

          numberOfRepetitionsOfPositioningAlgorithm = 5
          for k in range(numberOfRepetitionsOfPositioningAlgorithm):
            oldLineStartPos = lineStartPos
            oldLineEndPos = lineEndPos

            fibulaLineNorm = np.linalg.norm(lineEndPos-lineStartPos)
            fibulaLineDirection = (lineEndPos-lineStartPos)/fibulaLineNorm

            intersectionA = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Intersection A %d' % i)
            intersectionB = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Intersection B %d' % i)
            intersectionA.CreateDefaultDisplayNodes()
            intersectionB.CreateDefaultDisplayNodes()
            
            intersectionAModelItemID = shNode.GetItemByDataNode(intersectionA)
            shNode.SetItemParent(intersectionAModelItemID, intersectionsForCentroidCalculationFolder)
            intersectionBModelItemID = shNode.GetItemByDataNode(intersectionB)
            shNode.SetItemParent(intersectionBModelItemID, intersectionsForCentroidCalculationFolder)
            
            getIntersectionBetweenModelAnd1PlaneWithNormalAndOrigin_2(fibulaModelNode,fibulaLineDirection,lineStartPos,intersectionA)
            getIntersectionBetweenModelAnd1PlaneWithNormalAndOrigin_2(fibulaModelNode,fibulaLineDirection,lineEndPos,intersectionB)
            lineStartPos = getCentroid(intersectionA)
            lineEndPos = getCentroid(intersectionB)

            #Create fibula axis:
            fibulaX, fibulaY, fibulaZ, fibulaOrigin = self.createFibulaAxisFromFibulaLineAndNotLeftChecked_2(lineStartPos,lineEndPos,notLeftFibulaChecked)
            
            lineEndPos = lineStartPos + boneSegmentsDistance[i]*fibulaZ

            error = np.linalg.norm(lineStartPos-oldLineStartPos) + np.linalg.norm(lineEndPos-oldLineEndPos)
            if error < 0.01:# Unavoidable errors because of fibula bone shape are about 0.6-0.8mm
              break
          
          fibulaToWorldRotationMatrix = self.getAxes1ToWorldRotationMatrix(fibulaX, fibulaY, fibulaZ)
          mandibleAxisToFibulaRotationMatrix = self.getAxes1ToAxes2RotationMatrix(mandibleAxisToWorldRotationMatrix, fibulaToWorldRotationMatrix)
          self.mandibleAxisToFibulaRotationMatrixesList.append(mandibleAxisToFibulaRotationMatrix)

          self.fibulaPlanesPositionA.append(lineStartPos)
          self.fibulaPlanesPositionB.append(lineEndPos)

          shNode.RemoveItem(intersectionsForCentroidCalculationFolder)

        mandiblePlane0ToFibulaPlaneATransformNode = slicer.vtkMRMLLinearTransformNode()
        mandiblePlane0ToFibulaPlaneATransformNode.SetName("Mandible2Fibula Transform%d_A" % i)
        slicer.mrmlScene.AddNode(mandiblePlane0ToFibulaPlaneATransformNode)
        mandiblePlane1ToFibulaPlaneBTransformNode = slicer.vtkMRMLLinearTransformNode()
        mandiblePlane1ToFibulaPlaneBTransformNode.SetName("Mandible2Fibula Transform%d_B" % i)
        slicer.mrmlScene.AddNode(mandiblePlane1ToFibulaPlaneBTransformNode)

        mandiblePlane0ToFibulaPlaneATransform = vtk.vtkTransform()
        mandiblePlane0ToFibulaPlaneATransform.PostMultiply()
        mandiblePlane0ToFibulaPlaneATransform.Translate(-mandiblePlane0Origin[0], -mandiblePlane0Origin[1], -mandiblePlane0Origin[2])
        mandiblePlane0ToFibulaPlaneATransform.Concatenate(mandibleAxisToFibulaRotationMatrix)
        mandiblePlane0ToFibulaPlaneATransform.Translate(self.fibulaPlanesPositionA[i])

        mandiblePlane0ToFibulaPlaneATransformNode.SetMatrixTransformToParent(mandiblePlane0ToFibulaPlaneATransform.GetMatrix())
        mandiblePlane0ToFibulaPlaneATransformNode.UpdateScene(slicer.mrmlScene)


        mandiblePlane1ToFibulaPlaneBTransform = vtk.vtkTransform()
        mandiblePlane1ToFibulaPlaneBTransform.PostMultiply()
        mandiblePlane1ToFibulaPlaneBTransform.Translate(-mandiblePlane1Origin[0], -mandiblePlane1Origin[1], -mandiblePlane1Origin[2])
        mandiblePlane1ToFibulaPlaneBTransform.Concatenate(mandibleAxisToFibulaRotationMatrix)
        mandiblePlane1ToFibulaPlaneBTransform.Translate(self.fibulaPlanesPositionB[i])

        mandiblePlane1ToFibulaPlaneBTransformNode.SetMatrixTransformToParent(mandiblePlane1ToFibulaPlaneBTransform.GetMatrix())

        mandiblePlane1ToFibulaPlaneBTransformNode.UpdateScene(slicer.mrmlScene)

        fibulaPlaneA.SetAndObserveTransformNodeID(mandiblePlane0ToFibulaPlaneATransformNode.GetID())
        fibulaPlaneB.SetAndObserveTransformNodeID(mandiblePlane1ToFibulaPlaneBTransformNode.GetID())
        fibulaPlaneA.HardenTransform()
        fibulaPlaneB.HardenTransform()

        mandiblePlane0ToFibulaPlaneATransformNodeItemID = shNode.GetItemByDataNode(mandiblePlane0ToFibulaPlaneATransformNode)
        shNode.SetItemParent(mandiblePlane0ToFibulaPlaneATransformNodeItemID, mandible2FibulaTransformsFolder)
        mandiblePlane1ToFibulaPlaneBTransformNodeItemID = shNode.GetItemByDataNode(mandiblePlane1ToFibulaPlaneBTransformNode)
        shNode.SetItemParent(mandiblePlane1ToFibulaPlaneBTransformNodeItemID, mandible2FibulaTransformsFolder)

      shNode.RemoveItem(intersectionsFolder)

      if useMoreExactVersionOfPositioningAlgorithmCheckBoxChanged:
        parameterNode.SetParameter("useMoreExactVersionOfPositioningAlgorithmCheckBoxChanged","False")

      if fibulaPlanesCreationParametersChanged:
        parameterNode.SetParameter("fibulaPlanesCreationParametersChanged","False")

      if not mandiblePlanesOriginsAreTheSame:
        curvePointsList = []
        for mandiblePlaneIndex in range(len(planeList)):
          mandiblePlaneOrigin = [0,0,0]
          planeList[mandiblePlaneIndex].GetOrigin(mandiblePlaneOrigin)
          curvePointsList.append(mandiblePlaneOrigin)
        
        points = vtk.vtkPoints()
        curvePointsArray = np.array(curvePointsList)
        vtkPointsData = vtk.util.numpy_support.numpy_to_vtk(curvePointsArray, deep=1)
        points.SetNumberOfPoints(len(curvePointsArray))
        points.SetData(vtkPointsData)
        lastMandiblePlanesPositionCurve.SetControlPointPositionsWorld(points)

      if not lastFibulaPlanesPositionsExistAndIsValid:
        #delete curve that is alone
        slicer.mrmlScene.RemoveNode(lastFibulaPlanesPositionA)
        slicer.mrmlScene.RemoveNode(lastFibulaPlanesPositionB)
        lastFibulaPlanesPositionA = self.createCurveNodeFromListOfPointsAndName(self.fibulaPlanesPositionA,"lastFibulaPlanesPositionA")
        lastFibulaPlanesPositionB = self.createCurveNodeFromListOfPointsAndName(self.fibulaPlanesPositionB,"lastFibulaPlanesPositionB")
        parameterNode.SetNodeReferenceID("lastFibulaPlanesPositionA",lastFibulaPlanesPositionA.GetID())
        parameterNode.SetNodeReferenceID("lastFibulaPlanesPositionB",lastFibulaPlanesPositionB.GetID())
        #Create measurement lines
        self.createFibulaSegmentsLengthsLines(self.fibulaPlanesPositionA,self.fibulaPlanesPositionB)
      else:
        curveNodes = [lastFibulaPlanesPositionA,lastFibulaPlanesPositionB]
        pointLists = [self.fibulaPlanesPositionA,self.fibulaPlanesPositionB]
        for i in range (len(curveNodes)):
          points = vtk.vtkPoints()
          curvePointsArray = np.array(pointLists[i])
          vtkPointsData = vtk.util.numpy_support.numpy_to_vtk(curvePointsArray, deep=1)
          points.SetNumberOfPoints(len(curvePointsArray))
          points.SetData(vtkPointsData)
          curveNodes[i].SetControlPointPositionsWorld(points)

        #Update measurement lines
        fibulaSegmentsLengthsFolder = shNode.GetItemByName("Fibula Segments Lengths")
        fibulaSegmentsLengthsList = createListFromFolderID(fibulaSegmentsLengthsFolder)
        for i in range(len(fibulaSegmentsLengthsList)):
          fibulaSegmentLengthLine = fibulaSegmentsLengthsList[i]
          fibulaSegmentLengthLine.SetNthControlPointPositionFromArray(0,self.fibulaPlanesPositionA[i])
          fibulaSegmentLengthLine.SetNthControlPointPositionFromArray(1,self.fibulaPlanesPositionB[i])
    else:
      #Create fibula axis:
      fibulaX, fibulaY, fibulaZ, fibulaOrigin = self.createFibulaAxisFromFibulaLineAndNotLeftChecked(fibulaLine,notLeftFibulaChecked) 
      
      fibulaZLineNorm = getLineNorm(fibulaLine)

      self.fibulaPlanesPositionA = []
      self.fibulaPlanesPositionB = []

      self.mandibleAxisToFibulaRotationMatrixesList = []
      #Transform fibula planes to their final position-orientation
      for i in range(len(planeList)-1):
        mandiblePlane0 = planeList[i]
        mandiblePlane1 = planeList[i+1]
        mandiblePlane0X = [0,0,0]
        mandiblePlane0Y = [0,0,0]
        mandiblePlane0Z = [0,0,0]
        mandiblePlane0.GetAxes(mandiblePlane0X,mandiblePlane0Y,mandiblePlane0Z)
        mandiblePlane1X = [0,0,0]
        mandiblePlane1Y = [0,0,0]
        mandiblePlane1Z = [0,0,0]
        mandiblePlane1.GetAxes(mandiblePlane1X,mandiblePlane1Y,mandiblePlane1Z)
        mandiblePlane0Origin = [0,0,0]
        mandiblePlane0.GetOrigin(mandiblePlane0Origin)
        mandiblePlane1Origin = [0,0,0]
        mandiblePlane1.GetOrigin(mandiblePlane1Origin)
        fibulaPlaneA = fibulaPlanesList[2*i]
        fibulaPlaneB = fibulaPlanesList[2*i+1]
        fibulaPlaneA.SetAxes(mandiblePlane0X,mandiblePlane0Y,mandiblePlane0Z)
        fibulaPlaneA.SetOrigin(mandiblePlane0Origin)
        fibulaPlaneB.SetAxes(mandiblePlane1X,mandiblePlane1Y,mandiblePlane1Z)
        fibulaPlaneB.SetOrigin(mandiblePlane1Origin)

        #Create origin1-origin2 vector
        or0 = np.zeros(3)
        or1 = np.zeros(3)
        mandiblePlane0.GetOrigin(or0)
        mandiblePlane1.GetOrigin(or1)
        mandibleAxisZ = (or1-or0)/np.linalg.norm(or1-or0)
        
        #Get Y component of mandiblePlane0
        mandiblePlane0matrix = vtk.vtkMatrix4x4()
        if int(slicer.app.revision) > int(SLICER_CHANGE_OF_API_REVISION):
          mandiblePlane0.GetObjectToWorldMatrix(mandiblePlane0matrix)
        else:
          mandiblePlane0.GetPlaneToWorldMatrix(mandiblePlane0matrix)
        mandiblePlane0Y = np.array([mandiblePlane0matrix.GetElement(0,1),mandiblePlane0matrix.GetElement(1,1),mandiblePlane0matrix.GetElement(2,1)])
        
        mandibleAxisX = [0,0,0]
        vtk.vtkMath.Cross(mandiblePlane0Y, mandibleAxisZ, mandibleAxisX)
        mandibleAxisX = mandibleAxisX/np.linalg.norm(mandibleAxisX)
        mandibleAxisY = [0,0,0]
        vtk.vtkMath.Cross(mandibleAxisZ, mandibleAxisX, mandibleAxisY)
        mandibleAxisY = mandibleAxisY/np.linalg.norm(mandibleAxisY)

        mandibleAxisToWorldRotationMatrix = self.getAxes1ToWorldRotationMatrix(mandibleAxisX, mandibleAxisY, mandibleAxisZ)
        #Create fibula axis:
        fibulaX, fibulaY, fibulaZ, fibulaOrigin = self.createFibulaAxisFromFibulaLineAndNotLeftChecked(fibulaLine,notLeftFibulaChecked) 
        fibulaToWorldRotationMatrix = self.getAxes1ToWorldRotationMatrix(fibulaX, fibulaY, fibulaZ)

        mandibleAxisToFibulaRotationMatrix = self.getAxes1ToAxes2RotationMatrix(mandibleAxisToWorldRotationMatrix, fibulaToWorldRotationMatrix)

        fibulaPlaneAPosition = np.zeros(3)
        fibulaPlaneBPosition = np.zeros(3)
        lastFibulaPlanesPositionA.GetNthControlPointPosition(i,fibulaPlaneAPosition)
        lastFibulaPlanesPositionB.GetNthControlPointPosition(i,fibulaPlaneBPosition)
        self.fibulaPlanesPositionA.append(fibulaPlaneAPosition)
        self.fibulaPlanesPositionB.append(fibulaPlaneBPosition)

        if not useMoreExactVersionOfPositioningAlgorithmChecked:
          self.mandibleAxisToFibulaRotationMatrixesList.append(mandibleAxisToFibulaRotationMatrix)
        else:
          #Create fibula axis:
          fibulaX, fibulaY, fibulaZ, fibulaOrigin = self.createFibulaAxisFromFibulaLineAndNotLeftChecked_2(fibulaPlaneAPosition,fibulaPlaneBPosition,notLeftFibulaChecked)
          
          fibulaToWorldRotationMatrix = self.getAxes1ToWorldRotationMatrix(fibulaX, fibulaY, fibulaZ)
          mandibleAxisToFibulaRotationMatrix = self.getAxes1ToAxes2RotationMatrix(mandibleAxisToWorldRotationMatrix, fibulaToWorldRotationMatrix)
          self.mandibleAxisToFibulaRotationMatrixesList.append(mandibleAxisToFibulaRotationMatrix)

        mandiblePlane0ToFibulaPlaneATransformNode = slicer.vtkMRMLLinearTransformNode()
        mandiblePlane0ToFibulaPlaneATransformNode.SetName("Mandible2Fibula Transform%d_A" % i)
        slicer.mrmlScene.AddNode(mandiblePlane0ToFibulaPlaneATransformNode)
        mandiblePlane1ToFibulaPlaneBTransformNode = slicer.vtkMRMLLinearTransformNode()
        mandiblePlane1ToFibulaPlaneBTransformNode.SetName("Mandible2Fibula Transform%d_B" % i)
        slicer.mrmlScene.AddNode(mandiblePlane1ToFibulaPlaneBTransformNode)

        mandiblePlane0ToFibulaPlaneATransform = vtk.vtkTransform()
        mandiblePlane0ToFibulaPlaneATransform.PostMultiply()
        mandiblePlane0ToFibulaPlaneATransform.Translate(-mandiblePlane0Origin[0], -mandiblePlane0Origin[1], -mandiblePlane0Origin[2])
        mandiblePlane0ToFibulaPlaneATransform.Concatenate(mandibleAxisToFibulaRotationMatrix)
        mandiblePlane0ToFibulaPlaneATransform.Translate(fibulaPlaneAPosition)

        mandiblePlane0ToFibulaPlaneATransformNode.SetMatrixTransformToParent(mandiblePlane0ToFibulaPlaneATransform.GetMatrix())
        mandiblePlane0ToFibulaPlaneATransformNode.UpdateScene(slicer.mrmlScene)


        mandiblePlane1ToFibulaPlaneBTransform = vtk.vtkTransform()
        mandiblePlane1ToFibulaPlaneBTransform.PostMultiply()
        mandiblePlane1ToFibulaPlaneBTransform.Translate(-mandiblePlane1Origin[0], -mandiblePlane1Origin[1], -mandiblePlane1Origin[2])
        mandiblePlane1ToFibulaPlaneBTransform.Concatenate(mandibleAxisToFibulaRotationMatrix)
        mandiblePlane1ToFibulaPlaneBTransform.Translate(fibulaPlaneBPosition)

        mandiblePlane1ToFibulaPlaneBTransformNode.SetMatrixTransformToParent(mandiblePlane1ToFibulaPlaneBTransform.GetMatrix())

        mandiblePlane1ToFibulaPlaneBTransformNode.UpdateScene(slicer.mrmlScene)

        fibulaPlaneA.SetAndObserveTransformNodeID(mandiblePlane0ToFibulaPlaneATransformNode.GetID())
        fibulaPlaneB.SetAndObserveTransformNodeID(mandiblePlane1ToFibulaPlaneBTransformNode.GetID())
        fibulaPlaneA.HardenTransform()
        fibulaPlaneB.HardenTransform()

        mandiblePlane0ToFibulaPlaneATransformNodeItemID = shNode.GetItemByDataNode(mandiblePlane0ToFibulaPlaneATransformNode)
        shNode.SetItemParent(mandiblePlane0ToFibulaPlaneATransformNodeItemID, mandible2FibulaTransformsFolder)
        mandiblePlane1ToFibulaPlaneBTransformNodeItemID = shNode.GetItemByDataNode(mandiblePlane1ToFibulaPlaneBTransformNode)
        shNode.SetItemParent(mandiblePlane1ToFibulaPlaneBTransformNodeItemID, mandible2FibulaTransformsFolder)

  def createFibulaSegmentsLengthsLines(self,fibulaPlanesAPosition,fibulaPlanesBPosition):
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    fibulaSegmentsLengthsFolder = shNode.GetItemByName("Fibula Segments Lengths")
    shNode.RemoveItem(fibulaSegmentsLengthsFolder)
    fibulaSegmentsLengthsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Fibula Segments Lengths")
    
    for i in range(len(fibulaPlanesAPosition)):
      lineNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLMarkupsLineNode")
      lineNode.SetName("S%d" %i)
      slicer.mrmlScene.AddNode(lineNode)
      slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(lineNode)
      lineNodeItemID = shNode.GetItemByDataNode(lineNode)
      shNode.SetItemParent(lineNodeItemID, fibulaSegmentsLengthsFolder)

      displayNode = lineNode.GetDisplayNode()
      fibulaViewNode = slicer.mrmlScene.GetSingletonNode("2", "vtkMRMLViewNode")
      displayNode.AddViewNodeID(fibulaViewNode.GetID())
      displayNode.SetOccludedVisibility(True)
      
      lineNode.AddControlPoint(vtk.vtkVector3d(fibulaPlanesAPosition[i]))
      lineNode.AddControlPoint(vtk.vtkVector3d(fibulaPlanesBPosition[i]))

      lineNode.SetLocked(True)
  
  def createCurveNodeFromListOfPointsAndName(self,listOfPoints, name):
    curveNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLMarkupsCurveNode")
    curveNode.SetName("temp")
    slicer.mrmlScene.AddNode(curveNode)
    slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(curveNode)
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    curveNodeItemID = shNode.GetItemByDataNode(curveNode)
    shNode.SetItemParent(curveNodeItemID, self.getParentFolderItemID())
    curveNode.SetName(slicer.mrmlScene.GetUniqueNameByString(name))
    curveNode.SetLocked(True)

    displayNode = curveNode.GetDisplayNode()
    displayNode.SetVisibility(False)
    
    points = vtk.vtkPoints()
    curvePointsArray = np.array(listOfPoints)
    vtkPointsData = vtk.util.numpy_support.numpy_to_vtk(curvePointsArray, deep=1)
    points.SetNumberOfPoints(len(curvePointsArray))
    points.SetData(vtkPointsData)
    curveNode.SetControlPointPositionsWorld(points)

    return curveNode
  
  def createLastMandiblePlanesPositionCurve(self):
    planeList = createListFromFolderID(self.getMandiblePlanesFolderItemID())

    curvePointsList = []
    for mandiblePlaneIndex in range(len(planeList)):
      mandiblePlaneOrigin = [0,0,0]
      planeList[mandiblePlaneIndex].GetOrigin(mandiblePlaneOrigin)
      curvePointsList.append(mandiblePlaneOrigin)
    
    name = "lastMandiblePlanesPositionCurve"

    return self.createCurveNodeFromListOfPointsAndName(curvePointsList, name)

  
  def createFibulaPlanesFromMandiblePlanesAndFibulaAxis(self,mandiblePlanesList,fibulaPlanesList):
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    fibulaPlanesFolder = shNode.GetItemByName("Fibula planes")
    for i in range(len(mandiblePlanesList)-1):
      mandiblePlane0 = mandiblePlanesList[i]
      mandiblePlane1 = mandiblePlanesList[i+1]
      mandiblePlane0X = [0,0,0]
      mandiblePlane0Y = [0,0,0]
      mandiblePlane0Z = [0,0,0]
      mandiblePlane0.GetAxes(mandiblePlane0X,mandiblePlane0Y,mandiblePlane0Z)
      mandiblePlane1X = [0,0,0]
      mandiblePlane1Y = [0,0,0]
      mandiblePlane1Z = [0,0,0]
      mandiblePlane1.GetAxes(mandiblePlane1X,mandiblePlane1Y,mandiblePlane1Z)
      mandiblePlane0Origin = [0,0,0]
      mandiblePlane0.GetOrigin(mandiblePlane0Origin)
      mandiblePlane1Origin = [0,0,0]
      mandiblePlane1.GetOrigin(mandiblePlane1Origin)

      fibulaPlaneA = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsPlaneNode", "FibulaPlane%d_A" % i)
      slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(fibulaPlaneA)

      displayNode = fibulaPlaneA.GetDisplayNode()
      fibulaViewNode = slicer.mrmlScene.GetSingletonNode("2", "vtkMRMLViewNode")
      displayNode.AddViewNodeID(fibulaViewNode.GetID())
      displayNode.SetPropertiesLabelVisibility(False)

      fibulaPlaneAItemID = shNode.GetItemByDataNode(fibulaPlaneA)
      shNode.SetItemParent(fibulaPlaneAItemID, fibulaPlanesFolder)

      fibulaPlaneA.SetAxes(mandiblePlane0X,mandiblePlane0Y,mandiblePlane0Z)
      fibulaPlaneA.SetOrigin(mandiblePlane0Origin)
      fibulaPlaneA.SetLocked(True)
      fibulaPlanesList.append(fibulaPlaneA)


      fibulaPlaneB = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsPlaneNode", "FibulaPlane%d_B" % i)
      slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(fibulaPlaneB)

      displayNode = fibulaPlaneB.GetDisplayNode()
      displayNode.AddViewNodeID(fibulaViewNode.GetID())
      displayNode.SetPropertiesLabelVisibility(False)

      fibulaPlaneBItemID = shNode.GetItemByDataNode(fibulaPlaneB)
      shNode.SetItemParent(fibulaPlaneBItemID, fibulaPlanesFolder)

      fibulaPlaneB.SetAxes(mandiblePlane1X,mandiblePlane1Y,mandiblePlane1Z)
      fibulaPlaneB.SetOrigin(mandiblePlane1Origin)
      fibulaPlaneB.SetLocked(True)
      fibulaPlanesList.append(fibulaPlaneB)


      #Set new planes size
      oldPlanes = [mandiblePlane0,mandiblePlane1]
      newPlanes = [fibulaPlaneA,fibulaPlaneB]
      for j in range(2):
        o1 = np.zeros(3)
        x1 = np.zeros(3)
        y1 = np.zeros(3)
        oldPlanes[j].GetNthControlPointPosition(0,o1)
        oldPlanes[j].GetNthControlPointPosition(1,x1)
        oldPlanes[j].GetNthControlPointPosition(2,y1)
        xd1 = np.sqrt(vtk.vtkMath.Distance2BetweenPoints(o1,x1)) 
        yd1 = np.sqrt(vtk.vtkMath.Distance2BetweenPoints(o1,y1)) 

        on1 = np.zeros(3)
        xn1 = np.zeros(3)
        yn1 = np.zeros(3)
        newPlanes[j].GetNthControlPointPosition(0,on1)
        newPlanes[j].GetNthControlPointPosition(1,xn1)
        newPlanes[j].GetNthControlPointPosition(2,yn1)
        xnpv1 = (xn1-on1)/np.linalg.norm(xn1-on1)
        ynpv1 = (yn1-on1)/np.linalg.norm(yn1-on1)
        newPlanes[j].SetNthControlPointPositionFromArray(1,on1+xd1*xnpv1)
        newPlanes[j].SetNthControlPointPositionFromArray(2,on1+yd1*ynpv1)

        for i in range(3):
          newPlanes[j].SetNthControlPointVisibility(i,False)

    #Set up color for fibula planes
    for i in range(len(mandiblePlanesList)):
      if i == 0:
        oldDisplayNode = mandiblePlanesList[i].GetDisplayNode()
        color = oldDisplayNode.GetSelectedColor()

        displayNode = fibulaPlanesList[0].GetDisplayNode()
        displayNode.SetSelectedColor(color)
      else:
        if i == len(mandiblePlanesList)-1:
          oldDisplayNode = mandiblePlanesList[i].GetDisplayNode()
          color = oldDisplayNode.GetSelectedColor()

          displayNode = fibulaPlanesList[len(fibulaPlanesList)-1].GetDisplayNode()
          displayNode.SetSelectedColor(color)
        else:
          oldDisplayNode = mandiblePlanesList[i].GetDisplayNode()
          color = oldDisplayNode.GetSelectedColor()

          displayNode1 = fibulaPlanesList[2*i-1].GetDisplayNode()
          displayNode1.SetSelectedColor(color)
          displayNode2 = fibulaPlanesList[2*i].GetDisplayNode()
          displayNode2.SetSelectedColor(color)

  def createAndUpdateDynamicModelerNodes(self):
    parameterNode = self.getParameterNode()
    useNonDecimatedBoneModelsForPreviewChecked = parameterNode.GetParameter("useNonDecimatedBoneModelsForPreview") == "True"
    mandibularCurve = parameterNode.GetNodeReference("mandibleCurve")
    nonDecimatedFibulaModelNode = parameterNode.GetNodeReference("fibulaModelNode")
    decimatedFibulaModelNode = parameterNode.GetNodeReference("decimatedFibulaModelNode")
    nonDecimatedMandibleModelNode = parameterNode.GetNodeReference("mandibleModelNode")
    decimatedMandibleModelNode = parameterNode.GetNodeReference("decimatedMandibleModelNode")
    fixCutGoesThroughTheMandibleTwiceCheckBoxChanged = parameterNode.GetParameter('fixCutGoesThroughTheMandibleTwiceCheckBoxChanged') == "True"
    fixCutGoesThroughTheMandibleTwiceChecked = parameterNode.GetParameter('fixCutGoesThroughTheMandibleTwice') == "True"
    planeToFixCutGoesThroughTheMandibleTwice = parameterNode.GetNodeReference("planeToFixCutGoesThroughTheMandibleTwice")
    planeList = createListFromFolderID(self.getMandiblePlanesFolderItemID())
     
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    fibulaPlanesFolder = shNode.GetItemByName("Fibula planes")
    fibulaPlanesList = createListFromFolderID(fibulaPlanesFolder)
    
    if useNonDecimatedBoneModelsForPreviewChecked:
      nonDecimatedFibulaModelDisplayNode = nonDecimatedFibulaModelNode.GetDisplayNode()
      nonDecimatedFibulaModelDisplayNode.SetVisibility(True)
      decimatedFibulaModelDisplayNode = decimatedFibulaModelNode.GetDisplayNode()
      decimatedFibulaModelDisplayNode.SetVisibility(False)

      fibulaModelNode = nonDecimatedFibulaModelNode
      mandibleModelNode = nonDecimatedMandibleModelNode
    else:
      nonDecimatedFibulaModelDisplayNode = nonDecimatedFibulaModelNode.GetDisplayNode()
      nonDecimatedFibulaModelDisplayNode.SetVisibility(False)
      decimatedFibulaModelDisplayNode = decimatedFibulaModelNode.GetDisplayNode()
      decimatedFibulaModelDisplayNode.SetVisibility(True)

      fibulaModelNode = decimatedFibulaModelNode
      mandibleModelNode = decimatedMandibleModelNode

    planeCutsFolder = shNode.GetItemByName("Plane Cuts")
    if planeCutsFolder == 0 or fixCutGoesThroughTheMandibleTwiceCheckBoxChanged:
      shNode.RemoveItem(planeCutsFolder)
      cutBonesFolder = shNode.GetItemByName("Cut Bones")
      shNode.RemoveItem(cutBonesFolder)
      planeCutsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Plane Cuts")
      cutBonesFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Cut Bones")

      for i in range(0,len(fibulaPlanesList),2):
        modelNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLModelNode")
        modelNode.SetName("Fibula Segment {0}A-{1}B".format(i//2,i//2))
        slicer.mrmlScene.AddNode(modelNode)
        modelNode.CreateDefaultDisplayNodes()
        modelDisplayNode = modelNode.GetDisplayNode()
        modelDisplayNode.SetSliceIntersectionVisibility(True)

        fibulaViewNode = slicer.mrmlScene.GetSingletonNode("2", "vtkMRMLViewNode")
        modelDisplayNode.AddViewNodeID(fibulaViewNode.GetID())

        #Set color of the model
        aux = slicer.mrmlScene.GetNodeByID('vtkMRMLColorTableNodeFileMediumChartColors.txt')
        colorTable = aux.GetLookupTable()
        nColors = colorTable.GetNumberOfColors()
        ind = int((nColors-1) - i/2)
        colorwithalpha = colorTable.GetTableValue(ind)
        color = [colorwithalpha[0],colorwithalpha[1],colorwithalpha[2]]
        modelDisplayNode.SetColor(color)

        #Determinate plane creation direction and set up dynamic modeler
        planeOriginStart = np.zeros(3)
        planeOriginEnd = np.zeros(3)
        planeList[0].GetNthControlPointPosition(0,planeOriginStart)
        planeList[len(planeList)-1].GetNthControlPointPosition(0,planeOriginEnd)
        closestCurvePointStart = [0,0,0]
        closestCurvePointEnd = [0,0,0]
        closestCurvePointIndexStart = mandibularCurve.GetClosestPointPositionAlongCurveWorld(planeOriginStart,closestCurvePointStart)
        closestCurvePointIndexEnd = mandibularCurve.GetClosestPointPositionAlongCurveWorld(planeOriginEnd,closestCurvePointEnd)

        dynamicModelerNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLDynamicModelerNode")
        dynamicModelerNode.SetToolName("Plane cut")
        dynamicModelerNode.SetNodeReferenceID("PlaneCut.InputModel", fibulaModelNode.GetID())
        if closestCurvePointIndexStart > closestCurvePointIndexEnd:
          dynamicModelerNode.AddNodeReferenceID("PlaneCut.InputPlane", fibulaPlanesList[i].GetID())
          dynamicModelerNode.AddNodeReferenceID("PlaneCut.InputPlane", fibulaPlanesList[i+1].GetID())
        else:
          dynamicModelerNode.AddNodeReferenceID("PlaneCut.InputPlane", fibulaPlanesList[i+1].GetID())
          dynamicModelerNode.AddNodeReferenceID("PlaneCut.InputPlane", fibulaPlanesList[i].GetID()) 
        dynamicModelerNode.SetNodeReferenceID("PlaneCut.OutputNegativeModel", modelNode.GetID())
        dynamicModelerNode.SetAttribute("OperationType", "Difference")
        #slicer.modules.dynamicmodeler.logic().RunDynamicModelerTool(dynamicModelerNode)
        
        dynamicModelerNodeItemID = shNode.GetItemByDataNode(dynamicModelerNode)
        shNode.SetItemParent(dynamicModelerNodeItemID, planeCutsFolder)
        modelNodeItemID = shNode.GetItemByDataNode(modelNode)
        shNode.SetItemParent(modelNodeItemID, cutBonesFolder)
      
      
      modelNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLModelNode")
      modelNode.SetName("Resected mandible")
      slicer.mrmlScene.AddNode(modelNode)
      modelNode.CreateDefaultDisplayNodes()
      modelDisplayNode = modelNode.GetDisplayNode()
      modelDisplayNode.SetSliceIntersectionVisibility(True)

      mandibleViewNode = slicer.mrmlScene.GetSingletonNode("1", "vtkMRMLViewNode")
      modelDisplayNode.AddViewNodeID(mandibleViewNode.GetID())

      #Set color of the model
      aux = slicer.mrmlScene.GetNodeByID('vtkMRMLColorTableNodeFileMediumChartColors.txt')
      colorTable = aux.GetLookupTable()
      nColors = colorTable.GetNumberOfColors()
      ind = int((nColors-1) - (len(fibulaPlanesList)-1)/2 -1)
      colorwithalpha = colorTable.GetTableValue(ind)
      color = [colorwithalpha[0],colorwithalpha[1],colorwithalpha[2]]
      modelDisplayNode.SetColor(color)

      dynamicModelerNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLDynamicModelerNode")
      dynamicModelerNode.SetToolName("Plane cut")
      dynamicModelerNode.SetNodeReferenceID("PlaneCut.InputModel", mandibleModelNode.GetID())
      if closestCurvePointIndexStart > closestCurvePointIndexEnd:
        dynamicModelerNode.AddNodeReferenceID("PlaneCut.InputPlane", planeList[0].GetID())
        dynamicModelerNode.AddNodeReferenceID("PlaneCut.InputPlane", planeList[len(planeList)-1].GetID())
      else:
        dynamicModelerNode.AddNodeReferenceID("PlaneCut.InputPlane", planeList[len(planeList)-1].GetID())
        dynamicModelerNode.AddNodeReferenceID("PlaneCut.InputPlane", planeList[0].GetID()) 
      
      if fixCutGoesThroughTheMandibleTwiceChecked:
        #if planeToFixCutGoesThroughTheMandibleTwice == None:
        slicer.mrmlScene.RemoveNode(planeToFixCutGoesThroughTheMandibleTwice)
        mandibleCentroidX = parameterNode.GetParameter("mandibleCentroidX")
        mandibleCentroidY = parameterNode.GetParameter("mandibleCentroidY")
        mandibleCentroidZ = parameterNode.GetParameter("mandibleCentroidZ")
        mandibleCentroid = np.array([float(mandibleCentroidX),float(mandibleCentroidY),float(mandibleCentroidZ)])

        planeToFixCutGoesThroughTheMandibleTwice = slicer.mrmlScene.CreateNodeByClass("vtkMRMLMarkupsPlaneNode")
        planeToFixCutGoesThroughTheMandibleTwice.SetName("planeToFixCutGoesThroughTheMandibleTwice")
        slicer.mrmlScene.AddNode(planeToFixCutGoesThroughTheMandibleTwice)
        slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(planeToFixCutGoesThroughTheMandibleTwice)
        shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
        planeToFixCutGoesThroughTheMandibleTwiceItemID = shNode.GetItemByDataNode(planeToFixCutGoesThroughTheMandibleTwice)
        shNode.SetItemParent(planeToFixCutGoesThroughTheMandibleTwiceItemID, self.getParentFolderItemID())
        parameterNode.SetNodeReferenceID("planeToFixCutGoesThroughTheMandibleTwice",planeToFixCutGoesThroughTheMandibleTwice.GetID())

        displayNode = planeToFixCutGoesThroughTheMandibleTwice.GetDisplayNode()
        displayNode.SetVisibility(False)

        rightDirection = np.array([1,0,0])
        centerBetweenStartAndEndPlanes = (planeOriginStart + planeOriginEnd)/2
        planeToFixCutGoesThroughTheMandibleTwice.SetAxes([1,0,0],[0,1,0],[0,0,1])
        planeToFixCutGoesThroughTheMandibleTwice.SetOrigin(mandibleCentroid)
        if vtk.vtkMath.Dot(centerBetweenStartAndEndPlanes - mandibleCentroid, rightDirection) > 0:
          planeToFixCutGoesThroughTheMandibleTwice.SetNormal(rightDirection)
        else:
          planeToFixCutGoesThroughTheMandibleTwice.SetNormal(-rightDirection)

        dynamicModelerNode.AddNodeReferenceID("PlaneCut.InputPlane", planeToFixCutGoesThroughTheMandibleTwice.GetID())

      #else:
      #  slicer.mrmlScene.RemoveNode(planeToFixCutGoesThroughTheMandibleTwice)
      #  parameterNode.SetNodeReferenceID("planeToFixCutGoesThroughTheMandibleTwice",None)

      dynamicModelerNode.SetNodeReferenceID("PlaneCut.OutputPositiveModel", modelNode.GetID())
      dynamicModelerNode.SetAttribute("OperationType", "Difference")

      dynamicModelerNodeItemID = shNode.GetItemByDataNode(dynamicModelerNode)
      shNode.SetItemParent(dynamicModelerNodeItemID, planeCutsFolder)
      modelNodeItemID = shNode.GetItemByDataNode(modelNode)
      shNode.SetItemParent(modelNodeItemID, cutBonesFolder)

      if fixCutGoesThroughTheMandibleTwiceCheckBoxChanged:
        parameterNode.SetParameter('fixCutGoesThroughTheMandibleTwiceCheckBoxChanged','False')
    
    else:
      dynamicModelerNodesList = createListFromFolderID(planeCutsFolder)
      for i in range(len(dynamicModelerNodesList)):
        if i != (len(dynamicModelerNodesList) -1):
          dynamicModelerNodesList[i].SetNodeReferenceID("PlaneCut.InputModel", fibulaModelNode.GetID())
        else:
          dynamicModelerNodesList[i].SetNodeReferenceID("PlaneCut.InputModel", mandibleModelNode.GetID())

  def generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandible(self):
    parameterNode = self.getParameterNode()
    useNonDecimatedBoneModelsForPreviewChecked = parameterNode.GetParameter("useNonDecimatedBoneModelsForPreview") == "True"
    nonDecimatedMandibleModelNode = parameterNode.GetNodeReference("mandibleModelNode")
    decimatedMandibleModelNode = parameterNode.GetNodeReference("decimatedMandibleModelNode")
    planeList = createListFromFolderID(self.getMandiblePlanesFolderItemID())
    
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    fibulaPlanesFolder = shNode.GetItemByName("Fibula planes")

    if useNonDecimatedBoneModelsForPreviewChecked:
      mandibleModelNode = nonDecimatedMandibleModelNode
    else:
      mandibleModelNode = decimatedMandibleModelNode

    #delete all folders because there is only one plane and show mandible model
    if len(planeList) <= 1:
      shNode.RemoveItem(fibulaPlanesFolder)
      planeCutsFolder = shNode.GetItemByName("Plane Cuts")
      shNode.RemoveItem(planeCutsFolder)
      cutBonesFolder = shNode.GetItemByName("Cut Bones")
      shNode.RemoveItem(cutBonesFolder)
      transformedFibulaPiecesFolder = shNode.GetItemByName("Transformed Fibula Pieces")
      shNode.RemoveItem(transformedFibulaPiecesFolder)
      mandibleDisplayNode = mandibleModelNode.GetDisplayNode()
      mandibleDisplayNode.SetVisibility(True)
      return

    fibulaPlanesFolder = shNode.GetItemByName("Fibula planes")
    fibulaPlanesList = createListFromFolderID(fibulaPlanesFolder)

    #delete all the folders that are not updated
    if (len(fibulaPlanesList) != (2*len(planeList) - 2)) or not fibulaPlanesFolder:
      shNode.RemoveItem(fibulaPlanesFolder)
      planeCutsFolder = shNode.GetItemByName("Plane Cuts")
      shNode.RemoveItem(planeCutsFolder)
      cutBonesFolder = shNode.GetItemByName("Cut Bones")
      shNode.RemoveItem(cutBonesFolder)
      transformedFibulaPiecesFolder = shNode.GetItemByName("Transformed Fibula Pieces")
      shNode.RemoveItem(transformedFibulaPiecesFolder)
      fibulaPlanesFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Fibula planes")
      fibulaPlanesList = createListFromFolderID(fibulaPlanesFolder)
      #Create fibula planes and set their size
      self.createFibulaPlanesFromMandiblePlanesAndFibulaAxis(planeList,fibulaPlanesList)

    self.transformFibulaPlanes()

    self.createAndUpdateDynamicModelerNodes()
  
    self.updateFibulaPieces()

    self.tranformBonePiecesToMandible()

    self.setRedSliceForDisplayNodes()

  def setRedSliceForDisplayNodes(self):
    parameterNode = self.getParameterNode()
    scalarVolume = parameterNode.GetNodeReference("currentScalarVolume")
    fibulaCentroidX = parameterNode.GetParameter("fibulaCentroidX")
    fibulaCentroidY = parameterNode.GetParameter("fibulaCentroidY")
    fibulaCentroidZ = parameterNode.GetParameter("fibulaCentroidZ")
    mandibleCentroidX = parameterNode.GetParameter("mandibleCentroidX")
    mandibleCentroidY = parameterNode.GetParameter("mandibleCentroidY")
    mandibleCentroidZ = parameterNode.GetParameter("mandibleCentroidZ")
    
    fibulaCentroid = np.array([float(fibulaCentroidX),float(fibulaCentroidY),float(fibulaCentroidZ)])
    mandibleCentroid = np.array([float(mandibleCentroidX),float(mandibleCentroidY),float(mandibleCentroidZ)])

    bounds = [0,0,0,0,0,0]
    scalarVolume.GetBounds(bounds)
    bounds = np.array(bounds)
    centerOfScalarVolume = np.array([(bounds[0]+bounds[1])/2,(bounds[2]+bounds[3])/2,(bounds[4]+bounds[5])/2])
    
    shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    fibulaPlanesFolder = shNode.GetItemByName("Fibula planes")
    cutBonesFolder = shNode.GetItemByName("Cut Bones")
    transformedFibulaPiecesFolder = shNode.GetItemByName("Transformed Fibula Pieces")
    fibulaPlanesList = createListFromFolderID(fibulaPlanesFolder)
    cutBonesList = createListFromFolderID(cutBonesFolder)
    transformedFibulaPiecesList = createListFromFolderID(transformedFibulaPiecesFolder)
    redSliceNode = slicer.mrmlScene.GetSingletonNode("Red", "vtkMRMLSliceNode")

    if np.linalg.norm(fibulaCentroid-centerOfScalarVolume) < np.linalg.norm(mandibleCentroid-centerOfScalarVolume):
      #When fibulaScalarVolume:
      #addIterationList = fibulaPlanesList + cutBonesList[0:(len(cutBonesList)-1)]
      addIterationList = cutBonesList[0:(len(cutBonesList)-1)]
      
      for i in range(len(addIterationList)):
        displayNode = addIterationList[i].GetDisplayNode()
        displayNode.AddViewNodeID(redSliceNode.GetID())
    
    else:
      #When mandibleScalarVolume:
      addIterationList = [cutBonesList[len(cutBonesList)-1]] + transformedFibulaPiecesList
      
      for i in range(len(addIterationList)):
        displayNode = addIterationList[i].GetDisplayNode()
        displayNode.AddViewNodeID(redSliceNode.GetID())
      
  def getAxes1ToWorldRotationMatrix(self,axis1X,axis1Y,axis1Z):
    axes1ToWorldRotationMatrix = vtk.vtkMatrix4x4()
    axes1ToWorldRotationMatrix.DeepCopy((1, 0, 0, 0,
                                         0, 1, 0, 0,
                                         0, 0, 1, 0,
                                         0, 0, 0, 1))
    
    axes1ToWorldRotationMatrix.SetElement(0,0,axis1X[0])
    axes1ToWorldRotationMatrix.SetElement(0,1,axis1X[1])
    axes1ToWorldRotationMatrix.SetElement(0,2,axis1X[2])
    axes1ToWorldRotationMatrix.SetElement(1,0,axis1Y[0])
    axes1ToWorldRotationMatrix.SetElement(1,1,axis1Y[1])
    axes1ToWorldRotationMatrix.SetElement(1,2,axis1Y[2])
    axes1ToWorldRotationMatrix.SetElement(2,0,axis1Z[0])
    axes1ToWorldRotationMatrix.SetElement(2,1,axis1Z[1])
    axes1ToWorldRotationMatrix.SetElement(2,2,axis1Z[2])

    return axes1ToWorldRotationMatrix
  
  def getAxes1ToAxes2RotationMatrix(self,axes1ToWorldRotationMatrix,axes2ToWorldRotationMatrix):
    worldToAxes2RotationMatrix = vtk.vtkMatrix4x4()
    worldToAxes2RotationMatrix.DeepCopy(axes2ToWorldRotationMatrix)
    worldToAxes2RotationMatrix.Invert()
    
    axes1ToAxes2RotationMatrix = vtk.vtkMatrix4x4()
    vtk.vtkMatrix4x4.Multiply4x4(worldToAxes2RotationMatrix, axes1ToWorldRotationMatrix, axes1ToAxes2RotationMatrix)

    return axes1ToAxes2RotationMatrix

  def makeModels(self):
    layoutManager = slicer.app.layoutManager()
    layoutManager.setLayout(self.customLayoutId)

    slicer.util.resetSliceViews()

    parameterNode = self.getParameterNode()
    fibulaSegmentation = parameterNode.GetNodeReference("fibulaSegmentation")
    mandibularSegmentation = parameterNode.GetNodeReference("mandibularSegmentation")
    useNonDecimatedBoneModelsForPreviewChecked = parameterNode.GetParameter("useNonDecimatedBoneModelsForPreview") == "True"

    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    segmentationModelsFolder = shNode.GetItemByName("Segmentation Models")
    if segmentationModelsFolder:
      shNode.RemoveItem(segmentationModelsFolder)
      segmentationModelsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Segmentation Models")
    else:
      segmentationModelsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Segmentation Models")
    fibulaModelNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLModelNode")
    fibulaModelNode.SetName("fibula")
    mandibleModelNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLModelNode")
    mandibleModelNode.SetName("mandible")
    decimatedFibulaModelNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','decimatedFibula')
    decimatedMandibleModelNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','decimatedMandible')
    segmentations = [fibulaSegmentation,mandibularSegmentation]
    models = [fibulaModelNode,mandibleModelNode]
    decimatedModels = [decimatedFibulaModelNode,decimatedMandibleModelNode]
    for i in range(2):
      slicer.mrmlScene.AddNode(models[i])
      models[i].CreateDefaultDisplayNodes()
      decimatedModels[i].CreateDefaultDisplayNodes()

      seg = segmentations[i]
      seg.GetSegmentation().CreateRepresentation(slicer.vtkSegmentationConverter.GetSegmentationClosedSurfaceRepresentationName())
      segmentID = seg.GetSegmentation().GetNthSegmentID(0)
      segment = seg.GetSegmentation().GetSegment(segmentID)
      segDisplayNode = seg.GetDisplayNode()
      segDisplayNode.SetSegmentVisibility(segmentID,False)

      logic = slicer.modules.segmentations.logic()
      logic.ExportSegmentToRepresentationNode(segment, models[i])

      modelDisplayNode = models[i].GetDisplayNode()

      decimatedModelDisplayNode = decimatedModels[i].GetDisplayNode()
      decimatedModelDisplayNode.SetColor(models[i].GetDisplayNode().GetColor())

      if useNonDecimatedBoneModelsForPreviewChecked:
        modelDisplayNode.SetVisibility(True)
        decimatedModelDisplayNode.SetVisibility(False)
      else:
        modelDisplayNode.SetVisibility(False)
        decimatedModelDisplayNode.SetVisibility(True)

      param = {
              "inputModel": models[i],
              "outputModel": decimatedModels[i],
              "reductionFactor": 0.95,
              "method": "FastQuadric"
              }

      slicer.cli.runSync(slicer.modules.decimation, parameters=param)

      modelNodeItemID = shNode.GetItemByDataNode(models[i])
      shNode.SetItemParent(modelNodeItemID, segmentationModelsFolder)
      decimatedModelNodeItemID = shNode.GetItemByDataNode(decimatedModels[i])
      shNode.SetItemParent(decimatedModelNodeItemID, segmentationModelsFolder)

      if i==0:
        singletonTag = "2"
      else:
        singletonTag = "1"
      viewNode = slicer.mrmlScene.GetSingletonNode(singletonTag, "vtkMRMLViewNode")
      cameraNode = slicer.modules.cameras.logic().GetViewActiveCameraNode(viewNode)

      modelDisplayNode.AddViewNodeID(viewNode.GetID())
      decimatedModelDisplayNode.AddViewNodeID(viewNode.GetID())

      centroid = getCentroid(models[i])
      distanceMultiplier = 4
      if i==0: #distanceMultiplier selection is arbitrary
        viewUpDirection = [0,1,0]
      else:
        viewUpDirection = [0,0,1]
      cameraNode.SetPosition(distanceMultiplier*centroid)
      cameraNode.SetFocalPoint(centroid)
      cameraNode.SetViewUp(viewUpDirection)

      if i==0:
        parameterNode.SetParameter("fibulaCentroidX",str(centroid[0]))
        parameterNode.SetParameter("fibulaCentroidY",str(centroid[1]))
        parameterNode.SetParameter("fibulaCentroidZ",str(centroid[2]))
      else:
        parameterNode.SetParameter("mandibleCentroidX",str(centroid[0]))
        parameterNode.SetParameter("mandibleCentroidY",str(centroid[1]))
        parameterNode.SetParameter("mandibleCentroidZ",str(centroid[2]))

    parameterNode.SetNodeReferenceID("fibulaModelNode", fibulaModelNode.GetID())
    parameterNode.SetNodeReferenceID("mandibleModelNode", mandibleModelNode.GetID())
    parameterNode.SetNodeReferenceID("decimatedFibulaModelNode", decimatedFibulaModelNode.GetID())
    parameterNode.SetNodeReferenceID("decimatedMandibleModelNode", decimatedMandibleModelNode.GetID())

  def updateFibulaPieces(self):
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    planeCutsList = createListFromFolderID(shNode.GetItemByName("Plane Cuts"))
    for i in range(len(planeCutsList)):
      slicer.modules.dynamicmodeler.logic().RunDynamicModelerTool(planeCutsList[i])

  def tranformBonePiecesToMandible(self):
    parameterNode = self.getParameterNode()
    fibulaLine = parameterNode.GetNodeReference("fibulaLine")
    planeList = createListFromFolderID(self.getMandiblePlanesFolderItemID())

    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    bonePiecesTransformFolder = shNode.GetItemByName("Bone Pieces Transforms")
    shNode.RemoveItem(bonePiecesTransformFolder)
    bonePiecesTransformFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Bone Pieces Transforms")
    transformedFibulaPiecesFolder = shNode.GetItemByName("Transformed Fibula Pieces")
    shNode.RemoveItem(transformedFibulaPiecesFolder)
    transformedFibulaPiecesFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Transformed Fibula Pieces")

    lineStartPos = np.zeros(3)
    lineEndPos = np.zeros(3)
    fibulaLine.GetNthControlPointPositionWorld(0, lineStartPos)
    fibulaLine.GetNthControlPointPositionWorld(1, lineEndPos)
    fibulaOrigin = lineStartPos
    fibulaZ = (lineEndPos-lineStartPos)/np.linalg.norm(lineEndPos-lineStartPos)

    cutBonesList = createListFromFolderID(shNode.GetItemByName("Cut Bones"))
    for i in range(len(cutBonesList)-1):

      or0 = np.zeros(3)
      planeList[i].GetOrigin(or0)
      or1 = np.zeros(3)
      planeList[i+1].GetOrigin(or1)
      origin = (or0+or1)/2

      inverseRotationMatrix = vtk.vtkMatrix4x4()
      inverseRotationMatrix.DeepCopy(self.mandibleAxisToFibulaRotationMatrixesList[i])
      inverseRotationMatrix.Invert()

      fibulaPieceToMandibleAxisTransformNode = slicer.vtkMRMLLinearTransformNode()
      fibulaPieceToMandibleAxisTransformNode.SetName("Fibula Segment {0} Transform".format(i))
      slicer.mrmlScene.AddNode(fibulaPieceToMandibleAxisTransformNode)

      oldOrigin = (self.fibulaPlanesPositionA[i] + self.fibulaPlanesPositionB[i])/2

      fibulaPieceToMandibleAxisTransform = vtk.vtkTransform()
      fibulaPieceToMandibleAxisTransform.PostMultiply()
      fibulaPieceToMandibleAxisTransform.Translate(-oldOrigin[0],-oldOrigin[1],-oldOrigin[2])
      fibulaPieceToMandibleAxisTransform.Concatenate(inverseRotationMatrix)
      fibulaPieceToMandibleAxisTransform.Translate(origin)

      fibulaPieceToMandibleAxisTransformNode.SetMatrixTransformToParent(fibulaPieceToMandibleAxisTransform.GetMatrix())
      fibulaPieceToMandibleAxisTransformNode.UpdateScene(slicer.mrmlScene)

      transformedFibulaPiece = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode',slicer.mrmlScene.GetUniqueNameByString('Transformed ' + cutBonesList[i].GetName()))
      transformedFibulaPiece.CreateDefaultDisplayNodes()
      transformedFibulaPiece.CopyContent(cutBonesList[i])
      transformedFibulaPieceDisplayNode = transformedFibulaPiece.GetDisplayNode()
      transformedFibulaPieceDisplayNode.SetColor(cutBonesList[i].GetDisplayNode().GetColor())
      transformedFibulaPieceDisplayNode.SetSliceIntersectionVisibility(True)

      mandibleViewNode = slicer.mrmlScene.GetSingletonNode("1", "vtkMRMLViewNode")
      transformedFibulaPieceDisplayNode.AddViewNodeID(mandibleViewNode.GetID())

      transformedFibulaPiece.SetAndObserveTransformNodeID(fibulaPieceToMandibleAxisTransformNode.GetID())
      transformedFibulaPiece.HardenTransform()

      transformedFibulaPieceItemID = shNode.GetItemByDataNode(transformedFibulaPiece)
      shNode.SetItemParent(transformedFibulaPieceItemID, transformedFibulaPiecesFolder)

      fibulaPieceToMandibleAxisTransformNodeItemID = shNode.GetItemByDataNode(fibulaPieceToMandibleAxisTransformNode)
      shNode.SetItemParent(fibulaPieceToMandibleAxisTransformNodeItemID, bonePiecesTransformFolder)

  def mandiblePlanesPositioningForMaximumBoneContact(self):
    parameterNode = self.getParameterNode()
    mandibularCurve = parameterNode.GetNodeReference("mandibleCurve")
    planeList = createListFromFolderID(self.getMandiblePlanesFolderItemID())

    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    mandiblePlaneTransformsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Mandible Planes Transforms")
    
    for i in range(0,len(planeList)-2):
      or0 = np.zeros(3)
      or1 = np.zeros(3)
      or2 = np.zeros(3)
      planeList[i].GetOrigin(or0)
      planeList[i+1].GetOrigin(or1)
      planeList[i+2].GetOrigin(or2)
      lineDirectionVector0 = (or1-or0)/np.linalg.norm(or1-or0)
      lineDirectionVector1 = (or2-or1)/np.linalg.norm(or2-or1)

      #Get X, Y, Z components of mandiblePlane1
      mandiblePlane1matrix = vtk.vtkMatrix4x4()
      if int(slicer.app.revision) > int(SLICER_CHANGE_OF_API_REVISION):
        planeList[i+1].GetObjectToWorldMatrix(mandiblePlane1matrix)
      else:
        planeList[i+1].GetPlaneToWorldMatrix(mandiblePlane1matrix)
      mandiblePlane1X = np.array([mandiblePlane1matrix.GetElement(0,0),mandiblePlane1matrix.GetElement(1,0),mandiblePlane1matrix.GetElement(2,0)])
      mandiblePlane1Y = np.array([mandiblePlane1matrix.GetElement(0,1),mandiblePlane1matrix.GetElement(1,1),mandiblePlane1matrix.GetElement(2,1)])
      mandiblePlane1Z = np.array([mandiblePlane1matrix.GetElement(0,2),mandiblePlane1matrix.GetElement(1,2),mandiblePlane1matrix.GetElement(2,2)])

      middleAxisZ = (lineDirectionVector0+lineDirectionVector1)/np.linalg.norm(lineDirectionVector0+lineDirectionVector1)
      middleAxisX = [0,0,0]
      middleAxisY = [0,0,0]
      vtk.vtkMath.Cross(mandiblePlane1Y, middleAxisZ, middleAxisX)
      middleAxisX = middleAxisX/np.linalg.norm(middleAxisX)
      vtk.vtkMath.Cross(middleAxisZ, middleAxisX, middleAxisY)
      middleAxisY = middleAxisY/np.linalg.norm(middleAxisY)

      mandibleAxisToWorldRotationMatrix = self.getAxes1ToWorldRotationMatrix(mandiblePlane1X, mandiblePlane1Y, mandiblePlane1Z)
      middleAxisToWorldRotationMatrix = self.getAxes1ToWorldRotationMatrix(middleAxisX, middleAxisY, middleAxisZ)

      mandiblePlane0ToMiddleAxisRotationMatrix = self.getAxes1ToAxes2RotationMatrix(mandibleAxisToWorldRotationMatrix, middleAxisToWorldRotationMatrix)

      transformNode = slicer.vtkMRMLLinearTransformNode()
      transformNode.SetName("temp%d" % (i+1))
      slicer.mrmlScene.AddNode(transformNode)

      finalTransform = vtk.vtkTransform()
      finalTransform.PostMultiply()
      finalTransform.Translate(-or1[0], -or1[1], -or1[2])
      finalTransform.Concatenate(mandiblePlane0ToMiddleAxisRotationMatrix)
      finalTransform.Translate(or1)

      transformNode.SetMatrixTransformToParent(finalTransform.GetMatrix())

      transformNode.UpdateScene(slicer.mrmlScene)

      planeList[i+1].SetAndObserveTransformNodeID(transformNode.GetID())
      planeList[i+1].HardenTransform()
      
      transformNodeItemID = shNode.GetItemByDataNode(transformNode)
      shNode.SetItemParent(transformNodeItemID, mandiblePlaneTransformsFolder)
    
    shNode.RemoveItem(mandiblePlaneTransformsFolder)
  
  def setupMandiblePlaneStraightOverMandibleCurve(self,planeNode,temporalOrigin, mandibleCurve, planeNodeObserver):
    closestCurvePoint = [0,0,0]
    closestCurvePointIndex = mandibleCurve.GetClosestPointPositionAlongCurveWorld(temporalOrigin,closestCurvePoint)
    matrix = vtk.vtkMatrix4x4()
    mandibleCurve.GetCurvePointToWorldTransformAtPointIndex(closestCurvePointIndex,matrix)
    mandiblePlaneStraightOrigin = np.array([matrix.GetElement(0,3),matrix.GetElement(1,3),matrix.GetElement(2,3)])
    mandiblePlaneStraightZ = np.array([matrix.GetElement(0,2),matrix.GetElement(1,2),matrix.GetElement(2,2)])
    mandiblePlaneStraightY = [0,0,0]
    posterior = [0,-1,0]
    vtk.vtkMath.Cross(mandiblePlaneStraightZ, posterior, mandiblePlaneStraightY)
    mandiblePlaneStraightY = mandiblePlaneStraightY/np.linalg.norm(mandiblePlaneStraightY)
    mandiblePlaneStraightX = [0,0,0]
    vtk.vtkMath.Cross(mandiblePlaneStraightY, mandiblePlaneStraightZ, mandiblePlaneStraightX)
    mandiblePlaneStraightX = mandiblePlaneStraightX/np.linalg.norm(mandiblePlaneStraightX)
    dx = 25#Numbers choosen so the planes are visible enough
    dy = 25
    planeNode.RemoveObserver(planeNodeObserver)
    planeNode.SetNormal(mandiblePlaneStraightZ)
    planeNode.SetNthControlPointPositionFromArray(0,mandiblePlaneStraightOrigin)
    planeNode.SetNthControlPointPositionFromArray(1,mandiblePlaneStraightOrigin + mandiblePlaneStraightX*dx)
    planeNode.SetNthControlPointPositionFromArray(2,mandiblePlaneStraightOrigin + mandiblePlaneStraightY*dy)

  def createFibulaAxisFromFibulaLineAndNotLeftChecked(self,fibulaLine,notLeftFibulaChecked):
    lineStartPos = np.zeros(3)
    lineEndPos = np.zeros(3)
    fibulaLine.GetNthControlPointPositionWorld(0, lineStartPos)
    fibulaLine.GetNthControlPointPositionWorld(1, lineEndPos)
    fibulaOrigin = lineStartPos
    fibulaZLineNorm = np.linalg.norm(lineEndPos-lineStartPos)
    fibulaZ = (lineEndPos-lineStartPos)/fibulaZLineNorm
    fibulaX = [0,0,0]
    fibulaY = [0,0,0]
    anteriorDirection = [0,1,0]
    posteriorDirection = [0,-1,0]
    if notLeftFibulaChecked:
      vtk.vtkMath.Cross(fibulaZ, anteriorDirection, fibulaX)
      fibulaX = fibulaX/np.linalg.norm(fibulaX)
    else:
      vtk.vtkMath.Cross(fibulaZ, posteriorDirection, fibulaX)
      fibulaX = fibulaX/np.linalg.norm(fibulaX)
    vtk.vtkMath.Cross(fibulaZ, fibulaX, fibulaY)
    fibulaY = fibulaY/np.linalg.norm(fibulaY)

    return fibulaX, fibulaY, fibulaZ, fibulaOrigin

  def createFibulaAxisFromFibulaLineAndNotLeftChecked_2(self,lineStartPos,lineEndPos,notLeftFibulaChecked):
    fibulaOrigin = lineStartPos
    fibulaZLineNorm = np.linalg.norm(lineEndPos-lineStartPos)
    fibulaZ = (lineEndPos-lineStartPos)/fibulaZLineNorm
    fibulaX = [0,0,0]
    fibulaY = [0,0,0]
    anteriorDirection = [0,1,0]
    posteriorDirection = [0,-1,0]
    if notLeftFibulaChecked:
      vtk.vtkMath.Cross(fibulaZ, anteriorDirection, fibulaX)
      fibulaX = fibulaX/np.linalg.norm(fibulaX)
    else:
      vtk.vtkMath.Cross(fibulaZ, posteriorDirection, fibulaX)
      fibulaX = fibulaX/np.linalg.norm(fibulaX)
    vtk.vtkMath.Cross(fibulaZ, fibulaX, fibulaY)
    fibulaY = fibulaY/np.linalg.norm(fibulaY)

    return fibulaX, fibulaY, fibulaZ, fibulaOrigin
  
  def createMiterBoxesFromFibulaPlanes(self):
    parameterNode = self.getParameterNode()
    fibulaLine = parameterNode.GetNodeReference("fibulaLine")
    miterBoxDirectionLine = parameterNode.GetNodeReference("miterBoxDirectionLine")
    miterBoxSlotWidth = float(parameterNode.GetParameter("miterBoxSlotWidth"))
    miterBoxSlotLength = float(parameterNode.GetParameter("miterBoxSlotLength"))
    miterBoxSlotHeight = float(parameterNode.GetParameter("miterBoxSlotHeight"))
    miterBoxSlotWall = float(parameterNode.GetParameter("miterBoxSlotWall"))
    clearanceFitPrintingTolerance = float(parameterNode.GetParameter("clearanceFitPrintingTolerance"))
    biggerMiterBoxDistanceToFibula = float(parameterNode.GetParameter("biggerMiterBoxDistanceToFibula"))
    securityMarginOfFibulaPieces = float(parameterNode.GetParameter("securityMarginOfFibulaPieces"))
    notLeftFibulaChecked = parameterNode.GetParameter("notLeftFibula") == "True"
    checkSecurityMarginOnMiterBoxCreationChecked = parameterNode.GetParameter("checkSecurityMarginOnMiterBoxCreation") == "True"
    useMoreExactVersionOfPositioningAlgorithmChecked = parameterNode.GetParameter("useMoreExactVersionOfPositioningAlgorithm") == "True"
    fibulaModelNode = parameterNode.GetNodeReference("fibulaModelNode")

    scalarVolume = parameterNode.GetNodeReference("currentScalarVolume")
    fibulaCentroidX = parameterNode.GetParameter("fibulaCentroidX")
    fibulaCentroidY = parameterNode.GetParameter("fibulaCentroidY")
    fibulaCentroidZ = parameterNode.GetParameter("fibulaCentroidZ")
    mandibleCentroidX = parameterNode.GetParameter("mandibleCentroidX")
    mandibleCentroidY = parameterNode.GetParameter("mandibleCentroidY")
    mandibleCentroidZ = parameterNode.GetParameter("mandibleCentroidZ")
    
    fibulaCentroid = np.array([float(fibulaCentroidX),float(fibulaCentroidY),float(fibulaCentroidZ)])
    mandibleCentroid = np.array([float(mandibleCentroidX),float(mandibleCentroidY),float(mandibleCentroidZ)])

    bounds = [0,0,0,0,0,0]
    scalarVolume.GetBounds(bounds)
    bounds = np.array(bounds)
    centerOfScalarVolume = np.array([(bounds[0]+bounds[1])/2,(bounds[2]+bounds[3])/2,(bounds[4]+bounds[5])/2])

    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    fibulaPlanesFolder = shNode.GetItemByName("Fibula planes")
    fibulaPlanesList = createListFromFolderID(fibulaPlanesFolder)
    miterBoxesModelsFolder = shNode.GetItemByName("miterBoxes Models")
    shNode.RemoveItem(miterBoxesModelsFolder)
    biggerMiterBoxesModelsFolder = shNode.GetItemByName("biggerMiterBoxes Models")
    shNode.RemoveItem(biggerMiterBoxesModelsFolder)

    if checkSecurityMarginOnMiterBoxCreationChecked:
      cutBonesList = createListFromFolderID(shNode.GetItemByName("Cut Bones"))
      duplicateFibulaBonePiecesModelsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Duplicate Fibula Bone Pieces")
      duplicateFibulaBonePiecesTransformsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Duplicate Fibula Bone Pieces Transforms")
      
      for i in range(0,len(cutBonesList)-1):
        duplicateFibulaPiece = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Duplicate ' + cutBonesList[i].GetName())
        duplicateFibulaPiece.CreateDefaultDisplayNodes()
        duplicateFibulaPiece.CopyContent(cutBonesList[i])

        duplicateFibulaPieceItemID = shNode.GetItemByDataNode(duplicateFibulaPiece)
        shNode.SetItemParent(duplicateFibulaPieceItemID, duplicateFibulaBonePiecesModelsFolder)

      duplicateFibulaBonePiecesList = createListFromFolderID(duplicateFibulaBonePiecesModelsFolder)

      for i in range(1,len(duplicateFibulaBonePiecesList)):
        lineStartPos = np.zeros(3)
        lineEndPos = np.zeros(3)
        fibulaPlanesList[i*2].GetOrigin(lineStartPos)
        fibulaPlanesList[i*2 +1].GetOrigin(lineEndPos)
        #Create fibula axis:
        fibulaZ = (lineEndPos - lineStartPos)/np.linalg.norm(lineEndPos - lineStartPos)

        duplicateFibulaPieceTransformNode = slicer.vtkMRMLLinearTransformNode()
        duplicateFibulaPieceTransformNode.SetName("Duplicate Fibula Piece Transform {0}".format(i))
        slicer.mrmlScene.AddNode(duplicateFibulaPieceTransformNode)

        duplicateFibulaPieceTransform = vtk.vtkTransform()
        duplicateFibulaPieceTransform.PostMultiply()
        duplicateFibulaPieceTransform.Translate(-i*(securityMarginOfFibulaPieces + 1e-2)*fibulaZ)

        duplicateFibulaPieceTransformNode.SetMatrixTransformToParent(duplicateFibulaPieceTransform.GetMatrix())

        duplicateFibulaBonePiecesList[i].SetAndObserveTransformNodeID(duplicateFibulaPieceTransformNode.GetID())
        duplicateFibulaBonePiecesList[i].HardenTransform()

        duplicateFibulaPieceTransformNodeItemID = shNode.GetItemByDataNode(duplicateFibulaPieceTransformNode)
        shNode.SetItemParent(duplicateFibulaPieceTransformNodeItemID, duplicateFibulaBonePiecesTransformsFolder)

      collisionDetected = False
      for i in range(0,len(duplicateFibulaBonePiecesList) -1):
        if int(slicer.app.revision) > int(SLICER_CHANGE_OF_API_REVISION):
          collisionDetection = vtk.vtkCollisionDetectionFilter()
        else:
          import vtkSlicerRtCommonPython
          collisionDetection = vtkSlicerRtCommonPython.vtkCollisionDetectionFilter()
        collisionDetection.SetInputData(0, duplicateFibulaBonePiecesList[i].GetPolyData())
        collisionDetection.SetInputData(1, duplicateFibulaBonePiecesList[i+1].GetPolyData())
        matrix1 = vtk.vtkMatrix4x4()
        collisionDetection.SetMatrix(0, matrix1)
        collisionDetection.SetMatrix(1, matrix1)
        collisionDetection.SetBoxTolerance(0.0)
        collisionDetection.SetCellTolerance(0.0)
        collisionDetection.SetNumberOfCellsPerNode(2)
        collisionDetection.Update()
        
        if collisionDetection.GetNumberOfContacts() > 0:
          collisionDetected = True
          break
      
      shNode.RemoveItem(duplicateFibulaBonePiecesTransformsFolder)
      shNode.RemoveItem(duplicateFibulaBonePiecesModelsFolder)
      if collisionDetected:
        slicer.util.errorDisplay(f"Planned fibula segments could overlap each other (the distance in between them do not satisfy the security margin of {securityMarginOfFibulaPieces}mm). " +
            "You can fix this by increasing 'intersection distance multiplier' or 'between space' and pressing the update button")
        return


    miterBoxesModelsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"miterBoxes Models")
    biggerMiterBoxesModelsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"biggerMiterBoxes Models")
    miterBoxesTransformsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"miterBoxes Transforms")
    intersectionsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Intersections")
    pointsIntersectionsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Points Intersections")

    if not useMoreExactVersionOfPositioningAlgorithmChecked:
      #Create fibula axis:
      fibulaX, fibulaY, fibulaZ, fibulaOrigin = self.createFibulaAxisFromFibulaLineAndNotLeftChecked(fibulaLine,notLeftFibulaChecked) 

    fibulaViewNode = slicer.mrmlScene.GetSingletonNode("2", "vtkMRMLViewNode")

    for i in range(len(fibulaPlanesList)):
      if useMoreExactVersionOfPositioningAlgorithmChecked:
        lineStartPos = np.zeros(3)
        lineEndPos = np.zeros(3)
        fibulaPlanesList[(i//2)*2].GetOrigin(lineStartPos)
        fibulaPlanesList[(i//2)*2 +1].GetOrigin(lineEndPos)
        #Create fibula axis:
        fibulaX, fibulaY, fibulaZ, fibulaOrigin = self.createFibulaAxisFromFibulaLineAndNotLeftChecked_2(lineStartPos,lineEndPos,notLeftFibulaChecked)

      #miterBoxModel: the numbers are selected arbitrarily to make a box with the correct size then they'll be GUI set
      if i%2 == 0:
        miterBoxName = "miterBox%d_A" % (i//2)
        biggerMiterBoxName = "biggerMiterBox%d_A" % (i//2)
      else:
        miterBoxName = "miterBox%d_B" % (i//2)
        biggerMiterBoxName = "biggerMiterBox%d_B" % (i//2)
      miterBoxWidth = miterBoxSlotWidth+2*clearanceFitPrintingTolerance
      miterBoxLength = miterBoxSlotLength
      miterBoxHeight = 70
      miterBoxModel = createBox(miterBoxLength,miterBoxHeight,miterBoxWidth,miterBoxName)

      miterBoxDisplayNode = miterBoxModel.GetDisplayNode()
      miterBoxDisplayNode.AddViewNodeID(fibulaViewNode.GetID())

      miterBoxModelItemID = shNode.GetItemByDataNode(miterBoxModel)
      shNode.SetItemParent(miterBoxModelItemID, miterBoxesModelsFolder)

      biggerMiterBoxWidth = miterBoxSlotWidth+2*clearanceFitPrintingTolerance+2*miterBoxSlotWall
      biggerMiterBoxLength = miterBoxSlotLength+2*miterBoxSlotWall
      biggerMiterBoxHeight = miterBoxSlotHeight
      biggerMiterBoxModel = createBox(biggerMiterBoxLength,biggerMiterBoxHeight,biggerMiterBoxWidth,biggerMiterBoxName)
      biggerMiterBoxDisplayNode = biggerMiterBoxModel.GetDisplayNode()

      biggerMiterBoxDisplayNode.AddViewNodeID(fibulaViewNode.GetID())
      biggerMiterBoxDisplayNode.SetSliceIntersectionVisibility(True)
      if np.linalg.norm(fibulaCentroid-centerOfScalarVolume) < np.linalg.norm(mandibleCentroid-centerOfScalarVolume):
        redSliceNode = slicer.mrmlScene.GetSingletonNode("Red", "vtkMRMLSliceNode")
        biggerMiterBoxDisplayNode.AddViewNodeID(redSliceNode.GetID())

      biggerMiterBoxModelItemID = shNode.GetItemByDataNode(biggerMiterBoxModel)
      shNode.SetItemParent(biggerMiterBoxModelItemID, biggerMiterBoxesModelsFolder)

      fibulaPlaneMatrix = vtk.vtkMatrix4x4()
      if int(slicer.app.revision) > int(SLICER_CHANGE_OF_API_REVISION):
        fibulaPlanesList[i].GetObjectToWorldMatrix(fibulaPlaneMatrix)
      else:
        fibulaPlanesList[i].GetPlaneToWorldMatrix(fibulaPlaneMatrix)
      fibulaPlaneZ = np.array([fibulaPlaneMatrix.GetElement(0,2),fibulaPlaneMatrix.GetElement(1,2),fibulaPlaneMatrix.GetElement(2,2)])
      fibulaPlaneOrigin = np.array([fibulaPlaneMatrix.GetElement(0,3),fibulaPlaneMatrix.GetElement(1,3),fibulaPlaneMatrix.GetElement(2,3)])

      lineStartPos = np.zeros(3)
      lineEndPos = np.zeros(3)
      miterBoxDirectionLine.GetNthControlPointPositionWorld(0, lineStartPos)
      miterBoxDirectionLine.GetNthControlPointPositionWorld(1, lineEndPos)
      miterBoxDirection = (lineEndPos-lineStartPos)/np.linalg.norm(lineEndPos-lineStartPos)

      normalToMiterBoxDirectionAndFibulaZ = [0,0,0]
      vtk.vtkMath.Cross(miterBoxDirection, fibulaZ, normalToMiterBoxDirectionAndFibulaZ)
      normalToMiterBoxDirectionAndFibulaZ = normalToMiterBoxDirectionAndFibulaZ/np.linalg.norm(normalToMiterBoxDirectionAndFibulaZ)

      if i%2 == 0:
        intersectionModel = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Intersection%d_A' % (i//2))
      else:
        intersectionModel = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Intersection%d_B' % (i//2))
      intersectionModel.CreateDefaultDisplayNodes()
      getIntersectionBetweenModelAnd1Plane(fibulaModelNode,fibulaPlanesList[i],intersectionModel)
      intersectionModelCentroid = getCentroid(intersectionModel)
      if i%2 == 0:
        pointsIntersectionModel = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Points Intersection%d_A' % (i//2))
      else:
        pointsIntersectionModel = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Points Intersection%d_B' % (i//2))
      pointsIntersectionModel.CreateDefaultDisplayNodes()
      getIntersectionBetweenModelAnd1PlaneWithNormalAndOrigin_2(intersectionModel,normalToMiterBoxDirectionAndFibulaZ,intersectionModelCentroid,pointsIntersectionModel)
      pointOfIntersection = getPointOfATwoPointsModelThatMakesLineDirectionSimilarToVector(pointsIntersectionModel,miterBoxDirection)
      intersectionModelItemID = shNode.GetItemByDataNode(intersectionModel)
      shNode.SetItemParent(intersectionModelItemID, intersectionsFolder)
      pointsIntersectionModelItemID = shNode.GetItemByDataNode(pointsIntersectionModel)
      shNode.SetItemParent(pointsIntersectionModelItemID, pointsIntersectionsFolder)

      miterBoxAxisX = [0,0,0]
      miterBoxAxisY =  [0,0,0]
      miterBoxAxisZ = fibulaPlaneZ
      if vtk.vtkMath.Dot(fibulaZ, miterBoxAxisZ) < 0:
        miterBoxAxisZ = -miterBoxAxisZ
      vtk.vtkMath.Cross(miterBoxDirection, miterBoxAxisZ, miterBoxAxisX)
      miterBoxAxisX = miterBoxAxisX/np.linalg.norm(miterBoxAxisX)
      vtk.vtkMath.Cross(miterBoxAxisZ, miterBoxAxisX, miterBoxAxisY)
      miterBoxAxisY = miterBoxAxisY/np.linalg.norm(miterBoxAxisY)

      miterBoxAxisToWorldRotationMatrix = self.getAxes1ToWorldRotationMatrix(miterBoxAxisX, miterBoxAxisY, miterBoxAxisZ)
      WorldToWorldRotationMatrix = self.getAxes1ToWorldRotationMatrix([1,0,0], [0,1,0], [0,0,1])

      WorldToMiterBoxAxisRotationMatrix = self.getAxes1ToAxes2RotationMatrix(WorldToWorldRotationMatrix, miterBoxAxisToWorldRotationMatrix)

      #Calculations for deltaMiterBoxAxisY
      sinOfMiterBoxAxisZAndFibulaZVector = [0,0,0]
      vtk.vtkMath.Cross(miterBoxAxisZ, fibulaZ, sinOfMiterBoxAxisZAndFibulaZVector)
      sinOfMiterBoxAxisZAndFibulaZ = np.linalg.norm(sinOfMiterBoxAxisZAndFibulaZVector)
      rotatedMiterBoxAxisY = [0,0,0]
      vtk.vtkMath.Cross(fibulaZ, miterBoxAxisX, rotatedMiterBoxAxisY)
      rotatedMiterBoxAxisY = rotatedMiterBoxAxisY/np.linalg.norm(rotatedMiterBoxAxisY)
      cosOfRotatedMiterBoxAxisYAndMiterBoxAxisY = vtk.vtkMath.Dot(rotatedMiterBoxAxisY, miterBoxAxisY)
      deltaMiterBoxAxisY = biggerMiterBoxWidth/2*sinOfMiterBoxAxisZAndFibulaZ/cosOfRotatedMiterBoxAxisYAndMiterBoxAxisY

      transformNode = slicer.vtkMRMLLinearTransformNode()
      transformNode.SetName("temp%d" % i)
      slicer.mrmlScene.AddNode(transformNode)

      finalTransform = vtk.vtkTransform()
      finalTransform.PostMultiply()
      finalTransform.Concatenate(WorldToMiterBoxAxisRotationMatrix)
      if i%2 == 0:
        miterBoxAxisXTranslation = 0
        miterBoxAxisYTranslation = biggerMiterBoxHeight/2+deltaMiterBoxAxisY+biggerMiterBoxDistanceToFibula/cosOfRotatedMiterBoxAxisYAndMiterBoxAxisY
        miterBoxAxisZTranslation = -miterBoxSlotWidth/2
      else:
        miterBoxAxisXTranslation = 0
        miterBoxAxisYTranslation = biggerMiterBoxHeight/2+deltaMiterBoxAxisY+biggerMiterBoxDistanceToFibula/cosOfRotatedMiterBoxAxisYAndMiterBoxAxisY
        miterBoxAxisZTranslation = miterBoxSlotWidth/2
      finalTransform.Translate(pointOfIntersection + miterBoxAxisX*miterBoxAxisXTranslation + miterBoxAxisY*miterBoxAxisYTranslation + miterBoxAxisZ*miterBoxAxisZTranslation)
      transformNode.SetMatrixTransformToParent(finalTransform.GetMatrix())

      transformNode.UpdateScene(slicer.mrmlScene)

      miterBoxModel.SetAndObserveTransformNodeID(transformNode.GetID())
      miterBoxModel.HardenTransform()
      biggerMiterBoxModel.SetAndObserveTransformNodeID(transformNode.GetID())
      biggerMiterBoxModel.HardenTransform()
      
      transformNodeItemID = shNode.GetItemByDataNode(transformNode)
      shNode.SetItemParent(transformNodeItemID, miterBoxesTransformsFolder)
    
    shNode.RemoveItem(miterBoxesTransformsFolder)
    shNode.RemoveItem(intersectionsFolder)
    shNode.RemoveItem(pointsIntersectionsFolder)

  def createFibulaCylindersFiducialList(self):
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    fibulaCylindersFiducialsListsFolder = shNode.GetItemByName("Fibula Cylinders Fiducials Lists")
    if not fibulaCylindersFiducialsListsFolder:
      fibulaCylindersFiducialsListsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Fibula Cylinders Fiducials Lists")
    
    fibulaFiducialListNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLMarkupsFiducialNode")
    fibulaFiducialListNode.SetName("temp")
    slicer.mrmlScene.AddNode(fibulaFiducialListNode)
    slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(fibulaFiducialListNode)
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    fibulaFiducialListNodeItemID = shNode.GetItemByDataNode(fibulaFiducialListNode)
    shNode.SetItemParent(fibulaFiducialListNodeItemID, fibulaCylindersFiducialsListsFolder)
    fibulaFiducialListNode.SetName(slicer.mrmlScene.GetUniqueNameByString("fibulaCylindersFiducialsList"))

    #setup placement
    slicer.modules.markups.logic().SetActiveListID(fibulaFiducialListNode)
    interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
    interactionNode.SwitchToPersistentPlaceMode()

  def createCylindersFromFiducialListAndFibulaSurgicalGuideBase(self):
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    fibulaCylindersModelsFolder = shNode.GetItemByName("Fibula Cylinders Models")
    shNode.RemoveItem(fibulaCylindersModelsFolder)
    fibulaCylindersModelsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Fibula Cylinders Models")
    cylindersTransformsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Cylinders Transforms")
    
    parameterNode = self.getParameterNode()
    fibulaFiducialList = parameterNode.GetNodeReference("fibulaFiducialList")
    fibulaSurgicalGuideBaseModel = parameterNode.GetNodeReference("fibulaSurgicalGuideBaseModel")
    fibulaScrewHoleCylinderRadius = float(parameterNode.GetParameter("fibulaScrewHoleCylinderRadius"))

    normalsOfSurgicalGuideBaseModel = slicer.util.arrayFromModelPointData(fibulaSurgicalGuideBaseModel, 'Normals')
    
    surgicalGuideBaseMesh = fibulaSurgicalGuideBaseModel.GetMesh()

    for i in range(fibulaFiducialList.GetNumberOfFiducials()):
      pos = [0,0,0]
      fibulaFiducialList.GetNthFiducialPosition(i,pos)

      pointID = surgicalGuideBaseMesh.FindPoint(pos)

      normalAtPointID = normalsOfSurgicalGuideBaseModel[pointID]

      transformedCylinderAxisX = [0,0,0]
      transformedCylinderAxisY = [0,0,0]
      transformedCylinderAxisZ = normalAtPointID
      vtk.vtkMath.Perpendiculars(transformedCylinderAxisZ,transformedCylinderAxisX,transformedCylinderAxisY,0)

      cylinderModel = createCylinder(fibulaScrewHoleCylinderRadius, "cylinder%d" % i)
      cylinderModelItemID = shNode.GetItemByDataNode(cylinderModel)
      shNode.SetItemParent(cylinderModelItemID, fibulaCylindersModelsFolder)
      
      cylinderAxisX = [1,0,0]
      cylinderAxisY = [0,1,0]
      cylinderAxisZ = [0,0,1]

      cylinderAxisToWorldRotationMatrix = self.getAxes1ToWorldRotationMatrix(cylinderAxisX, cylinderAxisY, cylinderAxisZ)
      transformedCylinderAxisToWorldRotationMatrix = self.getAxes1ToWorldRotationMatrix(transformedCylinderAxisX, transformedCylinderAxisY, transformedCylinderAxisZ)

      cylinderAxisToTransformedCylinderAxisRotationMatrix = self.getAxes1ToAxes2RotationMatrix(cylinderAxisToWorldRotationMatrix, transformedCylinderAxisToWorldRotationMatrix)

      transformNode = slicer.vtkMRMLLinearTransformNode()
      transformNode.SetName("temp%d" % i)
      slicer.mrmlScene.AddNode(transformNode)

      finalTransform = vtk.vtkTransform()
      finalTransform.PostMultiply()
      finalTransform.Concatenate(cylinderAxisToTransformedCylinderAxisRotationMatrix)
      finalTransform.Translate(pos)

      transformNode.SetMatrixTransformToParent(finalTransform.GetMatrix())

      transformNode.UpdateScene(slicer.mrmlScene)

      cylinderModel.SetAndObserveTransformNodeID(transformNode.GetID())
      cylinderModel.HardenTransform()
      
      transformNodeItemID = shNode.GetItemByDataNode(transformNode)
      shNode.SetItemParent(transformNodeItemID, cylindersTransformsFolder)
    
    shNode.RemoveItem(cylindersTransformsFolder)
  
  def createCylindersFromFiducialListAndMandibleSurgicalGuideBase(self):
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    mandibleCylindersModelsFolder = shNode.GetItemByName("Mandible Cylinders Models")
    shNode.RemoveItem(mandibleCylindersModelsFolder)
    mandibleCylindersModelsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Mandible Cylinders Models")
    cylindersTransformsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Cylinders Transforms")
    
    parameterNode = self.getParameterNode()
    mandibleFiducialList = parameterNode.GetNodeReference("mandibleFiducialList")
    mandibleSurgicalGuideBaseModel = parameterNode.GetNodeReference("mandibleSurgicalGuideBaseModel")
    mandibleScrewHoleCylinderRadius = float(parameterNode.GetParameter("mandibleScrewHoleCylinderRadius"))

    normalsOfSurgicalGuideBaseModel = slicer.util.arrayFromModelPointData(mandibleSurgicalGuideBaseModel, 'Normals')
    
    surgicalGuideBaseMesh = mandibleSurgicalGuideBaseModel.GetMesh()

    for i in range(mandibleFiducialList.GetNumberOfFiducials()):
      pos = [0,0,0]
      mandibleFiducialList.GetNthFiducialPosition(i,pos)

      pointID = surgicalGuideBaseMesh.FindPoint(pos)

      normalAtPointID = normalsOfSurgicalGuideBaseModel[pointID]

      transformedCylinderAxisX = [0,0,0]
      transformedCylinderAxisY = [0,0,0]
      transformedCylinderAxisZ = normalAtPointID
      vtk.vtkMath.Perpendiculars(transformedCylinderAxisZ,transformedCylinderAxisX,transformedCylinderAxisY,0)

      cylinderModel = createCylinder(mandibleScrewHoleCylinderRadius, "cylinder%d" % i)
      cylinderModelItemID = shNode.GetItemByDataNode(cylinderModel)
      shNode.SetItemParent(cylinderModelItemID, mandibleCylindersModelsFolder)
      
      cylinderAxisX = [1,0,0]
      cylinderAxisY = [0,1,0]
      cylinderAxisZ = [0,0,1]

      cylinderAxisToWorldRotationMatrix = self.getAxes1ToWorldRotationMatrix(cylinderAxisX, cylinderAxisY, cylinderAxisZ)
      transformedCylinderAxisToWorldRotationMatrix = self.getAxes1ToWorldRotationMatrix(transformedCylinderAxisX, transformedCylinderAxisY, transformedCylinderAxisZ)

      cylinderAxisToTransformedCylinderAxisRotationMatrix = self.getAxes1ToAxes2RotationMatrix(cylinderAxisToWorldRotationMatrix, transformedCylinderAxisToWorldRotationMatrix)

      transformNode = slicer.vtkMRMLLinearTransformNode()
      transformNode.SetName("temp%d" % i)
      slicer.mrmlScene.AddNode(transformNode)

      finalTransform = vtk.vtkTransform()
      finalTransform.PostMultiply()
      finalTransform.Concatenate(cylinderAxisToTransformedCylinderAxisRotationMatrix)
      finalTransform.Translate(pos)

      transformNode.SetMatrixTransformToParent(finalTransform.GetMatrix())

      transformNode.UpdateScene(slicer.mrmlScene)

      cylinderModel.SetAndObserveTransformNodeID(transformNode.GetID())
      cylinderModel.HardenTransform()
      
      transformNodeItemID = shNode.GetItemByDataNode(transformNode)
      shNode.SetItemParent(transformNodeItemID, cylindersTransformsFolder)
    
    shNode.RemoveItem(cylindersTransformsFolder)

  def makeBooleanOperationsToFibulaSurgicalGuideBase(self):
    parameterNode = self.getParameterNode()
    fibulaSurgicalGuideBaseModel = parameterNode.GetNodeReference("fibulaSurgicalGuideBaseModel")

    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    fibulaCylindersModelsFolder = shNode.GetItemByName("Fibula Cylinders Models")
    cylindersModelsList = createListFromFolderID(fibulaCylindersModelsFolder)
    miterBoxesModelsFolder = shNode.GetItemByName("miterBoxes Models")
    miterBoxesModelsList = createListFromFolderID(miterBoxesModelsFolder)
    biggerMiterBoxesModelsFolder = shNode.GetItemByName("biggerMiterBoxes Models")
    biggerMiterBoxesModelsList = createListFromFolderID(biggerMiterBoxesModelsFolder)

    combineModelsLogic = slicer.modules.combinemodels.widgetRepresentation().self().logic

    surgicalGuideModel = slicer.modules.models.logic().AddModel(fibulaSurgicalGuideBaseModel.GetPolyData())
    surgicalGuideModel.SetName(slicer.mrmlScene.GetUniqueNameByString('FibulaSurgicalGuidePrototype'))
    surgicalGuideModelItemID = shNode.GetItemByDataNode(surgicalGuideModel)
    shNode.SetItemParent(surgicalGuideModelItemID, self.getParentFolderItemID())

    displayNode = surgicalGuideModel.GetDisplayNode()
    fibulaViewNode = slicer.mrmlScene.GetSingletonNode("2", "vtkMRMLViewNode")
    displayNode.AddViewNodeID(fibulaViewNode.GetID())

    for i in range(len(biggerMiterBoxesModelsList)):
      combineModelsLogic.process(surgicalGuideModel, biggerMiterBoxesModelsList[i], surgicalGuideModel, 'union')

    for i in range(len(cylindersModelsList)):
      combineModelsLogic.process(surgicalGuideModel, cylindersModelsList[i], surgicalGuideModel, 'difference')

    for i in range(len(miterBoxesModelsList)):
      combineModelsLogic.process(surgicalGuideModel, miterBoxesModelsList[i], surgicalGuideModel, 'difference')

    if surgicalGuideModel.GetPolyData().GetNumberOfPoints() == 0:
      slicer.mrmlScene.RemoveNode(surgicalGuideModel)
      slicer.util.errorDisplay("ERROR: Boolean operations to make fibula surgical guide failed")

  def createMandibleCylindersFiducialList(self):
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    mandibleCylindersFiducialsListsFolder = shNode.GetItemByName("Mandible Cylinders Fiducials Lists")
    if not mandibleCylindersFiducialsListsFolder:
      mandibleCylindersFiducialsListsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Mandible Cylinders Fiducials Lists")
    
    mandibleFiducialListNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLMarkupsFiducialNode")
    mandibleFiducialListNode.SetName("temp")
    slicer.mrmlScene.AddNode(mandibleFiducialListNode)
    slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(mandibleFiducialListNode)
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    mandibleFiducialListNodeItemID = shNode.GetItemByDataNode(mandibleFiducialListNode)
    shNode.SetItemParent(mandibleFiducialListNodeItemID, mandibleCylindersFiducialsListsFolder)
    mandibleFiducialListNode.SetName(slicer.mrmlScene.GetUniqueNameByString("mandibleCylindersFiducialsList"))

    #setup placement
    slicer.modules.markups.logic().SetActiveListID(mandibleFiducialListNode)
    interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
    interactionNode.SwitchToPersistentPlaceMode()

  def createSawBoxesFromFirstAndLastMandiblePlanes(self):
    parameterNode = self.getParameterNode()
    mandibularCurve = parameterNode.GetNodeReference("mandibleCurve")
    sawBoxSlotWidth = float(parameterNode.GetParameter("sawBoxSlotWidth"))
    sawBoxSlotLength = float(parameterNode.GetParameter("sawBoxSlotLength"))
    sawBoxSlotHeight = float(parameterNode.GetParameter("sawBoxSlotHeight"))
    sawBoxSlotWall = float(parameterNode.GetParameter("sawBoxSlotWall"))
    clearanceFitPrintingTolerance = float(parameterNode.GetParameter("clearanceFitPrintingTolerance"))
    biggerSawBoxDistanceToMandible = float(parameterNode.GetParameter("biggerSawBoxDistanceToMandible"))
    mandibleModelNode = parameterNode.GetNodeReference("mandibleModelNode")
    
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    mandibularPlanesFolder = shNode.GetItemByName("Mandibular planes")
    mandibularPlanesList = createListFromFolderID(mandibularPlanesFolder)
    sawBoxesModelsFolder = shNode.GetItemByName("sawBoxes Models")
    shNode.RemoveItem(sawBoxesModelsFolder)
    biggerSawBoxesModelsFolder = shNode.GetItemByName("biggerSawBoxes Models")
    shNode.RemoveItem(biggerSawBoxesModelsFolder)
    sawBoxesPlanesFolder = shNode.GetItemByName("sawBoxes Planes")
    shNode.RemoveItem(sawBoxesPlanesFolder)
    sawBoxesTransformsFolder = shNode.GetItemByName("sawBoxes Transforms")
    shNode.RemoveItem(sawBoxesTransformsFolder)
    sawBoxesModelsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"sawBoxes Models")
    biggerSawBoxesModelsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"biggerSawBoxes Models")
    sawBoxesPlanesFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"sawBoxes Planes")
    sawBoxesTransformsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"sawBoxes Transforms")
    intersectionsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Intersections")
    pointsIntersectionsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Points Intersections")

    mandibleViewNode = slicer.mrmlScene.GetSingletonNode("1", "vtkMRMLViewNode")

    #get best fitting plane to curve with curveCrescent normal direction
    curvePoints = slicer.util.arrayFromMarkupsCurvePoints(mandibularCurve)
    bestFittingPlaneNormalOfCurvePoints = getBestFittingPlaneNormalFromPoints(curvePoints)

    startIndex = 0
    curveLength = mandibularCurve.GetCurveLengthWorld()
    middleIndex = mandibularCurve.GetCurvePointIndexAlongCurveWorld(startIndex,curveLength)
    endIndex = mandibularCurve.GetCurvePointIndexAlongCurveWorld(startIndex,curveLength)
    matrix = vtk.vtkMatrix4x4()
    mandibularCurve.GetCurvePointToWorldTransformAtPointIndex(startIndex,matrix)
    startPoint = np.array([matrix.GetElement(0,3),matrix.GetElement(1,3),matrix.GetElement(2,3)])
    mandibularCurve.GetCurvePointToWorldTransformAtPointIndex(middleIndex,matrix)
    middlePoint = np.array([matrix.GetElement(0,3),matrix.GetElement(1,3),matrix.GetElement(2,3)])
    mandibularCurve.GetCurvePointToWorldTransformAtPointIndex(endIndex,matrix)
    endPoint = np.array([matrix.GetElement(0,3),matrix.GetElement(1,3),matrix.GetElement(2,3)])
    startToMiddle = middlePoint - startPoint
    middleToEnd = endPoint - middlePoint
    normalToCurve = [0,0,0]
    vtk.vtkMath.Cross(startToMiddle, middleToEnd, normalToCurve)
    
    if vtk.vtkMath.Dot(bestFittingPlaneNormalOfCurvePoints,normalToCurve) < 0:
      bestFittingPlaneNormalOfCurvePoints *= -1


    for i in range(0,len(mandibularPlanesList),len(mandibularPlanesList)-1):
      #sawBoxModel: the numbers are selected arbitrarily to make a box with the correct size then they'll be GUI set
      if i == 0:
        sawBoxName = "sawBox_%d" % i
        biggerSawBoxName = "biggerSawBox%d" % i
      else:
        sawBoxName = "sawBox_%d" % (len(mandibularPlanesList)-1)
        biggerSawBoxName = "biggerSawBox%d" % (len(mandibularPlanesList)-1)
      sawBoxWidth = sawBoxSlotWidth+2*clearanceFitPrintingTolerance
      sawBoxLength = sawBoxSlotLength
      sawBoxHeight = 70
      sawBoxModel = createBox(sawBoxLength,sawBoxHeight,sawBoxWidth,sawBoxName)
      sawBoxModelItemID = shNode.GetItemByDataNode(sawBoxModel)
      shNode.SetItemParent(sawBoxModelItemID, sawBoxesModelsFolder)

      sawBoxDisplayNode = sawBoxModel.GetDisplayNode()
      sawBoxDisplayNode.AddViewNodeID(mandibleViewNode.GetID())
      sawBoxDisplayNode.SetVisibility(False)

      biggerSawBoxWidth = sawBoxSlotWidth+2*clearanceFitPrintingTolerance+2*sawBoxSlotWall
      biggerSawBoxLength = sawBoxSlotLength+2*sawBoxSlotWall
      biggerSawBoxHeight = sawBoxSlotHeight
      biggerSawBoxModel = createBox(biggerSawBoxLength,biggerSawBoxHeight,biggerSawBoxWidth,biggerSawBoxName)
      biggerSawBoxModelItemID = shNode.GetItemByDataNode(biggerSawBoxModel)
      shNode.SetItemParent(biggerSawBoxModelItemID, biggerSawBoxesModelsFolder)

      biggerSawBoxDisplayNode = biggerSawBoxModel.GetDisplayNode()
      biggerSawBoxDisplayNode.AddViewNodeID(mandibleViewNode.GetID())

      #Create sawBox plane
      sawBoxPlane = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsPlaneNode", "sawBox Plane%d" % i)
      slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(sawBoxPlane)
      sawBoxPlaneItemID = shNode.GetItemByDataNode(sawBoxPlane)
      shNode.SetItemParent(sawBoxPlaneItemID, sawBoxesPlanesFolder)

      sawBoxPlane.SetAxes([1,0,0],[0,1,0],[0,0,1])
      sawBoxPlane.SetOrigin([0,0,0])
      sawBoxPlane.SetAttribute("isSawBoxPlane","True")

      displayNode = sawBoxPlane.GetDisplayNode()
      mandibleViewNode = slicer.mrmlScene.GetSingletonNode("1", "vtkMRMLViewNode")
      displayNode.AddViewNodeID(mandibleViewNode.GetID())
      displayNode.SetGlyphScale(2.5)
      displayNode.SetOpacity(0)
      displayNode.HandlesInteractiveOn()

      mandiblePlaneMatrix = vtk.vtkMatrix4x4()
      if int(slicer.app.revision) > int(SLICER_CHANGE_OF_API_REVISION):
        mandibularPlanesList[i].GetObjectToWorldMatrix(mandiblePlaneMatrix)
      else:
        mandibularPlanesList[i].GetPlaneToWorldMatrix(mandiblePlaneMatrix)
      mandiblePlaneZ = np.array([mandiblePlaneMatrix.GetElement(0,2),mandiblePlaneMatrix.GetElement(1,2),mandiblePlaneMatrix.GetElement(2,2)])
      
      if i == 0:
        intersectionModel = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Intersection%d' % i)
      else:
        intersectionModel = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Intersection%d' % (len(mandibularPlanesList)-1))
      intersectionModel.CreateDefaultDisplayNodes()
      getNearestIntersectionBetweenModelAnd1Plane(mandibleModelNode,mandibularPlanesList[i],intersectionModel)
      intersectionModelCentroid = getCentroid(intersectionModel)
      if i == 0:
        pointsIntersectionModel = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Points Intersection%d' % i)
      else:
        pointsIntersectionModel = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Points Intersection%d' % (len(mandibularPlanesList)-1))
      pointsIntersectionModel.CreateDefaultDisplayNodes()
      getIntersectionBetweenModelAnd1PlaneWithNormalAndOrigin_2(intersectionModel,bestFittingPlaneNormalOfCurvePoints,intersectionModelCentroid,pointsIntersectionModel)
      curvePlanarConvexityDirection = [0,0,0]
      vtk.vtkMath.Cross(mandiblePlaneZ, bestFittingPlaneNormalOfCurvePoints, curvePlanarConvexityDirection)
      pointOfIntersection = getPointOfATwoPointsModelThatMakesLineDirectionSimilarToVector(pointsIntersectionModel,curvePlanarConvexityDirection)
      intersectionModelItemID = shNode.GetItemByDataNode(intersectionModel)
      shNode.SetItemParent(intersectionModelItemID, intersectionsFolder)
      pointsIntersectionModelItemID = shNode.GetItemByDataNode(pointsIntersectionModel)
      shNode.SetItemParent(pointsIntersectionModelItemID, pointsIntersectionsFolder)


      sawBoxDirection = getAverageNormalFromModelPoint(mandibleModelNode,pointOfIntersection)
      #sawBoxDirection = (pointOfIntersection-intersectionModelCentroid)/np.linalg.norm(pointOfIntersection-intersectionModelCentroid)

      sawBoxAxisX = [0,0,0]
      sawBoxAxisY =  [0,0,0]
      sawBoxAxisZ = mandiblePlaneZ
      vtk.vtkMath.Cross(sawBoxDirection, sawBoxAxisZ, sawBoxAxisX)
      sawBoxAxisX = sawBoxAxisX/np.linalg.norm(sawBoxAxisX)
      vtk.vtkMath.Cross(sawBoxAxisZ, sawBoxAxisX, sawBoxAxisY)
      sawBoxAxisY = sawBoxAxisY/np.linalg.norm(sawBoxAxisY)

      sawBoxAxisToWorldRotationMatrix = self.getAxes1ToWorldRotationMatrix(sawBoxAxisX, sawBoxAxisY, sawBoxAxisZ)
      WorldToWorldRotationMatrix = self.getAxes1ToWorldRotationMatrix([1,0,0], [0,1,0], [0,0,1])

      WorldToSawBoxAxisRotationMatrix = self.getAxes1ToAxes2RotationMatrix(WorldToWorldRotationMatrix, sawBoxAxisToWorldRotationMatrix)

      WorldToSawBoxAxisX = np.array([WorldToSawBoxAxisRotationMatrix.GetElement(0,0),WorldToSawBoxAxisRotationMatrix.GetElement(1,0),WorldToSawBoxAxisRotationMatrix.GetElement(2,0)])
      WorldToSawBoxAxisY = np.array([WorldToSawBoxAxisRotationMatrix.GetElement(0,1),WorldToSawBoxAxisRotationMatrix.GetElement(1,1),WorldToSawBoxAxisRotationMatrix.GetElement(2,1)])
      WorldToSawBoxAxisZ = np.array([WorldToSawBoxAxisRotationMatrix.GetElement(0,2),WorldToSawBoxAxisRotationMatrix.GetElement(1,2),WorldToSawBoxAxisRotationMatrix.GetElement(2,2)])

      if i == 0:
        sawBoxAxisXTranslation = 0
        sawBoxAxisYTranslation = biggerSawBoxHeight/2+biggerSawBoxDistanceToMandible
        sawBoxAxisZTranslation = sawBoxSlotWidth/2
      else:
        sawBoxAxisXTranslation = 0
        sawBoxAxisYTranslation = biggerSawBoxHeight/2+biggerSawBoxDistanceToMandible
        sawBoxAxisZTranslation = -sawBoxSlotWidth/2
      WorldToSawBoxAxisOrigin = pointOfIntersection + sawBoxAxisX*sawBoxAxisXTranslation + sawBoxAxisY*sawBoxAxisYTranslation + sawBoxAxisZ*sawBoxAxisZTranslation

      sawBoxPlane.SetAxes(WorldToSawBoxAxisX,WorldToSawBoxAxisY,WorldToSawBoxAxisZ)
      sawBoxPlane.SetOrigin(WorldToSawBoxAxisOrigin)

      transformNode = slicer.vtkMRMLLinearTransformNode()
      transformNode.SetName("sawBoxTransform%d" % i)
      slicer.mrmlScene.AddNode(transformNode)

      sawBoxPlaneToWorldMatrix = vtk.vtkMatrix4x4()
      if int(slicer.app.revision) > int(SLICER_CHANGE_OF_API_REVISION):
        sawBoxPlane.GetObjectToWorldMatrix(sawBoxPlaneToWorldMatrix)
      else:
        sawBoxPlane.GetPlaneToWorldMatrix(sawBoxPlaneToWorldMatrix)
      transformNode.SetMatrixTransformToParent(sawBoxPlaneToWorldMatrix)

      transformNode.UpdateScene(slicer.mrmlScene)

      sawBoxModel.SetAndObserveTransformNodeID(transformNode.GetID())
      biggerSawBoxModel.SetAndObserveTransformNodeID(transformNode.GetID())
      
      transformNodeItemID = shNode.GetItemByDataNode(transformNode)
      shNode.SetItemParent(transformNodeItemID, sawBoxesTransformsFolder)

      observer = sawBoxPlane.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent,self.onSawBoxPlaneMoved)
      self.sawBoxPlaneObserversPlaneNodeIDAndTransformIDList.append([observer,sawBoxPlane.GetID(),transformNode.GetID()])

    shNode.RemoveItem(intersectionsFolder)
    shNode.RemoveItem(pointsIntersectionsFolder)
    
  def onSawBoxPlaneMoved(self,sourceNode,event):
    for i in range(len(self.sawBoxPlaneObserversPlaneNodeIDAndTransformIDList)):
      if self.sawBoxPlaneObserversPlaneNodeIDAndTransformIDList[i][1] == sourceNode.GetID():
        sawBoxPlane = slicer.mrmlScene.GetNodeByID(self.sawBoxPlaneObserversPlaneNodeIDAndTransformIDList[i][1])
        transformNode = slicer.mrmlScene.GetNodeByID(self.sawBoxPlaneObserversPlaneNodeIDAndTransformIDList[i][2])
        sawBoxPlaneToWorldMatrix = vtk.vtkMatrix4x4()
        if int(slicer.app.revision) > int(SLICER_CHANGE_OF_API_REVISION):
          sawBoxPlane.GetObjectToWorldMatrix(sawBoxPlaneToWorldMatrix)
        else:
          sawBoxPlane.GetPlaneToWorldMatrix(sawBoxPlaneToWorldMatrix)
        transformNode.SetMatrixTransformToParent(sawBoxPlaneToWorldMatrix)

  def makeBooleanOperationsToMandibleSurgicalGuideBase(self):
    parameterNode = self.getParameterNode()
    mandibleSurgicalGuideBaseModel = parameterNode.GetNodeReference("mandibleSurgicalGuideBaseModel")
    mandibleBridgeModel = parameterNode.GetNodeReference("mandibleBridgeModel")
    

    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    mandibleCylindersModelsFolder = shNode.GetItemByName("Mandible Cylinders Models")
    cylindersModelsList = createListFromFolderID(mandibleCylindersModelsFolder)
    sawBoxesModelsFolder = shNode.GetItemByName("sawBoxes Models")
    sawBoxesModelsList = createListFromFolderID(sawBoxesModelsFolder)
    biggerSawBoxesModelsFolder = shNode.GetItemByName("biggerSawBoxes Models")
    biggerSawBoxesModelsList = createListFromFolderID(biggerSawBoxesModelsFolder)

    combineModelsLogic = slicer.modules.combinemodels.widgetRepresentation().self().logic

    surgicalGuideModel = slicer.modules.models.logic().AddModel(mandibleSurgicalGuideBaseModel.GetPolyData())
    surgicalGuideModel.SetName(slicer.mrmlScene.GetUniqueNameByString('MandibleSurgicalGuidePrototype'))
    surgicalGuideModelItemID = shNode.GetItemByDataNode(surgicalGuideModel)
    shNode.SetItemParent(surgicalGuideModelItemID, self.getParentFolderItemID())

    displayNode = surgicalGuideModel.GetDisplayNode()
    mandibleViewNode = slicer.mrmlScene.GetSingletonNode("1", "vtkMRMLViewNode")
    displayNode.AddViewNodeID(mandibleViewNode.GetID())

    for i in range(len(biggerSawBoxesModelsList)):
      combineModelsLogic.process(surgicalGuideModel, biggerSawBoxesModelsList[i], surgicalGuideModel, 'union')
    
    if mandibleBridgeModel:
      combineModelsLogic.process(surgicalGuideModel, mandibleBridgeModel, surgicalGuideModel, 'union')

    for i in range(len(cylindersModelsList)):
      combineModelsLogic.process(surgicalGuideModel, cylindersModelsList[i], surgicalGuideModel, 'difference')

    for i in range(len(sawBoxesModelsList)):
      combineModelsLogic.process(surgicalGuideModel, sawBoxesModelsList[i], surgicalGuideModel, 'difference')

    if surgicalGuideModel.GetPolyData().GetNumberOfPoints() == 0:
      slicer.mrmlScene.RemoveNode(surgicalGuideModel)
      slicer.util.errorDisplay("ERROR: Boolean operations to make mandible surgical failed")


  def centerFibulaLine(self):
    parameterNode = self.getParameterNode()
    fibulaLine = parameterNode.GetNodeReference("fibulaLine")
    fibulaModelNode = parameterNode.GetNodeReference("fibulaModelNode")

    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    intersectionsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Intersections")

    lineStartPos = np.zeros(3)
    lineEndPos = np.zeros(3)
    fibulaLine.GetNthControlPointPositionWorld(0, lineStartPos)
    fibulaLine.GetNthControlPointPositionWorld(1, lineEndPos)

    numberOfRepetitionsOfPositioningAlgorithm = 5
    for i in range(numberOfRepetitionsOfPositioningAlgorithm):
      fibulaLineNorm = np.linalg.norm(lineEndPos-lineStartPos)
      fibulaLineDirection = (lineEndPos-lineStartPos)/fibulaLineNorm

      fibulaStartIntersectionModel = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','FibulaStartIntersection %d' % i)
      fibulaEndIntersectionModel = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','FibulaEndIntersection %d' % i)
      fibulaStartIntersectionModel.CreateDefaultDisplayNodes()
      fibulaEndIntersectionModel.CreateDefaultDisplayNodes()

      fibulaStartIntersectionModelItemID = shNode.GetItemByDataNode(fibulaStartIntersectionModel)
      shNode.SetItemParent(fibulaStartIntersectionModelItemID, intersectionsFolder)
      fibulaEndIntersectionModelItemID = shNode.GetItemByDataNode(fibulaEndIntersectionModel)
      shNode.SetItemParent(fibulaEndIntersectionModelItemID, intersectionsFolder)

      getIntersectionBetweenModelAnd1PlaneWithNormalAndOrigin_2(fibulaModelNode,fibulaLineDirection,lineStartPos,fibulaStartIntersectionModel)
      getIntersectionBetweenModelAnd1PlaneWithNormalAndOrigin_2(fibulaModelNode,fibulaLineDirection,lineEndPos,fibulaEndIntersectionModel)
      lineStartPos = getCentroid(fibulaStartIntersectionModel)
      lineEndPos = getCentroid(fibulaEndIntersectionModel)

    fibulaLine.SetNthControlPointPositionFromArray(0,lineStartPos)
    fibulaLine.SetNthControlPointPositionFromArray(1,lineEndPos)

    shNode.RemoveItem(intersectionsFolder)

  def create3DModelOfTheReconstruction(self):
    parameterNode = self.getParameterNode()
    fibulaLine = parameterNode.GetNodeReference("fibulaLine")
    planeList = createListFromFolderID(self.getMandiblePlanesFolderItemID())

    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    scaledFibulaPiecesFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Scaled Fibula Pieces")
    scaledFibulaPiecesTransformsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Scaled Fibula Pieces Transforms")
    transformedFibulaPiecesFolder = shNode.GetItemByName("Transformed Fibula Pieces")
    transformedFibulaPiecesList = createListFromFolderID(transformedFibulaPiecesFolder)
    cutBonesList = createListFromFolderID(shNode.GetItemByName("Cut Bones"))

    if len(transformedFibulaPiecesList) == 0:
      return

    for i in range(len(transformedFibulaPiecesList)):
      or0 = np.zeros(3)
      planeList[i].GetOrigin(or0)
      or1 = np.zeros(3)
      planeList[i+1].GetOrigin(or1)
      origin = (or0+or1)/2

      scaleTransformNode = slicer.vtkMRMLLinearTransformNode()
      scaleTransformNode.SetName("Scale Bone Piece {0} Transform".format(i))
      slicer.mrmlScene.AddNode(scaleTransformNode)

      scaleTransform = vtk.vtkTransform()
      scaleTransform.PostMultiply()
      scaleTransform.Translate(-origin)
      #Just scale them enough so that boolean union is successful
      scaleTransform.Scale(1.0001, 1.0001, 1.0001)
      scaleTransform.Translate(origin)

      scaleTransformNode.SetMatrixTransformToParent(scaleTransform.GetMatrix())
      scaleTransformNode.UpdateScene(slicer.mrmlScene)

      scaledFibulaPiece = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode',slicer.mrmlScene.GetUniqueNameByString('Scaled ' + cutBonesList[i].GetName()))
      scaledFibulaPiece.CreateDefaultDisplayNodes()
      scaledFibulaPiece.CopyContent(transformedFibulaPiecesList[i])
      scaledFibulaPieceDisplayNode = scaledFibulaPiece.GetDisplayNode()
      scaledFibulaPieceDisplayNode.SetColor(transformedFibulaPiecesList[i].GetDisplayNode().GetColor())
      scaledFibulaPieceDisplayNode.SetSliceIntersectionVisibility(True)

      scaledFibulaPiece.SetAndObserveTransformNodeID(scaleTransformNode.GetID())
      scaledFibulaPiece.HardenTransform()

      scaledFibulaPieceItemID = shNode.GetItemByDataNode(scaledFibulaPiece)
      shNode.SetItemParent(scaledFibulaPieceItemID, scaledFibulaPiecesFolder)

      scaleTransformNodeItemID = shNode.GetItemByDataNode(scaleTransformNode)
      shNode.SetItemParent(scaleTransformNodeItemID, scaledFibulaPiecesTransformsFolder)

    shNode.RemoveItem(scaledFibulaPiecesTransformsFolder)

    scaledFibulaPiecesList = createListFromFolderID(scaledFibulaPiecesFolder)

    mandibleReconstructionModel = slicer.modules.models.logic().AddModel(cutBonesList[-1].GetPolyData())
    mandibleReconstructionModel.SetName('Mandible Reconstruction')
    mandibleReconstructionModelItemID = shNode.GetItemByDataNode(mandibleReconstructionModel)
    shNode.SetItemParent(mandibleReconstructionModelItemID, self.getParentFolderItemID())

    combineModelsLogic = slicer.modules.combinemodels.widgetRepresentation().self().logic
    for i in range(len(scaledFibulaPiecesList)):
      combineModelsLogic.process(mandibleReconstructionModel, scaledFibulaPiecesList[i], mandibleReconstructionModel, 'union')

    shNode.RemoveItem(scaledFibulaPiecesFolder)
    
#
# BoneReconstructionPlannerTest
#

class BoneReconstructionPlannerTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear()

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_BoneReconstructionPlanner1()

  def test_BoneReconstructionPlanner1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests should exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")

    # Get/create input data

    import SampleData
    registerSampleData()
    inputVolume = SampleData.downloadSample('BoneReconstructionPlanner1')
    self.delayDisplay('Loaded test data set')

    inputScalarRange = inputVolume.GetImageData().GetScalarRange()
    self.assertEqual(inputScalarRange[0], 0)
    self.assertEqual(inputScalarRange[1], 695)

    outputVolume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode")
    threshold = 100

    # Test the module logic

    logic = BoneReconstructionPlannerLogic()

    # Test algorithm with non-inverted threshold
    logic.process(inputVolume, outputVolume, threshold, True)
    outputScalarRange = outputVolume.GetImageData().GetScalarRange()
    self.assertEqual(outputScalarRange[0], inputScalarRange[0])
    self.assertEqual(outputScalarRange[1], threshold)

    # Test algorithm with inverted threshold
    logic.process(inputVolume, outputVolume, threshold, False)
    outputScalarRange = outputVolume.GetImageData().GetScalarRange()
    self.assertEqual(outputScalarRange[0], inputScalarRange[0])
    self.assertEqual(outputScalarRange[1], inputScalarRange[1])

    self.delayDisplay('Test passed')


def createListFromFolderID(folderID):
  createdList = []
  shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
  myList = vtk.vtkIdList()
  shNode.GetItemChildren(folderID,myList)
  for i in range(myList.GetNumberOfIds()):
    createdList.append(shNode.GetItemDataNode(myList.GetId(i)))
  return createdList