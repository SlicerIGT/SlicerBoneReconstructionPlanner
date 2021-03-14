import os
import unittest
import logging
import vtk, qt, ctk, slicer, math
import numpy as np
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin

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
This is a module for surgical planning of mandibular reconstruction with free fibula flap.
See the whole project in <a href="https://github.com/lassoan/SlicerBoneReconstructionPlanner">this link</a>.
"""
    # TODO: replace with organization, grant and thanks
    self.parent.acknowledgementText = """
This file is developed by Mauro I. Dominguez with the supervision and advice of Eng. Andras Lasso, PerkLab,
and the useful inputs of Dr. Manjula Herath and it is made as a final project of engineering of Mauro.
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
    uris="https://github.com/lassoan/SlicerBoneReconstructionPlanner/releases/download/TestingData/FibulaCropped.nrrd",
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
    uris="https://github.com/lassoan/SlicerBoneReconstructionPlanner/releases/download/TestingData/ResectedMandible.nrrd",
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
    self.ui.fibulaLineSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.mandibleCurveSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.mandibularSegmentationSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.fibulaSegmentationSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.fibulaFiducialListSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.fibulaSurgicalGuideBaseSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.miterBoxDirectionLineSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.scalarVolumeSelector.connect("nodeActivated(vtkMRMLNode*)", self.onScalarVolumeChanged)
    self.ui.mandibleBridgeModelSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.mandibleSurgicalGuideBaseSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.mandibleFiducialListSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
   
    self.ui.initialSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.intersectionSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.betweenSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
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
    
    # Buttons
    self.ui.notLeftFibulaCheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)
    self.ui.createPlanesButton.connect('clicked(bool)', self.onCreatePlanesButton)
    self.ui.addCutPlaneButton.connect('clicked(bool)',self.onAddCutPlaneButton)
    self.ui.addMandibularCurveButton.connect('clicked(bool)',self.onAddMandibularCurveButton)
    self.ui.addFibulaLineButton.connect('clicked(bool)',self.onAddFibulaLineButton)
    self.ui.makeModelsButton.connect('clicked(bool)',self.onMakeModelsButton)
    self.ui.updateFibulaPiecesButton.connect('clicked(bool)',self.onUpdateFibulaPiecesButton)
    self.ui.bonesToMandibleButton.connect('clicked(bool)',self.onBonesToMandibleButton)
    self.ui.mandibularAutomaticPositioningButton.connect('clicked(bool)',self.onMandibularAutomaticPositioningButton)
    self.ui.createMiterBoxesFromFibulaPlanesButton.connect('clicked(bool)',self.onCreateMiterBoxesFromFibulaPlanesButton)
    self.ui.createFibulaCylindersFiducialListButton.connect('clicked(bool)',self.onCreateFibulaCylindersFiducialListButton)
    self.ui.createCylindersFromFiducialListAndFibulaSurgicalGuideBaseButton.connect('clicked(bool)',self.onCreateCylindersFromFiducialListAndSurgicalGuideBaseButton)
    self.ui.makeBooleanOperationsToFibulaSurgicalGuideBaseButton.connect('clicked(bool)', self.onMakeBooleanOperationsToFibulaSurgicalGuideBaseButton)
    self.ui.createMandibleCylindersFiducialListButton.connect('clicked(bool)', self.onCreateMandibleCylindersFiducialListButton)
    self.ui.createSawBoxesFromFirstAndLastMandiblePlanesButton.connect('clicked(bool)', self.onCreateSawBoxesFromFirstAndLastMandiblePlanesButton)
    self.ui.makeBooleanOperationsToMandibleSurgicalGuideBaseButton.connect('clicked(bool)', self.onMakeBooleanOperationsToMandibleSurgicalGuideBaseButton)
    self.ui.createCylindersFromFiducialListAndMandibleSurgicalGuideBaseButton.connect('clicked(bool)', self.onCreateCylindersFromFiducialListAndMandibleSurgicalGuideBaseButton)
    
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
        for i in range(len(self.logic.mandiblePlaneObserversAndNodeIDList)):
          if self.logic.mandiblePlaneObserversAndNodeIDList[i][1] == callData.GetID():
            observerIndex = i
        callData.RemoveObserver(self.logic.mandiblePlaneObserversAndNodeIDList.pop(observerIndex)[0])
        self.logic.onPlaneModifiedTimer(None,None)

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
      self.ui.createPlanesButton.enabled = True
    if fibulaPlanesFolder:  
      self.ui.updateFibulaPiecesButton.enabled = True
    if cutBonesFolder:
      self.ui.bonesToMandibleButton.enabled = True
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

    if self._parameterNode.GetParameter("initialSpace") != '':
      self.ui.initialSpinBox.setValue(float(self._parameterNode.GetParameter("initialSpace")))
    if self._parameterNode.GetParameter("intersectionPlaceOfFibulaPlanes") != '':
      self.ui.intersectionSpinBox.setValue(float(self._parameterNode.GetParameter("intersectionPlaceOfFibulaPlanes")))
    if self._parameterNode.GetParameter("additionalBetweenSpaceOfFibulaPlanes") != '':
      self.ui.betweenSpinBox.setValue(float(self._parameterNode.GetParameter("additionalBetweenSpaceOfFibulaPlanes")))
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

    self._parameterNode.SetNodeReferenceID("fibulaLine", self.ui.fibulaLineSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("mandibleCurve", self.ui.mandibleCurveSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("mandibularSegmentation", self.ui.mandibularSegmentationSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("fibulaSegmentation", self.ui.fibulaSegmentationSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("fibulaFiducialList", self.ui.fibulaFiducialListSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("fibulaSurgicalGuideBaseModel", self.ui.fibulaSurgicalGuideBaseSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("miterBoxDirectionLine", self.ui.miterBoxDirectionLineSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("mandibleBridgeModel", self.ui.mandibleBridgeModelSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("mandibleSurgicalGuideBaseModel", self.ui.mandibleSurgicalGuideBaseSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("mandibleFiducialList", self.ui.mandibleFiducialListSelector.currentNodeID)

    self._parameterNode.SetParameter("initialSpace", str(self.ui.initialSpinBox.value))
    self._parameterNode.SetParameter("intersectionPlaceOfFibulaPlanes", str(self.ui.intersectionSpinBox.value))
    self._parameterNode.SetParameter("additionalBetweenSpaceOfFibulaPlanes", str(self.ui.betweenSpinBox.value))
    self._parameterNode.SetParameter("miterBoxSlotWidth", str(self.ui.miterBoxSlotWidthSpinBox.value))
    self._parameterNode.SetParameter("miterBoxSlotLength", str(self.ui.miterBoxSlotLengthSpinBox.value))
    self._parameterNode.SetParameter("miterBoxSlotHeight", str(self.ui.miterBoxSlotHeightSpinBox.value))
    self._parameterNode.SetParameter("miterBoxSlotWall", str(self.ui.miterBoxSlotWallSpinBox.value))
    self._parameterNode.SetParameter("fibulaScrewHoleCylinderRadius", str(self.ui.fibulaScrewHoleCylinderRadiusSpinBox.value))
    self._parameterNode.SetParameter("clearanceFitPrintingTolerance", str(self.ui.clearanceFitPrintingToleranceSpinBox.value))
    self._parameterNode.SetParameter("biggerMiterBoxDistanceToFibula", str(self.ui.biggerMiterBoxDistanceToFibulaSpinBox.value))
    self._parameterNode.SetParameter("intersectionDistanceMultiplier", str(self.ui.intersectionDistanceMultiplierSpinBox.value))
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

    self._parameterNode.EndModify(wasModified)

  def onCreatePlanesButton(self):
    """
    Run processing when user clicks "Apply" button.
    """
    try:

      # Compute output
      self.logic.generateFibulaPlanes()
      
    except Exception as e:
      slicer.util.errorDisplay("Failed to compute results: "+str(e))
      import traceback
      traceback.print_exc()
    
    self.ui.updateFibulaPiecesButton.enabled = True

  def onAddMandibularCurveButton(self):
    self.logic.addMandibularCurve()

  def onAddFibulaLineButton(self):
    self.logic.addFibulaLine()

  def onScalarVolumeChanged(self):
    scalarVolume = self.ui.scalarVolumeSelector.currentNode()
    scalarVolumeID = scalarVolume.GetID()
    redSliceLogic = slicer.app.layoutManager().sliceWidget('Red').sliceLogic()
    redSliceLogic.GetSliceCompositeNode().SetBackgroundVolumeID(scalarVolumeID)
    greenSliceLogic = slicer.app.layoutManager().sliceWidget('Green').sliceLogic()
    greenSliceLogic.GetSliceCompositeNode().SetBackgroundVolumeID(scalarVolumeID)
    yellowSliceLogic = slicer.app.layoutManager().sliceWidget('Yellow').sliceLogic()
    yellowSliceLogic.GetSliceCompositeNode().SetBackgroundVolumeID(scalarVolumeID)
    
  def onAddCutPlaneButton(self):
    self.logic.addCutPlane()

  def onMakeModelsButton(self):
    self.logic.makeModels()
    self.ui.createPlanesButton.enabled = True

  def onUpdateFibulaPiecesButton(self):
    self.logic.updateFibulaPieces()
    self.ui.bonesToMandibleButton.enabled = True

  def onBonesToMandibleButton(self):
    self.logic.tranformBonePiecesToMandible()

  def onMandibularAutomaticPositioningButton(self):
    self.logic.mandiblePlanesPositioningForMaximumBoneContact()

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
    self.generateFibulaPlanesTimer = qt.QTimer()
    self.generateFibulaPlanesTimer.setInterval(300)
    self.generateFibulaPlanesTimer.setSingleShot(True)
    self.generateFibulaPlanesTimer.connect('timeout()', self.onPlaneModified)

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

    #setup placement
    slicer.modules.markups.logic().SetActiveListID(curveNode)
    interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
    interactionNode.SwitchToSinglePlaceMode()

  def addFibulaLine(self):
    lineNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLMarkupsLineNode")
    lineNode.SetName("temp")
    slicer.mrmlScene.AddNode(lineNode)
    slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(lineNode)
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    lineNodeItemID = shNode.GetItemByDataNode(lineNode)
    shNode.SetItemParent(lineNodeItemID, self.getParentFolderItemID())
    lineNode.SetName(slicer.mrmlScene.GetUniqueNameByString("fibulaLine"))

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

    #conections
    self.planeNodeObserver = planeNode.AddObserver(slicer.vtkMRMLMarkupsNode.PointPositionDefinedEvent,self.onPlanePointAdded)

    #setup placement
    slicer.modules.markups.logic().SetActiveListID(planeNode)
    interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
    interactionNode.SwitchToSinglePlaceMode()

  def onPlanePointAdded(self,sourceNode,event):
    parameterNode = self.getParameterNode()
    mandibleCurve = parameterNode.GetNodeReference("mandibleCurve")

    temporalOrigin = [0,0,0]
    sourceNode.GetNthControlPointPosition(0,temporalOrigin)
    
    self.setupMandiblePlaneStraightOverMandibleCurve(sourceNode,temporalOrigin, mandibleCurve, self.planeNodeObserver)

    displayNode = sourceNode.GetDisplayNode()
    displayNode.HandlesInteractiveOn()
    for i in range(3):
      sourceNode.SetNthControlPointVisibility(i,False)
    observer = sourceNode.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent,self.onPlaneModifiedTimer)
    self.mandiblePlaneObserversAndNodeIDList.append([observer,sourceNode.GetID()])
  
  def onPlaneModifiedTimer(self,sourceNode,event):
    self.generateFibulaPlanesTimer.start()

  def onPlaneModified(self):
    parameterNode = self.getParameterNode()
    fibulaLine = parameterNode.GetNodeReference("fibulaLine")

    if fibulaLine != None:
      try:
        # Compute output
        self.generateFibulaPlanes()

      except Exception as e:
        slicer.util.errorDisplay("Failed to compute results: "+str(e))
        import traceback
        traceback.print_exc()  

  def transformFibulaPlanes(self,fibulaModelNode,fibulaX,fibulaY,fibulaZ,fibulaOrigin,fibulaZLineNorm,planeList,fibulaPlanesList,initialSpace,intersectionPlaceOfFibulaPlanes,intersectionDistanceMultiplier,additionalBetweenSpaceOfFibulaPlanes):
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    mandible2FibulaTransformsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Mandible2Fibula transforms")

    #NewPlanes position and distance
    self.fibula2FibulaPlanesPositionA = []
    self.fibula2FibulaPlanesPositionB = []
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
      mandiblePlane0Normal = [0,0,0]
      mandiblePlane0.GetNormal(mandiblePlane0Normal)
      mandiblePlane1Normal = [0,0,0]
      mandiblePlane1.GetNormal(mandiblePlane1Normal)
      mandiblePlane0Origin = [0,0,0]
      mandiblePlane0.GetOrigin(mandiblePlane0Origin)
      mandiblePlane1Origin = [0,0,0]
      mandiblePlane1.GetOrigin(mandiblePlane1Origin)
      fibulaPlaneA = fibulaPlanesList[2*i]
      fibulaPlaneB = fibulaPlanesList[2*i+1]
      fibulaPlaneA.SetAxes([1,0,0], [0,1,0], [0,0,1])
      fibulaPlaneA.SetNormal(mandiblePlane0Normal)
      fibulaPlaneA.SetOrigin(mandiblePlane0Origin)
      fibulaPlaneB.SetAxes([1,0,0], [0,1,0], [0,0,1])
      fibulaPlaneB.SetNormal(mandiblePlane1Normal)
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
      mandiblePlane0.GetPlaneToWorldMatrix(mandiblePlane0matrix)
      mandiblePlane0Y = np.array([mandiblePlane0matrix.GetElement(0,1),mandiblePlane0matrix.GetElement(1,1),mandiblePlane0matrix.GetElement(2,1)])
      
      mandibleAxisX = [0,0,0]
      vtk.vtkMath.Cross(mandiblePlane0Y, mandibleAxisZ, mandibleAxisX)
      mandibleAxisX = mandibleAxisX/np.linalg.norm(mandibleAxisX)
      mandibleAxisY = [0,0,0]
      vtk.vtkMath.Cross(mandibleAxisZ, mandibleAxisX, mandibleAxisY)
      mandibleAxisY = mandibleAxisY/np.linalg.norm(mandibleAxisY)

      mandibleAxisToWorldRotationMatrix = self.getAxes1ToWorldRotationMatrix(mandibleAxisX, mandibleAxisY, mandibleAxisZ)
      fibulaToWorldRotationMatrix = self.getAxes1ToWorldRotationMatrix(fibulaX, fibulaY, fibulaZ)

      mandibleAxisToFibulaRotationMatrix = self.getAxes1ToAxes2RotationMatrix(mandibleAxisToWorldRotationMatrix, fibulaToWorldRotationMatrix)
      self.mandibleAxisToFibulaRotationMatrixesList.append(mandibleAxisToFibulaRotationMatrix)

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
        self.fibula2FibulaPlanesPositionA.append(fibulaZ*initialSpace)
        intersectionModelB = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Intersection%d_B' % i)
        intersectionModelB.CreateDefaultDisplayNodes()
        self.getIntersectionBetweenModelAnd1TransformedPlane(fibulaModelNode, mandiblePlane1ToIntersectionAxisTransform, fibulaPlaneB, intersectionModelB)
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
          self.getIntersectionBetweenModelAnd1TransformedPlane(fibulaModelNode, mandiblePlane0ToIntersectionAxisTransform, fibulaPlaneA, intersectionModelA)
          intersectionsList.append(intersectionModelA)
          intersectionModelAItemID = shNode.GetItemByDataNode(intersectionModelA)
          shNode.SetItemParent(intersectionModelAItemID, intersectionsFolder)
          j=j+1
          intersectionModelB = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Intersection%d_B' % i)
          intersectionModelB.CreateDefaultDisplayNodes()
          self.getIntersectionBetweenModelAnd1TransformedPlane(fibulaModelNode, mandiblePlane1ToIntersectionAxisTransform, fibulaPlaneB, intersectionModelB)
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
          self.getIntersectionBetweenModelAnd1TransformedPlane(fibulaModelNode, mandiblePlane0ToIntersectionAxisTransform, fibulaPlaneA, intersectionModelA)
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

        self.fibula2FibulaPlanesPositionA.append(self.fibula2FibulaPlanesPositionB[i-1] + fibulaZ*(intersectionDistanceMultiplier*betweenSpace[i-1]+additionalBetweenSpaceOfFibulaPlanes))

      self.fibula2FibulaPlanesPositionB.append(self.fibula2FibulaPlanesPositionA[i] + boneSegmentsDistance[i]*fibulaZ)

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
      mandiblePlane0ToFibulaPlaneATransform.Translate(fibulaOrigin)
      mandiblePlane0ToFibulaPlaneATransform.Translate(self.fibula2FibulaPlanesPositionA[i])

      mandiblePlane0ToFibulaPlaneATransformNode.SetMatrixTransformToParent(mandiblePlane0ToFibulaPlaneATransform.GetMatrix())
      mandiblePlane0ToFibulaPlaneATransformNode.UpdateScene(slicer.mrmlScene)


      mandiblePlane1ToFibulaPlaneBTransform = vtk.vtkTransform()
      mandiblePlane1ToFibulaPlaneBTransform.PostMultiply()
      mandiblePlane1ToFibulaPlaneBTransform.Translate(-mandiblePlane1Origin[0], -mandiblePlane1Origin[1], -mandiblePlane1Origin[2])
      mandiblePlane1ToFibulaPlaneBTransform.Concatenate(mandibleAxisToFibulaRotationMatrix)
      mandiblePlane1ToFibulaPlaneBTransform.Translate(fibulaOrigin)
      mandiblePlane1ToFibulaPlaneBTransform.Translate(self.fibula2FibulaPlanesPositionB[i])

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

  def createFibulaPlanesFromMandiblePlanesAndFibulaAxis(self,mandiblePlanesList,fibulaOrigin,fibulaPlanesList):
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    fibulaPlanesFolder = shNode.GetItemByName("Fibula planes")
    for i in range(len(mandiblePlanesList)-1):
      mandiblePlane0 = mandiblePlanesList[i]
      mandiblePlane1 = mandiblePlanesList[i+1]
      mandiblePlane0Normal = [0,0,0]
      mandiblePlane0.GetNormal(mandiblePlane0Normal)
      mandiblePlane1Normal = [0,0,0]
      mandiblePlane1.GetNormal(mandiblePlane1Normal)

      fibulaPlaneA = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsPlaneNode", "FibulaPlane%d_A" % i)
      slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(fibulaPlaneA)
      fibulaPlaneAItemID = shNode.GetItemByDataNode(fibulaPlaneA)
      shNode.SetItemParent(fibulaPlaneAItemID, fibulaPlanesFolder)
      fibulaPlaneA.SetAxes([1,0,0], [0,1,0], [0,0,1])
      fibulaPlaneA.SetNormal(mandiblePlane0Normal)
      fibulaPlaneA.SetOrigin(fibulaOrigin)
      fibulaPlaneA.SetLocked(True)
      fibulaPlanesList.append(fibulaPlaneA)

      fibulaPlaneB = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsPlaneNode", "FibulaPlane%d_B" % i)
      slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(fibulaPlaneB)
      fibulaPlaneBItemID = shNode.GetItemByDataNode(fibulaPlaneB)
      shNode.SetItemParent(fibulaPlaneBItemID, fibulaPlanesFolder)
      fibulaPlaneB.SetAxes([1,0,0], [0,1,0], [0,0,1])
      fibulaPlaneB.SetNormal(mandiblePlane1Normal)
      fibulaPlaneB.SetOrigin(fibulaOrigin)
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

  def createCutBonesWithDynamicModeler(self,planeList,fibulaPlanesList,mandibularCurve,fibulaModelNode,mandibleModelNode):
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    planeCutsFolder = shNode.GetItemByName("Plane Cuts")
    if planeCutsFolder == 0:
      cutBonesFolder = shNode.GetItemByName("Cut Bones")
      shNode.RemoveItem(cutBonesFolder)
      planeCutsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Plane Cuts")
      cutBonesFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Cut Bones")

      for i in range(0,len(fibulaPlanesList),2):
        modelNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLModelNode")
        modelNode.SetName("Fibula Segment {0}A-{1}B".format(i//2,i//2))
        slicer.mrmlScene.AddNode(modelNode)
        modelNode.CreateDefaultDisplayNodes()
        modelDisplay = modelNode.GetDisplayNode()
        #Set color of the model
        aux = slicer.mrmlScene.GetNodeByID('vtkMRMLColorTableNodeFileMediumChartColors.txt')
        colorTable = aux.GetLookupTable()
        nColors = colorTable.GetNumberOfColors()
        ind = int((nColors-1) - i/2)
        colorwithalpha = colorTable.GetTableValue(ind)
        color = [colorwithalpha[0],colorwithalpha[1],colorwithalpha[2]]
        modelDisplay.SetColor(color)

        #Determinate plane creation direction and set up dynamic modeler
        planeOriginStart = [0,0,0]
        planeOriginEnd = [0,0,0]
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
      modelDisplay = modelNode.GetDisplayNode()
      #Set color of the model
      aux = slicer.mrmlScene.GetNodeByID('vtkMRMLColorTableNodeFileMediumChartColors.txt')
      colorTable = aux.GetLookupTable()
      nColors = colorTable.GetNumberOfColors()
      ind = int((nColors-1) - (len(fibulaPlanesList)-1)/2 -1)
      colorwithalpha = colorTable.GetTableValue(ind)
      color = [colorwithalpha[0],colorwithalpha[1],colorwithalpha[2]]
      modelDisplay.SetColor(color)

      dynamicModelerNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLDynamicModelerNode")
      dynamicModelerNode.SetToolName("Plane cut")
      dynamicModelerNode.SetNodeReferenceID("PlaneCut.InputModel", mandibleModelNode.GetID())
      if closestCurvePointIndexStart > closestCurvePointIndexEnd:
        dynamicModelerNode.AddNodeReferenceID("PlaneCut.InputPlane", planeList[0].GetID())
        dynamicModelerNode.AddNodeReferenceID("PlaneCut.InputPlane", planeList[len(planeList)-1].GetID())
      else:
        dynamicModelerNode.AddNodeReferenceID("PlaneCut.InputPlane", planeList[len(planeList)-1].GetID())
        dynamicModelerNode.AddNodeReferenceID("PlaneCut.InputPlane", planeList[0].GetID()) 
      dynamicModelerNode.SetNodeReferenceID("PlaneCut.OutputPositiveModel", modelNode.GetID())
      dynamicModelerNode.SetAttribute("OperationType", "Difference")

      dynamicModelerNodeItemID = shNode.GetItemByDataNode(dynamicModelerNode)
      shNode.SetItemParent(dynamicModelerNodeItemID, planeCutsFolder)
      modelNodeItemID = shNode.GetItemByDataNode(modelNode)
      shNode.SetItemParent(modelNodeItemID, cutBonesFolder)

  def generateFibulaPlanes(self):
    parameterNode = self.getParameterNode()
    fibulaLine = parameterNode.GetNodeReference("fibulaLine")
    mandibularCurve = parameterNode.GetNodeReference("mandibleCurve")
    initialSpace = float(parameterNode.GetParameter("initialSpace"))
    intersectionPlaceOfFibulaPlanes = float(parameterNode.GetParameter("intersectionPlaceOfFibulaPlanes"))
    intersectionDistanceMultiplier = float(parameterNode.GetParameter("intersectionDistanceMultiplier"))
    additionalBetweenSpaceOfFibulaPlanes = float(parameterNode.GetParameter("additionalBetweenSpaceOfFibulaPlanes"))
    notLeftFibulaChecked = parameterNode.GetParameter("notLeftFibula") == "True"
    fibulaModelNode = parameterNode.GetNodeReference("fibulaModelNode")
    mandibleModelNode = parameterNode.GetNodeReference("mandibleModelNode")
    planeList = createListFromFolderID(self.getMandiblePlanesFolderItemID())
    
    if len(planeList) <= 1:
      return


    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()

    fibulaPlanesFolder = shNode.GetItemByName("Fibula planes")
    if fibulaPlanesFolder:
      fibulaPlanesList = createListFromFolderID(fibulaPlanesFolder)
      #delete all the folders that are not updated
      if ( len(fibulaPlanesList) != (2*len(planeList) - 2) ):
        shNode.RemoveItem(fibulaPlanesFolder)
        planeCutsFolder = shNode.GetItemByName("Plane Cuts")
        shNode.RemoveItem(planeCutsFolder)
        cutBonesFolder = shNode.GetItemByName("Cut Bones")
        shNode.RemoveItem(cutBonesFolder)

    #Delete old fibulaPlanesTransforms
    mandible2FibulaTransformsFolder = shNode.GetItemByName("Mandible2Fibula transforms")
    shNode.RemoveItem(mandible2FibulaTransformsFolder)

    #Create fibula axis:
    fibulaX, fibulaY, fibulaZ, fibulaOrigin = self.createFibulaAxisFromFibulaLineAndNotLeftChecked(fibulaLine,notLeftFibulaChecked) 
    
    fibulaPlanesFolder = shNode.GetItemByName("Fibula planes")
    fibulaPlanesList = createListFromFolderID(fibulaPlanesFolder)

    #Create fibula planes and set their size
    if fibulaPlanesFolder==0:
      fibulaPlanesFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Fibula planes")
      self.createFibulaPlanesFromMandiblePlanesAndFibulaAxis(planeList,fibulaOrigin,fibulaPlanesList)

    fibulaZLineNorm = self.getLineNorm(fibulaLine)

    self.transformFibulaPlanes(fibulaModelNode,fibulaX,fibulaY,fibulaZ,fibulaOrigin,fibulaZLineNorm,planeList,fibulaPlanesList,initialSpace,intersectionPlaceOfFibulaPlanes,intersectionDistanceMultiplier,additionalBetweenSpaceOfFibulaPlanes)

    self.createCutBonesWithDynamicModeler(planeList,fibulaPlanesList,mandibularCurve,fibulaModelNode,mandibleModelNode)
  
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
    parameterNode = self.getParameterNode()
    fibulaSegmentation = parameterNode.GetNodeReference("fibulaSegmentation")
    mandibularSegmentation = parameterNode.GetNodeReference("mandibularSegmentation")

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
    segmentations = [fibulaSegmentation,mandibularSegmentation]
    models = [fibulaModelNode,mandibleModelNode]
    for i in range(2):
      slicer.mrmlScene.AddNode(models[i])
      models[i].CreateDefaultDisplayNodes()

      seg = segmentations[i]
      seg.GetSegmentation().CreateRepresentation(slicer.vtkSegmentationConverter.GetSegmentationClosedSurfaceRepresentationName())
      #segmentID = seg.GetSegmentation().GetSegmentIdBySegmentName('fibulasegment')
      segmentID = seg.GetSegmentation().GetNthSegmentID(0)
      segment = seg.GetSegmentation().GetSegment(segmentID)

      logic = slicer.modules.segmentations.logic()
      logic.ExportSegmentToRepresentationNode(segment, models[i])

      modelNodeItemID = shNode.GetItemByDataNode(models[i])
      shNode.SetItemParent(modelNodeItemID, segmentationModelsFolder)

    parameterNode.SetNodeReferenceID("fibulaModelNode", fibulaModelNode.GetID())
    parameterNode.SetNodeReferenceID("mandibleModelNode", mandibleModelNode.GetID())

  def updateFibulaPieces(self):
    parameterNode = self.getParameterNode()
    mandibleModelNode = parameterNode.GetNodeReference("mandibleModelNode")
    mandibleModelDisplayNode = mandibleModelNode.GetDisplayNode()
    mandibleModelDisplayNode.SetVisibility(False)

    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    bonePiecesTransformFolder = shNode.GetItemByName("Bone Pieces Transforms")
    shNode.RemoveItem(bonePiecesTransformFolder)
    transformedFibulaPiecesFolder = shNode.GetItemByName("Transformed Fibula Pieces")
    shNode.RemoveItem(transformedFibulaPiecesFolder)
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

      oldOrigin = fibulaOrigin + (self.fibula2FibulaPlanesPositionA[i] + self.fibula2FibulaPlanesPositionB[i])/2

      fibulaPieceToMandibleAxisTransform = vtk.vtkTransform()
      fibulaPieceToMandibleAxisTransform.PostMultiply()
      #fibulaPieceToMandibleAxisTransform.Translate(-x1, -y1, -z1)
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
      transformedFibulaPiece.SetAndObserveTransformNodeID(fibulaPieceToMandibleAxisTransformNode.GetID())

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
  
  def getIntersectionBetweenModelAnd1TransformedPlane(self,modelNode,transform,planeNode,intersectionModel):
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

  def getIntersectionBetweenModelAnd1Plane(self,modelNode,planeNode,intersectionModel):
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

  def getNearestIntersectionBetweenModelAnd1Plane(self,modelNode,planeNode,intersectionModel):
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

  def getIntersectionBetweenModelAnd1PlaneWithNormalAndOrigin_2(self,modelNode,normal,origin,intersectionModel):
    plane = vtk.vtkPlane()
    plane.SetOrigin(origin)
    plane.SetNormal(normal)

    cutter = vtk.vtkCutter()
    cutter.SetInputData(modelNode.GetPolyData())
    cutter.SetCutFunction(plane)
    cutter.Update()

    intersectionModel.SetAndObservePolyData(cutter.GetOutput())

  def getIntersectionBetweenModelAnd1PlaneWithNormalAndOrigin(self,modelNode,normal,origin,intersectionModel):
    plane = vtk.vtkPlane()
    plane.SetOrigin(origin)
    plane.SetNormal(normal)

    clipper = vtk.vtkClipPolyData()
    clipper.SetInputData(modelNode.GetPolyData())
    clipper.SetClipFunction(plane)
    clipper.Update()

    intersectionModel.SetAndObservePolyData(clipper.GetOutput())

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

  def getAverageNormalFromModel(self,model):
    pointsOfModel = slicer.util.arrayFromModelPoints(model)
    normalsOfModel = slicer.util.arrayFromModelPointData(model, 'Normals')
    modelMesh = model.GetMesh()

    averageNormal = np.array([0,0,0])
    for pointID in range(len(pointsOfModel)):
      normalAtPointID = normalsOfModel[pointID]
      averageNormal = averageNormal + normalAtPointID
    
    averageNormal = averageNormal/len(pointsOfModel)

    return averageNormal

  def getAverageNormalFromModelPoint(self,model,point):
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

    averageNormal = self.getAverageNormalFromModel(cylinderIntersectionModel)

    slicer.mrmlScene.RemoveNode(cylinderIntersectionModel)

    return averageNormal


  def getCentroid(self,model):
    pd = model.GetPolyData().GetPoints().GetData()
    from vtk.util.numpy_support import vtk_to_numpy
    return np.average(vtk_to_numpy(pd), axis=0)

  def getPointOfATwoPointsModelThatMakesLineDirectionSimilarToVector(self,twoPointsModel,vector):
    pointsData = twoPointsModel.GetPolyData().GetPoints().GetData()
    from vtk.util.numpy_support import vtk_to_numpy

    points = vtk_to_numpy(pointsData)

    pointsVector = (points[1]-points[0])/np.linalg.norm(points[1]-points[0])

    if vtk.vtkMath.Dot(pointsVector, vector) > 0:
      return points[1]
    else:
      return points[0]

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

  def getLineNorm(self,line):
    lineStartPos = np.array([0,0,0])
    lineEndPos = np.array([0,0,0])
    line.GetNthControlPointPositionWorld(0, lineStartPos)
    line.GetNthControlPointPositionWorld(1, lineEndPos)
    return np.linalg.norm(lineEndPos-lineStartPos)
  
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
    notLeftFibulaChecked = parameterNode.GetParameter("notLeftFibula") == "True"
    fibulaModelNode = parameterNode.GetNodeReference("fibulaModelNode")

    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    fibulaPlanesFolder = shNode.GetItemByName("Fibula planes")
    fibulaPlanesList = createListFromFolderID(fibulaPlanesFolder)
    miterBoxesModelsFolder = shNode.GetItemByName("miterBoxes Models")
    shNode.RemoveItem(miterBoxesModelsFolder)
    biggerMiterBoxesModelsFolder = shNode.GetItemByName("biggerMiterBoxes Models")
    shNode.RemoveItem(biggerMiterBoxesModelsFolder)
    miterBoxesModelsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"miterBoxes Models")
    biggerMiterBoxesModelsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"biggerMiterBoxes Models")
    miterBoxesTransformsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"miterBoxes Transforms")
    intersectionsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Intersections")
    pointsIntersectionsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Points Intersections")

    #Create fibula axis:
    fibulaX, fibulaY, fibulaZ, fibulaOrigin = self.createFibulaAxisFromFibulaLineAndNotLeftChecked(fibulaLine,notLeftFibulaChecked) 

    for i in range(len(fibulaPlanesList)):
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
      miterBoxModel = self.createBox(miterBoxLength,miterBoxHeight,miterBoxWidth,miterBoxName)
      miterBoxModelItemID = shNode.GetItemByDataNode(miterBoxModel)
      shNode.SetItemParent(miterBoxModelItemID, miterBoxesModelsFolder)

      biggerMiterBoxWidth = miterBoxSlotWidth+2*clearanceFitPrintingTolerance+2*miterBoxSlotWall
      biggerMiterBoxLength = miterBoxSlotLength+2*miterBoxSlotWall
      biggerMiterBoxHeight = miterBoxSlotHeight
      biggerMiterBoxModel = self.createBox(biggerMiterBoxLength,biggerMiterBoxHeight,biggerMiterBoxWidth,biggerMiterBoxName)
      biggerMiterBoxModelItemID = shNode.GetItemByDataNode(biggerMiterBoxModel)
      shNode.SetItemParent(biggerMiterBoxModelItemID, biggerMiterBoxesModelsFolder)

      fibulaPlaneMatrix = vtk.vtkMatrix4x4()
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
      self.getIntersectionBetweenModelAnd1Plane(fibulaModelNode,fibulaPlanesList[i],intersectionModel)
      intersectionModelCentroid = self.getCentroid(intersectionModel)
      if i%2 == 0:
        pointsIntersectionModel = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Points Intersection%d_A' % (i//2))
      else:
        pointsIntersectionModel = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Points Intersection%d_B' % (i//2))
      pointsIntersectionModel.CreateDefaultDisplayNodes()
      self.getIntersectionBetweenModelAnd1PlaneWithNormalAndOrigin_2(intersectionModel,normalToMiterBoxDirectionAndFibulaZ,intersectionModelCentroid,pointsIntersectionModel)
      pointOfIntersection = self.getPointOfATwoPointsModelThatMakesLineDirectionSimilarToVector(pointsIntersectionModel,miterBoxDirection)
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

  
  def createBox(self, X, Y, Z, name):
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

      cylinderModel = self.createCylinder(fibulaScrewHoleCylinderRadius, "cylinder%d" % i)
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

      cylinderModel = self.createCylinder(mandibleScrewHoleCylinderRadius, "cylinder%d" % i)
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

  def createCylinder(self,R,name):
    cylinder = slicer.mrmlScene.CreateNodeByClass('vtkMRMLModelNode')
    cylinder.SetName(slicer.mrmlScene.GetUniqueNameByString(name))
    slicer.mrmlScene.AddNode(cylinder)
    cylinder.CreateDefaultDisplayNodes()
    lineSource = vtk.vtkLineSource()
    lineSource.SetPoint1(0, 0, 25)
    lineSource.SetPoint2(0, 0, -25)
    tubeFilter = vtk.vtkTubeFilter()
    tubeFilter.SetInputConnection(lineSource.GetOutputPort())
    tubeFilter.SetRadius(R)
    tubeFilter.SetNumberOfSides(50)
    tubeFilter.CappingOn()
    tubeFilter.Update()
    cylinder.SetAndObservePolyData(tubeFilter.GetOutput())
    return cylinder

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

    for i in range(len(biggerMiterBoxesModelsList)):
      combineModelsLogic.process(surgicalGuideModel, biggerMiterBoxesModelsList[i], surgicalGuideModel, 'union')

    for i in range(len(cylindersModelsList)):
      combineModelsLogic.process(surgicalGuideModel, cylindersModelsList[i], surgicalGuideModel, 'difference')

    for i in range(len(miterBoxesModelsList)):
      combineModelsLogic.process(surgicalGuideModel, miterBoxesModelsList[i], surgicalGuideModel, 'difference')

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
    sawBoxesModelsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"sawBoxes Models")
    biggerSawBoxesModelsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"biggerSawBoxes Models")
    sawBoxesTransformsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"sawBoxes Transforms")
    intersectionsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Intersections")
    pointsIntersectionsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Points Intersections")

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
      sawBoxModel = self.createBox(sawBoxLength,sawBoxHeight,sawBoxWidth,sawBoxName)
      sawBoxModelItemID = shNode.GetItemByDataNode(sawBoxModel)
      shNode.SetItemParent(sawBoxModelItemID, sawBoxesModelsFolder)

      biggerSawBoxWidth = sawBoxSlotWidth+2*clearanceFitPrintingTolerance+2*sawBoxSlotWall
      biggerSawBoxLength = sawBoxSlotLength+2*sawBoxSlotWall
      biggerSawBoxHeight = sawBoxSlotHeight
      biggerSawBoxModel = self.createBox(biggerSawBoxLength,biggerSawBoxHeight,biggerSawBoxWidth,biggerSawBoxName)
      biggerSawBoxModelItemID = shNode.GetItemByDataNode(biggerSawBoxModel)
      shNode.SetItemParent(biggerSawBoxModelItemID, biggerSawBoxesModelsFolder)

      mandiblePlaneMatrix = vtk.vtkMatrix4x4()
      mandibularPlanesList[i].GetPlaneToWorldMatrix(mandiblePlaneMatrix)
      mandiblePlaneZ = np.array([mandiblePlaneMatrix.GetElement(0,2),mandiblePlaneMatrix.GetElement(1,2),mandiblePlaneMatrix.GetElement(2,2)])
      mandiblePlaneOrigin = np.array([mandiblePlaneMatrix.GetElement(0,3),mandiblePlaneMatrix.GetElement(1,3),mandiblePlaneMatrix.GetElement(2,3)])

      closestCurvePoint = [0,0,0]
      closestCurvePointIndex = mandibularCurve.GetClosestPointPositionAlongCurveWorld(mandiblePlaneOrigin,closestCurvePoint)
      matrix = vtk.vtkMatrix4x4()
      mandibularCurve.GetCurvePointToWorldTransformAtPointIndex(closestCurvePointIndex,matrix)
      mandibularCurveX = np.array([matrix.GetElement(0,0),matrix.GetElement(1,0),matrix.GetElement(2,0)])
      normalToMandiblePlaneZAndMandibularCurveX = [0,0,0]
      vtk.vtkMath.Cross(mandiblePlaneZ, mandibularCurveX, normalToMandiblePlaneZAndMandibularCurveX)
      normalToMandiblePlaneZAndMandibularCurveX = normalToMandiblePlaneZAndMandibularCurveX/np.linalg.norm(normalToMandiblePlaneZAndMandibularCurveX)
      
      if i == 0:
        intersectionModel = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Intersection%d' % i)
      else:
        intersectionModel = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Intersection%d' % (len(mandibularPlanesList)-1))
      intersectionModel.CreateDefaultDisplayNodes()
      self.getNearestIntersectionBetweenModelAnd1Plane(mandibleModelNode,mandibularPlanesList[i],intersectionModel)
      intersectionModelCentroid = self.getCentroid(intersectionModel)
      if i == 0:
        pointsIntersectionModel = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Points Intersection%d' % i)
      else:
        pointsIntersectionModel = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Points Intersection%d' % (len(mandibularPlanesList)-1))
      pointsIntersectionModel.CreateDefaultDisplayNodes()
      self.getIntersectionBetweenModelAnd1PlaneWithNormalAndOrigin_2(intersectionModel,normalToMandiblePlaneZAndMandibularCurveX,intersectionModelCentroid,pointsIntersectionModel)
      anterior = [0,1,0]
      pointOfIntersection = self.getPointOfATwoPointsModelThatMakesLineDirectionSimilarToVector(pointsIntersectionModel,anterior)
      intersectionModelItemID = shNode.GetItemByDataNode(intersectionModel)
      shNode.SetItemParent(intersectionModelItemID, intersectionsFolder)
      pointsIntersectionModelItemID = shNode.GetItemByDataNode(pointsIntersectionModel)
      shNode.SetItemParent(pointsIntersectionModelItemID, pointsIntersectionsFolder)


      sawBoxDirection = self.getAverageNormalFromModelPoint(mandibleModelNode,pointOfIntersection)
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

      transformNode = slicer.vtkMRMLLinearTransformNode()
      transformNode.SetName("temp%d" % i)
      slicer.mrmlScene.AddNode(transformNode)

      finalTransform = vtk.vtkTransform()
      finalTransform.PostMultiply()
      finalTransform.Concatenate(WorldToSawBoxAxisRotationMatrix)
      if i == 0:
        sawBoxAxisXTranslation = 0
        sawBoxAxisYTranslation = biggerSawBoxHeight/2+biggerSawBoxDistanceToMandible
        sawBoxAxisZTranslation = sawBoxSlotWidth/2
      else:
        sawBoxAxisXTranslation = 0
        sawBoxAxisYTranslation = biggerSawBoxHeight/2+biggerSawBoxDistanceToMandible
        sawBoxAxisZTranslation = -sawBoxSlotWidth/2
      finalTransform.Translate(pointOfIntersection + sawBoxAxisX*sawBoxAxisXTranslation + sawBoxAxisY*sawBoxAxisYTranslation + sawBoxAxisZ*sawBoxAxisZTranslation)
      transformNode.SetMatrixTransformToParent(finalTransform.GetMatrix())

      transformNode.UpdateScene(slicer.mrmlScene)

      sawBoxModel.SetAndObserveTransformNodeID(transformNode.GetID())
      sawBoxModel.HardenTransform()
      biggerSawBoxModel.SetAndObserveTransformNodeID(transformNode.GetID())
      biggerSawBoxModel.HardenTransform()
      
      transformNodeItemID = shNode.GetItemByDataNode(transformNode)
      shNode.SetItemParent(transformNodeItemID, sawBoxesTransformsFolder)
    
    shNode.RemoveItem(sawBoxesTransformsFolder)
    shNode.RemoveItem(intersectionsFolder)
    shNode.RemoveItem(pointsIntersectionsFolder)
    
  def makeBooleanOperationsToMandibleSurgicalGuideBase(self):
    parameterNode = self.getParameterNode()
    mandibleSurgicalGuideBaseModel = parameterNode.GetNodeReference("mandibleSurgicalGuideBaseModel")
    mandibleBridgeModel = parameterNode.GetNodeReference("mandibleBridgeModel")
    

    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    mandibleCylindersModelsFolder = shNode.GetItemByName("Mandible Cylinders Models")
    cylindersModelsList = createListFromFolderID(mandibleCylindersModelsFolder)
    sawBoxesModelsFolder = shNode.GetItemByName("sawBoxes Models")
    miterBoxesModelsList = createListFromFolderID(sawBoxesModelsFolder)
    biggerSawBoxesModelsFolder = shNode.GetItemByName("biggerSawBoxes Models")
    biggerMiterBoxesModelsList = createListFromFolderID(biggerSawBoxesModelsFolder)

    combineModelsLogic = slicer.modules.combinemodels.widgetRepresentation().self().logic

    surgicalGuideModel = slicer.modules.models.logic().AddModel(mandibleSurgicalGuideBaseModel.GetPolyData())
    surgicalGuideModel.SetName(slicer.mrmlScene.GetUniqueNameByString('MandibleSurgicalGuidePrototype'))

    for i in range(len(biggerMiterBoxesModelsList)):
      combineModelsLogic.process(surgicalGuideModel, biggerMiterBoxesModelsList[i], surgicalGuideModel, 'union')
    
    combineModelsLogic.process(surgicalGuideModel, mandibleBridgeModel, surgicalGuideModel, 'union')

    for i in range(len(cylindersModelsList)):
      combineModelsLogic.process(surgicalGuideModel, cylindersModelsList[i], surgicalGuideModel, 'difference')

    for i in range(len(miterBoxesModelsList)):
      combineModelsLogic.process(surgicalGuideModel, miterBoxesModelsList[i], surgicalGuideModel, 'difference')



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