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
    self.initialSpace = 0
    self.betweenSpace = 0

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

    #Setup the mandibular curve widget
    mandibularCurve = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsCurveNode","mandibuleCurve")
    self.ui.mandibularCurvePlaceWidget.setButtonsVisible(False)
    self.ui.mandibularCurvePlaceWidget.placeButton().show()
    self.ui.mandibularCurvePlaceWidget.setMRMLScene(slicer.mrmlScene)
    self.ui.mandibularCurvePlaceWidget.placeMultipleMarkups = slicer.qSlicerMarkupsPlaceWidget.ForcePlaceSingleMarkup
    self.ui.mandibularCurvePlaceWidget.setCurrentNode(mandibularCurve)
    #self.ui.mandibularCurvePlaceWidget.connect('activeMarkupsFiducialPlaceModeChanged(bool)', self.addFiducials)
    #Setup the fibula line widget
    fibulaLine = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode","fibulaLine")
    self.ui.fibulaLinePlaceWidget.setButtonsVisible(False)
    self.ui.fibulaLinePlaceWidget.placeButton().show()
    self.ui.fibulaLinePlaceWidget.setMRMLScene(slicer.mrmlScene)
    self.ui.fibulaLinePlaceWidget.placeMultipleMarkups = slicer.qSlicerMarkupsPlaceWidget.ForcePlaceSingleMarkup
    self.ui.fibulaLinePlaceWidget.setCurrentNode(fibulaLine)
    #self.ui.fibulaLinePlaceWidget.connect('activeMarkupsFiducialPlaceModeChanged(bool)', self.addFiducials)

    # Create logic class. Logic implements all computations that should be possible to run
    # in batch mode, without a graphical user interface.
    self.logic = BoneReconstructionPlannerLogic()

    # Connections

    # These connections ensure that we update parameter node when scene is closed
    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

    # These connections ensure that whenever user changes some settings on the GUI, that is saved in the MRML scene
    # (in the selected parameter node).
    self.ui.fibulaLineSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.mandibleCurveSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.scalarVolumeSelector.connect("nodeActivated(vtkMRMLNode*)", self.onScalarVolumeChanged)
    self.ui.initialLineEdit.textEdited.connect(self.onInitialLineEdit)
    self.ui.betweenLineEdit.textEdited.connect(self.onBetweenLineEdit)

    # Buttons
    self.ui.createPlanesButton.connect('clicked(bool)', self.onCreatePlanesButton)
    self.ui.addCutPlaneButton.connect('clicked(bool)',self.onAddCutPlaneButton)
    self.ui.makeModelsButton.connect('clicked(bool)',self.onMakeModelsButton)
    self.ui.updateFibulaPiecesButton.connect('clicked(bool)',self.onUpdateFibulaPiecesButton)
    self.ui.bonesToMandibleButton.connect('clicked(bool)',self.onBonesToMandibleButton)
    self.ui.mandibularAutomaticPositioningButton.connect('clicked(bool)',self.onMandibularAutomaticPositioningButton)
    

    # Make sure parameter node is initialized (needed for module reload)
    self.initializeParameterNode()

    #self._parameterNode.SetHideFromEditors(False)
    shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    #shNode.RequestOwnerPluginSearch(self._parameterNode)
    #self.ui.planesTreeView.setRootItem(shNode.GetItemByDataNode(self._parameterNode))
    mandibularCurveItemID = shNode.GetItemByDataNode(mandibularCurve)
    shNode.SetItemParent(mandibularCurveItemID, self.logic.getParentFolderItemID())
    fibulaLineItemID = shNode.GetItemByDataNode(fibulaLine)
    shNode.SetItemParent(fibulaLineItemID, self.logic.getParentFolderItemID())


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

  def enter(self):
    """
    Called each time the user opens this module.
    """
    # Make sure parameter node exists and observed
    self.initializeParameterNode()

  def exit(self):
    """
    Called each time the user opens a different module.
    """
    # Do not react to parameter node changes (GUI wlil be updated when the user enters into the module)
    self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

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

    # Select default input nodes if nothing is selected yet to save a few clicks for the user
    if not self._parameterNode.GetNodeReference("InputVolume"):
      firstVolumeNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
      if firstVolumeNode:
        self._parameterNode.SetNodeReferenceID("InputVolume", firstVolumeNode.GetID())

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
    
    # Update buttons states and tooltips
    if self._parameterNode.GetNodeReference("fibulaLine"):
      self.ui.createPlanesButton.toolTip = "Create fibula planes from mandibular planes"
      #self.ui.createPlanesButton.enabled = True
    else:
      self.ui.createPlanesButton.toolTip = "Select fibula line and mandibular planes"
      #self.ui.createPlanesButton.enabled = False

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
    
    self._parameterNode.EndModify(wasModified)

  def onCreatePlanesButton(self):
    """
    Run processing when user clicks "Apply" button.
    """
    mandibularPlanesList = createListFromFolderID(self.logic.getMandiblePlanesFolderItemID())
    
    try:

      # Compute output
      self.logic.generateFibulaPlanes(self.ui.fibulaLineSelector.currentNode(), self.ui.mandibleCurveSelector.currentNode(), mandibularPlanesList, self.initialSpace, self.betweenSpace, self.ui.rightFibulaCheckBox.isChecked())
      
    except Exception as e:
      slicer.util.errorDisplay("Failed to compute results: "+str(e))
      import traceback
      traceback.print_exc()
    
    self.ui.updateFibulaPiecesButton.enabled = True

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
    planeNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLMarkupsPlaneNode")
    planeNode.SetName("temp")
    slicer.mrmlScene.AddNode(planeNode)
    slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(planeNode)
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    mandibularFolderID = self.logic.getMandiblePlanesFolderItemID()
    planeNodeItemID = shNode.GetItemByDataNode(planeNode)
    shNode.SetItemParent(planeNodeItemID, mandibularFolderID)
    planeNode.SetName(slicer.mrmlScene.GetUniqueNameByString("mandibularPlane"))

    aux = slicer.mrmlScene.GetNodeByID('vtkMRMLColorTableNodeFileMediumChartColors.txt')
    colorTable = aux.GetLookupTable()
    name = planeNode.GetName()
    if len(name.split('_'))==1:
      ind = 0
    else:
      ind = int(name.split('_')[1])%8
    #ind = shNode.GetNumberOfItemChildren(mandibularFolderID)-1
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
    interactionNode.SetCurrentInteractionMode(slicer.vtkMRMLInteractionNode().Place);

  def onMakeModelsButton(self):
    self.logic.makeModels(self.ui.fibulaSegmentationSelector.currentNode(),self.ui.mandibularSegmentationSelector.currentNode())
    self.ui.createPlanesButton.enabled = True

  def onUpdateFibulaPiecesButton(self):
    self.logic.updateFibulaPieces()
    self.ui.bonesToMandibleButton.enabled = True

  def onBonesToMandibleButton(self):
    mandibularPlanesList = createListFromFolderID(self.logic.getMandiblePlanesFolderItemID())
    self.logic.tranformBonePiecesToMandible(mandibularPlanesList, self.ui.fibulaLineSelector.currentNode(), self.initialSpace, self.betweenSpace)

  def onMandibularAutomaticPositioningButton(self):
    mandibularPlanesList = createListFromFolderID(self.logic.getMandiblePlanesFolderItemID())
    self.logic.mandiblePlanesPositioningForMaximumBoneContact(self.ui.mandibleCurveSelector.currentNode(), mandibularPlanesList)
      

  def onPlanePointAdded(self,sourceNode,event):
    temporalOrigin = [0,0,0]
    sourceNode.GetNthControlPointPosition(0,temporalOrigin)
    
    self.logic.setupMandiblePlaneStraightOverMandibleCurve(sourceNode,temporalOrigin, self.ui.mandibleCurveSelector.currentNode(), self.planeNodeObserver)

    displayNode = sourceNode.GetDisplayNode()
    displayNode.HandlesInteractiveOn()
    for i in range(3):
      sourceNode.SetNthControlPointVisibility(i,False)
    planeNodeObserver = sourceNode.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent,self.onPlaneModified)
  
  def onPlaneModified(self,sourceNode,event):
    if self.ui.fibulaLineSelector.currentNodeID != '' and self.ui.updateFibulaPiecesButton.enabled:
      mandibularPlanesList = createListFromFolderID(self.logic.getMandiblePlanesFolderItemID())

      try:
        # Compute output
        self.logic.generateFibulaPlanes(self.ui.fibulaLineSelector.currentNode(), self.ui.mandibleCurveSelector.currentNode(), mandibularPlanesList, self.initialSpace, self.betweenSpace, self.ui.rightFibulaCheckBox.isChecked())

      except Exception as e:
        slicer.util.errorDisplay("Failed to compute results: "+str(e))
        import traceback
        traceback.print_exc()
      

  def onInitialLineEdit(self,text):
    if text!= '':
      self.initialSpace = float(text)
  
  def onBetweenLineEdit(self,text):
    if text!= '':
      self.betweenSpace = float(text)
    


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
    self.rotTransformParameters = []
    self.rotTransformParameters2 = []

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

  def remakeMandible2FibulaTransformsFolderID(self):
    shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
    folderSubjectHierarchyID = shNode.GetItemByName("Mandible2Fibula transforms")
    if folderSubjectHierarchyID:
      shNode.RemoveItem(folderSubjectHierarchyID)
      mandible2FibulaTransformsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Mandible2Fibula transforms")
      return mandible2FibulaTransformsFolder
    else:
      return shNode.CreateFolderItem(self.getParentFolderItemID(),"Mandible2Fibula transforms")

  

  def generateFibulaPlanes(self,fibulaLine,mandibularCurve,planeList,initialSpace,betweenSpace,rightFibulaChecked):
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    mandible2FibulaTransformsFolder = self.remakeMandible2FibulaTransformsFolderID()

    #Create fibula axis:
    lineStartPos = np.zeros(3)
    lineEndPos = np.zeros(3)
    fibulaLine.GetNthControlPointPositionWorld(0, lineStartPos)
    fibulaLine.GetNthControlPointPositionWorld(1, lineEndPos)
    fibulaOrigin = lineStartPos
    fibulaZ = (lineEndPos-lineStartPos)/np.linalg.norm(lineEndPos-lineStartPos)
    fibulaX = [0,0,0]
    fibulaY = [0,0,0]
    anteriorDirection = [0,1,0]
    posteriorDirection = [0,-1,0]
    if rightFibulaChecked:
      vtk.vtkMath.Cross(fibulaZ, anteriorDirection, fibulaX)
      fibulaX = fibulaX/np.linalg.norm(fibulaX)
    else:
      vtk.vtkMath.Cross(fibulaZ, posteriorDirection, fibulaX)
      fibulaX = fibulaX/np.linalg.norm(fibulaX)
    vtk.vtkMath.Cross(fibulaZ, fibulaX, fibulaY)
    fibulaY = fibulaY/np.linalg.norm(fibulaY)

    #NewPlanes position and distance
    fibula2FibulaPlanesPositionA = []
    fibula2FibulaPlanesPositionB = []
    boneSegmentsDistance = []
    
    
    fibulaPlanesFolder = shNode.GetItemByName("Fibula planes")
    fibulaPlanesList = createListFromFolderID(fibulaPlanesFolder)

    #Create fibula planes and set their size
    if fibulaPlanesFolder==0:
      fibulaPlanesFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Fibula planes")
      for i in range(len(planeList)-1):
        mandiblePlane0 = planeList[i]
        mandiblePlane1 = planeList[i+1]
        mandiblePlane0Normal = [0,0,0]
        mandiblePlane0.GetNormal(mandiblePlane0Normal)
        mandiblePlane1Normal = [0,0,0]
        mandiblePlane1.GetNormal(mandiblePlane1Normal)

        fibulaPlaneA = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsPlaneNode", "FibulaPlane%d_A" % i)
        slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(fibulaPlaneA)
        fibulaPlaneAItemID = shNode.GetItemByDataNode(fibulaPlaneA)
        shNode.SetItemParent(fibulaPlaneAItemID, fibulaPlanesFolder)
        fibulaPlaneA.SetNormal(mandiblePlane0Normal)
        fibulaPlaneA.SetOrigin(fibulaOrigin)
        fibulaPlanesList.append(fibulaPlaneA)

        fibulaPlaneB = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsPlaneNode", "FibulaPlane%d_B" % i)
        slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(fibulaPlaneB)
        fibulaPlaneBItemID = shNode.GetItemByDataNode(fibulaPlaneB)
        shNode.SetItemParent(fibulaPlaneBItemID, fibulaPlanesFolder)
        fibulaPlaneB.SetNormal(mandiblePlane1Normal)
        fibulaPlaneB.SetOrigin(fibulaOrigin)
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
      for i in range(len(planeList)):
        if i == 0:
          oldDisplayNode = planeList[i].GetDisplayNode()
          color = oldDisplayNode.GetSelectedColor()

          displayNode = fibulaPlanesList[0].GetDisplayNode()
          displayNode.SetSelectedColor(color)
        else:
          if i == len(planeList)-1:
            oldDisplayNode = planeList[i].GetDisplayNode()
            color = oldDisplayNode.GetSelectedColor()

            displayNode = fibulaPlanesList[len(fibulaPlanesList)-1].GetDisplayNode()
            displayNode.SetSelectedColor(color)
          else:
            oldDisplayNode = planeList[i].GetDisplayNode()
            color = oldDisplayNode.GetSelectedColor()

            displayNode1 = fibulaPlanesList[2*i-1].GetDisplayNode()
            displayNode1.SetSelectedColor(color)
            displayNode2 = fibulaPlanesList[2*i].GetDisplayNode()
            displayNode2.SetSelectedColor(color)

    self.rotTransformParameters = []
    self.rotTransformParameters2 = []

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
      fibulaPlaneA.SetNormal(mandiblePlane0Normal)
      fibulaPlaneA.SetOrigin(mandiblePlane0Origin)
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

      #Start transformations
      rotAxis = [0,0,0]
      vtk.vtkMath.Cross(mandibleAxisZ, fibulaZ, rotAxis)
      rotAxis = rotAxis/np.linalg.norm(rotAxis)
      angleRad = vtk.vtkMath.AngleBetweenVectors(mandibleAxisZ, fibulaZ)
      angleDeg = vtk.vtkMath.DegreesFromRadians(angleRad)

      #this vector is created to check if rotAxis is okey or should be opposite
      rotatedMandibleAxisZ = [0,0,0]
      rotation = [angleRad,rotAxis[0],rotAxis[1],rotAxis[2]]
      vtk.vtkMath.RotateVectorByWXYZ(mandibleAxisZ,rotation,rotatedMandibleAxisZ)

      rotatedMandibleAxisX = [0,0,0]
      vtk.vtkMath.RotateVectorByWXYZ(mandibleAxisX,rotation,rotatedMandibleAxisX)

      difference = np.linalg.norm(fibulaZ-rotatedMandibleAxisZ)
      if (difference>0.01):
        rotAxis = [-rotAxis[0],-rotAxis[1],-rotAxis[2]]
        rotation = [angleRad,rotAxis[0],rotAxis[1],rotAxis[2]]
        vtk.vtkMath.RotateVectorByWXYZ(mandibleAxisZ,rotation,rotatedMandibleAxisZ)
        vtk.vtkMath.RotateVectorByWXYZ(mandibleAxisX,rotation,rotatedMandibleAxisX)
      self.rotTransformParameters.append([rotAxis,angleDeg])

      #Start transformations
      rotAxis2 = fibulaZ
      rotAxis2 = rotAxis2/np.linalg.norm(rotAxis2)
      angleRad2 = vtk.vtkMath.AngleBetweenVectors(rotatedMandibleAxisX, fibulaX)
      angleDeg2 = vtk.vtkMath.DegreesFromRadians(angleRad2)

      #this vector is created to check if rotAxis is okey or should be opposite
      doublyRotatedMandibleAxisX = [0,0,0]
      rotation2 = [angleRad2,rotAxis2[0],rotAxis2[1],rotAxis2[2]]
      vtk.vtkMath.RotateVectorByWXYZ(rotatedMandibleAxisX,rotation2,doublyRotatedMandibleAxisX)

      difference = np.linalg.norm(fibulaX-doublyRotatedMandibleAxisX)
      if (difference>0.01):
        rotAxis2 = [-rotAxis2[0],-rotAxis2[1],-rotAxis2[2]]
        rotation2 = [angleRad2,rotAxis2[0],rotAxis2[1],rotAxis2[2]]
        vtk.vtkMath.RotateVectorByWXYZ(rotatedMandibleAxisX,rotation2,doublyRotatedMandibleAxisX)
      self.rotTransformParameters2.append([rotAxis2,angleDeg2])
      

      mandiblePlane0ToFibulaPlaneATransformNode = slicer.vtkMRMLLinearTransformNode()
      mandiblePlane0ToFibulaPlaneATransformNode.SetName("Mandible2Fibula Transform%d_A" % i)
      slicer.mrmlScene.AddNode(mandiblePlane0ToFibulaPlaneATransformNode)
      mandiblePlane1ToFibulaPlaneBTransformNode = slicer.vtkMRMLLinearTransformNode()
      mandiblePlane1ToFibulaPlaneBTransformNode.SetName("Mandible2Fibula Transform%d_B" % i)
      slicer.mrmlScene.AddNode(mandiblePlane1ToFibulaPlaneBTransformNode)

      if i==0:
        fibula2FibulaPlanesPositionA.append(fibulaZ*initialSpace)
      else:
        fibula2FibulaPlanesPositionA.append(fibula2FibulaPlanesPositionB[i-1] + fibulaZ*betweenSpace)
      
      fibula2FibulaPlanesPositionB.append(fibula2FibulaPlanesPositionA[i] + boneSegmentsDistance[i]*fibulaZ)

      mandiblePlane0ToFibulaPlaneATransform = vtk.vtkTransform()
      mandiblePlane0ToFibulaPlaneATransform.PostMultiply()
      mandiblePlane0ToFibulaPlaneATransform.Translate(-mandiblePlane0Origin[0], -mandiblePlane0Origin[1], -mandiblePlane0Origin[2])
      mandiblePlane0ToFibulaPlaneATransform.RotateWXYZ(angleDeg,rotAxis)
      mandiblePlane0ToFibulaPlaneATransform.RotateWXYZ(angleDeg2,rotAxis2)
      mandiblePlane0ToFibulaPlaneATransform.Translate(fibulaOrigin)
      mandiblePlane0ToFibulaPlaneATransform.Translate(fibula2FibulaPlanesPositionA[i])

      mandiblePlane0ToFibulaPlaneATransformNode.SetMatrixTransformToParent(mandiblePlane0ToFibulaPlaneATransform.GetMatrix())
      mandiblePlane0ToFibulaPlaneATransformNode.UpdateScene(slicer.mrmlScene)


      mandiblePlane1ToFibulaPlaneBTransform = vtk.vtkTransform()
      mandiblePlane1ToFibulaPlaneBTransform.PostMultiply()
      mandiblePlane1ToFibulaPlaneBTransform.Translate(-mandiblePlane1Origin[0], -mandiblePlane1Origin[1], -mandiblePlane1Origin[2])
      mandiblePlane1ToFibulaPlaneBTransform.RotateWXYZ(angleDeg,rotAxis)
      mandiblePlane1ToFibulaPlaneBTransform.RotateWXYZ(angleDeg2,rotAxis2)
      mandiblePlane1ToFibulaPlaneBTransform.Translate(fibulaOrigin)
      mandiblePlane1ToFibulaPlaneBTransform.Translate(fibula2FibulaPlanesPositionB[i])

      mandiblePlane1ToFibulaPlaneBTransformNode.SetMatrixTransformToParent(mandiblePlane1ToFibulaPlaneBTransform.GetMatrix())

      mandiblePlane1ToFibulaPlaneBTransformNode.UpdateScene(slicer.mrmlScene)

      fibulaPlaneA.SetAndObserveTransformNodeID(mandiblePlane0ToFibulaPlaneATransformNode.GetID())
      fibulaPlaneB.SetAndObserveTransformNodeID(mandiblePlane1ToFibulaPlaneBTransformNode.GetID())

      mandiblePlane0ToFibulaPlaneATransformNodeItemID = shNode.GetItemByDataNode(mandiblePlane0ToFibulaPlaneATransformNode)
      shNode.SetItemParent(mandiblePlane0ToFibulaPlaneATransformNodeItemID, mandible2FibulaTransformsFolder)
      mandiblePlane1ToFibulaPlaneBTransformNodeItemID = shNode.GetItemByDataNode(mandiblePlane1ToFibulaPlaneBTransformNode)
      shNode.SetItemParent(mandiblePlane1ToFibulaPlaneBTransformNodeItemID, mandible2FibulaTransformsFolder)

    
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
        ind = int(7 - i/2)
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
        dynamicModelerNode.SetNodeReferenceID("PlaneCut.InputModel", self.fibulaModelNode.GetID())
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
      modelNode.SetName("Cut mandible")
      slicer.mrmlScene.AddNode(modelNode)
      modelNode.CreateDefaultDisplayNodes()
      modelDisplay = modelNode.GetDisplayNode()
      #Set color of the model
      aux = slicer.mrmlScene.GetNodeByID('vtkMRMLColorTableNodeFileMediumChartColors.txt')
      colorTable = aux.GetLookupTable()
      ind = int(7 - (len(fibulaPlanesList)-1)/2 -1)
      colorwithalpha = colorTable.GetTableValue(ind)
      color = [colorwithalpha[0],colorwithalpha[1],colorwithalpha[2]]
      modelDisplay.SetColor(color)

      dynamicModelerNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLDynamicModelerNode")
      dynamicModelerNode.SetToolName("Plane cut")
      dynamicModelerNode.SetNodeReferenceID("PlaneCut.InputModel", self.mandibleModelNode.GetID())
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
    
  def makeModels(self,fibulaSegmentation,mandibleSegmentation):
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    segmentationModelsFolder = shNode.GetItemByName("Segmentation Models")
    if segmentationModelsFolder:
      shNode.RemoveItem(segmentationModelsFolder)
      segmentationModelsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Segmentation Models")
    else:
      segmentationModelsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Segmentation Models")
    self.fibulaModelNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLModelNode")
    self.fibulaModelNode.SetName("fibula")
    self.mandibleModelNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLModelNode")
    self.mandibleModelNode.SetName("mandible")
    segmentations = [fibulaSegmentation,mandibleSegmentation]
    models = [self.fibulaModelNode,self.mandibleModelNode]
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

  def updateFibulaPieces(self):
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    bonePiecesTransformFolder = shNode.GetItemByName("Bone Pieces Transforms")
    shNode.RemoveItem(bonePiecesTransformFolder)
    planeCutsList = createListFromFolderID(shNode.GetItemByName("Plane Cuts"))
    for i in range(len(planeCutsList)):
      slicer.modules.dynamicmodeler.logic().RunDynamicModelerTool(planeCutsList[i])

  def tranformBonePiecesToMandible(self,planeList,fibulaLine,initialSpace,betweenSpace):
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    bonePiecesTransformFolder = shNode.GetItemByName("Bone Pieces Transforms")
    if bonePiecesTransformFolder:
      shNode.RemoveItem(bonePiecesTransformFolder)
    bonePiecesTransformFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Bone Pieces Transforms")

    lineStartPos = np.zeros(3)
    lineEndPos = np.zeros(3)
    fibulaLine.GetNthControlPointPositionWorld(0, lineStartPos)
    fibulaLine.GetNthControlPointPositionWorld(1, lineEndPos)
    fibulaOrigin = lineStartPos
    fibulaZ = (lineEndPos-lineStartPos)/np.linalg.norm(lineEndPos-lineStartPos)

    boneSegmentsDistance = []
    fibula2FibulaPlanesPositionA = []
    fibula2FibulaPlanesPositionB = []
    cutBonesList = createListFromFolderID(shNode.GetItemByName("Cut Bones"))
    for i in range(len(cutBonesList)-1):

      or0 = np.zeros(3)
      planeList[i].GetOrigin(or0)
      or1 = np.zeros(3)
      planeList[i+1].GetOrigin(or1)
      origin = (or0+or1)/2

      boneSegmentsDistance.append(np.linalg.norm(or1-or0))

      if i==0:
        fibula2FibulaPlanesPositionA.append(fibulaZ*initialSpace)
      else:
        fibula2FibulaPlanesPositionA.append(fibula2FibulaPlanesPositionB[i-1] + fibulaZ*betweenSpace)
      
      fibula2FibulaPlanesPositionB.append(fibula2FibulaPlanesPositionA[i] + boneSegmentsDistance[i]*fibulaZ)

      rotAxis = self.rotTransformParameters[i][0]
      angleDeg = self.rotTransformParameters[i][1]
      rotAxis2 = self.rotTransformParameters2[i][0]
      angleDeg2 = self.rotTransformParameters2[i][1]

      fibulaPieceToMandibleAxisTransformNode = slicer.vtkMRMLLinearTransformNode()
      fibulaPieceToMandibleAxisTransformNode.SetName("Fibula Segment {0} Transform".format(i))
      slicer.mrmlScene.AddNode(fibulaPieceToMandibleAxisTransformNode)

      oldOrigin = fibulaOrigin + (fibula2FibulaPlanesPositionA[i] + fibula2FibulaPlanesPositionB[i])/2

      fibulaPieceToMandibleAxisTransform = vtk.vtkTransform()
      fibulaPieceToMandibleAxisTransform.PostMultiply()
      #fibulaPieceToMandibleAxisTransform.Translate(-x1, -y1, -z1)
      fibulaPieceToMandibleAxisTransform.Translate(-oldOrigin[0],-oldOrigin[1],-oldOrigin[2])
      fibulaPieceToMandibleAxisTransform.RotateWXYZ(-angleDeg2,rotAxis2)
      fibulaPieceToMandibleAxisTransform.RotateWXYZ(-angleDeg,rotAxis)
      fibulaPieceToMandibleAxisTransform.Translate(origin)

      fibulaPieceToMandibleAxisTransformNode.SetMatrixTransformToParent(fibulaPieceToMandibleAxisTransform.GetMatrix())
      fibulaPieceToMandibleAxisTransformNode.UpdateScene(slicer.mrmlScene)

      cutBonesList[i].SetAndObserveTransformNodeID(fibulaPieceToMandibleAxisTransformNode.GetID())

      fibulaPieceToMandibleAxisTransformNodeItemID = shNode.GetItemByDataNode(fibulaPieceToMandibleAxisTransformNode)
      shNode.SetItemParent(fibulaPieceToMandibleAxisTransformNodeItemID, bonePiecesTransformFolder)

  def mandiblePlanesPositioningForMaximumBoneContact(self,mandibularCurve, planeList):
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
      planeList[i+1].SetNormal(lineDirectionVector0.tolist())

      rotAxis = [0,0,0]
      vtk.vtkMath.Cross(lineDirectionVector0, lineDirectionVector1, rotAxis)
      rotAxis = rotAxis/np.linalg.norm(rotAxis)
      angleRad = vtk.vtkMath.AngleBetweenVectors(lineDirectionVector0, lineDirectionVector1)/2
      angleDeg = vtk.vtkMath.DegreesFromRadians(angleRad)

      transformNode = slicer.vtkMRMLLinearTransformNode()
      transformNode.SetName("temp%d" % (i+1))
      slicer.mrmlScene.AddNode(transformNode)

      finalTransform = vtk.vtkTransform()
      finalTransform.PostMultiply()
      finalTransform.Translate(-or1[0], -or1[1], -or1[2])
      finalTransform.RotateWXYZ(angleDeg,rotAxis)
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