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
    sampleName='CTFibulaCropped',
    # Thumbnail should have size of approximately 260x280 pixels and stored in Resources/Icons folder.
    # It can be created by Screen Capture module, "Capture all views" option enabled, "Number of images" set to "Single".
    thumbnailFileName=os.path.join(iconsPath, 'iconCTFibulaCropped.png'),
    # Download URL and target file name
    uris="https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/releases/download/TestingData/CTFibulaCropped.nrrd",
    fileNames='CTFibulaCropped.nrrd',
    # Checksum to ensure file integrity. Can be computed by this command:
    #  import hashlib; print(hashlib.sha256(open(filename, "rb").read()).hexdigest())
    checksums = 'SHA256:5febc47a8fba6b43440be2b475f9defadffe9b47b1316d04217208b4497a4f72',
    # This node name will be used when the data set is loaded
    nodeNames='CTFibulaCropped'
  )

  # BoneReconstructionPlanner2
  SampleData.SampleDataLogic.registerCustomSampleDataSource(
    # Category and sample name displayed in Sample Data module
    category='BoneReconstructionPlanner',
    sampleName='CTFibula',
    thumbnailFileName=os.path.join(iconsPath, 'iconCTFibula.png'),
    # Download URL and target file name
    uris="https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/releases/download/TestingData/CTFibula.nrrd",
    fileNames='CTFibula.nrrd',
    checksums = 'SHA256:715ae01091b642677e6065b8d7bb4d15ed9adaf31c057f4b53ea70a425bba7a4',
    # This node name will be used when the data set is loaded
    nodeNames='CTFibula'
  )

  # BoneReconstructionPlanner3
  SampleData.SampleDataLogic.registerCustomSampleDataSource(
    # Category and sample name displayed in Sample Data module
    category='BoneReconstructionPlanner',
    sampleName='CTMandible',
    thumbnailFileName=os.path.join(iconsPath, 'iconCTMandible.png'),
    # Download URL and target file name
    uris="https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/releases/download/TestingData/CTMandible.nrrd",
    fileNames='CTMandible.nrrd',
    checksums = 'SHA256:352aefed1905bd2ad7373972a6bb115bd494e26e4fc438d2c8679384dcfd2654',
    # This node name will be used when the data set is loaded
    nodeNames='CTMandible'
  )

  # BoneReconstructionPlanner4
  SampleData.SampleDataLogic.registerCustomSampleDataSource(
    # Category and sample name displayed in Sample Data module
    category='BoneReconstructionPlanner',
    sampleName='FibulaSegmentation',
    thumbnailFileName=os.path.join(iconsPath, 'iconFibulaSegmentation.png'),
    loadFileType='SegmentationFile',
    # Download URL and target file name
    uris="https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/releases/download/TestingData/FibulaSegmentation.seg.nrrd",
    fileNames='FibulaSegmentation.seg.nrrd',
    checksums = 'SHA256:517bfe11a87b709cb8aa6d4187f41d8c86a8d9a033667a4fc8c8b95bf3eeb99d',
    # This node name will be used when the data set is loaded
    nodeNames='FibulaSegmentation'
  )

  # BoneReconstructionPlanner5
  SampleData.SampleDataLogic.registerCustomSampleDataSource(
    # Category and sample name displayed in Sample Data module
    category='BoneReconstructionPlanner',
    sampleName='MandibleSegmentation',
    thumbnailFileName=os.path.join(iconsPath, 'iconMandibleSegmentation.png'),
    loadFileType='SegmentationFile',
    # Download URL and target file name
    uris="https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/releases/download/TestingData/MandibleSegmentation.seg.nrrd",
    fileNames='MandibleSegmentation.seg.nrrd',
    checksums = 'SHA256:d815406843f7945997c8eee6d7cd906e707ed5a1a6aabb2787c5203297e3ef01',
    # This node name will be used when the data set is loaded
    nodeNames='MandibleSegmentation'
  )

  # BoneReconstructionPlanner6
  SampleData.SampleDataLogic.registerCustomSampleDataSource(
    # Category and sample name displayed in Sample Data module
    category='BoneReconstructionPlanner',
    sampleName='TestPlanBRP',
    thumbnailFileName=os.path.join(iconsPath, 'iconTestPlanBRP.png'),
    loadFileType='SceneFile',
    loadFiles="True",
    # Download URL and target file name
    uris="https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner/releases/download/TestingData/TestPlanBRP.mrb",
    fileNames='TestPlanBRP.mrb',
    checksums = 'SHA256:92ace5d23218e74a7deb04f78afa22e49ed98be6951ef4202ac9f26a8f79190b',
    # This node name will be used when the data set is loaded
    nodeNames='TestPlanBRP'
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

    #self.ui.dentalImplantCylinderSelector.addAttribute('vtkMRMLModelNode','isDentalImplantCylinder','True')

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
    self.ui.fibulaLineSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.mandibleCurveSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.mandibularSegmentationSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.fibulaSegmentationSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.fibulaFiducialListSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.fibulaSurgicalGuideBaseSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.miterBoxDirectionLineSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.scalarVolumeSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.mandibleBridgeModelSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.mandibleSurgicalGuideBaseSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.mandibleFiducialListSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.dentalImplantFiducialListSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    #self.ui.dentalImplantCylinderSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.plateCurveSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)

    self.ui.initialSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.betweenSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.securityMarginOfFibulaPiecesSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.miterBoxSlotWidthSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.miterBoxSlotLengthSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.miterBoxSlotHeightSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.miterBoxSlotWallSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.fibulaScrewHoleCylinderRadiusSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.clearanceFitPrintingToleranceSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.biggerMiterBoxDistanceToFibulaSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.intersectionDistanceMultiplierSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.sawBoxSlotWidthSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.sawBoxSlotLengthSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.sawBoxSlotHeightSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.sawBoxSlotWallSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.biggerSawBoxDistanceToMandibleSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.mandibleScrewHoleCylinderRadiusSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.dentalImplantCylinderRadiusSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.dentalImplantCylinderHeightSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.dentalImplantDrillGuideWallSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.plateCrossSectionalWidthSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.plateCrossSectionalLengthSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.plateCrossSectionalBevelRadiusPorcentageSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.plateTipsBevelRadiusSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandibleButton.checkBoxToggled.connect(self.updateParameterNodeFromGUI)
    self.ui.updateFibulaDentalImplantCylindersButton.checkBoxToggled.connect(self.updateParameterNodeFromGUI)

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
    self.ui.updateFibulaDentalImplantCylindersButton.connect('clicked(bool)', self.onUpdateFibulaDentalImplantCylindersButton)
    self.ui.centerFibulaLineButton.connect('clicked(bool)', self.onCenterFibulaLineButton)
    self.ui.showHideBiggerSawBoxesInteractionHandlesButton.connect('clicked(bool)', self.onShowHideBiggerSawBoxesInteractionHandlesButton)
    self.ui.showHideMandiblePlanesInteractionHandlesButton.connect('clicked(bool)', self.onShowHideMandiblePlanesInteractionHandlesButton)
    self.ui.create3DModelOfTheReconstructionButton.connect('clicked(bool)', self.onCreate3DModelOfTheReconstructionButton)
    self.ui.showHideFibulaSegmentsLengthsButton.connect('clicked(bool)', self.onShowHideFibulaSegmentsLengthsButton)
    self.ui.showHideOriginalMandibleButton.connect('clicked(bool)', self.onShowHideOriginalMandibleButton)
    self.ui.createDentalImplantCylindersFiducialListButton.connect('clicked(bool)', self.onCreateDentalImplantCylindersFiducialListButton)
    self.ui.createCylindersFromFiducialListAndNeomandiblePiecesButton.connect('clicked(bool)', self.onCreateCylindersFromFiducialListAndNeomandiblePiecesButton)
    self.ui.createPlateCurveButton.connect('clicked(bool)', self.onCreatePlateCurveButton)
    self.ui.createCustomPlateButton.connect('clicked(bool)', self.onCreateCustomPlateButton)
    self.ui.makeAllMandiblePlanesRotateTogetherCheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)
    self.ui.useMoreExactVersionOfPositioningAlgorithmCheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)
    self.ui.useNonDecimatedBoneModelsForPreviewCheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)
    self.ui.mandiblePlanesPositioningForMaximumBoneContactCheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)
    self.ui.fixCutGoesThroughTheMandibleTwiceCheckBox.connect('stateChanged(int)', self.onFixCutGoesThroughTheMandibleTwiceCheckBox)
    self.ui.checkSecurityMarginOnMiterBoxCreationCheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)
    self.ui.dentalImplantsPlanningAndFibulaDrillGuidesCheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)
    self.ui.customTitaniumPlateDesingCheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)
    self.ui.makeAllDentalImplanCylindersParallelCheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)

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
      if callData.GetAttribute("isDentalImplantPlane") == 'True':
        if len(self.logic.dentalImplantPlaneObserversPlaneNodeIDAndTransformIDList) > 0:
          for i in range(len(self.logic.dentalImplantPlaneObserversPlaneNodeIDAndTransformIDList)):
            if self.logic.dentalImplantPlaneObserversPlaneNodeIDAndTransformIDList[i][1] == callData.GetID():
              observerIndex = i
          callData.RemoveObserver(self.logic.dentalImplantPlaneObserversPlaneNodeIDAndTransformIDList.pop(observerIndex)[0])

  def enter(self):
    """
    Called each time the user opens this module.
    """
    # Make sure parameter node exists and observed
    self.initializeParameterNode()

    if not slicer.app.commandOptions().noMainWindow:
      self.logic.addCustomLayout()
    
    shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    mandibularPlanesFolder = shNode.GetItemByName("Mandibular planes")
    sawBoxesPlanesFolder = shNode.GetItemByName("sawBoxes Planes")
    dentalImplantsPlanesFolder = shNode.GetItemByName("dentalImplants Planes")
    mandibularPlanesList = createListFromFolderID(mandibularPlanesFolder)
    sawBoxesPlanesList = createListFromFolderID(sawBoxesPlanesFolder)
    dentalImplantsPlanesList = createListFromFolderID(dentalImplantsPlanesFolder)

    self.logic.setInteractiveHandlesVisibilityOfMarkups(
      mandibularPlanesList,
      visibility=True
    )
    self.logic.setMarkupsListLocked(mandibularPlanesList,locked=False)
    self.logic.addMandiblePlaneObservers()

    self.logic.setInteractiveHandlesVisibilityOfMarkups(
      sawBoxesPlanesList,
      visibility=True
    )
    self.logic.setMarkupsListLocked(sawBoxesPlanesList,locked=False)
    self.logic.addSawBoxPlaneObservers()

    self.logic.setInteractiveHandlesVisibilityOfMarkups(
      dentalImplantsPlanesList,
      visibility=True
    )
    self.logic.setMarkupsListLocked(dentalImplantsPlanesList,locked=False)
    self.logic.addDentalImplantsPlaneObservers()

    if (self.ui.scalarVolumeSelector.nodeCount() != 0) and (self.ui.scalarVolumeSelector.currentNode() == None):
      self.ui.scalarVolumeSelector.setCurrentNodeIndex(0)#0 == first scalarVolume

  def exit(self):
    """
    Called each time the user opens a different module.
    """
    # Do not react to parameter node changes (GUI wlil be updated when the user enters into the module)
    self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

    shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    mandibularPlanesFolder = shNode.GetItemByName("Mandibular planes")
    sawBoxesPlanesFolder = shNode.GetItemByName("sawBoxes Planes")
    dentalImplantsPlanesFolder = shNode.GetItemByName("dentalImplants Planes")
    mandibularPlanesList = createListFromFolderID(mandibularPlanesFolder)
    sawBoxesPlanesList = createListFromFolderID(sawBoxesPlanesFolder)
    dentalImplantsPlanesList = createListFromFolderID(dentalImplantsPlanesFolder)

    self.logic.setInteractiveHandlesVisibilityOfMarkups(
      mandibularPlanesList,
      visibility=False
    )
    self.logic.setMarkupsListLocked(mandibularPlanesList,locked=True)
    self.logic.removeMandiblePlaneObservers()

    self.logic.setInteractiveHandlesVisibilityOfMarkups(
      sawBoxesPlanesList,
      visibility=False
    )
    self.logic.setMarkupsListLocked(sawBoxesPlanesList,locked=True)
    self.logic.removeSawBoxPlaneObservers()

    self.logic.setInteractiveHandlesVisibilityOfMarkups(
      dentalImplantsPlanesList,
      visibility=False
    )
    self.logic.setMarkupsListLocked(dentalImplantsPlanesList,locked=True)
    self.logic.removeDentalImplantsPlaneObservers()

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

    # The line below is for selector updates
    currentScalarVolume = self._parameterNode.GetNodeReference("currentScalarVolume")
    self.ui.scalarVolumeSelector.setCurrentNode(currentScalarVolume)
    if currentScalarVolume is not None:
      scalarVolumeID = currentScalarVolume.GetID()
      if not slicer.app.commandOptions().noMainWindow:
        if scalarVolumeID:
          self.logic.setBackgroundVolumeFromID(scalarVolumeID)
          self.logic.setRedSliceForBoneModelsDisplayNodes()
          self.logic.setRedSliceForBoxModelsDisplayNodes()

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
    self.ui.dentalImplantFiducialListSelector.setCurrentNode(self._parameterNode.GetNodeReference("dentalImplantsFiducialList"))
    #self.ui.dentalImplantCylinderSelector.setCurrentNode(self._parameterNode.GetNodeReference("selectedDentalImplantCylinderModel"))
    self.ui.plateCurveSelector.setCurrentNode(self._parameterNode.GetNodeReference("plateCurve"))

    if self._parameterNode.GetNodeReference("fibulaSurgicalGuideBaseModel") is not None:
      self.ui.createCylindersFromFiducialListAndFibulaSurgicalGuideBaseButton.enabled = True
    else:
      self.ui.createCylindersFromFiducialListAndFibulaSurgicalGuideBaseButton.enabled = False

    if self._parameterNode.GetNodeReference("mandibleSurgicalGuideBaseModel") is not None:
      self.ui.createCylindersFromFiducialListAndMandibleSurgicalGuideBaseButton.enabled = True
    else:
      self.ui.createCylindersFromFiducialListAndMandibleSurgicalGuideBaseButton.enabled = False

    if self._parameterNode.GetParameter("initialSpace") != '':
      self.ui.initialSpinBox.setValue(float(self._parameterNode.GetParameter("initialSpace")))
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
    if self._parameterNode.GetParameter("dentalImplantCylinderRadius") != '':
      self.ui.dentalImplantCylinderRadiusSpinBox.setValue(float(self._parameterNode.GetParameter("dentalImplantCylinderRadius")))
    if self._parameterNode.GetParameter("dentalImplantCylinderHeight") != '':
      self.ui.dentalImplantCylinderHeightSpinBox.setValue(float(self._parameterNode.GetParameter("dentalImplantCylinderHeight")))
    if self._parameterNode.GetParameter("dentalImplantDrillGuideWall") != '':
      self.ui.dentalImplantDrillGuideWallSpinBox.setValue(float(self._parameterNode.GetParameter("dentalImplantDrillGuideWall")))
    if self._parameterNode.GetParameter("plateCrossSectionalWidth") != '':
      self.ui.plateCrossSectionalWidthSpinBox.setValue(float(self._parameterNode.GetParameter("plateCrossSectionalWidth")))
    if self._parameterNode.GetParameter("plateCrossSectionalLength") != '':
      self.ui.plateCrossSectionalLengthSpinBox.setValue(float(self._parameterNode.GetParameter("plateCrossSectionalLength")))
    if self._parameterNode.GetParameter("plateCrossSectionalBevelRadiusPorcentage") != '':
      self.ui.plateCrossSectionalBevelRadiusPorcentageSpinBox.setValue(float(self._parameterNode.GetParameter("plateCrossSectionalBevelRadiusPorcentage")))
    if self._parameterNode.GetParameter("plateTipsBevelRadius") != '':
      self.ui.plateTipsBevelRadiusSpinBox.setValue(float(self._parameterNode.GetParameter("plateTipsBevelRadius")))

    self.ui.notLeftFibulaCheckBox.checked = self._parameterNode.GetParameter("notLeftFibula") == "True"
    self.ui.makeAllMandiblePlanesRotateTogetherCheckBox.checked = self._parameterNode.GetParameter("makeAllMandiblePlanesRotateTogether") == "True"
    self.ui.useMoreExactVersionOfPositioningAlgorithmCheckBox.checked = self._parameterNode.GetParameter("useMoreExactVersionOfPositioningAlgorithm") == "True"
    self.ui.useNonDecimatedBoneModelsForPreviewCheckBox.checked = self._parameterNode.GetParameter("useNonDecimatedBoneModelsForPreview") == "True"
    self.ui.mandiblePlanesPositioningForMaximumBoneContactCheckBox.checked = self._parameterNode.GetParameter("mandiblePlanesPositioningForMaximumBoneContact") == "True"
    self.ui.checkSecurityMarginOnMiterBoxCreationCheckBox.checked = self._parameterNode.GetParameter("checkSecurityMarginOnMiterBoxCreation") != "False"

    dentalImplantsPlanningAndFibulaDrillGuidesChecked = self._parameterNode.GetParameter("dentalImplantsPlanningAndFibulaDrillGuides") == "True"
    customTitaniumPlateDesingChecked = self._parameterNode.GetParameter("customTitaniumPlateDesing") == "True"
    makeAllDentalImplanCylindersParallelChecked = self._parameterNode.GetParameter("makeAllDentalImplanCylindersParallel") == "True"
    self.ui.dentalImplantsPlanningAndFibulaDrillGuidesCheckBox.checked = dentalImplantsPlanningAndFibulaDrillGuidesChecked
    self.ui.customTitaniumPlateDesingCheckBox.checked = customTitaniumPlateDesingChecked
    self.ui.makeAllDentalImplanCylindersParallelCheckBox.checked = makeAllDentalImplanCylindersParallelChecked

    if dentalImplantsPlanningAndFibulaDrillGuidesChecked:
      self.ui.dentalImplantsPlanningCollapsibleButton.show()
      self.ui.makeBooleanOperationsToFibulaSurgicalGuideBaseButton.text = (
        "Make boolean operations to surgical\n guide base with screwHolesCylinders,\n fibulaDentalImplantCylinders and miterBoxes"
      )
    else:
      self.ui.dentalImplantsPlanningCollapsibleButton.hide()
      self.ui.makeBooleanOperationsToFibulaSurgicalGuideBaseButton.text = (
        "Make boolean operations to surgical\n guide base with screwHolesCylinders\n and miterBoxes"
      )
    
    if customTitaniumPlateDesingChecked:
      self.ui.customTitaniumPlateGenerationCollapsibleButton.show()
    else:
      self.ui.customTitaniumPlateGenerationCollapsibleButton.hide()

    
    if self._parameterNode.GetParameter("updateOnMandiblePlanesMovement") == "True":
      self.ui.generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandibleButton.checkState = 2
    else:
      self.ui.generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandibleButton.checkState = 0

    if self._parameterNode.GetParameter("updateOnDentalImplantPlanesMovement") == "True":
      self.ui.updateFibulaDentalImplantCylindersButton.checkState = 2
    else:
      self.ui.updateFibulaDentalImplantCylindersButton.checkState = 0

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

    previousScalarVolume = self._parameterNode.GetNodeReference("currentScalarVolume")
    self._parameterNode.SetNodeReferenceID("currentScalarVolume", self.ui.scalarVolumeSelector.currentNodeID)
    currentScalarVolumeChanged = str(
      not(self.ui.scalarVolumeSelector.currentNode() == previousScalarVolume)
    )
    if currentScalarVolumeChanged == "True":
      self._parameterNode.SetParameter("scalarVolumeChangedThroughParameterNode", "True")

    self._parameterNode.SetNodeReferenceID("mandibleCurve", self.ui.mandibleCurveSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("mandibularSegmentation", self.ui.mandibularSegmentationSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("fibulaSegmentation", self.ui.fibulaSegmentationSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("fibulaLine", self.ui.fibulaLineSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("fibulaFiducialList", self.ui.fibulaFiducialListSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("fibulaSurgicalGuideBaseModel", self.ui.fibulaSurgicalGuideBaseSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("miterBoxDirectionLine", self.ui.miterBoxDirectionLineSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("mandibleBridgeModel", self.ui.mandibleBridgeModelSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("mandibleSurgicalGuideBaseModel", self.ui.mandibleSurgicalGuideBaseSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("mandibleFiducialList", self.ui.mandibleFiducialListSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("dentalImplantsFiducialList", self.ui.dentalImplantFiducialListSelector.currentNodeID)
    #self._parameterNode.SetNodeReferenceID("selectedDentalImplantCylinderModel", self.ui.dentalImplantCylinderSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("plateCurve", self.ui.plateCurveSelector.currentNodeID)

    self._parameterNode.SetParameter("initialSpace", str(self.ui.initialSpinBox.value))
    self._parameterNode.SetParameter("additionalBetweenSpaceOfFibulaPlanes", str(self.ui.betweenSpinBox.value))
    self._parameterNode.SetParameter("intersectionDistanceMultiplier", str(self.ui.intersectionDistanceMultiplierSpinBox.value))
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
    self._parameterNode.SetParameter("dentalImplantCylinderRadius", str(self.ui.dentalImplantCylinderRadiusSpinBox.value))
    self._parameterNode.SetParameter("dentalImplantCylinderHeight", str(self.ui.dentalImplantCylinderHeightSpinBox.value))
    self._parameterNode.SetParameter("dentalImplantDrillGuideWall", str(self.ui.dentalImplantDrillGuideWallSpinBox.value))
    self._parameterNode.SetParameter("plateCrossSectionalWidth", str(self.ui.plateCrossSectionalWidthSpinBox.value))
    self._parameterNode.SetParameter("plateCrossSectionalLength", str(self.ui.plateCrossSectionalLengthSpinBox.value))
    self._parameterNode.SetParameter("plateCrossSectionalBevelRadiusPorcentage", str(self.ui.plateCrossSectionalBevelRadiusPorcentageSpinBox.value))
    self._parameterNode.SetParameter("plateTipsBevelRadius", str(self.ui.plateTipsBevelRadiusSpinBox.value))

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
    if self.ui.updateFibulaDentalImplantCylindersButton.checkState == qt.Qt.Checked:
      self._parameterNode.SetParameter("updateOnDentalImplantPlanesMovement","True")
    else:
      self._parameterNode.SetParameter("updateOnDentalImplantPlanesMovement","False")
    if self.ui.dentalImplantsPlanningAndFibulaDrillGuidesCheckBox.checked:
      self._parameterNode.SetParameter("dentalImplantsPlanningAndFibulaDrillGuides","True")
    else:
      self._parameterNode.SetParameter("dentalImplantsPlanningAndFibulaDrillGuides","False")
    if self.ui.customTitaniumPlateDesingCheckBox.checked:
      self._parameterNode.SetParameter("customTitaniumPlateDesing","True")
    else:
      self._parameterNode.SetParameter("customTitaniumPlateDesing","False")
    if self.ui.makeAllDentalImplanCylindersParallelCheckBox.checked:
      self._parameterNode.SetParameter("makeAllDentalImplanCylindersParallel","True")
    else:
      self._parameterNode.SetParameter("makeAllDentalImplanCylindersParallel","False")

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

  def onAddMandibularCurveButton(self):
    self.logic.addMandibularCurve()

  def onAddFibulaLineButton(self):
    self.logic.addFibulaLine()
    
  def onAddCutPlaneButton(self):
    self.logic.addCutPlane()

  def onMakeModelsButton(self):
    self.logic.makeModels()

  def onCreateMiterBoxesFromFibulaPlanesButton(self):
    self.logic.createMiterBoxesFromFibulaPlanes()

  def onCreateFibulaCylindersFiducialListButton(self):
    self.logic.createFibulaCylindersFiducialList()

  def onCreateCylindersFromFiducialListAndSurgicalGuideBaseButton(self):
    self.logic.createCylindersFromFiducialListAndFibulaSurgicalGuideBase()

  def onMakeBooleanOperationsToFibulaSurgicalGuideBaseButton(self):
    self.logic.makeBooleanOperationsToFibulaSurgicalGuideBase()

  def onCreateMandibleCylindersFiducialListButton(self):
    self.logic.createMandibleCylindersFiducialList()
  
  def onCreateDentalImplantCylindersFiducialListButton(self):
    self.logic.createDentalImplantCylindersFiducialList()

  def onCreateCylindersFromFiducialListAndNeomandiblePiecesButton(self):
    self.logic.createCylindersFromFiducialListAndNeomandiblePieces()

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

  def onUpdateFibulaDentalImplantCylindersButton(self):
    self.logic.onUpdateFibuladentalImplantsTimerTimeout()

  def onCreatePlateCurveButton(self):
    self.logic.createPlateCurve()

  def onCreateCustomPlateButton(self):
    self.logic.createCustomPlate()

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
    self.mandibleToFibulaRegistrationTransformMatricesList = []
    self.mandiblePlaneObserversAndNodeIDList = []
    self.sawBoxPlaneObserversPlaneNodeIDAndTransformIDList = []
    self.dentalImplantPlaneObserversPlaneNodeIDAndTransformIDList = []
    self.generateFibulaPlanesTimer = qt.QTimer()
    self.generateFibulaPlanesTimer.setInterval(300)
    self.generateFibulaPlanesTimer.setSingleShot(True)
    self.generateFibulaPlanesTimer.connect('timeout()', self.onGenerateFibulaPlanesTimerTimeout)
    self.updateFibuladentalImplantsTimer = qt.QTimer()
    self.updateFibuladentalImplantsTimer.setInterval(300)
    self.updateFibuladentalImplantsTimer.setSingleShot(True)
    self.updateFibuladentalImplantsTimer.connect('timeout()', self.onUpdateFibuladentalImplantsTimerTimeout)
    self.MANDIBLE_VIEW_SINGLETON_TAG = "1"
    self.FIBULA_VIEW_SINGLETON_TAG = "2"
    self.PLANE_SIDE_SIZE = 50.
    self.PLANE_GLYPH_SCALE = 2.5

    if not slicer.app.commandOptions().noMainWindow:
      self.addCustomLayout()

  def addCustomLayout(self):
    customLayout = f"""
      <layout type="vertical">
      <item>
        <layout type="horizontal">
        <item>
          <view class="vtkMRMLViewNode" singletontag="{self.MANDIBLE_VIEW_SINGLETON_TAG}">
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
        <view class="vtkMRMLViewNode" singletontag="{self.FIBULA_VIEW_SINGLETON_TAG}">
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
    if not parameterNode.GetParameter("scalarVolumeChangedThroughParameterNode"):
      parameterNode.SetParameter("scalarVolumeChangedThroughParameterNode","False")

  def getParentFolderItemID(self):
    shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    sceneItemID = shNode.GetSceneItemID()
    folderSubjectHierarchyID = shNode.GetItemByName("BoneReconstructionPlanner")
    if folderSubjectHierarchyID:
      return folderSubjectHierarchyID
    else:
      return shNode.CreateFolderItem(sceneItemID,"BoneReconstructionPlanner")

  def getMandibleReconstructionFolderItemID(self):
    shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    parentItemID = self.getParentFolderItemID()
    folderSubjectHierarchyID = shNode.GetItemByName("Mandible reconstruction")
    if folderSubjectHierarchyID:
      return folderSubjectHierarchyID
    else:
      return shNode.CreateFolderItem(parentItemID,"Mandible reconstruction")

  def getInverseMandibleReconstructionFolderItemID(self):
    shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    parentItemID = self.getParentFolderItemID()
    folderSubjectHierarchyID = shNode.GetItemByName("Inverse mandible reconstruction")
    if folderSubjectHierarchyID:
      return folderSubjectHierarchyID
    else:
      inverseMandibleReconstructionFolder = shNode.CreateFolderItem(parentItemID,"Inverse mandible reconstruction")
      pluginHandler = slicer.qSlicerSubjectHierarchyPluginHandler().instance()
      folderPlugin = pluginHandler.pluginByName("Folder")
      qt.QTimer.singleShot(0, lambda: folderPlugin.setDisplayVisibility(inverseMandibleReconstructionFolder, 0))
      return inverseMandibleReconstructionFolder

  def getDentalImplantsPlanningFolderItemID(self):
    shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    parentItemID = self.getParentFolderItemID()
    folderSubjectHierarchyID = shNode.GetItemByName("Dental Implants planning")
    if folderSubjectHierarchyID:
      return folderSubjectHierarchyID
    else:
      return shNode.CreateFolderItem(parentItemID,"Dental Implants planning")

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
    mandibleViewNode = slicer.mrmlScene.GetSingletonNode(self.MANDIBLE_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
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
    fibulaViewNode = slicer.mrmlScene.GetSingletonNode(self.FIBULA_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
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
    planeNode.SetSize(self.PLANE_SIDE_SIZE,self.PLANE_SIDE_SIZE)
    planeNode.SetPlaneType(slicer.vtkMRMLMarkupsPlaneNode.PlaneType3Points)

    aux = slicer.mrmlScene.GetNodeByID('vtkMRMLColorTableNodeFileMediumChartColors.txt')
    colorTable = aux.GetLookupTable()
    ind = colorIndex%8
    colorwithalpha = colorTable.GetTableValue(ind)
    color = [colorwithalpha[0],colorwithalpha[1],colorwithalpha[2]]

    #display node of the plane
    displayNode = planeNode.GetDisplayNode()
    displayNode.SetGlyphScale(self.PLANE_GLYPH_SCALE)
    displayNode.SetSelectedColor(color)
    displayNode.HandlesInteractiveOn()
    displayNode.RotationHandleVisibilityOn()
    displayNode.TranslationHandleVisibilityOn()
    displayNode.ScaleHandleVisibilityOff()

    mandibleViewNode = slicer.mrmlScene.GetSingletonNode(self.MANDIBLE_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
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

    self.reorderMandiblePlanes()
  
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

    if len(mandibularPlanesList) == 0:
      stopTime = time.time()
      logging.info('Processing completed in {0:.2f} seconds\n'.format(stopTime-startTime))
      return    
  
    self.removeMandiblePlaneObservers()

    self.reorderMandiblePlanes()

    if makeAllMandiblePlanesRotateTogetherChecked and mandiblePlanesPositioningForMaximumBoneContactChecked:
      self.mandiblePlanesPositioningForMaximumBoneContact()
      self.transformMandiblePlanesZRotationToBeTheSameAsInputPlane(mandiblePlaneOfRotation)
    elif mandiblePlanesPositioningForMaximumBoneContactChecked:
      self.mandiblePlanesPositioningForMaximumBoneContact()
    elif makeAllMandiblePlanesRotateTogetherChecked:
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
    mandiblePlanesTransformsFolder = shNode.CreateFolderItem(self.getMandibleReconstructionFolderItemID(),'Mandible Planes Transforms')

    if mandiblePlaneOfRotation == None:
      mandiblePlaneOfRotation = mandibularPlanesList[0]

    mandiblePlaneOfRotationMatrix = vtk.vtkMatrix4x4()
    mandiblePlaneOfRotation.GetObjectToWorldMatrix(mandiblePlaneOfRotationMatrix)
    mandiblePlaneOfRotationX = np.array([mandiblePlaneOfRotationMatrix.GetElement(0,0),mandiblePlaneOfRotationMatrix.GetElement(1,0),mandiblePlaneOfRotationMatrix.GetElement(2,0)])
    mandiblePlaneOfRotationY = np.array([mandiblePlaneOfRotationMatrix.GetElement(0,1),mandiblePlaneOfRotationMatrix.GetElement(1,1),mandiblePlaneOfRotationMatrix.GetElement(2,1)])
    mandiblePlaneOfRotationZ = np.array([mandiblePlaneOfRotationMatrix.GetElement(0,2),mandiblePlaneOfRotationMatrix.GetElement(1,2),mandiblePlaneOfRotationMatrix.GetElement(2,2)])
        
    for i in range(len(mandibularPlanesList)):
      if mandiblePlaneOfRotation.GetID() != mandibularPlanesList[i].GetID():
        mandiblePlaneMatrix = vtk.vtkMatrix4x4()
        mandibularPlanesList[i].GetObjectToWorldMatrix(mandiblePlaneMatrix)
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
        mandibularPlaneTransformationSuccess = mandibularPlanesList[i].HardenTransform()
        if not (mandibularPlaneTransformationSuccess):
          Exception('Hardening transforms was not successful')
        
        transformNodeItemID = shNode.GetItemByDataNode(transformNode)
        shNode.SetItemParent(transformNodeItemID, mandiblePlanesTransformsFolder)
      
    if mandiblePlanesTransformsFolder:
      shNode.RemoveItem(mandiblePlanesTransformsFolder)

  def setInteractiveHandlesVisibilityOfMarkups(self,markupsList,visibility):
    for i in range(len(markupsList)):
      displayNode = markupsList[i].GetDisplayNode()
      if visibility:
        displayNode.HandlesInteractiveOn()
      else:
        displayNode.HandlesInteractiveOff()

  def setMarkupsListLocked(self,markupsList,locked):
    for i in range(len(markupsList)):
      markupsList[i].SetLocked(locked)
  
  def addMandiblePlaneObservers(self):
    shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    mandibularPlanesFolder = shNode.GetItemByName("Mandibular planes")
    mandibularPlanesList = createListFromFolderID(mandibularPlanesFolder)

    for i in range(len(mandibularPlanesList)):
      observer = mandibularPlanesList[i].AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent,self.onPlaneModifiedTimer)
      self.mandiblePlaneObserversAndNodeIDList.append([observer,mandibularPlanesList[i].GetID()])

  def removeMandiblePlaneObservers(self):
    shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    mandibularPlanesFolder = shNode.GetItemByName("Mandibular planes")
    mandibularPlanesList = createListFromFolderID(mandibularPlanesFolder)

    if len(self.mandiblePlaneObserversAndNodeIDList) == 0:
      return

    for i in range(len(mandibularPlanesList)):
      mandiblePlane = slicer.mrmlScene.GetNodeByID(self.mandiblePlaneObserversAndNodeIDList[i][1])
      mandiblePlane.RemoveObserver(self.mandiblePlaneObserversAndNodeIDList[i][0])
    self.mandiblePlaneObserversAndNodeIDList = []

  def addSawBoxPlaneObservers(self):
    shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    sawBoxesPlanesFolder = shNode.GetItemByName("sawBoxes Planes")
    sawBoxesTransformsFolder = shNode.GetItemByName("sawBoxes Transforms")
    sawBoxesPlanesList = createListFromFolderID(sawBoxesPlanesFolder)
    sawBoxesTransformsList = createListFromFolderID(sawBoxesTransformsFolder)

    for i in range(len(sawBoxesPlanesList)):
      observer = sawBoxesPlanesList[i].AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent,self.onSawBoxPlaneMoved)
      self.sawBoxPlaneObserversPlaneNodeIDAndTransformIDList.append([observer,sawBoxesPlanesList[i].GetID(),sawBoxesTransformsList[i].GetID()])

  def removeSawBoxPlaneObservers(self):
    shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    sawBoxesPlanesFolder = shNode.GetItemByName("sawBoxes Planes")
    sawBoxesPlanesList = createListFromFolderID(sawBoxesPlanesFolder)
 
    if len(self.sawBoxPlaneObserversPlaneNodeIDAndTransformIDList) == 0:
      return

    for i in range(len(sawBoxesPlanesList)):
      sawBoxPlane = slicer.mrmlScene.GetNodeByID(self.sawBoxPlaneObserversPlaneNodeIDAndTransformIDList[i][1])
      sawBoxPlane.RemoveObserver(self.sawBoxPlaneObserversPlaneNodeIDAndTransformIDList[i][0])
    self.sawBoxPlaneObserversPlaneNodeIDAndTransformIDList = []

  def addDentalImplantsPlaneObservers(self):
    shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    dentalImplantsPlanesFolder = shNode.GetItemByName("dentalImplants Planes")
    dentalImplantsCylindersTransformsFolder = shNode.GetItemByName("Dental Implants Cylinders Transforms")
    dentalImplantsPlanesList = createListFromFolderID(dentalImplantsPlanesFolder)
    dentalImplantsCylindersTransformsList = createListFromFolderID(dentalImplantsCylindersTransformsFolder)

    for i in range(len(dentalImplantsPlanesList)):
      observer = dentalImplantsPlanesList[i].AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent,self.onDentalImplantPlaneMoved)
      self.dentalImplantPlaneObserversPlaneNodeIDAndTransformIDList.append([observer,dentalImplantsPlanesList[i].GetID(),dentalImplantsCylindersTransformsList[i].GetID()])

  def removeDentalImplantsPlaneObservers(self):
    shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    dentalImplantsPlanesFolder = shNode.GetItemByName("dentalImplants Planes")
    dentalImplantsPlanesList = createListFromFolderID(dentalImplantsPlanesFolder)
 
    if len(self.dentalImplantPlaneObserversPlaneNodeIDAndTransformIDList) == 0:
      return

    for i in range(len(dentalImplantsPlanesList)):
      dentalImplantsPlane = slicer.mrmlScene.GetNodeByID(self.dentalImplantPlaneObserversPlaneNodeIDAndTransformIDList[i][1])
      dentalImplantsPlane.RemoveObserver(self.dentalImplantPlaneObserversPlaneNodeIDAndTransformIDList[i][0])
    self.dentalImplantPlaneObserversPlaneNodeIDAndTransformIDList = []

  def transformFibulaPlanes(self):
    parameterNode = self.getParameterNode()
    fibulaLine = parameterNode.GetNodeReference("fibulaLine")
    initialSpace = float(parameterNode.GetParameter("initialSpace"))
    intersectionDistanceMultiplier = float(parameterNode.GetParameter("intersectionDistanceMultiplier"))
    additionalBetweenSpaceOfFibulaPlanes = float(parameterNode.GetParameter("additionalBetweenSpaceOfFibulaPlanes"))
    notLeftFibulaChecked = parameterNode.GetParameter("notLeftFibula") == "True"
    useMoreExactVersionOfPositioningAlgorithmChecked = parameterNode.GetParameter("useMoreExactVersionOfPositioningAlgorithm") == "True"
    fibulaModelNode = parameterNode.GetNodeReference("fibulaModelNode")
    planeList = createListFromFolderID(self.getMandiblePlanesFolderItemID())
    
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    fibulaPlanesFolder = shNode.GetItemByName("Fibula planes")
    fibulaPlanesList = createListFromFolderID(fibulaPlanesFolder)
    
    #Delete old fibulaPlanesTransforms
    mandible2FibulaTransformsFolder = shNode.GetItemByName("Mandible2Fibula transforms")
    if mandible2FibulaTransformsFolder:
      shNode.RemoveItem(mandible2FibulaTransformsFolder)
    mandible2FibulaTransformsFolder = shNode.CreateFolderItem(self.getMandibleReconstructionFolderItemID(),"Mandible2Fibula transforms")
    
    #Improve code readability by deleting if-else block that avoided recalculation if mandiblePlane rotated
    #Create fibula axis:
    fibulaX, fibulaY, fibulaZ, fibulaOrigin = self.createFibulaAxisFromFibulaLineAndNotLeftChecked(fibulaLine,notLeftFibulaChecked) 
    
    #NewPlanes position and distance
    self.fibulaPlanesPositionA = []
    self.fibulaPlanesPositionB = []
    boneSegmentsDistance = []

    #Set up transform for intersections to measure betweenSpace
    intersectionsFolder = shNode.CreateFolderItem(self.getMandibleReconstructionFolderItemID(),"Intersections")

    fibulaToRASRotationMatrix = self.getAxes1ToWorldRotationMatrix(fibulaX,fibulaY,fibulaZ)

    fibulaToRASRotationTransformNode = slicer.vtkMRMLLinearTransformNode()
    fibulaToRASRotationTransformNode.SetName("fibulaToRASRotationTransform")
    slicer.mrmlScene.AddNode(fibulaToRASRotationTransformNode)

    #rotation executed around fibulaOrigin
    fibulaToRASRotationTransform = vtk.vtkTransform()
    fibulaToRASRotationTransform.PostMultiply()
    fibulaToRASRotationTransform.Translate(-fibulaOrigin)
    fibulaToRASRotationTransform.Concatenate(fibulaToRASRotationMatrix)
    fibulaToRASRotationTransform.Translate(fibulaOrigin)

    fibulaToRASRotationTransformNode.SetMatrixTransformToParent(fibulaToRASRotationTransform.GetMatrix())
    fibulaToRASRotationTransformNode.UpdateScene(slicer.mrmlScene)

    fibulaToRASRotationTransformNodeItemID = shNode.GetItemByDataNode(fibulaToRASRotationTransformNode)
    shNode.SetItemParent(fibulaToRASRotationTransformNodeItemID, intersectionsFolder)

    intersectionsList = []
    j=0

    self.mandibleToFibulaRegistrationTransformMatricesList = []
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
      mandiblePlane0Origin = np.zeros(3)
      mandiblePlane0.GetOrigin(mandiblePlane0Origin)
      mandiblePlane1Origin = np.zeros(3)
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
      mandiblePlane0.GetObjectToWorldMatrix(mandiblePlane0matrix)
      mandiblePlane0Y = np.array([mandiblePlane0matrix.GetElement(0,1),mandiblePlane0matrix.GetElement(1,1),mandiblePlane0matrix.GetElement(2,1)])
      
      mandibleAxisX = [0,0,0]
      vtk.vtkMath.Cross(mandiblePlane0Y, mandibleAxisZ, mandibleAxisX)
      mandibleAxisX = mandibleAxisX/np.linalg.norm(mandibleAxisX)
      mandibleAxisY = [0,0,0]
      vtk.vtkMath.Cross(mandibleAxisZ, mandibleAxisX, mandibleAxisY)
      mandibleAxisY = mandibleAxisY/np.linalg.norm(mandibleAxisY)

      #Create fibula axis:
      fibulaX, fibulaY, fibulaZ, fibulaOrigin = self.createFibulaAxisFromFibulaLineAndNotLeftChecked(fibulaLine,notLeftFibulaChecked) 
      
      if i==0:
        self.fibulaPlanesPositionA.append(fibulaOrigin + fibulaZ*initialSpace)
        self.fibulaPlanesPositionB.append(self.fibulaPlanesPositionA[i] + boneSegmentsDistance[i]*fibulaZ)

        intersectionModelB = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Intersection%d_B' % i)
        intersectionModelB.CreateDefaultDisplayNodes()

        afterMandibleToWorldChangeOfFrameMatrix = self.getAxes1ToWorldChangeOfFrameMatrix(mandibleAxisX, mandibleAxisY, mandibleAxisZ, mandiblePlane1Origin)
        afterFibulaToWorldChangeOfFrameMatrix = self.getAxes1ToWorldChangeOfFrameMatrix(fibulaX, fibulaY, fibulaZ, self.fibulaPlanesPositionB[i])

        afterMandibleToAfterFibulaRegistrationTransformMatrix = self.getAxes1ToAxes2RegistrationTransformMatrix(afterMandibleToWorldChangeOfFrameMatrix,afterFibulaToWorldChangeOfFrameMatrix)

        getIntersectionBetweenModelAnd1TransformedPlane(fibulaModelNode, afterMandibleToAfterFibulaRegistrationTransformMatrix, mandiblePlane1, intersectionModelB)
        intersectionsList.append(intersectionModelB)
        intersectionsList[j].SetAndObserveTransformNodeID(fibulaToRASRotationTransformNode.GetID())
        intersectionsList[j].HardenTransform()
        intersectionModelBItemID = shNode.GetItemByDataNode(intersectionModelB)
        shNode.SetItemParent(intersectionModelBItemID, intersectionsFolder)
        j += 1

      else:
        boundsB = [0,0,0,0,0,0]
        boundsA = [0,0,0,0,0,0]

        intersectionModelA = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Intersection%d_A' % i)
        intersectionModelA.CreateDefaultDisplayNodes()

        beforeMandibleToWorldChangeOfFrameMatrix = self.getAxes1ToWorldChangeOfFrameMatrix(mandibleAxisX, mandibleAxisY, mandibleAxisZ, mandiblePlane0Origin)
        beforeFibulaToWorldChangeOfFrameMatrix = self.getAxes1ToWorldChangeOfFrameMatrix(fibulaX, fibulaY, fibulaZ, self.fibulaPlanesPositionB[i-1])

        beforeMandibleToBeforeFibulaRegistrationTransformMatrix = self.getAxes1ToAxes2RegistrationTransformMatrix(beforeMandibleToWorldChangeOfFrameMatrix,beforeFibulaToWorldChangeOfFrameMatrix)

        getIntersectionBetweenModelAnd1TransformedPlane(fibulaModelNode, beforeMandibleToBeforeFibulaRegistrationTransformMatrix, mandiblePlane0, intersectionModelA)
        intersectionsList.append(intersectionModelA)
        intersectionModelAItemID = shNode.GetItemByDataNode(intersectionModelA)
        shNode.SetItemParent(intersectionModelAItemID, intersectionsFolder)
        intersectionsList[j].SetAndObserveTransformNodeID(fibulaToRASRotationTransformNode.GetID())
        intersectionsList[j].HardenTransform()
        j += 1

        intersectionsList[j-2].GetBounds(boundsB)
        intersectionsList[(j-2)+1].GetBounds(boundsA)

        #calculate how much each FibulaPlaneA should be translated so that it doesn't intersect with fibulaPlaneB
        zBSup = boundsB[5]
        zAInf = boundsA[4]
        deltaZ = zBSup - zAInf

        self.fibulaPlanesPositionA.append(self.fibulaPlanesPositionB[i-1] + fibulaZ*(intersectionDistanceMultiplier*deltaZ + additionalBetweenSpaceOfFibulaPlanes))
        self.fibulaPlanesPositionB.append(self.fibulaPlanesPositionA[i] + boneSegmentsDistance[i]*fibulaZ)

        if i!=(len(planeList)-2):
          afterMandibleToWorldChangeOfFrameMatrix = self.getAxes1ToWorldChangeOfFrameMatrix(mandibleAxisX, mandibleAxisY, mandibleAxisZ, mandiblePlane1Origin)
          afterFibulaToWorldChangeOfFrameMatrix = self.getAxes1ToWorldChangeOfFrameMatrix(fibulaX, fibulaY, fibulaZ, self.fibulaPlanesPositionB[i])

          afterMandibleToAfterFibulaRegistrationTransformMatrix = self.getAxes1ToAxes2RegistrationTransformMatrix(afterMandibleToWorldChangeOfFrameMatrix,afterFibulaToWorldChangeOfFrameMatrix)

          intersectionModelB = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Intersection%d_B' % i)
          intersectionModelB.CreateDefaultDisplayNodes()
          getIntersectionBetweenModelAnd1TransformedPlane(fibulaModelNode, afterMandibleToAfterFibulaRegistrationTransformMatrix, mandiblePlane1, intersectionModelB)
          intersectionsList.append(intersectionModelB)
          intersectionModelBItemID = shNode.GetItemByDataNode(intersectionModelB)
          shNode.SetItemParent(intersectionModelBItemID, intersectionsFolder)
          intersectionsList[j].SetAndObserveTransformNodeID(fibulaToRASRotationTransformNode.GetID())
          intersectionsList[j].HardenTransform()
          j += 1

      if useMoreExactVersionOfPositioningAlgorithmChecked:
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
        
        self.fibulaPlanesPositionA.append(lineStartPos)
        self.fibulaPlanesPositionB.append(lineEndPos)

        if intersectionsForCentroidCalculationFolder:
          shNode.RemoveItem(intersectionsForCentroidCalculationFolder)

      mandibleToFibulaRegistrationTransformNode = slicer.vtkMRMLLinearTransformNode()
      mandibleToFibulaRegistrationTransformNode.SetName("Mandible2Fibula Registration Transform%d" % i)
      slicer.mrmlScene.AddNode(mandibleToFibulaRegistrationTransformNode)

      mandibleToWorldChangeOfFrameMatrix = self.getAxes1ToWorldChangeOfFrameMatrix(mandibleAxisX, mandibleAxisY, mandibleAxisZ, (mandiblePlane0Origin + mandiblePlane1Origin)/2)
      fibulaToWorldChangeOfFrameMatrix = self.getAxes1ToWorldChangeOfFrameMatrix(fibulaX, fibulaY, fibulaZ, (self.fibulaPlanesPositionA[i] + self.fibulaPlanesPositionB[i])/2)
      
      mandibleToFibulaRegistrationTransformMatrix = self.getAxes1ToAxes2RegistrationTransformMatrix(mandibleToWorldChangeOfFrameMatrix,fibulaToWorldChangeOfFrameMatrix)

      self.mandibleToFibulaRegistrationTransformMatricesList.append(mandibleToFibulaRegistrationTransformMatrix)

      mandibleToFibulaRegistrationTransformNode.SetMatrixTransformToParent(mandibleToFibulaRegistrationTransformMatrix)
      mandibleToFibulaRegistrationTransformNode.UpdateScene(slicer.mrmlScene)

      fibulaPlaneA.SetAndObserveTransformNodeID(mandibleToFibulaRegistrationTransformNode.GetID())
      fibulaPlaneB.SetAndObserveTransformNodeID(mandibleToFibulaRegistrationTransformNode.GetID())
      fibulaPlaneA.HardenTransform()
      fibulaPlaneB.HardenTransform()

      mandibleToFibulaRegistrationTransformNodeItemID = shNode.GetItemByDataNode(mandibleToFibulaRegistrationTransformNode)
      shNode.SetItemParent(mandibleToFibulaRegistrationTransformNodeItemID, mandible2FibulaTransformsFolder)
      
    if intersectionsFolder:
      shNode.RemoveItem(intersectionsFolder)

    #Create measurement lines
    self.createFibulaSegmentsLengthsLines(self.fibulaPlanesPositionA,self.fibulaPlanesPositionB)
  
  def createFibulaSegmentsLengthsLines(self,fibulaPlanesAPosition,fibulaPlanesBPosition):
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    fibulaSegmentsLengthsFolder = shNode.GetItemByName("Fibula Segments Lengths")
    if fibulaSegmentsLengthsFolder:
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
      fibulaViewNode = slicer.mrmlScene.GetSingletonNode(self.FIBULA_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
      displayNode.AddViewNodeID(fibulaViewNode.GetID())
      displayNode.SetOccludedVisibility(True)
      
      lineNode.AddControlPoint(vtk.vtkVector3d(fibulaPlanesAPosition[i]))
      lineNode.AddControlPoint(vtk.vtkVector3d(fibulaPlanesBPosition[i]))

      lineNode.SetLocked(True)
  
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
      fibulaPlaneA.SetSize(self.PLANE_SIDE_SIZE,self.PLANE_SIDE_SIZE)
      fibulaPlaneA.SetPlaneType(slicer.vtkMRMLMarkupsPlaneNode.PlaneType3Points)

      displayNode = fibulaPlaneA.GetDisplayNode()
      fibulaViewNode = slicer.mrmlScene.GetSingletonNode(self.FIBULA_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
      displayNode.AddViewNodeID(fibulaViewNode.GetID())
      displayNode.SetPropertiesLabelVisibility(False)
      displayNode.HandlesInteractiveOff()

      fibulaPlaneAItemID = shNode.GetItemByDataNode(fibulaPlaneA)
      shNode.SetItemParent(fibulaPlaneAItemID, fibulaPlanesFolder)

      fibulaPlaneA.SetAxes(mandiblePlane0X,mandiblePlane0Y,mandiblePlane0Z)
      fibulaPlaneA.SetOrigin(mandiblePlane0Origin)
      fibulaPlaneA.SetLocked(True)
      fibulaPlanesList.append(fibulaPlaneA)


      fibulaPlaneB = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsPlaneNode", "FibulaPlane%d_B" % i)
      slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(fibulaPlaneB)
      fibulaPlaneB.SetSize(self.PLANE_SIDE_SIZE,self.PLANE_SIDE_SIZE)
      fibulaPlaneB.SetPlaneType(slicer.vtkMRMLMarkupsPlaneNode.PlaneType3Points)

      displayNode = fibulaPlaneB.GetDisplayNode()
      displayNode.AddViewNodeID(fibulaViewNode.GetID())
      displayNode.SetPropertiesLabelVisibility(False)
      displayNode.HandlesInteractiveOff()

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
        newPlanes[j].SetNthControlPointPosition(1,on1+xd1*xnpv1)
        newPlanes[j].SetNthControlPointPosition(2,on1+yd1*ynpv1)

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
      decimatedFibulaModelDisplayNode = decimatedFibulaModelNode.GetDisplayNode()
      nonDecimatedFibulaModelDisplayNode.SetVisibility(True)
      decimatedFibulaModelDisplayNode.SetVisibility(False)

      nonDecimatedMandibleModelDisplayNode =  nonDecimatedMandibleModelNode.GetDisplayNode()
      decimatedMandibleModelDisplayNode = decimatedFibulaModelNode.GetDisplayNode()
      previousMandibleModelVisibility = (
        nonDecimatedMandibleModelDisplayNode.GetVisibility() or
        decimatedMandibleModelDisplayNode.GetVisibility()
      )
      nonDecimatedMandibleModelDisplayNode.SetVisibility(True and previousMandibleModelVisibility)
      decimatedMandibleModelDisplayNode.SetVisibility(False)

      fibulaModelNode = nonDecimatedFibulaModelNode
      mandibleModelNode = nonDecimatedMandibleModelNode
    else:
      nonDecimatedFibulaModelDisplayNode = nonDecimatedFibulaModelNode.GetDisplayNode()
      decimatedFibulaModelDisplayNode = decimatedFibulaModelNode.GetDisplayNode()
      nonDecimatedFibulaModelDisplayNode.SetVisibility(False)
      decimatedFibulaModelDisplayNode.SetVisibility(True)

      nonDecimatedMandibleModelDisplayNode =  nonDecimatedMandibleModelNode.GetDisplayNode()
      decimatedMandibleModelDisplayNode = decimatedFibulaModelNode.GetDisplayNode()
      previousMandibleModelVisibility = (
        nonDecimatedMandibleModelDisplayNode.GetVisibility() or
        decimatedMandibleModelDisplayNode.GetVisibility()
      )
      nonDecimatedMandibleModelDisplayNode.SetVisibility(False)
      decimatedMandibleModelDisplayNode.SetVisibility(True and previousMandibleModelVisibility)

      fibulaModelNode = decimatedFibulaModelNode
      mandibleModelNode = decimatedMandibleModelNode

    planeCutsFolder = shNode.GetItemByName("Plane Cuts")
    if planeCutsFolder == 0 or fixCutGoesThroughTheMandibleTwiceCheckBoxChanged:
      if planeCutsFolder:
        shNode.RemoveItem(planeCutsFolder)
      cutBonesFolder = shNode.GetItemByName("Cut Bones")
      if cutBonesFolder:
        shNode.RemoveItem(cutBonesFolder)
      planeCutsFolder = shNode.CreateFolderItem(self.getMandibleReconstructionFolderItemID(),"Plane Cuts")
      cutBonesFolder = shNode.CreateFolderItem(self.getMandibleReconstructionFolderItemID(),"Cut Bones")

      for i in range(0,len(fibulaPlanesList),2):
        modelNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLModelNode")
        modelNode.SetName("Fibula Segment {0}A-{1}B".format(i//2,i//2))
        slicer.mrmlScene.AddNode(modelNode)
        modelNode.CreateDefaultDisplayNodes()
        modelDisplayNode = modelNode.GetDisplayNode()
        modelDisplayNode.SetVisibility2D(True)

        fibulaViewNode = slicer.mrmlScene.GetSingletonNode(self.FIBULA_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
        modelDisplayNode.AddViewNodeID(fibulaViewNode.GetID())

        #Set color of the model
        aux = slicer.mrmlScene.GetNodeByID('vtkMRMLColorTableNodeFileMediumChartColors.txt')
        colorTable = aux.GetLookupTable()
        nColors = colorTable.GetNumberOfColors()
        ind = int((nColors-1) - i/2)
        colorwithalpha = colorTable.GetTableValue(ind)
        color = [colorwithalpha[0],colorwithalpha[1],colorwithalpha[2]]
        modelDisplayNode.SetColor(color)

        dynamicModelerNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLDynamicModelerNode")
        dynamicModelerNode.SetToolName("Plane cut")
        dynamicModelerNode.SetNodeReferenceID("PlaneCut.InputModel", fibulaModelNode.GetID())
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
      modelDisplayNode.SetVisibility2D(True)

      mandibleViewNode = slicer.mrmlScene.GetSingletonNode(self.MANDIBLE_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
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
        shNode.SetItemParent(planeToFixCutGoesThroughTheMandibleTwiceItemID, self.getMandibleReconstructionFolderItemID())
        parameterNode.SetNodeReferenceID("planeToFixCutGoesThroughTheMandibleTwice",planeToFixCutGoesThroughTheMandibleTwice.GetID())

        displayNode = planeToFixCutGoesThroughTheMandibleTwice.GetDisplayNode()
        displayNode.SetVisibility(False)
        displayNode.HandlesInteractiveOff()

        planeOriginStart = np.zeros(3)
        planeOriginEnd = np.zeros(3)
        planeList[0].GetNthControlPointPosition(0,planeOriginStart)
        planeList[len(planeList)-1].GetNthControlPointPosition(0,planeOriginEnd)

        rightDirection = np.array([1.,0.,0.])
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
          dynamicModelerNodesList[i].RemoveNodeReferenceIDs("PlaneCut.InputPlane")
          dynamicModelerNodesList[i].AddNodeReferenceID("PlaneCut.InputPlane", planeList[len(planeList)-1].GetID())
          dynamicModelerNodesList[i].AddNodeReferenceID("PlaneCut.InputPlane", planeList[0].GetID()) 


    inversePlaneCutsFolder = shNode.GetItemByName("Inverse Plane Cuts")
    inverseAppendFolder = shNode.GetItemByName("Inverse Append")
    inversePlaneCutsList = createListFromFolderID(inversePlaneCutsFolder)
    inverseAppendList = createListFromFolderID(inverseAppendFolder)
    numberOfFibulaPieces = len(createListFromFolderID(planeCutsFolder)) -1
    if (
      (inversePlaneCutsFolder == 0) or 
      (inverseAppendFolder == 0) or
      (len(inversePlaneCutsList) != numberOfFibulaPieces) or
      (len(inverseAppendList) != numberOfFibulaPieces)
      ):
      if inversePlaneCutsFolder:
        shNode.RemoveItem(inversePlaneCutsFolder)
      if inverseAppendFolder:
        shNode.RemoveItem(inverseAppendFolder)
      cutMandiblePiecesFolder = shNode.GetItemByName("Cut Mandible Pieces")
      if cutMandiblePiecesFolder:
        shNode.RemoveItem(cutMandiblePiecesFolder)
      fullMandiblesFolder = shNode.GetItemByName("Full Mandibles")
      if fullMandiblesFolder:
        shNode.RemoveItem(fullMandiblesFolder)
      inversePlaneCutsFolder = shNode.CreateFolderItem(self.getInverseMandibleReconstructionFolderItemID(),"Inverse Plane Cuts")
      inverseAppendFolder = shNode.CreateFolderItem(self.getInverseMandibleReconstructionFolderItemID(),"Inverse Append")
      cutMandiblePiecesFolder = shNode.CreateFolderItem(self.getInverseMandibleReconstructionFolderItemID(),"Cut Mandible Pieces")
      fullMandiblesFolder = shNode.CreateFolderItem(self.getInverseMandibleReconstructionFolderItemID(),"Full Mandibles")

      pluginHandler = slicer.qSlicerSubjectHierarchyPluginHandler().instance()
      folderPlugin = pluginHandler.pluginByName("Folder")
      qt.QTimer.singleShot(0, lambda: folderPlugin.setDisplayVisibility(fullMandiblesFolder, 0))

      for i in range(len(planeList)-1):
        modelNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLModelNode")
        modelNode.SetName("Mandible Segment {0}".format(i))
        slicer.mrmlScene.AddNode(modelNode)
        modelNode.CreateDefaultDisplayNodes()
        modelDisplayNode = modelNode.GetDisplayNode()
        modelDisplayNode.SetVisibility2D(True)

        fullModelNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLModelNode")
        fullModelNode.SetName("Mandible {0}".format(i))
        slicer.mrmlScene.AddNode(fullModelNode)
        fullModelNode.CreateDefaultDisplayNodes()
        fullModelDisplayNode = fullModelNode.GetDisplayNode()
        fullModelDisplayNode.SetVisibility2D(True)

        mandibleViewNode = slicer.mrmlScene.GetSingletonNode(self.MANDIBLE_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
        modelDisplayNode.AddViewNodeID(mandibleViewNode.GetID())
        fullModelDisplayNode.AddViewNodeID(mandibleViewNode.GetID())

        #Set color of the model
        aux = slicer.mrmlScene.GetNodeByID('vtkMRMLColorTableNodeFileMediumChartColors.txt')
        colorTable = aux.GetLookupTable()
        nColors = colorTable.GetNumberOfColors()
        ind = int((nColors-1) - i)
        colorwithalpha = colorTable.GetTableValue(ind)
        color = [colorwithalpha[0],colorwithalpha[1],colorwithalpha[2]]
        modelDisplayNode.SetColor(color)
        fullModelDisplayNode.SetColor(color)

        dynamicModelerNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLDynamicModelerNode")
        dynamicModelerNode.SetToolName("Plane cut")
        dynamicModelerNode.SetNodeReferenceID("PlaneCut.InputModel", mandibleModelNode.GetID())
        dynamicModelerNode.AddNodeReferenceID("PlaneCut.InputPlane", planeList[i+1].GetID())
        dynamicModelerNode.AddNodeReferenceID("PlaneCut.InputPlane", planeList[i].GetID()) 
        dynamicModelerNode.SetNodeReferenceID("PlaneCut.OutputNegativeModel", modelNode.GetID())
        dynamicModelerNode.SetAttribute("OperationType", "Difference")
        #slicer.modules.dynamicmodeler.logic().RunDynamicModelerTool(dynamicModelerNode)
        
        dynamicModelerNode2 = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLDynamicModelerNode")
        dynamicModelerNode2.SetToolName("Append")
        dynamicModelerNode2.SetNodeReferenceID("Append.InputModel", mandibleModelNode.GetID())
        dynamicModelerNode2.SetNodeReferenceID("Append.OutputModel", fullModelNode.GetID())

        dynamicModelerNodeItemID = shNode.GetItemByDataNode(dynamicModelerNode)
        shNode.SetItemParent(dynamicModelerNodeItemID, inversePlaneCutsFolder)

        dynamicModelerNode2ItemID = shNode.GetItemByDataNode(dynamicModelerNode2)
        shNode.SetItemParent(dynamicModelerNode2ItemID, inverseAppendFolder)

        modelNodeItemID = shNode.GetItemByDataNode(modelNode)
        shNode.SetItemParent(modelNodeItemID, cutMandiblePiecesFolder)

        fullModelNodeItemID = shNode.GetItemByDataNode(fullModelNode)
        shNode.SetItemParent(fullModelNodeItemID, fullMandiblesFolder)
        
    
    else:
      dynamicModelerNodesList = createListFromFolderID(inversePlaneCutsFolder)
      for i in range(len(dynamicModelerNodesList)):
        dynamicModelerNodesList[i].SetNodeReferenceID("PlaneCut.InputModel", mandibleModelNode.GetID())

      dynamicModelerNodesList = createListFromFolderID(inverseAppendFolder)
      for i in range(len(dynamicModelerNodesList)):
        dynamicModelerNodesList[i].SetNodeReferenceID("Append.InputModel", mandibleModelNode.GetID())


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
      if fibulaPlanesFolder:
        shNode.RemoveItem(fibulaPlanesFolder)
      planeCutsFolder = shNode.GetItemByName("Plane Cuts")
      if planeCutsFolder:
        shNode.RemoveItem(planeCutsFolder)
      cutBonesFolder = shNode.GetItemByName("Cut Bones")
      if cutBonesFolder:
        shNode.RemoveItem(cutBonesFolder)
      transformedFibulaPiecesFolder = shNode.GetItemByName("Transformed Fibula Pieces")
      if transformedFibulaPiecesFolder:
        shNode.RemoveItem(transformedFibulaPiecesFolder)
      mandibleDisplayNode = mandibleModelNode.GetDisplayNode()
      mandibleDisplayNode.SetVisibility(True)
      return

    fibulaPlanesFolder = shNode.GetItemByName("Fibula planes")
    fibulaPlanesList = createListFromFolderID(fibulaPlanesFolder)

    #delete all the folders that are not updated
    if (len(fibulaPlanesList) != (2*len(planeList) - 2)) or not fibulaPlanesFolder:
      if fibulaPlanesFolder:
        shNode.RemoveItem(fibulaPlanesFolder)
      planeCutsFolder = shNode.GetItemByName("Plane Cuts")
      if planeCutsFolder:
        shNode.RemoveItem(planeCutsFolder)
      cutBonesFolder = shNode.GetItemByName("Cut Bones")
      if cutBonesFolder:
        shNode.RemoveItem(cutBonesFolder)
      transformedFibulaPiecesFolder = shNode.GetItemByName("Transformed Fibula Pieces")
      if transformedFibulaPiecesFolder:
        shNode.RemoveItem(transformedFibulaPiecesFolder)
      fibulaPlanesFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Fibula planes")
      fibulaPlanesList = createListFromFolderID(fibulaPlanesFolder)
      #Create fibula planes and set their size
      self.createFibulaPlanesFromMandiblePlanesAndFibulaAxis(planeList,fibulaPlanesList)

    self.transformFibulaPlanes()

    self.createAndUpdateDynamicModelerNodes()
  
    self.updateFibulaPieces()

    self.updateInverseMandiblePieces()

    self.tranformFibulaPiecesToMandible()

    self.tranformMandiblePiecesToFibula()

    self.setRedSliceForBoneModelsDisplayNodes()

  def reorderMandiblePlanes(self):
    mandibularPlanesFolder = self.getMandiblePlanesFolderItemID()
    planeList = createListFromFolderID(mandibularPlanesFolder)
    parameterNode = self.getParameterNode()
    mandibularCurve = parameterNode.GetNodeReference("mandibleCurve")

    if len(planeList) < 2:
      return
    
    reverseOrder = False
    mandiblePlanesIndicesList = []
    if len(planeList) == 2:
      #Determinate plane creation direction and set up dynamic modeler
      planeOriginStart = np.zeros(3)
      planeOriginEnd = np.zeros(3)
      planeList[0].GetNthControlPointPosition(0,planeOriginStart)
      planeList[1].GetNthControlPointPosition(0,planeOriginEnd)
      closestCurvePointStart = [0,0,0]
      closestCurvePointEnd = [0,0,0]
      closestCurvePointIndexStart = mandibularCurve.GetClosestPointPositionAlongCurveWorld(planeOriginStart,closestCurvePointStart)
      closestCurvePointIndexEnd = mandibularCurve.GetClosestPointPositionAlongCurveWorld(planeOriginEnd,closestCurvePointEnd)
      mandiblePlanesIndicesList.append([
        planeList[0],
        closestCurvePointIndexStart
      ])
      mandiblePlanesIndicesList.append([
        planeList[1],
        closestCurvePointIndexEnd
      ])
    else:
      #there are n mandible planes
      originsList = []
      mandiblePlanesIndicesList = []
      for i in range(len(planeList)):
        planeOrigin = np.zeros(3)
        planeList[i].GetNthControlPointPosition(0,planeOrigin)
        originsList.append(planeOrigin)
        closestCurvePoint = [0,0,0]
        closestCurvePointIndex = mandibularCurve.GetClosestPointPositionAlongCurveWorld(
          planeOrigin,closestCurvePoint
        )
        mandiblePlanesIndicesList.append([
          planeList[i],
          closestCurvePointIndex
        ])

      normalOfPoints = getBestFittingPlaneNormalFromPoints(
        np.array(
            originsList
        )
      )

      curvePoints = slicer.util.arrayFromMarkupsCurvePoints(mandibularCurve)
      bestFittingPlaneNormalOfCurvePoints = getBestFittingPlaneNormalFromPoints(curvePoints)
      
      reverseOrder = vtk.vtkMath.Dot(normalOfPoints,bestFittingPlaneNormalOfCurvePoints) < 0

      mandiblePlanesIndicesList.sort(key=lambda item: item[1], reverse=reverseOrder)

    #print(mandiblePlanesIndicesList)

    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    mandibularPlanesFolder2 = shNode.CreateFolderItem(self.getParentFolderItemID(),"Mandibular planes 2")

    for i in range(len(mandiblePlanesIndicesList)):
      mandiblePlane = mandiblePlanesIndicesList[i][0]
      mandiblePlaneItemID = shNode.GetItemByDataNode(mandiblePlane)
      shNode.SetItemParent(mandiblePlaneItemID, mandibularPlanesFolder2)

    if mandibularPlanesFolder:
      shNode.RemoveItem(mandibularPlanesFolder)
    shNode.SetItemName(mandibularPlanesFolder2,"Mandibular planes")

  def setRedSliceForBoneModelsDisplayNodes(self):
    parameterNode = self.getParameterNode()
    scalarVolume = parameterNode.GetNodeReference("currentScalarVolume")
    fibulaCentroidX = parameterNode.GetParameter("fibulaCentroidX")
    fibulaCentroidY = parameterNode.GetParameter("fibulaCentroidY")
    fibulaCentroidZ = parameterNode.GetParameter("fibulaCentroidZ")
    mandibleCentroidX = parameterNode.GetParameter("mandibleCentroidX")
    mandibleCentroidY = parameterNode.GetParameter("mandibleCentroidY")
    mandibleCentroidZ = parameterNode.GetParameter("mandibleCentroidZ")
    
    if fibulaCentroidX == "":
      return

    fibulaCentroid = np.array([float(fibulaCentroidX),float(fibulaCentroidY),float(fibulaCentroidZ)])
    mandibleCentroid = np.array([float(mandibleCentroidX),float(mandibleCentroidY),float(mandibleCentroidZ)])

    bounds = [0,0,0,0,0,0]
    scalarVolume.GetBounds(bounds)
    bounds = np.array(bounds)
    centerOfScalarVolume = np.array([(bounds[0]+bounds[1])/2,(bounds[2]+bounds[3])/2,(bounds[4]+bounds[5])/2])
    
    shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    cutBonesFolder = shNode.GetItemByName("Cut Bones")
    transformedFibulaPiecesFolder = shNode.GetItemByName("Transformed Fibula Pieces")
    cutMandiblePiecesFolder = shNode.GetItemByName("Cut Mandible Pieces")
    transformedMandiblePiecesFolder = shNode.GetItemByName("Transformed Mandible Pieces")
    transformedFullMandiblesFolder = shNode.GetItemByName("Transformed Full Mandible")
    cutBonesList = createListFromFolderID(cutBonesFolder)
    transformedFibulaPiecesList = createListFromFolderID(transformedFibulaPiecesFolder)
    transformedMandiblePiecesList = createListFromFolderID(transformedMandiblePiecesFolder)
    transformedFullMandiblesList = createListFromFolderID(transformedFullMandiblesFolder)
    cutMandiblePiecesList = createListFromFolderID(cutMandiblePiecesFolder)
    redSliceNode = slicer.mrmlScene.GetSingletonNode("Red", "vtkMRMLSliceNode")

    if np.linalg.norm(fibulaCentroid-centerOfScalarVolume) < np.linalg.norm(mandibleCentroid-centerOfScalarVolume):
      #When fibulaScalarVolume:
      addIterationList = cutBonesList[0:-1] + transformedMandiblePiecesList + transformedFullMandiblesList
      removeIterationList = cutBonesList[-1:] + transformedFibulaPiecesList + cutMandiblePiecesList
      
    else:
      #When mandibleScalarVolume:
      addIterationList = cutBonesList[-1:] + transformedFibulaPiecesList + cutMandiblePiecesList
      removeIterationList = cutBonesList[0:-1] + transformedMandiblePiecesList + transformedFullMandiblesList
    
    for i in range(len(removeIterationList)):
      displayNode = removeIterationList[i].GetDisplayNode()
      displayNode.RemoveViewNodeID(redSliceNode.GetID())

    for i in range(len(addIterationList)):
      displayNode = addIterationList[i].GetDisplayNode()
      displayNode.AddViewNodeID(redSliceNode.GetID())
  
  def setRedSliceForBoxModelsDisplayNodes(self):
    parameterNode = self.getParameterNode()
    scalarVolume = parameterNode.GetNodeReference("currentScalarVolume")
    fibulaCentroidX = parameterNode.GetParameter("fibulaCentroidX")
    fibulaCentroidY = parameterNode.GetParameter("fibulaCentroidY")
    fibulaCentroidZ = parameterNode.GetParameter("fibulaCentroidZ")
    mandibleCentroidX = parameterNode.GetParameter("mandibleCentroidX")
    mandibleCentroidY = parameterNode.GetParameter("mandibleCentroidY")
    mandibleCentroidZ = parameterNode.GetParameter("mandibleCentroidZ")
    
    if fibulaCentroidX == "":
      return

    fibulaCentroid = np.array([float(fibulaCentroidX),float(fibulaCentroidY),float(fibulaCentroidZ)])
    mandibleCentroid = np.array([float(mandibleCentroidX),float(mandibleCentroidY),float(mandibleCentroidZ)])

    bounds = [0,0,0,0,0,0]
    scalarVolume.GetBounds(bounds)
    bounds = np.array(bounds)
    centerOfScalarVolume = np.array([(bounds[0]+bounds[1])/2,(bounds[2]+bounds[3])/2,(bounds[4]+bounds[5])/2])
    
    shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    biggerMiterBoxesFolder = shNode.GetItemByName("biggerMiterBoxes Models")
    biggerSawBoxesModelsFolder = shNode.GetItemByName("biggerSawBoxes Models")
    biggerSawBoxesModelsList = createListFromFolderID(biggerSawBoxesModelsFolder)
    biggerMiterBoxesList = createListFromFolderID(biggerMiterBoxesFolder)
    redSliceNode = slicer.mrmlScene.GetSingletonNode("Red", "vtkMRMLSliceNode")

   
    if np.linalg.norm(fibulaCentroid-centerOfScalarVolume) < np.linalg.norm(mandibleCentroid-centerOfScalarVolume):
      #When fibulaScalarVolume:
      addIterationList = biggerMiterBoxesList
      removeIterationList = biggerSawBoxesModelsList
    else:
      #When mandibleScalarVolume:
      addIterationList = biggerSawBoxesModelsList
      removeIterationList = biggerMiterBoxesList
      
    for i in range(len(removeIterationList)):
      displayNode = removeIterationList[i].GetDisplayNode()
      displayNode.RemoveViewNodeID(redSliceNode.GetID())

    for i in range(len(addIterationList)):
      displayNode = addIterationList[i].GetDisplayNode()
      displayNode.AddViewNodeID(redSliceNode.GetID())

  def getAxes1ToWorldRotationMatrix(self,axis1X,axis1Y,axis1Z):
    "rotationMatrix is the transpose of a non-translation changeOfFrameMatrix"
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
  
  def getAxes1ToWorldChangeOfFrameMatrix(self,axis1X,axis1Y,axis1Z,axisOrigin):
    axes1ToWorldChangeOfFrameMatrix = vtk.vtkMatrix4x4()
    axes1ToWorldChangeOfFrameMatrix.DeepCopy((1, 0, 0, 0,
                                          0, 1, 0, 0,
                                          0, 0, 1, 0,
                                          0, 0, 0, 1))
    axes1ToWorldChangeOfFrameMatrix.SetElement(0,0,axis1X[0])
    axes1ToWorldChangeOfFrameMatrix.SetElement(1,0,axis1X[1])
    axes1ToWorldChangeOfFrameMatrix.SetElement(2,0,axis1X[2])
    axes1ToWorldChangeOfFrameMatrix.SetElement(0,1,axis1Y[0])
    axes1ToWorldChangeOfFrameMatrix.SetElement(1,1,axis1Y[1])
    axes1ToWorldChangeOfFrameMatrix.SetElement(2,1,axis1Y[2])
    axes1ToWorldChangeOfFrameMatrix.SetElement(0,2,axis1Z[0])
    axes1ToWorldChangeOfFrameMatrix.SetElement(1,2,axis1Z[1])
    axes1ToWorldChangeOfFrameMatrix.SetElement(2,2,axis1Z[2])
    axes1ToWorldChangeOfFrameMatrix.SetElement(0,3,axisOrigin[0])
    axes1ToWorldChangeOfFrameMatrix.SetElement(1,3,axisOrigin[1])
    axes1ToWorldChangeOfFrameMatrix.SetElement(2,3,axisOrigin[2])
    return axes1ToWorldChangeOfFrameMatrix

  def getAxes1ToAxes2RegistrationTransformMatrix(self,axes1ToWorldChangeOfFrameMatrix,axes2ToWorldChangeOfFrameMatrix):
    worldToAxes1ChangeOfFrameMatrix = vtk.vtkMatrix4x4()
    worldToAxes1ChangeOfFrameMatrix.DeepCopy(axes1ToWorldChangeOfFrameMatrix)
    worldToAxes1ChangeOfFrameMatrix.Invert()
    axes1ToAxes2RegistrationTransformMatrix = vtk.vtkMatrix4x4()
    vtk.vtkMatrix4x4.Multiply4x4(axes2ToWorldChangeOfFrameMatrix, worldToAxes1ChangeOfFrameMatrix, axes1ToAxes2RegistrationTransformMatrix)
    return axes1ToAxes2RegistrationTransformMatrix

  def makeModels(self):
    if not slicer.app.commandOptions().noMainWindow:
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

    wasModified = parameterNode.StartModify()

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
        singletonTag = self.FIBULA_VIEW_SINGLETON_TAG
      else:
        singletonTag = self.MANDIBLE_VIEW_SINGLETON_TAG
      viewNode = slicer.mrmlScene.GetSingletonNode(singletonTag, "vtkMRMLViewNode")
      cameraNode = slicer.modules.cameras.logic().GetViewActiveCameraNode(viewNode)

      modelDisplayNode.AddViewNodeID(viewNode.GetID())
      decimatedModelDisplayNode.AddViewNodeID(viewNode.GetID())

      centroid = getCentroid(models[i])
      if i==0:
        viewUpDirection = np.array([0.,1.,0.])
        cameraDirection = np.array([1.,0.,0.])
      else:
        viewUpDirection = np.array([0.,0.,1.])
        cameraDirection = np.array([0.,-1.,0.])
      cameraNode.SetPosition(centroid-cameraDirection*300)
      cameraNode.SetFocalPoint(centroid)
      cameraNode.SetViewUp(viewUpDirection)
      cameraNode.ResetClippingRange()

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

    parameterNode.EndModify(wasModified)

    if not slicer.app.commandOptions().noMainWindow:
      slicer.util.forceRenderAllViews()

  def updateFibulaPieces(self):
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    planeCutsList = createListFromFolderID(shNode.GetItemByName("Plane Cuts"))
    for i in range(len(planeCutsList)):
      slicer.modules.dynamicmodeler.logic().RunDynamicModelerTool(planeCutsList[i])

  def updateInverseMandiblePieces(self):
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    inversePlaneCutsList = createListFromFolderID(shNode.GetItemByName("Inverse Plane Cuts"))
    for i in range(len(inversePlaneCutsList)):
      slicer.modules.dynamicmodeler.logic().RunDynamicModelerTool(inversePlaneCutsList[i])

    inverseAppendList = createListFromFolderID(shNode.GetItemByName("Inverse Append"))
    for i in range(len(inverseAppendList)):
      slicer.modules.dynamicmodeler.logic().RunDynamicModelerTool(inverseAppendList[i])

  def tranformMandiblePiecesToFibula(self):
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    mandible2FibulaTransformsFolder = shNode.GetItemByName("Mandible2Fibula transforms")
    mandible2FibulaTransformsList = createListFromFolderID(mandible2FibulaTransformsFolder)
    transformedMandiblePiecesFolder = shNode.GetItemByName("Transformed Mandible Pieces")
    transformedFullMandiblesFolder = shNode.GetItemByName("Transformed Full Mandible")
    if transformedMandiblePiecesFolder:
      shNode.RemoveItem(transformedMandiblePiecesFolder)
    if transformedFullMandiblesFolder:
      shNode.RemoveItem(transformedFullMandiblesFolder)
    transformedMandiblePiecesFolder = shNode.CreateFolderItem(self.getInverseMandibleReconstructionFolderItemID(),"Transformed Mandible Pieces")
    transformedFullMandiblesFolder = shNode.CreateFolderItem(self.getInverseMandibleReconstructionFolderItemID(),"Transformed Full Mandible")

    cutMandiblePiecesList = createListFromFolderID(shNode.GetItemByName("Cut Mandible Pieces"))
    for i in range(len(cutMandiblePiecesList)):
      transformedMandiblePiece = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode',slicer.mrmlScene.GetUniqueNameByString('Transformed ' + cutMandiblePiecesList[i].GetName()))
      transformedMandiblePiece.CreateDefaultDisplayNodes()
      transformedMandiblePiece.CopyContent(cutMandiblePiecesList[i])
      transformedMandiblePieceDisplayNode = transformedMandiblePiece.GetDisplayNode()
      transformedMandiblePieceDisplayNode.SetColor(cutMandiblePiecesList[i].GetDisplayNode().GetColor())
      transformedMandiblePieceDisplayNode.SetVisibility2D(True)

      fibulaViewNode = slicer.mrmlScene.GetSingletonNode(self.FIBULA_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
      transformedMandiblePieceDisplayNode.AddViewNodeID(fibulaViewNode.GetID())

      transformedMandiblePiece.SetAndObserveTransformNodeID(mandible2FibulaTransformsList[i].GetID())
      transformedMandiblePieceTransformationSuccess = transformedMandiblePiece.HardenTransform()
      if not (transformedMandiblePieceTransformationSuccess):
        Exception('Hardening transforms was not successful')

      transformedMandiblePieceItemID = shNode.GetItemByDataNode(transformedMandiblePiece)
      shNode.SetItemParent(transformedMandiblePieceItemID, transformedMandiblePiecesFolder)

    mandibleList = createListFromFolderID(shNode.GetItemByName("Full Mandibles"))
    for i in range(len(mandibleList)):
      transformedMandible = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode',slicer.mrmlScene.GetUniqueNameByString('Transformed ' + mandibleList[i].GetName()))
      transformedMandible.CreateDefaultDisplayNodes()
      transformedMandible.CopyContent(mandibleList[i])
      transformedMandibleDisplayNode = transformedMandible.GetDisplayNode()
      transformedMandibleDisplayNode.SetColor(mandibleList[i].GetDisplayNode().GetColor())
      transformedMandibleDisplayNode.SetVisibility2D(True)

      fibulaViewNode = slicer.mrmlScene.GetSingletonNode(self.FIBULA_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
      transformedMandibleDisplayNode.AddViewNodeID(fibulaViewNode.GetID())

      transformedMandible.SetAndObserveTransformNodeID(mandible2FibulaTransformsList[i].GetID())
      transformedMandibleTransformationSuccess = transformedMandible.HardenTransform()
      if not (transformedMandibleTransformationSuccess):
        Exception('Hardening transforms was not successful')

      transformedMandibleItemID = shNode.GetItemByDataNode(transformedMandible)
      shNode.SetItemParent(transformedMandibleItemID, transformedFullMandiblesFolder)

    pluginHandler = slicer.qSlicerSubjectHierarchyPluginHandler().instance()
    folderPlugin = pluginHandler.pluginByName("Folder")
    qt.QTimer.singleShot(0, lambda: folderPlugin.setDisplayVisibility(transformedFullMandiblesFolder, 1))

  def tranformFibulaPiecesToMandible(self):
    parameterNode = self.getParameterNode()
    fibulaLine = parameterNode.GetNodeReference("fibulaLine")
    planeList = createListFromFolderID(self.getMandiblePlanesFolderItemID())

    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    bonePiecesTransformFolder = shNode.GetItemByName("Bone Pieces Transforms")
    if bonePiecesTransformFolder:
      shNode.RemoveItem(bonePiecesTransformFolder)
    bonePiecesTransformFolder = shNode.CreateFolderItem(self.getMandibleReconstructionFolderItemID(),"Bone Pieces Transforms")
    transformedFibulaPiecesFolder = shNode.GetItemByName("Transformed Fibula Pieces")
    if transformedFibulaPiecesFolder:
      shNode.RemoveItem(transformedFibulaPiecesFolder)
    transformedFibulaPiecesFolder = shNode.CreateFolderItem(self.getMandibleReconstructionFolderItemID(),"Transformed Fibula Pieces")

    lineStartPos = np.zeros(3)
    lineEndPos = np.zeros(3)
    fibulaLine.GetNthControlPointPositionWorld(0, lineStartPos)
    fibulaLine.GetNthControlPointPositionWorld(1, lineEndPos)
    fibulaOrigin = lineStartPos
    fibulaZ = (lineEndPos-lineStartPos)/np.linalg.norm(lineEndPos-lineStartPos)

    cutBonesList = createListFromFolderID(shNode.GetItemByName("Cut Bones"))
    for i in range(len(cutBonesList)-1):
      fibulaToMandibleRegistrationTransformMatrix = vtk.vtkMatrix4x4()
      fibulaToMandibleRegistrationTransformMatrix.DeepCopy(self.mandibleToFibulaRegistrationTransformMatricesList[i])
      fibulaToMandibleRegistrationTransformMatrix.Invert()

      fibulaPieceToMandibleAxisTransformNode = slicer.vtkMRMLLinearTransformNode()
      fibulaPieceToMandibleAxisTransformNode.SetName("Fibula Segment {0} Transform".format(i))
      slicer.mrmlScene.AddNode(fibulaPieceToMandibleAxisTransformNode)

      fibulaPieceToMandibleAxisTransformNode.SetMatrixTransformToParent(fibulaToMandibleRegistrationTransformMatrix)
      fibulaPieceToMandibleAxisTransformNode.UpdateScene(slicer.mrmlScene)

      transformedFibulaPiece = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode',slicer.mrmlScene.GetUniqueNameByString('Transformed ' + cutBonesList[i].GetName()))
      transformedFibulaPiece.CreateDefaultDisplayNodes()
      transformedFibulaPiece.CopyContent(cutBonesList[i])
      transformedFibulaPieceDisplayNode = transformedFibulaPiece.GetDisplayNode()
      transformedFibulaPieceDisplayNode.SetColor(cutBonesList[i].GetDisplayNode().GetColor())
      transformedFibulaPieceDisplayNode.SetVisibility2D(True)

      mandibleViewNode = slicer.mrmlScene.GetSingletonNode(self.MANDIBLE_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
      transformedFibulaPieceDisplayNode.AddViewNodeID(mandibleViewNode.GetID())

      transformedFibulaPiece.SetAndObserveTransformNodeID(fibulaPieceToMandibleAxisTransformNode.GetID())
      transformedFibulaPieceTransformationSuccess = transformedFibulaPiece.HardenTransform()
      if not (transformedFibulaPieceTransformationSuccess):
        Exception('Hardening transforms was not successful')

      transformedFibulaPieceItemID = shNode.GetItemByDataNode(transformedFibulaPiece)
      shNode.SetItemParent(transformedFibulaPieceItemID, transformedFibulaPiecesFolder)

      fibulaPieceToMandibleAxisTransformNodeItemID = shNode.GetItemByDataNode(fibulaPieceToMandibleAxisTransformNode)
      shNode.SetItemParent(fibulaPieceToMandibleAxisTransformNodeItemID, bonePiecesTransformFolder)

  def mandiblePlanesPositioningForMaximumBoneContact(self):
    parameterNode = self.getParameterNode()
    mandibularCurve = parameterNode.GetNodeReference("mandibleCurve")
    planeList = createListFromFolderID(self.getMandiblePlanesFolderItemID())

    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    mandiblePlaneTransformsFolder = shNode.CreateFolderItem(self.getMandibleReconstructionFolderItemID(),"Mandible Planes Transforms")
    
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
      planeList[i+1].GetObjectToWorldMatrix(mandiblePlane1matrix)
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
      planeTransformationSuccess = planeList[i+1].HardenTransform()
      if not (planeTransformationSuccess):
        Exception('Hardening transforms was not successful')
      
      transformNodeItemID = shNode.GetItemByDataNode(transformNode)
      shNode.SetItemParent(transformNodeItemID, mandiblePlaneTransformsFolder)
    
    if mandiblePlaneTransformsFolder:
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
    planeNode.SetNthControlPointPosition(0,mandiblePlaneStraightOrigin)
    planeNode.SetNthControlPointPosition(1,mandiblePlaneStraightOrigin + mandiblePlaneStraightX*dx)
    planeNode.SetNthControlPointPosition(2,mandiblePlaneStraightOrigin + mandiblePlaneStraightY*dy)

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
    if miterBoxesModelsFolder:
      shNode.RemoveItem(miterBoxesModelsFolder)
    biggerMiterBoxesModelsFolder = shNode.GetItemByName("biggerMiterBoxes Models")
    if biggerMiterBoxesModelsFolder:
      shNode.RemoveItem(biggerMiterBoxesModelsFolder)

    if checkSecurityMarginOnMiterBoxCreationChecked:
      cutBonesList = createListFromFolderID(shNode.GetItemByName("Cut Bones"))
      duplicateFibulaBonePiecesModelsFolder = shNode.CreateFolderItem(self.getMandibleReconstructionFolderItemID(),"Duplicate Fibula Bone Pieces")
      duplicateFibulaBonePiecesTransformsFolder = shNode.CreateFolderItem(self.getMandibleReconstructionFolderItemID(),"Duplicate Fibula Bone Pieces Transforms")
      
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
        duplicateFibulaBonePieceTransformationSuccess = duplicateFibulaBonePiecesList[i].HardenTransform()
        if not (duplicateFibulaBonePieceTransformationSuccess):
          Exception('Hardening transforms was not successful')

        duplicateFibulaPieceTransformNodeItemID = shNode.GetItemByDataNode(duplicateFibulaPieceTransformNode)
        shNode.SetItemParent(duplicateFibulaPieceTransformNodeItemID, duplicateFibulaBonePiecesTransformsFolder)

      collisionDetected = False
      for i in range(0,len(duplicateFibulaBonePiecesList) -1):
        collisionDetection = vtk.vtkCollisionDetectionFilter()
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
      
      if duplicateFibulaBonePiecesTransformsFolder:
        shNode.RemoveItem(duplicateFibulaBonePiecesTransformsFolder)
      if duplicateFibulaBonePiecesModelsFolder:
        shNode.RemoveItem(duplicateFibulaBonePiecesModelsFolder)
      if collisionDetected:
        slicer.util.errorDisplay(f"Planned fibula segments could overlap each other (the distance in between them do not satisfy the security margin of {securityMarginOfFibulaPieces}mm). " +
            "You can fix this by increasing 'intersection distance multiplier' or 'between space' and pressing the update button")
        return


    miterBoxesModelsFolder = shNode.CreateFolderItem(self.getMandibleReconstructionFolderItemID(),"miterBoxes Models")
    biggerMiterBoxesModelsFolder = shNode.CreateFolderItem(self.getMandibleReconstructionFolderItemID(),"biggerMiterBoxes Models")
    miterBoxesTransformsFolder = shNode.CreateFolderItem(self.getMandibleReconstructionFolderItemID(),"miterBoxes Transforms")
    intersectionsFolder = shNode.CreateFolderItem(self.getMandibleReconstructionFolderItemID(),"Intersections")
    pointsIntersectionsFolder = shNode.CreateFolderItem(self.getMandibleReconstructionFolderItemID(),"Points Intersections")

    if not useMoreExactVersionOfPositioningAlgorithmChecked:
      #Create fibula axis:
      fibulaX, fibulaY, fibulaZ, fibulaOrigin = self.createFibulaAxisFromFibulaLineAndNotLeftChecked(fibulaLine,notLeftFibulaChecked) 

    fibulaViewNode = slicer.mrmlScene.GetSingletonNode(self.FIBULA_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")

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
      biggerMiterBoxDisplayNode.SetVisibility2D(True)
      if np.linalg.norm(fibulaCentroid-centerOfScalarVolume) < np.linalg.norm(mandibleCentroid-centerOfScalarVolume):
        redSliceNode = slicer.mrmlScene.GetSingletonNode("Red", "vtkMRMLSliceNode")
        biggerMiterBoxDisplayNode.AddViewNodeID(redSliceNode.GetID())

      biggerMiterBoxModelItemID = shNode.GetItemByDataNode(biggerMiterBoxModel)
      shNode.SetItemParent(biggerMiterBoxModelItemID, biggerMiterBoxesModelsFolder)

      fibulaPlaneMatrix = vtk.vtkMatrix4x4()
      fibulaPlanesList[i].GetObjectToWorldMatrix(fibulaPlaneMatrix)
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

      #Calculations for deltaMiterBoxAxisY
      sinOfMiterBoxAxisZAndFibulaZVector = [0,0,0]
      vtk.vtkMath.Cross(miterBoxAxisZ, fibulaZ, sinOfMiterBoxAxisZAndFibulaZVector)
      sinOfMiterBoxAxisZAndFibulaZ = np.linalg.norm(sinOfMiterBoxAxisZAndFibulaZVector)
      rotatedMiterBoxAxisY = [0,0,0]
      vtk.vtkMath.Cross(fibulaZ, miterBoxAxisX, rotatedMiterBoxAxisY)
      rotatedMiterBoxAxisY = rotatedMiterBoxAxisY/np.linalg.norm(rotatedMiterBoxAxisY)
      cosOfRotatedMiterBoxAxisYAndMiterBoxAxisY = vtk.vtkMath.Dot(rotatedMiterBoxAxisY, miterBoxAxisY)
      deltaMiterBoxAxisY = biggerMiterBoxWidth/2*sinOfMiterBoxAxisZAndFibulaZ/cosOfRotatedMiterBoxAxisYAndMiterBoxAxisY

      miterBoxToWorldChangeOfFrameTransformNode = slicer.vtkMRMLLinearTransformNode()
      miterBoxToWorldChangeOfFrameTransformNode.SetName("temp%d" % i)
      slicer.mrmlScene.AddNode(miterBoxToWorldChangeOfFrameTransformNode)

      if i%2 == 0:
        miterBoxAxisXTranslation = 0
        miterBoxAxisYTranslation = biggerMiterBoxHeight/2+deltaMiterBoxAxisY+biggerMiterBoxDistanceToFibula/cosOfRotatedMiterBoxAxisYAndMiterBoxAxisY
        miterBoxAxisZTranslation = -miterBoxSlotWidth/2
      else:
        miterBoxAxisXTranslation = 0
        miterBoxAxisYTranslation = biggerMiterBoxHeight/2+deltaMiterBoxAxisY+biggerMiterBoxDistanceToFibula/cosOfRotatedMiterBoxAxisYAndMiterBoxAxisY
        miterBoxAxisZTranslation = miterBoxSlotWidth/2
      
      miterBoxOrigin = pointOfIntersection + miterBoxAxisX*miterBoxAxisXTranslation + miterBoxAxisY*miterBoxAxisYTranslation + miterBoxAxisZ*miterBoxAxisZTranslation
      miterBoxToWorldChangeOfFrameMatrix = self.getAxes1ToWorldChangeOfFrameMatrix(miterBoxAxisX, miterBoxAxisY, miterBoxAxisZ, miterBoxOrigin)

      miterBoxToWorldChangeOfFrameTransformNode.SetMatrixTransformToParent(miterBoxToWorldChangeOfFrameMatrix)
      miterBoxToWorldChangeOfFrameTransformNode.UpdateScene(slicer.mrmlScene)

      miterBoxModel.SetAndObserveTransformNodeID(miterBoxToWorldChangeOfFrameTransformNode.GetID())
      miterBoxTransformationSuccess = miterBoxModel.HardenTransform()
      biggerMiterBoxModel.SetAndObserveTransformNodeID(miterBoxToWorldChangeOfFrameTransformNode.GetID())
      biggerMiterBoxTransformationSuccess = biggerMiterBoxModel.HardenTransform()

      if not (miterBoxTransformationSuccess and biggerMiterBoxTransformationSuccess):
        Exception('Hardening transforms was not successful')

      miterBoxToWorldChangeOfFrameTransformNodeItemID = shNode.GetItemByDataNode(miterBoxToWorldChangeOfFrameTransformNode)
      shNode.SetItemParent(miterBoxToWorldChangeOfFrameTransformNodeItemID, miterBoxesTransformsFolder)
    
    if miterBoxesTransformsFolder:
      shNode.RemoveItem(miterBoxesTransformsFolder)
    if intersectionsFolder:
      shNode.RemoveItem(intersectionsFolder)
    if pointsIntersectionsFolder:
      shNode.RemoveItem(pointsIntersectionsFolder)

    self.setRedSliceForBoxModelsDisplayNodes()

  def createDentalImplantCylindersFiducialList(self):
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    dentalImplantCylindersFiducialsListsFolder = shNode.GetItemByName("Dental Implants Cylinders Fiducials")
    if not dentalImplantCylindersFiducialsListsFolder:
      dentalImplantCylindersFiducialsListsFolder = shNode.CreateFolderItem(self.getDentalImplantsPlanningFolderItemID(),"Dental Implants Cylinders Fiducials")
    
    dentalImplantFiducialListNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLMarkupsFiducialNode")
    dentalImplantFiducialListNode.SetName("temp")
    slicer.mrmlScene.AddNode(dentalImplantFiducialListNode)
    slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(dentalImplantFiducialListNode)
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    dentalImplantFiducialListNodeItemID = shNode.GetItemByDataNode(dentalImplantFiducialListNode)
    shNode.SetItemParent(dentalImplantFiducialListNodeItemID, dentalImplantCylindersFiducialsListsFolder)
    dentalImplantFiducialListNode.SetName(slicer.mrmlScene.GetUniqueNameByString("dentalImplantCylindersFiducialsList"))

    displayNode = dentalImplantFiducialListNode.GetDisplayNode()
    mandibleViewNode = slicer.mrmlScene.GetSingletonNode(self.MANDIBLE_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
    displayNode.AddViewNodeID(mandibleViewNode.GetID())

    #setup placement
    slicer.modules.markups.logic().SetActiveListID(dentalImplantFiducialListNode)
    interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
    interactionNode.SwitchToPersistentPlaceMode()
  
  def createFibulaCylindersFiducialList(self):
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    fibulaCylindersFiducialsListsFolder = shNode.GetItemByName("Fibula Cylinders Fiducials Lists")
    if not fibulaCylindersFiducialsListsFolder:
      fibulaCylindersFiducialsListsFolder = shNode.CreateFolderItem(self.getMandibleReconstructionFolderItemID(),"Fibula Cylinders Fiducials Lists")
    
    fibulaFiducialListNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLMarkupsFiducialNode")
    fibulaFiducialListNode.SetName("temp")
    slicer.mrmlScene.AddNode(fibulaFiducialListNode)
    slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(fibulaFiducialListNode)
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    fibulaFiducialListNodeItemID = shNode.GetItemByDataNode(fibulaFiducialListNode)
    shNode.SetItemParent(fibulaFiducialListNodeItemID, fibulaCylindersFiducialsListsFolder)
    fibulaFiducialListNode.SetName(slicer.mrmlScene.GetUniqueNameByString("fibulaCylindersFiducialsList"))

    displayNode = fibulaFiducialListNode.GetDisplayNode()
    fibulaViewNode = slicer.mrmlScene.GetSingletonNode(self.FIBULA_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
    displayNode.AddViewNodeID(fibulaViewNode.GetID())

    #setup placement
    slicer.modules.markups.logic().SetActiveListID(fibulaFiducialListNode)
    interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
    interactionNode.SwitchToPersistentPlaceMode()

  def createCylindersFromFiducialListAndFibulaSurgicalGuideBase(self):
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    fibulaCylindersModelsFolder = shNode.GetItemByName("Fibula Cylinders Models")
    if fibulaCylindersModelsFolder:
      shNode.RemoveItem(fibulaCylindersModelsFolder)
    fibulaCylindersModelsFolder = shNode.CreateFolderItem(self.getMandibleReconstructionFolderItemID(),"Fibula Cylinders Models")
    cylindersTransformsFolder = shNode.CreateFolderItem(self.getMandibleReconstructionFolderItemID(),"Cylinders Transforms")
    
    parameterNode = self.getParameterNode()
    fibulaFiducialList = parameterNode.GetNodeReference("fibulaFiducialList")
    fibulaSurgicalGuideBaseModel = parameterNode.GetNodeReference("fibulaSurgicalGuideBaseModel")
    fibulaScrewHoleCylinderRadius = float(parameterNode.GetParameter("fibulaScrewHoleCylinderRadius"))

    normalsOfSurgicalGuideBaseModel = slicer.util.arrayFromModelPointData(fibulaSurgicalGuideBaseModel, 'Normals')
    
    surgicalGuideBaseMesh = fibulaSurgicalGuideBaseModel.GetMesh()

    for i in range(fibulaFiducialList.GetNumberOfControlPoints()):
      cylinderOrigin = [0,0,0]
      fibulaFiducialList.GetNthControlPointPosition(i,cylinderOrigin)

      pointID = surgicalGuideBaseMesh.FindPoint(cylinderOrigin)

      normalAtPointID = normalsOfSurgicalGuideBaseModel[pointID]

      cylinderAxisX = [0,0,0]
      cylinderAxisY = [0,0,0]
      cylinderAxisZ = normalAtPointID
      vtk.vtkMath.Perpendiculars(cylinderAxisZ,cylinderAxisX,cylinderAxisY,0)

      cylinderModel = createCylinder("cylinder%d" % i, fibulaScrewHoleCylinderRadius)
      cylinderModelItemID = shNode.GetItemByDataNode(cylinderModel)
      shNode.SetItemParent(cylinderModelItemID, fibulaCylindersModelsFolder)
      
      cylinderToWorldChangeOfFrameMatrix = self.getAxes1ToWorldChangeOfFrameMatrix(cylinderAxisX, cylinderAxisY, cylinderAxisZ, cylinderOrigin)

      cylinderToWorldChangeOfFrameTransformNode = slicer.vtkMRMLLinearTransformNode()
      cylinderToWorldChangeOfFrameTransformNode.SetName("temp%d" % i)
      slicer.mrmlScene.AddNode(cylinderToWorldChangeOfFrameTransformNode)

      cylinderToWorldChangeOfFrameTransformNode.SetMatrixTransformToParent(cylinderToWorldChangeOfFrameMatrix)

      cylinderToWorldChangeOfFrameTransformNode.UpdateScene(slicer.mrmlScene)

      cylinderModel.SetAndObserveTransformNodeID(cylinderToWorldChangeOfFrameTransformNode.GetID())
      cylinderModel.HardenTransform()
      
      cylinderTransformationSuccess = cylinderModel.HardenTransform()
      if not (cylinderTransformationSuccess):
        Exception('Hardening transforms was not successful')

      cylinderToWorldChangeOfFrameTransformNodeItemID = shNode.GetItemByDataNode(cylinderToWorldChangeOfFrameTransformNode)
      shNode.SetItemParent(cylinderToWorldChangeOfFrameTransformNodeItemID, cylindersTransformsFolder)
    
    if cylindersTransformsFolder:
      shNode.RemoveItem(cylindersTransformsFolder)
  
  def createCylindersFromFiducialListAndMandibleSurgicalGuideBase(self):
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    mandibleCylindersModelsFolder = shNode.GetItemByName("Mandible Cylinders Models")
    if mandibleCylindersModelsFolder:
      shNode.RemoveItem(mandibleCylindersModelsFolder)
    mandibleCylindersModelsFolder = shNode.CreateFolderItem(self.getMandibleReconstructionFolderItemID(),"Mandible Cylinders Models")
    cylindersTransformsFolder = shNode.CreateFolderItem(self.getMandibleReconstructionFolderItemID(),"Cylinders Transforms")
    
    parameterNode = self.getParameterNode()
    mandibleFiducialList = parameterNode.GetNodeReference("mandibleFiducialList")
    mandibleSurgicalGuideBaseModel = parameterNode.GetNodeReference("mandibleSurgicalGuideBaseModel")
    mandibleScrewHoleCylinderRadius = float(parameterNode.GetParameter("mandibleScrewHoleCylinderRadius"))

    normalsOfSurgicalGuideBaseModel = slicer.util.arrayFromModelPointData(mandibleSurgicalGuideBaseModel, 'Normals')
    
    surgicalGuideBaseMesh = mandibleSurgicalGuideBaseModel.GetMesh()

    for i in range(mandibleFiducialList.GetNumberOfControlPoints()):
      cylinderOrigin = [0,0,0]
      mandibleFiducialList.GetNthControlPointPosition(i,cylinderOrigin)

      pointID = surgicalGuideBaseMesh.FindPoint(cylinderOrigin)

      normalAtPointID = normalsOfSurgicalGuideBaseModel[pointID]

      cylinderAxisX = [0,0,0]
      cylinderAxisY = [0,0,0]
      cylinderAxisZ = normalAtPointID
      vtk.vtkMath.Perpendiculars(cylinderAxisZ,cylinderAxisX,cylinderAxisY,0)

      cylinderModel = createCylinder("cylinder%d" % i, mandibleScrewHoleCylinderRadius)
      cylinderModelItemID = shNode.GetItemByDataNode(cylinderModel)
      shNode.SetItemParent(cylinderModelItemID, mandibleCylindersModelsFolder)
      
      cylinderToWorldChangeOfFrameMatrix = self.getAxes1ToWorldChangeOfFrameMatrix(cylinderAxisX, cylinderAxisY, cylinderAxisZ, cylinderOrigin)

      cylinderToWorldChangeOfFrameTransformNode = slicer.vtkMRMLLinearTransformNode()
      cylinderToWorldChangeOfFrameTransformNode.SetName("temp%d" % i)
      slicer.mrmlScene.AddNode(cylinderToWorldChangeOfFrameTransformNode)

      cylinderToWorldChangeOfFrameTransformNode.SetMatrixTransformToParent(cylinderToWorldChangeOfFrameMatrix)

      cylinderToWorldChangeOfFrameTransformNode.UpdateScene(slicer.mrmlScene)

      cylinderModel.SetAndObserveTransformNodeID(cylinderToWorldChangeOfFrameTransformNode.GetID())
      cylinderModel.HardenTransform()

      cylinderTransformationSuccess = cylinderModel.HardenTransform()
      if not (cylinderTransformationSuccess):
        Exception('Hardening transforms was not successful')
      
      cylinderToWorldChangeOfFrameTransformNodeItemID = shNode.GetItemByDataNode(cylinderToWorldChangeOfFrameTransformNode)
      shNode.SetItemParent(cylinderToWorldChangeOfFrameTransformNodeItemID, cylindersTransformsFolder)

    if cylindersTransformsFolder:
      shNode.RemoveItem(cylindersTransformsFolder)

  def createCylindersFromFiducialListAndNeomandiblePieces(self):
    #self.create3DModelOfTheReconstruction()

    parameterNode = self.getParameterNode()
    mandibularCurve = parameterNode.GetNodeReference("mandibleCurve")
    mandibleReconstructionModel = parameterNode.GetNodeReference("mandibleReconstructionModel")
    dentalImplantsFiducialList = parameterNode.GetNodeReference("dentalImplantsFiducialList")
    dentalImplantCylinderRadius = float(parameterNode.GetParameter("dentalImplantCylinderRadius"))
    dentalImplantCylinderHeight = float(parameterNode.GetParameter("dentalImplantCylinderHeight"))
    dentalImplantDrillGuideWall = float(parameterNode.GetParameter("dentalImplantDrillGuideWall"))

    #mandibleReconstructionModelDisplayNode = mandibleReconstructionModel.GetDisplayNode()
    #mandibleReconstructionModelDisplayNode.SetVisibility(False)

    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    dentalImplantsCylindersModelsFolder = shNode.GetItemByName("Dental Implants Cylinders Models")
    dentalImplantsPlanesFolder = shNode.GetItemByName("dentalImplants Planes")
    dentalImplantsCylindersTransformsFolder = shNode.GetItemByName("Dental Implants Cylinders Transforms")
    fibulaDentalImplantsCylindersModelsFolder = shNode.GetItemByName("Fibula Dental Implants Cylinders Models")
    biggerFibulaDentalImplantsCylindersModelsFolder = shNode.GetItemByName("Bigger Fibula Dental Implants Cylinders Models")
    if dentalImplantsCylindersModelsFolder:
      shNode.RemoveItem(dentalImplantsCylindersModelsFolder)
    if dentalImplantsPlanesFolder:
      shNode.RemoveItem(dentalImplantsPlanesFolder)
    if dentalImplantsCylindersTransformsFolder:
      shNode.RemoveItem(dentalImplantsCylindersTransformsFolder)
    if fibulaDentalImplantsCylindersModelsFolder:
      shNode.RemoveItem(fibulaDentalImplantsCylindersModelsFolder)
    if biggerFibulaDentalImplantsCylindersModelsFolder:
      shNode.RemoveItem(biggerFibulaDentalImplantsCylindersModelsFolder)
    dentalImplantsCylindersModelsFolder = shNode.CreateFolderItem(self.getDentalImplantsPlanningFolderItemID(),"Dental Implants Cylinders Models")
    dentalImplantsPlanesFolder = shNode.CreateFolderItem(self.getDentalImplantsPlanningFolderItemID(),"dentalImplants Planes")
    dentalImplantsCylindersTransformsFolder = shNode.CreateFolderItem(self.getDentalImplantsPlanningFolderItemID(),"Dental Implants Cylinders Transforms")
    fibulaDentalImplantsCylindersModelsFolder = shNode.CreateFolderItem(self.getDentalImplantsPlanningFolderItemID(),"Fibula Dental Implants Cylinders Models")
    biggerFibulaDentalImplantsCylindersModelsFolder = shNode.CreateFolderItem(self.getDentalImplantsPlanningFolderItemID(),"Bigger Fibula Dental Implants Cylinders Models")

    transformedFibulaPiecesFolder = shNode.GetItemByName("Transformed Fibula Pieces")
    transformedFibulaPiecesList = createListFromFolderID(transformedFibulaPiecesFolder)

    noCapsTransformedFibulaPiecesFolder = shNode.GetItemByName("No Caps Transformed Fibula Pieces")
    if noCapsTransformedFibulaPiecesFolder:
      shNode.RemoveItem(noCapsTransformedFibulaPiecesFolder)
    noCapsTransformedFibulaPiecesFolder = shNode.CreateFolderItem(self.getDentalImplantsPlanningFolderItemID(),"No Caps Transformed Fibula Pieces")

    #create noCapsTransformedFibulaPieces
    for i in range(len(transformedFibulaPiecesList)):
      noCapsTransformedFibulaPiece = slicer.mrmlScene.CreateNodeByClass('vtkMRMLModelNode')
      noCapsTransformedFibulaPiece.SetName(f"noCapsTransformedFibulaPiece {i}")
      slicer.mrmlScene.AddNode(noCapsTransformedFibulaPiece)
      noCapsTransformedFibulaPiece.CreateDefaultDisplayNodes()
      noCapsTransformedFibulaPiece.GetDisplayNode().SetVisibility(False)

      connectivityFilter = vtk.vtkConnectivityFilter()
      connectivityFilter.SetInputData(transformedFibulaPiecesList[i].GetMesh())
      connectivityFilter.SetExtractionModeToLargestRegion()
      connectivityFilter.Update()

      noCapsTransformedFibulaPiece.SetAndObserveMesh(calculateNormals(connectivityFilter.GetOutput()))
      noCapsTransformedFibulaPieceItemID = shNode.GetItemByDataNode(noCapsTransformedFibulaPiece)
      shNode.SetItemParent(noCapsTransformedFibulaPieceItemID, noCapsTransformedFibulaPiecesFolder)

    noCapsTransformedFibulaPiecesList = createListFromFolderID(noCapsTransformedFibulaPiecesFolder)
    
    mandibleViewNode = slicer.mrmlScene.GetSingletonNode(self.MANDIBLE_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
    fibulaViewNode = slicer.mrmlScene.GetSingletonNode(self.FIBULA_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")

    aux = slicer.mrmlScene.GetNodeByID('vtkMRMLColorTableNodeFileMediumChartColors.txt')
    colorTable = aux.GetLookupTable()
    ind = 0# Because it is the last color fibula segments will take
    colorwithalpha = colorTable.GetTableValue(ind)
    color = [colorwithalpha[0],colorwithalpha[1],colorwithalpha[2]]

    for i in range(dentalImplantsFiducialList.GetNumberOfControlPoints()):
      dentalImplantCylinderModel = createCylinder("implantCylinder%d" % i,dentalImplantCylinderRadius,dentalImplantCylinderHeight)
      dentalImplantCylinderModelItemID = shNode.GetItemByDataNode(dentalImplantCylinderModel)
      shNode.SetItemParent(dentalImplantCylinderModelItemID, dentalImplantsCylindersModelsFolder)

      dentalImplantCylinderDisplayNode = dentalImplantCylinderModel.GetDisplayNode()
      dentalImplantCylinderDisplayNode.AddViewNodeID(mandibleViewNode.GetID())
      dentalImplantCylinderDisplayNode.SetColor(color)

      fibulaDentalImplantCylinderModel = createCylinder("fibulaImplantCylinder%d" % i,dentalImplantCylinderRadius)
      fibulaDentalImplantCylinderModelItemID = shNode.GetItemByDataNode(fibulaDentalImplantCylinderModel)
      shNode.SetItemParent(fibulaDentalImplantCylinderModelItemID, fibulaDentalImplantsCylindersModelsFolder)
      
      fibulaDentalImplantCylinderDisplayNode = fibulaDentalImplantCylinderModel.GetDisplayNode()
      fibulaDentalImplantCylinderDisplayNode.AddViewNodeID(fibulaViewNode.GetID())
      fibulaDentalImplantCylinderDisplayNode.SetVisibility(False)
      fibulaDentalImplantCylinderDisplayNode.SetColor(color)

      biggerFibulaDentalImplantCylinderModel = createCylinder("biggerFibulaImplantCylinder%d" % i,dentalImplantCylinderRadius + dentalImplantDrillGuideWall,dentalImplantCylinderHeight)
      biggerFibulaDentalImplantCylinderModelItemID = shNode.GetItemByDataNode(biggerFibulaDentalImplantCylinderModel)
      shNode.SetItemParent(biggerFibulaDentalImplantCylinderModelItemID, biggerFibulaDentalImplantsCylindersModelsFolder)
      
      biggerFibulaDentalImplantCylinderDisplayNode = biggerFibulaDentalImplantCylinderModel.GetDisplayNode()
      biggerFibulaDentalImplantCylinderDisplayNode.AddViewNodeID(fibulaViewNode.GetID())
      biggerFibulaDentalImplantCylinderDisplayNode.SetVisibility(False)
      biggerFibulaDentalImplantCylinderDisplayNode.SetColor(color)

      #Create dentalImplant plane
      dentalImplantPlane = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsPlaneNode", "dentalImplant Plane%d" % i)
      slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(dentalImplantPlane)
      dentalImplantPlaneItemID = shNode.GetItemByDataNode(dentalImplantPlane)
      shNode.SetItemParent(dentalImplantPlaneItemID, dentalImplantsPlanesFolder)

      dentalImplantPlane.SetAxes([1,0,0],[0,1,0],[0,0,1])
      dentalImplantPlane.SetOrigin([0,0,0])
      dentalImplantPlane.SetAttribute("isDentalImplantPlane","True")
      dentalImplantPlane.SetPlaneType(slicer.vtkMRMLMarkupsPlaneNode.PlaneType3Points)

      displayNode = dentalImplantPlane.GetDisplayNode()
      mandibleViewNode = slicer.mrmlScene.GetSingletonNode(self.MANDIBLE_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
      displayNode.AddViewNodeID(mandibleViewNode.GetID())
      displayNode.SetGlyphScale(self.PLANE_GLYPH_SCALE)
      displayNode.SetOpacity(0)
      displayNode.HandlesInteractiveOn()
      displayNode.RotationHandleVisibilityOn()
      displayNode.TranslationHandleVisibilityOn()
      displayNode.ScaleHandleVisibilityOff()
      displayNode.SetRotationHandleComponentVisibility(True,True,False,False)

      pos = [0,0,0]
      dentalImplantsFiducialList.GetNthControlPointPosition(i,pos)
      pos = np.array(pos)

      # searchModelClosestToPointFromList
      nearestPieceIndex = 0
      nearestDistance = 1e5
      for j in range(1,len(noCapsTransformedFibulaPiecesList)):
        currentDistance = np.linalg.norm(
          pos - getClosestModelPointToPosition(noCapsTransformedFibulaPiecesList[j],pos)
        )
        
        if currentDistance < nearestDistance:
          nearestPieceIndex = j
          nearestDistance = currentDistance

      dentalImplantAxisZ = getAverageNormalFromModelPoint2(
        noCapsTransformedFibulaPiecesList[nearestPieceIndex],
        pos
      )

      if dentalImplantAxisZ is None:
        dentalImplantAxisZ = np.zeros(3)
        dentalImplantAxisZ[2] = 1

      dentalImplantAxisZ = dentalImplantAxisZ/np.linalg.norm(dentalImplantAxisZ)

      closestCurvePoint = [0,0,0]
      closestCurvePointIndex = mandibularCurve.GetClosestPointPositionAlongCurveWorld(pos,closestCurvePoint)
      matrix = vtk.vtkMatrix4x4()
      mandibularCurve.GetCurvePointToWorldTransformAtPointIndex(closestCurvePointIndex,matrix)
      mandibularCurveX = np.array([matrix.GetElement(0,0),matrix.GetElement(1,0),matrix.GetElement(2,0)])
      normalToDentalImplantAxisZAndMandibularCurveX = [0,0,0]
      vtk.vtkMath.Cross(dentalImplantAxisZ, mandibularCurveX, normalToDentalImplantAxisZAndMandibularCurveX)
      normalToDentalImplantAxisZAndMandibularCurveX = normalToDentalImplantAxisZAndMandibularCurveX/np.linalg.norm(normalToDentalImplantAxisZAndMandibularCurveX)


      dentalImplantAxisX = [0,0,0]
      dentalImplantAxisY =  [0,0,0]
      vtk.vtkMath.Cross(normalToDentalImplantAxisZAndMandibularCurveX, dentalImplantAxisZ, dentalImplantAxisX)
      dentalImplantAxisX = dentalImplantAxisX/np.linalg.norm(dentalImplantAxisX)
      vtk.vtkMath.Cross(dentalImplantAxisZ, dentalImplantAxisX, dentalImplantAxisY)
      dentalImplantAxisY = dentalImplantAxisY/np.linalg.norm(dentalImplantAxisY)

      dentalImplantPlane.SetAxes(dentalImplantAxisX,dentalImplantAxisY,dentalImplantAxisZ)
      dentalImplantPlane.SetOrigin(pos)

      dentalImplantCylinderTransformNode = slicer.vtkMRMLLinearTransformNode()
      dentalImplantCylinderTransformNode.SetName("dentalImplantTransform%d" % i)
      slicer.mrmlScene.AddNode(dentalImplantCylinderTransformNode)

      dentalImplantPlaneToWorldMatrix = vtk.vtkMatrix4x4()
      dentalImplantPlane.GetObjectToWorldMatrix(dentalImplantPlaneToWorldMatrix)
      dentalImplantCylinderTransformNode.SetMatrixTransformToParent(dentalImplantPlaneToWorldMatrix)

      dentalImplantCylinderTransformNode.UpdateScene(slicer.mrmlScene)

      dentalImplantCylinderModel.SetAndObserveTransformNodeID(dentalImplantCylinderTransformNode.GetID())
      
      dentalImplantCylinderTransformNodeItemID = shNode.GetItemByDataNode(dentalImplantCylinderTransformNode)
      shNode.SetItemParent(dentalImplantCylinderTransformNodeItemID, dentalImplantsCylindersTransformsFolder)

      observer = dentalImplantPlane.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent,self.onDentalImplantPlaneMoved)
      self.dentalImplantPlaneObserversPlaneNodeIDAndTransformIDList.append([observer,dentalImplantPlane.GetID(),dentalImplantCylinderTransformNode.GetID()])

    self.onUpdateFibuladentalImplantsTimerTimeout()

  def onUpdateFibuladentalImplantsTimerTimeout(self):
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()

    #check if self.mandibleToFibulaRegistrationTransformMatricesList exists, if not, create it
    if len(self.mandibleToFibulaRegistrationTransformMatricesList) == 0:
      mandible2FibulaTransformsFolder = shNode.GetItemByName("Mandible2Fibula transforms")
      mandibleToFibulaRegistrationTransformNodesList = createListFromFolderID(mandible2FibulaTransformsFolder)
      if len(mandibleToFibulaRegistrationTransformNodesList) != 0:
        for i in range(len(mandibleToFibulaRegistrationTransformNodesList)):
          mandibleToFibulaRegistrationMatrix = vtk.vtkMatrix4x4()
          mandibleToFibulaRegistrationTransformNodesList[i].GetMatrixTransformToParent(mandibleToFibulaRegistrationMatrix)
          self.mandibleToFibulaRegistrationTransformMatricesList.append(mandibleToFibulaRegistrationMatrix)
      else:
        self.generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandible()

    #Check collision of dentalImplantCylinder with cutBones, create/update a transform and apply it to cylinders
    fibulaDentalImplantsCylindersTransformsFolder = shNode.GetItemByName("Fibula Dental Implants Cylinders Transforms")
    if fibulaDentalImplantsCylindersTransformsFolder:
      shNode.RemoveItem(fibulaDentalImplantsCylindersTransformsFolder)
    fibulaDentalImplantsCylindersTransformsFolder = shNode.CreateFolderItem(self.getDentalImplantsPlanningFolderItemID(),"Fibula Dental Implants Cylinders Transforms")

    transformedFibulaPiecesFolder = shNode.GetItemByName("Transformed Fibula Pieces")
    dentalImplantsCylindersModelsFolder = shNode.GetItemByName("Dental Implants Cylinders Models")
    fibulaDentalImplantsCylindersModelsFolder = shNode.GetItemByName("Fibula Dental Implants Cylinders Models")
    biggerFibulaDentalImplantsCylindersModelsFolder = shNode.GetItemByName("Bigger Fibula Dental Implants Cylinders Models")
    fibulaPlanesFolder = shNode.GetItemByName("Fibula planes")
    mandiblePlanesFolder = shNode.GetItemByName("Mandibular planes")

    transformedFibulaPiecesList = createListFromFolderID(transformedFibulaPiecesFolder)
    dentalImplantsCylindersModelsList = createListFromFolderID(dentalImplantsCylindersModelsFolder)
    fibulaDentalImplantsCylindersModelsList = createListFromFolderID(fibulaDentalImplantsCylindersModelsFolder)
    biggerFibulaDentalImplantsCylindersModelsList = createListFromFolderID(biggerFibulaDentalImplantsCylindersModelsFolder)
    fibulaPlanesList = createListFromFolderID(fibulaPlanesFolder)
    mandiblePlanesList = createListFromFolderID(mandiblePlanesFolder)

    for i in range(len(dentalImplantsCylindersModelsList)):
      dentalImplantCylinderModel = dentalImplantsCylindersModelsList[i]
      fibulaDentalImplantCylinderModel = fibulaDentalImplantsCylindersModelsList[i]
      biggerFibulaDentalImplantCylinderModel = biggerFibulaDentalImplantsCylindersModelsList[i]

      biggerFibulaDentalImplantCylinderDisplayNode = biggerFibulaDentalImplantCylinderModel.GetDisplayNode()
      biggerFibulaDentalImplantCylinderDisplayNode.SetVisibility(True)

      #check in what reconstructed bone piece the implant is positioned
      transformedFibulaPieceIndex = 0
      for j in range(len(transformedFibulaPiecesList)):
        transformedFibulaPiece = transformedFibulaPiecesList[j]
        collisionDetection = vtk.vtkCollisionDetectionFilter()
        collisionDetection.SetInputData(0, dentalImplantCylinderModel.GetPolyData())
        collisionDetection.SetInputData(1, transformedFibulaPiece.GetPolyData())
        dentalImplantCylinderModelTransformMatrix = dentalImplantCylinderModel.GetParentTransformNode().GetTransformToParent().GetMatrix()
        collisionDetection.SetMatrix(0, dentalImplantCylinderModelTransformMatrix)
        identityMatrix = vtk.vtkMatrix4x4()
        collisionDetection.SetMatrix(1, identityMatrix)
        collisionDetection.SetBoxTolerance(0.0)
        collisionDetection.SetCellTolerance(0.0)
        collisionDetection.SetNumberOfCellsPerNode(2)
        collisionDetection.Update()
          
        if collisionDetection.GetNumberOfContacts() > 0:
          transformedFibulaPieceIndex = j
          break

      fibulaDentalImplantCylinderTransformNode = slicer.vtkMRMLLinearTransformNode()
      fibulaDentalImplantCylinderTransformNode.SetName("fibulaDentalImplantTransform%d" % i)
      slicer.mrmlScene.AddNode(fibulaDentalImplantCylinderTransformNode)

      dentalImplantCylinderToWorldChangeOfFrameMatrix = (dentalImplantCylinderModel.
        GetParentTransformNode().GetTransformToParent().GetMatrix())
      fibulaDentalImplantCylinderTransform = vtk.vtkTransform()
      fibulaDentalImplantCylinderTransform.PostMultiply()
      fibulaDentalImplantCylinderTransform.Concatenate(dentalImplantCylinderToWorldChangeOfFrameMatrix)
      fibulaDentalImplantCylinderTransform.Concatenate(self.mandibleToFibulaRegistrationTransformMatricesList[transformedFibulaPieceIndex])

      biggerFibulaDentalImplantCylinderTransformMatrix = fibulaDentalImplantCylinderTransform.GetMatrix()
      biggerFibulaDentalImplantCylinderAxisZ = np.array([biggerFibulaDentalImplantCylinderTransformMatrix.GetElement(0,2),
        biggerFibulaDentalImplantCylinderTransformMatrix.GetElement(1,2),biggerFibulaDentalImplantCylinderTransformMatrix.GetElement(2,2)])
      heightOfBiggerFibulaDentalImplantCylinder = float(biggerFibulaDentalImplantCylinderModel.GetAttribute('height'))
      #fibulaDentalImplantCylinderTransform.Translate(heightOfBiggerFibulaDentalImplantCylinder/2*biggerFibulaDentalImplantCylinderAxisZ)

      fibulaDentalImplantCylinderTransformNode.SetMatrixTransformToParent(fibulaDentalImplantCylinderTransform.GetMatrix())

      fibulaDentalImplantCylinderTransformNode.UpdateScene(slicer.mrmlScene)

      fibulaDentalImplantCylinderModel.SetAndObserveTransformNodeID(fibulaDentalImplantCylinderTransformNode.GetID())
      biggerFibulaDentalImplantCylinderModel.SetAndObserveTransformNodeID(fibulaDentalImplantCylinderTransformNode.GetID())
      
      fibulaDentalImplantCylinderTransformNodeItemID = shNode.GetItemByDataNode(fibulaDentalImplantCylinderTransformNode)
      shNode.SetItemParent(fibulaDentalImplantCylinderTransformNodeItemID, fibulaDentalImplantsCylindersTransformsFolder)

  def makeBooleanOperationsToFibulaSurgicalGuideBase(self):
    parameterNode = self.getParameterNode()
    fibulaSurgicalGuideBaseModel = parameterNode.GetNodeReference("fibulaSurgicalGuideBaseModel")
    dentalImplantsPlanningAndFibulaDrillGuidesChecked = parameterNode.GetParameter("dentalImplantsPlanningAndFibulaDrillGuides") == "True"

    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    fibulaCylindersModelsFolder = shNode.GetItemByName("Fibula Cylinders Models")
    cylindersModelsList = createListFromFolderID(fibulaCylindersModelsFolder)
    miterBoxesModelsFolder = shNode.GetItemByName("miterBoxes Models")
    miterBoxesModelsList = createListFromFolderID(miterBoxesModelsFolder)
    biggerMiterBoxesModelsFolder = shNode.GetItemByName("biggerMiterBoxes Models")
    biggerMiterBoxesModelsList = createListFromFolderID(biggerMiterBoxesModelsFolder)
    fibulaDentalImplantsCylindersModelsFolder = shNode.GetItemByName("Fibula Dental Implants Cylinders Models")
    fibulaDentalImplantsCylindersModelsList = createListFromFolderID(fibulaDentalImplantsCylindersModelsFolder)
    biggerFibulaDentalImplantsCylindersModelsFolder = shNode.GetItemByName("Bigger Fibula Dental Implants Cylinders Models")
    biggerFibulaDentalImplantsCylindersModelsList = createListFromFolderID(biggerFibulaDentalImplantsCylindersModelsFolder)

    combineModelsLogic = slicer.modules.combinemodels.widgetRepresentation().self().logic

    surgicalGuideModel = slicer.modules.models.logic().AddModel(fibulaSurgicalGuideBaseModel.GetPolyData())
    surgicalGuideModel.SetName(slicer.mrmlScene.GetUniqueNameByString('FibulaSurgicalGuidePrototype'))
    surgicalGuideModelItemID = shNode.GetItemByDataNode(surgicalGuideModel)
    shNode.SetItemParent(surgicalGuideModelItemID, self.getMandibleReconstructionFolderItemID())

    displayNode = surgicalGuideModel.GetDisplayNode()
    fibulaViewNode = slicer.mrmlScene.GetSingletonNode(self.FIBULA_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
    displayNode.AddViewNodeID(fibulaViewNode.GetID())

    for i in range(len(biggerMiterBoxesModelsList)):
      combineModelsLogic.process(surgicalGuideModel, biggerMiterBoxesModelsList[i], surgicalGuideModel, 'union')

    if dentalImplantsPlanningAndFibulaDrillGuidesChecked:
      for i in range(len(biggerFibulaDentalImplantsCylindersModelsList)):
        combineModelsLogic.process(surgicalGuideModel, biggerFibulaDentalImplantsCylindersModelsList[i], surgicalGuideModel, 'union')

    for i in range(len(cylindersModelsList)):
      combineModelsLogic.process(surgicalGuideModel, cylindersModelsList[i], surgicalGuideModel, 'difference')

    for i in range(len(miterBoxesModelsList)):
      combineModelsLogic.process(surgicalGuideModel, miterBoxesModelsList[i], surgicalGuideModel, 'difference')

    if dentalImplantsPlanningAndFibulaDrillGuidesChecked:
      for i in range(len(fibulaDentalImplantsCylindersModelsList)):
        combineModelsLogic.process(surgicalGuideModel, fibulaDentalImplantsCylindersModelsList[i], surgicalGuideModel, 'difference')

    if surgicalGuideModel.GetPolyData().GetNumberOfPoints() == 0:
      slicer.mrmlScene.RemoveNode(surgicalGuideModel)
      slicer.util.errorDisplay("ERROR: Boolean operations to make fibula surgical guide failed")

  def createMandibleCylindersFiducialList(self):
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    mandibleCylindersFiducialsListsFolder = shNode.GetItemByName("Mandible Cylinders Fiducials Lists")
    if not mandibleCylindersFiducialsListsFolder:
      mandibleCylindersFiducialsListsFolder = shNode.CreateFolderItem(self.getMandibleReconstructionFolderItemID(),"Mandible Cylinders Fiducials Lists")
    
    mandibleFiducialListNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLMarkupsFiducialNode")
    mandibleFiducialListNode.SetName("temp")
    slicer.mrmlScene.AddNode(mandibleFiducialListNode)
    slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(mandibleFiducialListNode)
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    mandibleFiducialListNodeItemID = shNode.GetItemByDataNode(mandibleFiducialListNode)
    shNode.SetItemParent(mandibleFiducialListNodeItemID, mandibleCylindersFiducialsListsFolder)
    mandibleFiducialListNode.SetName(slicer.mrmlScene.GetUniqueNameByString("mandibleCylindersFiducialsList"))

    displayNode = mandibleFiducialListNode.GetDisplayNode()
    mandibleViewNode = slicer.mrmlScene.GetSingletonNode(self.MANDIBLE_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
    displayNode.AddViewNodeID(mandibleViewNode.GetID())

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
    if sawBoxesModelsFolder:
      shNode.RemoveItem(sawBoxesModelsFolder)
    biggerSawBoxesModelsFolder = shNode.GetItemByName("biggerSawBoxes Models")
    if biggerSawBoxesModelsFolder:
      shNode.RemoveItem(biggerSawBoxesModelsFolder)
    sawBoxesPlanesFolder = shNode.GetItemByName("sawBoxes Planes")
    if sawBoxesPlanesFolder:
      shNode.RemoveItem(sawBoxesPlanesFolder)
    sawBoxesTransformsFolder = shNode.GetItemByName("sawBoxes Transforms")
    if sawBoxesTransformsFolder:
      shNode.RemoveItem(sawBoxesTransformsFolder)
    sawBoxesModelsFolder = shNode.CreateFolderItem(self.getMandibleReconstructionFolderItemID(),"sawBoxes Models")
    biggerSawBoxesModelsFolder = shNode.CreateFolderItem(self.getMandibleReconstructionFolderItemID(),"biggerSawBoxes Models")
    sawBoxesPlanesFolder = shNode.CreateFolderItem(self.getMandibleReconstructionFolderItemID(),"sawBoxes Planes")
    sawBoxesTransformsFolder = shNode.CreateFolderItem(self.getMandibleReconstructionFolderItemID(),"sawBoxes Transforms")
    intersectionsFolder = shNode.CreateFolderItem(self.getMandibleReconstructionFolderItemID(),"Intersections")
    pointsIntersectionsFolder = shNode.CreateFolderItem(self.getMandibleReconstructionFolderItemID(),"Points Intersections")

    mandibleViewNode = slicer.mrmlScene.GetSingletonNode(self.MANDIBLE_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")

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
      biggerSawBoxDisplayNode.SetVisibility2D(True)

      sawBoxPlane.SetAxes([1,0,0],[0,1,0],[0,0,1])
      sawBoxPlane.SetOrigin([0,0,0])
      sawBoxPlane.SetAttribute("isSawBoxPlane","True")
      sawBoxPlane.SetPlaneType(slicer.vtkMRMLMarkupsPlaneNode.PlaneType3Points)

      displayNode = sawBoxPlane.GetDisplayNode()
      mandibleViewNode = slicer.mrmlScene.GetSingletonNode(self.MANDIBLE_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
      displayNode.AddViewNodeID(mandibleViewNode.GetID())
      displayNode.SetGlyphScale(self.PLANE_GLYPH_SCALE)
      displayNode.SetOpacity(0)
      displayNode.HandlesInteractiveOn()
      displayNode.RotationHandleVisibilityOn()
      displayNode.TranslationHandleVisibilityOn()
      displayNode.ScaleHandleVisibilityOff()
      displayNode.SetTranslationHandleComponentVisibility(True,True,False,False)
      displayNode.SetRotationHandleComponentVisibility(False,False,True,False)

      mandiblePlaneMatrix = vtk.vtkMatrix4x4()
      mandibularPlanesList[i].GetObjectToWorldMatrix(mandiblePlaneMatrix)
      mandiblePlaneZ = np.array([mandiblePlaneMatrix.GetElement(0,2),mandiblePlaneMatrix.GetElement(1,2),mandiblePlaneMatrix.GetElement(2,2)])
      
      if i == 0:
        intersectionModel = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Intersection%d' % i)
      else:
        intersectionModel = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Intersection%d' % (len(mandibularPlanesList)-1))
      intersectionModel.CreateDefaultDisplayNodes()
      getNearestIntersectionBetweenModelAnd1Plane(mandibleModelNode,mandibularPlanesList[i],intersectionModel)
      
      curvePlanarConvexityDirection = [0,0,0]
      vtk.vtkMath.Cross(mandiblePlaneZ, bestFittingPlaneNormalOfCurvePoints, curvePlanarConvexityDirection)

      if intersectionModel.GetPolyData().GetNumberOfPoints() != 0:
        intersectionModelCentroid = getCentroid(intersectionModel)
        if i == 0:
          pointsIntersectionModel = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Points Intersection%d' % i)
        else:
          pointsIntersectionModel = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Points Intersection%d' % (len(mandibularPlanesList)-1))
        pointsIntersectionModel.CreateDefaultDisplayNodes()
        getIntersectionBetweenModelAnd1PlaneWithNormalAndOrigin_2(intersectionModel,bestFittingPlaneNormalOfCurvePoints,intersectionModelCentroid,pointsIntersectionModel)
        pointOfIntersection = getPointOfATwoPointsModelThatMakesLineDirectionSimilarToVector(pointsIntersectionModel,curvePlanarConvexityDirection)
      else:
        pointOfIntersection = [0,0,0]
        mandibularPlanesList[i].GetOrigin(pointOfIntersection)
      intersectionModelItemID = shNode.GetItemByDataNode(intersectionModel)
      shNode.SetItemParent(intersectionModelItemID, intersectionsFolder)
      pointsIntersectionModelItemID = shNode.GetItemByDataNode(pointsIntersectionModel)
      shNode.SetItemParent(pointsIntersectionModelItemID, pointsIntersectionsFolder)

      if intersectionModel.GetPolyData().GetNumberOfPoints() != 0:
        sawBoxDirection = getAverageNormalFromModelPoint2(mandibleModelNode,pointOfIntersection)
        if sawBoxDirection is None:
          sawBoxDirection = np.zeros(3)
          sawBoxDirection[1] = 1
        #sawBoxDirection = (pointOfIntersection-intersectionModelCentroid)/np.linalg.norm(pointOfIntersection-intersectionModelCentroid)
      else:
        sawBoxDirection = curvePlanarConvexityDirection

      sawBoxAxisX = [0,0,0]
      sawBoxAxisY =  [0,0,0]
      sawBoxAxisZ = mandiblePlaneZ
      vtk.vtkMath.Cross(sawBoxDirection, sawBoxAxisZ, sawBoxAxisX)
      sawBoxAxisX = sawBoxAxisX/np.linalg.norm(sawBoxAxisX)
      vtk.vtkMath.Cross(sawBoxAxisZ, sawBoxAxisX, sawBoxAxisY)
      sawBoxAxisY = sawBoxAxisY/np.linalg.norm(sawBoxAxisY)

      if i == 0:
        sawBoxAxisXTranslation = 0
        sawBoxAxisYTranslation = biggerSawBoxHeight/2+biggerSawBoxDistanceToMandible
        sawBoxAxisZTranslation = sawBoxSlotWidth/2
      else:
        sawBoxAxisXTranslation = 0
        sawBoxAxisYTranslation = biggerSawBoxHeight/2+biggerSawBoxDistanceToMandible
        sawBoxAxisZTranslation = -sawBoxSlotWidth/2
      sawBoxAxisOrigin = pointOfIntersection + sawBoxAxisX*sawBoxAxisXTranslation + sawBoxAxisY*sawBoxAxisYTranslation + sawBoxAxisZ*sawBoxAxisZTranslation

      sawBoxPlane.SetAxes(sawBoxAxisX,sawBoxAxisY,sawBoxAxisZ)
      sawBoxPlane.SetOrigin(sawBoxAxisOrigin)

      transformNode = slicer.vtkMRMLLinearTransformNode()
      transformNode.SetName("sawBoxTransform%d" % i)
      slicer.mrmlScene.AddNode(transformNode)

      sawBoxPlaneToWorldMatrix = vtk.vtkMatrix4x4()
      sawBoxPlane.GetObjectToWorldMatrix(sawBoxPlaneToWorldMatrix)
      transformNode.SetMatrixTransformToParent(sawBoxPlaneToWorldMatrix)

      transformNode.UpdateScene(slicer.mrmlScene)

      sawBoxModel.SetAndObserveTransformNodeID(transformNode.GetID())
      biggerSawBoxModel.SetAndObserveTransformNodeID(transformNode.GetID())
      
      transformNodeItemID = shNode.GetItemByDataNode(transformNode)
      shNode.SetItemParent(transformNodeItemID, sawBoxesTransformsFolder)

      observer = sawBoxPlane.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent,self.onSawBoxPlaneMoved)
      self.sawBoxPlaneObserversPlaneNodeIDAndTransformIDList.append([observer,sawBoxPlane.GetID(),transformNode.GetID()])

    if intersectionsFolder:
      shNode.RemoveItem(intersectionsFolder)
    if pointsIntersectionsFolder:
      shNode.RemoveItem(pointsIntersectionsFolder)
    
    self.setRedSliceForBoxModelsDisplayNodes()
    
  def onSawBoxPlaneMoved(self,sourceNode,event):
    for i in range(len(self.sawBoxPlaneObserversPlaneNodeIDAndTransformIDList)):
      if self.sawBoxPlaneObserversPlaneNodeIDAndTransformIDList[i][1] == sourceNode.GetID():
        sawBoxPlane = slicer.mrmlScene.GetNodeByID(self.sawBoxPlaneObserversPlaneNodeIDAndTransformIDList[i][1])
        transformNode = slicer.mrmlScene.GetNodeByID(self.sawBoxPlaneObserversPlaneNodeIDAndTransformIDList[i][2])
        sawBoxPlaneToWorldMatrix = vtk.vtkMatrix4x4()
        sawBoxPlane.GetObjectToWorldMatrix(sawBoxPlaneToWorldMatrix)
        transformNode.SetMatrixTransformToParent(sawBoxPlaneToWorldMatrix)

  def onDentalImplantPlaneMoved(self,sourceNode,event):
    parameterNode = self.getParameterNode()
    makeAllDentalImplanCylindersParallelChecked = parameterNode.GetParameter("makeAllDentalImplanCylindersParallel") == "True"

    orientationToCopyIndex = 0
    copyOrientationIndices = []
    
    for i in range(len(self.dentalImplantPlaneObserversPlaneNodeIDAndTransformIDList)):
      if self.dentalImplantPlaneObserversPlaneNodeIDAndTransformIDList[i][1] == sourceNode.GetID():
        orientationToCopyIndex = i
        dentalImplantPlane = slicer.mrmlScene.GetNodeByID(self.dentalImplantPlaneObserversPlaneNodeIDAndTransformIDList[i][1])
        transformNode = slicer.mrmlScene.GetNodeByID(self.dentalImplantPlaneObserversPlaneNodeIDAndTransformIDList[i][2])
        dentalImplantPlaneToWorldMatrix = vtk.vtkMatrix4x4()
        dentalImplantPlane.GetObjectToWorldMatrix(dentalImplantPlaneToWorldMatrix)
        transformNode.SetMatrixTransformToParent(dentalImplantPlaneToWorldMatrix)
      else:
        copyOrientationIndices.append(i)

    
    if makeAllDentalImplanCylindersParallelChecked:
      copyFromPlane = slicer.mrmlScene.GetNodeByID(
          self.dentalImplantPlaneObserversPlaneNodeIDAndTransformIDList[orientationToCopyIndex][1]
      )
      copyFromPlaneObserverTag = (
          self.dentalImplantPlaneObserversPlaneNodeIDAndTransformIDList[orientationToCopyIndex][0]
      )

      #copyFromPlane.RemoveObserver(copyFromPlaneObserverTag)

      orientationToCopyMatrix = vtk.vtkMatrix4x4()
      copyFromPlane.GetObjectToWorldMatrix(orientationToCopyMatrix)

      for i in range(len(copyOrientationIndices)):
        copyToIndex = copyOrientationIndices[i]
        observerTag = self.dentalImplantPlaneObserversPlaneNodeIDAndTransformIDList[copyToIndex][0]
        currentDentalImplantPlane = slicer.mrmlScene.GetNodeByID(
          self.dentalImplantPlaneObserversPlaneNodeIDAndTransformIDList[copyToIndex][1]
        )
        transformNode = slicer.mrmlScene.GetNodeByID(
          self.dentalImplantPlaneObserversPlaneNodeIDAndTransformIDList[copyToIndex][2]
        )

        currentDentalImplantPlane.RemoveObserver(observerTag)

        currentPlaneToWorld = vtk.vtkMatrix4x4()
        currentDentalImplantPlane.GetObjectToWorldMatrix(currentPlaneToWorld)
        origin = [0,0,0]
        currentPlanePos = [0,0,0,0]
        currentPlaneToWorld.MultiplyPoint(np.append(origin,1.0),currentPlanePos)
        currentPlanePos = currentPlanePos[0:3]

        worldToCurrentPlane = vtk.vtkMatrix4x4()
        vtk.vtkMatrix4x4.Invert(currentPlaneToWorld, worldToCurrentPlane)

        parallelTransform = vtk.vtkTransform()
        parallelTransform.PostMultiply()
        parallelTransform.Concatenate(orientationToCopyMatrix)
        oldTranslation = [0,0,0]
        parallelTransform.GetPosition(oldTranslation)
        parallelTransform.Translate(-oldTranslation[0],-oldTranslation[1],-oldTranslation[2])
        parallelTransform.Translate(currentPlanePos[0],currentPlanePos[1],currentPlanePos[2])

        transformForCurrentDentalImplantPlane = vtk.vtkTransform()
        transformForCurrentDentalImplantPlane.PostMultiply()
        transformForCurrentDentalImplantPlane.Concatenate(worldToCurrentPlane)
        transformForCurrentDentalImplantPlane.Concatenate(parallelTransform)

        for j in range(3):
          oldPos = currentDentalImplantPlane.GetNthControlPointPosition(j)
          newPos = [0,0,0]
          transformForCurrentDentalImplantPlane.TransformPoint(oldPos,newPos)
          currentDentalImplantPlane.SetNthControlPointPosition(j,newPos)

        observerTag = currentDentalImplantPlane.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent,self.onDentalImplantPlaneMoved)
        self.dentalImplantPlaneObserversPlaneNodeIDAndTransformIDList[copyToIndex][0] = observerTag

        transformNode.SetMatrixTransformToParent(parallelTransform.GetMatrix())

      #observerTag = copyFromPlane.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent,self.onDentalImplantPlaneMoved)
      #self.dentalImplantPlaneObserversPlaneNodeIDAndTransformIDList[orientationToCopyIndex][0] = observerTag
    
    updateOnDentalImplantPlanesMovement = parameterNode.GetParameter("updateOnDentalImplantPlanesMovement") == "True"

    if updateOnDentalImplantPlanesMovement:
      self.updateFibuladentalImplantsTimer.start()

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
    shNode.SetItemParent(surgicalGuideModelItemID, self.getMandibleReconstructionFolderItemID())

    displayNode = surgicalGuideModel.GetDisplayNode()
    mandibleViewNode = slicer.mrmlScene.GetSingletonNode(self.MANDIBLE_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
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
    intersectionsFolder = shNode.CreateFolderItem(self.getMandibleReconstructionFolderItemID(),"Intersections")

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

    fibulaLine.SetNthControlPointPosition(0,lineStartPos)
    fibulaLine.SetNthControlPointPosition(1,lineEndPos)

    if intersectionsFolder:
      shNode.RemoveItem(intersectionsFolder)

  def setBackgroundVolumeFromID(self,scalarVolumeID):
    redSliceLogic = slicer.app.layoutManager().sliceWidget('Red').sliceLogic()
    redSliceLogic.GetSliceCompositeNode().SetBackgroundVolumeID(scalarVolumeID)
    greenSliceLogic = slicer.app.layoutManager().sliceWidget('Green').sliceLogic()
    greenSliceLogic.GetSliceCompositeNode().SetBackgroundVolumeID(scalarVolumeID)
    yellowSliceLogic = slicer.app.layoutManager().sliceWidget('Yellow').sliceLogic()
    yellowSliceLogic.GetSliceCompositeNode().SetBackgroundVolumeID(scalarVolumeID)

    slicer.util.resetSliceViews()

  def create3DModelOfTheReconstruction(self):
    import time
    startTime = time.time()
    logging.info('Processing started')

    parameterNode = self.getParameterNode()
    previousMandibleReconstructionModel = parameterNode.GetNodeReference('mandibleReconstructionModel')

    if previousMandibleReconstructionModel:
      slicer.mrmlScene.RemoveNode(previousMandibleReconstructionModel)

    if parameterNode.GetParameter("useNonDecimatedBoneModelsForPreview") != "True":
      parameterNode.SetParameter("useNonDecimatedBoneModelsForPreview","True")
      self.onGenerateFibulaPlanesTimerTimeout()

    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    transformedFibulaPiecesFolder = shNode.GetItemByName("Transformed Fibula Pieces")
    transformedFibulaPiecesList = createListFromFolderID(transformedFibulaPiecesFolder)
    planeList = createListFromFolderID(self.getMandiblePlanesFolderItemID())

    if len(transformedFibulaPiecesList) == 0:
      return

    mandibleReconstructionModel = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Mandible Reconstruction')
    mandibleReconstructionModel.CreateDefaultDisplayNodes()

    displayNode = mandibleReconstructionModel.GetDisplayNode()
    mandibleViewNode = slicer.mrmlScene.GetSingletonNode(self.MANDIBLE_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
    displayNode.AddViewNodeID(mandibleViewNode.GetID())

    parameterNode.SetNodeReferenceID("mandibleReconstructionModel", mandibleReconstructionModel.GetID())

    mandibleReconstructionModelItemID = shNode.GetItemByDataNode(mandibleReconstructionModel)
    shNode.SetItemParent(mandibleReconstructionModelItemID, self.getMandibleReconstructionFolderItemID())

    startingObject, listOfObjectsToUnite = self.getReconstructionObjectsPreparedForBooleanUnion()

    correctionsCounter = 0
    correctionsCounterLimit = 5
    i = 0
    lastProblematicPlaneIndex = -1
    lastSuccessfulUnionResult = vtk.vtkPolyData()
    currentResult = vtk.vtkPolyData()
    while i < len(listOfObjectsToUnite) and correctionsCounter < correctionsCounterLimit:
      tempResultsList = []
      booleanFilter = slicer.vtkPolyDataBooleanFilter()
      booleanFilter.SetOperModeToUnion()
      if i==0:
        firstObjectWithNormals = calculateNormals(startingObject)
        booleanFilter.SetInputData(0, firstObjectWithNormals)
        #model = slicer.modules.models.logic().AddModel(firstObjectWithNormals)
        #model.SetName(slicer.mrmlScene.GetUniqueNameByString('firstObjectWithNormals'))
      else:
        firstObjectWithNormals = calculateNormals(currentResult)
        booleanFilter.SetInputData(0, firstObjectWithNormals)
        #model = slicer.modules.models.logic().AddModel(firstObjectWithNormals)
        #model.SetName(slicer.mrmlScene.GetUniqueNameByString('firstObjectWithNormals'))
      secondObjectWithNormals = calculateNormals(listOfObjectsToUnite[i])
      booleanFilter.SetInputData(1, secondObjectWithNormals)
      #model = slicer.modules.models.logic().AddModel(secondObjectWithNormals)
      #model.SetName(slicer.mrmlScene.GetUniqueNameByString('secondObjectWithNormals'))
      booleanFilter.Update()
      #model = slicer.modules.models.logic().AddModel(booleanFilter.GetOutput())
      #model.SetName(slicer.mrmlScene.GetUniqueNameByString('UnionOfNonInverted'))

      resultPolydata = vtk.vtkPolyData()
      resultPolydata.DeepCopy(booleanFilter.GetOutput())
      tempResultsList.append([resultPolydata,calculateSurfaceArea(resultPolydata)])
      
      booleanFilter.SetOperModeToIntersection()
      secondObjectWithNormals = calculateNormals(listOfObjectsToUnite[i],flip=True)
      booleanFilter.SetInputData(1, secondObjectWithNormals)
      booleanFilter.Update()
      #model = slicer.modules.models.logic().AddModel(booleanFilter.GetOutput())
      #model.SetName(slicer.mrmlScene.GetUniqueNameByString('IntersectionSecondInverted'))
      
      resultPolydata = vtk.vtkPolyData()
      resultPolydata.DeepCopy(booleanFilter.GetOutput())
      tempResultsList.append([resultPolydata,calculateSurfaceArea(resultPolydata)])

      booleanFilter.SetOperModeToIntersection()
      if i == 0:
        firstObjectWithNormals = calculateNormals(startingObject,flip=True)
        booleanFilter.SetInputData(0, firstObjectWithNormals)
      else:
        firstObjectWithNormals = calculateNormals(currentResult,flip=True)
        booleanFilter.SetInputData(0, firstObjectWithNormals)
      secondObjectWithNormals = calculateNormals(listOfObjectsToUnite[i])
      booleanFilter.SetInputData(1, secondObjectWithNormals)
      booleanFilter.Update()
      #model = slicer.modules.models.logic().AddModel(booleanFilter.GetOutput())
      #model.SetName(slicer.mrmlScene.GetUniqueNameByString('IntersectionFirstInverted'))

      resultPolydata = vtk.vtkPolyData()
      resultPolydata.DeepCopy(booleanFilter.GetOutput())
      tempResultsList.append([resultPolydata,calculateSurfaceArea(resultPolydata)])

      booleanFilter.SetOperModeToIntersection()
      secondObjectWithNormals = calculateNormals(listOfObjectsToUnite[i],flip=True)
      booleanFilter.SetInputData(1, secondObjectWithNormals)
      booleanFilter.Update()
      #model = slicer.modules.models.logic().AddModel(booleanFilter.GetOutput())
      #model.SetName(slicer.mrmlScene.GetUniqueNameByString('IntersectionBothInverted'))
      
      resultPolydata = vtk.vtkPolyData()
      resultPolydata.DeepCopy(booleanFilter.GetOutput())
      tempResultsList.append([resultPolydata,calculateSurfaceArea(resultPolydata)])

      tempResultsList.sort(key = lambda item : item[1],reverse=True)

      #print(i)
      #print(tempResultsList[0][1])
      
      if tempResultsList[0][1] <= calculateSurfaceArea(currentResult):
      #if False:
        origin = np.zeros(3)
        normal = np.zeros(3)
        planeList[i].GetOrigin(origin)
        #print(origin)
        planeList[i].GetNormal(normal)
        origin += normal*0.01
        #print(origin)

        correctionsCounter += 1

        lastProblematicPlaneIndex = i
        lastSuccessfulUnionResult.ShallowCopy(currentResult)

        self.removeMandiblePlaneObservers()
        planeList[i].SetOrigin(origin)
        self.addMandiblePlaneObservers()

        self.onGenerateFibulaPlanesTimerTimeout()

        startingObject, listOfObjectsToUnite = self.getReconstructionObjectsPreparedForBooleanUnion()

        i = 0
        currentResult = vtk.vtkPolyData()
      else:
        currentResult = tempResultsList[0][0]

        #model = slicer.modules.models.logic().AddModel(currentResult)
        #model.SetName(slicer.mrmlScene.GetUniqueNameByString('currentResult'))

        i+=1

    stopTime = time.time()
    logging.info('Processing completed in {0:.2f} seconds\n'.format(stopTime-startTime))
    
    if correctionsCounter == correctionsCounterLimit:
      mandibleReconstructionModel.SetAndObservePolyData(lastSuccessfulUnionResult)
      slicer.util.errorDisplay(f"""The number of tries to create the mandible model were exceded.
Please try changing the position of {planeList[lastProblematicPlaneIndex].GetName()}.
Then click the update button so the fibulaPieces and resected mandible are recalculated.
Then click 'Create 3D model of reconstruction...' again.""")
    else:
      mandibleReconstructionModel.SetAndObservePolyData(calculateNormals(currentResult))

  def getReconstructionObjectsPreparedForBooleanUnion(self):
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    planeList = createListFromFolderID(self.getMandiblePlanesFolderItemID())
    transformedFibulaPiecesFolder = shNode.GetItemByName("Transformed Fibula Pieces")
    transformedFibulaPiecesList = createListFromFolderID(transformedFibulaPiecesFolder)
    cutBonesList = createListFromFolderID(shNode.GetItemByName("Cut Bones"))

    scaledFibulaPiecesList = []
    for i in range(len(transformedFibulaPiecesList)):
      or0 = np.zeros(3)
      planeList[i].GetOrigin(or0)
      or1 = np.zeros(3)
      planeList[i+1].GetOrigin(or1)
      origin = (or0+or1)/2
      #origin = getCentroid(transformedFibulaPiecesList[i])

      scaleTransform = vtk.vtkTransform()
      scaleTransform.PostMultiply()
      scaleTransform.Translate(-origin)
      #Just scale them enough so that boolean union is successful
      scaleTransform.Scale(1.0001, 1.0001, 1.0001)
      scaleTransform.Translate(origin)

      scaleTransformer = vtk.vtkTransformPolyDataFilter()
      scaleTransformer.SetTransform(scaleTransform)
      scaleTransformer.SetInputData(transformedFibulaPiecesList[i].GetPolyData())
      scaleTransformer.Update()

      scaledFibulaPiece = vtk.vtkPolyData()
      scaledFibulaPiece.ShallowCopy(scaleTransformer.GetOutput())

      scaledFibulaPiecesList.append(scaledFibulaPiece)

    mandiblePlaneOrigin = np.zeros(3)
    planeList[0].GetOrigin(mandiblePlaneOrigin)
    sideOneConnectivityFilter = vtk.vtkConnectivityFilter()
    sideOneConnectivityFilter.SetInputData(cutBonesList[-1].GetPolyData())
    sideOneConnectivityFilter.SetExtractionModeToClosestPointRegion()
    sideOneConnectivityFilter.SetClosestPoint(mandiblePlaneOrigin)
    sideOneConnectivityFilter.Update()

    sideOneFillHolesFilter = vtk.vtkFillHolesFilter()
    sideOneFillHolesFilter.SetInputData(sideOneConnectivityFilter.GetOutput())
    sideOneFillHolesFilter.SetHoleSize(50)
    sideOneFillHolesFilter.Update()

    mandiblePlaneOrigin = np.zeros(3)
    planeList[-1].GetOrigin(mandiblePlaneOrigin)
    sideTwoConnectivityFilter = vtk.vtkConnectivityFilter()
    sideTwoConnectivityFilter.SetInputData(cutBonesList[-1].GetPolyData())
    sideTwoConnectivityFilter.SetExtractionModeToClosestPointRegion()
    sideTwoConnectivityFilter.SetClosestPoint(mandiblePlaneOrigin)
    sideTwoConnectivityFilter.Update()

    sideTwoFillHolesFilter = vtk.vtkFillHolesFilter()
    sideTwoFillHolesFilter.SetInputData(sideTwoConnectivityFilter.GetOutput())
    sideTwoFillHolesFilter.SetHoleSize(50)
    sideTwoFillHolesFilter.Update()

    startingObject = sideOneFillHolesFilter.GetOutput()
    listOfObjectsToUnite = scaledFibulaPiecesList + [sideTwoFillHolesFilter.GetOutput()]

    return startingObject, listOfObjectsToUnite

  def createPlateCurve(self):
    curveNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLMarkupsCurveNode")
    curveNode.SetName("temp")
    slicer.mrmlScene.AddNode(curveNode)
    slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(curveNode)
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    curveNodeItemID = shNode.GetItemByDataNode(curveNode)
    shNode.SetItemParent(curveNodeItemID, self.getParentFolderItemID())
    curveNode.SetName(slicer.mrmlScene.GetUniqueNameByString("plateCurve"))

    displayNode = curveNode.GetDisplayNode()
    mandibleViewNode = slicer.mrmlScene.GetSingletonNode("1", "vtkMRMLViewNode")
    displayNode.AddViewNodeID(mandibleViewNode.GetID())

    #setup placement
    slicer.modules.markups.logic().SetActiveListID(curveNode)
    interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
    interactionNode.SwitchToSinglePlaceMode()

  def createCustomPlate(self):
    #self.create3DModelOfTheReconstruction()

    parameterNode = self.getParameterNode()
    plateCurve = parameterNode.GetNodeReference("plateCurve")

    mandibleReconstructionModel = parameterNode.GetNodeReference("mandibleReconstructionModel")
    if mandibleReconstructionModel is None:
      self.create3DModelOfTheReconstruction()
      mandibleReconstructionModel = parameterNode.GetNodeReference("mandibleReconstructionModel")

    plateCrossSectionalWidth = float(parameterNode.GetParameter("plateCrossSectionalWidth"))
    plateCrossSectionalLength = float(parameterNode.GetParameter("plateCrossSectionalLength"))
    plateCrossSectionalBevelRadiusPorcentage = float(parameterNode.GetParameter("plateCrossSectionalBevelRadiusPorcentage"))
    plateTipsBevelRadius = float(parameterNode.GetParameter("plateTipsBevelRadius"))

    #create cross sectional area of the curve
    cornerOfRectangleXY = np.array([plateCrossSectionalWidth/2, plateCrossSectionalLength/2])
    
    if (plateCrossSectionalWidth < plateCrossSectionalLength):
      plateCrossSectionalBevelRadius = (plateCrossSectionalBevelRadiusPorcentage/100)*plateCrossSectionalWidth
    else:
      plateCrossSectionalBevelRadius = (plateCrossSectionalBevelRadiusPorcentage/100)*plateCrossSectionalLength

    twoJoinPoinstOfBevelAndLinesXY = np.array(
            [
                [cornerOfRectangleXY[0] - plateCrossSectionalBevelRadius, cornerOfRectangleXY[1]],
                [cornerOfRectangleXY[0], cornerOfRectangleXY[1] - plateCrossSectionalBevelRadius]
            ]
        )

    allJoinPointsOfBevelsAndLinesXY = np.array(
            [
                twoJoinPoinstOfBevelAndLinesXY[0],
                twoJoinPoinstOfBevelAndLinesXY[1],
                [twoJoinPoinstOfBevelAndLinesXY[1][0], -twoJoinPoinstOfBevelAndLinesXY[1][1]],
                [twoJoinPoinstOfBevelAndLinesXY[0][0], -twoJoinPoinstOfBevelAndLinesXY[0][1]],
                -twoJoinPoinstOfBevelAndLinesXY[0],
                -twoJoinPoinstOfBevelAndLinesXY[1],
                [-twoJoinPoinstOfBevelAndLinesXY[1][0], twoJoinPoinstOfBevelAndLinesXY[1][1]],
                [-twoJoinPoinstOfBevelAndLinesXY[0][0], twoJoinPoinstOfBevelAndLinesXY[0][1]]
            ]
        )

    bevelCircleArcCenterXY = np.array(
                [cornerOfRectangleXY[0] - plateCrossSectionalBevelRadius, cornerOfRectangleXY[1] - plateCrossSectionalBevelRadius]
        )
    
    bevelCircleArcsCenterXY = np.array(
            [
                bevelCircleArcCenterXY,
                [bevelCircleArcCenterXY[0], -bevelCircleArcCenterXY[1]],
                [-bevelCircleArcCenterXY[0], -bevelCircleArcCenterXY[1]],
                [-bevelCircleArcCenterXY[0], bevelCircleArcCenterXY[1]]
            ]
        )

    #createBevelArcs
    bevelArcsPointList = []
    #segments 0 to n
    nOfsegments = 5
    for i in range(0,len(allJoinPointsOfBevelsAndLinesXY),2):
      bevelArcPoints = self.createAlmostQuarterArcFromPointsAndCenter(allJoinPointsOfBevelsAndLinesXY[i],
        allJoinPointsOfBevelsAndLinesXY[i+1],bevelCircleArcsCenterXY[i//2],nOfsegments)
      bevelArcsPointList.append(bevelArcPoints)

    if len(bevelArcsPointList[0]) != 0:
      arcSegmentLength = np.linalg.norm(bevelArcsPointList[0][0] - allJoinPointsOfBevelsAndLinesXY[0])
    else:
      arcSegmentLength = np.linalg.norm(allJoinPointsOfBevelsAndLinesXY[1] - allJoinPointsOfBevelsAndLinesXY[0])

    allJoinPointsOfBevelsAndLinesXYList = allJoinPointsOfBevelsAndLinesXY.tolist()
    allJoinPointsOfBevelsAndLinesXYListFirstLast = allJoinPointsOfBevelsAndLinesXYList[1:] + [allJoinPointsOfBevelsAndLinesXYList[0]]
    linesPointList = []
    for i in range(0,len(allJoinPointsOfBevelsAndLinesXYListFirstLast),2):
      linePoints = self.createLineFromPointsAndDistanceBetweenPoints(allJoinPointsOfBevelsAndLinesXYListFirstLast[i],
        allJoinPointsOfBevelsAndLinesXYListFirstLast[i+1],arcSegmentLength)
      linesPointList.append(linePoints)

    polygonPoints = []
    for i in range(4):
      polygonPoints += [np.array(allJoinPointsOfBevelsAndLinesXYList[2*i])] + bevelArcsPointList[i] + [np.array(allJoinPointsOfBevelsAndLinesXYList[2*i+1])] + linesPointList[i]


    #Resample input curve
    plateCurveResampled = slicer.mrmlScene.CreateNodeByClass("vtkMRMLMarkupsCurveNode")
    plateCurveResampled.SetName("plateCurveResampled")
    slicer.mrmlScene.AddNode(plateCurveResampled)
    slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(plateCurveResampled)

    points = vtk.vtkPoints()
    curvePointsArray = slicer.util.arrayFromMarkupsControlPoints(plateCurve)
    vtkPointsData = vtk.util.numpy_support.numpy_to_vtk(curvePointsArray, deep=1)
    points.SetNumberOfPoints(len(curvePointsArray))
    points.SetData(vtkPointsData)
    plateCurveResampled.SetControlPointPositionsWorld(points)

    plateCurveResampled.ResampleCurveWorld(10)


    cellArray = vtk.vtkCellArray()
    points = vtk.vtkPoints()
    pointID = 0

    startIndex = 0
    curveMatrix = vtk.vtkMatrix4x4()
    plateCurveResampled.GetCurvePointToWorldTransformAtPointIndex(startIndex,curveMatrix)
    plateCurveResampledX = np.array([curveMatrix.GetElement(0,0),curveMatrix.GetElement(1,0),curveMatrix.GetElement(2,0)])
    plateCurveResampledY = np.array([curveMatrix.GetElement(0,1),curveMatrix.GetElement(1,1),curveMatrix.GetElement(2,1)])
    plateCurveResampledZ = np.array([curveMatrix.GetElement(0,2),curveMatrix.GetElement(1,2),curveMatrix.GetElement(2,2)])
    plateCurveResampledOrigin = np.array([curveMatrix.GetElement(0,3),curveMatrix.GetElement(1,3),curveMatrix.GetElement(2,3)])

    
    normalsOfMandibleReconstructionModel = slicer.util.arrayFromModelPointData(mandibleReconstructionModel, 'Normals')
    
    pointsLocator = vtk.vtkPointLocator()
    pointsLocator.SetDataSet(mandibleReconstructionModel.GetPolyData())
    pointsLocator.BuildLocator()

    
    pointIDOfClosestPoint = pointsLocator.FindClosestPoint(plateCurveResampledOrigin)
    normalAtPointID = normalsOfMandibleReconstructionModel[pointIDOfClosestPoint]
    
    vectorSimilarToPlateCurveY = [0,0,0]
    vtk.vtkMath.Cross(plateCurveResampledZ, normalAtPointID, vectorSimilarToPlateCurveY)
    vectorSimilarToPlateCurveY = vectorSimilarToPlateCurveY/np.linalg.norm(vectorSimilarToPlateCurveY)

    epsilon = 0.0001
    angleRadians = vtk.vtkMath.AngleBetweenVectors(plateCurveResampledY,vectorSimilarToPlateCurveY)
    if not (vtk.vtkMath.Dot(plateCurveResampledY,vectorSimilarToPlateCurveY) >= 1.0 - epsilon):
      rotationAxis = [0,0,0]
      vtk.vtkMath.Cross(plateCurveResampledY, vectorSimilarToPlateCurveY, rotationAxis)
      if (vtk.vtkMath.Norm(rotationAxis) < epsilon):
        #plateCurveResampledY + vectorSimilarToPlateCurveY are facing opposite directions.
        rotationAxis = np.copy(plateCurveResampledZ) 
      rotationAxis = rotationAxis/np.linalg.norm(rotationAxis)
    else:
      rotationAxis = np.copy(plateCurveResampledZ)

    if vtk.vtkMath.Dot(plateCurveResampledZ,rotationAxis) < 0:
      rotationAxisMultiplier = -1
    else:
      rotationAxisMultiplier = 1


    curveToWorldTransform = vtk.vtkTransform()
    curveToWorldTransform.PostMultiply()
    curveToWorldTransform.Concatenate(curveMatrix)
    #rotate around plateCurveResampledOrigin
    curveToWorldTransform.Translate(-plateCurveResampledOrigin)
    curveToWorldTransform.RotateWXYZ(vtk.vtkMath.DegreesFromRadians(angleRadians), rotationAxisMultiplier*plateCurveResampledZ)
    curveToWorldTransform.Translate(plateCurveResampledOrigin)
    curveToWorldTransform.TransformVector([1,0,0],plateCurveResampledX)
    #give offset to be away of the mandibleReconstruction
    curveToWorldTransform.Translate(plateCurveResampledX*plateCrossSectionalWidth/2)

    firstTransformedPolygonPoints = []
    for i in range(len(polygonPoints)):
      transformedPolygonPoint = np.zeros(3)
      curveToWorldTransform.TransformPoint(np.append(polygonPoints[i], 0.0), transformedPolygonPoint)
      firstTransformedPolygonPoints.append(transformedPolygonPoint)

    polygon = vtk.vtkPolygon()
    polygon.GetPointIds().SetNumberOfIds(len(firstTransformedPolygonPoints))
    for i in range(len(firstTransformedPolygonPoints)):
        points.InsertNextPoint(firstTransformedPolygonPoints[i])
        polygon.GetPointIds().SetId(i, pointID)
        pointID += 1

    cellArray.InsertNextCell(polygon)

    curvePoints = slicer.util.arrayFromMarkupsCurvePoints(plateCurveResampled)

    for j in range(1,len(curvePoints)):
      curvePoint = curvePoints[j]
      
      secondTransformedPolygonPoints = []
      
      closestCurvePoint = [0,0,0]
      closestCurvePointIndex = plateCurveResampled.GetClosestPointPositionAlongCurveWorld(curvePoint,closestCurvePoint)
      
      curveMatrix = vtk.vtkMatrix4x4()
      plateCurveResampled.GetCurvePointToWorldTransformAtPointIndex(closestCurvePointIndex,curveMatrix)
      plateCurveResampledX = np.array([curveMatrix.GetElement(0,0),curveMatrix.GetElement(1,0),curveMatrix.GetElement(2,0)])
      plateCurveResampledZ = np.array([curveMatrix.GetElement(0,2),curveMatrix.GetElement(1,2),curveMatrix.GetElement(2,2)])
      plateCurveResampledOrigin = np.array([curveMatrix.GetElement(0,3),curveMatrix.GetElement(1,3),curveMatrix.GetElement(2,3)])

      curveToWorldTransform = vtk.vtkTransform()
      curveToWorldTransform.PostMultiply()
      curveToWorldTransform.Concatenate(curveMatrix)
      #rotate around plateCurveResampledOrigin
      curveToWorldTransform.Translate(-plateCurveResampledOrigin)
      curveToWorldTransform.RotateWXYZ(vtk.vtkMath.DegreesFromRadians(angleRadians), rotationAxisMultiplier*plateCurveResampledZ)
      curveToWorldTransform.Translate(plateCurveResampledOrigin)
      curveToWorldTransform.TransformVector([1,0,0],plateCurveResampledX)
      #give offset to be away of the mandibleReconstruction
      curveToWorldTransform.Translate(plateCurveResampledX*plateCrossSectionalWidth/2)
      
      for i in range(len(polygonPoints)):
        transformedPolygonPoint = np.zeros(3)
        curveToWorldTransform.TransformPoint(np.append(polygonPoints[i], 0.0), transformedPolygonPoint)
        secondTransformedPolygonPoints.append(transformedPolygonPoint)

      if self.pointsOverlap(firstTransformedPolygonPoints,secondTransformedPolygonPoints) == True:
        continue
      
      for i in range(len(secondTransformedPolygonPoints)):
        points.InsertNextPoint(secondTransformedPolygonPoints[i])
        pointID += 1

      for k in range(len(firstTransformedPolygonPoints)):
        polygon = vtk.vtkPolygon()
        polygon.GetPointIds().SetNumberOfIds(3)
        polygon.GetPointIds().SetId(0, k + pointID - len(secondTransformedPolygonPoints))
        polygon.GetPointIds().SetId(2, k + pointID - 2*len(secondTransformedPolygonPoints))
        if k!=(len(firstTransformedPolygonPoints) -1):
          polygon.GetPointIds().SetId(1, k + 1 + pointID - len(secondTransformedPolygonPoints))
        else:
          polygon.GetPointIds().SetId(1, pointID - len(secondTransformedPolygonPoints))
        
        cellArray.InsertNextCell(polygon)
        
        polygon = vtk.vtkPolygon()
        polygon.GetPointIds().SetNumberOfIds(3)
        polygon.GetPointIds().SetId(0, k + pointID - 2*len(secondTransformedPolygonPoints))
        if k!=(len(firstTransformedPolygonPoints) -1):
          polygon.GetPointIds().SetId(1, k + 1 + pointID - len(secondTransformedPolygonPoints))
          polygon.GetPointIds().SetId(2, k + 1 + pointID - 2*len(secondTransformedPolygonPoints))
        else:
          polygon.GetPointIds().SetId(1, pointID - len(secondTransformedPolygonPoints))
          polygon.GetPointIds().SetId(2, pointID - 2*len(secondTransformedPolygonPoints))
        
        cellArray.InsertNextCell(polygon)
      
      firstTransformedPolygonPoints = secondTransformedPolygonPoints.copy()

      if j == (len(curvePoints)-1):
        polygon = vtk.vtkPolygon()
        polygon.GetPointIds().SetNumberOfIds(len(polygonPoints))
        for i in range(len(polygonPoints)):
            polygon.GetPointIds().SetId(i, pointID-len(polygonPoints) +i)
        
        cellArray.InsertNextCell(polygon)

    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)
    polydata.SetPolys(cellArray)

    triangleFilter = vtk.vtkTriangleFilter()
    triangleFilter.SetInputData(polydata)
    triangleFilter.Update()

    extrusionModel = slicer.mrmlScene.CreateNodeByClass("vtkMRMLModelNode")
    slicer.mrmlScene.AddNode(extrusionModel)
    extrusionModel.SetName(slicer.mrmlScene.GetUniqueNameByString('customTitaniumPlatePrototype'))
    extrusionModel.CreateDefaultDisplayNodes()
    extrusionModel.SetAndObservePolyData(triangleFilter.GetOutput())

    slicer.mrmlScene.RemoveNode(plateCurveResampled)

  def pointsOverlap(self,firstPolygonPoints,secondPolygonPoints):
    firstPolygonPoints_np = np.array(firstPolygonPoints, dtype="float")
    secondPolygonPoints_np = np.array(secondPolygonPoints, dtype="float")
    centroidFirstPolygonPoints = np.average(firstPolygonPoints_np, axis=0)
    centroidSecondPolygonPoints = np.average(firstPolygonPoints_np, axis=0)
    defaultDirection = (
      (centroidSecondPolygonPoints - centroidFirstPolygonPoints) / 
      np.linalg.norm(centroidSecondPolygonPoints - centroidFirstPolygonPoints)
    )
    
    for i in range(len(firstPolygonPoints_np)):
      firstPolygonPoint = firstPolygonPoints_np[i]
      for j in range(len(secondPolygonPoints_np)):
        secondPolygonPoint = secondPolygonPoints_np[j]
        direction = secondPolygonPoint - firstPolygonPoint
        projectedOrientedDistance = defaultDirection @ direction.T
        if projectedOrientedDistance < 0:
          return True
    
    return False
  
  def createAlmostQuarterArcFromPointsAndCenter(self,pointStartXY,pointEndXY,centerXY,nOfsegments):
    if nOfsegments <= 1:
      return []

    almostQuarterArcPoints = []

    vectorStart = np.append(pointStartXY - centerXY, 0.0)
    vectorEnd = np.append(pointEndXY - centerXY, 0.0)
    center = np.append(centerXY, 0.0)
    angleRadians = vtk.vtkMath.AngleBetweenVectors(vectorStart, vectorEnd)/nOfsegments
    rotationAxis = [0,0,0]
    vtk.vtkMath.Cross(vectorStart, vectorEnd, rotationAxis)
    rotationAxis = rotationAxis/np.linalg.norm(rotationAxis)
    rotationTransform = vtk.vtkTransform()
    rotationTransform.PostMultiply()
    rotationTransform.Translate(-center)
    rotationTransform.RotateWXYZ(vtk.vtkMath.DegreesFromRadians(angleRadians), rotationAxis)
    rotationTransform.Translate(center)

    transformedPoint = np.append(np.copy(pointStartXY), 0.0)
    for i in range(nOfsegments-1):
      rotationTransform.TransformPoint(transformedPoint, transformedPoint)
      almostQuarterArcPoints.append(transformedPoint[:2])
      transformedPoint = np.copy(transformedPoint)

    return almostQuarterArcPoints

  def createLineFromPointsAndDistanceBetweenPoints(self,pointStartXY,pointEndXY,arcSegmentLength):
    return []

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
    slicer.util.mainWindow().enabled = False
    self.setUp()
    self.section_EnterBRP()
    self.section_GetWidget()
    self.section_GetLogic()
    self.section_LoadSampleData()
    self.section_MakeModels()
    self.section_AddMandibularCurve()
    self.section_AddMandiblePlanes()
    self.section_AddFibulaLineAndCenterIt()
    self.section_SimulateAndImproveMandibleReconstruction()
    self.section_createMiterBoxesFromCorrespondingLine()
    self.section_createAndUpdateSawBoxesFromMandiblePlanes()
    slicer.util.mainWindow().enabled = True

  def section_EnterBRP(self):
    self.assertIsNotNone(slicer.modules.bonereconstructionplanner)
    slicer.util.selectModule('Data')
    slicer.util.selectModule('BoneReconstructionPlanner')
    self.assertEqual(slicer.util.selectedModule(),'BoneReconstructionPlanner')
  
  def section_GetWidget(self):
    self.widgetBRP = slicer.modules.bonereconstructionplanner.widgetRepresentation().self()
      
  def section_GetLogic(self):
    self.logicBRP = self.widgetBRP.logic  
      
  def test_LoadFinishedPlanSampleData(self):
    # this test should be updated with a new TestPlanBRP sample data.
    self.section_EnterBRP()
    self.section_GetWidget()
    self.section_GetLogic()

    self.delayDisplay("Started loading TestPlanBRP scene")
    import SampleData
    SampleData.downloadSample('TestPlanBRP')
    self.delayDisplay('Loaded TestPlanBRP scene')


    self.delayDisplay('Checking correct import')

    if int(slicer.app.revision) >= 31454:
      expecterNumberOfNodesByClass = {
        'vtkMRMLScalarVolumeNode': 2,
        'vtkMRMLSegmentationNode': 2,
        'vtkMRMLModelNode': 45,
        'vtkMRMLMarkupsCurveNode': 4,
        'vtkMRMLMarkupsPlaneNode': 12,
        'vtkMRMLMarkupsLineNode': 5,
        'vtkMRMLDynamicModelerNode': 4,
        'vtkMRMLMarkupsFiducialNode': 3,
        'vtkMRMLLinearTransformNode': 17
      }
    else:
      expecterNumberOfNodesByClass = {
        'vtkMRMLScalarVolumeNode': 2,
        'vtkMRMLSegmentationNode': 2,
        'vtkMRMLModelNode': 42,
        'vtkMRMLMarkupsCurveNode': 4,
        'vtkMRMLMarkupsPlaneNode': 12,
        'vtkMRMLMarkupsLineNode': 5,
        'vtkMRMLDynamicModelerNode': 4,
        'vtkMRMLMarkupsFiducialNode': 3,
        'vtkMRMLLinearTransformNode': 14
      }

    for nodeClass, expectedNumberOfNodesInScene in expecterNumberOfNodesByClass.items():
      self.assertEqual(
        slicer.mrmlScene.GetNumberOfNodesByClass(nodeClass),
        expectedNumberOfNodesInScene
      )


    # weak test to ensure integrity of the folder hierarchy, 
    #   just check if the number of leaf/one-level-below-BRPFolder items is okay
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    sceneItemId = shNode.GetSceneItemID()
    leafIdList = vtk.vtkIdList()
    shNode.GetItemChildren(sceneItemId,leafIdList,True)

    self.assertEqual(
      leafIdList.GetNumberOfIds(),
      110
    )

    BRPFolder = shNode.GetItemByName("BoneReconstructionPlanner")
    oneLevelBelowBRPIdList = vtk.vtkIdList()
    shNode.GetItemChildren(BRPFolder,oneLevelBelowBRPIdList,False)

    self.assertEqual(
      oneLevelBelowBRPIdList.GetNumberOfIds(),
      27
    )

    self.delayDisplay('Test data imported correctly')

  def section_LoadSampleData(self):
    # Get input data
    import SampleData
    self.fibulaVolume = SampleData.downloadSample('CTFibula')
    self.delayDisplay('Loaded CTFibula')
    self.mandibleVolume = SampleData.downloadSample('CTMandible')
    self.delayDisplay('Loaded CTMandible')
    self.fibulaSegmentation = SampleData.downloadSample('FibulaSegmentation')
    self.delayDisplay('Loaded FibulaSegmentation')
    self.mandibleSegmentation = SampleData.downloadSample('MandibleSegmentation')
    self.delayDisplay('Loaded MandibleSegmentation')

    parameterNode = self.logicBRP.getParameterNode()
    wasModified = parameterNode.StartModify()
    parameterNode.SetNodeReferenceID("currentScalarVolume", self.mandibleVolume.GetID())
    parameterNode.SetParameter("scalarVolumeChangedThroughParameterNode", "True")
    parameterNode.SetNodeReferenceID("fibulaSegmentation", self.fibulaSegmentation.GetID())
    parameterNode.SetNodeReferenceID("mandibularSegmentation", self.mandibleSegmentation.GetID())
    parameterNode.EndModify(wasModified)

    self.assertEqual(
      parameterNode.GetNodeReference("currentScalarVolume").GetID(),
      self.mandibleVolume.GetID()
    )
    self.assertEqual(
      parameterNode.GetNodeReference("fibulaSegmentation").GetID(),
      self.fibulaSegmentation.GetID()
    )
    self.assertEqual(
      parameterNode.GetNodeReference("mandibularSegmentation").GetID(),
      self.mandibleSegmentation.GetID()
    )
      
  def section_MakeModels(self):
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
    self.delayDisplay("Starting the MakeModelsTest")

    parameterNode = self.logicBRP.getParameterNode()

    self.logicBRP.makeModels()

    fibulaModelNode = parameterNode.GetNodeReference("fibulaModelNode")
    mandibleModelNode = parameterNode.GetNodeReference("mandibleModelNode")
    decimatedFibulaModelNode = parameterNode.GetNodeReference("decimatedFibulaModelNode")
    decimatedMandibleModelNode = parameterNode.GetNodeReference("decimatedMandibleModelNode")

    allowedDifferenceFactor = 0.02
    targetFibulaPoints = 197962
    targetMandiblePoints = 109820
    targetDecimatedFibulaPoints = 9872
    targetDecimatedMandiblePoints = 5483
    self.assertLess(
      abs(fibulaModelNode.GetMesh().GetNumberOfPoints() - targetFibulaPoints), 
      allowedDifferenceFactor*targetFibulaPoints
    )
    self.assertLess(
      abs(mandibleModelNode.GetMesh().GetNumberOfPoints()-targetMandiblePoints), 
      allowedDifferenceFactor*targetMandiblePoints
    )
    self.assertLess(
      abs(decimatedFibulaModelNode.GetMesh().GetNumberOfPoints() - targetDecimatedFibulaPoints), 
      allowedDifferenceFactor*targetDecimatedFibulaPoints
    )
    self.assertLess(
      abs(decimatedMandibleModelNode.GetMesh().GetNumberOfPoints()-targetDecimatedMandiblePoints), 
      allowedDifferenceFactor*targetDecimatedMandiblePoints
    )
    
    fibulaCentroidX = float(parameterNode.GetParameter("fibulaCentroidX"))
    fibulaCentroidY = float(parameterNode.GetParameter("fibulaCentroidY"))
    fibulaCentroidZ = float(parameterNode.GetParameter("fibulaCentroidZ"))
    mandibleCentroidX = float(parameterNode.GetParameter("mandibleCentroidX"))
    mandibleCentroidY = float(parameterNode.GetParameter("mandibleCentroidY"))
    mandibleCentroidZ = float(parameterNode.GetParameter("mandibleCentroidZ"))

    #np.testing.assert_almost_equal(actual,desired)
    np.testing.assert_almost_equal(fibulaCentroidX,-95.32889,decimal=1)
    np.testing.assert_almost_equal(fibulaCentroidY,-8.86916,decimal=1)
    np.testing.assert_almost_equal(fibulaCentroidZ,-18.44151,decimal=1)
    np.testing.assert_almost_equal(mandibleCentroidX,0.1073946,decimal=1)
    np.testing.assert_almost_equal(mandibleCentroidY,65.49171,decimal=1)
    np.testing.assert_almost_equal(mandibleCentroidZ,-57.415688,decimal=1)

    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    BRPFolder = shNode.GetItemByName("BoneReconstructionPlanner")
    segmentationModelsFolder = shNode.GetItemByName("Segmentation Models")
    fibulaModelItemID = shNode.GetItemByDataNode(fibulaModelNode)
    mandibleModelItemID = shNode.GetItemByDataNode(mandibleModelNode)
    decimatedFibulaModelItemID = shNode.GetItemByDataNode(decimatedFibulaModelNode)
    decimatedMandibleModelItemID = shNode.GetItemByDataNode(decimatedMandibleModelNode)

    self.assertNotEqual(BRPFolder,shNode.GetInvalidItemID())
    self.assertNotEqual(segmentationModelsFolder,shNode.GetInvalidItemID())

    self.assertEqual(
      BRPFolder,
      shNode.GetItemParent(segmentationModelsFolder)
    )
    self.assertEqual(
      segmentationModelsFolder,
      shNode.GetItemParent(fibulaModelItemID)
    )
    self.assertEqual(
      segmentationModelsFolder,
      shNode.GetItemParent(mandibleModelItemID)
    )
    self.assertEqual(
      segmentationModelsFolder,
      shNode.GetItemParent(decimatedFibulaModelItemID)
    )
    self.assertEqual(
      segmentationModelsFolder,
      shNode.GetItemParent(decimatedMandibleModelItemID)
    )

    self.delayDisplay("MakeModelsTest successful")

  def section_AddMandibularCurve(self):
    self.delayDisplay("Starting the AddMandibularCurveTest")

    mandibularCurvePoints = [
      [ 43.02632904,  61.06202698, -60.92616272],
      [ 33.40823746,  83.49567413, -71.52266693],
      [ 20.23157501, 103.01984406, -78.46653748],
      [  3.63758111, 110.96538544, -82.94055939],
      [-15.31359386, 103.96769714, -83.5898056 ],
      [-31.47601509,  77.34331512, -76.59559631],
      [-44.32816696,  47.25786209, -64.23408508],
    ]

    self.logicBRP.addMandibularCurve()
    selectionNode = slicer.app.applicationLogic().GetSelectionNode()
    mandibularCurveNode = slicer.mrmlScene.GetNodeByID(
      selectionNode.GetActivePlaceNodeID()
    )
    for point in mandibularCurvePoints:
      mandibularCurveNode.AddControlPoint(*point)
    interactionNode = slicer.app.applicationLogic().GetInteractionNode()
    interactionNode.SwitchToViewTransformMode()

    self.assertEqual(
      len(mandibularCurvePoints),
      mandibularCurveNode.GetNumberOfControlPoints()
    )

    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    BRPFolder = shNode.GetItemByName("BoneReconstructionPlanner")
    mandibularCurveItemID = shNode.GetItemByDataNode(mandibularCurveNode)
    self.assertEqual(
      BRPFolder,
      shNode.GetItemParent(mandibularCurveItemID)
    )

    #the mandibleCurveSelector autopopulates and updates the parameterNode
    parameterNode = self.logicBRP.getParameterNode()
    mandibleCurveFromParameterNode = parameterNode.GetNodeReference("mandibleCurve")
    self.assertEqual(
      mandibularCurveNode.GetID(),
      mandibleCurveFromParameterNode.GetID()
    )

    self.delayDisplay("AddMandibularCurveTest successful")
  
  def section_AddMandiblePlanes(self):
    self.delayDisplay("Starting the AddMandibularPlanesTest")

    planeOrigins = [
      [38.89806365966797, 71.97505950927734, -65.15746307373047],
      [-28.70669174194336, 81.52465057373047, -75.59122467041016],
      [21.20140266418457, 100.38216400146484, -73.75139617919922],
      [-9.514277458190918, 105.30805969238281, -79.4371337890625],
    ]

    for origin in planeOrigins:
      self.logicBRP.addCutPlane()
      selectionNode = slicer.app.applicationLogic().GetSelectionNode()
      mandibularPlaneNode = slicer.mrmlScene.GetNodeByID(
        selectionNode.GetActivePlaceNodeID()
      )
      mandibularPlaneNode.AddControlPoint(*origin)
      interactionNode = slicer.app.applicationLogic().GetInteractionNode()
      interactionNode.SwitchToViewTransformMode()
    

    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()

    BRPFolder = shNode.GetItemByName("BoneReconstructionPlanner")
    mandibularPlanesFolderItemID = shNode.GetItemByName("Mandibular planes")

    self.assertEqual(
      BRPFolder,
      shNode.GetItemParent(mandibularPlanesFolderItemID)
    )

    mandibularPlanesList = createListFromFolderID(mandibularPlanesFolderItemID)
    self.assertEqual(
      len(mandibularPlanesList),
      4
    )

    colorArray = []

    for planeNode in mandibularPlanesList:
      self.assertEqual(
        planeNode.GetNumberOfControlPoints(),
        3
      )
      self.assertTrue(
        planeNode.GetAttribute("isMandibularPlane") == "True"
      )
      self.assertTrue(
        np.allclose(
          np.array(planeNode.GetSize()),
          np.array([self.logicBRP.PLANE_SIDE_SIZE,self.logicBRP.PLANE_SIDE_SIZE])
        )
      )
      self.assertEqual(
        planeNode.GetPlaneType(),
        slicer.vtkMRMLMarkupsPlaneNode.PlaneType3Points
      )
      
      displayNode = planeNode.GetDisplayNode()
      self.assertEqual(
        displayNode.GetGlyphScale(),
        self.logicBRP.PLANE_GLYPH_SCALE
      )
      self.assertTrue(
        displayNode.GetHandlesInteractive(),
      )
      self.assertTrue(
        displayNode.GetTranslationHandleVisibility(),
      )
      self.assertTrue(
        displayNode.GetRotationHandleVisibility(),
      )
      self.assertFalse(
        displayNode.GetScaleHandleVisibility(),
      )

      colorArray.append(displayNode.GetSelectedColor())
    
    colorArray = np.array(colorArray)

    # check that plane colors do not repeat
    for i in range(len(colorArray)):
      for j in range(len(colorArray)):
        if i!=j:
          self.assertFalse(
            np.allclose(
              colorArray[i],
              colorArray[j]
            )
          )
    
    # check planes order
    parameterNode = self.logicBRP.getParameterNode()
    mandibleCurve = parameterNode.GetNodeReference("mandibleCurve")
    closestCurvePoint = [0,0,0]
    smallerCurvePointIndex = 0
    for i in range(len(mandibularPlanesList)):
      origin = [0,0,0]
      mandibularPlanesList[i].GetOrigin(origin)
      curvePointIndex = mandibleCurve.GetClosestPointPositionAlongCurveWorld(
        origin,closestCurvePoint
      )
      self.assertLessEqual(smallerCurvePointIndex, curvePointIndex)
      if smallerCurvePointIndex <= curvePointIndex:
        smallerCurvePointIndex = curvePointIndex

    self.delayDisplay("AddMandibularPlanesTest successful")

  def section_AddFibulaLineAndCenterIt(self):
    self.delayDisplay("Starting the AddFibulaLineAndCenterItTest")

    fibulaLinePoints = [
      [-91.39446258544922, -12.100865364074707, -90.508544921875],
      [-104.19928741455078, -9.48827075958252, 47.4937744140625],
    ]

    self.logicBRP.addFibulaLine()
    selectionNode = slicer.app.applicationLogic().GetSelectionNode()
    fibulaLineNode = slicer.mrmlScene.GetNodeByID(
      selectionNode.GetActivePlaceNodeID()
    )
    for point in fibulaLinePoints:
      fibulaLineNode.AddControlPoint(*point)
    interactionNode = slicer.app.applicationLogic().GetInteractionNode()
    interactionNode.SwitchToViewTransformMode()

    self.assertEqual(
      len(fibulaLinePoints),
      fibulaLineNode.GetNumberOfControlPoints()
    )

    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    BRPFolder = shNode.GetItemByName("BoneReconstructionPlanner")
    fibulaLineItemID = shNode.GetItemByDataNode(fibulaLineNode)
    self.assertEqual(
      BRPFolder,
      shNode.GetItemParent(fibulaLineItemID)
    )

    #the fibulaLineSelector autopopulates and updates the parameterNode
    parameterNode = self.logicBRP.getParameterNode()
    fibulaLineFromParameterNode = parameterNode.GetNodeReference("fibulaLine")
    self.assertEqual(
      fibulaLineNode.GetID(),
      fibulaLineFromParameterNode.GetID()
    )

    self.logicBRP.centerFibulaLine()

    centeredLinePoints = np.array(
      [
        [ -88.24621582,  -10.96450806,  -90.23794556],
        [-100.49311066,   -9.26262665,   47.83334351]
      ]
    )

    for i in range(2):
      self.assertTrue(
        np.allclose(
          fibulaLineNode.GetNthControlPointPosition(i),
          centeredLinePoints[i],
          atol=1e-2
        )
      )

    self.delayDisplay("AddFibulaLineAndCenterItTest successful")

  def section_SimulateAndImproveMandibleReconstruction(self):
    self.delayDisplay("Starting the SimulateAndImproveMandibleReconstruction")
    self.delayDisplay("Create the reconstruction for first time")
    self.logicBRP.onGenerateFibulaPlanesTimerTimeout()
    self.delayDisplay("Reconstruction successful")
    #

    # # generate mandibular plane movements with this code:
    # def createListFromFolderID(folderID):
    #   createdList = []
    #   shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    #   myList = vtk.vtkIdList()
    #   shNode.GetItemChildren(folderID,myList)
    #   for i in range(myList.GetNumberOfIds()):
    #     createdList.append(shNode.GetItemDataNode(myList.GetId(i)))
    #   return createdList
    # def updateMandibularPlaneMovementsList(caller=None,event=None,movementsList=[]):
    #   plane = caller
    #   planeMatrix = vtk.vtkMatrix4x4()
    #   plane.GetObjectToWorldMatrix(planeMatrix)
    #   movementsList.append([plane.GetID(),slicer.util.arrayFromVTKMatrix(planeMatrix).tolist()])
    # shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    # mandiblePlanesFolder = shNode.GetItemByName("Mandibular planes")
    # mandiblePlanes = createListFromFolderID(mandiblePlanesFolder)
    # # list to save the movements for the test
    # movementsList = []
    # # set observers
    # planesAndObserversList = []
    # for plane in mandiblePlanes:
    #   planesAndObserversList.append(
    #     [
    #         plane.GetID(),
    #         plane.AddObserver(
    #             slicer.vtkMRMLMarkupsNode.PointEndInteractionEvent,
    #             lambda caller,event,movementsList=movementsList: updateMandibularPlaneMovementsList(caller,event,movementsList)
    #         )
    #     ]
    #  )
    # 
    # 

    if not slicer.app.commandOptions().noMainWindow:
      layoutManager = slicer.app.layoutManager()
      mandibleViewNode = slicer.mrmlScene.GetSingletonNode(self.logicBRP.MANDIBLE_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
      if int(slicer.app.revision) >= 31524:
        layoutManager.addMaximizedViewNode(mandibleViewNode)
      else:
        layoutManager.setMaximizedViewNode(mandibleViewNode)

    # 8 movements below
    # movementsList = [['vtkMRMLMarkupsPlaneNode4', [[0.5161781920883237, -0.04134258142560255, -0.8554828256449669, -9.862711906433127], [-0.8468593163756161, 0.12466280634486007, -0.5169994999823967, 107.90783691406249], [0.12802098374975024, 0.991337468108258, 0.02933687175645767, -83.94944763183594], [0.0, 0.0, 0.0, 1.0]]], ['vtkMRMLMarkupsPlaneNode4', [[0.516178231664674, -0.041342429710410605, -0.8554828090973949, -7.397708892822266], [-0.8468592958433797, 0.12466287181842768, -0.5169995178272775, 103.8636703491211], [0.12802095999946736, 0.9913374662019095, 0.029337039816463184, -83.33809661865234], [0.0, 0.0, 0.0, 1.0]]], ['vtkMRMLMarkupsPlaneNode2', [[0.8922376682835299, 0.18524939419545736, -0.41181865577725557, -28.11571121215824], [-0.4465787117400004, 0.22681900255851603, -0.8655175297467994, 84.53712463378889], [-0.06692830131275733, 0.9561567873673105, 0.2851048937756292, -79.05013275146474], [0.0, 0.0, 0.0, 1.0]]], ['vtkMRMLMarkupsPlaneNode2', [[0.8922376766572847, 0.1852491791773996, -0.41181873435688954, -24.693025588989258], [-0.4465787239770117, 0.22681897690359318, -0.8655175301560744, 82.82402038574219], [-0.06692810802850067, 0.9561568351115349, 0.2851047790290762, -79.30686950683594], [0.0, 0.0, 0.0, 1.0]]], ['vtkMRMLMarkupsPlaneNode3', [[-0.708383352772158, -0.24065112649761564, -0.6635360282838488, 22.992961883544925], [-0.6972025285352179, 0.09205350357255149, 0.7109393692039546, 100.19924163818364], [-0.11000754392029201, 0.9662366106681359, -0.23299174338413398, -77.51470947265622], [0.0, 0.0, 0.0, 1.0]]], ['vtkMRMLMarkupsPlaneNode3', [[-0.7083834009232749, -0.240651176447713, -0.6635359587623766, 20.943126678466797], [-0.6972024658214877, 0.09205345939667467, 0.7109394364258759, 98.18177032470703], [-0.11000763132079507, 0.9662366024361924, -0.23299173625635644, -77.8330307006836], [0.0, 0.0, 0.0, 1.0]]], ['vtkMRMLMarkupsPlaneNode1', [[-0.8984010895060554, -0.2612400933848085, -0.35302846341708666, 39.90895843505858], [-0.42656108809295407, 0.32777755218344756, 0.8429753937153698, 68.75823974609365], [-0.1045041649853625, 0.9079182176236601, -0.4059105684849661, -64.72950744628893], [0.0, 0.0, 0.0, 1.0]]], ['vtkMRMLMarkupsPlaneNode1', [[-0.8984010923061703, -0.2612399980002971, -0.3530285268754991, 36.00282287597656], [-0.4265610935556299, 0.32777742996859105, 0.8429754384724448, 66.90361022949219], [-0.10450411861599232, 0.9079182891912633, -0.4059104203445687, -65.18387603759766], [0.0, 0.0, 0.0, 1.0]]]]
    # 4 movements below
    movementsList = [['vtkMRMLMarkupsPlaneNode4', [[0.516178231664674, -0.041342429710410605, -0.8554828090973949, -7.397708892822266], [-0.8468592958433797, 0.12466287181842768, -0.5169995178272775, 103.8636703491211], [0.12802095999946736, 0.9913374662019095, 0.029337039816463184, -83.33809661865234], [0.0, 0.0, 0.0, 1.0]]], ['vtkMRMLMarkupsPlaneNode2', [[0.8922376766572847, 0.1852491791773996, -0.41181873435688954, -24.693025588989258], [-0.4465787239770117, 0.22681897690359318, -0.8655175301560744, 82.82402038574219], [-0.06692810802850067, 0.9561568351115349, 0.2851047790290762, -79.30686950683594], [0.0, 0.0, 0.0, 1.0]]], ['vtkMRMLMarkupsPlaneNode3', [[-0.7083834009232749, -0.240651176447713, -0.6635359587623766, 20.943126678466797], [-0.6972024658214877, 0.09205345939667467, 0.7109394364258759, 98.18177032470703], [-0.11000763132079507, 0.9662366024361924, -0.23299173625635644, -77.8330307006836], [0.0, 0.0, 0.0, 1.0]]], ['vtkMRMLMarkupsPlaneNode1', [[-0.8984010923061703, -0.2612399980002971, -0.3530285268754991, 36.00282287597656], [-0.4265610935556299, 0.32777742996859105, 0.8429754384724448, 66.90361022949219], [-0.10450411861599232, 0.9079182891912633, -0.4059104203445687, -65.18387603759766], [0.0, 0.0, 0.0, 1.0]]]]
    for item in movementsList:
      self.delayDisplay("Update mandibular plane and reconstruction")
      self.delayDisplay("Move mandibular plane")
      nodeID = item[0]
      newPlaneToWorldMatrix = slicer.util.vtkMatrixFromArray(np.array(item[1]))
      planeNode = slicer.mrmlScene.GetNodeByID(nodeID)
      oldPlaneToWorld = vtk.vtkMatrix4x4()
      planeNode.GetObjectToWorldMatrix(oldPlaneToWorld)
      worldToOldPlane = vtk.vtkMatrix4x4()
      vtk.vtkMatrix4x4.Invert(oldPlaneToWorld, worldToOldPlane)
      transform = vtk.vtkTransform()
      transform.PostMultiply()
      transform.Concatenate(worldToOldPlane)
      transform.Concatenate(newPlaneToWorldMatrix)
      wasModified = planeNode.StartModify()
      for i in range(3):
        oldPos = planeNode.GetNthControlPointPosition(i)
        newPos = [0,0,0]
        transform.TransformPoint(oldPos,newPos)
        planeNode.SetNthControlPointPosition(i,newPos)
      planeNode.EndModify(wasModified)
      self.delayDisplay("Mandibular plane moved")
      #
      self.delayDisplay("Update reconstruction")
      self.logicBRP.onGenerateFibulaPlanesTimerTimeout()
      self.delayDisplay("Update successful")
    
    if not slicer.app.commandOptions().noMainWindow:
      # hide original mandible
      self.widgetBRP.onShowHideOriginalMandibleButton()
      # hide mandible plane handles
      self.widgetBRP.onShowHideMandiblePlanesInteractionHandlesButton()
    
    self.delayDisplay("Optimize bones contact in reconstruction")
    parameterNode = self.logicBRP.getParameterNode()
    parameterNode.SetParameter("mandiblePlanesPositioningForMaximumBoneContact","True")
    self.logicBRP.onGenerateFibulaPlanesTimerTimeout()
    self.delayDisplay("Bones contact optimized")

    if not slicer.app.commandOptions().noMainWindow:
      fibulaViewNode = slicer.mrmlScene.GetSingletonNode(self.logicBRP.FIBULA_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
      layoutManager = slicer.app.layoutManager()
      if int(slicer.app.revision) >= 31524:
        layoutManager.removeMaximizedViewNode(mandibleViewNode)
        layoutManager.addMaximizedViewNode(fibulaViewNode)
      else:
        layoutManager.setMaximizedViewNode(None)
        layoutManager.setMaximizedViewNode(fibulaViewNode)

    # solve rotation about the anatomical axis of the grafted bone-pieces
    self.delayDisplay("Make between-bone-pieces relative rotation zero")
    parameterNode = self.logicBRP.getParameterNode()
    parameterNode.SetParameter("makeAllMandiblePlanesRotateTogether","True")
    self.logicBRP.onGenerateFibulaPlanesTimerTimeout()
    self.delayDisplay("Achieved zero relative rotation")

    if not slicer.app.commandOptions().noMainWindow:
      layoutManager = slicer.app.layoutManager()
      if int(slicer.app.revision) >= 31524:
        layoutManager.removeMaximizedViewNode(fibulaViewNode)
      else:
        layoutManager.setMaximizedViewNode(None)

    self.delayDisplay("SimulateAndImproveMandibleReconstruction test successful")
    
  def section_createMiterBoxesFromCorrespondingLine(self):
    self.delayDisplay("Starting the createMiterBoxesFromCorrespondingLine test")

    parameterNode = self.logicBRP.getParameterNode()
    wasModified = parameterNode.StartModify()
    parameterNode.SetNodeReferenceID("currentScalarVolume", self.fibulaVolume.GetID())
    parameterNode.SetParameter("scalarVolumeChangedThroughParameterNode", "True")
    parameterNode.EndModify(wasModified)

    sliceOffset = -38.08869552612305
    if not slicer.app.commandOptions().noMainWindow:
      redSliceNode = slicer.mrmlScene.GetSingletonNode("Red", "vtkMRMLSliceNode")
      redSliceNode.SetSliceOffset(sliceOffset)

    miterBoxLinePoints = [
      [-92.47185918150018, -10.999045106771323, sliceOffset],
      [-104.08360013902106, -12.657865243560021, sliceOffset],
    ]
    
    miterBoxLine = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode", "miterBoxLine")
    miterBoxLine.CreateDefaultDisplayNodes()
    
    for point in miterBoxLinePoints:
      miterBoxLine.AddControlPoint(*point)

    self.assertEqual(
      len(miterBoxLinePoints),
      miterBoxLine.GetNumberOfControlPoints()
    )

    wasModified = parameterNode.StartModify()
    parameterNode.SetParameter("checkSecurityMarginOnMiterBoxCreation","False")
    parameterNode.SetNodeReferenceID("miterBoxDirectionLine",miterBoxLine.GetID())
    parameterNode.EndModify(wasModified)
    self.logicBRP.createMiterBoxesFromFibulaPlanes()

    # asserts below

    self.delayDisplay("CreateMiterBoxesFromCorrespondingLine test successful")

  def section_createAndUpdateSawBoxesFromMandiblePlanes(self):
    self.delayDisplay("Starting the createAndUpdateSawBoxesFromMandiblePlanes test")

    if not slicer.app.commandOptions().noMainWindow:
      layoutManager = slicer.app.layoutManager()
      mandibleViewNode = slicer.mrmlScene.GetSingletonNode(self.logicBRP.MANDIBLE_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
      if int(slicer.app.revision) >= 31524:
        layoutManager.addMaximizedViewNode(mandibleViewNode)
      else:
        layoutManager.setMaximizedViewNode(mandibleViewNode)

    self.logicBRP.createSawBoxesFromFirstAndLastMandiblePlanes()

    # # generate saw boxes movements with this code:
    # def createListFromFolderID(folderID):
    #   createdList = []
    #   shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    #   myList = vtk.vtkIdList()
    #   shNode.GetItemChildren(folderID,myList)
    #   for i in range(myList.GetNumberOfIds()):
    #     createdList.append(shNode.GetItemDataNode(myList.GetId(i)))
    #   return createdList
    # def updateSawBoxesMovementsList(caller=None,event=None,movementsList=[]):
    #   plane = caller
    #   planeMatrix = vtk.vtkMatrix4x4()
    #   plane.GetObjectToWorldMatrix(planeMatrix)
    #   movementsList.append([plane.GetID(),slicer.util.arrayFromVTKMatrix(planeMatrix).tolist()])
    # shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    # sawBoxesPlanesFolder = shNode.GetItemByName("sawBoxes Planes")
    # sawBoxesPlanes = createListFromFolderID(mandiblePlanesFolder)
    # # list to save the movements for the test
    # movementsList = []
    # # set observers
    # planesAndObserversList = []
    # for plane in sawBoxesPlanes:
    #   planesAndObserversList.append(
    #     [
    #         plane.GetID(),
    #         plane.AddObserver(
    #             slicer.vtkMRMLMarkupsNode.PointEndInteractionEvent,
    #             lambda caller,event,movementsList=movementsList: updateSawBoxesMovementsList(caller,event,movementsList)
    #         )
    #     ]
    #  )
    # 
    # 

    movementsList = [['vtkMRMLMarkupsPlaneNode11', [[-0.10858201072394683, 0.9292904853485047, -0.3530285268754998, 42.21461987204822], [0.39399905998699103, 0.3662746931765254, 0.8429754384724443, 76.13834598713792], [0.9126744697188107, -0.04756093963730036, -0.40591042034456926, -52.639932827421404], [0.0, 0.0, 0.0, 1.0]]], ['vtkMRMLMarkupsPlaneNode11', [[-0.10858201072394683, 0.9292904853485047, -0.3530285268754998, 43.024681091308594], [0.39399905998699103, 0.3662746931765254, 0.8429754384724443, 73.1989517211914], [0.9126744697188107, -0.04756093963730036, -0.40591042034456926, -59.4488639831543], [0.0, 0.0, 0.0, 1.0]]], ['vtkMRMLMarkupsPlaneNode11', [[-0.10858201072394683, 0.9292904853485047, -0.3530285268754998, 47.28470993041992], [0.39399905998699103, 0.3662746931765254, 0.8429754384724443, 74.87801361083984], [0.9126744697188107, -0.04756093963730036, -0.40591042034456926, -59.66689682006836], [0.0, 0.0, 0.0, 1.0]]], ['vtkMRMLMarkupsPlaneNode12', [[0.1458282507662034, -0.8995217903481598, -0.4118187343568899, -35.072343539111024], [0.24624056084596485, 0.4361708279869181, -0.8655175301560744, 90.12325764191597], [0.9581751966486786, 0.024810431315229024, 0.28510477902907616, -73.89405603129094], [0.0, 0.0, 0.0, 1.0]]]]

    for item in movementsList:
      self.delayDisplay("Move saw box")
      nodeID = item[0]
      newPlaneToWorldMatrix = slicer.util.vtkMatrixFromArray(np.array(item[1]))
      planeNode = slicer.mrmlScene.GetNodeByID(nodeID)
      oldPlaneToWorld = vtk.vtkMatrix4x4()
      planeNode.GetObjectToNodeMatrix(oldPlaneToWorld)
      worldToOldPlane = vtk.vtkMatrix4x4()
      vtk.vtkMatrix4x4.Invert(oldPlaneToWorld, worldToOldPlane)
      transform = vtk.vtkTransform()
      transform.PostMultiply()
      transform.Concatenate(worldToOldPlane)
      transform.Concatenate(newPlaneToWorldMatrix)
      wasModified = planeNode.StartModify()
      for i in range(3):
        oldPos = planeNode.GetNthControlPointPosition(i)
        newPos = [0,0,0]
        transform.TransformPoint(oldPos,newPos)
        planeNode.SetNthControlPointPosition(i,newPos)
      planeNode.EndModify(wasModified)
      self.delayDisplay("Saw box moved")

    if not slicer.app.commandOptions().noMainWindow:
      layoutManager = slicer.app.layoutManager()
      if int(slicer.app.revision) >= 31524:
        layoutManager.removeMaximizedViewNode(mandibleViewNode)
      else:
        layoutManager.setMaximizedViewNode(None)
      # show mandible plane handles
      self.widgetBRP.onShowHideMandiblePlanesInteractionHandlesButton()
      # hide saw boxes handles
      self.widgetBRP.onShowHideBiggerSawBoxesInteractionHandlesButton()

    # asserts below


    self.delayDisplay("CreateAndUpdateSawBoxesFromMandiblePlanes test successful")

def createListFromFolderID(folderID):
  shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
  createdList = []

  if folderID != shNode.GetInvalidItemID():
    myList = vtk.vtkIdList()
    shNode.GetItemChildren(folderID,myList)
    for i in range(myList.GetNumberOfIds()):
      createdList.append(shNode.GetItemDataNode(myList.GetId(i)))
  
  return createdList