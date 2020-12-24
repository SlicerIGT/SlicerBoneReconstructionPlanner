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
    self.parent.categories = ["Examples"]  # TODO: set categories (folders where the module shows up in the module selector)
    self.parent.dependencies = []  # TODO: add here list of module names that this module requires
    self.parent.contributors = ["John Doe (AnyWare Corp.)"]  # TODO: replace with "Firstname Lastname (Organization)"
    # TODO: update with short description of the module and a link to online module documentation
    self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
See more information in <a href="https://github.com/organization/projectname#BoneReconstructionPlanner">module documentation</a>.
"""
    # TODO: replace with organization, grant and thanks
    self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc., Andras Lasso, PerkLab,
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
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
    self.mandibularPlanesList = []
    self.initialSpace = 0
    self.betweenSpace = 0
    self.mandibularFolder = 0

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
    self.ui.fibulaLineSelector.setMRMLScene(slicer.mrmlScene)
    self.ui.scalarVolumeSelector.setMRMLScene(slicer.mrmlScene)
    self.ui.mandibularSegmentationSelector.setMRMLScene(slicer.mrmlScene)
    self.ui.fibulaSegmentationSelector.setMRMLScene(slicer.mrmlScene)
    self.ui.planesTreeView.setMRMLScene(slicer.mrmlScene)
    

    #Setup the mandibular curve widget
    curveNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsCurveNode","mandibuleCurve")
    self.ui.mandibularCurvePlaceWidget.setButtonsVisible(False)
    self.ui.mandibularCurvePlaceWidget.placeButton().show()
    self.ui.mandibularCurvePlaceWidget.setMRMLScene(slicer.mrmlScene)
    self.ui.mandibularCurvePlaceWidget.placeMultipleMarkups = slicer.qSlicerMarkupsPlaceWidget.ForcePlaceSingleMarkup
    self.ui.mandibularCurvePlaceWidget.setCurrentNode(curveNode)
    #self.ui.mandibularCurvePlaceWidget.connect('activeMarkupsFiducialPlaceModeChanged(bool)', self.addFiducials)
    #Setup the fibula line widget
    lineNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsLineNode","fibulaLine")
    self.ui.fibulaLinePlaceWidget.setButtonsVisible(False)
    self.ui.fibulaLinePlaceWidget.placeButton().show()
    self.ui.fibulaLinePlaceWidget.setMRMLScene(slicer.mrmlScene)
    self.ui.fibulaLinePlaceWidget.placeMultipleMarkups = slicer.qSlicerMarkupsPlaceWidget.ForcePlaceSingleMarkup
    self.ui.fibulaLinePlaceWidget.setCurrentNode(lineNode)
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
    self.ui.scalarVolumeSelector.connect("nodeActivated(vtkMRMLNode*)", self.onScalarVolumeChanged)
    self.ui.addCutPlaneButton.connect('clicked(bool)',self.onAddCutPlaneButton)
    self.ui.makeModelsButton.connect('clicked(bool)',self.onMakeModelsButton)
    self.ui.updateFibulaPiecesButton.connect('clicked(bool)',self.onUpdateFibulaPiecesButton)
    self.ui.initialLineEdit.textEdited.connect(self.onInitialLineEdit)
    self.ui.betweenLineEdit.textEdited.connect(self.onBetweenLineEdit)


    # Buttons
    self.ui.createPlanesButton.connect('clicked(bool)', self.onCreatePlanesButton)

    # Make sure parameter node is initialized (needed for module reload)
    self.initializeParameterNode()

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
    self.createMandibularPlanesList()
    
    try:

      # Compute output
      self.logic.process(self.ui.fibulaLineSelector.currentNode(), self.mandibularPlanesList, self.initialSpace, self.betweenSpace)
      
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
    if shNode.GetItemName(self.mandibularFolder) == '':
      sceneItemID = shNode.GetSceneItemID() #My parent
      self.mandibularFolder = shNode.CreateFolderItem(sceneItemID,"Mandibular planes")
    shNode.CreateItem(self.mandibularFolder,planeNode)
    planeNode.SetName(slicer.mrmlScene.GetUniqueNameByString("mandibularPlane"))

    aux = slicer.mrmlScene.GetNodeByID('vtkMRMLColorTableNodeFileMediumChartColors.txt')
    colorTable = aux.GetLookupTable()
    name = planeNode.GetName()
    if len(name.split('_'))==1:
      ind = 0
    else:
      ind = int(name.split('_')[1])%8
    #ind = shNode.GetNumberOfItemChildren(self.mandibularFolder)-1
    colorwithalpha = colorTable.GetTableValue(ind)
    color = [colorwithalpha[0],colorwithalpha[1],colorwithalpha[2]]

    #display node of the plane
    displayNode = planeNode.GetDisplayNode()
    displayNode.SetGlyphScale(2.5)
    displayNode.SetSelectedColor(color)

    #conections
    planeNodeObserver = planeNode.AddObserver(slicer.vtkMRMLMarkupsNode.PointPositionDefinedEvent,self.onPlanePointAdded)

    #setup placement
    slicer.modules.markups.logic().SetActiveListID(planeNode)
    interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
    interactionNode.SetCurrentInteractionMode(slicer.vtkMRMLInteractionNode().Place);

  def onMakeModelsButton(self):
    self.logic.process2(self.ui.fibulaSegmentationSelector.currentNode(),self.ui.mandibularSegmentationSelector.currentNode())
    self.ui.createPlanesButton.enabled = True

  def onUpdateFibulaPiecesButton(self):
    self.logic.process3()

  def onPlanePointAdded(self,sourceNode,event):
    nControlPoints = sourceNode.GetNumberOfControlPoints()
    if nControlPoints ==3:
      displayNode = sourceNode.GetDisplayNode()
      displayNode.HandlesInteractiveOn()
      for i in range(nControlPoints):
        sourceNode.SetNthControlPointVisibility(i,False)
      planeNodeObserver = sourceNode.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent,self.onPlaneModified)
  
  def onPlaneModified(self,sourceNode,event):
    if self.ui.fibulaLineSelector.currentNodeID != '' and self.ui.updateFibulaPiecesButton.enabled:
      self.createMandibularPlanesList()

      try:
        # Compute output
        self.logic.process(self.ui.fibulaLineSelector.currentNode(), self.mandibularPlanesList, self.initialSpace, self.betweenSpace)

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
  
  def createMandibularPlanesList(self):
    self.mandibularPlanesList = []
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    myList = vtk.vtkIdList()
    shNode.GetItemChildren(self.mandibularFolder,myList)
    for i in range(myList.GetNumberOfIds()):
      self.mandibularPlanesList.append(shNode.GetItemDataNode(myList.GetId(i)))

  def numberOfPlanes(self):
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    return shNode.GetNumberOfItemChildren(self.mandibularFolder)
    


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
    self.fibulaFolder = 0
    self.transformsFolder = 0
    self.planeCutsFolder = 0
    self.cuttedBonesFolder = 0
    self.fibulaPlanesList = []
    self.planeCutsList = []

  def setDefaultParameters(self, parameterNode):
    """
    Initialize parameter node with default settings.
    """
    if not parameterNode.GetParameter("Threshold"):
      parameterNode.SetParameter("Threshold", "100.0")
    if not parameterNode.GetParameter("Invert"):
      parameterNode.SetParameter("Invert", "false")

  def process(self,fibulaLine,planeList,initialSpace,betweenSpace):
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    sceneItemID = shNode.GetSceneItemID()
    if self.transformsFolder:
      shNode.RemoveItem(self.transformsFolder)
      self.transformsFolder = ''

    self.transformsFolder = shNode.CreateFolderItem(sceneItemID,"Mandible2Fibula transforms")

    #Create line versor
    lineStartPos = np.zeros(3)
    lineEndPos = np.zeros(3)
    fibulaLine.GetNthControlPointPositionWorld(0, lineStartPos)
    fibulaLine.GetNthControlPointPositionWorld(1, lineEndPos)
    lineDirectionVersor = (lineEndPos-lineStartPos)/np.linalg.norm(lineEndPos-lineStartPos)

    #NewPlanes position and distance
    planesPositionA = []
    planesPositionB = []
    d = []
    
    #Create fibula planes and set their size
    if shNode.GetItemName(self.fibulaFolder) == '':
      self.fibulaFolder = shNode.CreateFolderItem(sceneItemID,"Fibula planes")
      self.fibulaPlanesList = []

      for i in range(len(planeList)-1):
        plane1 = planeList[i]
        plane2 = planeList[i+1]
        plane1Normal = [0,0,0]
        plane1.GetNormal(plane1Normal)
        plane2Normal = [0,0,0]
        plane2.GetNormal(plane2Normal)

        newPlane1 = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsPlaneNode", "FibulaPlane%d_A" % i)
        slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(newPlane1)
        shNode.CreateItem(self.fibulaFolder,newPlane1)
        newPlane1.SetNormal(plane1Normal)
        newPlane1.SetOrigin(lineStartPos)
        self.fibulaPlanesList.append(newPlane1)

        newPlane2 = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsPlaneNode", "FibulaPlane%d_B" % i)
        slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(newPlane2)
        shNode.CreateItem(self.fibulaFolder,newPlane2)
        newPlane2.SetNormal(plane2Normal)
        newPlane2.SetOrigin(lineStartPos)
        self.fibulaPlanesList.append(newPlane2)


        #Set new planes size
        oldPlanes = [plane1,plane2]
        newPlanes = [newPlane1,newPlane2]
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

      #Set up color for fibula planes
      for i in range(len(planeList)):
        if i == 0:
          oldDisplayNode = planeList[i].GetDisplayNode()
          color = oldDisplayNode.GetSelectedColor()

          displayNode = self.fibulaPlanesList[0].GetDisplayNode()
          displayNode.SetSelectedColor(color)
        else:
          if i == len(planeList)-1:
            oldDisplayNode = planeList[i].GetDisplayNode()
            color = oldDisplayNode.GetSelectedColor()

            displayNode = self.fibulaPlanesList[len(self.fibulaPlanesList)-1].GetDisplayNode()
            displayNode.SetSelectedColor(color)
          else:
            if ((i-1)%2)==0:
              oldDisplayNode = planeList[i].GetDisplayNode()
              color = oldDisplayNode.GetSelectedColor()

              displayNode1 = self.fibulaPlanesList[i].GetDisplayNode()
              displayNode1.SetSelectedColor(color)
              displayNode2 = self.fibulaPlanesList[i+1].GetDisplayNode()
              displayNode2.SetSelectedColor(color)

    #Transform fibula planes to their final position-orientation
    for i in range(len(planeList)-1):
      plane1 = planeList[i]
      plane2 = planeList[i+1]
      plane1Normal = [0,0,0]
      plane1.GetNormal(plane1Normal)
      plane2Normal = [0,0,0]
      plane2.GetNormal(plane2Normal)
      newPlane1 = self.fibulaPlanesList[2*i]
      newPlane2 = self.fibulaPlanesList[2*i+1]
      newPlane1.SetNormal(plane1Normal)
      newPlane1.SetOrigin(lineStartPos)
      newPlane2.SetNormal(plane2Normal)
      newPlane2.SetOrigin(lineStartPos)

      #Start transformations
      rotAxis = [0,0,0]
      vtk.vtkMath.Cross(plane1Normal, lineDirectionVersor, rotAxis)
      rotAxis = rotAxis/np.linalg.norm(rotAxis)
      angleRad = vtk.vtkMath.AngleBetweenVectors(plane1Normal, lineDirectionVersor)
      angleDeg = vtk.vtkMath.DegreesFromRadians(angleRad)

      #this versor is created to check if rotAxis is okey or should be opposite
      v1l = [0,0,0]
      q = [angleRad,rotAxis[0],rotAxis[1],rotAxis[2]]
      vtk.vtkMath.RotateVectorByWXYZ(plane1Normal,q,v1l)

      difference = np.linalg.norm(lineDirectionVersor-v1l)
      if (difference>0.01):
        rotAxis = [-rotAxis[0],-rotAxis[1],-rotAxis[2]]
        q = [angleRad,rotAxis[0],rotAxis[1],rotAxis[2]]
        vtk.vtkMath.RotateVectorByWXYZ(plane1Normal,q,v1l)
      
      v2l = [0,0,0]
      vtk.vtkMath.RotateVectorByWXYZ(plane2Normal,q,v2l)

      rotAxis2 = [0,0,0]
      vtk.vtkMath.Cross(v1l, v2l, rotAxis2)
      rotAxis2 = rotAxis2/np.linalg.norm(rotAxis2)
      angleRad2 = vtk.vtkMath.AngleBetweenVectors(v1l, v2l)/2
      angleDeg2 = vtk.vtkMath.DegreesFromRadians(angleRad2)

      #this versor is created to check if rotAxis2 is okey or should be opposite
      v2r = [0,0,0]
      q2 = [angleRad2,rotAxis2[0],rotAxis2[1],rotAxis2[2]]
      vtk.vtkMath.RotateVectorByWXYZ(v2l,q2,v2r)
      angleRad3 = vtk.vtkMath.AngleBetweenVectors(v1l, v2r)
      difference = abs(angleRad3 - angleRad2)
      if (difference>0.01):
        rotAxis2 = [-rotAxis2[0],-rotAxis2[1],-rotAxis2[2]]



      transformFidA = slicer.vtkMRMLLinearTransformNode()
      transformFidA.SetName("Mandible2Fibula Transform%d_A" % i)
      slicer.mrmlScene.AddNode(transformFidA)
      transformFidB = slicer.vtkMRMLLinearTransformNode()
      transformFidB.SetName("Mandible2Fibula Transform%d_B" % i)
      slicer.mrmlScene.AddNode(transformFidB)

      or1 = [0,0,0]
      or2 = [0,0,0]
      plane1.GetOrigin(or1)
      plane2.GetOrigin(or2)
      d.append(np.sqrt(vtk.vtkMath.Distance2BetweenPoints(or1,or2)))

      if i==0:
        planesPositionA.append(lineDirectionVersor*initialSpace)
      else:
        planesPositionA.append(planesPositionB[i-1] + lineDirectionVersor*betweenSpace)
      
      planesPositionB.append(planesPositionA[i] + d[i]*lineDirectionVersor)

      finalTransformA = vtk.vtkTransform()
      finalTransformA.PostMultiply()
      finalTransformA.Translate(-lineStartPos[0], -lineStartPos[1], -lineStartPos[2])
      finalTransformA.RotateWXYZ(angleDeg,rotAxis)
      finalTransformA.RotateWXYZ(angleDeg2,rotAxis2)
      finalTransformA.Translate(lineStartPos)
      finalTransformA.Translate(planesPositionA[i])

      transformFidA.SetMatrixTransformToParent(finalTransformA.GetMatrix())
      transformFidA.UpdateScene(slicer.mrmlScene)


      finalTransformB = vtk.vtkTransform()
      finalTransformB.PostMultiply()
      finalTransformB.Translate(-lineStartPos[0], -lineStartPos[1], -lineStartPos[2])
      finalTransformB.RotateWXYZ(angleDeg,rotAxis)
      finalTransformB.RotateWXYZ(angleDeg2,rotAxis2)
      finalTransformB.Translate(lineStartPos)
      finalTransformB.Translate(planesPositionB[i])

      transformFidB.SetMatrixTransformToParent(finalTransformB.GetMatrix())

      transformFidB.UpdateScene(slicer.mrmlScene)

      newPlane1.SetAndObserveTransformNodeID(transformFidA.GetID())
      newPlane2.SetAndObserveTransformNodeID(transformFidB.GetID())

      shNode.CreateItem(self.transformsFolder,transformFidA)
      shNode.CreateItem(self.transformsFolder,transformFidB)

    
    if shNode.GetItemName(self.planeCutsFolder) == '':
      if shNode.GetItemName(self.cuttedBonesFolder) != '':
        shNode.RemoveItem(self.cuttedBonesFolder)
        self.planeCutsList = []
      self.planeCutsFolder = shNode.CreateFolderItem(sceneItemID,"Plane Cuts")
      self.cuttedBonesFolder = shNode.CreateFolderItem(sceneItemID,"Cutted Bones")

      for i in range(0,len(self.fibulaPlanesList),2):
        modelNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLModelNode")
        modelNode.SetName("Fibula Segment {0}A-{1}B".format(i//2,i//2))
        slicer.mrmlScene.AddNode(modelNode)
        modelNode.CreateDefaultDisplayNodes()
        modelDisplay = modelNode.GetDisplayNode()
        #Set color of the model
        aux = slicer.mrmlScene.GetNodeByID('vtkMRMLColorTableNodeFileMediumChartColors.txt')
        colorTable = aux.GetLookupTable()
        ind = 7
        colorwithalpha = colorTable.GetTableValue(ind)
        color = [colorwithalpha[0],colorwithalpha[1],colorwithalpha[2]]
        modelDisplay.SetColor(color)

        dynamicModelerNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLDynamicModelerNode")
        dynamicModelerNode.SetToolName("Plane cut")
        dynamicModelerNode.SetNodeReferenceID("PlaneCut.InputModel", self.fibulaModelNode.GetID())
        dynamicModelerNode.AddNodeReferenceID("PlaneCut.InputPlane", self.fibulaPlanesList[i+1].GetID())
        dynamicModelerNode.AddNodeReferenceID("PlaneCut.InputPlane", self.fibulaPlanesList[i].GetID())
        dynamicModelerNode.SetNodeReferenceID("PlaneCut.OutputNegativeModel", modelNode.GetID())
        dynamicModelerNode.SetAttribute("OperationType", "Difference")
        self.planeCutsList.append(dynamicModelerNode)
        #slicer.modules.dynamicmodeler.logic().RunDynamicModelerTool(dynamicModelerNode)
        
        shNode.CreateItem(self.planeCutsFolder,dynamicModelerNode)
        shNode.CreateItem(self.cuttedBonesFolder,modelNode)
      
      
      modelNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLModelNode")
      modelNode.SetName("Cutted mandible")
      slicer.mrmlScene.AddNode(modelNode)
      modelNode.CreateDefaultDisplayNodes()
      modelDisplay = modelNode.GetDisplayNode()
      #Set color of the model
      aux = slicer.mrmlScene.GetNodeByID('vtkMRMLColorTableNodeFileMediumChartColors.txt')
      colorTable = aux.GetLookupTable()
      ind = 6
      colorwithalpha = colorTable.GetTableValue(ind)
      color = [colorwithalpha[0],colorwithalpha[1],colorwithalpha[2]]
      modelDisplay.SetColor(color)

      dynamicModelerNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLDynamicModelerNode")
      dynamicModelerNode.SetToolName("Plane cut")
      dynamicModelerNode.SetNodeReferenceID("PlaneCut.InputModel", self.mandibleModelNode.GetID())
      dynamicModelerNode.AddNodeReferenceID("PlaneCut.InputPlane", planeList[0].GetID())
      dynamicModelerNode.AddNodeReferenceID("PlaneCut.InputPlane", planeList[len(planeList)-1].GetID())
      dynamicModelerNode.SetNodeReferenceID("PlaneCut.OutputPositiveModel", modelNode.GetID())
      dynamicModelerNode.SetAttribute("OperationType", "Difference")
      self.planeCutsList.append(dynamicModelerNode)

      shNode.CreateItem(self.cuttedBonesFolder,modelNode)
      
      
    
  def process2(self,fibulaSegmentation,mandibleSegmentation):
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

  def process3(self):
    for i in range(len(self.planeCutsList)):
      slicer.modules.dynamicmodeler.logic().RunDynamicModelerTool(self.planeCutsList[i])





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
