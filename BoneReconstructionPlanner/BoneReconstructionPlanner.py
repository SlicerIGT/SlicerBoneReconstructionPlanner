import os
import unittest
import logging
import vtk, qt, ctk, slicer, math
import numpy as np
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from BRPLib.helperFunctions import *
from BRPLib.guiWidgets import *
from BRPLib.MOOSEHelper import *
from BRPLib.DentalSegmentatorHelper import *
import json
import traceback

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
    slicer.app.connect("startupCompleted()", addBRPLayout)

#
# Register sample data sets in Sample Data module
#

def registerSampleData():
  """
  Add datasets to Sample Data module.
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

def readDefaultParameters():
  """
  Return default parameters as a dict
  """
  defaultParametersPath = os.path.join(os.path.dirname(__file__), 'Resources/defaultParameters.json')
  # read as json and convert to dictionary
  with open(defaultParametersPath, 'r') as file:
    defaultParametersDict = json.load(file)
  return defaultParametersDict

def confirm_clean_and_load_test_data():
  """
  Show dialog to load test data
  """
  confirm_close_msg_box = ctk.ctkMessageBox()
  confirm_close_msg_box.setAttribute(qt.Qt.WA_DeleteOnClose)
  confirm_close_msg_box.setWindowTitle("Delete everything and load test data?")
  confirm_close_msg_box.setText("The scene will be cleaned and test data will be loaded. Do you want to proceed?")

  confirm_close_msg_box.addButton("Clean scene and load test data", qt.QMessageBox.AcceptRole)
  confirm_close_msg_box.addButton(qt.QMessageBox.Cancel)

  confirm_close_msg_box.setIcon(qt.QMessageBox.Question)
  result_code = confirm_close_msg_box.exec()

  if result_code == qt.QMessageBox.Cancel:
    return False
  if result_code == qt.QMessageBox.AcceptRole:
    import SampleData
    sampleDataLogic = SampleData.SampleDataLogic()
    sampleDataLogic.downloadSample('CTMandible')
    sampleDataLogic.downloadSample('CTFibula')
    sampleDataLogic.downloadSample('MandibleSegmentation')
    sampleDataLogic.downloadSample('FibulaSegmentation')
  return True

def setLightingMode(renderingMode = "Lamp"):
  """
  Select rendering mode
  """
  try:
    lightsLogic = slicer.modules.lights.widgetRepresentation().self().logic
  except:
    errorString = "BoneReconstructionPlanner: Lights module is not available. Install Sandbox extension"
    slicer.util.messageBox(
      errorString, 
      dontShowAgainSettingsKey = "BRP/MissingSandboxExtension"
    )
    return
  viewNodesList = slicer.util.getNodesByClass("vtkMRMLViewNode")
  for viewNode in viewNodesList:
    lightsLogic.addManagedView(viewNode)
  if renderingMode == "Lamp":
    lightsLogic.setUseLightKit(False)
    lightsLogic.setSingleLightIntensity(1.0)
    lightsLogic.setUseSSAO(False)
  elif renderingMode == "Lamp and Shadows":
    lightsLogic.setUseLightKit(False)
    lightsLogic.setSingleLightIntensity(1.0)
    lightsLogic.setUseSSAO(True)
  elif renderingMode == "MultiLamp":
    lightsLogic.setUseLightKit(True)
    lightsLogic.setUseSSAO(False)
  elif renderingMode == "MultiLamp and Shadows":
    lightsLogic.setUseLightKit(True)
    lightsLogic.setUseSSAO(True)

def displayOrientation3DCube(display):
  """
  Select visibility of the 3D Cube on the corner of the 3D views
  """
  threeDViewNodes = slicer.util.getNodesByClass("vtkMRMLViewNode")
  if len(threeDViewNodes) == 0:
    return
  for viewNode in threeDViewNodes:
    if display:
      viewNode.SetOrientationMarkerType(slicer.vtkMRMLAbstractViewNode.OrientationMarkerTypeCube)
    else:
      viewNode.SetOrientationMarkerType(slicer.vtkMRMLAbstractViewNode.OrientationMarkerTypeNone)
    viewNode.SetOrientationMarkerSize(slicer.vtkMRMLAbstractViewNode.OrientationMarkerSizeMedium)

def setModelsLightingInterpolationMethod(interpolationMethod = "Gouraud"):
  """
  Select models' lighting interpolation method
  """
  DEFAULT_LIGHTING_VALUES_GOURAUD = {
    "Ambient": 0.0,
    "Diffuse": 1.0,
    "Specular": 0.0,
    "Power": 1.0,
    "Metallic": 0.0,
    "Roughness": 0.5
  }
  PREFERRED_LIGHTING_EMPIRICAL_VALUES_PBR = {
    "Diffuse": 1.0,
    "Metallic": 0.0,
    "Roughness": 0.3
  }

  shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
  folderSubjectHierarchyID = shNode.GetItemByName("BoneReconstructionPlanner")
  childIDs = vtk.vtkIdList()
  shNode.GetItemChildren(folderSubjectHierarchyID, childIDs, True)

  for id in range(childIDs.GetNumberOfIds()):
    itemID = childIDs.GetId(id)
    dataNode = shNode.GetItemDataNode(itemID)
    if (dataNode is None) or not(dataNode.IsA("vtkMRMLModelNode")):
      continue
    displayNode = dataNode.GetDisplayNode()
    if displayNode:
      if interpolationMethod == "PBR":
        # Set interpolation to PBR
        displayNode.SetInterpolation(slicer.vtkMRMLDisplayNode.PBRInterpolation)
        displayNode.SetDiffuse(PREFERRED_LIGHTING_EMPIRICAL_VALUES_PBR["Diffuse"])
        displayNode.SetMetallic(PREFERRED_LIGHTING_EMPIRICAL_VALUES_PBR["Metallic"])
        displayNode.SetRoughness(PREFERRED_LIGHTING_EMPIRICAL_VALUES_PBR["Roughness"])
      elif interpolationMethod == "Gouraud":
        # Set interpolation to Gouraud
        displayNode.SetInterpolation(slicer.vtkMRMLDisplayNode.GouraudInterpolation)
        displayNode.SetAmbient(DEFAULT_LIGHTING_VALUES_GOURAUD["Ambient"])
        displayNode.SetDiffuse(DEFAULT_LIGHTING_VALUES_GOURAUD["Diffuse"])
        displayNode.SetSpecular(DEFAULT_LIGHTING_VALUES_GOURAUD["Specular"])
        displayNode.SetPower(DEFAULT_LIGHTING_VALUES_GOURAUD["Power"])
        displayNode.SetMetallic(DEFAULT_LIGHTING_VALUES_GOURAUD["Metallic"])
        displayNode.SetRoughness(DEFAULT_LIGHTING_VALUES_GOURAUD["Roughness"])

slicer.MANDIBLE_VIEW_SINGLETON_TAG = "1"
slicer.FIBULA_VIEW_SINGLETON_TAG = "2"
slicer.RED_VIEW_ID = "vtkMRMLSliceNodeRed"
slicer.MANDIBLE_VIEW_ID = "vtkMRMLViewNode1"
slicer.FIBULA_VIEW_ID = "vtkMRMLViewNode2"
slicer.BRPLayoutId=101
slicer.PLANE_SIDE_SIZE = 50.
slicer.PLANE_GLYPH_SCALE = 2.5
slicer.SURGICAL_GUIDE_COLOR = [243/255, 149/255, 42/255] # orange

USING_GUI = not(slicer.app.commandOptions().noMainWindow)

def addBRPLayout():
  if not USING_GUI:
    return

  BRPLayout = f"""
    <layout type="vertical">
    <item>
      <layout type="horizontal">
      <item>
        <view class="vtkMRMLViewNode" singletontag="{slicer.MANDIBLE_VIEW_SINGLETON_TAG}">
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
      <view class="vtkMRMLViewNode" singletontag="{slicer.FIBULA_VIEW_SINGLETON_TAG}">
      <property name="viewlabel" action="default">2</property>
      </view>
    </item>
    </layout>
  """
  # Built-in layout IDs are all below 100, so you can choose any large random number
  # for your custom layout ID.

  # Add button to layout selector toolbar for this custom layout
  viewToolBar = slicer.util.mainWindow().findChild('QToolBar', 'ViewToolBar')
  layoutMenu = viewToolBar.widgetForAction(viewToolBar.actions()[0]).menu()
  layoutSwitchActionParent = layoutMenu  # use `layoutMenu` to add inside layout list, use `viewToolBar` to add next the standard layout list
  BRPLayoutExists = False
  for action in layoutSwitchActionParent.actions():
    if action.data() == slicer.BRPLayoutId:
      BRPLayoutExists = True
      break
  if not BRPLayoutExists:
    layoutManager = slicer.app.layoutManager()
    layoutManager.layoutLogic().GetLayoutNode().AddLayoutDescription(slicer.BRPLayoutId, BRPLayout)
    # add it to layout menu
    layoutSwitchAction = layoutSwitchActionParent.addAction("BoneReconstructionPlanner") # add inside layout list
    layoutSwitchAction.setData(slicer.BRPLayoutId)
    layoutSwitchAction.setIcon(qt.QIcon(':Icons/Go.png'))
    layoutSwitchAction.setToolTip('3D Mandible View, Red Slice and 3D Fibula View')
    return True
  return False

def setBRPLayout():
  if not USING_GUI:
    return
  layoutManager = slicer.app.layoutManager()
  layoutManager.setLayout(slicer.BRPLayoutId)

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
    self.version = "5.8.1.08.09" # Slicer stable release version + BRP code date
    ScriptedLoadableModuleWidget.__init__(self, parent)
    VTKObservationMixin.__init__(self)  # needed for parameter node observation
    self.logic = None
    self._parameterNode = None
    self._shNode = None
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

    #processingLabel = qt.QLabel("Processing...")
    #processingLabel.setAlignment(qt.Qt.AlignCenter)
    #processingLabel.setStyleSheet("QLabel {color: green; font-family: 'Lato Semibold'; font-size: 30pt;}")
    #slicer.util.mainWindow().statusBar().insertWidget(0,processingLabel)
    #self.ui.processingLabel = processingLabel

    # additional UI setup
    self.ui.versionLabel.text = f"Version: {self.version}" 

    import os
    updatePlanningIconPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons/update_48.svg')

    generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandibleButton = checkablePushButtonWithIcon(
      "Update\nvirtual\nplan",
      qt.QIcon(updatePlanningIconPath)
    )
    generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandibleButton.setToolTip(
      "Update fibula planes over fibula line;\nupdate fibula bone pieces \nand transform them to mandible"
    )
    
    updateVSPButtonsLayout = self.ui.updateVSPButtonsFrame.layout()
    updateVSPButtonsLayout.insertWidget(0, generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandibleButton)

    self.ui.generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandibleButton = generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandibleButton

    mailIconPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons/mail_48.svg')
    self.ui.emailBugReportButton.setIcon(qt.QIcon(mailIconPath))
    self.ui.emailFeatureRequestButton.setIcon(qt.QIcon(mailIconPath))
    
    openDocumentationIconPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons/quick_reference_48.svg')
    self.ui.openDocumentationButton.setIcon(qt.QIcon(openDocumentationIconPath))

    testDataIconPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons/experiment_48.svg')
    self.ui.loadTestCaseButton.setIcon(qt.QIcon(testDataIconPath))

    boneIconPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons/bone_48.svg')
    self.ui.makeModelsButton.setIcon(qt.QIcon(boneIconPath))

    fibulaNormalizationTransformIconPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons/fibula_normalization_transform.png')
    self.ui.fibulaNormalizationTransformButton.setIcon(qt.QIcon(fibulaNormalizationTransformIconPath))

    #targetIconPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons/target_48.svg')
    #self.ui.centerFibulaLineButton.setIcon(qt.QIcon(targetIconPath))
    
    planeIconPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons/MarkupsPlaneMouseModePlaceAdd.png')
    self.ui.addCutPlaneButton.setIcon(qt.QIcon(planeIconPath))
    trashbinIconPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons/MarkupsDelete.png')
    self.ui.removeCutPlaneButton.setIcon(qt.QIcon(trashbinIconPath))
    visibilityIconPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons/visibility_48.svg')
    self.ui.interCondylarBeamVisibilityToolButton.setIcon(qt.QIcon(visibilityIconPath))
    increaseIconPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons/add_48.svg')
    self.ui.interCondylarBeamIncreaseSizeButton.setIcon(qt.QIcon(increaseIconPath))
    decreaseIconPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons/remove_48.svg')
    self.ui.interCondylarBeamDecreaseSizeButton.setIcon(qt.QIcon(decreaseIconPath))

    self.ui.neomandibleVisibilityButton.setIcon(qt.QIcon(visibilityIconPath))
    
    recycleIconPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons/recycle_48.svg')
    self.ui.hardVSPUpdateButton.setIcon(qt.QIcon(recycleIconPath))
    
    lockIconPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons/lock_48.svg')
    self.ui.lockVSPButton.setIcon(qt.QIcon(lockIconPath))

    self.ui.showMandiblePlanesToolButton.setIcon(qt.QIcon(visibilityIconPath))
    self.ui.showMandiblePlanesToolButton.setIconSize(qt.QSize(24,24))
    self.ui.showMandiblePlanesToolButton.setMinimumSize(24,24)

    axesIconPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons/axes.svg')
    self.ui.showMandiblePlanesInteractionHandlesToolButton.setIcon(qt.QIcon(axesIconPath))
    self.ui.showMandiblePlanesInteractionHandlesToolButton.setIconSize(qt.QSize(24,24))
    self.ui.showMandiblePlanesInteractionHandlesToolButton.setMinimumSize(24,24)

    inCameraPlaneIconPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons/linked_camera_48.svg')
    self.ui.inCameraPlaneInteractionHandlesToolButton.setIcon(qt.QIcon(inCameraPlaneIconPath))
    self.ui.inCameraPlaneInteractionHandlesToolButton.setIconSize(qt.QSize(24,24))
    self.ui.inCameraPlaneInteractionHandlesToolButton.setMinimumSize(24,24)

    booleanOperationsIconPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons/construction_48.svg')
    self.ui.create3DModelOfTheReconstructionButton.setIcon(qt.QIcon(booleanOperationsIconPath))
    self.ui.makeBooleanOperationsToFibulaSurgicalGuideBaseButton.setIcon(qt.QIcon(booleanOperationsIconPath))
    self.ui.makeBooleanOperationsToFibulaSurgicalGuideBaseButton.setIconSize(qt.QSize(48,48))
    self.ui.makeBooleanOperationsToMandibleSurgicalGuideBaseButton.setIcon(qt.QIcon(booleanOperationsIconPath))
    self.ui.makeBooleanOperationsToMandibleSurgicalGuideBaseButton.setIconSize(qt.QSize(48,48))

    #self.ui.dentalImplantCylinderSelector.addAttribute('vtkMRMLModelNode','isDentalImplantCylinder','True')



    # Create logic class. Logic implements all computations that should be possible to run
    # in batch mode, without a graphical user interface.
    self.logic = BoneReconstructionPlannerLogic()

    # mandibularCurvePlaceWidget
    placeWidget = self.ui.mandibleCurvePlaceWidget
    placeWidget.setInteractionNode(slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton"))
    placeWidget.setCurrentNode(self.logic.getMandibularCurve())
    placeWidget.buttonsVisible = False
    placeWidget.placeButton().show()
    placeWidget.deleteButton().show()
    placeWidget.placeMultipleMarkups = slicer.qSlicerMarkupsPlaceWidget.ForcePlaceSingleMarkup
    placeWidget.setDeleteAllControlPointsOptionVisible(False)

    # fibulaLinePlaceWidget
    placeWidget = self.ui.fibulaLinePlaceWidget
    placeWidget.setInteractionNode(slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton"))
    placeWidget.setCurrentNode(self.logic.getFibulaLine())
    placeWidget.buttonsVisible = False
    placeWidget.placeButton().show()
    placeWidget.deleteButton().show()
    #placeWidget.placeMultipleMarkups = slicer.qSlicerMarkupsPlaceWidget.ForcePlaceMultipleMarkups
    placeWidget.placeMultipleMarkups = slicer.qSlicerMarkupsPlaceWidget.ForcePlaceSingleMarkup
    placeWidget.setDeleteAllControlPointsOptionVisible(False)

    # interCondylarBeamLinePlaceWidget
    placeWidget = self.ui.interCondylarBeamLinePlaceWidget
    placeWidget.setInteractionNode(slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton"))
    placeWidget.setCurrentNode(self.logic.getInterCondylarBeamLine())
    placeWidget.buttonsVisible = False
    placeWidget.placeButton().show()
    placeWidget.deleteButton().show()
    #placeWidget.placeMultipleMarkups = slicer.qSlicerMarkupsPlaceWidget.ForcePlaceMultipleMarkups
    placeWidget.placeMultipleMarkups = slicer.qSlicerMarkupsPlaceWidget.ForcePlaceSingleMarkup
    placeWidget.setDeleteAllControlPointsOptionVisible(False)

    # miterBoxLinePlaceWidget
    placeWidget = self.ui.miterBoxDirectionLinePlaceWidget
    placeWidget.setInteractionNode(slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton"))
    placeWidget.setCurrentNode(self.logic.getMiterBoxDirectionLine())
    placeWidget.buttonsVisible = False
    placeWidget.placeButton().show()
    placeWidget.deleteButton().show()
    #placeWidget.placeMultipleMarkups = slicer.qSlicerMarkupsPlaceWidget.ForcePlaceMultipleMarkups
    placeWidget.placeMultipleMarkups = slicer.qSlicerMarkupsPlaceWidget.ForcePlaceSingleMarkup
    placeWidget.setDeleteAllControlPointsOptionVisible(False)

    # fibulaFiducialsPlaceWidget
    placeWidget = self.ui.fibulaFiducialsPlaceWidget
    placeWidget.setInteractionNode(slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton"))
    placeWidget.setCurrentNode(self.logic.getFibulaFiducials())
    placeWidget.buttonsVisible = False
    placeWidget.placeButton().show()
    placeWidget.deleteButton().show()
    #placeWidget.placeMultipleMarkups = slicer.qSlicerMarkupsPlaceWidget.ForcePlaceMultipleMarkups
    placeWidget.placeMultipleMarkups = slicer.qSlicerMarkupsPlaceWidget.ForcePlaceSingleMarkup
    placeWidget.setDeleteAllControlPointsOptionVisible(False)

    # mandibleFiducialsPlaceWidget
    placeWidget = self.ui.mandibleFiducialsPlaceWidget
    placeWidget.setInteractionNode(slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton"))
    placeWidget.setCurrentNode(self.logic.getMandibleFiducials())
    placeWidget.buttonsVisible = False
    placeWidget.placeButton().show()
    placeWidget.deleteButton().show()
    #placeWidget.placeMultipleMarkups = slicer.qSlicerMarkupsPlaceWidget.ForcePlaceMultipleMarkups
    placeWidget.placeMultipleMarkups = slicer.qSlicerMarkupsPlaceWidget.ForcePlaceSingleMarkup
    placeWidget.setDeleteAllControlPointsOptionVisible(False)

    # mandibleBridgeCurvePlaceWidget
    placeWidget = self.ui.mandibleBridgeCurvePlaceWidget
    placeWidget.setInteractionNode(slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton"))
    placeWidget.setCurrentNode(self.logic.getMandibleBridgeCurve())
    placeWidget.buttonsVisible = False
    placeWidget.placeButton().show()
    placeWidget.deleteButton().show()
    #placeWidget.placeMultipleMarkups = slicer.qSlicerMarkupsPlaceWidget.ForcePlaceMultipleMarkups
    placeWidget.placeMultipleMarkups = slicer.qSlicerMarkupsPlaceWidget.ForcePlaceSingleMarkup
    placeWidget.setDeleteAllControlPointsOptionVisible(False)

    # leftSideMandibleGuideBaseCurvePlaceWidget
    placeWidget = self.ui.leftSideMandibleGuideBaseCurvePlaceWidget
    placeWidget.setInteractionNode(slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton"))
    placeWidget.setCurrentNode(self.logic.getLeftSideMandibleGuideBaseCurve())
    placeWidget.buttonsVisible = False
    placeWidget.placeButton().show()
    placeWidget.deleteButton().show()
    #placeWidget.placeMultipleMarkups = slicer.qSlicerMarkupsPlaceWidget.ForcePlaceMultipleMarkups
    placeWidget.placeMultipleMarkups = slicer.qSlicerMarkupsPlaceWidget.ForcePlaceSingleMarkup
    placeWidget.setDeleteAllControlPointsOptionVisible(False)

    # rightSideMandibleGuideBaseCurvePlaceWidget
    placeWidget = self.ui.rightSideMandibleGuideBaseCurvePlaceWidget
    placeWidget.setInteractionNode(slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton"))
    placeWidget.setCurrentNode(self.logic.getRightSideMandibleGuideBaseCurve())
    placeWidget.buttonsVisible = False
    placeWidget.placeButton().show()
    placeWidget.deleteButton().show()
    #placeWidget.placeMultipleMarkups = slicer.qSlicerMarkupsPlaceWidget.ForcePlaceMultipleMarkups
    placeWidget.placeMultipleMarkups = slicer.qSlicerMarkupsPlaceWidget.ForcePlaceSingleMarkup
    placeWidget.setDeleteAllControlPointsOptionVisible(False)

    # Connections

    # These connections ensure that we update parameter node when scene is closed
    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

    slicer.mrmlScene.AddObserver(slicer.mrmlScene.NodeAboutToBeRemovedEvent, self.onNodeAboutToBeRemovedEvent) 
    slicer.mrmlScene.AddObserver(slicer.mrmlScene.NodeRemovedEvent, self.onNodeRemovedEvent)

    # These connections ensure that whenever user changes some settings on the GUI, that is saved in the MRML scene
    # (in the selected parameter node).
    self.ui.headCTSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.legsCTSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.mandibularSegmentSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.mandibularSegmentSelector.connect("currentSegmentChanged(QString)", self.updateParameterNodeFromGUI)
    self.ui.fibulaSegmentSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.fibulaSegmentSelector.connect("currentSegmentChanged(QString)", self.updateParameterNodeFromGUI)
    self.ui.vesselsSegmentSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.vesselsSegmentSelector.connect("currentSegmentChanged(QString)", self.updateParameterNodeFromGUI)
    self.ui.fibulaSurgicalGuideBaseSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.scalarVolumeSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.mandibleSurgicalGuideBaseSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.dentalImplantFiducialListSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    #self.ui.dentalImplantCylinderSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.plateCurveSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)

    self.ui.headCTCorticalBoneThresholdSlider.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.legsCTCorticalBoneThresholdSlider.valueChanged.connect(self.updateParameterNodeFromGUI)

    self.ui.initialSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.betweenSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.securityMarginOfFibulaPiecesSpinBox.valueChanged.connect(self.updateMiterBoxes)
    self.ui.miterBoxSlotWidthSpinBox.valueChanged.connect(self.updateMiterBoxes)
    self.ui.miterBoxSlotLengthSpinBox.valueChanged.connect(self.updateMiterBoxes)
    self.ui.miterBoxSlotHeightSpinBox.valueChanged.connect(self.updateMiterBoxes)
    self.ui.miterBoxSlotWallSpinBox.valueChanged.connect(self.updateMiterBoxes)
    self.ui.fibulaScrewHoleCylinderRadiusSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.clearanceFitPrintingToleranceSpinBox.valueChanged.connect(self.updateMiterBoxes)
    self.ui.biggerMiterBoxDistanceToFibulaSpinBox.valueChanged.connect(self.updateMiterBoxes)
    self.ui.fibulaGuidebaseThicknessSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.fibulaGuidebaseMarginSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.fibulaGuidebaseAngleSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.sawBoxSlotWidthSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.sawBoxSlotLengthSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.sawBoxSlotHeightSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.sawBoxSlotWallSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.biggerSawBoxDistanceToMandibleSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.mandibleScrewHoleCylinderRadiusSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.mandibleBridgeRadiusSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.mandibleGuidebaseThicknessSpinBox.valueChanged.connect(self.updateMandibleGuideBases)
    self.ui.dentalImplantCylinderRadiusSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.dentalImplantCylinderHeightSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.dentalImplantDrillGuideWallSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.plateCrossSectionalWidthSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.plateCrossSectionalLengthSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.plateCrossSectionalBevelRadiusPorcentageSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.plateTipsBevelRadiusSpinBox.valueChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandibleButton.checkBoxToggled.connect(self.updateParameterNodeFromGUI)
    self.ui.updateFibulaDentalImplantCylindersButton.checkBoxToggled.connect(self.updateParameterNodeFromGUI)
    self.ui.donorLegComboBox.currentTextChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.fibulaSegmentsMeasurementModeComboBox.currentTextChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.kindOfMandibleResectionComboBox.currentTextChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.mandibleSideToRemoveComboBox.currentTextChanged.connect(self.updateParameterNodeFromGUI)
    self.ui.miterBoxesGuideTypeComboBox.currentTextChanged.connect(self.updateMiterBoxes)
    self.ui.miterBoxesBoxTypeComboBox.currentTextChanged.connect(self.updateMiterBoxes)
    self.ui.sawBoxesGuideTypeComboBox.currentTextChanged.connect(self.updateParameterNodeFromGUI)

    # Buttons
    self.ui.emailBugReportButton.connect('clicked(bool)',self.onEmailBugReportButton)
    self.ui.emailFeatureRequestButton.connect('clicked(bool)',self.onEmailFeatureRequestButton)
    self.ui.openDocumentationButton.connect('clicked(bool)',self.onOpenDocumentationButton)
    self.ui.loadTestCaseButton.connect('clicked(bool)', self.onLoadTestCaseButton)
    self.ui.installAISegmentationsButton.connect('clicked(bool)', self.onInstallAISegmentationsButton)
    self.ui.runHeadSegmentationButton.connect('clicked(bool)', self.onRunHeadSegmentationButton)
    self.ui.runLegsSegmentationButton.connect('clicked(bool)', self.onRunLegsSegmentationButton)
    self.ui.runHeadAndLegsSegmentationButton.connect('clicked(bool)', self.onRunHeadAndLegsSegmentationButton)
    self.ui.addCutPlaneButton.connect('clicked(bool)',self.onAddCutPlaneButton)
    self.ui.removeCutPlaneButton.connect('clicked(bool)',self.onRemoveCutPlaneButton)
    self.ui.makeModelsButton.connect('clicked(bool)',self.onMakeModelsButton)
    self.ui.generateFibulaGuidebaseButton.connect('clicked(bool)',self.onGenerateFibulaGuidebaseButton)
    self.ui.makeBooleanOperationsToFibulaSurgicalGuideBaseButton.connect('clicked(bool)', self.onMakeBooleanOperationsToFibulaSurgicalGuideBaseButton)
    self.ui.createSawBoxesFromFirstAndLastMandiblePlanesButton.connect('clicked(bool)', self.onCreateSawBoxesFromFirstAndLastMandiblePlanesButton)
    self.ui.makeBooleanOperationsToMandibleSurgicalGuideBaseButton.connect('clicked(bool)', self.onMakeBooleanOperationsToMandibleSurgicalGuideBaseButton)
    self.ui.generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandibleButton.connect('clicked(bool)', self.onGenerateFibulaPlanesFibulaBonePiecesAndTransformThemToMandibleButton)
    self.ui.updateFibulaDentalImplantCylindersButton.connect('clicked(bool)', self.onUpdateFibulaDentalImplantCylindersButton)
    self.ui.create3DModelOfTheReconstructionButton.connect('clicked(bool)', self.onCreate3DModelOfTheReconstructionButton)
    self.ui.createDentalImplantCylindersFiducialListButton.connect('clicked(bool)', self.onCreateDentalImplantCylindersFiducialListButton)
    self.ui.createCylindersFromFiducialListAndNeomandiblePiecesButton.connect('clicked(bool)', self.onCreateCylindersFromFiducialListAndNeomandiblePiecesButton)
    self.ui.createPlateCurveButton.connect('clicked(bool)', self.onCreatePlateCurveButton)
    self.ui.createCustomPlateButton.connect('clicked(bool)', self.onCreateCustomPlateButton)
    self.ui.hardVSPUpdateButton.connect('clicked(bool)', self.onHardVSPUpdateButton)
    self.ui.interCondylarBeamIncreaseSizeButton.connect('clicked(bool)', self.onInterCondylarBeamIncreaseSizeButton)
    self.ui.interCondylarBeamDecreaseSizeButton.connect('clicked(bool)', self.onInterCondylarBeamDecreaseSizeButton)
    self.ui.interCondylarBeamVisibilityToolButton.connect('clicked(bool)', self.updateParameterNodeFromGUI)
    self.ui.lockVSPButton.connect('toggled(bool)', self.onLockVSPButton)
    self.ui.neomandibleVisibilityButton.connect('toggled(bool)', self.onNeomandibleVisibilityButton)
    self.ui.fibulaNormalizationTransformButton.connect('toggled(bool)', self.onFibulaNormalizationTransformButton)
    self.ui.includeVesselsOnPlanCheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)
    self.ui.makeAllMandiblePlanesRotateTogetherCheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)
    self.ui.useMoreExactVersionOfPositioningAlgorithmCheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)
    self.ui.useNonDecimatedModelsForPreviewCheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)
    self.ui.mandiblePlanesPositioningForMaximumBoneContactCheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)
    self.ui.fixCutGoesThroughTheMandibleTwiceCheckBox.connect('stateChanged(int)', self.onFixCutGoesThroughTheMandibleTwiceCheckBox)
    self.ui.checkSecurityMarginOnMiterBoxCreationCheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)
    self.ui.fibulaSurgicalGuideElementsVisibleCheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)
    self.ui.fibulaSurgicalGuideVisibleCheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)
    self.ui.mandibleSurgicalGuideElementsVisibleCheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)
    self.ui.mandibleSurgicalGuideVisibleCheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)
    self.ui.AISegmentationsCheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)
    self.ui.dentalImplantsPlanningAndFibulaDrillGuidesCheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)
    self.ui.customTitaniumPlateDesingCheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)
    self.ui.makeAllDentalImplanCylindersParallelCheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)
    self.ui.showFibulaSegmentsLengthsCheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)
    self.ui.showOriginalMandibleCheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)
    self.ui.showBiggerSawBoxesInteractionHandlesCheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)
    self.ui.useMandibleGuideBasesFromCurvesCheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)
    self.ui.showMandiblePlanesToolButton.connect('clicked(bool)', self.updateParameterNodeFromGUI)
    self.ui.showMandiblePlanesInteractionHandlesToolButton.connect('clicked(bool)', self.updateParameterNodeFromGUI)
    self.ui.inCameraPlaneInteractionHandlesToolButton.connect('clicked(bool)', self.updateParameterNodeFromGUI)
    self.ui.orientation3DCubeCheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)
    self.ui.lightingModeComboBox.textActivated.connect(self.updateParameterNodeFromGUI)
    self.ui.lightingInterpolationMethodComboBox.textActivated.connect(self.updateParameterNodeFromGUI)
    self.ui.restoreDefaultSettingsButton.connect('clicked(bool)', self.onRestoreDefaultSettingsButton)
    self.ui.overwriteDefaultSettingsButton.connect('clicked(bool)', self.onOverwriteDefaultSettingsButton)

    # Make sure parameter node is initialized (needed for module reload)
    self.initializeParameterNode()

  def onLoadTestCaseButton(self):
    """
    Load BoneReconstructionPlanner test data using SampleData module
    """
    self._parameterNode.SetParameter("currentlyProcessing", str(True))
    confirm_clean_and_load_test_data()
    self._parameterNode.SetParameter("currentlyProcessing", str(False))

  def onInstallAISegmentationsButton(self):
    """
    Install Head and Legs segmentation
    """
    self.logic.installAISegmentations()

  def onRunHeadSegmentationButton(self):
    """
    Run head segmentation
    """
    self.logic.runHeadSegmentation()

  def onRunLegsSegmentationButton(self):
    """
    Run legs segmentation
    """
    self.logic.runLegsSegmentation()

  def onRunHeadAndLegsSegmentationButton(self):
    """
    Run head and legs segmentations
    """
    self.logic.runHeadSegmentation()
    self.logic.runLegsSegmentation()

  def updateMiterBoxes(self, caller=None, event=None):
    """
    Update miterBoxes parameters and start update timer countdown
    """
    self.updateParameterNodeFromGUI(caller=None, event=None)
    self.logic.createMiterBoxesFromFibulaPlanes()

  def updateMandibleGuideBases(self, caller=None, event=None):
    """
    Update mandible guide bases parameters and start update timer countdown
    """
    self.updateParameterNodeFromGUI(caller=None, event=None)
    self.logic.onLeftSideMandibleGuideBaseCurvePointUpdated()
    self.logic.onRightSideMandibleGuideBaseCurvePointUpdated()
  
  def cleanup(self):
    """
    Called when the application closes and the module widget is destroyed.
    """
    self.removeObservers()

  @vtk.calldata_type(vtk.VTK_OBJECT)
  def onNodeAboutToBeRemovedEvent(self, caller, event, callData):
    """
    Processing to do before a node is removed from the scene
    """
    if callData.GetClassName() == 'vtkMRMLMarkupsPlaneNode':
      if callData.GetAttribute("isMandibularPlane") == 'True':
        if len(self.logic.mandiblePlaneObserversAndNodeIDList) > 0:
          for i in range(len(self.logic.mandiblePlaneObserversAndNodeIDList)):
            if self.logic.mandiblePlaneObserversAndNodeIDList[i][1] == callData.GetID():
              observerIndex = i
          callData.RemoveObserver(self.logic.mandiblePlaneObserversAndNodeIDList.pop(observerIndex)[0])
        self.logic.onPlaneModifiedSetTimer(None,None)
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
    
    if callData.GetClassName() == 'vtkMRMLMarkupsLineNode':
      if callData.GetAttribute("isFibulaLine") == 'True':
        callData.RemoveObserver(self.logic.fibulaLineControlPointDefinedObserver)
        callData.RemoveObserver(self.logic.fibulaLineControlPointEndInteractionObserver)
        callData.RemoveObserver(self.logic.fibulaLineControlPointRemovedObserver)
        self.logic.fibulaLineControlPointDefinedObserver = 0
        self.logic.fibulaLineControlPointEndInteractionObserver = 0
        self.logic.fibulaLineControlPointRemovedObserver = 0
        for observer in self.logic.fibulaLineInstructionsEventsObserversList:
          callData.RemoveObserver(observer)
        self.logic.fibulaLineInstructionsEventsObserversList = []
      if callData.GetAttribute("isInterCondylarBeamLine") == 'True':
        callData.RemoveObserver(self.logic.interCondylarBeamLineControlPointDefinedObserver)
        callData.RemoveObserver(self.logic.interCondylarBeamLineControlPointEndInteractionObserver)
        callData.RemoveObserver(self.logic.interCondylarBeamLineControlPointRemovedObserver)
        self.logic.interCondylarBeamLineControlPointDefinedObserver = 0
        self.logic.interCondylarBeamLineControlPointEndInteractionObserver = 0
        self.logic.interCondylarBeamLineControlPointRemovedObserver = 0
      if callData.GetAttribute("isMiterBoxDirectionLine") == 'True':
        callData.RemoveObserver(self.logic.miterBoxDirectionLineControlPointDefinedObserver)
        callData.RemoveObserver(self.logic.miterBoxDirectionLineControlPointEndInteractionObserver)
        callData.RemoveObserver(self.logic.miterBoxDirectionLineControlPointRemovedObserver)
        self.logic.miterBoxDirectionLineControlPointDefinedObserver = 0
        self.logic.miterBoxDirectionLineControlPointEndInteractionObserver = 0
        self.logic.miterBoxDirectionLineControlPointRemovedObserver = 0
    
    if callData.GetClassName() == 'vtkMRMLMarkupsFiducialNode':
      if callData.GetAttribute("isFibulaFiducials") == 'True':
        callData.RemoveObserver(self.logic.fibulaFiducialListControlPointDefinedObserver)
        callData.RemoveObserver(self.logic.fibulaFiducialListControlPointEndInteractionObserver)
        callData.RemoveObserver(self.logic.fibulaFiducialListControlPointRemovedObserver)
        self.logic.fibulaFiducialListControlPointDefinedObserver = 0
        self.logic.fibulaFiducialListControlPointEndInteractionObserver = 0
        self.logic.fibulaFiducialListControlPointRemovedObserver = 0
      if callData.GetAttribute("isMandibleFiducials") == 'True':
        callData.RemoveObserver(self.logic.mandibleFiducialListControlPointDefinedObserver)
        callData.RemoveObserver(self.logic.mandibleFiducialListControlPointEndInteractionObserver)
        callData.RemoveObserver(self.logic.mandibleFiducialListControlPointRemovedObserver)
        self.logic.mandibleFiducialListControlPointDefinedObserver = 0
        self.logic.mandibleFiducialListControlPointEndInteractionObserver = 0
        self.logic.mandibleFiducialListControlPointRemovedObserver = 0

    if callData.GetClassName() == 'vtkMRMLMarkupsCurveNode':
      if callData.GetAttribute("isMandibleCurve") == 'True':
        for observer in self.logic.mandibularCurveInstructionsEventsObserversList:
          callData.RemoveObserver(observer)
        self.logic.mandibularCurveInstructionsEventsObserversList = []
      if callData.GetAttribute("isMandibleBridgeCurve") == 'True':
        callData.RemoveObserver(self.logic.mandibleBridgeCurveControlPointDefinedObserver)
        callData.RemoveObserver(self.logic.mandibleBridgeCurveControlPointEndInteractionObserver)
        callData.RemoveObserver(self.logic.mandibleBridgeCurveControlPointRemovedObserver)
        self.logic.mandibleBridgeCurveControlPointDefinedObserver = 0
        self.logic.mandibleBridgeCurveControlPointEndInteractionObserver = 0
        self.logic.mandibleBridgeCurveControlPointRemovedObserver = 0
    
    if callData.GetClassName() == 'vtkMRMLMarkupsClosedCurveNode':
      if callData.GetAttribute("isLeftSideMandibleGuideBaseCurve") == 'True':
        callData.RemoveObserver(self.logic.leftSideMandibleGuideBaseCurveControlPointDefinedObserver)
        callData.RemoveObserver(self.logic.leftSideMandibleGuideBaseCurveControlPointEndInteractionObserver)
        callData.RemoveObserver(self.logic.leftSideMandibleGuideBaseCurveControlPointRemovedObserver)
        self.logic.leftSideMandibleGuideBaseCurveControlPointDefinedObserver = 0
        self.logic.leftSideMandibleGuideBaseCurveControlPointEndInteractionObserver = 0
        self.logic.leftSideMandibleGuideBaseCurveControlPointRemovedObserver = 0
      if callData.GetAttribute("isRightSideMandibleGuideBaseCurve") == 'True':
        callData.RemoveObserver(self.logic.rightSideMandibleGuideBaseCurveControlPointDefinedObserver)
        callData.RemoveObserver(self.logic.rightSideMandibleGuideBaseCurveControlPointEndInteractionObserver)
        callData.RemoveObserver(self.logic.rightSideMandibleGuideBaseCurveControlPointRemovedObserver)
        self.logic.rightSideMandibleGuideBaseCurveControlPointDefinedObserver = 0
        self.logic.rightSideMandibleGuideBaseCurveControlPointEndInteractionObserver = 0
        self.logic.rightSideMandibleGuideBaseCurveControlPointRemovedObserver = 0

  @vtk.calldata_type(vtk.VTK_OBJECT)
  def onNodeRemovedEvent(self, caller, event, callData):
    """
    Processing to do after a node is removed from the scene
    """
    if self._parameterNode is None:
      return

    if callData.GetClassName() == 'vtkMRMLMarkupsCurveNode' and callData.GetAttribute("isMandibleCurve") == 'True':
      #print(callData.GetName())
      placeWidget = self.ui.mandibleCurvePlaceWidget
      placeWidget.setCurrentNode(self.logic.getMandibularCurve())
    if callData.GetClassName() == 'vtkMRMLMarkupsLineNode' and callData.GetAttribute("isFibulaLine") == 'True':
      #print(callData.GetName())
      placeWidget = self.ui.fibulaLinePlaceWidget
      placeWidget.setCurrentNode(self.logic.getFibulaLine())
    if callData.GetClassName() == 'vtkMRMLMarkupsLineNode' and callData.GetAttribute("isInterCondylarBeamLine") == 'True':
      #print(callData.GetName())
      placeWidget = self.ui.interCondylarBeamLinePlaceWidget
      placeWidget.setCurrentNode(self.logic.getInterCondylarBeamLine())
    if callData.GetClassName() == 'vtkMRMLMarkupsLineNode' and callData.GetAttribute("isMiterBoxDirectionLine") == 'True':
      #print(callData.GetName())
      placeWidget = self.ui.miterBoxDirectionLinePlaceWidget
      placeWidget.setCurrentNode(self.logic.getMiterBoxDirectionLine())
    if callData.GetClassName() == 'vtkMRMLMarkupsFiducialNode' and callData.GetAttribute("isFibulaFiducials") == 'True':
      #print(callData.GetName())
      placeWidget = self.ui.fibulaFiducialsPlaceWidget
      placeWidget.setCurrentNode(self.logic.getFibulaFiducials())
    if callData.GetClassName() == 'vtkMRMLMarkupsFiducialNode' and callData.GetAttribute("isMandibleFiducials") == 'True':
      #print(callData.GetName())
      placeWidget = self.ui.mandibleFiducialsPlaceWidget
      placeWidget.setCurrentNode(self.logic.getMandibleFiducials())
    if callData.GetClassName() == 'vtkMRMLMarkupsCurveNode' and callData.GetAttribute("isMandibleBridgeCurve") == 'True':
      #print(callData.GetName())
      placeWidget = self.ui.mandibleBridgeCurvePlaceWidget
      placeWidget.setCurrentNode(self.logic.getMandibleBridgeCurve())
    if callData.GetClassName() == 'vtkMRMLMarkupsClosedCurveNode' and callData.GetAttribute("isLeftSideMandibleGuideBaseCurve") == 'True':
      #print(callData.GetName())
      # The curve node was deleted as a whole, so drop its guide base model and refresh the combined model
      leftSideMandibleGuideBaseModel = self._parameterNode.GetNodeReference("leftSideMandibleGuideBaseModel")
      if leftSideMandibleGuideBaseModel is not None:
        self._parameterNode.SetNodeReferenceID("leftSideMandibleGuideBaseModel", "")
        slicer.mrmlScene.RemoveNode(leftSideMandibleGuideBaseModel)
        self.logic.updateBothMandibleGuideBaseModels()
      placeWidget = self.ui.leftSideMandibleGuideBaseCurvePlaceWidget
      placeWidget.setCurrentNode(self.logic.getLeftSideMandibleGuideBaseCurve())
    if callData.GetClassName() == 'vtkMRMLMarkupsClosedCurveNode' and callData.GetAttribute("isRightSideMandibleGuideBaseCurve") == 'True':
      #print(callData.GetName())
      # The curve node was deleted as a whole, so drop its guide base model and refresh the combined model
      rightSideMandibleGuideBaseModel = self._parameterNode.GetNodeReference("rightSideMandibleGuideBaseModel")
      if rightSideMandibleGuideBaseModel is not None:
        self._parameterNode.SetNodeReferenceID("rightSideMandibleGuideBaseModel", "")
        slicer.mrmlScene.RemoveNode(rightSideMandibleGuideBaseModel)
        self.logic.updateBothMandibleGuideBaseModels()
      placeWidget = self.ui.rightSideMandibleGuideBaseCurvePlaceWidget
      placeWidget.setCurrentNode(self.logic.getRightSideMandibleGuideBaseCurve())

  def enter(self):
    """
    Called each time the user opens this module.
    """
    # Make sure parameter node exists and observed
    self.initializeParameterNode()

    # Backward compatibility: older scenes used "Plane Cuts" for what is now "Bone Plane Cuts"
    renameFolderByName("Plane Cuts", "Bone Plane Cuts")

    mandibularPlanesList = createListFromFolderName("Mandibular planes")
    sawBoxesPlanesList = createListFromFolderName("sawBoxes Planes")
    dentalImplantsPlanesList = createListFromFolderName("dentalImplants Planes")

    #self.setMandiblePlanesInteractionHandlesVisibility(visibility=True)
    if self._parameterNode.GetParameter("lockVSP") == "False":
      self._parameterNode.SetParameter("showMandiblePlanesInteractionHandles","True")
    self.logic.setMarkupsListLocked(mandibularPlanesList,locked=False)
    self.logic.addMandiblePlaneObservers()

    # make it not visible to not clutter the mandible 3D view
    #self.setBiggerSawBoxesInteractionHandlesVisibility(visibility=False)
    self._parameterNode.SetParameter("showBiggerSawBoxesInteractionHandles","False")
    self.logic.setMarkupsListLocked(sawBoxesPlanesList,locked=False)
    self.logic.addSawBoxPlaneObservers()

    self.logic.setInteractiveHandlesVisibilityOfMarkups(
      dentalImplantsPlanesList,
      visibility=True
    )
    self.logic.setMarkupsListLocked(dentalImplantsPlanesList,locked=False)
    self.logic.addDentalImplantsPlaneObservers()

    self.setMarkupControlPointsVisibility(self.logic.getMandibularCurve(), visibility=True)
    self.setMarkupControlPointsVisibility(self.logic.getInterCondylarBeamLine(), visibility=True)
    self.setMarkupControlPointsVisibility(self.logic.getFibulaLine(), visibility=True)
    self.setMarkupControlPointsVisibility(self.logic.getFibulaFiducials(), visibility=True)
    self.setMarkupControlPointsVisibility(self.logic.getMandibleFiducials(), visibility=True)
    self.setMarkupControlPointsVisibility(self.logic.getMandibleBridgeCurve(), visibility=True)
    self.setMarkupControlPointsVisibility(self.logic.getLeftSideMandibleGuideBaseCurve(), visibility=True)
    self.setMarkupControlPointsVisibility(self.logic.getRightSideMandibleGuideBaseCurve(), visibility=True)

    markupsList = [
      self.logic.getMandibularCurve(),
      self.logic.getInterCondylarBeamLine(),
      self.logic.getFibulaLine(),
      self.logic.getFibulaFiducials(),
      self.logic.getMandibleFiducials(),
      self.logic.getMandibleBridgeCurve(),
      self.logic.getLeftSideMandibleGuideBaseCurve(),
      self.logic.getRightSideMandibleGuideBaseCurve()
    ]
    self.logic.setMarkupsListLocked(markupsList,locked=False)
    
    if self.logic.interCondylarBeamLineControlPointDefinedObserver == 0:
      observerTag = self.logic.getInterCondylarBeamLine().AddObserver(
        slicer.vtkMRMLMarkupsNode.PointPositionDefinedEvent,
        self.logic.onInterCondylarLinePointUpdated
      )
      self.logic.interCondylarBeamLineControlPointDefinedObserver = observerTag
    
    if self.logic.interCondylarBeamLineControlPointEndInteractionObserver == 0:
      observerTag = self.logic.getInterCondylarBeamLine().AddObserver(
        slicer.vtkMRMLMarkupsNode.PointEndInteractionEvent,
        self.logic.onInterCondylarLinePointUpdated
      )
      self.logic.interCondylarBeamLineControlPointEndInteractionObserver = observerTag  
    
    if self.logic.interCondylarBeamLineControlPointRemovedObserver == 0:
      observerTag = self.logic.getInterCondylarBeamLine().AddObserver(
        slicer.vtkMRMLMarkupsNode.PointRemovedEvent,
        self.logic.onInterCondylarLinePointUpdated
      )
      self.logic.interCondylarBeamLineControlPointRemovedObserver = observerTag  

    if self.logic.fibulaLineControlPointDefinedObserver == 0:
      observerTag = self.logic.getFibulaLine().AddObserver(
        slicer.vtkMRMLMarkupsNode.PointPositionDefinedEvent,
        self.logic.onFibulaLinePointUpdated
      )
      self.logic.fibulaLineControlPointDefinedObserver = observerTag
    
    if self.logic.fibulaLineControlPointEndInteractionObserver == 0:
      observerTag = self.logic.getFibulaLine().AddObserver(
        slicer.vtkMRMLMarkupsNode.PointEndInteractionEvent,
        self.logic.onFibulaLinePointUpdated
      )
      self.logic.fibulaLineControlPointEndInteractionObserver = observerTag
    
    if self.logic.fibulaLineControlPointRemovedObserver == 0:
      observerTag = self.logic.getFibulaLine().AddObserver(
        slicer.vtkMRMLMarkupsNode.PointRemovedEvent,
        self.logic.onFibulaLinePointUpdated
      )
      self.logic.fibulaLineControlPointRemovedObserver = observerTag

    if self.logic.fibulaFiducialListControlPointDefinedObserver == 0:
      observerTag = self.logic.getFibulaFiducials().AddObserver(
        slicer.vtkMRMLMarkupsNode.PointPositionDefinedEvent,
        self.logic.onFibulaFiducialsPointModified
      )
      self.logic.fibulaFiducialListControlPointDefinedObserver = observerTag
    
    if self.logic.fibulaFiducialListControlPointEndInteractionObserver == 0:
      observerTag = self.logic.getFibulaFiducials().AddObserver(
        slicer.vtkMRMLMarkupsNode.PointEndInteractionEvent,
        self.logic.onFibulaFiducialsPointModified
      )
      self.logic.fibulaFiducialListControlPointEndInteractionObserver = observerTag  
    
    if self.logic.fibulaFiducialListControlPointRemovedObserver == 0:
      observerTag = self.logic.getFibulaFiducials().AddObserver(
        slicer.vtkMRMLMarkupsNode.PointRemovedEvent,
        self.logic.onFibulaFiducialsPointModified
      )
      self.logic.fibulaFiducialListControlPointRemovedObserver = observerTag  

    if self.logic.mandibleFiducialListControlPointDefinedObserver == 0:
      observerTag = self.logic.getMandibleFiducials().AddObserver(
        slicer.vtkMRMLMarkupsNode.PointPositionDefinedEvent,
        self.logic.onMandibleFiducialsPointModified
      )
      self.logic.mandibleFiducialListControlPointDefinedObserver = observerTag
    
    if self.logic.mandibleFiducialListControlPointEndInteractionObserver == 0:
      observerTag = self.logic.getMandibleFiducials().AddObserver(
        slicer.vtkMRMLMarkupsNode.PointEndInteractionEvent,
        self.logic.onMandibleFiducialsPointModified
      )
      self.logic.mandibleFiducialListControlPointEndInteractionObserver = observerTag  
    
    if self.logic.mandibleFiducialListControlPointRemovedObserver == 0:
      observerTag = self.logic.getMandibleFiducials().AddObserver(
        slicer.vtkMRMLMarkupsNode.PointRemovedEvent,
        self.logic.onMandibleFiducialsPointModified
      )
      self.logic.mandibleFiducialListControlPointRemovedObserver = observerTag  

    if self.logic.mandibleBridgeCurveControlPointDefinedObserver == 0:
      observerTag = self.logic.getMandibleBridgeCurve().AddObserver(
        slicer.vtkMRMLMarkupsNode.PointPositionDefinedEvent,
        self.logic.onMandibleBridgeCurvePointUpdated
      )
      self.logic.mandibleBridgeCurveControlPointDefinedObserver = observerTag

    if self.logic.mandibleBridgeCurveControlPointEndInteractionObserver == 0:
      observerTag = self.logic.getMandibleBridgeCurve().AddObserver(
        slicer.vtkMRMLMarkupsNode.PointEndInteractionEvent,
        self.logic.onMandibleBridgeCurvePointUpdated
      )
      self.logic.mandibleBridgeCurveControlPointEndInteractionObserver = observerTag

    if self.logic.mandibleBridgeCurveControlPointRemovedObserver == 0:
      observerTag = self.logic.getMandibleBridgeCurve().AddObserver(
        slicer.vtkMRMLMarkupsNode.PointRemovedEvent,
        self.logic.onMandibleBridgeCurvePointUpdated
      )
      self.logic.mandibleBridgeCurveControlPointRemovedObserver = observerTag

    if self.logic.miterBoxDirectionLineControlPointDefinedObserver == 0:
      observerTag = self.logic.getMiterBoxDirectionLine().AddObserver(
        slicer.vtkMRMLMarkupsNode.PointPositionDefinedEvent,
        self.logic.onMiterBoxDirectionLinePointUpdated
      )
      self.logic.miterBoxDirectionLineControlPointDefinedObserver = observerTag

    if self.logic.miterBoxDirectionLineControlPointEndInteractionObserver == 0:
      observerTag = self.logic.getMiterBoxDirectionLine().AddObserver(
        slicer.vtkMRMLMarkupsNode.PointEndInteractionEvent,
        self.logic.onMiterBoxDirectionLinePointUpdated
      )
      self.logic.miterBoxDirectionLineControlPointEndInteractionObserver = observerTag

    if self.logic.miterBoxDirectionLineControlPointRemovedObserver == 0:
      observerTag = self.logic.getMiterBoxDirectionLine().AddObserver(
        slicer.vtkMRMLMarkupsNode.PointRemovedEvent,
        self.logic.onMiterBoxDirectionLinePointUpdated
      )
      self.logic.miterBoxDirectionLineControlPointRemovedObserver = observerTag

    if self.logic.leftSideMandibleGuideBaseCurveControlPointDefinedObserver == 0:
      observerTag = self.logic.getLeftSideMandibleGuideBaseCurve().AddObserver(
        slicer.vtkMRMLMarkupsNode.PointPositionDefinedEvent,
        self.logic.onLeftSideMandibleGuideBaseCurvePointUpdated
      )
      self.logic.leftSideMandibleGuideBaseCurveControlPointDefinedObserver = observerTag

    if self.logic.leftSideMandibleGuideBaseCurveControlPointEndInteractionObserver == 0:
      observerTag = self.logic.getLeftSideMandibleGuideBaseCurve().AddObserver(
        slicer.vtkMRMLMarkupsNode.PointEndInteractionEvent,
        self.logic.onLeftSideMandibleGuideBaseCurvePointUpdated
      )
      self.logic.leftSideMandibleGuideBaseCurveControlPointEndInteractionObserver = observerTag

    if self.logic.leftSideMandibleGuideBaseCurveControlPointRemovedObserver == 0:
      observerTag = self.logic.getLeftSideMandibleGuideBaseCurve().AddObserver(
        slicer.vtkMRMLMarkupsNode.PointRemovedEvent,
        self.logic.onLeftSideMandibleGuideBaseCurvePointUpdated
      )
      self.logic.leftSideMandibleGuideBaseCurveControlPointRemovedObserver = observerTag

    if self.logic.rightSideMandibleGuideBaseCurveControlPointDefinedObserver == 0:
      observerTag = self.logic.getRightSideMandibleGuideBaseCurve().AddObserver(
        slicer.vtkMRMLMarkupsNode.PointPositionDefinedEvent,
        self.logic.onRightSideMandibleGuideBaseCurvePointUpdated
      )
      self.logic.rightSideMandibleGuideBaseCurveControlPointDefinedObserver = observerTag

    if self.logic.rightSideMandibleGuideBaseCurveControlPointEndInteractionObserver == 0:
      observerTag = self.logic.getRightSideMandibleGuideBaseCurve().AddObserver(
        slicer.vtkMRMLMarkupsNode.PointEndInteractionEvent,
        self.logic.onRightSideMandibleGuideBaseCurvePointUpdated
      )
      self.logic.rightSideMandibleGuideBaseCurveControlPointEndInteractionObserver = observerTag

    if self.logic.rightSideMandibleGuideBaseCurveControlPointRemovedObserver == 0:
      observerTag = self.logic.getRightSideMandibleGuideBaseCurve().AddObserver(
        slicer.vtkMRMLMarkupsNode.PointRemovedEvent,
        self.logic.onRightSideMandibleGuideBaseCurvePointUpdated
      )
      self.logic.rightSideMandibleGuideBaseCurveControlPointRemovedObserver = observerTag
    
    if (self.ui.scalarVolumeSelector.nodeCount() != 0) and (self.ui.scalarVolumeSelector.currentNode() == None):
      self.ui.scalarVolumeSelector.setCurrentNodeIndex(0)#0 == first scalarVolume

  def exit(self):
    """
    Called each time the user opens a different module.
    """
    # Do not react to parameter node changes (GUI wlil be updated when the user enters into the module)
    self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

    mandibularPlanesList = createListFromFolderName("Mandibular planes")
    sawBoxesPlanesList = createListFromFolderName("sawBoxes Planes")
    dentalImplantsPlanesList = createListFromFolderName("dentalImplants Planes")

    #self.logic.setInteractiveHandlesVisibilityOfMarkups(
    #  mandibularPlanesList,
    #  visibility=False
    #)
    if self._parameterNode.GetParameter("lockVSP") == "False":
      self._parameterNode.SetParameter("showMandiblePlanesInteractionHandles","False")
      self.updateGUIFromParameterNode() # needed because parameterNode observer was removed
    self.logic.setMarkupsListLocked(mandibularPlanesList,locked=True)
    self.logic.removeMandiblePlaneObservers()

    #self.logic.setInteractiveHandlesVisibilityOfMarkups(
    #  sawBoxesPlanesList,
    #  visibility=False
    #)
    self._parameterNode.SetParameter("showBiggerSawBoxesInteractionHandles","False")
    self.updateGUIFromParameterNode() # needed because parameterNode observer was removed
    self.logic.setMarkupsListLocked(sawBoxesPlanesList,locked=True)
    self.logic.removeSawBoxPlaneObservers()

    self.logic.setInteractiveHandlesVisibilityOfMarkups(
      dentalImplantsPlanesList,
      visibility=False
    )
    self.logic.setMarkupsListLocked(dentalImplantsPlanesList,locked=True)
    self.logic.removeDentalImplantsPlaneObservers()

    self.setMarkupControlPointsVisibility(self.logic.getMandibularCurve(), visibility=False)
    self.setMarkupControlPointsVisibility(self.logic.getInterCondylarBeamLine(), visibility=False)
    self.setMarkupControlPointsVisibility(self.logic.getFibulaLine(), visibility=False)
    self.setMarkupControlPointsVisibility(self.logic.getFibulaFiducials(), visibility=False)
    self.setMarkupControlPointsVisibility(self.logic.getMandibleFiducials(), visibility=False)
    self.setMarkupControlPointsVisibility(self.logic.getMandibleBridgeCurve(), visibility=False)
    self.setMarkupControlPointsVisibility(self.logic.getRightSideMandibleGuideBaseCurve(), visibility=False)
    self.setMarkupControlPointsVisibility(self.logic.getRightSideMandibleGuideBaseCurve(), visibility=False)

    markupsList = [
      self.logic.getMandibularCurve(),
      self.logic.getInterCondylarBeamLine(),
      self.logic.getFibulaLine(),
      self.logic.getFibulaFiducials(),
      self.logic.getMandibleFiducials(),
      self.logic.getMandibleBridgeCurve(),
      self.logic.getLeftSideMandibleGuideBaseCurve(),
      self.logic.getRightSideMandibleGuideBaseCurve()
    ]
    self.logic.setMarkupsListLocked(markupsList,locked=True)

    self.logic.getInterCondylarBeamLine().RemoveObserver(self.logic.interCondylarBeamLineControlPointDefinedObserver)
    self.logic.interCondylarBeamLineControlPointDefinedObserver = 0

    self.logic.getInterCondylarBeamLine().RemoveObserver(self.logic.interCondylarBeamLineControlPointEndInteractionObserver)
    self.logic.interCondylarBeamLineControlPointEndInteractionObserver = 0

    self.logic.getInterCondylarBeamLine().RemoveObserver(self.logic.interCondylarBeamLineControlPointRemovedObserver)
    self.logic.interCondylarBeamLineControlPointRemovedObserver = 0

    self.logic.getFibulaFiducials().RemoveObserver(self.logic.fibulaFiducialListControlPointDefinedObserver)
    self.logic.fibulaFiducialListControlPointDefinedObserver = 0

    self.logic.getFibulaFiducials().RemoveObserver(self.logic.fibulaFiducialListControlPointEndInteractionObserver)
    self.logic.fibulaFiducialListControlPointEndInteractionObserver = 0

    self.logic.getFibulaFiducials().RemoveObserver(self.logic.fibulaFiducialListControlPointRemovedObserver)
    self.logic.fibulaFiducialListControlPointRemovedObserver = 0

    self.logic.getMandibleFiducials().RemoveObserver(self.logic.mandibleFiducialListControlPointDefinedObserver)
    self.logic.mandibleFiducialListControlPointDefinedObserver = 0

    self.logic.getMandibleFiducials().RemoveObserver(self.logic.mandibleFiducialListControlPointEndInteractionObserver)
    self.logic.mandibleFiducialListControlPointEndInteractionObserver = 0

    self.logic.getMandibleFiducials().RemoveObserver(self.logic.mandibleFiducialListControlPointRemovedObserver)
    self.logic.mandibleFiducialListControlPointRemovedObserver = 0

    self.logic.getFibulaLine().RemoveObserver(self.logic.fibulaLineControlPointDefinedObserver)
    self.logic.fibulaLineControlPointDefinedObserver = 0

    self.logic.getFibulaLine().RemoveObserver(self.logic.fibulaLineControlPointEndInteractionObserver)
    self.logic.fibulaLineControlPointEndInteractionObserver = 0

    self.logic.getFibulaLine().RemoveObserver(self.logic.fibulaLineControlPointRemovedObserver)
    self.logic.fibulaLineControlPointRemovedObserver = 0

    self.logic.getMandibleBridgeCurve().RemoveObserver(self.logic.mandibleBridgeCurveControlPointDefinedObserver)
    self.logic.mandibleBridgeCurveControlPointDefinedObserver = 0

    self.logic.getMandibleBridgeCurve().RemoveObserver(self.logic.mandibleBridgeCurveControlPointEndInteractionObserver)
    self.logic.mandibleBridgeCurveControlPointEndInteractionObserver = 0

    self.logic.getMandibleBridgeCurve().RemoveObserver(self.logic.mandibleBridgeCurveControlPointRemovedObserver)
    self.logic.mandibleBridgeCurveControlPointRemovedObserver = 0

    self.logic.getMiterBoxDirectionLine().RemoveObserver(self.logic.miterBoxDirectionLineControlPointDefinedObserver)
    self.logic.miterBoxDirectionLineControlPointDefinedObserver = 0

    self.logic.getMiterBoxDirectionLine().RemoveObserver(self.logic.miterBoxDirectionLineControlPointEndInteractionObserver)
    self.logic.miterBoxDirectionLineControlPointEndInteractionObserver = 0

    self.logic.getMiterBoxDirectionLine().RemoveObserver(self.logic.miterBoxDirectionLineControlPointRemovedObserver)
    self.logic.miterBoxDirectionLineControlPointRemovedObserver = 0

    self.logic.getLeftSideMandibleGuideBaseCurve().RemoveObserver(self.logic.leftSideMandibleGuideBaseCurveControlPointDefinedObserver)
    self.logic.leftSideMandibleGuideBaseCurveControlPointDefinedObserver = 0

    self.logic.getLeftSideMandibleGuideBaseCurve().RemoveObserver(self.logic.leftSideMandibleGuideBaseCurveControlPointEndInteractionObserver)
    self.logic.leftSideMandibleGuideBaseCurveControlPointEndInteractionObserver = 0

    self.logic.getLeftSideMandibleGuideBaseCurve().RemoveObserver(self.logic.leftSideMandibleGuideBaseCurveControlPointRemovedObserver)
    self.logic.leftSideMandibleGuideBaseCurveControlPointRemovedObserver = 0

    self.logic.getRightSideMandibleGuideBaseCurve().RemoveObserver(self.logic.rightSideMandibleGuideBaseCurveControlPointDefinedObserver)
    self.logic.rightSideMandibleGuideBaseCurveControlPointDefinedObserver = 0

    self.logic.getRightSideMandibleGuideBaseCurve().RemoveObserver(self.logic.rightSideMandibleGuideBaseCurveControlPointEndInteractionObserver)
    self.logic.rightSideMandibleGuideBaseCurveControlPointEndInteractionObserver = 0

    self.logic.getRightSideMandibleGuideBaseCurve().RemoveObserver(self.logic.rightSideMandibleGuideBaseCurveControlPointRemovedObserver)
    self.logic.rightSideMandibleGuideBaseCurveControlPointRemovedObserver = 0

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
    #self.setShNode(slicer.mrmlScene.GetSubjectHierarchyNode())

  def setShNode(self, inputShNode):
    """
    Set and observe subject hierarchy node.
    Observation is needed because when the subject hierarchy node is changed then the GUI must be updated immediately.
    """
    
    # Unobserve previously selected subject hierarchy node and add an observer to the newly selected.
    # Changes of subject hierarchy node are observed so that whenever it is changed by a script or any other module
    # those are reflected immediately in the GUI.
    if self._shNode is not None:
      self.removeObserver(self._shNode, slicer.vtkMRMLSubjectHierarchyNode.SubjectHierarchyItemModifiedEvent, self.logic.onShNodeModified)
    self._shNode = inputShNode
    if self._shNode is not None:
      self.addObserver(self._shNode, slicer.vtkMRMLSubjectHierarchyNode.SubjectHierarchyItemModifiedEvent, self.logic.onShNodeModified)

    self.logic.onShNodeModified(caller = self._shNode, event = None, callData = 0)
  
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

    if self._parameterNode is None:
      return
    
    # only put here code that updates the GUI but does not cause any changes in the parameterNode,
    # in other words, only widgets that do not have any connections, otherwise put them below
    # the _updatingGUIFromParameterNode flag

    if self._updatingGUIFromParameterNode:
      return

    # Make sure GUI changes do not call updateParameterNodeFromGUI (it could cause infinite loop)
    self._updatingGUIFromParameterNode = True

    # The line below is for selector updates
    currentScalarVolume = self._parameterNode.GetNodeReference("currentScalarVolume")
    self.ui.scalarVolumeSelector.setCurrentNode(currentScalarVolume)
    if currentScalarVolume is not None:
      scalarVolumeID = currentScalarVolume.GetID()
      if USING_GUI:
        if scalarVolumeID:
          self.logic.setBackgroundVolumeFromID(scalarVolumeID)
          self.logic.setRedSliceForModelsDisplayNodes()
          self.logic.setRedSliceForMarkupsDisplayNodes()

    self.ui.installAISegmentationsButton.enabled = self._parameterNode.GetParameter("AISegmentationsInstalled") == "False"
    self.ui.runAISegmentationsFrame.enabled = self._parameterNode.GetParameter("AISegmentationsInstalled") == "True"
    self.ui.runHeadSegmentationButton.enabled = self._parameterNode.GetNodeReference("headCT") is not None
    self.ui.runLegsSegmentationButton.enabled = self._parameterNode.GetNodeReference("legsCT") is not None
    self.ui.runHeadAndLegsSegmentationButton.enabled = (
      (self._parameterNode.GetNodeReference("headCT") is not None) and 
      (self._parameterNode.GetNodeReference("legsCT") is not None)
    )
    #if self._parameterNode.GetNodeReference("headCT") is not None:
    #scalarRange = self._parameterNode.GetNodeReference("headCT").GetImageData().GetScalarRange()
    #self.ui.headCTCorticalBoneThresholdSlider.maximum = scalarRange[1]
    self.ui.headCTCorticalBoneThresholdSlider.enabled = self._parameterNode.GetNodeReference("headCT") is not None
    self.ui.legsCTCorticalBoneThresholdSlider.enabled = self._parameterNode.GetNodeReference("legsCT") is not None
    self.ui.headCTCorticalBoneThresholdSlider.value = float(self._parameterNode.GetParameter("headCTCorticalBoneThreshold"))
    self.ui.legsCTCorticalBoneThresholdSlider.value = float(self._parameterNode.GetParameter("legsCTCorticalBoneThreshold"))

    # Update node selectors
    self.ui.headCTSelector.setCurrentNode(self._parameterNode.GetNodeReference("headCT"))
    self.ui.legsCTSelector.setCurrentNode(self._parameterNode.GetNodeReference("legsCT"))
    self.ui.mandibularSegmentSelector.setCurrentNode(self._parameterNode.GetNodeReference("mandibularSegmentation"))
    self.ui.mandibularSegmentSelector.setCurrentSegmentID(self._parameterNode.GetParameter("mandibularSegment"))
    self.ui.fibulaSegmentSelector.setCurrentNode(self._parameterNode.GetNodeReference("fibulaSegmentation"))
    self.ui.fibulaSegmentSelector.setCurrentSegmentID(self._parameterNode.GetParameter("fibulaSegment"))
    self.ui.vesselsSegmentSelector.setCurrentNode(self._parameterNode.GetNodeReference("vesselsSegmentation"))
    self.ui.vesselsSegmentSelector.setCurrentSegmentID(self._parameterNode.GetParameter("vesselsSegment"))
    self.ui.fibulaSurgicalGuideBaseSelector.setCurrentNode(self._parameterNode.GetNodeReference("fibulaSurgicalGuideBaseModel"))
    self.ui.mandibleSurgicalGuideBaseSelector.setCurrentNode(self._parameterNode.GetNodeReference("mandibleSurgicalGuideBaseModel"))
    self.ui.dentalImplantFiducialListSelector.setCurrentNode(self._parameterNode.GetNodeReference("dentalImplantsFiducialList"))
    #self.ui.dentalImplantCylinderSelector.setCurrentNode(self._parameterNode.GetNodeReference("selectedDentalImplantCylinderModel"))
    self.ui.plateCurveSelector.setCurrentNode(self._parameterNode.GetNodeReference("plateCurve"))

    # Keep the planning place widgets pointing to the currently referenced nodes.
    # They are otherwise only bound at setup or on node removal, so loading a scene
    # (which switches the referenced nodes) would leave the widgets bound to stale nodes.
    self.ui.mandibleCurvePlaceWidget.setCurrentNode(self.logic.getMandibularCurve())
    self.ui.fibulaLinePlaceWidget.setCurrentNode(self.logic.getFibulaLine())
    self.ui.interCondylarBeamLinePlaceWidget.setCurrentNode(self.logic.getInterCondylarBeamLine())
    self.ui.miterBoxDirectionLinePlaceWidget.setCurrentNode(self.logic.getMiterBoxDirectionLine())
    self.ui.fibulaFiducialsPlaceWidget.setCurrentNode(self.logic.getFibulaFiducials())
    self.ui.mandibleFiducialsPlaceWidget.setCurrentNode(self.logic.getMandibleFiducials())
    self.ui.mandibleBridgeCurvePlaceWidget.setCurrentNode(self.logic.getMandibleBridgeCurve())
    self.ui.leftSideMandibleGuideBaseCurvePlaceWidget.setCurrentNode(self.logic.getLeftSideMandibleGuideBaseCurve())
    self.ui.rightSideMandibleGuideBaseCurvePlaceWidget.setCurrentNode(self.logic.getRightSideMandibleGuideBaseCurve())

    self.ui.donorLegComboBox.currentText = self._parameterNode.GetParameter("donorLeg")
    
    self.ui.initialSpinBox.setValue(float(self._parameterNode.GetParameter("initialSpace_mm")))
    self.ui.betweenSpinBox.setValue(float(self._parameterNode.GetParameter("additionalBetweenSpaceOfFibulaPlanes_mm")))
    self.ui.securityMarginOfFibulaPiecesSpinBox.setValue(float(self._parameterNode.GetParameter("securityMarginOfFibulaPieces_mm")))
    self.ui.miterBoxSlotWidthSpinBox.setValue(float(self._parameterNode.GetParameter("miterBoxSlotWidth_mm")))
    self.ui.miterBoxSlotLengthSpinBox.setValue(float(self._parameterNode.GetParameter("miterBoxSlotLength_mm")))
    self.ui.miterBoxSlotHeightSpinBox.setValue(float(self._parameterNode.GetParameter("miterBoxSlotHeight_mm")))
    self.ui.miterBoxSlotWallSpinBox.setValue(float(self._parameterNode.GetParameter("miterBoxSlotWall_mm")))
    self.ui.fibulaScrewHoleCylinderRadiusSpinBox.setValue(float(self._parameterNode.GetParameter("fibulaScrewHoleCylinderRadius_mm")))
    self.ui.clearanceFitPrintingToleranceSpinBox.setValue(float(self._parameterNode.GetParameter("clearanceFitPrintingTolerance_mm")))
    self.ui.fibulaGuidebaseThicknessSpinBox.setValue(float(self._parameterNode.GetParameter("fibulaGuidebaseThickness_mm")))
    self.ui.fibulaGuidebaseMarginSpinBox.setValue(float(self._parameterNode.GetParameter("fibulaGuidebaseMargin_mm")))
    self.ui.fibulaGuidebaseAngleSpinBox.setValue(float(self._parameterNode.GetParameter("fibulaGuidebaseAngle_mm")))
    self.ui.biggerMiterBoxDistanceToFibulaSpinBox.setValue(float(self._parameterNode.GetParameter("biggerMiterBoxDistanceToFibula_mm")))
    self.ui.sawBoxSlotWidthSpinBox.setValue(float(self._parameterNode.GetParameter("sawBoxSlotWidth_mm")))
    self.ui.sawBoxSlotLengthSpinBox.setValue(float(self._parameterNode.GetParameter("sawBoxSlotLength_mm")))
    self.ui.sawBoxSlotHeightSpinBox.setValue(float(self._parameterNode.GetParameter("sawBoxSlotHeight_mm")))
    self.ui.sawBoxSlotWallSpinBox.setValue(float(self._parameterNode.GetParameter("sawBoxSlotWall_mm")))
    self.ui.biggerSawBoxDistanceToMandibleSpinBox.setValue(float(self._parameterNode.GetParameter("biggerSawBoxDistanceToMandible_mm")))
    self.ui.mandibleScrewHoleCylinderRadiusSpinBox.setValue(float(self._parameterNode.GetParameter("mandibleScrewHoleCylinderRadius_mm")))
    self.ui.mandibleBridgeRadiusSpinBox.setValue(float(self._parameterNode.GetParameter("mandibleBridgeRadius_mm")))
    self.ui.mandibleGuidebaseThicknessSpinBox.setValue(float(self._parameterNode.GetParameter("mandibleGuidebaseThickness_mm")))
    self.ui.dentalImplantCylinderRadiusSpinBox.setValue(float(self._parameterNode.GetParameter("dentalImplantCylinderRadius_mm")))
    self.ui.dentalImplantCylinderHeightSpinBox.setValue(float(self._parameterNode.GetParameter("dentalImplantCylinderHeight_mm")))
    self.ui.dentalImplantDrillGuideWallSpinBox.setValue(float(self._parameterNode.GetParameter("dentalImplantDrillGuideWall_mm")))
    self.ui.plateCrossSectionalWidthSpinBox.setValue(float(self._parameterNode.GetParameter("plateCrossSectionalWidth_mm")))
    self.ui.plateCrossSectionalLengthSpinBox.setValue(float(self._parameterNode.GetParameter("plateCrossSectionalLength_mm")))
    self.ui.plateCrossSectionalBevelRadiusPorcentageSpinBox.setValue(float(self._parameterNode.GetParameter("plateCrossSectionalBevelRadiusPorcentage")))
    self.ui.plateTipsBevelRadiusSpinBox.setValue(float(self._parameterNode.GetParameter("plateTipsBevelRadius")))

    self.ui.fibulaNormalizationTransformButton.checked = self._parameterNode.GetParameter("fibulaNormalizationTransform") == "True"
    self.ui.makeAllMandiblePlanesRotateTogetherCheckBox.checked = self._parameterNode.GetParameter("makeAllMandiblePlanesRotateTogether") == "True"
    self.ui.useMoreExactVersionOfPositioningAlgorithmCheckBox.checked = self._parameterNode.GetParameter("useMoreExactVersionOfPositioningAlgorithm") == "True"
    self.ui.mandiblePlanesPositioningForMaximumBoneContactCheckBox.checked = self._parameterNode.GetParameter("mandiblePlanesPositioningForMaximumBoneContact") == "True"
    
    includeVesselsOnPlanChecked = self._parameterNode.GetParameter("includeVesselsOnPlan") == "True"
    self.ui.includeVesselsOnPlanCheckBox.checked = includeVesselsOnPlanChecked
    self.setOriginalAndTranslatedVesselsVisibility(includeVesselsOnPlanChecked)

    useNonDecimatedModelsForPreviewChecked = self._parameterNode.GetParameter("useNonDecimatedModelsForPreview") == "True"
    self.ui.useNonDecimatedModelsForPreviewCheckBox.checked = useNonDecimatedModelsForPreviewChecked
    self.showInputModelsAsNonDecimated(useNonDecimatedModelsForPreviewChecked)

    fibulaSurgicalGuideElementsVisible = self._parameterNode.GetParameter("fibulaSurgicalGuideElementsVisible") == "True"
    self.ui.fibulaSurgicalGuideElementsVisibleCheckBox.checked = fibulaSurgicalGuideElementsVisible
    self.setFibulaGuideBaseElementsVisibility(fibulaSurgicalGuideElementsVisible)

    fibulaSurgicalGuideVisible = self._parameterNode.GetParameter("fibulaSurgicalGuideVisible") == "True"
    self.ui.fibulaSurgicalGuideVisibleCheckBox.checked = fibulaSurgicalGuideVisible
    self.setFibulaSurgicalGuideVisibility(fibulaSurgicalGuideVisible)
    self.ui.fibulaSurgicalGuideVisibleCheckBox.enabled = (
      self._parameterNode.GetNodeReference("fibulaSurgicalGuidePrototypeModel") is not None
    )

    mandibleSurgicalGuideElementsVisible = self._parameterNode.GetParameter("mandibleSurgicalGuideElementsVisible") == "True"
    self.ui.mandibleSurgicalGuideElementsVisibleCheckBox.checked = mandibleSurgicalGuideElementsVisible
    self.setMandibleGuideBaseElementsVisibility(mandibleSurgicalGuideElementsVisible)

    mandibleSurgicalGuideVisible = self._parameterNode.GetParameter("mandibleSurgicalGuideVisible") == "True"
    self.ui.mandibleSurgicalGuideVisibleCheckBox.checked = mandibleSurgicalGuideVisible
    self.setMandibleSurgicalGuideVisibility(mandibleSurgicalGuideVisible)
    self.ui.mandibleSurgicalGuideVisibleCheckBox.enabled = (
      self._parameterNode.GetNodeReference("mandibleSurgicalGuidePrototypeModel") is not None
    )

    if self._parameterNode.GetParameter("miterBoxesNeedUpdate") == "True":
      # always hide till the GUI feedback feature is complete
      self.ui.miterBoxesNeedUpdateLabel.hide()
      # self.ui.miterBoxesNeedUpdateLabel.show()
    else:
      self.ui.miterBoxesNeedUpdateLabel.hide()

    if self._parameterNode.GetParameter("sawBoxesNeedUpdate") == "True":
      # always hide till the GUI feedback feature is complete
      # self.ui.sawBoxesNeedUpdateLabel.show()
      self.ui.sawBoxesNeedUpdateLabel.hide()
    else:
      self.ui.sawBoxesNeedUpdateLabel.hide()

    useMandibleGuideBasesFromCurvesChecked = self._parameterNode.GetParameter("useMandibleGuideBasesFromCurves") == "True"
    self.ui.mandibleSurgicalGuideBaseSelector.enabled = not useMandibleGuideBasesFromCurvesChecked
    self.ui.useMandibleGuideBasesFromCurvesCheckBox.checked = useMandibleGuideBasesFromCurvesChecked

    doDisplayOrientation3DCube = self._parameterNode.GetParameter("displayOrientation3DCube") == "True"
    self.ui.orientation3DCubeCheckBox.checked = doDisplayOrientation3DCube
    displayOrientation3DCube(doDisplayOrientation3DCube)
    
    self.ui.lightingModeComboBox.currentText = self._parameterNode.GetParameter("lightingMode")
    setLightingMode(self._parameterNode.GetParameter("lightingMode"))
    self.ui.lightingInterpolationMethodComboBox.currentText = self._parameterNode.GetParameter("lightingInterpolationMethod")
    setModelsLightingInterpolationMethod(self._parameterNode.GetParameter("lightingInterpolationMethod"))

    self.ui.makeModelsButton.enabled = (
      (self._parameterNode.GetNodeReference("mandibularSegmentation") is not None) and
      (self._parameterNode.GetNodeReference("fibulaSegmentation") is not None) and
      (self._parameterNode.GetParameter("mandibularSegment") != "") and
      (self._parameterNode.GetParameter("fibulaSegment") != "")
    )
    
    checkSecurityMarginOnMiterBoxCreationChecked = self._parameterNode.GetParameter("checkSecurityMarginOnMiterBoxCreation") != "False"
    self.ui.checkSecurityMarginOnMiterBoxCreationCheckBox.checked = checkSecurityMarginOnMiterBoxCreationChecked
    self.ui.securityMarginOfFibulaPiecesFrame.enabled = checkSecurityMarginOnMiterBoxCreationChecked

    self.ui.fibulaSegmentsMeasurementModeComboBox.currentText = self._parameterNode.GetParameter("fibulaSegmentsMeasurementMode")
    
    self.ui.mandibleSideToRemoveComboBox.removeItem(2)
    kindOfMandibleResection = self._parameterNode.GetParameter("kindOfMandibleResection")
    self.ui.kindOfMandibleResectionComboBox.currentText = kindOfMandibleResection
    if kindOfMandibleResection == "Segmental Mandibulectomy":
      self.ui.mandibleBridgeCurvePlaceWidget.enabled = True
      self.ui.mandibleBridgeCurvePlaceWidget.toolTip = "Bridge model to connect both mandible guides (optional)."

      self.ui.mandibleSideToRemoveComboBox.enabled = False
      self.ui.mandibleSideToRemoveComboBox.addItem("")
      self.ui.mandibleSideToRemoveComboBox.currentText = ""
    else:
      self.ui.mandibleBridgeCurvePlaceWidget.enabled = False
      self.ui.mandibleBridgeCurvePlaceWidget.toolTip = "Bridge model will not be used since you selected an hemimandibulectomy."

      self.ui.mandibleSideToRemoveComboBox.enabled = True
      self.ui.mandibleSideToRemoveComboBox.removeItem(2)
      self.ui.mandibleSideToRemoveComboBox.currentText = self._parameterNode.GetParameter("mandibleSideToRemove")


    # TODO: finish implementation, probably needs turning around the fibula centerline support of miterBoxes
    self.ui.miterBoxesGuideTypeLabel.hide()
    self.ui.miterBoxesGuideTypeComboBox.hide()
    self.ui.miterBoxesGuideTypeComboBox.currentText = self._parameterNode.GetParameter("miterBoxesGuideType")
    self.ui.sawBoxesGuideTypeLabel.hide()
    self.ui.sawBoxesGuideTypeComboBox.hide()
    self.ui.sawBoxesGuideTypeComboBox.currentText = self._parameterNode.GetParameter("sawBoxesGuideType")


    #if self._parameterNode.GetParameter("miterBoxesGuideType") == "Slot":
    #  self.ui.miterBoxesBoxTypeLabel.show()
    #  self.ui.miterBoxesBoxTypeComboBox.show()
    #else:
    #  self.ui.miterBoxesBoxTypeLabel.hide()
    #  self.ui.miterBoxesBoxTypeComboBox.hide()
    self.ui.miterBoxesBoxTypeComboBox.currentText = self._parameterNode.GetParameter("miterBoxesBoxType")


    #if self._parameterNode.GetParameter("sawBoxesGuideType") == "Slot":
    #  self.ui.sawBoxesBoxTypeLabel.show()
    #  self.ui.sawBoxesBoxTypeComboBox.show()
    #else:
    #  self.ui.sawBoxesBoxTypeLabel.hide()
    #  self.ui.sawBoxesBoxTypeComboBox.hide()
    #self.ui.sawBoxesBoxTypeComboBox.currentText = self._parameterNode.GetParameter("sawBoxesBoxType")

    
    AISegmentationsChecked = self._parameterNode.GetParameter("AISegmentations") == "True"
    dentalImplantsPlanningAndFibulaDrillGuidesChecked = self._parameterNode.GetParameter("dentalImplantsPlanningAndFibulaDrillGuides") == "True"
    customTitaniumPlateDesingChecked = self._parameterNode.GetParameter("customTitaniumPlateDesing") == "True"
    makeAllDentalImplanCylindersParallelChecked = self._parameterNode.GetParameter("makeAllDentalImplanCylindersParallel") == "True"
    self.ui.AISegmentationsCheckBox.checked = AISegmentationsChecked
    self.ui.dentalImplantsPlanningAndFibulaDrillGuidesCheckBox.checked = dentalImplantsPlanningAndFibulaDrillGuidesChecked
    self.ui.customTitaniumPlateDesingCheckBox.checked = customTitaniumPlateDesingChecked
    self.ui.makeAllDentalImplanCylindersParallelCheckBox.checked = makeAllDentalImplanCylindersParallelChecked

    if AISegmentationsChecked:
      self.ui.AISegmentationCollapsibleButton.show()
    else:
      self.ui.AISegmentationCollapsibleButton.hide()
    
    if dentalImplantsPlanningAndFibulaDrillGuidesChecked:
      self.ui.dentalImplantsPlanningCollapsibleButton.show()
      self.ui.makeBooleanOperationsToFibulaSurgicalGuideBaseButton.text = (
        "Create fibula\nand implants\nsurgical guide"
      )
    else:
      self.ui.dentalImplantsPlanningCollapsibleButton.hide()
      self.ui.makeBooleanOperationsToFibulaSurgicalGuideBaseButton.text = (
        "Create fibula\nsurgical guide"
      )
    
    if customTitaniumPlateDesingChecked:
      self.ui.customTitaniumPlateGenerationCollapsibleButton.show()
    else:
      self.ui.customTitaniumPlateGenerationCollapsibleButton.hide()

    showInterCondylarBeamBoxChecked = self._parameterNode.GetParameter("showInterCondylarBeamBox") == "True"
    self.ui.interCondylarBeamVisibilityToolButton.checked = showInterCondylarBeamBoxChecked
    self.setInterCondylarBeamVisibility(showInterCondylarBeamBoxChecked)

    lockVSPChecked = self._parameterNode.GetParameter("lockVSP") == "True"

    showMandiblePlanesChecked = self._parameterNode.GetParameter("showMandiblePlanes") == "True"
    self.ui.showMandiblePlanesToolButton.checked = showMandiblePlanesChecked
    self.setMandiblePlanesVisibility(showMandiblePlanesChecked)
    
    showMandiblePlanesInteractionHandlesChecked = self._parameterNode.GetParameter("showMandiblePlanesInteractionHandles") == "True"
    showMandiblePlanesInteractionHandles = (
      showMandiblePlanesChecked and showMandiblePlanesInteractionHandlesChecked and
      (not lockVSPChecked)
    )
    self.ui.showMandiblePlanesInteractionHandlesToolButton.checked = (
      showMandiblePlanesInteractionHandles
    )
    self.setMandiblePlanesInteractionHandlesVisibility(showMandiblePlanesInteractionHandles)
    self.ui.showMandiblePlanesInteractionHandlesToolButton.enabled = (
      showMandiblePlanesChecked and
      (not lockVSPChecked)
    )
    
    inCameraPlaneInteractionHandlesChecked = self._parameterNode.GetParameter("inCameraPlaneInteractionHandles") == "True"
    inCameraPlaneInteractionHandles = (
      showMandiblePlanesChecked and 
      showMandiblePlanesInteractionHandlesChecked and 
      inCameraPlaneInteractionHandlesChecked and
      (not lockVSPChecked)
    )
    self.ui.inCameraPlaneInteractionHandlesToolButton.checked = (
      inCameraPlaneInteractionHandles
    )
    self.setMandiblePlanesInCameraPlaneInteractionHandles(inCameraPlaneInteractionHandles)
    self.ui.inCameraPlaneInteractionHandlesToolButton.enabled = (
      showMandiblePlanesChecked and
      showMandiblePlanesInteractionHandlesChecked and 
      (not lockVSPChecked)
    )


    mandibularPlanesList = createListFromFolderName("Mandibular planes")
    fibulaLine = self._parameterNode.GetNodeReference("fibulaLine")
    mandibularCurve = self._parameterNode.GetNodeReference("mandibleCurve")
    planningObjectsList = mandibularPlanesList + [fibulaLine,mandibularCurve]
    if lockVSPChecked:
      self.setMandiblePlanesVisibility(showMandiblePlanesChecked)
      self.logic.setMarkupsListLocked(planningObjectsList,locked=True)
      #self.logic.removeMandiblePlaneObservers()
      #
      self.ui.lockVSPButton.checked = True
      self.ui.parametersOfVSPFrame.enabled = False
      self.ui.updateVSPButtonsFrame.enabled = False
      self.ui.create3DModelOfTheReconstructionFrame.enabled = False
    else:
      #self.setMandiblePlanesVisibility(True)
      self.logic.setMarkupsListLocked(planningObjectsList,locked=False)
      #self.logic.removeMandiblePlaneObservers() # in case they already exist
      #self.logic.addMandiblePlaneObservers()
      #
      self.ui.lockVSPButton.checked = False
      self.ui.parametersOfVSPFrame.enabled = True
      self.ui.updateVSPButtonsFrame.enabled = True
      self.ui.create3DModelOfTheReconstructionFrame.enabled = True
    

    self.ui.neomandibleVisibilityButton.checked = self._parameterNode.GetParameter("neomandibleVisible") == "True"


    if self._parameterNode.GetParameter("updateOnMandiblePlanesMovement") == "True":
      self.ui.generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandibleButton.checkState = 2
    else:
      self.ui.generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandibleButton.checkState = 0

    if self._parameterNode.GetParameter("updateOnDentalImplantPlanesMovement") == "True":
      self.ui.updateFibulaDentalImplantCylindersButton.checkState = 2
    else:
      self.ui.updateFibulaDentalImplantCylindersButton.checkState = 0

    showFibulaSegmentsLengthsChecked = self._parameterNode.GetParameter("showFibulaSegmentsLengths") == "True"
    self.ui.showFibulaSegmentsLengthsCheckBox.checked = showFibulaSegmentsLengthsChecked
    self.setFibulaSegmentsLengthsVisibility(showFibulaSegmentsLengthsChecked)
    
    showOriginalMandibleChecked = self._parameterNode.GetParameter("showOriginalMandible") == "True"
    self.ui.showOriginalMandibleCheckBox.checked = showOriginalMandibleChecked
    self.setOriginalMandibleVisibility(showOriginalMandibleChecked)

    showBiggerSawBoxesInteractionHandlesChecked = self._parameterNode.GetParameter("showBiggerSawBoxesInteractionHandles") == "True"
    self.ui.showBiggerSawBoxesInteractionHandlesCheckBox.checked = showBiggerSawBoxesInteractionHandlesChecked
    self.setBiggerSawBoxesInteractionHandlesVisibility(showBiggerSawBoxesInteractionHandlesChecked)

    # we are going to change the instructions any time the parameterNode is modified
    self.logic.setPlanningInformativeText()
    self.ui.planningInformativeLabel.text = self._parameterNode.GetParameter("planningInformativeText")
    self.ui.planningInformativeLabel.hide() # hide until new BRP version supports it fully

    # All the GUI updates are done
    self._updatingGUIFromParameterNode = False

  def updateParameterNodeFromGUI(self, caller=None, event=None):
    """
    This method is called when the user makes any change in the GUI.
    The changes are saved into the parameter node (so that they are restored when the scene is saved and loaded).
    """

    if (
      self._parameterNode is None or 
      self._updatingGUIFromParameterNode or
      not USING_GUI
    ):
      return

    wasModified = self._parameterNode.StartModify()  # Modify all properties in a single batch

    previousScalarVolume = self._parameterNode.GetNodeReference("currentScalarVolume")
    self._parameterNode.SetNodeReferenceID("currentScalarVolume", self.ui.scalarVolumeSelector.currentNodeID)
    currentScalarVolumeChanged = str(
      self.ui.scalarVolumeSelector.currentNode() is not previousScalarVolume
    )
    if currentScalarVolumeChanged == "True":
      self._parameterNode.SetParameter("scalarVolumeChangedThroughParameterNode", "True")
      if previousScalarVolume is not None:
        self.ui.scalarVolumeSelector.currentNode().SetAndObserveTransformNodeID(
          previousScalarVolume.GetTransformNodeID()
        )
        previousScalarVolume.SetAndObserveTransformNodeID("")

    self._parameterNode.SetNodeReferenceID("headCT", self.ui.headCTSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("legsCT", self.ui.legsCTSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("mandibularSegmentation", self.ui.mandibularSegmentSelector.currentNodeID())
    self._parameterNode.SetParameter("mandibularSegment", self.ui.mandibularSegmentSelector.currentSegmentID())
    self._parameterNode.SetNodeReferenceID("fibulaSegmentation", self.ui.fibulaSegmentSelector.currentNodeID())
    self._parameterNode.SetParameter("fibulaSegment", self.ui.fibulaSegmentSelector.currentSegmentID())
    self._parameterNode.SetNodeReferenceID("vesselsSegmentation", self.ui.vesselsSegmentSelector.currentNodeID())
    self._parameterNode.SetParameter("vesselsSegment", self.ui.vesselsSegmentSelector.currentSegmentID())
    self._parameterNode.SetNodeReferenceID("fibulaSurgicalGuideBaseModel", self.ui.fibulaSurgicalGuideBaseSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("mandibleSurgicalGuideBaseModel", self.ui.mandibleSurgicalGuideBaseSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("dentalImplantsFiducialList", self.ui.dentalImplantFiducialListSelector.currentNodeID)
    #self._parameterNode.SetNodeReferenceID("selectedDentalImplantCylinderModel", self.ui.dentalImplantCylinderSelector.currentNodeID)
    self._parameterNode.SetNodeReferenceID("plateCurve", self.ui.plateCurveSelector.currentNodeID)

    self._parameterNode.SetParameter("headCTCorticalBoneThreshold", str(self.ui.headCTCorticalBoneThresholdSlider.value))
    self._parameterNode.SetParameter("legsCTCorticalBoneThreshold", str(self.ui.legsCTCorticalBoneThresholdSlider.value))

    self._parameterNode.SetParameter("initialSpace_mm", str(self.ui.initialSpinBox.value))
    self._parameterNode.SetParameter("additionalBetweenSpaceOfFibulaPlanes_mm", str(self.ui.betweenSpinBox.value))
    self._parameterNode.SetParameter("securityMarginOfFibulaPieces_mm", str(self.ui.securityMarginOfFibulaPiecesSpinBox.value))
    self._parameterNode.SetParameter("miterBoxSlotWidth_mm", str(self.ui.miterBoxSlotWidthSpinBox.value))
    self._parameterNode.SetParameter("miterBoxSlotLength_mm", str(self.ui.miterBoxSlotLengthSpinBox.value))
    self._parameterNode.SetParameter("miterBoxSlotHeight_mm", str(self.ui.miterBoxSlotHeightSpinBox.value))
    self._parameterNode.SetParameter("miterBoxSlotWall_mm", str(self.ui.miterBoxSlotWallSpinBox.value))
    self._parameterNode.SetParameter("fibulaScrewHoleCylinderRadius_mm", str(self.ui.fibulaScrewHoleCylinderRadiusSpinBox.value))
    self._parameterNode.SetParameter("clearanceFitPrintingTolerance_mm", str(self.ui.clearanceFitPrintingToleranceSpinBox.value))
    self._parameterNode.SetParameter("biggerMiterBoxDistanceToFibula_mm", str(self.ui.biggerMiterBoxDistanceToFibulaSpinBox.value))
    self._parameterNode.SetParameter("fibulaGuidebaseThickness_mm", str(self.ui.fibulaGuidebaseThicknessSpinBox.value))
    self._parameterNode.SetParameter("fibulaGuidebaseMargin_mm", str(self.ui.fibulaGuidebaseMarginSpinBox.value))
    self._parameterNode.SetParameter("fibulaGuidebaseAngle_mm", str(self.ui.fibulaGuidebaseAngleSpinBox.value))
    self._parameterNode.SetParameter("sawBoxSlotWidth_mm", str(self.ui.sawBoxSlotWidthSpinBox.value))
    self._parameterNode.SetParameter("sawBoxSlotLength_mm", str(self.ui.sawBoxSlotLengthSpinBox.value))
    self._parameterNode.SetParameter("sawBoxSlotHeight_mm", str(self.ui.sawBoxSlotHeightSpinBox.value))
    self._parameterNode.SetParameter("sawBoxSlotWall_mm", str(self.ui.sawBoxSlotWallSpinBox.value))
    self._parameterNode.SetParameter("biggerSawBoxDistanceToMandible_mm", str(self.ui.biggerSawBoxDistanceToMandibleSpinBox.value))
    self._parameterNode.SetParameter("mandibleScrewHoleCylinderRadius_mm", str(self.ui.mandibleScrewHoleCylinderRadiusSpinBox.value))
    self._parameterNode.SetParameter("mandibleBridgeRadius_mm", str(self.ui.mandibleBridgeRadiusSpinBox.value))
    self._parameterNode.SetParameter("mandibleGuidebaseThickness_mm", str(self.ui.mandibleGuidebaseThicknessSpinBox.value))
    self._parameterNode.SetParameter("dentalImplantCylinderRadius_mm", str(self.ui.dentalImplantCylinderRadiusSpinBox.value))
    self._parameterNode.SetParameter("dentalImplantCylinderHeight_mm", str(self.ui.dentalImplantCylinderHeightSpinBox.value))
    self._parameterNode.SetParameter("dentalImplantDrillGuideWall_mm", str(self.ui.dentalImplantDrillGuideWallSpinBox.value))
    self._parameterNode.SetParameter("plateCrossSectionalWidth_mm", str(self.ui.plateCrossSectionalWidthSpinBox.value))
    self._parameterNode.SetParameter("plateCrossSectionalLength_mm", str(self.ui.plateCrossSectionalLengthSpinBox.value))
    self._parameterNode.SetParameter("plateCrossSectionalBevelRadiusPorcentage", str(self.ui.plateCrossSectionalBevelRadiusPorcentageSpinBox.value))
    self._parameterNode.SetParameter("plateTipsBevelRadius", str(self.ui.plateTipsBevelRadiusSpinBox.value))

    self._parameterNode.SetParameter("fibulaSegmentsMeasurementMode", self.ui.fibulaSegmentsMeasurementModeComboBox.currentText)
    self._parameterNode.SetParameter("miterBoxesGuideType", self.ui.miterBoxesGuideTypeComboBox.currentText)
    self._parameterNode.SetParameter("miterBoxesBoxType", self.ui.miterBoxesBoxTypeComboBox.currentText)
    self._parameterNode.SetParameter("sawBoxesGuideType", self.ui.sawBoxesGuideTypeComboBox.currentText)
    self._parameterNode.SetParameter("kindOfMandibleResection", self.ui.kindOfMandibleResectionComboBox.currentText)
    if self.ui.mandibleSideToRemoveComboBox.currentText != "":
      self._parameterNode.SetParameter("mandibleSideToRemove", self.ui.mandibleSideToRemoveComboBox.currentText)

    self._parameterNode.SetParameter("donorLeg", self.ui.donorLegComboBox.currentText)

    if self.ui.includeVesselsOnPlanCheckBox.checked:
      self._parameterNode.SetParameter("includeVesselsOnPlan","True")
    else:
      self._parameterNode.SetParameter("includeVesselsOnPlan","False")
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
    if self.ui.useNonDecimatedModelsForPreviewCheckBox.checked:
      self._parameterNode.SetParameter("useNonDecimatedModelsForPreview","True")
    else:
      self._parameterNode.SetParameter("useNonDecimatedModelsForPreview","False")
    if self.ui.interCondylarBeamVisibilityToolButton.checked:
      self._parameterNode.SetParameter("showInterCondylarBeamBox","True")
    else:
      self._parameterNode.SetParameter("showInterCondylarBeamBox","False")
    if self.ui.showMandiblePlanesToolButton.checked:
      self._parameterNode.SetParameter("showMandiblePlanes","True")
    else:
      self._parameterNode.SetParameter("showMandiblePlanes","False")
    if self.ui.showMandiblePlanesInteractionHandlesToolButton.checked:
      self._parameterNode.SetParameter("showMandiblePlanesInteractionHandles","True")
    else:
      self._parameterNode.SetParameter("showMandiblePlanesInteractionHandles","False")
    if self.ui.inCameraPlaneInteractionHandlesToolButton.checked:
      self._parameterNode.SetParameter("inCameraPlaneInteractionHandles","True")
    else:
      self._parameterNode.SetParameter("inCameraPlaneInteractionHandles","False")
    if self.ui.checkSecurityMarginOnMiterBoxCreationCheckBox.checked:
      self._parameterNode.SetParameter("checkSecurityMarginOnMiterBoxCreation","True")
    else:
      self._parameterNode.SetParameter("checkSecurityMarginOnMiterBoxCreation","False")
    if self.ui.fibulaSurgicalGuideElementsVisibleCheckBox.checked:
      self._parameterNode.SetParameter("fibulaSurgicalGuideElementsVisible","True")
    else:
      self._parameterNode.SetParameter("fibulaSurgicalGuideElementsVisible","False")
    if self.ui.fibulaSurgicalGuideVisibleCheckBox.checked:
      self._parameterNode.SetParameter("fibulaSurgicalGuideVisible","True")
    else:
      self._parameterNode.SetParameter("fibulaSurgicalGuideVisible","False")
    if self.ui.mandibleSurgicalGuideElementsVisibleCheckBox.checked:
      self._parameterNode.SetParameter("mandibleSurgicalGuideElementsVisible","True")
    else:
      self._parameterNode.SetParameter("mandibleSurgicalGuideElementsVisible","False")
    if self.ui.mandibleSurgicalGuideVisibleCheckBox.checked:
      self._parameterNode.SetParameter("mandibleSurgicalGuideVisible","True")
    else:
      self._parameterNode.SetParameter("mandibleSurgicalGuideVisible","False")
    if self.ui.useMandibleGuideBasesFromCurvesCheckBox.checked:
      self._parameterNode.SetParameter("useMandibleGuideBasesFromCurves","True")
    else:
      self._parameterNode.SetParameter("useMandibleGuideBasesFromCurves","False")
    if self.ui.generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandibleButton.checkState == qt.Qt.Checked:
      self._parameterNode.SetParameter("updateOnMandiblePlanesMovement","True")
    else:
      self._parameterNode.SetParameter("updateOnMandiblePlanesMovement","False")
    if self.ui.updateFibulaDentalImplantCylindersButton.checkState == qt.Qt.Checked:
      self._parameterNode.SetParameter("updateOnDentalImplantPlanesMovement","True")
    else:
      self._parameterNode.SetParameter("updateOnDentalImplantPlanesMovement","False")
    if self.ui.AISegmentationsCheckBox.checked:
      self._parameterNode.SetParameter("AISegmentations","True")
    else:
      self._parameterNode.SetParameter("AISegmentations","False")
    self.logic.overwriteParameter("AISegmentations")
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

    if self.ui.showFibulaSegmentsLengthsCheckBox.checked:
      self._parameterNode.SetParameter("showFibulaSegmentsLengths", "True")
    else:
      self._parameterNode.SetParameter("showFibulaSegmentsLengths", "False")
    if self.ui.showOriginalMandibleCheckBox.checked:
      self._parameterNode.SetParameter("showOriginalMandible", "True")
    else:
      self._parameterNode.SetParameter("showOriginalMandible", "False")
    if self.ui.showBiggerSawBoxesInteractionHandlesCheckBox.checked:
      self._parameterNode.SetParameter("showBiggerSawBoxesInteractionHandles", "True")
    else:
      self._parameterNode.SetParameter("showBiggerSawBoxesInteractionHandles", "False")
    if self.ui.orientation3DCubeCheckBox.checked:
      self._parameterNode.SetParameter("displayOrientation3DCube", "True")
    else:
      self._parameterNode.SetParameter("displayOrientation3DCube", "False")

    self._parameterNode.SetParameter("lightingInterpolationMethod", self.ui.lightingInterpolationMethodComboBox.currentText)
    self._parameterNode.SetParameter("lightingMode", self.ui.lightingModeComboBox.currentText)

    self._parameterNode.EndModify(wasModified)

  def onRestoreDefaultSettingsButton(self):
    """
    Execute function to restore default parameters
    """
    self.logic.restoreDefaultParameters()

  def onOverwriteDefaultSettingsButton(self):
    """
    Execute function to overwrite default parameters
    """
    self.logic.overwriteDefaultParameters()

  def onEmailBugReportButton(self):
    """
    Execute function to start an email client with an email draft about a bug
    """
    send2 = ".".join("bone reconstruction planner+bug report@gmail com".split(" "))
    self.logic.prepareSendEmailOnWebBrowser(
      emailVariable = send2,
      subjectVariable = "[WRITE BUG TITLE]",
      bodyVariable = "Please describe the bug you found here." + "\n\n" + "Please attach the error log file here." 
    )

  def onEmailFeatureRequestButton(self):
    """
    Execute function to start an email client with an email draft requesting a feature
    """
    send2 = ".".join("bone reconstruction planner+feature request@gmail com".split(" "))
    self.logic.prepareSendEmailOnWebBrowser(
      emailVariable = send2,
      subjectVariable = "[WRITE FEATURE REQUEST TITLE]",
      bodyVariable = "Please describe the new feature you'd like here." 
    )
  
  def onOpenDocumentationButton(self):
    """
    Execute function to open the online BoneReconstructionPlanner documentation using a web-browser 
    """
    self.logic.openDocumentationOnWebBrowser()
  
  def onFixCutGoesThroughTheMandibleTwiceCheckBox(self):
    """
    Function to remember the checkbox was changed, and to update the parameterNode as usual 
    """
    # TODO this should use the updateParameterNodeFromGUI function
    if self._parameterNode is None or self._updatingGUIFromParameterNode:
      return

    wasModified = self._parameterNode.StartModify()
    if self.ui.fixCutGoesThroughTheMandibleTwiceCheckBox.checked:
      self._parameterNode.SetParameter("fixCutGoesThroughTheMandibleTwice","True")
    else:
      self._parameterNode.SetParameter("fixCutGoesThroughTheMandibleTwice","False")
    self._parameterNode.SetParameter("fixCutGoesThroughTheMandibleTwiceCheckBoxChanged","True")
    self._parameterNode.EndModify(wasModified)
    
  def onAddCutPlaneButton(self):
    """
    Function to start creating a mandible plane
    """
    self.logic.addCutPlane()

  def onRemoveCutPlaneButton(self):
    """
    Function to delete last mandible plane according to mandible curve index decreasing order
    """
    self.logic.removeCutPlane()
  
  def processingLabelShow(self, show):
    """
    Show processing label on the lower left corner of screen
    """
    # TODO: replace this function by using a dialog that is cancellable and that changes the mouse cursor to busy mode
    if not USING_GUI:
      return
    if show:
      self.ui.processingLabel.show()
    else:
      self.ui.processingLabel.hide()
    slicer.app.processEvents()

  def onMakeModelsButton(self):
    """
    Callback function to create bone models from segmentations
    """
    self.logic.makeModels()

  def onGenerateFibulaGuidebaseButton(self):
    """
    Callback function to create the fibula surgical guide base before boolean operations
    """
    self.logic.generateFibulaGuidebase()
  
  def onMakeBooleanOperationsToFibulaSurgicalGuideBaseButton(self):
    """
    Callback function to create the fibula surgical guide
    """
    self.logic.makeBooleanOperationsToFibulaSurgicalGuideBase()
  
  def onCreateDentalImplantCylindersFiducialListButton(self):
    """
    Callback function to create fiducials for dental implant cylinders
    """
    # TODO: remove this function and show the user a markupsSimpleWidget
    self.logic.createDentalImplantCylindersFiducialList()

  def onCreateCylindersFromFiducialListAndNeomandiblePiecesButton(self):
    """
    Callback function to create implant cylinders
    """
    self.logic.createCylindersFromFiducialListAndNeomandiblePieces()

  def onCreateSawBoxesFromFirstAndLastMandiblePlanesButton(self):
    """
    Callback function to create sawBoxes
    """
    self.logic.createSawBoxesFromFirstAndLastMandiblePlanes()

  def onMakeBooleanOperationsToMandibleSurgicalGuideBaseButton(self):
    """
    Callback function to create mandible surgical guide
    """
    self.logic.makeBooleanOperationsToMandibleSurgicalGuideBase()

  def onGenerateFibulaPlanesFibulaBonePiecesAndTransformThemToMandibleButton(self):
    """
    Callback function to execute the main pipeline for virtual surgical planning
    """
    self.logic.onGenerateFibulaPlanesTimerTimeout()
  
  def onHardVSPUpdateButton(self):
    """
    Callback function clean earlier, might be faulty, visualization and execute the main pipeline for virtual surgical planning again
    """
    self.logic.hardVSPUpdate()

  def onInterCondylarBeamIncreaseSizeButton(self):
    """
    Callback function to increase the intercondylar beam size
    """
    self.logic.interCondylarBeamSizeChange(positive = True)
  
  def onInterCondylarBeamDecreaseSizeButton(self):
    """
    Callback function to decrease the intercondylar beam size
    """
    self.logic.interCondylarBeamSizeChange(positive = False)

  def onFibulaNormalizationTransformButton(self,checked):
    """
    Callback function to avoid GUI modification of VSP parameters
    """
    self.logic.updateNormalizationFibulaLineTransform(checked)
  
  def onLockVSPButton(self,checked):
    """
    Callback function to avoid GUI modification of VSP parameters
    """
    self.logic.lockVSP(checked)

  def onNeomandibleVisibilityButton(self,checked):
    """
    Callback function to avoid GUI modification of VSP parameters
    """
    self.logic.setNeomandibleVisibility(checked)
  
  def setBiggerSawBoxesInteractionHandlesVisibility(self, visibility):
    """
    Set bigger sawBoxes interactive handles visibility
    """
    if not USING_GUI:
      return
    
    sawBoxesPlanesList = createListFromFolderName("sawBoxes Planes")

    for i in range(len(sawBoxesPlanesList)):
      displayNode = sawBoxesPlanesList[i].GetDisplayNode()
      displayNode.SetHandlesInteractive(visibility)

  def setMandiblePlanesVisibility(self, visibility):
    """
    Set mandible planes visibility
    """
    if not USING_GUI:
      return
    
    mandibularPlanesList = createListFromFolderName("Mandibular planes")

    for i in range(len(mandibularPlanesList)):
      displayNode = mandibularPlanesList[i].GetDisplayNode()
      displayNode.SetVisibility(visibility)

  def setMarkupControlPointsVisibility(self, markupsNode, visibility):
    """
    Set visibility of all control points in a markupNode. Does not affect rendering of interpolating lines.
    """
    if not USING_GUI:
      return
    
    if markupsNode is not None:
      for i in range(markupsNode.GetNumberOfControlPoints()):
        markupsNode.SetNthControlPointVisibility(i, visibility)
  
  def setInterCondylarBeamVisibility(self, visibility):
    """
    Set visibility of intercondylar beam model
    """
    if not USING_GUI:
      return
    
    interCondylarBeamBox = self._parameterNode.GetNodeReference("interCondylarBeamBox")

    if interCondylarBeamBox is not None:
      displayNode = interCondylarBeamBox.GetDisplayNode()
      displayNode.SetVisibility(visibility)

  def showInputModelsAsNonDecimated(self, nonDecimated):
    """
    Set visibility of fibula surgical guide elements
    """
    if not USING_GUI:
      return
    
    showOriginalMandibleChecked = self._parameterNode.GetParameter("showOriginalMandible") == "True"
    includeVesselsOnPlanChecked = self._parameterNode.GetParameter("includeVesselsOnPlan") == "True"

    nonDecimatedFibulaModelNode = self._parameterNode.GetNodeReference("fibulaModelNode")
    decimatedFibulaModelNode = self._parameterNode.GetNodeReference("decimatedFibulaModelNode")
    nonDecimatedMandibleModelNode = self._parameterNode.GetNodeReference("mandibleModelNode")
    decimatedMandibleModelNode = self._parameterNode.GetNodeReference("decimatedMandibleModelNode")
    nonDecimatedVesselsModelNode = self._parameterNode.GetNodeReference("vesselsModelNode")
    decimatedVesselsModelNode = self._parameterNode.GetNodeReference("decimatedVesselsModelNode")

    if not (
      nonDecimatedFibulaModelNode and 
      decimatedFibulaModelNode and 
      nonDecimatedMandibleModelNode and 
      decimatedMandibleModelNode
    ):
      return
    
    if nonDecimated:
      nonDecimatedFibulaModelDisplayNode = nonDecimatedFibulaModelNode.GetDisplayNode()
      decimatedFibulaModelDisplayNode = decimatedFibulaModelNode.GetDisplayNode()
      nonDecimatedFibulaModelDisplayNode.SetVisibility(True)
      decimatedFibulaModelDisplayNode.SetVisibility(False)

      nonDecimatedMandibleModelDisplayNode =  nonDecimatedMandibleModelNode.GetDisplayNode()
      decimatedMandibleModelDisplayNode = decimatedMandibleModelNode.GetDisplayNode()
      nonDecimatedMandibleModelDisplayNode.SetVisibility(True and showOriginalMandibleChecked)
      decimatedMandibleModelDisplayNode.SetVisibility(False)

      if nonDecimatedVesselsModelNode and decimatedVesselsModelNode:
        nonDecimatedVesselsModelDisplayNode = nonDecimatedVesselsModelNode.GetDisplayNode()
        decimatedVesselsModelDisplayNode = decimatedVesselsModelNode.GetDisplayNode()
        nonDecimatedVesselsModelDisplayNode.SetVisibility(True and includeVesselsOnPlanChecked)
        decimatedVesselsModelDisplayNode.SetVisibility(False)
      
    else:
      nonDecimatedFibulaModelDisplayNode = nonDecimatedFibulaModelNode.GetDisplayNode()
      decimatedFibulaModelDisplayNode = decimatedFibulaModelNode.GetDisplayNode()
      nonDecimatedFibulaModelDisplayNode.SetVisibility(False)
      decimatedFibulaModelDisplayNode.SetVisibility(True)

      nonDecimatedMandibleModelDisplayNode =  nonDecimatedMandibleModelNode.GetDisplayNode()
      decimatedMandibleModelDisplayNode = decimatedMandibleModelNode.GetDisplayNode()
      nonDecimatedMandibleModelDisplayNode.SetVisibility(False)
      decimatedMandibleModelDisplayNode.SetVisibility(True and showOriginalMandibleChecked)

      if nonDecimatedVesselsModelNode and decimatedVesselsModelNode:
        nonDecimatedVesselsModelDisplayNode = nonDecimatedVesselsModelNode.GetDisplayNode()
        decimatedVesselsModelDisplayNode = decimatedVesselsModelNode.GetDisplayNode()
        nonDecimatedVesselsModelDisplayNode.SetVisibility(False)
        decimatedVesselsModelDisplayNode.SetVisibility(True and includeVesselsOnPlanChecked)
    
    # and since the other models are created from them (e.g. dynamic modeler ones), they share the current visibility mode
    # after planning update
  
  def setFibulaGuideBaseElementsVisibility(self, visibility):
    """
    Set visibility of fibula surgical guide elements
    """
    if not USING_GUI:
      return
    
    fibulaSurgicalGuideBase = self._parameterNode.GetNodeReference("fibulaSurgicalGuideBaseModel")
    
    if fibulaSurgicalGuideBase is not None:
      fibulaSurgicalGuideBase.GetDisplayNode().SetVisibility(visibility)

    folderNames = [
      "previewMiterBoxes Models",
      "Fibula Cylinders Models"
    ]

    for folderName in folderNames:
      folderItem = getFolder(folderName)
      setFolderItemVisibility(folderItem, visibility)

  def setOriginalAndTranslatedVesselsVisibility(self, visibility):
    """
    Set visibility of original and translated vessels
    """
    if not USING_GUI:
      return
    
    vesselsModel = self.logic.getCurrentVesselsModel()
    
    if vesselsModel is not None:
      vesselsModel.GetDisplayNode().SetVisibility(visibility)
    
    folderNames = [
      "Cut Vessels",
      "Transformed Vessels Pieces"
    ]

    for folderName in folderNames:
      folderItem = getFolder(folderName)
      setFolderItemVisibility(folderItem, visibility)

  def setFibulaSurgicalGuideVisibility(self, visibility):
    """
    Set visibility of fibula surgical guide
    """
    if not USING_GUI:
      return
    
    fibulaSurgicalGuide = self._parameterNode.GetNodeReference("fibulaSurgicalGuidePrototypeModel")

    if fibulaSurgicalGuide is not None:
      fibulaSurgicalGuide.GetDisplayNode().SetVisibility(visibility)

  def setMandibleGuideBaseElementsVisibility(self, visibility):
    """
    Set visibility of mandible surgical guide elements
    """
    if not USING_GUI:
      return

    mandibleSurgicalGuideBase = self._parameterNode.GetNodeReference("mandibleSurgicalGuideBaseModel")

    if mandibleSurgicalGuideBase is not None:
      mandibleSurgicalGuideBase.GetDisplayNode().SetVisibility(visibility)
      mandibleViewNode = slicer.mrmlScene.GetSingletonNode(slicer.MANDIBLE_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
      mandibleSurgicalGuideBase.GetDisplayNode().AddViewNodeID(mandibleViewNode.GetID())
      mandibleSurgicalGuideBase.GetDisplayNode().SetVisibility2D(True)
      moveNodeToFolder(mandibleSurgicalGuideBase, getFolder("BoneReconstructionPlanner"))
      self.logic.setRedSliceForModelsDisplayNodes()
      self.logic.setRedSliceForMarkupsDisplayNodes()

    bothSidesMandibleGuideBaseModel = self._parameterNode.GetNodeReference("bothSidesMandibleGuideBaseModel")
    if bothSidesMandibleGuideBaseModel is not None:
      bothSidesMandibleGuideBaseModel.GetDisplayNode().SetVisibility(visibility)
      mandibleViewNode = slicer.mrmlScene.GetSingletonNode(slicer.MANDIBLE_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
      bothSidesMandibleGuideBaseModel.GetDisplayNode().AddViewNodeID(mandibleViewNode.GetID())
      bothSidesMandibleGuideBaseModel.GetDisplayNode().SetVisibility2D(True)
      moveNodeToFolder(bothSidesMandibleGuideBaseModel, getFolder("BoneReconstructionPlanner"))
      self.logic.setRedSliceForModelsDisplayNodes()
      self.logic.setRedSliceForMarkupsDisplayNodes()

    mandibleBridgeTube = self._parameterNode.GetNodeReference("mandibleBridgeTube")

    if mandibleBridgeTube is not None:
      mandibleBridgeTube.GetDisplayNode().SetVisibility(visibility)

    folderNames = [
      "previewSawBoxes Models",
      "Mandible Cylinders Models"
    ]

    for folderName in folderNames:
      folderItem = getFolder(folderName)
      setFolderItemVisibility(folderItem, visibility)

  def setMandibleSurgicalGuideVisibility(self, visibility):
    """
    Set visibility of mandible surgical guide
    """
    if not USING_GUI:
      return

    mandibleSurgicalGuide = self._parameterNode.GetNodeReference("mandibleSurgicalGuidePrototypeModel")

    if mandibleSurgicalGuide is not None:
      mandibleSurgicalGuide.GetDisplayNode().SetVisibility(visibility)

  def setMandiblePlanesInteractionHandlesVisibility(self, visibility):
    """
    Set visibility of mandible planes interactive handles
    """
    if not USING_GUI:
      return
    
    mandibularPlanesList = createListFromFolderName("Mandibular planes")

    for i in range(len(mandibularPlanesList)):
      displayNode = mandibularPlanesList[i].GetDisplayNode()
      displayNode.SetHandlesInteractive(visibility)

  def setMandiblePlanesInCameraPlaneInteractionHandles(self, visibility):
    """
    Set visibility of rotation interactive handles of mandible planes to inPlane only if True
    """
    if not USING_GUI:
      return
    
    mandibularPlanesList = createListFromFolderName("Mandibular planes")

    for i in range(len(mandibularPlanesList)):
      displayNode = mandibularPlanesList[i].GetDisplayNode()
      if visibility:
        x = False
        y = False
        z = False
        inPlane = True
      else:
        x = True
        y = True
        z = True
        inPlane = False
      displayNode.SetRotationHandleComponentVisibility(x,y,z,inPlane)
  
  def setFibulaSegmentsLengthsVisibility(self, visibility):
    """
    Set fibula segment measurement lines visibility
    """
    if not USING_GUI:
      return
    
    fibulaSegmentsLengthsList = createListFromFolderName("Fibula Segments Lengths")

    for i in range(len(fibulaSegmentsLengthsList)):
      lineDisplayNode = fibulaSegmentsLengthsList[i].GetDisplayNode()
      lineDisplayNode.SetVisibility(visibility)

  def onCreate3DModelOfTheReconstructionButton(self):
    """
    Callback to create a 3D model of the neomandible (with or without an intercondylar beam)
    """
    self.logic.create3DModelOfTheReconstruction()

  def setOriginalMandibleVisibility(self, visibility):
    """
    Set original mandible visibility
    """
    if not USING_GUI:
      return
    
    mandibleModelNode = self._parameterNode.GetNodeReference("mandibleModelNode")
    decimatedMandibleModelNode = self._parameterNode.GetNodeReference("decimatedMandibleModelNode")
    
    if (mandibleModelNode is None) and (decimatedMandibleModelNode is None):
      return

    useNonDecimatedModelsForPreviewChecked = self._parameterNode.GetParameter("useNonDecimatedModelsForPreview") == "True"

    mandibleModelDisplayNode = mandibleModelNode.GetDisplayNode()
    decimatedMandibleModelDisplayNode = decimatedMandibleModelNode.GetDisplayNode()

    if useNonDecimatedModelsForPreviewChecked:
      mandibleModelDisplayNode.SetVisibility(visibility)
      decimatedMandibleModelDisplayNode.SetVisibility(False)
    else:
      decimatedMandibleModelDisplayNode.SetVisibility(visibility)
      mandibleModelDisplayNode.SetVisibility(False)

  def onUpdateFibulaDentalImplantCylindersButton(self):
    """
    Callback to update fibula drill guides according to dental implants
    """
    self.logic.onUpdateFibulaDentalImplantsTimerTimeout()

  def onCreatePlateCurveButton(self):
    """
    Callback to create a plate curve
    """
    self.logic.createPlateCurve()

  def onCreateCustomPlateButton(self):
    """
    Callback to create a custom plate
    """
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
    self.fibulaLineInstructionsEventsObserversList = []
    self.mandibularCurveInstructionsEventsObserversList = []
    self.resectedMandibleAndObserver = []
    self.planeNodeAndObserver = []
    # self.mandibleCurveModifiedObserver = 0 # TODO: could be implemented on the future
    self.interCondylarBeamLineControlPointDefinedObserver = 0
    self.interCondylarBeamLineControlPointEndInteractionObserver = 0
    self.interCondylarBeamLineControlPointRemovedObserver = 0
    self.mandibleBridgeCurveControlPointDefinedObserver = 0
    self.mandibleBridgeCurveControlPointEndInteractionObserver = 0
    self.mandibleBridgeCurveControlPointRemovedObserver = 0
    self.miterBoxDirectionLineControlPointDefinedObserver = 0
    self.miterBoxDirectionLineControlPointEndInteractionObserver = 0
    self.miterBoxDirectionLineControlPointRemovedObserver = 0
    self.fibulaLineControlPointEndInteractionObserver = 0
    self.fibulaLineControlPointRemovedObserver = 0
    self.fibulaLineControlPointDefinedObserver = 0
    self.fibulaFiducialListControlPointDefinedObserver = 0
    self.fibulaFiducialListControlPointEndInteractionObserver = 0
    self.fibulaFiducialListControlPointRemovedObserver = 0
    self.mandibleFiducialListControlPointDefinedObserver = 0
    self.mandibleFiducialListControlPointEndInteractionObserver = 0
    self.mandibleFiducialListControlPointRemovedObserver = 0
    self.leftSideMandibleGuideBaseCurveControlPointDefinedObserver = 0
    self.leftSideMandibleGuideBaseCurveControlPointEndInteractionObserver = 0
    self.leftSideMandibleGuideBaseCurveControlPointRemovedObserver = 0
    self.rightSideMandibleGuideBaseCurveControlPointDefinedObserver = 0
    self.rightSideMandibleGuideBaseCurveControlPointEndInteractionObserver = 0
    self.rightSideMandibleGuideBaseCurveControlPointRemovedObserver = 0
    self.generateFibulaPlanesTimer = qt.QTimer()
    self.generateFibulaPlanesTimer.setInterval(300)
    self.generateFibulaPlanesTimer.setSingleShot(True)
    self.generateFibulaPlanesTimer.connect('timeout()', self.onGenerateFibulaPlanesTimerTimeout)
    self.updateFibuladentalImplantsTimer = qt.QTimer()
    self.updateFibuladentalImplantsTimer.setInterval(150)
    self.updateFibuladentalImplantsTimer.setSingleShot(True)
    self.updateFibuladentalImplantsTimer.connect('timeout()', self.onUpdateFibulaDentalImplantsTimerTimeout)

  def setDefaultParameters(self, parameterNode):
    """
    Initialize parameter node with default settings.
    """
    defaultParametersDict = readDefaultParameters()
    for parameterName, parameterValue in defaultParametersDict.items():
      valueFromSettings = rs(parameterName)
      if valueFromSettings is None:
        ws(parameterName, parameterValue)
        wp(parameterNode, parameterName, parameterValue)
      elif not parameterNode.GetParameter(parameterName):
        wp(parameterNode, parameterName, valueFromSettings)

  def restoreDefaultParameters(self):
    """
    Restore parameterNode and settings to default parameters from the defaultParameters.json
    """
    defaultParametersDict = readDefaultParameters()
    parameterNode = self.getParameterNode()
    for parameterName, parameterValue in defaultParametersDict.items():
      ws(parameterName, parameterValue)
      wp(parameterNode, parameterName, parameterValue)

  def overwriteDefaultParameters(self):
    """
    Overwrite default settings to current values on the parameterNode
    """
    defaultParametersDict = readDefaultParameters()
    parameterNode = self.getParameterNode()
    for parameterName in defaultParametersDict.keys():
      valueFromParameterNode = rp(parameterNode, parameterName)
      ws(parameterName, valueFromParameterNode)
  
  def overwriteParameter(self, parameterName):
    """
    Overwrite default setting to current value on the parameterNode
    """
    parameterNode = self.getParameterNode()
    valueFromParameterNode = rp(parameterNode, parameterName)
    ws(parameterName, valueFromParameterNode)

  @saveExecutedMethodWithTelemetry
  def prepareSendEmailOnWebBrowser(self, emailVariable, subjectVariable, bodyVariable, ccVariable="", bccVariable=""):
    parsedBodyVariable = bodyVariable.replace(" ", "%20").replace("\n", "%0D%0A")
    #
    prepareEmailString = (
      f'mailto:{emailVariable}?'
      f'subject={subjectVariable}&'
      f'body={parsedBodyVariable}'
    )
    #
    if ccVariable != "":
      prepareEmailString += f'&cc={ccVariable}'
    #
    if bccVariable != "":
      prepareEmailString += f'&bcc={bccVariable}'
    #
    prepareEmailUrl = qt.QUrl(prepareEmailString)
    #
    # Open email client
    qt.QDesktopServices.openUrl(prepareEmailUrl)
  
  @saveExecutedMethodWithTelemetry
  def openDocumentationOnWebBrowser(self):
    documentationUrl = qt.QUrl("https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner#table-of-contents")
    qt.QDesktopServices.openUrl(documentationUrl)
  
  @vtk.calldata_type(vtk.VTK_LONG)
  def onShNodeModified(self, caller, event, callData):
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    shItemIDModified = callData
    
    #if shNode.GetItemByName("Mandibular planes 2"):
    #  return

    validFolderIDs = [
      shNode.GetItemByName("Mandibular planes"),
      shNode.GetItemByName("Cut Bones"),
      shNode.GetItemByName("Transformed Fibula Pieces")
    ]

    if shItemIDModified in validFolderIDs:
      self.setPlanningInformativeText()
  
  def setPlanningInformativeText(self, sourceNode=None, event=None, callData=None):
    """
    Set informative text for the user during the planning
    """
    # abort until new BRP version supports it fully
    return

    if not USING_GUI:
      return
    
    parameterNode = self.getParameterNode()
    
    fibulaSegmentation = parameterNode.GetNodeReference("fibulaSegmentation")
    mandibularSegmentation = parameterNode.GetNodeReference("mandibularSegmentation")
    fibulaModel = self.getCurrentFibulaModel()
    mandibleModel = self.getCurrentMandibleModel()
    mandibularCurve = self.getMandibularCurve()
    fibulaLine = self.getFibulaLine()
    mandibleReconstructionModel = parameterNode.GetNodeReference("mandibleReconstructionModel")

    virtualPlanWasSuccessfulFlag = parameterNode.GetParameter("virtualPlanWasSuccessful") == "True"
    lockVSPChecked = parameterNode.GetParameter("lockVSP") == "True"
    virtualPlanFailedDueToCutGoesThroughMandibleTwiceChecked = (
      parameterNode.GetParameter("virtualPlanFailedDueToCutGoesThroughMandibleTwice") == "True"
    )
    
    numberOfMandiblePlanes = len(createListFromFolderName("Mandibular planes"))

    numberOfCutBones = len(createListFromFolderName("Cut Bones"))
    numberOfTransformedFibulaPieces = len(createListFromFolderName("Transformed Fibula Pieces"))
    numberOfCutBonesValid = numberOfCutBones == numberOfMandiblePlanes
    numberOfTransformedFibulaPiecesValid = numberOfTransformedFibulaPieces == (numberOfMandiblePlanes - 1)
    virtualPlanResultsExist = (numberOfCutBones >= 2) and (numberOfTransformedFibulaPieces >= 1)
    virtualPlanResultsAreValid = numberOfCutBonesValid and numberOfTransformedFibulaPiecesValid
    

    # I'm not sure if this variable is robust
    probablyNeedsFixCutGoesThroughTheMandibleTwice = False
    if numberOfCutBones >= 2:
      # numberOfComponentsOfResectedMandible is not a good measurement because there could be small floating 
      #   islands cut that change the count
      resectedMandibleModel = createListFromFolderName("Cut Bones")[-1]
      if resectedMandibleModel:
        if resectedMandibleModel.GetPolyData():
          if resectedMandibleModel.GetPolyData().GetNumberOfPoints() > 0:
            numberOfComponentsOfResectedMandible = countComponentsInPolyData(
              resectedMandibleModel.GetPolyData()
            )
            kindOfMandibleResection = parameterNode.GetParameter("kindOfMandibleResection")
            if kindOfMandibleResection == "Segmental Mandibulectomy":
              probablyNeedsFixCutGoesThroughTheMandibleTwice = numberOfComponentsOfResectedMandible > 4


    # conditions list
    instruction_loadTestData = not fibulaSegmentation and not mandibularSegmentation
    instruction_selectFibulaSegmentation = not fibulaSegmentation
    instruction_selectMandibularSegmentation = not mandibularSegmentation
    finishedSelectingSegmentations = fibulaSegmentation and mandibularSegmentation
    instruction_selectDonorLeg = finishedSelectingSegmentations and (not fibulaModel and not mandibleModel)
    instruction_createBoneModels = finishedSelectingSegmentations and (not fibulaModel and not mandibleModel)
    finishedCreatingBoneModels = fibulaModel and mandibleModel
    instruction_verifyMandibularCurvePoints = finishedCreatingBoneModels and (mandibularCurve.GetNumberOfControlPoints() < 2)
    instruction_verifyFibulaLinePoints = finishedCreatingBoneModels and (fibulaLine.GetNumberOfControlPoints() != 2)
    finishedVerifyingMandibularCurveAndFibulaLine = (
      finishedCreatingBoneModels and 
      (mandibularCurve.GetNumberOfControlPoints() >= 2) and 
      (fibulaLine.GetNumberOfControlPoints() == 2)
    )
    instruction_addMandiblePlanes = finishedVerifyingMandibularCurveAndFibulaLine and (numberOfMandiblePlanes < 2)
    finishedVirtualPlanComponentsCreation = (
      fibulaModel and 
      mandibleModel and 
      (mandibularCurve.GetNumberOfControlPoints() >= 2) and
      (fibulaLine.GetNumberOfControlPoints() == 2) and
      (numberOfMandiblePlanes >= 2)
    )
    instruction_createFirstPlan = finishedVirtualPlanComponentsCreation and (not virtualPlanResultsExist)
    instruction_virtualPlanFailed = (
      finishedVirtualPlanComponentsCreation and 
      virtualPlanResultsExist and
      (
        (not virtualPlanResultsAreValid) or (not virtualPlanWasSuccessfulFlag)
      )
    )
    instruction_updateVirtualPlan = (
      finishedVirtualPlanComponentsCreation and 
      virtualPlanResultsExist and
      virtualPlanResultsAreValid and
      virtualPlanWasSuccessfulFlag and
      (not lockVSPChecked)
    )
    finishedVirtualPlan = (
      finishedVirtualPlanComponentsCreation and 
      virtualPlanResultsExist and
      virtualPlanResultsAreValid and
      virtualPlanWasSuccessfulFlag
    )
    instruction_lockPlan = finishedVirtualPlan and not lockVSPChecked
    instruction_planLocked = finishedVirtualPlan and lockVSPChecked

    instruction_createNeoMandibleModel = (
      finishedVirtualPlan and
      (not lockVSPChecked)
    )
    instruction_neoMandibleModelSuccessful = (
      finishedVirtualPlan and
      (not lockVSPChecked) and
      mandibleReconstructionModel
    )

    instruction_fixCutGoesThroughMandibleTwice = (
      finishedVirtualPlan and
      (not lockVSPChecked) and
      (not virtualPlanFailedDueToCutGoesThroughMandibleTwiceChecked) and
      probablyNeedsFixCutGoesThroughTheMandibleTwice
    )

    instructionsDict = {
      "- Please click 'Load test case' if using BRP for the first time.\n": instruction_loadTestData,

      "- Please select the fibula segmentation.\n": instruction_selectFibulaSegmentation,

      "- Please select the mandibular segmentation.\n": instruction_selectMandibularSegmentation,
      
      "- Please select donor leg.\n": instruction_selectDonorLeg,

      "- Please click create bone models.\n": instruction_createBoneModels,
      
      "- Please verify the mandibular curve has at least 2 points.\n": instruction_verifyMandibularCurvePoints,
      
      "- Please verify the fibula line has 2 points.\n": instruction_verifyFibulaLinePoints,
      
      "- Please create at least 2 mandible planes.\n": instruction_addMandiblePlanes,
      
      "- Please move a mandibular plane or click on\n'update virtual plan' to continue with the workflow.\n": instruction_createFirstPlan,
      
      "- Plan failed, please click the reset button next to 'update virtual plan'.\n": instruction_virtualPlanFailed,
      
      "- Plan successful. Keep editing if desired. \n": instruction_updateVirtualPlan,
      
      "- Click on the lock button if finished to avoid accidental modifications of the plan.\n": instruction_lockPlan,

      "- Plan locked. Please unlock if you want to keep editing the plan.\n": instruction_planLocked,
      
      "- You can click 'Create neomandible' to get a 3D printable model and, optionally, " + 
      "you can add an intercondylar beam to it.\n": instruction_createNeoMandibleModel,

      "- Neomandible model created successfully. \n": instruction_neoMandibleModelSuccessful,

      "- Please use 'Fix cut goes through the mandible twice' if needed.\n": instruction_fixCutGoesThroughMandibleTwice
    }

    planningInformativeText = ""
    for instruction, condition in instructionsDict.items():
      if condition:
        planningInformativeText += instruction
        #break
    
    parameterNode.SetParameter(
      "planningInformativeText", planningInformativeText
    )
    return




    # consider using, they look very nice:
    slicer.modules.BoneReconstructionPlannerWidget.ui.mandibleCurvePlaceWidget.setStyleSheet("background-color:red;")
    slicer.modules.BoneReconstructionPlannerWidget.ui.mandibleCurvePlaceWidget.setStyleSheet("background-color:yellow;")
    slicer.modules.BoneReconstructionPlannerWidget.ui.mandibleCurvePlaceWidget.setStyleSheet("background-color:green;")
    slicer.modules.BoneReconstructionPlannerWidget.ui.reconstructionPlanningFrame.setStyleSheet("background-color:lightgreen;")
  
  def setNeomandibleVisibility(self, visibility):
    """
    Set neomandible visibility
    """
    if not USING_GUI:
      return
    
    parameterNode = self.getParameterNode()
    parameterNode.SetParameter("neomandibleVisible", str(visibility))
    
    mandibleReconstructionModel = parameterNode.GetNodeReference("mandibleReconstructionModel")
    
    if mandibleReconstructionModel is not None:
      mandibleReconstructionModel.GetDisplayNode().SetVisibility(visibility)

  def getMandibularCurve(self, startPlacementMode = False):
    parameterNode = self.getParameterNode()
    mandibularCurve = parameterNode.GetNodeReference("mandibleCurve")
    if mandibularCurve is None:
      mandibularCurve = slicer.mrmlScene.CreateNodeByClass("vtkMRMLMarkupsCurveNode")
      mandibularCurve.SetName("temp")
      slicer.mrmlScene.AddNode(mandibularCurve)
      slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(mandibularCurve)
      mandibularCurve.SetAttribute("isMandibleCurve","True")
      moveNodeToFolder(mandibularCurve, getFolder("BoneReconstructionPlanner"))
      mandibularCurve.SetName(slicer.mrmlScene.GetUniqueNameByString("mandibularCurve"))
      parameterNode.SetNodeReferenceID("mandibleCurve",mandibularCurve.GetID())

      displayNode = mandibularCurve.GetDisplayNode()
      displayNode.AddViewNodeID(slicer.MANDIBLE_VIEW_ID)
      self.setRedSliceForMarkupsDisplayNodes()

      # update instructions events
      instructionsEvents = [
        slicer.vtkMRMLMarkupsNode.PointPositionDefinedEvent, 
        slicer.vtkMRMLMarkupsNode.PointEndInteractionEvent, 
        slicer.vtkMRMLMarkupsNode.PointRemovedEvent
      ]
      self.mandibularCurveInstructionsEventsObserversList = []
      for event in instructionsEvents:
        observer = mandibularCurve.AddObserver(
          event,
          self.setPlanningInformativeText
        )
        self.mandibularCurveInstructionsEventsObserversList.append(observer)

    if startPlacementMode:
      #setup placement
      slicer.modules.markups.logic().SetActiveListID(mandibularCurve)
      interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
      interactionNode.SwitchToSinglePlaceMode()
    
    return mandibularCurve

  def getFibulaLine(self, startPlacementMode = False):
    parameterNode = self.getParameterNode()
    fibulaLine = parameterNode.GetNodeReference("fibulaLine")
    if fibulaLine is None:
      fibulaLine = slicer.mrmlScene.CreateNodeByClass("vtkMRMLMarkupsLineNode")
      fibulaLine.SetName("temp")
      slicer.mrmlScene.AddNode(fibulaLine)
      slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(fibulaLine)
      fibulaLine.SetAttribute("isFibulaLine","True")
      moveNodeToFolder(fibulaLine, getFolder("BoneReconstructionPlanner"))
      fibulaLine.SetName(slicer.mrmlScene.GetUniqueNameByString("fibulaLine"))
      parameterNode.SetNodeReferenceID("fibulaLine",fibulaLine.GetID())

      displayNode = fibulaLine.GetDisplayNode()
      displayNode.AddViewNodeID(slicer.FIBULA_VIEW_ID)
      self.setRedSliceForMarkupsDisplayNodes()

      #connections
      self.fibulaLineControlPointDefinedObserver = fibulaLine.AddObserver(
        slicer.vtkMRMLMarkupsNode.PointPositionDefinedEvent,
        self.onFibulaLinePointUpdated
      )
      self.fibulaLineControlPointEndInteractionObserver = fibulaLine.AddObserver(
        slicer.vtkMRMLMarkupsNode.PointEndInteractionEvent,
        self.onFibulaLinePointUpdated
      )
      self.fibulaLineControlPointRemovedObserver = fibulaLine.AddObserver(
        slicer.vtkMRMLMarkupsNode.PointRemovedEvent,
        self.onFibulaLinePointUpdated
      )

      # update instructions events
      instructionsEvents = [
        slicer.vtkMRMLMarkupsNode.PointPositionDefinedEvent, 
        slicer.vtkMRMLMarkupsNode.PointEndInteractionEvent, 
        slicer.vtkMRMLMarkupsNode.PointRemovedEvent
      ]
      self.fibulaLineInstructionsEventsObserversList = []
      for event in instructionsEvents:
        observer = fibulaLine.AddObserver(
          event,
          self.setPlanningInformativeText
        )
        self.fibulaLineInstructionsEventsObserversList.append(observer)

    if startPlacementMode:
      #setup placement
      slicer.modules.markups.logic().SetActiveListID(fibulaLine)
      interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
      interactionNode.SwitchToSinglePlaceMode()
    
    return fibulaLine

  def getInterCondylarBeamLine(self, startPlacementMode = False):
    parameterNode = self.getParameterNode()
    interCondylarBeamLine = parameterNode.GetNodeReference("interCondylarBeamLine")
    if interCondylarBeamLine is None:
      interCondylarBeamLine = slicer.mrmlScene.CreateNodeByClass("vtkMRMLMarkupsLineNode")
      interCondylarBeamLine.SetName("temp")
      slicer.mrmlScene.AddNode(interCondylarBeamLine)
      slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(interCondylarBeamLine)
      interCondylarBeamLine.SetAttribute("isInterCondylarBeamLine","True")
      moveNodeToFolder(interCondylarBeamLine, getFolder("BoneReconstructionPlanner"))
      interCondylarBeamLine.SetName(slicer.mrmlScene.GetUniqueNameByString("interCondylarBeamLine"))
      parameterNode.SetNodeReferenceID("interCondylarBeamLine",interCondylarBeamLine.GetID())

      displayNode = interCondylarBeamLine.GetDisplayNode()
      displayNode.AddViewNodeID(slicer.MANDIBLE_VIEW_ID)
      displayNode.SetOccludedVisibility(True)
      self.setRedSliceForMarkupsDisplayNodes()

      #conections
      self.interCondylarBeamLineControlPointDefinedObserver = interCondylarBeamLine.AddObserver(
        slicer.vtkMRMLMarkupsNode.PointPositionDefinedEvent,
        self.onInterCondylarLinePointUpdated
      )
      self.interCondylarBeamLineControlPointEndInteractionObserver = interCondylarBeamLine.AddObserver(
        slicer.vtkMRMLMarkupsNode.PointEndInteractionEvent,
        self.onInterCondylarLinePointUpdated
      )
      self.interCondylarBeamLineControlPointRemovedObserver = interCondylarBeamLine.AddObserver(
        slicer.vtkMRMLMarkupsNode.PointRemovedEvent,
        self.onInterCondylarLinePointUpdated
      )

    if startPlacementMode:
      #setup placement
      slicer.modules.markups.logic().SetActiveListID(interCondylarBeamLine)
      interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
      interactionNode.SwitchToSinglePlaceMode()
    
    return interCondylarBeamLine
  
  def getMiterBoxDirectionLine(self, startPlacementMode = False):
    parameterNode = self.getParameterNode()
    miterBoxDirectionLine = parameterNode.GetNodeReference("miterBoxDirectionLine")
    if miterBoxDirectionLine is None:
      miterBoxDirectionLine = slicer.mrmlScene.CreateNodeByClass("vtkMRMLMarkupsLineNode")
      miterBoxDirectionLine.SetName("temp")
      slicer.mrmlScene.AddNode(miterBoxDirectionLine)
      slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(miterBoxDirectionLine)
      miterBoxDirectionLine.SetAttribute("isMiterBoxDirectionLine","True")
      moveNodeToFolder(miterBoxDirectionLine, getFolder("BoneReconstructionPlanner"))
      miterBoxDirectionLine.SetName(slicer.mrmlScene.GetUniqueNameByString("miterBoxDirectionLine"))
      parameterNode.SetNodeReferenceID("miterBoxDirectionLine",miterBoxDirectionLine.GetID())

      displayNode = miterBoxDirectionLine.GetDisplayNode()
      displayNode.AddViewNodeID(slicer.FIBULA_VIEW_ID)
      displayNode.SetOccludedVisibility(True)
      self.setRedSliceForMarkupsDisplayNodes()

      #conections
      self.miterBoxDirectionLineControlPointDefinedObserver = miterBoxDirectionLine.AddObserver(
        slicer.vtkMRMLMarkupsNode.PointPositionDefinedEvent,
        self.onMiterBoxDirectionLinePointUpdated
      )
      self.miterBoxDirectionLineControlPointEndInteractionObserver = miterBoxDirectionLine.AddObserver(
        slicer.vtkMRMLMarkupsNode.PointEndInteractionEvent,
        self.onMiterBoxDirectionLinePointUpdated
      )
      self.miterBoxDirectionLineControlPointRemovedObserver = miterBoxDirectionLine.AddObserver(
        slicer.vtkMRMLMarkupsNode.PointRemovedEvent,
        self.onMiterBoxDirectionLinePointUpdated
      )

    if startPlacementMode:
      #setup placement
      slicer.modules.markups.logic().SetActiveListID(miterBoxDirectionLine)
      interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
      interactionNode.SwitchToSinglePlaceMode()
    
    return miterBoxDirectionLine
  
  def getFibulaFiducials(self, startPlacementMode = False):
    parameterNode = self.getParameterNode()
    fibulaFiducialList = parameterNode.GetNodeReference("fibulaFiducialList")
    if fibulaFiducialList is None:
      fibulaFiducialList = slicer.mrmlScene.CreateNodeByClass("vtkMRMLMarkupsFiducialNode")
      fibulaFiducialList.SetName("temp")
      slicer.mrmlScene.AddNode(fibulaFiducialList)
      slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(fibulaFiducialList)
      fibulaFiducialList.SetAttribute("isFibulaFiducials","True")
      moveNodeToFolder(fibulaFiducialList, getFolder("BoneReconstructionPlanner"))
      fibulaFiducialList.SetName(slicer.mrmlScene.GetUniqueNameByString("fibulaFiducialList"))
      parameterNode.SetNodeReferenceID("fibulaFiducialList",fibulaFiducialList.GetID())

      displayNode = fibulaFiducialList.GetDisplayNode()
      displayNode.AddViewNodeID(slicer.FIBULA_VIEW_ID)
      displayNode.SetOccludedVisibility(True)
      self.setRedSliceForMarkupsDisplayNodes()

      #conections
      self.fibulaFiducialListControlPointDefinedObserver = fibulaFiducialList.AddObserver(
        slicer.vtkMRMLMarkupsNode.PointPositionDefinedEvent,
        self.onFibulaFiducialsPointModified
      )
      self.fibulaFiducialListControlPointEndInteractionObserver = fibulaFiducialList.AddObserver(
        slicer.vtkMRMLMarkupsNode.PointEndInteractionEvent,
        self.onFibulaFiducialsPointModified
      )
      self.fibulaFiducialListControlPointRemovedObserver = fibulaFiducialList.AddObserver(
        slicer.vtkMRMLMarkupsNode.PointRemovedEvent,
        self.onFibulaFiducialsPointModified
      )

    if startPlacementMode:
      #setup placement
      slicer.modules.markups.logic().SetActiveListID(fibulaFiducialList)
      interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
      interactionNode.SwitchToPersistentPlaceMode()
    
    return fibulaFiducialList
  
  def getMandibleFiducials(self, startPlacementMode = False):
    parameterNode = self.getParameterNode()
    mandibleFiducialList = parameterNode.GetNodeReference("mandibleFiducialList")
    if mandibleFiducialList is None:
      mandibleFiducialList = slicer.mrmlScene.CreateNodeByClass("vtkMRMLMarkupsFiducialNode")
      mandibleFiducialList.SetName("temp")
      slicer.mrmlScene.AddNode(mandibleFiducialList)
      slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(mandibleFiducialList)
      mandibleFiducialList.SetAttribute("isMandibleFiducials","True")
      moveNodeToFolder(mandibleFiducialList, getFolder("BoneReconstructionPlanner"))
      mandibleFiducialList.SetName(slicer.mrmlScene.GetUniqueNameByString("mandibleFiducialList"))
      parameterNode.SetNodeReferenceID("mandibleFiducialList",mandibleFiducialList.GetID())

      displayNode = mandibleFiducialList.GetDisplayNode()
      displayNode.AddViewNodeID(slicer.MANDIBLE_VIEW_ID)
      displayNode.SetOccludedVisibility(True)
      self.setRedSliceForMarkupsDisplayNodes()

      #conections
      self.mandibleFiducialListControlPointDefinedObserver = mandibleFiducialList.AddObserver(
        slicer.vtkMRMLMarkupsNode.PointPositionDefinedEvent,
        self.onMandibleFiducialsPointModified
      )
      self.mandibleFiducialListControlPointEndInteractionObserver = mandibleFiducialList.AddObserver(
        slicer.vtkMRMLMarkupsNode.PointEndInteractionEvent,
        self.onMandibleFiducialsPointModified
      )
      self.mandibleFiducialListControlPointRemovedObserver = mandibleFiducialList.AddObserver(
        slicer.vtkMRMLMarkupsNode.PointRemovedEvent,
        self.onMandibleFiducialsPointModified
      )

    if startPlacementMode:
      #setup placement
      slicer.modules.markups.logic().SetActiveListID(mandibleFiducialList)
      interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
      interactionNode.SwitchToPersistentPlaceMode()
    
    return mandibleFiducialList
  
  def getMandibleBridgeCurve(self, startPlacementMode = False):
    parameterNode = self.getParameterNode()
    mandibleBridgeCurve = parameterNode.GetNodeReference("mandibleBridgeCurve")
    if mandibleBridgeCurve is None:
      mandibleBridgeCurve = slicer.mrmlScene.CreateNodeByClass("vtkMRMLMarkupsCurveNode")
      mandibleBridgeCurve.SetName("temp")
      slicer.mrmlScene.AddNode(mandibleBridgeCurve)
      slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(mandibleBridgeCurve)
      mandibleBridgeCurve.SetAttribute("isMandibleBridgeCurve","True")
      moveNodeToFolder(mandibleBridgeCurve, getFolder("BoneReconstructionPlanner"))
      mandibleBridgeCurve.SetName(slicer.mrmlScene.GetUniqueNameByString("mandibleBridgeCurve"))
      parameterNode.SetNodeReferenceID("mandibleBridgeCurve",mandibleBridgeCurve.GetID())

      displayNode = mandibleBridgeCurve.GetDisplayNode()
      displayNode.AddViewNodeID(slicer.MANDIBLE_VIEW_ID)
      displayNode.SetOccludedVisibility(True)
      self.setRedSliceForMarkupsDisplayNodes()

      #conections
      self.mandibleBridgeCurveControlPointDefinedObserver = mandibleBridgeCurve.AddObserver(
        slicer.vtkMRMLMarkupsNode.PointPositionDefinedEvent,
        self.onMandibleBridgeCurvePointUpdated
      )
      self.mandibleBridgeCurveControlPointEndInteractionObserver = mandibleBridgeCurve.AddObserver(
        slicer.vtkMRMLMarkupsNode.PointEndInteractionEvent,
        self.onMandibleBridgeCurvePointUpdated
      )
      self.mandibleBridgeCurveControlPointRemovedObserver = mandibleBridgeCurve.AddObserver(
        slicer.vtkMRMLMarkupsNode.PointRemovedEvent,
        self.onMandibleBridgeCurvePointUpdated
      )

    if startPlacementMode:
      #setup placement
      slicer.modules.markups.logic().SetActiveListID(mandibleBridgeCurve)
      interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
      interactionNode.SwitchToSinglePlaceMode()
    
    return mandibleBridgeCurve
  
  def getLeftSideMandibleGuideBaseCurve(self, startPlacementMode = False):
    parameterNode = self.getParameterNode()
    leftSideMandibleGuideBaseCurve = parameterNode.GetNodeReference("leftSideMandibleGuideBaseCurve")
    if leftSideMandibleGuideBaseCurve is None:
      leftSideMandibleGuideBaseCurve = slicer.mrmlScene.CreateNodeByClass("vtkMRMLMarkupsClosedCurveNode")
      leftSideMandibleGuideBaseCurve.SetName("temp")
      slicer.mrmlScene.AddNode(leftSideMandibleGuideBaseCurve)
      slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(leftSideMandibleGuideBaseCurve)
      leftSideMandibleGuideBaseCurve.SetAttribute("isLeftSideMandibleGuideBaseCurve","True")
      moveNodeToFolder(leftSideMandibleGuideBaseCurve, getFolder("BoneReconstructionPlanner"))
      leftSideMandibleGuideBaseCurve.SetName(slicer.mrmlScene.GetUniqueNameByString("leftSideMandibleGuideBaseCurve"))
      parameterNode.SetNodeReferenceID("leftSideMandibleGuideBaseCurve",leftSideMandibleGuideBaseCurve.GetID())

      displayNode = leftSideMandibleGuideBaseCurve.GetDisplayNode()
      displayNode.AddViewNodeID(slicer.MANDIBLE_VIEW_ID)
      displayNode.SetOccludedVisibility(True)
      self.setRedSliceForMarkupsDisplayNodes()

      #conections
      self.leftSideMandibleGuideBaseCurveControlPointDefinedObserver = leftSideMandibleGuideBaseCurve.AddObserver(
        slicer.vtkMRMLMarkupsNode.PointPositionDefinedEvent,
        self.onLeftSideMandibleGuideBaseCurvePointUpdated
      )
      self.leftSideMandibleGuideBaseCurveControlPointEndInteractionObserver = leftSideMandibleGuideBaseCurve.AddObserver(
        slicer.vtkMRMLMarkupsNode.PointEndInteractionEvent,
        self.onLeftSideMandibleGuideBaseCurvePointUpdated
      )
      self.leftSideMandibleGuideBaseCurveControlPointRemovedObserver = leftSideMandibleGuideBaseCurve.AddObserver(
        slicer.vtkMRMLMarkupsNode.PointRemovedEvent,
        self.onLeftSideMandibleGuideBaseCurvePointUpdated
      )

    if startPlacementMode:
      #setup placement
      slicer.modules.markups.logic().SetActiveListID(leftSideMandibleGuideBaseCurve)
      interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
      interactionNode.SwitchToSinglePlaceMode()
    
    return leftSideMandibleGuideBaseCurve

  def getRightSideMandibleGuideBaseCurve(self, startPlacementMode = False):
    parameterNode = self.getParameterNode()
    rightSideMandibleGuideBaseCurve = parameterNode.GetNodeReference("rightSideMandibleGuideBaseCurve")
    if rightSideMandibleGuideBaseCurve is None:
      rightSideMandibleGuideBaseCurve = slicer.mrmlScene.CreateNodeByClass("vtkMRMLMarkupsClosedCurveNode")
      rightSideMandibleGuideBaseCurve.SetName("temp")
      slicer.mrmlScene.AddNode(rightSideMandibleGuideBaseCurve)
      slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(rightSideMandibleGuideBaseCurve)
      rightSideMandibleGuideBaseCurve.SetAttribute("isRightSideMandibleGuideBaseCurve","True")
      moveNodeToFolder(rightSideMandibleGuideBaseCurve, getFolder("BoneReconstructionPlanner"))
      rightSideMandibleGuideBaseCurve.SetName(slicer.mrmlScene.GetUniqueNameByString("rightSideMandibleGuideBaseCurve"))
      parameterNode.SetNodeReferenceID("rightSideMandibleGuideBaseCurve",rightSideMandibleGuideBaseCurve.GetID())

      displayNode = rightSideMandibleGuideBaseCurve.GetDisplayNode()
      displayNode.AddViewNodeID(slicer.MANDIBLE_VIEW_ID)
      displayNode.SetOccludedVisibility(True)
      self.setRedSliceForMarkupsDisplayNodes()

      #conections
      self.rightSideMandibleGuideBaseCurveControlPointDefinedObserver = rightSideMandibleGuideBaseCurve.AddObserver(
        slicer.vtkMRMLMarkupsNode.PointPositionDefinedEvent,
        self.onRightSideMandibleGuideBaseCurvePointUpdated
      )
      self.rightSideMandibleGuideBaseCurveControlPointEndInteractionObserver = rightSideMandibleGuideBaseCurve.AddObserver(
        slicer.vtkMRMLMarkupsNode.PointEndInteractionEvent,
        self.onRightSideMandibleGuideBaseCurvePointUpdated
      )
      self.rightSideMandibleGuideBaseCurveControlPointRemovedObserver = rightSideMandibleGuideBaseCurve.AddObserver(
        slicer.vtkMRMLMarkupsNode.PointRemovedEvent,
        self.onRightSideMandibleGuideBaseCurvePointUpdated
      )

    if startPlacementMode:
      #setup placement
      slicer.modules.markups.logic().SetActiveListID(rightSideMandibleGuideBaseCurve)
      interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
      interactionNode.SwitchToSinglePlaceMode()
    
    return rightSideMandibleGuideBaseCurve

  def onMandibleBridgeCurvePointUpdated(self,sourceNode,event):
    parameterNode = self.getParameterNode()
    mandibleBridgeCurve = parameterNode.GetNodeReference("mandibleBridgeCurve")
    mandibleBridgeTube = parameterNode.GetNodeReference("mandibleBridgeTube")
    if mandibleBridgeCurve.GetNumberOfControlPoints() <= 1:
      if mandibleBridgeTube is not None:
        parameterNode.SetNodeReferenceID("mandibleBridgeTube", "")
        slicer.mrmlScene.RemoveNode(mandibleBridgeTube)
    else:
      self.updateMandibleBridgeTube()

  def updateMandibleBridgeTube(self):
    parameterNode = self.getParameterNode()
    mandibleBridgeCurve = self.getMandibleBridgeCurve()
    mandibleBridgeTube = parameterNode.GetNodeReference("mandibleBridgeTube")
    mandibleBridgeRadius = float(parameterNode.GetParameter("mandibleBridgeRadius_mm"))

    if mandibleBridgeCurve.GetNumberOfControlPoints() <= 1:
      return
    
    if mandibleBridgeTube is None:
      # create the placeholder model
      mandibleBridgeTube = slicer.mrmlScene.CreateNodeByClass("vtkMRMLModelNode")
      mandibleBridgeTube.SetName("temp")
      slicer.mrmlScene.AddNode(mandibleBridgeTube)
      mandibleBridgeTube.CreateDefaultDisplayNodes()
      parentFolder = getFolder("Mandible reconstruction")
      moveNodeToFolder(mandibleBridgeTube, parentFolder)
      mandibleBridgeTube.SetName(slicer.mrmlScene.GetUniqueNameByString("mandibleBridgeTube"))
      parameterNode.SetNodeReferenceID("mandibleBridgeTube",mandibleBridgeTube.GetID())

      mandibleBridgeTubeDisplayNode = mandibleBridgeTube.GetDisplayNode()
      mandibleBridgeTubeDisplayNode.SetVisibility2D(True)
      mandibleBridgeTubeDisplayNode.SetVisibility(True) # now make it visible
      mandibleBridgeTubeDisplayNode.AddViewNodeID(slicer.MANDIBLE_VIEW_ID)
      self.setRedSliceForModelsDisplayNodes()
      self.setRedSliceForMarkupsDisplayNodes()

    markupsToModel = slicer.modules.markupstomodel.logic()
    # see https://github.com/SlicerIGT/SlicerMarkupsToModel/blob/312cf9f8ccb84613e191a0a3f18cd3f865026aeb/MarkupsToModel/Logic/vtkSlicerMarkupsToModelLogic.h#L78-L85
    markupsToModel.UpdateOutputCurveModel( 
      mandibleBridgeCurve, mandibleBridgeTube, slicer.vtkMRMLMarkupsToModelNode.CardinalSpline, 
      False, mandibleBridgeRadius, 8, 5, True, 3, slicer.vtkMRMLMarkupsToModelNode.RawIndices, 
      None, slicer.vtkMRMLMarkupsToModelNode.MovingLeastSquares 
    )
  
  def onFibulaFiducialsPointModified(self,sourceNode,event):
    fibulaCylindersModelsList = createListFromFolderName("Fibula Cylinders Models")
    for i in range(len(fibulaCylindersModelsList)):
      fibulaCylindersModelsList[i].GetDisplayNode().SetVisibility(False)
    self.createCylindersFromFiducialListAndFibulaSurgicalGuideBase()

  def onMandibleFiducialsPointModified(self,sourceNode,event):
    mandibleCylindersModelsList = createListFromFolderName("Mandible Cylinders Models")
    for i in range(len(mandibleCylindersModelsList)):
      mandibleCylindersModelsList[i].GetDisplayNode().SetVisibility(False)
    self.createCylindersFromFiducialListAndMandibleSurgicalGuideBase()

  def onMiterBoxDirectionLinePointUpdated(self,sourceNode,event):
    miterBoxDirectionLine = self.getMiterBoxDirectionLine()
    if miterBoxDirectionLine.GetNumberOfControlPoints() == 2:
      self.createMiterBoxesFromFibulaPlanes()
  
  def interCondylarBeamSizeChange(self, positive = True):
    parameterNode = self.getParameterNode()
    interCondylarBeamBoxSize = float(parameterNode.GetParameter("interCondylarBeamBoxSize_mm"))
    interCondylarBeamBoxSizeStep = float(parameterNode.GetParameter("interCondylarBeamBoxSizeStep_mm"))

    if positive:
      interCondylarBeamBoxSize += interCondylarBeamBoxSizeStep
    elif interCondylarBeamBoxSize >= 2*interCondylarBeamBoxSizeStep:
      interCondylarBeamBoxSize -= interCondylarBeamBoxSizeStep

    parameterNode.SetParameter("interCondylarBeamBoxSize_mm", str(interCondylarBeamBoxSize))

    self.updateInterCondylarBeamBox()
  
  def installAISegmentations(self):
    try:
      mooseHelper = MOOSEHelper()
      mooseHelper.installAIDependenciesIfNeeded()

      dentalSegmentatorAIModelDir = os.path.join(os.path.dirname(__file__), 'Resources/ML')
      dentalSegmentatorHelper = DentalSegmentatorHelper(
        dentalSegmentatorAIModelDir
      )
      dentalSegmentatorHelper.installAIDependenciesIfNeeded()
    except Exception as e:
      logging.error("Error installing AI dependencies: " + str(e))
      if USING_GUI:
        qt.QMessageBox.critical(
          slicer.util.mainWindow(), 
          "Error installing AI dependencies", 
          "An error occurred while installing AI dependencies. Please do a complete restart of Slicer and try again."
        )
    else:
      parameterNode = self.getParameterNode()
      parameterNode.SetParameter("AISegmentationsInstalled", "True")
      self.overwriteParameter("AISegmentationsInstalled")
  
  def runHeadSegmentation(self):
    parameterNode = self.getParameterNode()
    headVolume = parameterNode.GetNodeReference("headCT")
    mandibularSegmentation = parameterNode.GetNodeReference("mandibularSegmentation")
    
    dentalSegmentatorAIModelDir = os.path.join(os.path.dirname(__file__), 'Resources/ML')

    dentalSegmentatorHelper = DentalSegmentatorHelper(
      dentalSegmentatorAIModelDir
    )
    dentalSegmentatorHelper.setVolumeNode(headVolume)
    dentalSegmentatorHelper.setSegmentationNode(mandibularSegmentation)
    dentalSegmentatorHelper.setParameter(
      "headCTCorticalBoneThreshold", 
      int(float(parameterNode.GetParameter("headCTCorticalBoneThreshold")))
    )

    # add ProgressDialog from helperFunctions below with all needed parameters
    progressDialog = slicer.util.createProgressDialog(
      windowTitle = "Running AI Workflow", 
      labelText = "Processing...", 
      value = 0, 
      maximum = 100
    )
    dentalSegmentatorHelper.doFullAIWorkflow()
    progressDialog.close()
    
    mandibularSegmentation = dentalSegmentatorHelper.getSegmentationNode()
    print("mandibularSegmentationName " + mandibularSegmentation.GetName())
    parameterNode.SetNodeReferenceID("mandibularSegmentation", mandibularSegmentation.GetID())
  
  def runLegsSegmentation(self):
    parameterNode = self.getParameterNode()
    legsVolume = parameterNode.GetNodeReference("legsCT")
    fibulaSegmentation = parameterNode.GetNodeReference("fibulaSegmentation")
    
    mooseHelper = MOOSEHelper()
    mooseHelper.setVolumeNode(legsVolume)
    mooseHelper.setSegmentationNode(fibulaSegmentation)
    mooseHelper.setParameter(
      "legsCTCorticalBoneThreshold", 
      int(float(parameterNode.GetParameter("legsCTCorticalBoneThreshold")))
    )

    # add ProgressDialog from helperFunctions below with all needed parameters
    progressDialog = slicer.util.createProgressDialog(
      windowTitle = "Running AI Workflow", 
      labelText = "Processing...", 
      value = 0, 
      maximum = 100
    )
    mooseHelper.doFullAIWorkflow()
    progressDialog.close()
    
    legsAISegmentation = mooseHelper.getSegmentationNode()
    print("legsAISegmentationName " + legsAISegmentation.GetName())
    parameterNode.SetNodeReferenceID("fibulaSegmentation", legsAISegmentation.GetID())

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
    parentFolder = getFolder("Mandibular planes")
    moveNodeToFolder(planeNode, parentFolder)
    planeNode.SetName(slicer.mrmlScene.GetUniqueNameByString("mandibularPlane"))
    planeNode.SetAttribute("isMandibularPlane","True")
    planeNode.SetSize(slicer.PLANE_SIDE_SIZE,slicer.PLANE_SIDE_SIZE)
    planeNode.SetPlaneType(slicer.vtkMRMLMarkupsPlaneNode.PlaneType3Points)

    aux = slicer.mrmlScene.GetNodeByID('vtkMRMLColorTableNodeFileMediumChartColors.txt')
    colorTable = aux.GetLookupTable()
    ind = colorIndex%8
    colorwithalpha = colorTable.GetTableValue(ind)
    color = [colorwithalpha[0],colorwithalpha[1],colorwithalpha[2]]

    #display node of the plane
    displayNode = planeNode.GetDisplayNode()
    displayNode.SetGlyphScale(slicer.PLANE_GLYPH_SCALE)
    displayNode.SetSelectedColor(color)
    displayNode.HandlesInteractiveOn()
    displayNode.RotationHandleVisibilityOn()
    displayNode.TranslationHandleVisibilityOn()
    displayNode.ScaleHandleVisibilityOff()

    mandibleViewNode = slicer.mrmlScene.GetSingletonNode(slicer.MANDIBLE_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
    displayNode.AddViewNodeID(mandibleViewNode.GetID())

    self.setRedSliceForMarkupsDisplayNodes()

    #conections
    self.planeNodeAndObserver = [
      planeNode,
      planeNode.AddObserver(slicer.vtkMRMLMarkupsNode.PointPositionDefinedEvent,self.onPlanePointAdded)
    ]

    #setup placement
    slicer.modules.markups.logic().SetActiveListID(planeNode)
    interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
    interactionNode.SwitchToSinglePlaceMode()
  
  def removeCutPlane(self):
    mandibularPlanesList = createListFromFolderName("Mandibular planes")

    if len(mandibularPlanesList) > 0:
      # remove the last plane
      planeNode = mandibularPlanesList[-1]
      slicer.mrmlScene.RemoveNode(planeNode)

  def onInterCondylarLinePointUpdated(self,sourceNode,event):
    parameterNode = self.getParameterNode()
    interCondylarBeamLine = parameterNode.GetNodeReference("interCondylarBeamLine")
    interCondylarBeamBox = parameterNode.GetNodeReference("interCondylarBeamBox")
    if interCondylarBeamLine.GetNumberOfControlPoints() <= 1:
      if interCondylarBeamBox is not None:
        parameterNode.SetNodeReferenceID("interCondylarBeamBox", "")
        slicer.mrmlScene.RemoveNode(interCondylarBeamBox)
    else:
      self.updateInterCondylarBeamBox()
  
  # def onInterCondylarLineTimerTimeout(self):
  #   self.updateInterCondylarBeamBox()

  def updateInterCondylarBeamBox(self):
    parameterNode = self.getParameterNode()
    interCondylarBeamLine = parameterNode.GetNodeReference("interCondylarBeamLine")
    interCondylarBeamBox = parameterNode.GetNodeReference("interCondylarBeamBox")
    interCondylarBeamBoxSize = float(parameterNode.GetParameter("interCondylarBeamBoxSize_mm"))

    if interCondylarBeamLine.GetNumberOfControlPoints() != 2:
      return

    if interCondylarBeamBox is None:
      # create the placeholder model
      interCondylarBeamBox = slicer.mrmlScene.CreateNodeByClass("vtkMRMLModelNode")
      interCondylarBeamBox.SetName("temp")
      slicer.mrmlScene.AddNode(interCondylarBeamBox)
      interCondylarBeamBox.CreateDefaultDisplayNodes()
      parentFolder = getFolder("Mandible reconstruction")
      moveNodeToFolder(interCondylarBeamBox, parentFolder)
      interCondylarBeamBox.SetName(slicer.mrmlScene.GetUniqueNameByString("interCondylarBeamBox"))
      parameterNode.SetNodeReferenceID("interCondylarBeamBox",interCondylarBeamBox.GetID())

      interCondylarBeamBoxDisplayNode = interCondylarBeamBox.GetDisplayNode()
      interCondylarBeamBoxDisplayNode.SetVisibility2D(True)
      interCondylarBeamBoxDisplayNode.SetVisibility(True) # now make it visible
      interCondylarBeamBoxDisplayNode.AddViewNodeID(slicer.MANDIBLE_VIEW_ID)
      self.setRedSliceForModelsDisplayNodes()
      self.setRedSliceForMarkupsDisplayNodes()

    markupsToModel = slicer.modules.markupstomodel.logic()
    # see https://github.com/SlicerIGT/SlicerMarkupsToModel/blob/312cf9f8ccb84613e191a0a3f18cd3f865026aeb/MarkupsToModel/Logic/vtkSlicerMarkupsToModelLogic.h#L78-L85
    markupsToModel.UpdateOutputCurveModel( 
      interCondylarBeamLine, interCondylarBeamBox, slicer.vtkMRMLMarkupsToModelNode.CardinalSpline, 
      False, interCondylarBeamBoxSize/2, 4, 5, True, 3, slicer.vtkMRMLMarkupsToModelNode.RawIndices, 
      None, slicer.vtkMRMLMarkupsToModelNode.MovingLeastSquares 
    )

  def onFibulaLinePointUpdated(self,sourceNode,event):
    fibulaLine = self.getFibulaLine()
    if fibulaLine.GetNumberOfControlPoints() == 2:
      self.centerFibulaLine()
  
  def onLeftSideMandibleGuideBaseCurvePointUpdated(self,sourceNode=None,event=None):
    parameterNode = self.getParameterNode()
    leftSideMandibleGuideBaseCurve = self.getLeftSideMandibleGuideBaseCurve()
    leftSideMandibleGuideBaseModel = parameterNode.GetNodeReference("leftSideMandibleGuideBaseModel")
    if leftSideMandibleGuideBaseCurve.GetNumberOfControlPoints() < 3:
      if leftSideMandibleGuideBaseModel is not None:
        parameterNode.SetNodeReferenceID("leftSideMandibleGuideBaseModel", "")
        slicer.mrmlScene.RemoveNode(leftSideMandibleGuideBaseModel)
        self.updateBothMandibleGuideBaseModels()
    else:
      self.updateLeftSideMandibleGuideBaseModel()

  def onRightSideMandibleGuideBaseCurvePointUpdated(self,sourceNode=None,event=None):
    parameterNode = self.getParameterNode()
    rightSideMandibleGuideBaseCurve = self.getRightSideMandibleGuideBaseCurve()
    rightSideMandibleGuideBaseModel = parameterNode.GetNodeReference("rightSideMandibleGuideBaseModel")
    if rightSideMandibleGuideBaseCurve.GetNumberOfControlPoints() < 3:
      if rightSideMandibleGuideBaseModel is not None:
        parameterNode.SetNodeReferenceID("rightSideMandibleGuideBaseModel", "")
        slicer.mrmlScene.RemoveNode(rightSideMandibleGuideBaseModel)
        self.updateBothMandibleGuideBaseModels()
    else:
      self.updateRightSideMandibleGuideBaseModel()

  def updateLeftSideMandibleGuideBaseModel(self):
    parameterNode = self.getParameterNode()
    leftSideMandibleGuideBaseCurve = self.getLeftSideMandibleGuideBaseCurve()
    mandibleModelNode = parameterNode.GetNodeReference("mandibleModelNode")
    mandibleGuidebaseThickness = float(parameterNode.GetParameter("mandibleGuidebaseThickness_mm"))

    leftSideMandibleGuideBaseModel = parameterNode.GetNodeReference("leftSideMandibleGuideBaseModel")
    if leftSideMandibleGuideBaseModel is None:
      leftSideMandibleGuideBaseModel = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode")
      leftSideMandibleGuideBaseModel.SetName(slicer.mrmlScene.GetUniqueNameByString("leftSideMandibleGuideBaseModel"))
      leftSideMandibleGuideBaseModel.CreateDefaultDisplayNodes()
      parameterNode.SetNodeReferenceID("leftSideMandibleGuideBaseModel", leftSideMandibleGuideBaseModel.GetID())
      mandibleViewNode = slicer.mrmlScene.GetSingletonNode(slicer.MANDIBLE_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
      leftSideMandibleGuideBaseModel.GetDisplayNode().AddViewNodeID(mandibleViewNode.GetID())
      leftSideMandibleGuideBaseModel.GetDisplayNode().SetVisibility2D(True)
      moveNodeToFolder(leftSideMandibleGuideBaseModel, getFolder("BoneReconstructionPlanner"))
      parameterNode.SetNodeReferenceID("leftSideMandibleGuideBaseModel", leftSideMandibleGuideBaseModel.GetID())

    # Extract the patch of the mandible surface enclosed by the closed curve using a dynamic modeler Curve cut
    curveCutModel = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", "temporalLeftSideMandibleGuideBaseCurveCutModel")
    curveCutModel.CreateDefaultDisplayNodes()
    curveCutModel.GetDisplayNode().SetVisibility(False)

    dynamicModelerNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLDynamicModelerNode")
    dynamicModelerNode.SetToolName("Curve cut")
    dynamicModelerNode.SetNodeReferenceID("CurveCut.InputModel", mandibleModelNode.GetID())
    dynamicModelerNode.SetNodeReferenceID("CurveCut.InputCurve", leftSideMandibleGuideBaseCurve.GetID())
    dynamicModelerNode.SetNodeReferenceID("CurveCut.OutputInside", curveCutModel.GetID())
    dynamicModelerNode.SetAttribute("CurveCut.StraightCut", "1")
    slicer.modules.dynamicmodeler.logic().RunDynamicModelerTool(dynamicModelerNode)

    curveCutPolyData = curveCutModel.GetPolyData()
    if curveCutPolyData is None or curveCutPolyData.GetNumberOfPoints() == 0:
      slicer.mrmlScene.RemoveNode(dynamicModelerNode)
      slicer.mrmlScene.RemoveNode(curveCutModel)
      return

    # Compute the average normal of the curve-cut patch
    curveCutModel.SetAndObservePolyData(calculateNormals(curveCutModel.GetPolyData()))
    normalsArray = slicer.util.arrayFromModelPointData(curveCutModel, 'Normals')
    averageNormal = np.mean(normalsArray, axis=0)
    averageNormal = averageNormal/np.linalg.norm(averageNormal)

    # Force the extrusion to point outward (away from the mandible), not into the bone.
    # AutoOrientNormals is unreliable on open patches, so the sign of the averaged normal
    # cannot be trusted; determine the outward direction geometrically instead.
    outwardDirection = getCentroid(curveCutModel) - getCentroid(mandibleModelNode)
    if np.dot(averageNormal, outwardDirection) < 0:
      averageNormal = -averageNormal

    # Extrude the patch along the average normal to give it the requested thickness
    extrudeFilter = vtk.vtkLinearExtrusionFilter()
    extrudeFilter.SetInputData(curveCutModel.GetPolyData())
    extrudeFilter.SetExtrusionTypeToVectorExtrusion()
    extrudeFilter.SetVector(averageNormal * mandibleGuidebaseThickness)
    extrudeFilter.CappingOn()
    extrudeFilter.Update()

    leftSideMandibleGuideBaseModel.SetAndObservePolyData(calculateNormals(extrudeFilter.GetOutput()))

    slicer.mrmlScene.RemoveNode(dynamicModelerNode)
    slicer.mrmlScene.RemoveNode(curveCutModel)

    self.updateBothMandibleGuideBaseModels()

  def updateRightSideMandibleGuideBaseModel(self):
    parameterNode = self.getParameterNode()
    rightSideMandibleGuideBaseCurve = self.getRightSideMandibleGuideBaseCurve()
    mandibleModelNode = parameterNode.GetNodeReference("mandibleModelNode")
    mandibleGuidebaseThickness = float(parameterNode.GetParameter("mandibleGuidebaseThickness_mm"))

    rightSideMandibleGuideBaseModel = parameterNode.GetNodeReference("rightSideMandibleGuideBaseModel")
    if rightSideMandibleGuideBaseModel is None:
      rightSideMandibleGuideBaseModel = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode")
      rightSideMandibleGuideBaseModel.SetName(slicer.mrmlScene.GetUniqueNameByString("rightSideMandibleGuideBaseModel"))
      rightSideMandibleGuideBaseModel.CreateDefaultDisplayNodes()
      parameterNode.SetNodeReferenceID("rightSideMandibleGuideBaseModel", rightSideMandibleGuideBaseModel.GetID())
      mandibleViewNode = slicer.mrmlScene.GetSingletonNode(slicer.MANDIBLE_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
      rightSideMandibleGuideBaseModel.GetDisplayNode().AddViewNodeID(mandibleViewNode.GetID())
      rightSideMandibleGuideBaseModel.GetDisplayNode().SetVisibility2D(True)
      moveNodeToFolder(rightSideMandibleGuideBaseModel, getFolder("BoneReconstructionPlanner"))
      parameterNode.SetNodeReferenceID("rightSideMandibleGuideBaseModel", rightSideMandibleGuideBaseModel.GetID())

    # Extract the patch of the mandible surface enclosed by the closed curve using a dynamic modeler Curve cut
    curveCutModel = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", "temporalRightSideMandibleGuideBaseCurveCutModel")
    curveCutModel.CreateDefaultDisplayNodes()
    curveCutModel.GetDisplayNode().SetVisibility(False)

    dynamicModelerNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLDynamicModelerNode")
    dynamicModelerNode.SetToolName("Curve cut")
    dynamicModelerNode.SetNodeReferenceID("CurveCut.InputModel", mandibleModelNode.GetID())
    dynamicModelerNode.SetNodeReferenceID("CurveCut.InputCurve", rightSideMandibleGuideBaseCurve.GetID())
    dynamicModelerNode.SetNodeReferenceID("CurveCut.OutputInside", curveCutModel.GetID())
    dynamicModelerNode.SetAttribute("CurveCut.StraightCut", "1")
    slicer.modules.dynamicmodeler.logic().RunDynamicModelerTool(dynamicModelerNode)

    curveCutPolyData = curveCutModel.GetPolyData()
    if curveCutPolyData is None or curveCutPolyData.GetNumberOfPoints() == 0:
      slicer.mrmlScene.RemoveNode(dynamicModelerNode)
      slicer.mrmlScene.RemoveNode(curveCutModel)
      return

    # Compute the average normal of the curve-cut patch
    curveCutModel.SetAndObservePolyData(calculateNormals(curveCutModel.GetPolyData()))
    normalsArray = slicer.util.arrayFromModelPointData(curveCutModel, 'Normals')
    averageNormal = np.mean(normalsArray, axis=0)
    averageNormal = averageNormal/np.linalg.norm(averageNormal)

    # Force the extrusion to point outward (away from the mandible), not into the bone.
    # AutoOrientNormals is unreliable on open patches, so the sign of the averaged normal
    # cannot be trusted; determine the outward direction geometrically instead.
    outwardDirection = getCentroid(curveCutModel) - getCentroid(mandibleModelNode)
    if np.dot(averageNormal, outwardDirection) < 0:
      averageNormal = -averageNormal

    # Extrude the patch along the average normal to give it the requested thickness
    extrudeFilter = vtk.vtkLinearExtrusionFilter()
    extrudeFilter.SetInputData(curveCutModel.GetPolyData())
    extrudeFilter.SetExtrusionTypeToVectorExtrusion()
    extrudeFilter.SetVector(averageNormal * mandibleGuidebaseThickness)
    extrudeFilter.CappingOn()
    extrudeFilter.Update()

    rightSideMandibleGuideBaseModel.SetAndObservePolyData(calculateNormals(extrudeFilter.GetOutput()))

    slicer.mrmlScene.RemoveNode(dynamicModelerNode)
    slicer.mrmlScene.RemoveNode(curveCutModel)

    self.updateBothMandibleGuideBaseModels()

  def updateBothMandibleGuideBaseModels(self):
    # append both left and right guide base models into a single model to be used for boolean operations when creating the surgical guide
    parameterNode = self.getParameterNode()
    leftSideMandibleGuideBaseModel = parameterNode.GetNodeReference("leftSideMandibleGuideBaseModel")
    rightSideMandibleGuideBaseModel = parameterNode.GetNodeReference("rightSideMandibleGuideBaseModel")

    if leftSideMandibleGuideBaseModel is None and rightSideMandibleGuideBaseModel is None:
      # No guide base sides remain, so remove the combined model entirely instead of
      # leaving an empty node behind (an empty model would also break later boolean operations).
      bothSidesMandibleGuideBaseModel = parameterNode.GetNodeReference("bothSidesMandibleGuideBaseModel")
      if bothSidesMandibleGuideBaseModel is not None:
        parameterNode.SetNodeReferenceID("bothSidesMandibleGuideBaseModel", "")
        slicer.mrmlScene.RemoveNode(bothSidesMandibleGuideBaseModel)
      return

    appendFilter = vtk.vtkAppendPolyData()
    
    if leftSideMandibleGuideBaseModel is not None:
      appendFilter.AddInputData(leftSideMandibleGuideBaseModel.GetPolyData())
      leftSideMandibleGuideBaseModel.GetDisplayNode().SetVisibility(False)
    
    if rightSideMandibleGuideBaseModel is not None:
      appendFilter.AddInputData(rightSideMandibleGuideBaseModel.GetPolyData())
      rightSideMandibleGuideBaseModel.GetDisplayNode().SetVisibility(False)
    
    appendFilter.Update()

    combinedPolyData = appendFilter.GetOutput()

    # clean the combined polydata to avoid issues in later boolean operations
    cleanFilter = vtk.vtkCleanPolyData()
    cleanFilter.SetInputData(combinedPolyData)
    cleanFilter.Update()

    combinedCleanedPolyData = cleanFilter.GetOutput()

    finalPolyData = calculateNormals(combinedCleanedPolyData)

    bothSidesMandibleGuideBaseModel = parameterNode.GetNodeReference("bothSidesMandibleGuideBaseModel")
    if bothSidesMandibleGuideBaseModel is None:
      # create the placeholder model
      bothSidesMandibleGuideBaseModel = slicer.mrmlScene.CreateNodeByClass("vtkMRMLModelNode")
      bothSidesMandibleGuideBaseModel.SetName("temp")
      slicer.mrmlScene.AddNode(bothSidesMandibleGuideBaseModel)
      bothSidesMandibleGuideBaseModel.CreateDefaultDisplayNodes()
      parentFolder = getFolder("Mandible reconstruction")
      moveNodeToFolder(bothSidesMandibleGuideBaseModel, parentFolder)
      bothSidesMandibleGuideBaseModel.SetName(slicer.mrmlScene.GetUniqueNameByString("bothSidesMandibleGuideBaseModel"))
      parameterNode.SetNodeReferenceID("bothSidesMandibleGuideBaseModel", bothSidesMandibleGuideBaseModel.GetID())

      bothSidesMandibleGuideBaseModelDisplayNode = bothSidesMandibleGuideBaseModel.GetDisplayNode()
      bothSidesMandibleGuideBaseModelDisplayNode.SetVisibility2D(True)
      bothSidesMandibleGuideBaseModelDisplayNode.SetVisibility(True) # now make it visible
      bothSidesMandibleGuideBaseModelDisplayNode.AddViewNodeID(slicer.MANDIBLE_VIEW_ID)
      self.setRedSliceForModelsDisplayNodes()
      self.setRedSliceForMarkupsDisplayNodes()
    
    bothSidesMandibleGuideBaseModel.SetAndObservePolyData(finalPolyData)
  
  def onPlanePointAdded(self,sourceNode,event):
    parameterNode = self.getParameterNode()
    mandibleCurve = parameterNode.GetNodeReference("mandibleCurve")
    if mandibleCurve.GetNumberOfControlPoints() < 2:
      interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
      interactionNode.SwitchToViewTransformMode()
      slicer.mrmlScene.RemoveNode(sourceNode)
      slicer.util.errorDisplay("Did you draw the mandibular curve before adding the planes? If not, please draw it first.")
      return

    mandibularPlanesList = createListFromFolderName("Mandibular planes")

    temporalOrigin = [0,0,0]
    sourceNode.GetNthControlPointPosition(0,temporalOrigin)
    
    self.setupMandiblePlaneStraightOverMandibleCurve(sourceNode,temporalOrigin, mandibleCurve)

    displayNode = sourceNode.GetDisplayNode()
    displayNode.HandlesInteractiveOn()
    for i in range(3):
      sourceNode.SetNthControlPointVisibility(i,False)
    observer = sourceNode.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent,self.onPlaneModifiedSetTimer)
    self.mandiblePlaneObserversAndNodeIDList.append([observer,sourceNode.GetID()])

    self.reorderMandiblePlanes()
  
  def onPlaneModifiedSetTimer(self,sourceNode,event):
    parameterNode = self.getParameterNode()
    updateOnMandiblePlanesMovementChecked = parameterNode.GetParameter("updateOnMandiblePlanesMovement") == "True"
    makeAllMandiblePlanesRotateTogetherChecked = parameterNode.GetParameter("makeAllMandiblePlanesRotateTogether") == "True"
    
    if makeAllMandiblePlanesRotateTogetherChecked and sourceNode != None:
      parameterNode.SetNodeReferenceID("mandiblePlaneOfRotation", sourceNode.GetID())

    if updateOnMandiblePlanesMovementChecked:
      self.generateFibulaPlanesTimer.start()

  @saveExecutedMethodWithTelemetry
  def onGenerateFibulaPlanesTimerTimeout(self):
    parameterNode = self.getParameterNode()
    parameterNode.SetParameter("virtualPlanWasSuccessful", str(False))
    parameterNode.SetParameter("currentlyProcessing", str(True))
    lockVSPChecked = parameterNode.GetParameter("lockVSP") == "True"
    if lockVSPChecked:
      logging.info('VSP updates are locked. Please set "lockVSP" parameter to "False".')
      parameterNode.SetParameter("currentlyProcessing", str(False))
      return
    
    import time
    startTime = time.time()
    logging.info('Processing started')

    mandibularPlanesList = createListFromFolderName("Mandibular planes")

    parameterNode = self.getParameterNode()
    mandiblePlanesPositioningForMaximumBoneContactChecked = parameterNode.GetParameter("mandiblePlanesPositioningForMaximumBoneContact") == "True"
    makeAllMandiblePlanesRotateTogetherChecked = parameterNode.GetParameter("makeAllMandiblePlanesRotateTogether") == "True"
    mandiblePlaneOfRotation = parameterNode.GetNodeReference("mandiblePlaneOfRotation")
    fibulaLine = parameterNode.GetNodeReference("fibulaLine")

    if len(mandibularPlanesList) == 0:
      stopTime = time.time()
      logging.info('Processing completed in {0:.2f} seconds\n'.format(stopTime-startTime))
      parameterNode.SetParameter("currentlyProcessing", str(False))
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

    
    parameterNode.SetParameter("miterBoxesNeedUpdate", str(True))
    parameterNode.SetParameter("sawBoxesNeedUpdate", str(True))
    parameterNode.SetParameter("virtualPlanWasSuccessful", str(True))

    stopTime = time.time()
    logging.info('Processing completed in {0:.2f} seconds\n'.format(stopTime-startTime))
    parameterNode.SetParameter("currentlyProcessing", str(False))

  def transformMandiblePlanesZRotationToBeTheSameAsInputPlane(self,mandiblePlaneOfRotation):
    mandibularPlanesList = createListFromFolderName("Mandibular planes")
    mandiblePlanesTransformsFolder = getFolder("Mandible Planes Transforms")

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
        
        moveNodeToFolder(transformNode, mandiblePlanesTransformsFolder)
      
    removeFolder(mandiblePlanesTransformsFolder)

  def setInteractiveHandlesVisibilityOfMarkups(self,markupsList,visibility):
    for i in range(len(markupsList)):
      displayNode = markupsList[i].GetDisplayNode()
      if visibility:
        displayNode.HandlesInteractiveOn()
      else:
        displayNode.HandlesInteractiveOff()

  def setMarkupsListLocked(self,markupsList,locked):
    for i in range(len(markupsList)):
      if markupsList[i] is not None:
        markupsList[i].SetLocked(locked)
  
  def addMandiblePlaneObservers(self):
    mandibularPlanesList = createListFromFolderName("Mandibular planes")

    for i in range(len(mandibularPlanesList)):
      if len(self.planeNodeAndObserver) != 0:
        if (self.planeNodeAndObserver[0] == mandibularPlanesList[i]):
          continue
      observer = mandibularPlanesList[i].AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent,self.onPlaneModifiedSetTimer)
      self.mandiblePlaneObserversAndNodeIDList.append([observer,mandibularPlanesList[i].GetID()])

  def removeMandiblePlaneObservers(self):
    if len(self.mandiblePlaneObserversAndNodeIDList) == 0:
      return

    for i in range(len(self.mandiblePlaneObserversAndNodeIDList)):
      mandiblePlane = slicer.mrmlScene.GetNodeByID(self.mandiblePlaneObserversAndNodeIDList[i][1])
      mandiblePlane.RemoveObserver(self.mandiblePlaneObserversAndNodeIDList[i][0])
    self.mandiblePlaneObserversAndNodeIDList = []

  def addSawBoxPlaneObservers(self):
    sawBoxesPlanesList = createListFromFolderName("sawBoxes Planes")
    sawBoxesTransformsList = createListFromFolderName("sawBoxes Transforms")

    for i in range(len(sawBoxesPlanesList)):
      observer = sawBoxesPlanesList[i].AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent,self.onSawBoxPlaneMoved)
      self.sawBoxPlaneObserversPlaneNodeIDAndTransformIDList.append([observer,sawBoxesPlanesList[i].GetID(),sawBoxesTransformsList[i].GetID()])

  def removeSawBoxPlaneObservers(self):
    sawBoxesPlanesList = createListFromFolderName("sawBoxes Planes")
 
    if len(self.sawBoxPlaneObserversPlaneNodeIDAndTransformIDList) == 0:
      return

    for i in range(len(sawBoxesPlanesList)):
      sawBoxPlane = slicer.mrmlScene.GetNodeByID(self.sawBoxPlaneObserversPlaneNodeIDAndTransformIDList[i][1])
      sawBoxPlane.RemoveObserver(self.sawBoxPlaneObserversPlaneNodeIDAndTransformIDList[i][0])
    self.sawBoxPlaneObserversPlaneNodeIDAndTransformIDList = []

  def addDentalImplantsPlaneObservers(self):
    dentalImplantsPlanesList = createListFromFolderName("dentalImplants Planes")
    dentalImplantsCylindersTransformsList = createListFromFolderName("Dental Implants Cylinders Transforms")

    for i in range(len(dentalImplantsPlanesList)):
      observer = dentalImplantsPlanesList[i].AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent,self.onDentalImplantPlaneMoved)
      self.dentalImplantPlaneObserversPlaneNodeIDAndTransformIDList.append([observer,dentalImplantsPlanesList[i].GetID(),dentalImplantsCylindersTransformsList[i].GetID()])

  def removeDentalImplantsPlaneObservers(self):
    dentalImplantsPlanesList = createListFromFolderName("dentalImplants Planes")
 
    if len(self.dentalImplantPlaneObserversPlaneNodeIDAndTransformIDList) == 0:
      return

    for i in range(len(dentalImplantsPlanesList)):
      dentalImplantsPlane = slicer.mrmlScene.GetNodeByID(self.dentalImplantPlaneObserversPlaneNodeIDAndTransformIDList[i][1])
      dentalImplantsPlane.RemoveObserver(self.dentalImplantPlaneObserversPlaneNodeIDAndTransformIDList[i][0])
    self.dentalImplantPlaneObserversPlaneNodeIDAndTransformIDList = []

  def transformFibulaPlanes(self):
    parameterNode = self.getParameterNode()
    fibulaLine = parameterNode.GetNodeReference("fibulaLine")
    initialSpace = float(parameterNode.GetParameter("initialSpace_mm"))
    additionalBetweenSpaceOfFibulaPlanes = float(parameterNode.GetParameter("additionalBetweenSpaceOfFibulaPlanes_mm"))
    rightSideLegIsDonor = parameterNode.GetParameter("donorLeg") == "Right"
    useMoreExactVersionOfPositioningAlgorithmChecked = parameterNode.GetParameter("useMoreExactVersionOfPositioningAlgorithm") == "True"
    fibulaModelNode = parameterNode.GetNodeReference("fibulaModelNode")
    planeList = createListFromFolderName("Mandibular planes")
    
    fibulaPlanesList = createListFromFolderName("Fibula planes")
    
    #Delete old fibulaPlanesTransforms
    mandible2FibulaTransformsFolder = getFolder("Mandible2Fibula transforms", reset = True)
    
    #Improve code readability by deleting if-else block that avoided recalculation if mandiblePlane rotated
    #Create fibula axis:
    fibulaX, fibulaY, fibulaZ, fibulaOrigin = self.createFibulaAxisFromFibulaLineAndRightSideLegChecked(fibulaLine,rightSideLegIsDonor) 
    
    #NewPlanes position and distance
    self.fibulaPlanesPositionA = []
    self.fibulaPlanesPositionB = []
    boneSegmentsDistance = []

    #Set up transform for intersections to measure betweenSpace
    intersectionsFolder = getFolder("Intersections")

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

    moveNodeToFolder(fibulaToRASRotationTransformNode, intersectionsFolder)

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
      fibulaX, fibulaY, fibulaZ, fibulaOrigin = self.createFibulaAxisFromFibulaLineAndRightSideLegChecked(fibulaLine,rightSideLegIsDonor) 
      
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
        moveNodeToFolder(intersectionModelB, intersectionsFolder)
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
        moveNodeToFolder(intersectionModelA, intersectionsFolder)
        intersectionsList[j].SetAndObserveTransformNodeID(fibulaToRASRotationTransformNode.GetID())
        intersectionsList[j].HardenTransform()
        j += 1

        intersectionsList[j-2].GetBounds(boundsB)
        intersectionsList[(j-2)+1].GetBounds(boundsA)

        #calculate how much each FibulaPlaneA should be translated so that it doesn't intersect with fibulaPlaneB
        zBSup = boundsB[5]
        zAInf = boundsA[4]
        deltaZ = zBSup - zAInf

        self.fibulaPlanesPositionA.append(self.fibulaPlanesPositionB[i-1] + fibulaZ*(deltaZ + additionalBetweenSpaceOfFibulaPlanes))
        self.fibulaPlanesPositionB.append(self.fibulaPlanesPositionA[i] + boneSegmentsDistance[i]*fibulaZ)

        if i!=(len(planeList)-2):
          afterMandibleToWorldChangeOfFrameMatrix = self.getAxes1ToWorldChangeOfFrameMatrix(mandibleAxisX, mandibleAxisY, mandibleAxisZ, mandiblePlane1Origin)
          afterFibulaToWorldChangeOfFrameMatrix = self.getAxes1ToWorldChangeOfFrameMatrix(fibulaX, fibulaY, fibulaZ, self.fibulaPlanesPositionB[i])

          afterMandibleToAfterFibulaRegistrationTransformMatrix = self.getAxes1ToAxes2RegistrationTransformMatrix(afterMandibleToWorldChangeOfFrameMatrix,afterFibulaToWorldChangeOfFrameMatrix)

          intersectionModelB = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Intersection%d_B' % i)
          intersectionModelB.CreateDefaultDisplayNodes()
          getIntersectionBetweenModelAnd1TransformedPlane(fibulaModelNode, afterMandibleToAfterFibulaRegistrationTransformMatrix, mandiblePlane1, intersectionModelB)
          intersectionsList.append(intersectionModelB)
          moveNodeToFolder(intersectionModelB, intersectionsFolder)
          intersectionsList[j].SetAndObserveTransformNodeID(fibulaToRASRotationTransformNode.GetID())
          intersectionsList[j].HardenTransform()
          j += 1

      if useMoreExactVersionOfPositioningAlgorithmChecked:
        intersectionsForCentroidCalculationFolder = getFolder("Intersections For Centroid Calculation")

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
          
          moveNodeToFolder(intersectionA, intersectionsForCentroidCalculationFolder)
          moveNodeToFolder(intersectionB, intersectionsForCentroidCalculationFolder)
          
          getIntersectionBetweenModelAnd1PlaneWithNormalAndOrigin(fibulaModelNode,fibulaLineDirection,lineStartPos,intersectionA)
          getIntersectionBetweenModelAnd1PlaneWithNormalAndOrigin(fibulaModelNode,fibulaLineDirection,lineEndPos,intersectionB)
          lineStartPos = getCentroid(intersectionA)
          lineEndPos = getCentroid(intersectionB)

          #Create fibula axis:
          fibulaX, fibulaY, fibulaZ, fibulaOrigin = self.createFibulaAxisFromFibulaLineAndRightSideLegChecked_2(lineStartPos,lineEndPos,rightSideLegIsDonor)
          
          lineEndPos = lineStartPos + boneSegmentsDistance[i]*fibulaZ

          error = np.linalg.norm(lineStartPos-oldLineStartPos) + np.linalg.norm(lineEndPos-oldLineEndPos)
          if error < 0.01:# Unavoidable errors because of fibula bone shape are about 0.6-0.8mm
            break
        
        self.fibulaPlanesPositionA.append(lineStartPos)
        self.fibulaPlanesPositionB.append(lineEndPos)

        removeFolder(intersectionsForCentroidCalculationFolder)

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

      moveNodeToFolder(mandibleToFibulaRegistrationTransformNode, mandible2FibulaTransformsFolder)
      
    removeFolder(intersectionsFolder)

    #Create measurement lines
    self.createFibulaSegmentsLengthsLines()
  
  def createFibulaSegmentsLengthsLines(self):
    parameterNode = self.getParameterNode()
    fibulaModelNode = parameterNode.GetNodeReference("fibulaModelNode")
    fibulaSegmentsMeasurementMode = parameterNode.GetParameter("fibulaSegmentsMeasurementMode")
    
    fibulaSegmentsLengthsFolder = getFolder("Fibula Segments Lengths", reset = True)
    intersectionsFolder = getFolder("Intersections For Lines Calculation", reset = True)

    fibulaPlanesList = createListFromFolderName("Fibula planes")
    
    for i in range(len(fibulaPlanesList)//2):
      intersectionA = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Intersection A %d' % i)
      intersectionB = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Intersection B %d' % i)
      intersectionA.CreateDefaultDisplayNodes()
      intersectionB.CreateDefaultDisplayNodes()
      
      moveNodeToFolder(intersectionA, intersectionsFolder)
      moveNodeToFolder(intersectionB, intersectionsFolder)

      getIntersectionBetweenModelAnd1Plane(fibulaModelNode,fibulaPlanesList[2*i],intersectionA)
      getIntersectionBetweenModelAnd1Plane(fibulaModelNode,fibulaPlanesList[2*i+1],intersectionB)

      positionA, positionB = (
        getIntersectionPointsOfEachModelByMode(intersectionA,intersectionB,fibulaSegmentsMeasurementMode)
      )

      lineNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLMarkupsLineNode")
      lineNode.SetName("S%d" %i)
      slicer.mrmlScene.AddNode(lineNode)
      slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(lineNode)
      moveNodeToFolder(lineNode, fibulaSegmentsLengthsFolder)

      displayNode = lineNode.GetDisplayNode()
      fibulaViewNode = slicer.mrmlScene.GetSingletonNode(slicer.FIBULA_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
      displayNode.AddViewNodeID(fibulaViewNode.GetID())
      displayNode.SetOccludedVisibility(True)
      
      lineNode.AddControlPoint(vtk.vtkVector3d(positionA))
      lineNode.AddControlPoint(vtk.vtkVector3d(positionB))

      lineNode.SetLocked(True)
      
    removeFolder(intersectionsFolder)
  
  def createFibulaPlanesFromMandiblePlanesAndFibulaAxis(self,mandiblePlanesList,fibulaPlanesList):
    fibulaPlanesFolder = getFolder("Fibula planes")
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
      fibulaPlaneA.SetSize(slicer.PLANE_SIDE_SIZE,slicer.PLANE_SIDE_SIZE)
      fibulaPlaneA.SetPlaneType(slicer.vtkMRMLMarkupsPlaneNode.PlaneType3Points)

      displayNode = fibulaPlaneA.GetDisplayNode()
      fibulaViewNode = slicer.mrmlScene.GetSingletonNode(slicer.FIBULA_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
      displayNode.AddViewNodeID(fibulaViewNode.GetID())
      displayNode.SetPropertiesLabelVisibility(False)
      displayNode.HandlesInteractiveOff()

      moveNodeToFolder(fibulaPlaneA, fibulaPlanesFolder)

      fibulaPlaneA.SetAxes(mandiblePlane0X,mandiblePlane0Y,mandiblePlane0Z)
      fibulaPlaneA.SetOrigin(mandiblePlane0Origin)
      fibulaPlaneA.SetLocked(True)
      fibulaPlanesList.append(fibulaPlaneA)


      fibulaPlaneB = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsPlaneNode", "FibulaPlane%d_B" % i)
      slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(fibulaPlaneB)
      fibulaPlaneB.SetSize(slicer.PLANE_SIDE_SIZE,slicer.PLANE_SIDE_SIZE)
      fibulaPlaneB.SetPlaneType(slicer.vtkMRMLMarkupsPlaneNode.PlaneType3Points)

      displayNode = fibulaPlaneB.GetDisplayNode()
      displayNode.AddViewNodeID(fibulaViewNode.GetID())
      displayNode.SetPropertiesLabelVisibility(False)
      displayNode.HandlesInteractiveOff()

      moveNodeToFolder(fibulaPlaneB, fibulaPlanesFolder)

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

    self.setRedSliceForMarkupsDisplayNodes()

  def createAndUpdateDynamicModelerNodes(self):
    parameterNode = self.getParameterNode()
    #useNonDecimatedModelsForPreviewChecked = parameterNode.GetParameter("useNonDecimatedModelsForPreview") == "True"
    #mandibularCurve = parameterNode.GetNodeReference("mandibleCurve")
    #nonDecimatedFibulaModelNode = parameterNode.GetNodeReference("fibulaModelNode")
    #decimatedFibulaModelNode = parameterNode.GetNodeReference("decimatedFibulaModelNode")
    #nonDecimatedMandibleModelNode = parameterNode.GetNodeReference("mandibleModelNode")
    #decimatedMandibleModelNode = parameterNode.GetNodeReference("decimatedMandibleModelNode")
    fixCutGoesThroughTheMandibleTwiceCheckBoxChanged = parameterNode.GetParameter('fixCutGoesThroughTheMandibleTwiceCheckBoxChanged') == "True"
    fixCutGoesThroughTheMandibleTwiceChecked = parameterNode.GetParameter('fixCutGoesThroughTheMandibleTwice') == "True"
    planeToFixCutGoesThroughTheMandibleTwice = parameterNode.GetNodeReference("planeToFixCutGoesThroughTheMandibleTwice")
    planeList = createListFromFolderName("Mandibular planes")
     
    fibulaPlanesList = createListFromFolderName("Fibula planes")

    fibulaModelNode = self.getCurrentFibulaModel()
    mandibleModelNode = self.getCurrentMandibleModel()
    vesselsModelNode = self.getCurrentVesselsModel()

    bonePlaneCutsList = createListFromFolderName("Bone Plane Cuts")
    if len(bonePlaneCutsList) == 0 or fixCutGoesThroughTheMandibleTwiceCheckBoxChanged:
      bonePlaneCutsFolder = getFolder("Bone Plane Cuts", reset = True)
      cutBonesFolder = getFolder("Cut Bones", reset = True)
      vesselsPlaneCutsFolder = getFolder("Vessels Plane Cuts", reset = True)
      cutVesselsFolder = getFolder("Cut Vessels", reset = True)

      for i in range(0,len(fibulaPlanesList),2):
        modelNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLModelNode")
        modelNode.SetName("Fibula Segment {0}A-{1}B".format(i//2,i//2))
        slicer.mrmlScene.AddNode(modelNode)
        modelNode.CreateDefaultDisplayNodes()
        modelDisplayNode = modelNode.GetDisplayNode()
        modelDisplayNode.SetVisibility2D(True)

        fibulaViewNode = slicer.mrmlScene.GetSingletonNode(slicer.FIBULA_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
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
        
        moveNodeToFolder(dynamicModelerNode, bonePlaneCutsFolder)
        moveNodeToFolder(modelNode, cutBonesFolder)
      
      if vesselsModelNode:
        for i in range(0,len(fibulaPlanesList),2):
          modelNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLModelNode")
          modelNode.SetName("Vessels Segment {0}A-{1}B".format(i//2,i//2))
          slicer.mrmlScene.AddNode(modelNode)
          modelNode.CreateDefaultDisplayNodes()
          modelDisplayNode = modelNode.GetDisplayNode()
          modelDisplayNode.SetVisibility2D(True)

          fibulaViewNode = slicer.mrmlScene.GetSingletonNode(slicer.FIBULA_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
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
          dynamicModelerNode.SetNodeReferenceID("PlaneCut.InputModel", vesselsModelNode.GetID())
          dynamicModelerNode.AddNodeReferenceID("PlaneCut.InputPlane", fibulaPlanesList[i+1].GetID())
          dynamicModelerNode.AddNodeReferenceID("PlaneCut.InputPlane", fibulaPlanesList[i].GetID()) 
          dynamicModelerNode.SetNodeReferenceID("PlaneCut.OutputNegativeModel", modelNode.GetID())
          dynamicModelerNode.SetAttribute("OperationType", "Difference")
          #slicer.modules.dynamicmodeler.logic().RunDynamicModelerTool(dynamicModelerNode)
          
          moveNodeToFolder(dynamicModelerNode, vesselsPlaneCutsFolder)
          moveNodeToFolder(modelNode, cutVesselsFolder)
      
      modelNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLModelNode")
      modelNode.SetName("Resected mandible")
      slicer.mrmlScene.AddNode(modelNode)
      modelNode.CreateDefaultDisplayNodes()
      modelDisplayNode = modelNode.GetDisplayNode()
      modelDisplayNode.SetVisibility2D(True)
      modelNode.SetAttribute("isResectedMandibleModel","True")

      self.resectedMandibleAndObserver = [
        modelNode, 
        modelNode.AddObserver(slicer.vtkMRMLModelNode.MeshModifiedEvent, self.setPlanningInformativeText)
      ]

      mandibleViewNode = slicer.mrmlScene.GetSingletonNode(slicer.MANDIBLE_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
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

        # TODO, maybe the 2 lines below or the whole if block could be avoided by
        # using dynamicModelerNode.RemoveNodeReferenceIDs("") in combination with other methods
        parameterNode.SetNodeReferenceID("planeToFixCutGoesThroughTheMandibleTwice", "")
        slicer.mrmlScene.RemoveNode(planeToFixCutGoesThroughTheMandibleTwice)

        mandibleCentroidX = parameterNode.GetParameter("mandibleCentroidX")
        mandibleCentroidY = parameterNode.GetParameter("mandibleCentroidY")
        mandibleCentroidZ = parameterNode.GetParameter("mandibleCentroidZ")
        mandibleCentroid = np.array([float(mandibleCentroidX),float(mandibleCentroidY),float(mandibleCentroidZ)])

        planeToFixCutGoesThroughTheMandibleTwice = slicer.mrmlScene.CreateNodeByClass("vtkMRMLMarkupsPlaneNode")
        planeToFixCutGoesThroughTheMandibleTwice.SetName("planeToFixCutGoesThroughTheMandibleTwice")
        slicer.mrmlScene.AddNode(planeToFixCutGoesThroughTheMandibleTwice)
        slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(planeToFixCutGoesThroughTheMandibleTwice)
        parentFolder = getFolder("Mandible reconstruction")
        moveNodeToFolder(planeToFixCutGoesThroughTheMandibleTwice, parentFolder)
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

      moveNodeToFolder(dynamicModelerNode, bonePlaneCutsFolder)
      moveNodeToFolder(modelNode, cutBonesFolder)

      if fixCutGoesThroughTheMandibleTwiceCheckBoxChanged:
        parameterNode.SetParameter('fixCutGoesThroughTheMandibleTwiceCheckBoxChanged','False')
    
    else:
      dynamicModelerNodesList = createListFromFolderName("Bone Plane Cuts")
      for i in range(len(dynamicModelerNodesList)):
        if i != (len(dynamicModelerNodesList) -1):
          dynamicModelerNodesList[i].SetNodeReferenceID("PlaneCut.InputModel", fibulaModelNode.GetID())
        else:
          dynamicModelerNodesList[i].SetNodeReferenceID("PlaneCut.InputModel", mandibleModelNode.GetID())
          dynamicModelerNodesList[i].RemoveNodeReferenceIDs("PlaneCut.InputPlane")
          dynamicModelerNodesList[i].AddNodeReferenceID("PlaneCut.InputPlane", planeList[len(planeList)-1].GetID())
          dynamicModelerNodesList[i].AddNodeReferenceID("PlaneCut.InputPlane", planeList[0].GetID()) 
          if fixCutGoesThroughTheMandibleTwiceChecked:
            dynamicModelerNodesList[i].AddNodeReferenceID("PlaneCut.InputPlane", planeToFixCutGoesThroughTheMandibleTwice.GetID())

      if vesselsModelNode:
        dynamicModelerNodesList = createListFromFolderName("Vessels Plane Cuts")
        for i in range(len(dynamicModelerNodesList)):
          dynamicModelerNodesList[i].SetNodeReferenceID("PlaneCut.InputModel", vesselsModelNode.GetID())

    inversePlaneCutsList = createListFromFolderName("Inverse Plane Cuts")
    inverseAppendList = createListFromFolderName("Inverse Append")
    numberOfFibulaPieces = len(createListFromFolderName("Bone Plane Cuts")) -1
    if (
      (len(inversePlaneCutsList) != numberOfFibulaPieces) or
      (len(inverseAppendList) != numberOfFibulaPieces)
    ):
      inverseMandibleReconstructionFolder = getFolder("Inverse mandible reconstruction", reset = True)
      setFolderItemVisibility(inverseMandibleReconstructionFolder, False)
      inversePlaneCutsFolder = getFolder("Inverse Plane Cuts", reset = True)
      inverseAppendFolder = getFolder("Inverse Append", reset = True)
      cutMandiblePiecesFolder = getFolder("Cut Mandible Pieces", reset = True)
      fullMandiblesFolder = getFolder("Full Mandibles", reset = True)

      qt.QTimer.singleShot(0, lambda: setFolderItemVisibility(fullMandiblesFolder, 0))

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

        mandibleViewNode = slicer.mrmlScene.GetSingletonNode(slicer.MANDIBLE_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
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

        moveNodeToFolder(dynamicModelerNode, inversePlaneCutsFolder)
        moveNodeToFolder(dynamicModelerNode2, inverseAppendFolder)
        moveNodeToFolder(modelNode, cutMandiblePiecesFolder)
        moveNodeToFolder(fullModelNode, fullMandiblesFolder)
        
    
    else:
      dynamicModelerNodesList = createListFromFolderName("Inverse Plane Cuts")
      for i in range(len(dynamicModelerNodesList)):
        dynamicModelerNodesList[i].SetNodeReferenceID("PlaneCut.InputModel", mandibleModelNode.GetID())

      dynamicModelerNodesList = createListFromFolderName("Inverse Append")
      for i in range(len(dynamicModelerNodesList)):
        dynamicModelerNodesList[i].SetNodeReferenceID("Append.InputModel", mandibleModelNode.GetID())

  def resetPlan(self):
    removeFolder(getFolder("Fibula planes"))
    removeFolder(getFolder("Bone Plane Cuts"))
    removeFolder(getFolder("Cut Bones"))
    removeFolder(getFolder("Transformed Fibula Pieces"))
    removeFolder(getFolder("Vessels Plane Cuts"))
    removeFolder(getFolder("Cut Vessels"))
    removeFolder(getFolder("Transformed Vessels Pieces"))
    #self.getParameterNode().SetParameter("fixCutGoesThroughTheMandibleTwiceCheckBoxChanged", str(True))
  
  @saveExecutedMethodWithTelemetry
  def hardVSPUpdate(self):
    self.resetPlan()
    self.onGenerateFibulaPlanesTimerTimeout()

  @saveExecutedMethodWithTelemetry
  def lockVSP(self, doLock):
    parameterNode = self.getParameterNode()
    parameterNode.SetParameter("lockVSP", str(doLock))

  def generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandible(self):
    parameterNode = self.getParameterNode()
    useNonDecimatedModelsForPreviewChecked = parameterNode.GetParameter("useNonDecimatedModelsForPreview") == "True"
    nonDecimatedMandibleModelNode = parameterNode.GetNodeReference("mandibleModelNode")
    decimatedMandibleModelNode = parameterNode.GetNodeReference("decimatedMandibleModelNode")
    planeList = createListFromFolderName("Mandibular planes")
    includeVesselsOnPlan = parameterNode.GetParameter("includeVesselsOnPlan") == "True"

    if useNonDecimatedModelsForPreviewChecked:
      mandibleModelNode = nonDecimatedMandibleModelNode
    else:
      mandibleModelNode = decimatedMandibleModelNode

    #delete all folders because there is only one plane and show mandible model
    if len(planeList) <= 1:
      self.resetPlan()
      mandibleDisplayNode = mandibleModelNode.GetDisplayNode()
      mandibleDisplayNode.SetVisibility(True)
      return

    fibulaPlanesList = createListFromFolderName("Fibula planes")

    #delete all the folders that are not updated
    if (len(fibulaPlanesList) != (2*len(planeList) - 2)) or (len(fibulaPlanesList) == 0):
      removeFolder(getFolder("Bone Plane Cuts"))
      removeFolder(getFolder("Cut Bones"))
      removeFolder(getFolder("Transformed Fibula Pieces"))
      removeFolder(getFolder("Vessels Plane Cuts"))
      removeFolder(getFolder("Cut Vessels"))
      removeFolder(getFolder("Transformed Vessels Pieces"))
      fibulaPlanesFolder = getFolder("Fibula planes", reset = True)
      fibulaPlanesList = createListFromFolderName("Fibula planes")
      #Create fibula planes and set their size
      self.createFibulaPlanesFromMandiblePlanesAndFibulaAxis(planeList,fibulaPlanesList)

    self.transformFibulaPlanes()

    kindOfMandibleResection = parameterNode.GetParameter("kindOfMandibleResection")
    if kindOfMandibleResection == "Hemimandibulectomy":
      # this is needed because otherwise decimation will make rendering of one mandible piece fail
      parameterNode.SetParameter("useNonDecimatedModelsForPreview", "True")

    self.createAndUpdateDynamicModelerNodes()
  
    self.updateFibulaPieces()
    
    self.updateVesselsPieces()

    self.updateInverseMandiblePieces()

    self.tranformFibulaPiecesToMandible()

    if includeVesselsOnPlan:
      self.tranformVesselsPiecesToMandible()

    # self.tranformMandiblePiecesToFibula()

    self.setRedSliceForModelsDisplayNodes()
    self.setRedSliceForMarkupsDisplayNodes()

    self.updateNormalizationFibulaLineTransform(None)

  def reorderMandiblePlanes(self):
    planeList = createListFromFolderName("Mandibular planes")
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

    mandibularPlanesFolder2 = getFolder("Mandibular planes 2")

    for i in range(len(mandiblePlanesIndicesList)):
      mandiblePlane = mandiblePlanesIndicesList[i][0]
      moveNodeToFolder(mandiblePlane, mandibularPlanesFolder2)

    removeFolder(getFolder("Mandibular planes"))
    renameFolder(mandibularPlanesFolder2,"Mandibular planes")

  def setRedSliceForModelsDisplayNodes(self):
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
    
    fibulaSurgicalGuideBase = parameterNode.GetNodeReference("fibulaSurgicalGuideBaseModel")
    mandibleSurgicalGuideBase = parameterNode.GetNodeReference("mandibleSurgicalGuideBaseModel")
    bothSidesMandibleGuideBaseModel = parameterNode.GetNodeReference("bothSidesMandibleGuideBaseModel")
    cutBonesList = createListFromFolderName("Cut Bones")
    transformedFibulaPiecesList = createListFromFolderName("Transformed Fibula Pieces")
    transformedMandiblePiecesList = createListFromFolderName("Transformed Mandible Pieces")
    transformedFullMandiblesList = createListFromFolderName("Transformed Full Mandible")
    cutMandiblePiecesList = createListFromFolderName("Cut Mandible Pieces")
    interCondylarBeamBox = parameterNode.GetNodeReference("interCondylarBeamBox")
    mandibleBridgeTube = parameterNode.GetNodeReference("mandibleBridgeTube")
    biggerSawBoxesModelsList = createListFromFolderName("biggerSawBoxes Models")
    biggerMiterBoxesList = createListFromFolderName("biggerMiterBoxes Models")
    redSliceNode = slicer.mrmlScene.GetSingletonNode("Red", "vtkMRMLSliceNode")

    if np.linalg.norm(fibulaCentroid-centerOfScalarVolume) < np.linalg.norm(mandibleCentroid-centerOfScalarVolume):
      #When fibulaScalarVolume:
      addIterationList = cutBonesList[0:-1] + transformedMandiblePiecesList + transformedFullMandiblesList + [fibulaSurgicalGuideBase] + biggerMiterBoxesList
      removeIterationList = cutBonesList[-1:] + transformedFibulaPiecesList + cutMandiblePiecesList + [interCondylarBeamBox, mandibleBridgeTube, mandibleSurgicalGuideBase, bothSidesMandibleGuideBaseModel] + biggerSawBoxesModelsList
      
    else:
      #When mandibleScalarVolume:
      addIterationList = cutBonesList[-1:] + transformedFibulaPiecesList + cutMandiblePiecesList + [interCondylarBeamBox, mandibleBridgeTube, mandibleSurgicalGuideBase, bothSidesMandibleGuideBaseModel] + biggerSawBoxesModelsList
      removeIterationList = cutBonesList[0:-1] + transformedMandiblePiecesList + transformedFullMandiblesList + [fibulaSurgicalGuideBase] + biggerMiterBoxesList
    
    for i in range(len(removeIterationList)):
      if removeIterationList[i] is not None:
        displayNode = removeIterationList[i].GetDisplayNode()
        displayNode.RemoveViewNodeID(redSliceNode.GetID())

    for i in range(len(addIterationList)):
      if addIterationList[i] is not None:
        displayNode = addIterationList[i].GetDisplayNode()
        displayNode.AddViewNodeID(redSliceNode.GetID())

  def setRedSliceForMarkupsDisplayNodes(self):
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

    # if set to None or [] is because I don't consider them important to be shown in the red slice
    fibulaLine = None
    fibulaFiducialList = parameterNode.GetNodeReference("fibulaFiducialList")
    miterBoxDirectionLine = parameterNode.GetNodeReference("miterBoxDirectionLine")
    fibulaPlanesList = []
    mandibleCurve = parameterNode.GetNodeReference("mandibleCurve")
    mandibleFiducialList = parameterNode.GetNodeReference("mandibleFiducialList")
    interCondylarBeamLine = parameterNode.GetNodeReference("interCondylarBeamLine")
    mandibleBridgeCurve = parameterNode.GetNodeReference("mandibleBridgeCurve")
    leftSideMandibleGuideBaseCurve = None
    rightSideMandibleGuideBaseCurve = None
    plateCurve = parameterNode.GetNodeReference("plateCurve")
    dentalImplantsFiducialList = parameterNode.GetNodeReference("dentalImplantsFiducialList")
    mandibularPlanesList = []
    sawBoxesPlanesList = createListFromFolderName("sawBoxes Planes")
    dentalImplantsPlanesList = createListFromFolderName("dentalImplants Planes")
    redSliceNode = slicer.mrmlScene.GetSingletonNode("Red", "vtkMRMLSliceNode")

    fibulaMarkupsList = [fibulaLine, fibulaFiducialList, miterBoxDirectionLine] + fibulaPlanesList
    mandibleMarkupsList = (
      [mandibleCurve, mandibleFiducialList, interCondylarBeamLine, mandibleBridgeCurve,
       leftSideMandibleGuideBaseCurve, rightSideMandibleGuideBaseCurve, plateCurve, dentalImplantsFiducialList]
      + mandibularPlanesList + sawBoxesPlanesList + dentalImplantsPlanesList
    )

    if np.linalg.norm(fibulaCentroid-centerOfScalarVolume) < np.linalg.norm(mandibleCentroid-centerOfScalarVolume):
      #When fibulaScalarVolume:
      addIterationList = fibulaMarkupsList
      removeIterationList = mandibleMarkupsList

    else:
      #When mandibleScalarVolume:
      addIterationList = mandibleMarkupsList
      removeIterationList = fibulaMarkupsList

    for i in range(len(removeIterationList)):
      if removeIterationList[i] is not None:
        displayNode = removeIterationList[i].GetDisplayNode()
        displayNode.RemoveViewNodeID(redSliceNode.GetID())

    for i in range(len(addIterationList)):
      if addIterationList[i] is not None:
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

  @saveExecutedMethodWithTelemetry
  def makeModels(self):
    setBRPLayout()
    slicer.util.resetSliceViews()

    parameterNode = self.getParameterNode()
    parameterNode.SetParameter("currentlyProcessing", str(True))
    fibulaSegmentation = parameterNode.GetNodeReference("fibulaSegmentation")
    fibulaSegment = parameterNode.GetParameter("fibulaSegment")
    mandibularSegmentation = parameterNode.GetNodeReference("mandibularSegmentation")
    mandibularSegment = parameterNode.GetParameter("mandibularSegment")
    vesselsSegmentation = parameterNode.GetNodeReference("vesselsSegmentation")
    vesselsSegment = parameterNode.GetParameter("vesselsSegment")
    useNonDecimatedModelsForPreviewChecked = parameterNode.GetParameter("useNonDecimatedModelsForPreview") == "True"

    wasModified = parameterNode.StartModify()

    segmentationModelsFolder = getFolder("Segmentation Models", reset = True)
    
    fibulaModelNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", "fibula")
    mandibleModelNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", "mandible")
    decimatedFibulaModelNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','decimatedFibula')
    decimatedMandibleModelNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','decimatedMandible')
    segmentations = [fibulaSegmentation,mandibularSegmentation]
    models = [fibulaModelNode,mandibleModelNode]
    decimatedModels = [decimatedFibulaModelNode,decimatedMandibleModelNode]
    segmentNames = ["Fibula","Mandible"]
    segmentIDs = [fibulaSegment,mandibularSegment]
    laterality = [parameterNode.GetParameter("donorLeg") + " ", ""]
    if vesselsSegmentation is not None and vesselsSegment != "":
      vesselsModelNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", "vessels")
      decimatedVesselsModelNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','decimatedVessels')
      segmentations.append(vesselsSegmentation)
      models.append(vesselsModelNode)
      decimatedModels.append(decimatedVesselsModelNode)
      segmentNames.append("Vessels")
      segmentIDs.append(vesselsSegment)
      laterality.append("")

    for i in range(len(models)):
      models[i].CreateDefaultDisplayNodes()
      decimatedModels[i].CreateDefaultDisplayNodes()

      seg = segmentations[i]
      seg.GetSegmentation().CreateRepresentation(slicer.vtkSegmentationConverter.GetSegmentationClosedSurfaceRepresentationName())
      name = laterality[i] + segmentNames[i]
      segmentID = segmentIDs[i]
      segment = seg.GetSegmentation().GetSegment(segmentID)
      segDisplayNode = seg.GetDisplayNode()
      segDisplayNode.SetVisibility(False)

      logic = slicer.modules.segmentations.logic()
      # this replaces original model names by segment names
      logic.ExportSegmentToRepresentationNode(segment, models[i])

      modelDisplayNode = models[i].GetDisplayNode()

      decimatedModelDisplayNode = decimatedModels[i].GetDisplayNode()
      decimatedModelDisplayNode.SetColor(models[i].GetDisplayNode().GetColor())

      param = {
              "inputModel": models[i],
              "outputModel": decimatedModels[i],
              "reductionFactor": 0.95,
              "method": "FastQuadric"
              }

      slicer.cli.runSync(slicer.modules.decimation, parameters=param)

      moveNodeToFolder(models[i], segmentationModelsFolder)
      moveNodeToFolder(decimatedModels[i], segmentationModelsFolder)

      if (i==0) or (i==2):
        singletonTag = slicer.FIBULA_VIEW_SINGLETON_TAG
      else:
        singletonTag = slicer.MANDIBLE_VIEW_SINGLETON_TAG
      viewNode = slicer.mrmlScene.GetSingletonNode(singletonTag, "vtkMRMLViewNode")
      cameraNode = slicer.modules.cameras.logic().GetViewActiveCameraNode(viewNode)

      modelDisplayNode.AddViewNodeID(viewNode.GetID())
      decimatedModelDisplayNode.AddViewNodeID(viewNode.GetID())

      centroid = getCentroid(models[i])
      if (i==0) or (i==2):
        viewUpDirection = np.array([0.,1.,0.])
        cameraDirection = np.array([1.,0.,0.])
      else:
        viewUpDirection = np.array([0.,0.,1.])
        cameraDirection = np.array([0.,-1.,0.])
      cameraNode.SetPosition(centroid-cameraDirection*300)
      cameraNode.SetFocalPoint(centroid)
      cameraNode.SetViewUp(viewUpDirection)
      cameraNode.ResetClippingRange()

      if (i==0) or (i==2):
        parameterNode.SetParameter("fibulaCentroidX",str(centroid[0]))
        parameterNode.SetParameter("fibulaCentroidY",str(centroid[1]))
        parameterNode.SetParameter("fibulaCentroidZ",str(centroid[2]))
      else:
        parameterNode.SetParameter("mandibleCentroidX",str(centroid[0]))
        parameterNode.SetParameter("mandibleCentroidY",str(centroid[1]))
        parameterNode.SetParameter("mandibleCentroidZ",str(centroid[2]))

      if i==0:
        fibulaSegmentID = segmentID

    fibulaModelNode.SetName("fibula")
    mandibleModelNode.SetName("mandible")
    if vesselsSegmentation is not None and vesselsSegment != "":
      vesselsModelNode.SetName("vessels")

    parameterNode.SetNodeReferenceID("fibulaModelNode", fibulaModelNode.GetID())
    parameterNode.SetNodeReferenceID("mandibleModelNode", mandibleModelNode.GetID())
    parameterNode.SetNodeReferenceID("decimatedFibulaModelNode", decimatedFibulaModelNode.GetID())
    parameterNode.SetNodeReferenceID("decimatedMandibleModelNode", decimatedMandibleModelNode.GetID())
    if vesselsSegmentation is not None and vesselsSegment != "":
      parameterNode.SetNodeReferenceID("vesselsModelNode", vesselsModelNode.GetID())
      parameterNode.SetNodeReferenceID("decimatedVesselsModelNode", decimatedVesselsModelNode.GetID())

    decimatedFibulaModelNode.SetAndObserveMesh(calculateNormals(decimatedFibulaModelNode.GetMesh()))
    decimatedMandibleModelNode.SetAndObserveMesh(calculateNormals(decimatedMandibleModelNode.GetMesh()))
    if vesselsSegmentation is not None and vesselsSegment != "":
      decimatedVesselsModelNode.SetAndObserveMesh(calculateNormals(decimatedVesselsModelNode.GetMesh()))

    self.autocreateFibulaLine(fibulaSegmentID, fibulaSegmentation)

    parameterNode.EndModify(wasModified)

    if USING_GUI:
      slicer.util.forceRenderAllViews()

    parameterNode.SetParameter("currentlyProcessing", str(False))

  def autocreateFibulaLine(self, segmentID, segmentationNode):
    obbOrigin, obbDiameters, principalZAxis = getSegmentStatistics(segmentID, segmentationNode)

    safeDistanceToFibulaTip = float(self.getParameterNode().GetParameter("safeDistanceToFibulaTip_mm"))

    superiorDirection = np.array([0.,0.,1.])
    # the next if expression body is not intuitive but its because of how segmentStatistics works
    if vtk.vtkMath.Dot(principalZAxis, superiorDirection) > 0:
      startPoint = obbOrigin
      endPoint = obbOrigin + principalZAxis*obbDiameters[2]
      fibulaFirstPoint = startPoint + principalZAxis*safeDistanceToFibulaTip
      fibulaLastPoint = endPoint - principalZAxis*safeDistanceToFibulaTip
    else:
      startPoint = obbOrigin + principalZAxis*obbDiameters[2]
      endPoint = obbOrigin
      fibulaFirstPoint = startPoint - principalZAxis*safeDistanceToFibulaTip
      fibulaLastPoint = endPoint + principalZAxis*safeDistanceToFibulaTip

    print("principalZAxis: " + str(principalZAxis))
    print("obbDiameters[2]: " + str(obbDiameters[2]))
    print("obbOrigin: " + str(obbOrigin))
    print("startPoint: " + str(startPoint))
    print("endPoint: " + str(endPoint))
    print("fibulaFirstPoint: " + str(fibulaFirstPoint))
    print("fibulaLastPoint: " + str(fibulaLastPoint))

    self.getFibulaLine().RemoveAllControlPoints()
    self.getFibulaLine().AddControlPoint(fibulaFirstPoint)
    self.getFibulaLine().AddControlPoint(fibulaLastPoint)
  
  def updateFibulaPieces(self):
    planeCutsList = createListFromFolderName("Bone Plane Cuts")
    for i in range(len(planeCutsList)):
      slicer.modules.dynamicmodeler.logic().RunDynamicModelerTool(planeCutsList[i])
    
    # update resected mandible model according to the kindOfMandibleResection
    resectedMandibleModel = None
    planeCutsList = createListFromFolderName("Cut Bones")
    for i in range(len(planeCutsList)):
      if planeCutsList[i].GetAttribute("isResectedMandibleModel") == "True":
        resectedMandibleModel = planeCutsList[i]
        break
    if not resectedMandibleModel:
      return
    
    self.filterOutUnconnectedModelPiecesAccordingToKindOfMandibleResection(resectedMandibleModel)

  def filterOutUnconnectedModelPiecesAccordingToKindOfMandibleResection(self, modelPieces):
    parameterNode = self.getParameterNode()
    kindOfMandibleResection = parameterNode.GetParameter("kindOfMandibleResection")
    if kindOfMandibleResection == "Segmental Mandibulectomy":
      return
    elif kindOfMandibleResection == "Hemimandibulectomy":
      rightMandiblePlane, leftMandiblePlane = self.getRightAndLeftMandibleResectionPlanes()
      mandibleSideToRemove = parameterNode.GetParameter("mandibleSideToRemove")
      if mandibleSideToRemove == "Removing right side":
        nearestPlane = leftMandiblePlane
      elif mandibleSideToRemove == "Removing left side":
        nearestPlane = rightMandiblePlane
      nearestPlaneOrigin = np.zeros(3)
      nearestPlane.GetNthControlPointPosition(0,nearestPlaneOrigin)
      #
      cleanPolyData = vtk.vtkCleanPolyData()
      cleanPolyData.SetInputData(modelPieces.GetPolyData())
      cleanPolyData.Update()
      # connectivity filter with point seed
      connectivityFilter = vtk.vtkPolyDataConnectivityFilter()
      connectivityFilter.SetInputData(cleanPolyData.GetOutput())
      connectivityFilter.SetExtractionModeToClosestPointRegion()
      connectivityFilter.SetClosestPoint(nearestPlaneOrigin)
      connectivityFilter.Update()
      closestRegion = vtk.vtkPolyData()
      closestRegion.DeepCopy(connectivityFilter.GetOutput())
      #
      modelPieces.SetAndObservePolyData(calculateNormals(closestRegion))

  def updateVesselsPieces(self):
    parameterNode = self.getParameterNode()
    
    includeVesselsOnPlan = parameterNode.GetParameter("includeVesselsOnPlan") == "True"
    if not includeVesselsOnPlan:
      return
    
    vesselsPlaneCutsList = createListFromFolderName("Vessels Plane Cuts")
    for i in range(len(vesselsPlaneCutsList)):
      slicer.modules.dynamicmodeler.logic().RunDynamicModelerTool(vesselsPlaneCutsList[i])

  def updateInverseMandiblePieces(self):
    inversePlaneCutsList = createListFromFolderName("Inverse Plane Cuts")
    for i in range(len(inversePlaneCutsList)):
      slicer.modules.dynamicmodeler.logic().RunDynamicModelerTool(inversePlaneCutsList[i])

    inverseAppendList = createListFromFolderName("Inverse Append")
    for i in range(len(inverseAppendList)):
      slicer.modules.dynamicmodeler.logic().RunDynamicModelerTool(inverseAppendList[i])

  def tranformMandiblePiecesToFibula(self):
    mandible2FibulaTransformsList = createListFromFolderName("Mandible2Fibula transforms")
    transformedMandiblePiecesFolder = getFolder("Transformed Mandible Pieces", reset = True)
    transformedFullMandiblesFolder = getFolder("Transformed Full Mandible", reset = True)

    cutMandiblePiecesList = createListFromFolderName("Cut Mandible Pieces")
    for i in range(len(cutMandiblePiecesList)):
      transformedMandiblePiece = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode',slicer.mrmlScene.GetUniqueNameByString('Transformed ' + cutMandiblePiecesList[i].GetName()))
      transformedMandiblePiece.CreateDefaultDisplayNodes()
      transformedMandiblePiece.CopyContent(cutMandiblePiecesList[i])
      transformedMandiblePieceDisplayNode = transformedMandiblePiece.GetDisplayNode()
      transformedMandiblePieceDisplayNode.SetColor(cutMandiblePiecesList[i].GetDisplayNode().GetColor())
      transformedMandiblePieceDisplayNode.SetVisibility2D(True)

      fibulaViewNode = slicer.mrmlScene.GetSingletonNode(slicer.FIBULA_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
      transformedMandiblePieceDisplayNode.AddViewNodeID(fibulaViewNode.GetID())

      transformedMandiblePiece.SetAndObserveTransformNodeID(mandible2FibulaTransformsList[i].GetID())
      transformedMandiblePieceTransformationSuccess = transformedMandiblePiece.HardenTransform()
      if not (transformedMandiblePieceTransformationSuccess):
        Exception('Hardening transforms was not successful')

      moveNodeToFolder(transformedMandiblePiece, transformedMandiblePiecesFolder)

    mandibleList = createListFromFolderName("Full Mandibles")
    for i in range(len(mandibleList)):
      transformedMandible = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode',slicer.mrmlScene.GetUniqueNameByString('Transformed ' + mandibleList[i].GetName()))
      transformedMandible.CreateDefaultDisplayNodes()
      transformedMandible.CopyContent(mandibleList[i])
      transformedMandibleDisplayNode = transformedMandible.GetDisplayNode()
      transformedMandibleDisplayNode.SetColor(mandibleList[i].GetDisplayNode().GetColor())
      transformedMandibleDisplayNode.SetVisibility2D(True)

      fibulaViewNode = slicer.mrmlScene.GetSingletonNode(slicer.FIBULA_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
      transformedMandibleDisplayNode.AddViewNodeID(fibulaViewNode.GetID())

      transformedMandible.SetAndObserveTransformNodeID(mandible2FibulaTransformsList[i].GetID())
      transformedMandibleTransformationSuccess = transformedMandible.HardenTransform()
      if not (transformedMandibleTransformationSuccess):
        Exception('Hardening transforms was not successful')

      moveNodeToFolder(transformedMandible, transformedFullMandiblesFolder)

    qt.QTimer.singleShot(0, lambda: setFolderItemVisibility(transformedFullMandiblesFolder, 1))

  def tranformFibulaPiecesToMandible(self):
    parameterNode = self.getParameterNode()
    fibulaLine = parameterNode.GetNodeReference("fibulaLine")
    planeList = createListFromFolderName("Mandibular planes")

    bonePiecesTransformFolder = getFolder("Bone Pieces Transforms", reset = True)
    transformedFibulaPiecesFolder = getFolder("Transformed Fibula Pieces", reset = True)

    lineStartPos = np.zeros(3)
    lineEndPos = np.zeros(3)
    fibulaLine.GetNthControlPointPositionWorld(0, lineStartPos)
    fibulaLine.GetNthControlPointPositionWorld(1, lineEndPos)
    fibulaOrigin = lineStartPos
    fibulaZ = (lineEndPos-lineStartPos)/np.linalg.norm(lineEndPos-lineStartPos)

    cutBonesList = createListFromFolderName("Cut Bones")
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

      mandibleViewNode = slicer.mrmlScene.GetSingletonNode(slicer.MANDIBLE_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
      transformedFibulaPieceDisplayNode.AddViewNodeID(mandibleViewNode.GetID())

      transformedFibulaPiece.SetAndObserveTransformNodeID(fibulaPieceToMandibleAxisTransformNode.GetID())
      transformedFibulaPieceTransformationSuccess = transformedFibulaPiece.HardenTransform()
      if not (transformedFibulaPieceTransformationSuccess):
        Exception('Hardening transforms was not successful')

      moveNodeToFolder(transformedFibulaPiece, transformedFibulaPiecesFolder)
      moveNodeToFolder(fibulaPieceToMandibleAxisTransformNode, bonePiecesTransformFolder)

  def tranformVesselsPiecesToMandible(self):
    vesselsPiecesTransformFolder = getFolder("Vessels Pieces Transforms", reset = True)
    transformedVesselsPiecesFolder = getFolder("Transformed Vessels Pieces", reset = True)

    cutVesselsList = createListFromFolderName("Cut Vessels")
    for i in range(len(cutVesselsList)):
      fibulaToMandibleRegistrationTransformMatrix = vtk.vtkMatrix4x4()
      fibulaToMandibleRegistrationTransformMatrix.DeepCopy(self.mandibleToFibulaRegistrationTransformMatricesList[i])
      fibulaToMandibleRegistrationTransformMatrix.Invert()

      vesselsPieceToMandibleAxisTransformNode = slicer.vtkMRMLLinearTransformNode()
      vesselsPieceToMandibleAxisTransformNode.SetName("Vessels Segment {0} Transform".format(i))
      slicer.mrmlScene.AddNode(vesselsPieceToMandibleAxisTransformNode)

      vesselsPieceToMandibleAxisTransformNode.SetMatrixTransformToParent(fibulaToMandibleRegistrationTransformMatrix)
      vesselsPieceToMandibleAxisTransformNode.UpdateScene(slicer.mrmlScene)

      transformedVesselsPiece = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode',slicer.mrmlScene.GetUniqueNameByString('Transformed ' + cutVesselsList[i].GetName()))
      transformedVesselsPiece.CreateDefaultDisplayNodes()
      transformedVesselsPiece.CopyContent(cutVesselsList[i])
      transformedVesselsPieceDisplayNode = transformedVesselsPiece.GetDisplayNode()
      transformedVesselsPieceDisplayNode.SetColor(cutVesselsList[i].GetDisplayNode().GetColor())
      transformedVesselsPieceDisplayNode.SetVisibility2D(True)

      mandibleViewNode = slicer.mrmlScene.GetSingletonNode(slicer.MANDIBLE_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
      transformedVesselsPieceDisplayNode.AddViewNodeID(mandibleViewNode.GetID())

      transformedVesselsPiece.SetAndObserveTransformNodeID(vesselsPieceToMandibleAxisTransformNode.GetID())
      transformedVesselsPieceTransformationSuccess = transformedVesselsPiece.HardenTransform()
      if not (transformedVesselsPieceTransformationSuccess):
        Exception('Hardening transforms was not successful')

      moveNodeToFolder(transformedVesselsPiece, transformedVesselsPiecesFolder)
      moveNodeToFolder(vesselsPieceToMandibleAxisTransformNode, vesselsPiecesTransformFolder)

  @saveExecutedMethodWithTelemetry
  def mandiblePlanesPositioningForMaximumBoneContact(self):
    parameterNode = self.getParameterNode()
    mandibularCurve = parameterNode.GetNodeReference("mandibleCurve")
    planeList = createListFromFolderName("Mandibular planes")

    mandiblePlaneTransformsFolder = getFolder("Mandible Planes Transforms")
    
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
      
      moveNodeToFolder(transformNode, mandiblePlaneTransformsFolder)
    
    removeFolder(mandiblePlaneTransformsFolder)
  
  def setupMandiblePlaneStraightOverMandibleCurve(self,planeNode,temporalOrigin, mandibleCurve):
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
    self.planeNodeAndObserver[0].RemoveObserver(self.planeNodeAndObserver[1])
    self.planeNodeAndObserver = []
    planeNode.SetNormal(mandiblePlaneStraightZ)
    planeNode.SetNthControlPointPosition(0,mandiblePlaneStraightOrigin)
    planeNode.SetNthControlPointPosition(1,mandiblePlaneStraightOrigin + mandiblePlaneStraightX*dx)
    planeNode.SetNthControlPointPosition(2,mandiblePlaneStraightOrigin + mandiblePlaneStraightY*dy)

  def createFibulaAxisFromFibulaLineAndRightSideLegChecked(self,fibulaLine,rightSideLegIsDonor):
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
    # make fibulaX always point in the medial direction
    if rightSideLegIsDonor:
      vtk.vtkMath.Cross(fibulaZ, anteriorDirection, fibulaX)
      fibulaX = fibulaX/np.linalg.norm(fibulaX)
    else:
      vtk.vtkMath.Cross(fibulaZ, posteriorDirection, fibulaX)
      fibulaX = fibulaX/np.linalg.norm(fibulaX)
    vtk.vtkMath.Cross(fibulaZ, fibulaX, fibulaY)
    fibulaY = fibulaY/np.linalg.norm(fibulaY)

    return fibulaX, fibulaY, fibulaZ, fibulaOrigin

  def createFibulaAxisFromFibulaLineAndRightSideLegChecked_2(self,lineStartPos,lineEndPos,rightSideLegIsDonor):
    fibulaOrigin = lineStartPos
    fibulaZLineNorm = np.linalg.norm(lineEndPos-lineStartPos)
    fibulaZ = (lineEndPos-lineStartPos)/fibulaZLineNorm
    fibulaX = [0,0,0]
    fibulaY = [0,0,0]
    anteriorDirection = [0,1,0]
    posteriorDirection = [0,-1,0]
    # make fibulaX always point in the medial direction
    if rightSideLegIsDonor:
      vtk.vtkMath.Cross(fibulaZ, anteriorDirection, fibulaX)
      fibulaX = fibulaX/np.linalg.norm(fibulaX)
    else:
      vtk.vtkMath.Cross(fibulaZ, posteriorDirection, fibulaX)
      fibulaX = fibulaX/np.linalg.norm(fibulaX)
    vtk.vtkMath.Cross(fibulaZ, fibulaX, fibulaY)
    fibulaY = fibulaY/np.linalg.norm(fibulaY)

    return fibulaX, fibulaY, fibulaZ, fibulaOrigin
  
  @saveExecutedMethodWithTelemetry
  def createMiterBoxesFromFibulaPlanes(self):
    __unusedVar = None

    parameterNode = self.getParameterNode()
    fibulaLine = parameterNode.GetNodeReference("fibulaLine")
    miterBoxDirectionLine = parameterNode.GetNodeReference("miterBoxDirectionLine")
    
    if (not fibulaLine) or (not miterBoxDirectionLine):
      return
    if (fibulaLine.GetNumberOfControlPoints() < 2) or (miterBoxDirectionLine.GetNumberOfControlPoints() < 2):
      return

    miterBoxSlotWidth = float(parameterNode.GetParameter("miterBoxSlotWidth_mm"))
    miterBoxSlotLength = float(parameterNode.GetParameter("miterBoxSlotLength_mm"))
    miterBoxSlotHeight = float(parameterNode.GetParameter("miterBoxSlotHeight_mm"))
    miterBoxSlotWall = float(parameterNode.GetParameter("miterBoxSlotWall_mm"))
    clearanceFitPrintingTolerance = float(parameterNode.GetParameter("clearanceFitPrintingTolerance_mm"))
    biggerMiterBoxDistanceToFibula = float(parameterNode.GetParameter("biggerMiterBoxDistanceToFibula_mm"))
    securityMarginOfFibulaPieces = float(parameterNode.GetParameter("securityMarginOfFibulaPieces_mm"))
    rightSideLegIsDonor = parameterNode.GetParameter("donorLeg") == "Right"
    checkSecurityMarginOnMiterBoxCreationChecked = parameterNode.GetParameter("checkSecurityMarginOnMiterBoxCreation") == "True"
    useMoreExactVersionOfPositioningAlgorithmChecked = parameterNode.GetParameter("useMoreExactVersionOfPositioningAlgorithm") == "True"
    miterBoxesGuideType = parameterNode.GetParameter("miterBoxesGuideType")
    miterBoxesBoxType = parameterNode.GetParameter("miterBoxesBoxType")
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

    fibulaPlanesList = createListFromFolderName("Fibula planes")

    if checkSecurityMarginOnMiterBoxCreationChecked:
      cutBonesList = createListFromFolderName("Cut Bones")
      duplicateFibulaBonePiecesModelsFolder = getFolder("Duplicate Fibula Bone Pieces")
      duplicateFibulaBonePiecesTransformsFolder = getFolder("Duplicate Fibula Bone Pieces Transforms")
      
      for i in range(0,len(cutBonesList)-1):
        duplicateFibulaPiece = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Duplicate ' + cutBonesList[i].GetName())
        duplicateFibulaPiece.CreateDefaultDisplayNodes()
        duplicateFibulaPiece.CopyContent(cutBonesList[i])

        moveNodeToFolder(duplicateFibulaPiece, duplicateFibulaBonePiecesModelsFolder)

      duplicateFibulaBonePiecesList = createListFromFolderName("Duplicate Fibula Bone Pieces")

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

        moveNodeToFolder(duplicateFibulaPieceTransformNode, duplicateFibulaBonePiecesTransformsFolder)

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
      
      removeFolder(duplicateFibulaBonePiecesTransformsFolder)
      removeFolder(duplicateFibulaBonePiecesModelsFolder)
      if collisionDetected:
        slicer.util.errorDisplay(f"Planned fibula segments could overlap each other (the distance in between them do not satisfy the security margin of {securityMarginOfFibulaPieces}mm). " +
            "You can fix this by increasing 'between space' and pressing the update button")
        return


    biggerMiterBoxesModelsFolder = getFolder("biggerMiterBoxes Models", reset = True)
    rectangletModelsFolder = getFolder("rectanglet Models", reset = True)
    lowResolutionBiggerMiterBoxesModelsFolder = getFolder("lowResolutionBiggerMiterBoxes Models", reset = True)
    if miterBoxesGuideType == "Slot":
      miterBoxesModelsFolder = getFolder("miterBoxes Models", reset = True)
      previewMiterBoxesModelsFolder = getFolder("previewMiterBoxes Models", reset = True)
    miterBoxesTransformsFolder = getFolder("miterBoxes Transforms")
    intersectionsFolder = getFolder("Intersections")
    pointsIntersectionsFolder = getFolder("Points Intersections")

    if not useMoreExactVersionOfPositioningAlgorithmChecked:
      #Create fibula axis:
      fibulaX, fibulaY, fibulaZ, fibulaOrigin = self.createFibulaAxisFromFibulaLineAndRightSideLegChecked(fibulaLine,rightSideLegIsDonor) 

    fibulaViewNode = slicer.mrmlScene.GetSingletonNode(slicer.FIBULA_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")

    obb_tree = build_surface_locator(fibulaModelNode.GetPolyData())
    enc = vtk.vtkSelectEnclosedPoints()
    enc.SetSurfaceData(fibulaModelNode.GetPolyData())
    enc.CheckSurfaceOff()   # skip surface-integrity check for speed

    combineModelsLogic = combineModelsRobustLogic
    for i in range(len(fibulaPlanesList)):
      if useMoreExactVersionOfPositioningAlgorithmChecked:
        lineStartPos = np.zeros(3)
        lineEndPos = np.zeros(3)
        fibulaPlanesList[(i//2)*2].GetOrigin(lineStartPos)
        fibulaPlanesList[(i//2)*2 +1].GetOrigin(lineEndPos)
        #Create fibula axis:
        fibulaX, fibulaY, fibulaZ, fibulaOrigin = self.createFibulaAxisFromFibulaLineAndRightSideLegChecked_2(lineStartPos,lineEndPos,rightSideLegIsDonor)

      #miterBoxModel: the numbers are selected arbitrarily to make a box with the correct size then they'll be GUI set
      if i%2 == 0:
        miterBoxName = "miterBox%d_A" % (i//2)
        biggerMiterBoxName = "biggerMiterBox%d_A" % (i//2)
        previewMiterBoxName = "previewMiterBox%d_A" % (i//2)
      else:
        miterBoxName = "miterBox%d_B" % (i//2)
        biggerMiterBoxName = "biggerMiterBox%d_B" % (i//2)
        previewMiterBoxName = "previewMiterBox%d_B" % (i//2)
      miterBoxWidth = miterBoxSlotWidth+2*clearanceFitPrintingTolerance
      miterBoxLength = miterBoxSlotLength
      miterBoxHeight = 70
      if miterBoxesGuideType == "Slot":
        miterBoxModel, __unusedVar = createBox(miterBoxLength,miterBoxHeight,miterBoxWidth,miterBoxName)
        slicer.mrmlScene.RemoveNode(__unusedVar)

        miterBoxDisplayNode = miterBoxModel.GetDisplayNode()
        miterBoxDisplayNode.SetVisibility(False)
        miterBoxDisplayNode.AddViewNodeID(fibulaViewNode.GetID())

        moveNodeToFolder(miterBoxModel, miterBoxesModelsFolder)

      elif miterBoxesGuideType == "Border":
        pass # not need to create the sawBox

      if miterBoxesGuideType == "Slot":
        biggerMiterBoxWidth = miterBoxSlotWidth+2*clearanceFitPrintingTolerance+2*miterBoxSlotWall
        biggerMiterBoxLength = miterBoxSlotLength+2*miterBoxSlotWall
      elif miterBoxesGuideType == "Border":
        biggerMiterBoxWidth = miterBoxSlotWidth+clearanceFitPrintingTolerance
        biggerMiterBoxLength = miterBoxSlotLength
      
      fibulaPlaneMatrix = vtk.vtkMatrix4x4()
      fibulaPlanesList[i].GetObjectToWorldMatrix(fibulaPlaneMatrix)
      fibulaPlaneZ = np.array([fibulaPlaneMatrix.GetElement(0,2),fibulaPlaneMatrix.GetElement(1,2),fibulaPlaneMatrix.GetElement(2,2)])
      fibulaPlaneOrigin = np.array([fibulaPlaneMatrix.GetElement(0,3),fibulaPlaneMatrix.GetElement(1,3),fibulaPlaneMatrix.GetElement(2,3)])

      lineStartPos = np.zeros(3)
      lineEndPos = np.zeros(3)
      miterBoxDirectionLine.GetNthControlPointPositionWorld(0, lineStartPos)
      miterBoxDirectionLine.GetNthControlPointPositionWorld(1, lineEndPos)
      miterBoxDirection = (lineEndPos-lineStartPos)/np.linalg.norm(lineEndPos-lineStartPos)

      miterBoxAxisX = [0,0,0]
      miterBoxAxisY =  [0,0,0]
      miterBoxAxisZ = fibulaPlaneZ
      if vtk.vtkMath.Dot(fibulaZ, miterBoxAxisZ) < 0:
        miterBoxAxisZ = -miterBoxAxisZ
      vtk.vtkMath.Cross(miterBoxDirection, miterBoxAxisZ, miterBoxAxisX)
      miterBoxAxisX = miterBoxAxisX/np.linalg.norm(miterBoxAxisX)
      vtk.vtkMath.Cross(miterBoxAxisZ, miterBoxAxisX, miterBoxAxisY)
      miterBoxAxisY = miterBoxAxisY/np.linalg.norm(miterBoxAxisY)
      
      biggerMiterBoxHeight = miterBoxSlotHeight
      if miterBoxesBoxType == "Regular":
        biggerMiterBoxModel, rectangletModel = createBox(biggerMiterBoxLength,biggerMiterBoxHeight,biggerMiterBoxWidth,biggerMiterBoxName)
      elif miterBoxesBoxType == "Adapted":
        biggerMiterBoxModel, rectangletModel = createAdaptedBox(
          biggerMiterBoxLength,
          biggerMiterBoxHeight,
          biggerMiterBoxWidth,
          biggerMiterBoxName,
          miterBoxAxisX,
          miterBoxAxisZ,
          fibulaZ,
          highResolution = True
        )
      lowResolutionBiggerMiterBoxModel, __unusedVar = createBox(
        biggerMiterBoxLength,
        biggerMiterBoxHeight,
        biggerMiterBoxWidth,
        biggerMiterBoxName + "_lowRes",
        highResolution=False
      )
      slicer.mrmlScene.RemoveNode(__unusedVar)
      lowResolutionBiggerMiterBoxModel.GetDisplayNode().SetVisibility3D(False)

      biggerMiterBoxDisplayNode = biggerMiterBoxModel.GetDisplayNode()
      biggerMiterBoxDisplayNode.AddViewNodeID(fibulaViewNode.GetID())
      if miterBoxesGuideType == "Slot":
        biggerMiterBoxDisplayNode.SetVisibility3D(False)
      elif miterBoxesGuideType == "Border":
        biggerMiterBoxDisplayNode.SetVisibility3D(True)
      biggerMiterBoxDisplayNode.SetVisibility2D(True)
      if np.linalg.norm(fibulaCentroid-centerOfScalarVolume) < np.linalg.norm(mandibleCentroid-centerOfScalarVolume):
        redSliceNode = slicer.mrmlScene.GetSingletonNode("Red", "vtkMRMLSliceNode")
        biggerMiterBoxDisplayNode.AddViewNodeID(redSliceNode.GetID())
      rectangletDisplayNode = rectangletModel.GetDisplayNode()
      rectangletDisplayNode.SetVisibility(False)

      moveNodeToFolder(biggerMiterBoxModel, biggerMiterBoxesModelsFolder)
      moveNodeToFolder(rectangletModel, rectangletModelsFolder)
      moveNodeToFolder(lowResolutionBiggerMiterBoxModel, lowResolutionBiggerMiterBoxesModelsFolder)

      if miterBoxesGuideType == "Slot":
        # previewMiterBoxes
        previewMiterBoxModel = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", previewMiterBoxName)
        combineModelsLogic.process(
          biggerMiterBoxModel, miterBoxModel, previewMiterBoxModel, 'difference'
        )
        previewMiterBoxDisplayNode = previewMiterBoxModel.GetDisplayNode()
        previewMiterBoxDisplayNode.AddViewNodeID(fibulaViewNode.GetID())

        moveNodeToFolder(previewMiterBoxModel, previewMiterBoxesModelsFolder)

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
      getIntersectionBetweenModelAnd1PlaneWithNormalAndOrigin(intersectionModel,normalToMiterBoxDirectionAndFibulaZ,intersectionModelCentroid,pointsIntersectionModel)
      pointOfIntersection = nearestPointOverLineWithTheVectorDirection(pointsIntersectionModel,miterBoxDirection)
      moveNodeToFolder(intersectionModel, intersectionsFolder)
      moveNodeToFolder(pointsIntersectionModel, pointsIntersectionsFolder)

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

      if miterBoxesGuideType == "Border":
        auxTransform = vtk.vtkTransform()
        auxTransform.PostMultiply()
        if i%2 == 0:
          auxTransform.Translate(0,0,miterBoxSlotWidth)
        else:
          auxTransform.Translate(0,0,-miterBoxSlotWidth)
        miterBoxToWorldChangeOfFrameTransformNode.SetMatrixTransformToParent(auxTransform.GetMatrix())
        biggerMiterBoxModel.SetAndObserveTransformNodeID(miterBoxToWorldChangeOfFrameTransformNode.GetID())
        biggerSawBoxTransformationSuccess = biggerMiterBoxModel.HardenTransform()
        if not (biggerSawBoxTransformationSuccess):
          Exception('Hardening transforms was not successful')
        lowResolutionBiggerMiterBoxModel.SetAndObserveTransformNodeID(miterBoxToWorldChangeOfFrameTransformNode.GetID())
        lowResolutionBiggerMiterBoxTransformationSuccess = lowResolutionBiggerMiterBoxModel.HardenTransform()
        if not (lowResolutionBiggerMiterBoxTransformationSuccess):
          Exception('Hardening transforms was not successful')

      if i%2 == 0:
        miterBoxAxisXTranslation = 0
        miterBoxAxisYTranslation = biggerMiterBoxHeight/2
        miterBoxAxisZTranslation = -miterBoxSlotWidth/2
      else:
        miterBoxAxisXTranslation = 0
        miterBoxAxisYTranslation = biggerMiterBoxHeight/2
        miterBoxAxisZTranslation = miterBoxSlotWidth/2
      


      miterBoxOrigin = pointOfIntersection + miterBoxAxisX*miterBoxAxisXTranslation + miterBoxAxisY*miterBoxAxisYTranslation + miterBoxAxisZ*miterBoxAxisZTranslation
      miterBoxToWorldChangeOfFrameMatrix = self.getAxes1ToWorldChangeOfFrameMatrix(miterBoxAxisX, miterBoxAxisY, miterBoxAxisZ, miterBoxOrigin)


      # iterative rectanglet position correction until no bone collision is detected (in case of collision, the miter box is moved away from the fibula along the miter box direction)

      touchingBone = True
      while touchingBone:
    

        surface_polydata = fibulaModelNode.GetPolyData()

        # transform filter
        transformFilter = vtk.vtkTransformPolyDataFilter()
        transformFilter.SetInputData(rectangletModel.GetPolyData())
        transform = vtk.vtkTransform()
        transform.PostMultiply()
        transform.SetMatrix(miterBoxToWorldChangeOfFrameMatrix)
        transformFilter.SetTransform(transform)
        transformFilter.Update()
        rect_polydata = transformFilter.GetOutput()
        

        touchingBone = False  # reset: assume no collision, prove otherwise
        skipSecondTest = False
        skipThirdTest = False
        # 0. Quick bounding-box rejection (microseconds)
        r_bounds = rect_polydata.GetBounds()
        s_bounds = surface_polydata.GetBounds()
        for axis in range(3):
          if r_bounds[2*axis+1] < s_bounds[2*axis] or r_bounds[2*axis] > s_bounds[2*axis+1]:
            skipSecondTest = True
            skipThirdTest = True
            break

        if not skipSecondTest:
          # 1. Edge-intersection test (each edge is O(log N) with OBBTree)
          hit_pts = vtk.vtkPoints()
          for p1, p2 in rectangles_edges(rect_polydata):
            if obb_tree.IntersectWithLine(p1, p2, hit_pts, None) > 0:
              touchingBone = True
              skipThirdTest = True
              break

        if not skipThirdTest:
          # 2. Check if any rectangle vertex is *inside* the closed surface
          #    (handles case where rectangle is fully contained)
          enc.SetInputData(rect_polydata)
          enc.Update()
          pts = rect_polydata.GetPoints()
          for i in range(pts.GetNumberOfPoints()):
            if enc.IsInside(i):
              touchingBone = True
              break

        if touchingBone:
          miterBoxAxisYTranslation += 0.5
          miterBoxOrigin = pointOfIntersection + miterBoxAxisX*miterBoxAxisXTranslation + miterBoxAxisY*miterBoxAxisYTranslation + miterBoxAxisZ*miterBoxAxisZTranslation
          miterBoxToWorldChangeOfFrameMatrix = self.getAxes1ToWorldChangeOfFrameMatrix(miterBoxAxisX, miterBoxAxisY, miterBoxAxisZ, miterBoxOrigin)




      miterBoxAxisYTranslation += biggerMiterBoxDistanceToFibula
      miterBoxOrigin = pointOfIntersection + miterBoxAxisX*miterBoxAxisXTranslation + miterBoxAxisY*miterBoxAxisYTranslation + miterBoxAxisZ*miterBoxAxisZTranslation
      miterBoxToWorldChangeOfFrameMatrix = self.getAxes1ToWorldChangeOfFrameMatrix(miterBoxAxisX, miterBoxAxisY, miterBoxAxisZ, miterBoxOrigin)



      miterBoxToWorldChangeOfFrameTransformNode.SetMatrixTransformToParent(miterBoxToWorldChangeOfFrameMatrix)
      miterBoxToWorldChangeOfFrameTransformNode.UpdateScene(slicer.mrmlScene)

      biggerMiterBoxModel.SetAndObserveTransformNodeID(miterBoxToWorldChangeOfFrameTransformNode.GetID())
      biggerMiterBoxTransformationSuccess = biggerMiterBoxModel.HardenTransform()
      if not (
        biggerMiterBoxTransformationSuccess
      ):
        Exception('Hardening transforms was not successful')
      rectangletModel.SetAndObserveTransformNodeID(miterBoxToWorldChangeOfFrameTransformNode.GetID())
      rectangletTransformationSuccess = rectangletModel.HardenTransform()
      if not (rectangletTransformationSuccess):
        Exception('Hardening transforms was not successful')
      lowResolutionBiggerMiterBoxModel.SetAndObserveTransformNodeID(miterBoxToWorldChangeOfFrameTransformNode.GetID())
      lowResolutionBiggerMiterBoxTransformationSuccess = lowResolutionBiggerMiterBoxModel.HardenTransform()
      if not (
        lowResolutionBiggerMiterBoxTransformationSuccess
      ):
        Exception('Hardening transforms was not successful')
      
      if miterBoxesGuideType == "Slot":
        miterBoxModel.SetAndObserveTransformNodeID(miterBoxToWorldChangeOfFrameTransformNode.GetID())
        miterBoxTransformationSuccess = miterBoxModel.HardenTransform()
        previewMiterBoxModel.SetAndObserveTransformNodeID(miterBoxToWorldChangeOfFrameTransformNode.GetID())
        previewMiterBoxTransformationSuccess = previewMiterBoxModel.HardenTransform()
        if not (
          miterBoxTransformationSuccess and 
          previewMiterBoxTransformationSuccess
        ):
          Exception('Hardening transforms was not successful')

      moveNodeToFolder(miterBoxToWorldChangeOfFrameTransformNode, miterBoxesTransformsFolder)
    
    removeFolder(miterBoxesTransformsFolder)
    removeFolder(intersectionsFolder)
    removeFolder(pointsIntersectionsFolder)

    parameterNode.SetParameter("miterBoxesNeedUpdate", str(False))

    self.setRedSliceForModelsDisplayNodes()
    self.setRedSliceForMarkupsDisplayNodes()

    self.updateNormalizationFibulaLineTransform(None)

  def generateFibulaGuidebase(self):
    parameterNode = self.getParameterNode()
    fibulaGuidebaseThickness = float(parameterNode.GetParameter("fibulaGuidebaseThickness_mm"))
    fibulaGuidebaseMargin = float(parameterNode.GetParameter("fibulaGuidebaseMargin_mm"))
    fibulaGuidebaseAngle = float(parameterNode.GetParameter("fibulaGuidebaseAngle_mm"))

    fibulaLine = self.getFibulaLine()
    miterBoxDirectionLine = self.getMiterBoxDirectionLine()
    fibulaSegmentation = parameterNode.GetNodeReference("fibulaSegmentation")
    lowResolutionBiggerMiterBoxesModelsList = createListFromFolderName("lowResolutionBiggerMiterBoxes Models")


    projectedPointsStartingBoxPoints, projectedPointsEndingBoxPoints = projectBoxesOverFibulaLine(
      lowResolutionBiggerMiterBoxesModelsList,
      fibulaLine
    )
    distantPoint1, distantPoint2 = getMostDistantPoints(
      projectedPointsStartingBoxPoints, projectedPointsEndingBoxPoints
    )
    distantPoint1 = np.array(distantPoint1)
    distantPoint2 = np.array(distantPoint2)


    middlePoint = (distantPoint1 + distantPoint2)/2
    verticalPlaneNormal1 = middlePoint - distantPoint1
    verticalPlaneNormal1 = verticalPlaneNormal1/np.linalg.norm(verticalPlaneNormal1)
    verticalPlaneNormal2 = middlePoint - distantPoint2
    verticalPlaneNormal2 = verticalPlaneNormal2/np.linalg.norm(verticalPlaneNormal2)
    verticalPlaneOrigin1 = distantPoint1
    verticalPlaneOrigin2 = distantPoint2

    fibulaLineStartPoint = np.zeros(3)
    fibulaLineEndPoint = np.zeros(3)
    fibulaLine.GetNthControlPointPosition(0, fibulaLineStartPoint)
    fibulaLine.GetNthControlPointPosition(1, fibulaLineEndPoint)
    fibulaLineDirection = fibulaLineEndPoint - fibulaLineStartPoint
    fibulaLineDirection = fibulaLineDirection/np.linalg.norm(fibulaLineDirection)

    miterBoxDirectionLineStartPoint = np.zeros(3)
    miterBoxDirectionLineEndPoint = np.zeros(3)
    miterBoxDirectionLine.GetNthControlPointPosition(0, miterBoxDirectionLineStartPoint)
    miterBoxDirectionLine.GetNthControlPointPosition(1, miterBoxDirectionLineEndPoint)
    miterBoxDirectionLineDirection = miterBoxDirectionLineEndPoint - miterBoxDirectionLineStartPoint
    miterBoxDirectionLineDirection = miterBoxDirectionLineDirection/np.linalg.norm(miterBoxDirectionLineDirection)

    correctedMiterBoxDirectionLineDirection = np.zeros(3) 
    auxiliarVector = np.zeros(3)
    vtk.vtkMath.Cross(fibulaLineDirection, miterBoxDirectionLineDirection, auxiliarVector)
    vtk.vtkMath.Cross(auxiliarVector, fibulaLineDirection, correctedMiterBoxDirectionLineDirection)

    rotatedMiterBoxDirectionLine1 = np.zeros(3)
    rotatedMiterBoxDirectionLine2 = np.zeros(3)
    wxyz = np.zeros(4)
    radians = vtk.vtkMath.RadiansFromDegrees(fibulaGuidebaseAngle/2 - 90)
    wxyz[0] = radians
    wxyz[1:] = fibulaLineDirection
    vtk.vtkMath.RotateVectorByWXYZ(
      correctedMiterBoxDirectionLineDirection,
      wxyz,
      rotatedMiterBoxDirectionLine1
    )
    rotatedMiterBoxDirectionLine1 = rotatedMiterBoxDirectionLine1/np.linalg.norm(rotatedMiterBoxDirectionLine1)
    wxyz[0] = -radians
    vtk.vtkMath.RotateVectorByWXYZ(
      correctedMiterBoxDirectionLineDirection,
      wxyz,
      rotatedMiterBoxDirectionLine2
    )
    rotatedMiterBoxDirectionLine2 = rotatedMiterBoxDirectionLine2/np.linalg.norm(rotatedMiterBoxDirectionLine2)

    sidePlane1Normal = rotatedMiterBoxDirectionLine2
    sidePlane2Normal = rotatedMiterBoxDirectionLine1
    sidePlane1Origin = middlePoint
    sidePlane2Origin = middlePoint

    normalsList = [verticalPlaneNormal1, verticalPlaneNormal2, sidePlane1Normal, sidePlane2Normal]
    originsList = [verticalPlaneOrigin1, verticalPlaneOrigin2, sidePlane1Origin, sidePlane2Origin]
    planeCollection = vtk.vtkPlaneCollection()
    for normal, origin in zip(normalsList, originsList):
      plane = vtk.vtkPlane()
      plane.SetNormal(normal)
      plane.SetOrigin(origin)
      planeCollection.AddItem(plane)


    laterality = parameterNode.GetParameter("donorLeg") + " "
    organ = "Fibula"
    hollowWithMarginSegmentID = createHollowWithMargin(
      fibulaSegmentation,
      laterality + organ,
      fibulaGuidebaseMargin,
      fibulaGuidebaseThickness
    )

    hollowWithMarginModel = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", "fibulaHollowWithMarginModel")
    hollowWithMarginModel.CreateDefaultDisplayNodes()

    seg = fibulaSegmentation
    seg.GetSegmentation().CreateRepresentation(slicer.vtkSegmentationConverter.GetSegmentationClosedSurfaceRepresentationName())

    segment = seg.GetSegmentation().GetSegment(hollowWithMarginSegmentID)

    logic = slicer.modules.segmentations.logic()
    # this replaces original model names by segment names
    logic.ExportSegmentToRepresentationNode(segment, hollowWithMarginModel)
    hollowWithMarginModel.SetName(slicer.mrmlScene.GetUniqueNameByString('fibulaHollowWithMarginModel'))
    hollowWithMarginModel.GetDisplayNode().SetVisibility(False)


    clipper = vtk.vtkClipClosedSurface()
    clipper.SetInputData(hollowWithMarginModel.GetPolyData())
    clipper.SetClippingPlanes(planeCollection)
    clipper.InsideOutOff()
    clipper.Update()

    modelsLogic = slicer.modules.models.logic()
    fibulaSurgicalGuideBaseModel = modelsLogic.AddModel(calculateNormals(clipper.GetOutput()))
    fibulaSurgicalGuideBaseModel.SetName(slicer.mrmlScene.GetUniqueNameByString('fibulaSurgicalGuideBaseModel'))
    parameterNode.SetNodeReferenceID("fibulaSurgicalGuideBaseModel", fibulaSurgicalGuideBaseModel.GetID())
    fibulaViewNode = slicer.mrmlScene.GetSingletonNode(slicer.FIBULA_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
    fibulaSurgicalGuideBaseModel.GetDisplayNode().AddViewNodeID(fibulaViewNode.GetID())
    fibulaSurgicalGuideBaseModel.GetDisplayNode().SetVisibility2D(True)
    moveNodeToFolder(fibulaSurgicalGuideBaseModel, getFolder("BoneReconstructionPlanner"))

    slicer.mrmlScene.RemoveNode(hollowWithMarginModel)

    self.updateNormalizationFibulaLineTransform(None)
  
  def createDentalImplantCylindersFiducialList(self):
    dentalImplantCylindersFiducialsListsFolder = getFolder("Dental Implants Cylinders Fiducials", reset = True)
    
    dentalImplantFiducialListNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLMarkupsFiducialNode")
    dentalImplantFiducialListNode.SetName("temp")
    slicer.mrmlScene.AddNode(dentalImplantFiducialListNode)
    slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(dentalImplantFiducialListNode)
    moveNodeToFolder(dentalImplantFiducialListNode, dentalImplantCylindersFiducialsListsFolder)
    dentalImplantFiducialListNode.SetName(slicer.mrmlScene.GetUniqueNameByString("dentalImplantCylindersFiducialsList"))

    displayNode = dentalImplantFiducialListNode.GetDisplayNode()
    mandibleViewNode = slicer.mrmlScene.GetSingletonNode(slicer.MANDIBLE_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
    displayNode.AddViewNodeID(mandibleViewNode.GetID())

    #setup placement
    slicer.modules.markups.logic().SetActiveListID(dentalImplantFiducialListNode)
    interactionNode = slicer.mrmlScene.GetNodeByID("vtkMRMLInteractionNodeSingleton")
    interactionNode.SwitchToPersistentPlaceMode()

  def getCurrentFibulaModel(self):
    parameterNode = self.getParameterNode()
    useNonDecimatedModelsForPreviewChecked = parameterNode.GetParameter("useNonDecimatedModelsForPreview") == "True"
    
    if useNonDecimatedModelsForPreviewChecked:
      fibulaModelNode = parameterNode.GetNodeReference("fibulaModelNode")
    else:
      fibulaModelNode = parameterNode.GetNodeReference("decimatedFibulaModelNode")
    
    return fibulaModelNode

  def getCurrentVesselsModel(self):
    parameterNode = self.getParameterNode()
    useNonDecimatedModelsForPreviewChecked = parameterNode.GetParameter("useNonDecimatedModelsForPreview") == "True"
    
    vesselsModelNode = parameterNode.GetNodeReference("vesselsModelNode")
    decimatedVesselsModelNode = parameterNode.GetNodeReference("decimatedVesselsModelNode")
    if vesselsModelNode and decimatedVesselsModelNode:
      if useNonDecimatedModelsForPreviewChecked:
        currentVesselsModelNode = vesselsModelNode
      else:
        currentVesselsModelNode = decimatedVesselsModelNode
    else:
      currentVesselsModelNode = None

    return currentVesselsModelNode

  def getCurrentMandibleModel(self):
    parameterNode = self.getParameterNode()
    useNonDecimatedModelsForPreviewChecked = parameterNode.GetParameter("useNonDecimatedModelsForPreview") == "True"
    
    if useNonDecimatedModelsForPreviewChecked:
      mandibleModelNode = parameterNode.GetNodeReference("mandibleModelNode")
    else:
      mandibleModelNode = parameterNode.GetNodeReference("decimatedMandibleModelNode")

    return mandibleModelNode

  @saveExecutedMethodWithTelemetry
  def createCylindersFromFiducialListAndFibulaSurgicalGuideBase(self):
    fibulaCylindersModelsFolder = getFolder("Fibula Cylinders Models", reset = True)
    cylindersTransformsFolder = getFolder("Cylinders Transforms")
    
    parameterNode = self.getParameterNode()
    fibulaFiducialList = self.getFibulaFiducials()
    fibulaSurgicalGuideBaseModel = parameterNode.GetNodeReference("fibulaSurgicalGuideBaseModel")
    if fibulaSurgicalGuideBaseModel is None:
      fibulaSurgicalGuideBaseModel = self.getCurrentFibulaModel() # we are just reading a normal
    fibulaScrewHoleCylinderRadius = float(parameterNode.GetParameter("fibulaScrewHoleCylinderRadius_mm"))

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
      moveNodeToFolder(cylinderModel, fibulaCylindersModelsFolder)
      
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

      displayNode = cylinderModel.GetDisplayNode()
      displayNode.AddViewNodeID(slicer.FIBULA_VIEW_ID)

      moveNodeToFolder(cylinderToWorldChangeOfFrameTransformNode, cylindersTransformsFolder)
    
    removeFolder(cylindersTransformsFolder)
  
  @saveExecutedMethodWithTelemetry
  def createCylindersFromFiducialListAndMandibleSurgicalGuideBase(self):
    mandibleCylindersModelsFolder = getFolder("Mandible Cylinders Models", reset = True)
    cylindersTransformsFolder = getFolder("Cylinders Transforms")
    
    parameterNode = self.getParameterNode()
    mandibleFiducialList = self.getMandibleFiducials()
    mandibleSurgicalGuideBaseModel = parameterNode.GetNodeReference("mandibleSurgicalGuideBaseModel")
    if mandibleSurgicalGuideBaseModel is None:
      mandibleSurgicalGuideBaseModel = self.getCurrentMandibleModel() # we are just reading a normal
    mandibleScrewHoleCylinderRadius = float(parameterNode.GetParameter("mandibleScrewHoleCylinderRadius_mm"))

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
      moveNodeToFolder(cylinderModel, mandibleCylindersModelsFolder)
      
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
      
      displayNode = cylinderModel.GetDisplayNode()
      displayNode.AddViewNodeID(slicer.MANDIBLE_VIEW_ID)
      
      moveNodeToFolder(cylinderToWorldChangeOfFrameTransformNode, cylindersTransformsFolder)

    removeFolder(cylindersTransformsFolder)

  def createCylindersFromFiducialListAndNeomandiblePieces(self):
    #self.create3DModelOfTheReconstruction()

    parameterNode = self.getParameterNode()
    mandibularCurve = parameterNode.GetNodeReference("mandibleCurve")
    mandibleReconstructionModel = parameterNode.GetNodeReference("mandibleReconstructionModel")
    dentalImplantsFiducialList = parameterNode.GetNodeReference("dentalImplantsFiducialList")
    dentalImplantCylinderRadius = float(parameterNode.GetParameter("dentalImplantCylinderRadius_mm"))
    dentalImplantCylinderHeight = float(parameterNode.GetParameter("dentalImplantCylinderHeight_mm"))
    dentalImplantDrillGuideWall = float(parameterNode.GetParameter("dentalImplantDrillGuideWall_mm"))

    #mandibleReconstructionModelDisplayNode = mandibleReconstructionModel.GetDisplayNode()
    #mandibleReconstructionModelDisplayNode.SetVisibility(False)

    dentalImplantsCylindersModelsFolder = getFolder("Dental Implants Cylinders Models", reset = True)
    dentalImplantsPlanesFolder = getFolder("dentalImplants Planes", reset = True)
    dentalImplantsCylindersTransformsFolder = getFolder("Dental Implants Cylinders Transforms", reset = True)
    fibulaDentalImplantsCylindersModelsFolder = getFolder("Fibula Dental Implants Cylinders Models", reset = True)
    biggerFibulaDentalImplantsCylindersModelsFolder = getFolder("Bigger Fibula Dental Implants Cylinders Models", reset = True)
    
    transformedFibulaPiecesList = createListFromFolderName("Transformed Fibula Pieces")

    noCapsTransformedFibulaPiecesFolder = getFolder("No Caps Transformed Fibula Pieces", reset = True)

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
      moveNodeToFolder(noCapsTransformedFibulaPiece, noCapsTransformedFibulaPiecesFolder)

    noCapsTransformedFibulaPiecesList = createListFromFolderName("No Caps Transformed Fibula Pieces")
    
    mandibleViewNode = slicer.mrmlScene.GetSingletonNode(slicer.MANDIBLE_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
    fibulaViewNode = slicer.mrmlScene.GetSingletonNode(slicer.FIBULA_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")

    aux = slicer.mrmlScene.GetNodeByID('vtkMRMLColorTableNodeFileMediumChartColors.txt')
    colorTable = aux.GetLookupTable()
    ind = 0# Because it is the last color fibula segments will take
    colorwithalpha = colorTable.GetTableValue(ind)
    color = [colorwithalpha[0],colorwithalpha[1],colorwithalpha[2]]

    for i in range(dentalImplantsFiducialList.GetNumberOfControlPoints()):
      dentalImplantCylinderModel = createCylinder("implantCylinder%d" % i,dentalImplantCylinderRadius,dentalImplantCylinderHeight)
      moveNodeToFolder(dentalImplantCylinderModel, dentalImplantsCylindersModelsFolder)

      dentalImplantCylinderDisplayNode = dentalImplantCylinderModel.GetDisplayNode()
      dentalImplantCylinderDisplayNode.AddViewNodeID(mandibleViewNode.GetID())
      dentalImplantCylinderDisplayNode.SetColor(color)

      fibulaDentalImplantCylinderModel = createCylinder("fibulaImplantCylinder%d" % i,dentalImplantCylinderRadius)
      moveNodeToFolder(fibulaDentalImplantCylinderModel, fibulaDentalImplantsCylindersModelsFolder)
      
      fibulaDentalImplantCylinderDisplayNode = fibulaDentalImplantCylinderModel.GetDisplayNode()
      fibulaDentalImplantCylinderDisplayNode.AddViewNodeID(fibulaViewNode.GetID())
      fibulaDentalImplantCylinderDisplayNode.SetVisibility(False)
      fibulaDentalImplantCylinderDisplayNode.SetColor(color)

      biggerFibulaDentalImplantCylinderModel = createCylinder("biggerFibulaImplantCylinder%d" % i,dentalImplantCylinderRadius + dentalImplantDrillGuideWall,dentalImplantCylinderHeight)
      moveNodeToFolder(biggerFibulaDentalImplantCylinderModel, biggerFibulaDentalImplantsCylindersModelsFolder)
      
      biggerFibulaDentalImplantCylinderDisplayNode = biggerFibulaDentalImplantCylinderModel.GetDisplayNode()
      biggerFibulaDentalImplantCylinderDisplayNode.AddViewNodeID(fibulaViewNode.GetID())
      biggerFibulaDentalImplantCylinderDisplayNode.SetVisibility(False)
      biggerFibulaDentalImplantCylinderDisplayNode.SetColor(color)

      #Create dentalImplant plane
      dentalImplantPlane = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsPlaneNode", "dentalImplant Plane%d" % i)
      slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(dentalImplantPlane)
      moveNodeToFolder(dentalImplantPlane, dentalImplantsPlanesFolder)

      dentalImplantPlane.SetAxes([1,0,0],[0,1,0],[0,0,1])
      dentalImplantPlane.SetOrigin([0,0,0])
      dentalImplantPlane.SetAttribute("isDentalImplantPlane","True")
      dentalImplantPlane.SetPlaneType(slicer.vtkMRMLMarkupsPlaneNode.PlaneType3Points)

      displayNode = dentalImplantPlane.GetDisplayNode()
      mandibleViewNode = slicer.mrmlScene.GetSingletonNode(slicer.MANDIBLE_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
      displayNode.AddViewNodeID(mandibleViewNode.GetID())
      displayNode.SetGlyphScale(slicer.PLANE_GLYPH_SCALE)
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
      
      moveNodeToFolder(dentalImplantCylinderTransformNode, dentalImplantsCylindersTransformsFolder)

      observer = dentalImplantPlane.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent,self.onDentalImplantPlaneMoved)
      self.dentalImplantPlaneObserversPlaneNodeIDAndTransformIDList.append([observer,dentalImplantPlane.GetID(),dentalImplantCylinderTransformNode.GetID()])

    self.setRedSliceForMarkupsDisplayNodes()

    self.onUpdateFibulaDentalImplantsTimerTimeout()

  def onUpdateFibulaDentalImplantsTimerTimeout(self):
    #check if self.mandibleToFibulaRegistrationTransformMatricesList exists, if not, create it
    if len(self.mandibleToFibulaRegistrationTransformMatricesList) == 0:
      mandibleToFibulaRegistrationTransformNodesList = createListFromFolderName("Mandible2Fibula transforms")
      if len(mandibleToFibulaRegistrationTransformNodesList) != 0:
        for i in range(len(mandibleToFibulaRegistrationTransformNodesList)):
          mandibleToFibulaRegistrationMatrix = vtk.vtkMatrix4x4()
          mandibleToFibulaRegistrationTransformNodesList[i].GetMatrixTransformToParent(mandibleToFibulaRegistrationMatrix)
          self.mandibleToFibulaRegistrationTransformMatricesList.append(mandibleToFibulaRegistrationMatrix)
      else:
        self.generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandible()

    #Check collision of dentalImplantCylinder with cutBones, create/update a transform and apply it to cylinders
    fibulaDentalImplantsCylindersTransformsFolder = getFolder("Fibula Dental Implants Cylinders Transforms", reset = True)

    transformedFibulaPiecesList = createListFromFolderName("Transformed Fibula Pieces")
    dentalImplantsCylindersModelsList = createListFromFolderName("Dental Implants Cylinders Models")
    fibulaDentalImplantsCylindersModelsList = createListFromFolderName("Fibula Dental Implants Cylinders Models")
    biggerFibulaDentalImplantsCylindersModelsList = createListFromFolderName("Bigger Fibula Dental Implants Cylinders Models")
    fibulaPlanesList = createListFromFolderName("Fibula planes")
    mandiblePlanesList = createListFromFolderName("Mandibular planes")

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
      
      moveNodeToFolder(fibulaDentalImplantCylinderTransformNode, fibulaDentalImplantsCylindersTransformsFolder)

    self.updateNormalizationFibulaLineTransform(None)
  
  @saveExecutedMethodWithTelemetry
  def makeBooleanOperationsToFibulaSurgicalGuideBase(self):
    parameterNode = self.getParameterNode()
    fibulaSurgicalGuideBaseModel = parameterNode.GetNodeReference("fibulaSurgicalGuideBaseModel")
    dentalImplantsPlanningAndFibulaDrillGuidesChecked = parameterNode.GetParameter("dentalImplantsPlanningAndFibulaDrillGuides") == "True"

    cylindersModelsList = createListFromFolderName("Fibula Cylinders Models")
    miterBoxesModelsList = createListFromFolderName("miterBoxes Models")
    biggerMiterBoxesModelsList = createListFromFolderName("biggerMiterBoxes Models")
    fibulaDentalImplantsCylindersModelsList = createListFromFolderName("Fibula Dental Implants Cylinders Models")
    biggerFibulaDentalImplantsCylindersModelsList = createListFromFolderName("Bigger Fibula Dental Implants Cylinders Models")

    combineModelsLogic = combineModelsRobustLogic

    surgicalGuideModel = slicer.modules.models.logic().AddModel(fibulaSurgicalGuideBaseModel.GetPolyData())
    surgicalGuideModel.SetName(slicer.mrmlScene.GetUniqueNameByString('FibulaSurgicalGuidePrototype'))
    parentFolder = getFolder("Mandible reconstruction")
    moveNodeToFolder(surgicalGuideModel, parentFolder)

    displayNode = surgicalGuideModel.GetDisplayNode()
    fibulaViewNode = slicer.mrmlScene.GetSingletonNode(slicer.FIBULA_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
    displayNode.AddViewNodeID(fibulaViewNode.GetID())
    displayNode.SetColor(slicer.SURGICAL_GUIDE_COLOR)

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

    if (
      surgicalGuideModel.GetPolyData().GetNumberOfPoints() <
      fibulaSurgicalGuideBaseModel.GetPolyData().GetNumberOfPoints()
    ):
      slicer.mrmlScene.RemoveNode(surgicalGuideModel)
      slicer.util.errorDisplay("ERROR: Boolean operations to make fibula surgical guide failed")
      return
    
    parameterNode.SetParameter("fibulaSurgicalGuideElementsVisible", str(False))
    parameterNode.SetParameter("fibulaSurgicalGuideVisible", str(True))
    parameterNode.SetNodeReferenceID("fibulaSurgicalGuidePrototypeModel", surgicalGuideModel.GetID())

    self.updateNormalizationFibulaLineTransform(None)

  def createSawBoxesFromFirstAndLastMandiblePlanes(self):
    parameterNode = self.getParameterNode()
    mandibularCurve = parameterNode.GetNodeReference("mandibleCurve")
    sawBoxSlotWidth = float(parameterNode.GetParameter("sawBoxSlotWidth_mm"))
    sawBoxSlotLength = float(parameterNode.GetParameter("sawBoxSlotLength_mm"))
    sawBoxSlotHeight = float(parameterNode.GetParameter("sawBoxSlotHeight_mm"))
    sawBoxSlotWall = float(parameterNode.GetParameter("sawBoxSlotWall_mm"))
    clearanceFitPrintingTolerance = float(parameterNode.GetParameter("clearanceFitPrintingTolerance_mm"))
    biggerSawBoxDistanceToMandible = float(parameterNode.GetParameter("biggerSawBoxDistanceToMandible_mm"))
    mandibleModelNode = parameterNode.GetNodeReference("mandibleModelNode")
    kindOfMandibleResection = parameterNode.GetParameter("kindOfMandibleResection")
    sawBoxesGuideType = parameterNode.GetParameter("sawBoxesGuideType")
    
    mandibularPlanesList = createListFromFolderName("Mandibular planes")

    if len(mandibularPlanesList) < 2:
      return
    
    if kindOfMandibleResection == "Segmental Mandibulectomy":
      resectionPlanesList = [mandibularPlanesList[0],mandibularPlanesList[-1]]
    elif kindOfMandibleResection == "Hemimandibulectomy":
      rightMandiblePlane, leftMandiblePlane = self.getRightAndLeftMandibleResectionPlanes()
      mandibleSideToRemove = parameterNode.GetParameter("mandibleSideToRemove")
      if mandibleSideToRemove == "Removing right side":
        resectionPlanesList = [leftMandiblePlane]
      elif mandibleSideToRemove == "Removing left side":
        resectionPlanesList = [rightMandiblePlane]
    
    biggerSawBoxesModelsFolder = getFolder("biggerSawBoxes Models", reset = True)
    if sawBoxesGuideType == "Slot":  
      sawBoxesModelsFolder = getFolder("sawBoxes Models", reset = True)
      previewSawBoxesModelsFolder = getFolder("previewSawBoxes Models", reset = True)
    sawBoxesPlanesFolder = getFolder("sawBoxes Planes", reset = True)
    sawBoxesTransformsFolder = getFolder("sawBoxes Transforms", reset = True)
    intersectionsFolder = getFolder("Intersections", reset = True)
    pointsIntersectionsFolder = getFolder("Points Intersections", reset = True)

    mandibleViewNode = slicer.mrmlScene.GetSingletonNode(slicer.MANDIBLE_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")

    #get best fitting plane to curve with curveCrescent normal direction
    curvePoints = slicer.util.arrayFromMarkupsCurvePoints(mandibularCurve)
    if len(curvePoints) <= 2:
      bestFittingPlaneNormalOfCurvePoints = np.array([0,0,1])
    else:
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


    combineModelsLogic = combineModelsRobustLogic
    for i in range(len(resectionPlanesList)):
      #sawBoxModel: the numbers are selected arbitrarily to make a box with the correct size then they'll be GUI set
      if i == 0:
        sawBoxName = "sawBox_%d" % i
        biggerSawBoxName = "biggerSawBox%d" % i
        previewSawBoxName = "previewSawBox%d" % i
      else:
        sawBoxName = "sawBox_%d" % (len(mandibularPlanesList)-1)
        biggerSawBoxName = "biggerSawBox%d" % (len(mandibularPlanesList)-1)
        previewSawBoxName = "previewSawBox%d" % (len(mandibularPlanesList)-1)
      sawBoxWidth = sawBoxSlotWidth+2*clearanceFitPrintingTolerance
      sawBoxLength = sawBoxSlotLength
      sawBoxHeight = 70
      if sawBoxesGuideType == "Slot":
        sawBoxModel, __unusedVar = createBox(sawBoxLength,sawBoxHeight,sawBoxWidth,sawBoxName)
        slicer.mrmlScene.RemoveNode(__unusedVar)
        moveNodeToFolder(sawBoxModel, sawBoxesModelsFolder)

        sawBoxDisplayNode = sawBoxModel.GetDisplayNode()
        sawBoxDisplayNode.AddViewNodeID(mandibleViewNode.GetID())
        sawBoxDisplayNode.SetVisibility(False)
      
      elif sawBoxesGuideType == "Border":
        pass # not need to create the sawBox


      if sawBoxesGuideType == "Slot":
        biggerSawBoxWidth = sawBoxSlotWidth+2*clearanceFitPrintingTolerance+2*sawBoxSlotWall
        biggerSawBoxLength = sawBoxSlotLength+2*sawBoxSlotWall
      elif sawBoxesGuideType == "Border":
        biggerSawBoxWidth = sawBoxSlotWidth+clearanceFitPrintingTolerance
        biggerSawBoxLength = sawBoxSlotLength
      biggerSawBoxHeight = sawBoxSlotHeight
      biggerSawBoxModel, __unusedVar = createBox(biggerSawBoxLength,biggerSawBoxHeight,biggerSawBoxWidth,biggerSawBoxName)
      slicer.mrmlScene.RemoveNode(__unusedVar)
      moveNodeToFolder(biggerSawBoxModel, biggerSawBoxesModelsFolder)

      biggerSawBoxDisplayNode = biggerSawBoxModel.GetDisplayNode()
      biggerSawBoxDisplayNode.AddViewNodeID(mandibleViewNode.GetID())

      if sawBoxesGuideType == "Slot":
        # previewSawBoxes
        previewSawBoxModel = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", previewSawBoxName)
        combineModelsLogic.process(biggerSawBoxModel, sawBoxModel, previewSawBoxModel, 'difference')
        previewSawBoxDisplayNode = previewSawBoxModel.GetDisplayNode()
        previewSawBoxDisplayNode.AddViewNodeID(mandibleViewNode.GetID())

        moveNodeToFolder(previewSawBoxModel, previewSawBoxesModelsFolder)

      #Create sawBox plane
      sawBoxPlane = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsPlaneNode", "sawBox Plane%d" % i)
      slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(sawBoxPlane)
      moveNodeToFolder(sawBoxPlane, sawBoxesPlanesFolder)
      biggerSawBoxDisplayNode.SetVisibility2D(True)
      if sawBoxesGuideType == "Slot":
        biggerSawBoxDisplayNode.SetVisibility3D(False)
      elif sawBoxesGuideType == "Border":
        biggerSawBoxDisplayNode.SetVisibility3D(True)

      sawBoxPlane.SetAxes([1,0,0],[0,1,0],[0,0,1])
      sawBoxPlane.SetOrigin([0,0,0])
      sawBoxPlane.SetAttribute("isSawBoxPlane","True")
      sawBoxPlane.SetPlaneType(slicer.vtkMRMLMarkupsPlaneNode.PlaneType3Points)

      displayNode = sawBoxPlane.GetDisplayNode()
      mandibleViewNode = slicer.mrmlScene.GetSingletonNode(slicer.MANDIBLE_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
      displayNode.AddViewNodeID(mandibleViewNode.GetID())
      displayNode.SetGlyphScale(slicer.PLANE_GLYPH_SCALE)
      displayNode.SetOpacity(0)
      displayNode.HandlesInteractiveOn()
      displayNode.RotationHandleVisibilityOn()
      displayNode.TranslationHandleVisibilityOn()
      displayNode.ScaleHandleVisibilityOff()
      displayNode.SetTranslationHandleComponentVisibility(True,True,False,False)
      displayNode.SetRotationHandleComponentVisibility(False,False,True,False)

      mandiblePlaneMatrix = vtk.vtkMatrix4x4()
      resectionPlanesList[i].GetObjectToWorldMatrix(mandiblePlaneMatrix)
      mandiblePlaneZ = np.array([mandiblePlaneMatrix.GetElement(0,2),mandiblePlaneMatrix.GetElement(1,2),mandiblePlaneMatrix.GetElement(2,2)])
      
      if i == 0:
        intersectionModel = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Intersection%d' % i)
      else:
        intersectionModel = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Intersection%d' % (len(mandibularPlanesList)-1))
      intersectionModel.CreateDefaultDisplayNodes()
      getFurthestIntersectionBetweenModelAnd1Plane(mandibleModelNode,resectionPlanesList[i],intersectionModel)
      
      curvePlanarConvexityDirection = [0,0,0]
      vtk.vtkMath.Cross(mandiblePlaneZ, bestFittingPlaneNormalOfCurvePoints, curvePlanarConvexityDirection)

      if intersectionModel.GetPolyData().GetNumberOfPoints() != 0:
        intersectionModelCentroid = getCentroid(intersectionModel)
        if i == 0:
          pointsIntersectionModel = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Points Intersection%d' % i)
        else:
          pointsIntersectionModel = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Points Intersection%d' % (len(mandibularPlanesList)-1))
        pointsIntersectionModel.CreateDefaultDisplayNodes()
        getIntersectionBetweenModelAnd1PlaneWithNormalAndOrigin(intersectionModel,bestFittingPlaneNormalOfCurvePoints,intersectionModelCentroid,pointsIntersectionModel)
        if pointsIntersectionModel.GetPolyData().GetNumberOfPoints() != 0:
          pointOfIntersection = nearestPointOverLineWithTheVectorDirection(pointsIntersectionModel,curvePlanarConvexityDirection)
        else:
          pointOfIntersection = intersectionModelCentroid
      else:
        pointOfIntersection = [0,0,0]
        resectionPlanesList[i].GetOrigin(pointOfIntersection)
      moveNodeToFolder(intersectionModel, intersectionsFolder)
      moveNodeToFolder(pointsIntersectionModel, pointsIntersectionsFolder)

      # Y is contralingual
      # Z is curve crescent (and normal of the mandible plane)
      # X is inferior
      sawBoxAxisX = [0,0,0]
      sawBoxAxisY =  [0,0,0]
      sawBoxAxisZ = mandiblePlaneZ
      vtk.vtkMath.Cross(sawBoxAxisZ, bestFittingPlaneNormalOfCurvePoints, sawBoxAxisY)
      sawBoxAxisY = sawBoxAxisY/np.linalg.norm(sawBoxAxisY)
      vtk.vtkMath.Cross(sawBoxAxisY, sawBoxAxisZ, sawBoxAxisX)
      sawBoxAxisX = sawBoxAxisX/np.linalg.norm(sawBoxAxisX)

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

      if sawBoxesGuideType == "Border":
        auxTransform = vtk.vtkTransform()
        auxTransform.PostMultiply()
        if i == 0:
          auxTransform.Translate(0,0,-sawBoxSlotWidth)
        else:
          auxTransform.Translate(0,0,sawBoxSlotWidth)
        transformNode.SetMatrixTransformToParent(auxTransform.GetMatrix())
        biggerSawBoxModel.SetAndObserveTransformNodeID(transformNode.GetID())
        biggerSawBoxTransformationSuccess = biggerSawBoxModel.HardenTransform()
        if not (biggerSawBoxTransformationSuccess):
          Exception('Hardening transforms was not successful')

      sawBoxPlaneToWorldMatrix = vtk.vtkMatrix4x4()
      sawBoxPlane.GetObjectToWorldMatrix(sawBoxPlaneToWorldMatrix)
      transformNode.SetMatrixTransformToParent(sawBoxPlaneToWorldMatrix)

      transformNode.UpdateScene(slicer.mrmlScene)

      biggerSawBoxModel.SetAndObserveTransformNodeID(transformNode.GetID())
      if sawBoxesGuideType == "Slot":
        sawBoxModel.SetAndObserveTransformNodeID(transformNode.GetID())
        previewSawBoxModel.SetAndObserveTransformNodeID(transformNode.GetID())
      
      moveNodeToFolder(transformNode, sawBoxesTransformsFolder)

      observer = sawBoxPlane.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent,self.onSawBoxPlaneMoved)
      self.sawBoxPlaneObserversPlaneNodeIDAndTransformIDList.append([observer,sawBoxPlane.GetID(),transformNode.GetID()])

    removeFolder(intersectionsFolder)
    removeFolder(pointsIntersectionsFolder)
    
    self.setRedSliceForModelsDisplayNodes()
    self.setRedSliceForMarkupsDisplayNodes()

    parameterNode.SetParameter("sawBoxesNeedUpdate", str(False))

    parameterNode.SetParameter("showBiggerSawBoxesInteractionHandles","True")
    
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

  @saveExecutedMethodWithTelemetry
  def makeBooleanOperationsToMandibleSurgicalGuideBase(self):
    parameterNode = self.getParameterNode()
    mandibleSurgicalGuideBaseModel = parameterNode.GetNodeReference("mandibleSurgicalGuideBaseModel")
    bothSidesMandibleGuideBaseModel = parameterNode.GetNodeReference("bothSidesMandibleGuideBaseModel")
    useMandibleGuideBasesFromCurves = parameterNode.GetParameter("useMandibleGuideBasesFromCurves") == "True"

    if useMandibleGuideBasesFromCurves:
      mandibleSurgicalGuideBaseModel = bothSidesMandibleGuideBaseModel

    mandibleBridgeModel = parameterNode.GetNodeReference("mandibleBridgeTube")
    
    kindOfMandibleResection = parameterNode.GetParameter("kindOfMandibleResection")

    cylindersModelsList = createListFromFolderName("Mandible Cylinders Models")
    sawBoxesModelsList = createListFromFolderName("sawBoxes Models")
    biggerSawBoxesModelsList = createListFromFolderName("biggerSawBoxes Models")

    combineModelsLogic = combineModelsRobustLogic

    surgicalGuideModel = slicer.modules.models.logic().AddModel(mandibleSurgicalGuideBaseModel.GetPolyData())
    surgicalGuideModel.SetName(slicer.mrmlScene.GetUniqueNameByString('MandibleSurgicalGuidePrototype'))
    parentFolder = getFolder("Mandible reconstruction")
    moveNodeToFolder(surgicalGuideModel, parentFolder)

    displayNode = surgicalGuideModel.GetDisplayNode()
    mandibleViewNode = slicer.mrmlScene.GetSingletonNode(slicer.MANDIBLE_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
    displayNode.AddViewNodeID(mandibleViewNode.GetID())

    self.filterOutUnconnectedModelPiecesAccordingToKindOfMandibleResection(surgicalGuideModel)

    for i in range(len(biggerSawBoxesModelsList)):
      combineModelsLogic.process(surgicalGuideModel, biggerSawBoxesModelsList[i], surgicalGuideModel, 'union')
    
    if (
      mandibleBridgeModel and 
      (kindOfMandibleResection == "Segmental Mandibulectomy")
    ):
      combineModelsLogic.process(surgicalGuideModel, mandibleBridgeModel, surgicalGuideModel, 'union')
    
    for i in range(len(cylindersModelsList)):
      combineModelsLogic.process(surgicalGuideModel, cylindersModelsList[i], surgicalGuideModel, 'difference')
    
    for i in range(len(sawBoxesModelsList)):
      combineModelsLogic.process(surgicalGuideModel, sawBoxesModelsList[i], surgicalGuideModel, 'difference')

    if surgicalGuideModel.GetPolyData().GetNumberOfPoints() == 0:
      slicer.mrmlScene.RemoveNode(surgicalGuideModel)
      slicer.util.errorDisplay("ERROR: Boolean operations to make mandible surgical failed")
      return

    parameterNode.SetParameter("mandibleSurgicalGuideElementsVisible", str(False))
    parameterNode.SetParameter("mandibleSurgicalGuideVisible", str(True))
    parameterNode.SetNodeReferenceID("mandibleSurgicalGuidePrototypeModel", surgicalGuideModel.GetID())

  def getRightAndLeftMandibleResectionPlanes(self):
    parameterNode = self.getParameterNode()
    mandibleModelNode = parameterNode.GetNodeReference("mandibleModelNode")
    mandibleCentroid = getCentroid(mandibleModelNode)

    planeList = createListFromFolderName("Mandibular planes")
    
    firstMandiblePlaneOrigin = np.zeros(3)
    planeList[0].GetNthControlPointPosition(0,firstMandiblePlaneOrigin)
    lastMandiblePlaneOrigin = np.zeros(3)
    planeList[-1].GetNthControlPointPosition(0,lastMandiblePlaneOrigin)
    centroidToFirstPlane = firstMandiblePlaneOrigin - mandibleCentroid
    centroidToLastPlane = lastMandiblePlaneOrigin - mandibleCentroid
    crossProductResult = np.zeros(3)
    vtk.vtkMath.Cross(centroidToFirstPlane,centroidToLastPlane,crossProductResult)
    crossProductResult = crossProductResult/np.linalg.norm(crossProductResult)
    
    superiorDirection = np.zeros(3)
    superiorDirection[2] = 1

    mandiblePlanesDrawnRightToLeft = (crossProductResult @ superiorDirection) > 0

    if mandiblePlanesDrawnRightToLeft:
      rightPlaneOrigin = firstMandiblePlaneOrigin
      leftPlaneOrigin = lastMandiblePlaneOrigin
      rightPlane = planeList[0]
      leftPlane = planeList[-1]
    else:
      rightPlaneOrigin = lastMandiblePlaneOrigin
      leftPlaneOrigin = firstMandiblePlaneOrigin
      rightPlane = planeList[-1]
      leftPlane = planeList[0]

    #return rightPlaneOrigin, leftPlaneOrigin
    return rightPlane, leftPlane

  @saveExecutedMethodWithTelemetry
  def centerFibulaLine(self):
    parameterNode = self.getParameterNode()
    fibulaLine = parameterNode.GetNodeReference("fibulaLine")
    fibulaModelNode = parameterNode.GetNodeReference("fibulaModelNode")

    intersectionsFolder = getFolder("Intersections")

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

      moveNodeToFolder(fibulaStartIntersectionModel, intersectionsFolder)
      moveNodeToFolder(fibulaEndIntersectionModel, intersectionsFolder)

      getIntersectionBetweenModelAnd1PlaneWithNormalAndOrigin(fibulaModelNode,fibulaLineDirection,lineStartPos,fibulaStartIntersectionModel)
      getIntersectionBetweenModelAnd1PlaneWithNormalAndOrigin(fibulaModelNode,fibulaLineDirection,lineEndPos,fibulaEndIntersectionModel)
      lineStartPos = getCentroid(fibulaStartIntersectionModel)
      lineEndPos = getCentroid(fibulaEndIntersectionModel)
      if lineStartPos is None or lineEndPos is None:
        removeFolder(intersectionsFolder)
        raise slicer.util.errorDisplay("ERROR: Line has invalid direction, please re-draw it")

    fibulaLine.SetNthControlPointPosition(0,lineStartPos)
    fibulaLine.SetNthControlPointPosition(1,lineEndPos)

    removeFolder(intersectionsFolder)

    fibulaNormalizationTransformChecked = parameterNode.GetParameter("fibulaNormalizationTransform") == "True"
    self.updateNormalizationFibulaLineTransform(fibulaNormalizationTransformChecked)

  def getNodesLinkedToFibula(self):
    parameterNode = self.getParameterNode()
    nodes = []

    for refKey in ["fibulaModelNode", "decimatedFibulaModelNode", "fibulaLine",
                   "fibulaSurgicalGuidePrototypeModel", "miterBoxDirectionLine",
                   "fibulaSurgicalGuideBaseModel", "vesselsModelNode", "decimatedVesselsModelNode"]:
      node = parameterNode.GetNodeReference(refKey)
      if node is not None:
        nodes.append(node)

    # Cut Bones: skip last item because it is the resected mandible, not a fibula piece
    cutBonesList = createListFromFolderName("Cut Bones")
    nodes.extend(cutBonesList[:-1])

    folderNames = [
      "Fibula planes",
      "Fibula Segments Lengths",
      "Transformed Mandible Pieces",
      "Transformed Full Mandible",
      "miterBoxes Models",
      "biggerMiterBoxes Models",
      "lowResolutionBiggerMiterBoxes Models",
      "rectanglet Models",
      "previewMiterBoxes Models",
      "Fibula Cylinders Models",
      "Dental Implants Cylinders Models",
      "Fibula Dental Implants Cylinders Models",
      "Bigger Fibula Dental Implants Cylinders Models",
      "Cut Vessels",
    ]
    for folderName in folderNames:
      nodesList = createListFromFolderName(folderName)
      nodes.extend(nodesList)

    return nodes

  def updateNormalizationFibulaLineTransform(self, fibulaNormalizationTransformChecked):
    parameterNode = self.getParameterNode()
    fibulaLine = parameterNode.GetNodeReference("fibulaLine")
    
    fibulaNormalizationTransformNode = parameterNode.GetNodeReference("fibulaNormalizationTransformNode")
    if fibulaNormalizationTransformNode is None:
      fibulaNormalizationTransformNode = slicer.vtkMRMLLinearTransformNode()
      fibulaNormalizationTransformNode.SetName("FibulaNormalizationTransform")
      slicer.mrmlScene.AddNode(fibulaNormalizationTransformNode)
      parameterNode.SetNodeReferenceID("fibulaNormalizationTransformNode", fibulaNormalizationTransformNode.GetID())
    
    currentScalarVolume = parameterNode.GetNodeReference("currentScalarVolume")
    if currentScalarVolume is not None:
      currentScalarVolume.SetAndObserveTransformNodeID(fibulaNormalizationTransformNode.GetID())
    
    if fibulaNormalizationTransformChecked is not None:
      parameterNode.SetParameter("fibulaNormalizationTransform", str(fibulaNormalizationTransformChecked))
      if not fibulaNormalizationTransformChecked:
        identityMatrix = vtk.vtkMatrix4x4()
        identityMatrix.Identity()
        fibulaNormalizationTransformNode.SetMatrixTransformToParent(identityMatrix)
      else:
        lineStartPos = np.zeros(3)
        lineEndPos = np.zeros(3)
        fibulaLine.GetNthControlPointPosition(0, lineStartPos)
        fibulaLine.GetNthControlPointPosition(1, lineEndPos)
        fibulaLineDirection = (lineEndPos-lineStartPos)/np.linalg.norm(lineEndPos-lineStartPos)
        lineCenter = (lineStartPos+lineEndPos)/2
        #get rotation
        referenceDirection = np.array([0,0,1])
        rotationAxis = np.cross(fibulaLineDirection, referenceDirection)
        rotationAngle = np.arccos(np.dot(fibulaLineDirection, referenceDirection))
        rotationTransform = vtk.vtkTransform()
        rotationTransform.PostMultiply()
        rotationTransform.Translate(-lineCenter)
        rotationTransform.RotateWXYZ(np.degrees(rotationAngle), rotationAxis)
        rotationTransform.Translate(lineCenter)
        fibulaNormalizationTransformNode.SetMatrixTransformToParent(rotationTransform.GetMatrix())

    fibulaLinkedNodes = self.getNodesLinkedToFibula()
    for node in fibulaLinkedNodes:
      node.SetAndObserveTransformNodeID(fibulaNormalizationTransformNode.GetID())
  
  def setBackgroundVolumeFromID(self,scalarVolumeID):
    redSliceLogic = slicer.app.layoutManager().sliceWidget('Red').sliceLogic()
    redSliceLogic.GetSliceCompositeNode().SetBackgroundVolumeID(scalarVolumeID)
    greenSliceLogic = slicer.app.layoutManager().sliceWidget('Green').sliceLogic()
    greenSliceLogic.GetSliceCompositeNode().SetBackgroundVolumeID(scalarVolumeID)
    yellowSliceLogic = slicer.app.layoutManager().sliceWidget('Yellow').sliceLogic()
    yellowSliceLogic.GetSliceCompositeNode().SetBackgroundVolumeID(scalarVolumeID)

  @saveExecutedMethodWithTelemetry
  def create3DModelOfTheReconstruction(self):
    import time
    startTime = time.time()
    logging.info('Processing started')

    parameterNode = self.getParameterNode()

    if parameterNode.GetParameter("useNonDecimatedModelsForPreview") != "True":
      parameterNode.SetParameter("useNonDecimatedModelsForPreview","True")
      self.onGenerateFibulaPlanesTimerTimeout()

    transformedFibulaPiecesList = createListFromFolderName("Transformed Fibula Pieces")
    planeList = createListFromFolderName("Mandibular planes")

    if len(transformedFibulaPiecesList) == 0:
      return

    modelsLogic = slicer.modules.models.logic()
    mandibleReconstructionModel = modelsLogic.AddModel(vtk.vtkPolyData())
    mandibleReconstructionModel.SetName(slicer.mrmlScene.GetUniqueNameByString('MandibleReconstructionModel'))

    displayNode = mandibleReconstructionModel.GetDisplayNode()
    mandibleViewNode = slicer.mrmlScene.GetSingletonNode(slicer.MANDIBLE_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
    displayNode.AddViewNodeID(mandibleViewNode.GetID())

    parentFolder = getFolder("Mandible reconstruction")
    moveNodeToFolder(mandibleReconstructionModel, parentFolder)

    cutBonesList = createListFromFolderName("Cut Bones")
    resectedMandible = cutBonesList[-1]

    scaledFibulaPiecesFolder = getFolder("Scaled Fibula Pieces")
    self.exportScaledFibulaPiecesForNeomandibleReconstructionToFolder(scaledFibulaPiecesFolder)
    scaledFibulaPiecesList = createListFromFolderName("Scaled Fibula Pieces")

    combineModelsLogic = combineModelsRobustLogic
    listOfObjectsToUnite = scaledFibulaPiecesList + [resectedMandible]
    for i in range(len(listOfObjectsToUnite)):
      combineModelsLogic.process(mandibleReconstructionModel, listOfObjectsToUnite[i], mandibleReconstructionModel, 'union')
    interCondylarBeamBox = parameterNode.GetNodeReference("interCondylarBeamBox")
    if interCondylarBeamBox is not None:
      combineModelsLogic.process(mandibleReconstructionModel, interCondylarBeamBox, mandibleReconstructionModel, 'union')
    
    removeFolder(scaledFibulaPiecesFolder)

    if mandibleReconstructionModel.GetPolyData().GetNumberOfPoints() == 0:
      slicer.mrmlScene.RemoveNode(mandibleReconstructionModel)
      slicer.util.errorDisplay("ERROR: Boolean operations to make neomandible model failed")
      return
    
    parameterNode.SetNodeReferenceID("mandibleReconstructionModel", mandibleReconstructionModel.GetID())
    parameterNode.SetParameter("neomandibleVisible", "True")

  def exportScaledFibulaPiecesForNeomandibleReconstructionToFolder(self, scaledFibulaPiecesFolder, scaleFactor=1.001, overlap=0.05):
    planeList = createListFromFolderName("Mandibular planes")
    transformedFibulaPiecesList = createListFromFolderName("Transformed Fibula Pieces")

    def rotationMatrixDirToZ(d):
      # Rotation (3x3) that maps the unit vector d onto the +Z axis (Rodrigues' formula)
      z = np.array([0.0, 0.0, 1.0])
      v = np.cross(d, z)
      c = np.dot(d, z)
      if c > 1.0 - 1e-8:
        return np.eye(3)
      if c < -1.0 + 1e-8:
        return np.diag([1.0, -1.0, -1.0])
      skew = np.array([
        [0.0, -v[2], v[1]],
        [v[2], 0.0, -v[0]],
        [-v[1], v[0], 0.0],
      ])
      return np.eye(3) + skew + skew @ skew * (1.0 / (1.0 + c))

    def vtkMatrixFrom3x3(R):
      m = vtk.vtkMatrix4x4()
      m.Identity()
      for r in range(3):
        for col in range(3):
          m.SetElement(r, col, R[r][col])
      return m

    for i in range(len(transformedFibulaPiecesList)):
      or0 = np.zeros(3)
      planeList[i].GetOrigin(or0)
      or1 = np.zeros(3)
      planeList[i+1].GetOrigin(or1)
      origin = (or0+or1)/2

      # Extend the piece by a fixed amount (overlap) past each cut plane along the
      # inter-plane axis. This guarantees adjacent pieces overlap enough for the
      # boolean union to succeed, independently of the piece length (a proportional
      # scale alone leaves short pieces with minimal contact).
      axis = or1 - or0
      length = np.linalg.norm(axis)
      if length > 0:
        direction = axis / length
        axialScale = (length + 2*overlap) / length
        R = rotationMatrixDirToZ(direction)
      else:
        axialScale = 1.0
        R = np.eye(3)

      scaleTransform = vtk.vtkTransform()
      scaleTransform.PostMultiply()
      scaleTransform.Translate(-origin)
      #Just scale them enough so that boolean union is successful
      scaleTransform.Scale(scaleFactor, scaleFactor, scaleFactor)
      # Align the inter-plane axis with Z, stretch along it, then rotate back
      scaleTransform.Concatenate(vtkMatrixFrom3x3(R))
      scaleTransform.Scale(1.0, 1.0, axialScale)
      scaleTransform.Concatenate(vtkMatrixFrom3x3(R.T))
      scaleTransform.Translate(origin)

      scaleTransformer = vtk.vtkTransformPolyDataFilter()
      scaleTransformer.SetTransform(scaleTransform)
      scaleTransformer.SetInputData(transformedFibulaPiecesList[i].GetPolyData())
      scaleTransformer.Update()

      scaledFibulaPiece = vtk.vtkPolyData()
      scaledFibulaPiece.ShallowCopy(scaleTransformer.GetOutput())

      scaledFibulaPieceModel = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','Scaled Fibula Piece %d' % i)
      scaledFibulaPieceModel.CreateDefaultDisplayNodes()
      scaledFibulaPieceModel.SetAndObservePolyData(scaledFibulaPiece)

      moveNodeToFolder(scaledFibulaPieceModel, scaledFibulaPiecesFolder)

    return

  def createPlateCurve(self):
    curveNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLMarkupsCurveNode")
    curveNode.SetName("temp")
    slicer.mrmlScene.AddNode(curveNode)
    slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(curveNode)
    moveNodeToFolder(curveNode, getFolder("BoneReconstructionPlanner"))
    curveNode.SetName(slicer.mrmlScene.GetUniqueNameByString("plateCurve"))

    displayNode = curveNode.GetDisplayNode()
    mandibleViewNode = slicer.mrmlScene.GetSingletonNode("1", "vtkMRMLViewNode")
    displayNode.AddViewNodeID(mandibleViewNode.GetID())

    self.setRedSliceForMarkupsDisplayNodes()

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

    plateCrossSectionalWidth = float(parameterNode.GetParameter("plateCrossSectionalWidth_mm"))
    plateCrossSectionalLength = float(parameterNode.GetParameter("plateCrossSectionalLength_mm"))
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
    #slicer.util.mainWindow().enabled = False
    slicer.app.processEvents()
    slicer.mrmlScene.Clear()
    slicer.app.processEvents()

  def closeUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.app.processEvents()
    slicer.mrmlScene.Clear()
    #slicer.util.mainWindow().enabled = True
    slicer.app.processEvents()
    
  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.section_EnterBRP()
    self.section_GetWidget()
    self.section_GetLogic()
    self.section_LoadSampleDataV2()
    self.section_SelectSampleSegmentations()
    self.section_MakeBoneModels()
    self.section_SetMandibularCurve()
    self.section_SetFibulaLine()
    self.section_AddMandiblePlanes()
    #self.section_SimulateAndImproveMandibleReconstruction()
    #self.section_createMiterBoxesFromCorrespondingLine()
    ##self.section_prepareGuideBaseForFibulaGuide()
    #self.section_createAndUpdateSawBoxesFromMandiblePlanes()
    #self.closeUp()

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
      
  def section_LoadSampleDataV2(self):
    # load using GUI
    slicer.app.processEvents()
    self.widgetBRP.ui.loadTestCaseButton.click()
    slicer.app.processEvents()
    fibulaVolumeThroughGUI = slicer.util.getNode('CTFibula')
    mandibleVolumeThroughGUI = slicer.util.getNode('CTMandible')
    fibulaSegmentationThroughGUI = slicer.util.getNode('FibulaSegmentation')
    mandibleSegmentationThroughGUI = slicer.util.getNode('MandibleSegmentation')

    # load using SampleData module for comparison
    import SampleData
    fibulaVolumeThroughSampleData = SampleData.downloadSample('CTFibula')
    mandibleVolumeThroughSampleData = SampleData.downloadSample('CTMandible')
    fibulaSegmentationThroughSampleData = SampleData.downloadSample('FibulaSegmentation')
    mandibleSegmentationThroughSampleData = SampleData.downloadSample('MandibleSegmentation')

    self.assertTrue(
      areVolumesEqual(
        fibulaVolumeThroughGUI, 
        fibulaVolumeThroughSampleData
      )      
    )
    self.assertTrue(
      areVolumesEqual(
        mandibleVolumeThroughGUI, 
        mandibleVolumeThroughSampleData
      )      
    )
    self.assertTrue(
      areSegmentationsEqual(
        fibulaSegmentationThroughGUI, 
        fibulaSegmentationThroughSampleData
      )      
    )
    self.assertTrue(
      areSegmentationsEqual(
        mandibleSegmentationThroughGUI, 
        mandibleSegmentationThroughSampleData
      )      
    )

    # remove duplicate of data
    slicer.mrmlScene.RemoveNode(fibulaVolumeThroughSampleData)
    slicer.mrmlScene.RemoveNode(mandibleVolumeThroughSampleData)
    slicer.mrmlScene.RemoveNode(fibulaSegmentationThroughSampleData)
    slicer.mrmlScene.RemoveNode(mandibleSegmentationThroughSampleData)

  def section_SelectSampleSegmentations(self):
    fibulaSegmentationThroughGUI = slicer.util.getNode('FibulaSegmentation')
    mandibleSegmentationThroughGUI = slicer.util.getNode('MandibleSegmentation')

    slicer.app.processEvents()
    self.widgetBRP.ui.fibulaSegmentSelector.setCurrentNode(fibulaSegmentationThroughGUI)
    self.widgetBRP.ui.mandibularSegmentSelector.setCurrentNode(mandibleSegmentationThroughGUI)
    slicer.app.processEvents()

    parameterNode = self.logicBRP.getParameterNode()
    fibulaSegmentationThroughLogic = parameterNode.GetNodeReference("fibulaSegmentation")
    mandibleSegmentationThroughLogic = parameterNode.GetNodeReference("mandibularSegmentation")
    
    self.assertEqual(
      fibulaSegmentationThroughGUI.GetID(),
      fibulaSegmentationThroughLogic.GetID()
    )
    self.assertEqual(
      mandibleSegmentationThroughGUI.GetID(),
      mandibleSegmentationThroughLogic.GetID()
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
    # NEED TO ADD VESSELS MODEL TESTS
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
    BRPFolder = getFolder("BoneReconstructionPlanner")
    segmentationModelsFolder = getFolder("Segmentation Models")
    fibulaModelItemID = getItem(fibulaModelNode)
    mandibleModelItemID = getItem(mandibleModelNode)
    decimatedFibulaModelItemID = getItem(decimatedFibulaModelNode)
    decimatedMandibleModelItemID = getItem(decimatedMandibleModelNode)
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

  def section_MakeBoneModels(self):
    slicer.app.processEvents()
    self.widgetBRP.ui.makeModelsButton.click()
    slicer.app.processEvents()

    parameterNode = self.logicBRP.getParameterNode()

    # assertions
    # assertions on meshes centroids
    fibulaCentroid = [
      float(parameterNode.GetParameter("fibulaCentroidX")),
      float(parameterNode.GetParameter("fibulaCentroidY")),
      float(parameterNode.GetParameter("fibulaCentroidZ"))
    ]    
    mandibleCentroid = [
      float(parameterNode.GetParameter("mandibleCentroidX")),
      float(parameterNode.GetParameter("mandibleCentroidY")),
      float(parameterNode.GetParameter("mandibleCentroidZ"))
    ]

    precomputedFibulaCentroid = [-95.32889, -8.86916, -18.44151]
    precomputedMandibleCentroid = [0.1073946, 65.49171, -57.415688]

    relativeTolerance = 0.01
    self.assertTrue(
      np.allclose(fibulaCentroid,precomputedFibulaCentroid, rtol=relativeTolerance)
    )
    self.assertTrue(
      np.allclose(mandibleCentroid,precomputedMandibleCentroid, rtol=relativeTolerance)
    )

    # assert models are not None
    fibulaModelNode = parameterNode.GetNodeReference("fibulaModelNode")
    mandibleModelNode = parameterNode.GetNodeReference("mandibleModelNode")
    decimatedFibulaModelNode = parameterNode.GetNodeReference("decimatedFibulaModelNode")
    decimatedMandibleModelNode = parameterNode.GetNodeReference("decimatedMandibleModelNode")
    self.assertIsNotNone(fibulaModelNode)
    self.assertIsNotNone(mandibleModelNode)
    self.assertIsNotNone(decimatedFibulaModelNode)
    self.assertIsNotNone(decimatedMandibleModelNode)


    # assertions on meshes number of points
    allowedRelativeDifference = 0.02
    targetFibulaPoints = 197962
    targetMandiblePoints = 109820
    targetDecimatedFibulaPoints = 11120
    targetDecimatedMandiblePoints = 6602

    self.assertTrue(
      np.allclose(fibulaModelNode.GetMesh().GetNumberOfPoints(), targetFibulaPoints, rtol=allowedRelativeDifference)
    )
    self.assertTrue(
      np.allclose(mandibleModelNode.GetMesh().GetNumberOfPoints(), targetMandiblePoints, rtol=allowedRelativeDifference)
    )
    self.assertTrue(
      np.allclose(decimatedFibulaModelNode.GetMesh().GetNumberOfPoints(), targetDecimatedFibulaPoints, rtol=allowedRelativeDifference)
    )
    self.assertTrue(
      np.allclose(decimatedMandibleModelNode.GetMesh().GetNumberOfPoints(), targetDecimatedMandiblePoints, rtol=allowedRelativeDifference)
    )


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
    BRPFolder = getFolder("BoneReconstructionPlanner")
    mandibularCurveItemID = getItem(mandibularCurveNode)
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
  
  def section_SetMandibularCurve(self):
    mandibularCurvePoints = [
      [ 43.02632904,  61.06202698, -60.92616272],
      [ 33.40823746,  83.49567413, -71.52266693],
      [ 20.23157501, 103.01984406, -78.46653748],
      [  3.63758111, 110.96538544, -82.94055939],
      [-15.31359386, 103.96769714, -83.5898056 ],
      [-31.47601509,  77.34331512, -76.59559631],
      [-44.32816696,  47.25786209, -64.23408508],
    ]

    mandibularCurveNode = self.logicBRP.getMandibularCurve()
    for point in mandibularCurvePoints:
      mandibularCurveNode.AddControlPoint(*point)
    interactionNode = slicer.app.applicationLogic().GetInteractionNode()
    interactionNode.SwitchToViewTransformMode()

    self.assertEqual(
      len(mandibularCurvePoints),
      mandibularCurveNode.GetNumberOfControlPoints()
    )

    # check placement in the SH
    shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
    BRPFolder = getFolder("BoneReconstructionPlanner")
    mandibularCurveItemID = getItem(mandibularCurveNode)
    self.assertEqual(
      BRPFolder,
      shNode.GetItemParent(mandibularCurveItemID)
    )

    # the mandibleCurveSelector autopopulates and updates the parameterNode
    parameterNode = self.logicBRP.getParameterNode()
    mandibleCurveFromParameterNode = parameterNode.GetNodeReference("mandibleCurve")
    self.assertEqual(
      mandibularCurveNode.GetID(),
      mandibleCurveFromParameterNode.GetID()
    )

  def section_AddMandiblePlanes(self):
    self.delayDisplay("Starting the AddMandibularPlanesTest")

    planeOrigins = [
      [38.89806365966797, 71.97505950927734, -65.15746307373047],
      [-28.70669174194336, 81.52465057373047, -75.59122467041016],
      [21.20140266418457, 100.38216400146484, -73.75139617919922],
      [-9.514277458190918, 105.30805969238281, -79.4371337890625],
    ]

    for origin in planeOrigins:
      slicer.app.processEvents()
      self.widgetBRP.ui.addCutPlaneButton.click()
      slicer.app.processEvents()
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

    mandibularPlanesList = createListFromFolderName("Mandibular planes")
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
          np.array([slicer.PLANE_SIDE_SIZE,slicer.PLANE_SIDE_SIZE])
        )
      )
      self.assertEqual(
        planeNode.GetPlaneType(),
        slicer.vtkMRMLMarkupsPlaneNode.PlaneType3Points
      )
      
      displayNode = planeNode.GetDisplayNode()
      self.assertEqual(
        displayNode.GetGlyphScale(),
        slicer.PLANE_GLYPH_SCALE
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
    mandibleCurve = self.logicBRP.getMandibularCurve()
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

    getFolder = slicer.mrmlScene.GetSubjectHierarchyNode()
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
        [ -88.32122039794922, -10.915949821472168, -90.24563598632812],
        [-100.49141693115234, -9.320514678955078, 47.834014892578125]
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

  def section_SetFibulaLine(self):
    fibulaLinePoints = [
      [-91.39446258544922, -12.100865364074707, -90.508544921875],
      [-104.19928741455078, -9.48827075958252, 47.4937744140625],
    ]

    fibulaLineNode = self.logicBRP.getFibulaLine()
    for point in fibulaLinePoints:
      fibulaLineNode.AddControlPoint(*point)
    interactionNode = slicer.app.applicationLogic().GetInteractionNode()
    interactionNode.SwitchToViewTransformMode()

    self.assertEqual(
      len(fibulaLinePoints),
      fibulaLineNode.GetNumberOfControlPoints()
    )

    # check placement in the SH
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

    centeredLinePoints = np.array(
      [
        [ -88.32122039794922, -10.915949821472168, -90.24563598632812],
        [-100.49141693115234, -9.320514678955078, 47.834014892578125]
      ]
    )

    relativeTolerance = 0.01
    for i in range(2):
      self.assertTrue(
        np.allclose(
          fibulaLineNode.GetNthControlPointPosition(i),
          centeredLinePoints[i],
          rtol=relativeTolerance
        )
      )

  def section_SimulateAndImproveMandibleReconstruction(self):
    self.delayDisplay("Starting the SimulateAndImproveMandibleReconstruction")
    self.delayDisplay("Create the reconstruction for first time")
    self.logicBRP.onGenerateFibulaPlanesTimerTimeout()
    self.delayDisplay("Reconstruction successful")
    #

    # # generate mandibular plane movements with this code:
    # def createListFromFolderName(folderID):
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
    # mandiblePlanes = createListFromFolderName(mandiblePlanesFolder)
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

    if USING_GUI:
      layoutManager = slicer.app.layoutManager()
      mandibleViewNode = slicer.mrmlScene.GetSingletonNode(slicer.MANDIBLE_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
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
    
    if USING_GUI:
      # hide original mandible
      self.widgetBRP.ui.setOriginalMandibleVisibility(False)
      # hide mandible plane handles
      self.widgetBRP.ui.setMandiblePlanesInteractionHandlesVisibility(False)

    self.delayDisplay("Optimize bones contact in reconstruction")
    parameterNode = self.logicBRP.getParameterNode()
    parameterNode.SetParameter("mandiblePlanesPositioningForMaximumBoneContact","True")
    self.logicBRP.onGenerateFibulaPlanesTimerTimeout()
    self.delayDisplay("Bones contact optimized")

    if USING_GUI:
      fibulaViewNode = slicer.mrmlScene.GetSingletonNode(slicer.FIBULA_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
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

    if USING_GUI:
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
    if USING_GUI:
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

  def loadFibulaGuideBase(self):
    import SampleData
    self.fibulaSurgicalGuideBaseModel = SampleData.downloadSample('FibulaGuideBase')
    self.delayDisplay('Loaded FibulaGuideBase')

    parameterNode = self.logicBRP.getParameterNode()
    parameterNode.SetNodeReferenceID("fibulaSurgicalGuideBaseModel", self.fibulaSurgicalGuideBaseModel.GetID())

    self.assertEqual(
      parameterNode.GetNodeReference("fibulaSurgicalGuideBaseModel").GetID(),
      self.fibulaSurgicalGuideBaseModel.GetID()
    )
  
  def section_prepareGuideBaseForFibulaGuide(self):
    self.loadFibulaGuideBase()

  def section_createAndUpdateSawBoxesFromMandiblePlanes(self):
    self.delayDisplay("Starting the createAndUpdateSawBoxesFromMandiblePlanes test")

    if USING_GUI:
      layoutManager = slicer.app.layoutManager()
      mandibleViewNode = slicer.mrmlScene.GetSingletonNode(slicer.MANDIBLE_VIEW_SINGLETON_TAG, "vtkMRMLViewNode")
      if int(slicer.app.revision) >= 31524:
        layoutManager.addMaximizedViewNode(mandibleViewNode)
      else:
        layoutManager.setMaximizedViewNode(mandibleViewNode)

    self.logicBRP.createSawBoxesFromFirstAndLastMandiblePlanes()

    # # generate saw boxes movements with this code:
    # def createListFromFolderName(folderID):
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
    # sawBoxesPlanes = createListFromFolderName(mandiblePlanesFolder)
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

    if USING_GUI:
      layoutManager = slicer.app.layoutManager()
      if int(slicer.app.revision) >= 31524:
        layoutManager.removeMaximizedViewNode(mandibleViewNode)
      else:
        layoutManager.setMaximizedViewNode(None)
      # show mandible plane handles
      self.widgetBRP.ui.setMandiblePlanesInteractionHandlesVisibility(True)
      # hide saw boxes handles
      self.widgetBRP.ui.setBiggerSawBoxesInteractionHandlesVisibility(False)

    # asserts below


    self.delayDisplay("CreateAndUpdateSawBoxesFromMandiblePlanes test successful")
