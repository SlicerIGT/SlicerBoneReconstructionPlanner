import logging
import os
from typing import Annotated, Optional

import vtk, qt, slicer
import numpy as np

from slicer.i18n import tr as _
from slicer.i18n import translate
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
#from BRPLib.helperFunctions import *

#
# AddMagnetsToModel
#


class AddMagnetsToModel(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = _("AddMagnetsToModel")  # TODO: make this more human readable by adding spaces
        # TODO: set categories (folders where the module shows up in the module selector)
        self.parent.categories = [translate("qSlicerAbstractCoreModule", "Surface Models")]
        self.parent.dependencies = []  # TODO: add here list of module names that this module requires
        self.parent.contributors = ["Mauro I. Dominguez (Independent)"]  # TODO: replace with "Firstname Lastname (Organization)"
        # TODO: update with short description of the module and a link to online module documentation
        # _() function marks text as translatable to other languages
        self.parent.helpText = _("""
This is a module to create 3D models with magnets.
See more information in <a href="https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner#AddMagnetsToModel">module documentation</a>.
""")
        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = _("""
This file was originally developed by Mauro I. Dominguez (Independent).
""")

#
# AddMagnetsToModelWidget
#


class AddMagnetsToModelWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None) -> None:
        """Called when the user opens the module the first time and the widget is initialized."""
        self.version = "5.6.2.24.12"
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)  # needed for parameter node observation
        self.logic = None
        self._parameterNode = None
        self._updatingGUIFromParameterNode = False

    def setup(self) -> None:
        """Called when the user opens the module the first time and the widget is initialized."""
        ScriptedLoadableModuleWidget.setup(self)

        # Load widget from .ui file (created by Qt Designer).
        # Additional widgets can be instantiated manually and added to self.layout.
        uiWidget = slicer.util.loadUI(self.resourcePath("UI/AddMagnetsToModel.ui"))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        uiWidget.setMRMLScene(slicer.mrmlScene)

        # additional UI setup
        self.ui.versionLabel.text = f"Version: {self.version}" 

        import os
        lockIconPath = os.path.join(os.path.dirname(__file__), '../BoneReconstructionPlanner/Resources/Icons/lock_48.svg')
        self.ui.lockDesignButton.setIcon(qt.QIcon(lockIconPath))

        # Create logic class. Logic implements all computations that should be possible to run
        # in batch mode, without a graphical user interface.
        self.logic = AddMagnetsToModelLogic()

        # Connections

        # These connections ensure that we update parameter node when scene is closed
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)
        
        slicer.mrmlScene.AddObserver(slicer.mrmlScene.NodeAboutToBeRemovedEvent, self.onNodeAboutToBeRemovedEvent) 

        # By order of appearance in the .ui file
        self.ui.setDual3DLayoutButton.connect("clicked(bool)", self.onSetDual3DLayoutButton)
        self.ui.segmentationSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
        self.ui.internalShellDoubleSlider.valueChanged.connect(self.updateParameterNodeFromGUI)
        self.ui.createModelButton.connect("clicked(bool)", self.onCreateModelButton)
        
        ## planePlaceWidget
        placeWidget = self.ui.planePlaceWidget
        placeWidget.setMRMLScene(slicer.mrmlScene)
        placeWidget.setInteractionNode(slicer.app.applicationLogic().GetInteractionNode())
        placeWidget.setCurrentNode(self.logic.getCutPlane())
        placeWidget.buttonsVisible = False
        placeWidget.placeButton().show()
        placeWidget.deleteButton().show()
        placeWidget.placeMultipleMarkups = slicer.qSlicerMarkupsPlaceWidget.ForcePlaceMultipleMarkups
        placeWidget.setDeleteAllControlPointsOptionVisible(False)

        self.ui.updatePlanarCutCheckbox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)
        self.ui.pointsRadioButton.connect('toggled(bool)', self.updateParameterNodeFromGUI)
        self.ui.handlesRadioButton.connect('toggled(bool)', self.updateParameterNodeFromGUI)
       
        ## cylindersPlaceWidget
        placeWidget = self.ui.cylindersPlaceWidget
        placeWidget.setMRMLScene(slicer.mrmlScene)
        placeWidget.setInteractionNode(slicer.app.applicationLogic().GetInteractionNode())
        placeWidget.setCurrentNode(self.logic.getCylindersFiducial())
        placeWidget.buttonsVisible = False
        placeWidget.placeButton().show()
        placeWidget.deleteButton().show()
        placeWidget.placeMultipleMarkups = slicer.qSlicerMarkupsPlaceWidget.ForcePlaceSingleMarkup
        placeWidget.setDeleteAllControlPointsOptionVisible(True)

        self.ui.internalShellDoubleSlider.valueChanged.connect(self.updateParameterNodeFromGUI)
        self.ui.extraCylindersDiameterDoubleSlider.valueChanged.connect(self.updateParameterNodeFromGUI)
        self.ui.cylindersDepthDoubleSlider.valueChanged.connect(self.updateParameterNodeFromGUI)
        self.ui.cylindersVisibilityCheckBox.connect('stateChanged(int)', self.updateParameterNodeFromGUI)

        self.ui.updateFinalModelsPreviewButton.connect("clicked(bool)", self.onUpdateFinalModelsPreviewButton)
        self.ui.lockDesignButton.connect('toggled(bool)', self.updateParameterNodeFromGUI)
        self.ui.exportFinalModelsAsButton.connect("clicked(bool)", self.onExportFinalModelsAsButton)
        self.ui.saveSceneButton.connect("clicked(bool)", self.onSaveSceneButtonAs)

        # Make sure parameter node is initialized (needed for module reload)
        self.initializeParameterNode()

    def cleanup(self) -> None:
        """Called when the application closes and the module widget is destroyed."""
        self.removeObservers()

    @vtk.calldata_type(vtk.VTK_OBJECT)
    def onNodeAboutToBeRemovedEvent(self, caller, event, callData):
        if callData.GetClassName() == 'vtkMRMLMarkupsPlaneNode':
            if callData.GetAttribute("isCutPlane") == 'True':
                callData.RemoveObserver(self.logic.cutPlaneObserver)
                self.logic.cutPlaneObserver = 0
        if callData.GetClassName() == 'vtkMRMLMarkupsFiducialNode':
            if callData.GetAttribute("isCylindersFiducial") == 'True':
                callData.RemoveObserver(self.logic.cylindersFiducialObserver)
                self.logic.cylindersFiducialObserver = 0

    def enter(self) -> None:
        """Called each time the user opens this module."""
        # Make sure parameter node exists and observed
        self.initializeParameterNode()
        
        self.logic.addCutPlaneObserver()
        self.logic.setCutPlaneLocked(False)
        #self.logic.setInteractiveHandlesVisibilityOfCutPlane(True)
        self.logic.setInteractionsOfCutPlane(True)
        
        self.logic.addCylindersFiducialObserver()
        self.logic.setCylindersFiducialLocked(False)
        #self.logic.setInteractiveHandlesVisibilityOfCylindersFiducial(True)
        self.logic.setInteractionsOfCylindersFiducial(True)

    def exit(self) -> None:
        """Called each time the user opens a different module."""
        # Do not react to parameter node changes (GUI will be updated when the user enters into the module)
        self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

        self.logic.removeCutPlaneObserver()
        self.logic.setCutPlaneLocked(True)
        #self.logic.setInteractiveHandlesVisibilityOfCutPlane(False)
        self.logic.setInteractionsOfCutPlane(False)

        self.logic.removeCylindersFiducialObserver()
        self.logic.setCylindersFiducialLocked(True)
        #self.logic.setInteractiveHandlesVisibilityOfCylindersFiducial(False)
        self.logic.setInteractionsOfCylindersFiducial(False)

    def onSceneStartClose(self, caller, event) -> None:
        """Called just before the scene is closed."""
        # Parameter node will be reset, do not use it anymore
        self.setParameterNode(None)

    def onSceneEndClose(self, caller, event) -> None:
        """Called just after the scene is closed."""
        # If this module is shown while the scene is closed then recreate a new parameter node immediately
        if self.parent.isEntered:
            self.initializeParameterNode()

    def initializeParameterNode(self) -> None:
        """
        Ensure parameter node exists and observed.
        """
        # Parameter node stores all user choices in parameter values, node selections, etc.
        # so that when the scene is saved and reloaded, these settings are restored.

        self.setParameterNode(self.logic.getParameterNode())

    def setParameterNode(self, inputParameterNode) -> None:
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

        """
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
        """

        # Update node selectors and sliders
        self.ui.segmentationSelector.setCurrentNode(self._parameterNode.GetNodeReference("segmentation"))

        if self._parameterNode.GetNodeReference("segmentation") is not None:
            self.ui.createModelButton.enabled = True
        else:
            self.ui.createModelButton.enabled = False

        if self._parameterNode.GetParameter("internalShell") != '':
            self.ui.internalShellDoubleSlider.setValue(float(self._parameterNode.GetParameter("internalShell")))

        self.ui.updatePlanarCutCheckbox.checked = self._parameterNode.GetParameter("updatePlanarCut") == "True"
        self.ui.pointsRadioButton.checked = self._parameterNode.GetParameter("planeEditMode") == "Points"
        self.ui.handlesRadioButton.checked = self._parameterNode.GetParameter("planeEditMode") == "Handles"

        if self._parameterNode.GetParameter("innerCylindersDiameter") != '':
            self.ui.innerCylindersDiameterDoubleSlider.setValue(float(self._parameterNode.GetParameter("innerCylindersDiameter")))
        if self._parameterNode.GetParameter("extraCylindersDiameter") != '':
            self.ui.extraCylindersDiameterDoubleSlider.setValue(float(self._parameterNode.GetParameter("extraCylindersDiameter")))
        if self._parameterNode.GetParameter("cylindersDepth") != '':
            self.ui.cylindersDepthDoubleSlider.setValue(float(self._parameterNode.GetParameter("cylindersDepth")))
        if self._parameterNode.GetParameter("diameterTolerance") != '':
            self.ui.diameterToleranceSpinBox.setValue(float(self._parameterNode.GetParameter("diameterTolerance")))
        if self._parameterNode.GetParameter("depthDiameterTolerance") != '':
            self.ui.depthDiameterToleranceSpinBox.setValue(float(self._parameterNode.GetParameter("depthDiameterTolerance")))

        # check if all needed inputs are present
        planeValid = False
        cylindersValid = False
        if self.logic.getCutPlane() is not None:
            planeValid = self.logic.getCutPlane().GetIsPlaneValid()
        if self.logic.getCylindersFiducial() is not None:
            cylindersValid = self.logic.getCylindersFiducial().GetNumberOfControlPoints() > 0
        if planeValid and cylindersValid:
            self.ui.updateFinalModelsPreviewButton.enabled = True
        else:
            self.ui.updateFinalModelsPreviewButton.enabled = False
        
        # check models were created
        modelPartA = self._parameterNode.GetNodeReference("modelPartA")
        modelPartB = self._parameterNode.GetNodeReference("modelPartB")
        if (modelPartA is not None) and (modelPartB is not None):
            self.ui.exportFinalModelsAsButton.enabled = True
        else:
            self.ui.exportFinalModelsAsButton.enabled = False
       
        if self._parameterNode.GetParameter("lockDesign") == "True":
            self.ui.lockDesignButton.checked = True
            self.ui.inputModelFrame.enabled = False
            self.ui.cutPlaneFrame.enabled = False
            self.ui.parametersFrame.enabled = False
        else:
            self.ui.lockDesignButton.checked = False
            self.ui.inputModelFrame.enabled = True
            self.ui.cutPlaneFrame.enabled = True
            self.ui.parametersFrame.enabled = True
            

        """
        shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
        mandibularPlanesFolder = shNode.GetItemByName("Mandibular planes")
        mandibularPlanesList = createListFromFolderID(mandibularPlanesFolder)
        fibulaLine = self._parameterNode.GetNodeReference("fibulaLine")
        mandibularCurve = self._parameterNode.GetNodeReference("mandibleCurve")
        planningObjectsList = mandibularPlanesList + [fibulaLine,mandibularCurve]
        if lockVSPChecked:
            self.setMandiblePlanesVisibility(showMandiblePlanesChecked)
            self.logic.setMarkupsListLocked(planningObjectsList,locked=True)
            self.logic.removeMandiblePlaneObservers()
            #
            self.ui.lockVSPButton.checked = True
            self.ui.parametersOfVSPFrame.enabled = False
            self.ui.updateVSPButtonsFrame.enabled = False
            self.ui.create3DModelOfTheReconstructionFrame.enabled = False
        else:
            #self.setMandiblePlanesVisibility(True)
            self.logic.setMarkupsListLocked(planningObjectsList,locked=False)
            self.logic.removeMandiblePlaneObservers() # in case they already exist
            self.logic.addMandiblePlaneObservers()
            #
            self.ui.lockVSPButton.checked = False
            self.ui.parametersOfVSPFrame.enabled = True
            self.ui.updateVSPButtonsFrame.enabled = True
            self.ui.create3DModelOfTheReconstructionFrame.enabled = True
        
        
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
        self.setOriginalMandibleVisility(showOriginalMandibleChecked)

        showBiggerSawBoxesInteractionHandlesChecked = self._parameterNode.GetParameter("showBiggerSawBoxesInteractionHandles") == "True"
        self.ui.showBiggerSawBoxesInteractionHandlesCheckBox.checked = showBiggerSawBoxesInteractionHandlesChecked
        self.setBiggerSawBoxesInteractionHandlesVisibility(showBiggerSawBoxesInteractionHandlesChecked)
        """

        # All the GUI updates are done
        self._updatingGUIFromParameterNode = False

    def updateParameterNodeFromGUI(self, caller=None, event=None):
        """
        This method is called when the user makes any change in the GUI.
        The changes are saved into the parameter node (so that they are restored when the scene is saved and loaded).
        """

        if self._parameterNode is None or self._updatingGUIFromParameterNode:
            return

        wasModified = self._parameterNode.StartModify()    # Modify all properties in a single batch

        self._parameterNode.SetNodeReferenceID("segmentation", self.ui.segmentationSelector.currentNodeID)

        self._parameterNode.SetParameter("internalShell", str(self.ui.internalShellDoubleSlider.value))
        self._parameterNode.SetParameter("innerCylindersDiameter", str(self.ui.innerCylindersDiameterDoubleSlider.value))
        self._parameterNode.SetParameter("extraCylindersDiameter", str(self.ui.extraCylindersDiameterDoubleSlider.value))
        self._parameterNode.SetParameter("cylindersDepth", str(self.ui.cylindersDepthDoubleSlider.value))
        self._parameterNode.SetParameter("diameterTolerance", str(self.ui.diameterToleranceSpinBox.value))
        self._parameterNode.SetParameter("depthDiameterTolerance", str(self.ui.depthDiameterToleranceSpinBox.value))

        if self.ui.updatePlanarCutCheckbox.checked:
            self._parameterNode.SetParameter("updatePlanarCut","True")
        else:
            self._parameterNode.SetParameter("updatePlanarCut","False")
        if self.ui.cylindersVisibilityCheckBox.checked:
            self._parameterNode.SetParameter("cylindersVisibility","True")
        else:
            self._parameterNode.SetParameter("cylindersVisibility","False")
        if self.ui.pointsRadioButton.checked:
            self._parameterNode.SetParameter("planeEditMode","Points")
        if self.ui.handlesRadioButton.checked:
            self._parameterNode.SetParameter("planeEditMode","Handles")

        self._parameterNode.EndModify(wasModified)

    
    @vtk.calldata_type(vtk.VTK_OBJECT)
    def onNodeRemovedEvent(self, caller, event, callData):
        if callData.GetClassName() == 'vtkMRMLMarkupsPlaneNode' and callData.GetAttribute("isCutPlane") == 'True':
            #print(callData.GetName())
            placeWidget = self.ui.planePlaceWidget
            placeWidget.setCurrentNode(self.logic.getCutPlane())
        if callData.GetClassName() == 'vtkMRMLMarkupsFiducialNode' and callData.GetAttribute("isCylindersFiducial") == 'True':
            #print(callData.GetName())
            placeWidget = self.ui.cylindersPlaceWidget
            placeWidget.setCurrentNode(self.logic.getCylindersFiducial())
    
    def onSetDual3DLayoutButton(self) -> None:
        layoutManager = slicer.app.layoutManager()
        layoutManager.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutDual3DView)

    def onCreateModelButton(self) -> None:
        self.logic.createModel()
    
    def onUpdateFinalModelsPreviewButton(self) -> None:
        self.logic.updateFinalModelsPreview()

    def onExportFinalModelsAsButton(self) -> None:
        # QDialog to select folder and format
        thePath = "/my/folder"
        theFormat = "stl"
        self.logic.exportFinalModelsAs(directory = thePath, format = theFormat)

    def onSaveSceneButtonAs(self) -> None:
        # QDialog to select .mrb filename
        theFilename = "/the/path/myScene.mrb"
        slicer.util.saveScene(theFilename)

#
# AddMagnetsToModelLogic
#


class AddMagnetsToModelLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self) -> None:
        """Called when the logic class is instantiated. Can be used for initializing member variables."""
        ScriptedLoadableModuleLogic.__init__(self)
        self.updatePointsTimer = qt.QTimer()
        self.updatePointsTimer.setInterval(300)
        self.updatePointsTimer.setSingleShot(True)
        self.updatePointsTimer.connect('timeout()', self.onUpdatePointsTimerTimeout)
        self.HOLLOWED_SEGMENT_NAME = "Hollowed"
        self.cutPlaneObserver = 0
        self.cylindersFiducialObserver = 0

    def setDefaultParameters(self, parameterNode):
        """
        Initialize parameter node with default settings.
        """
        if not parameterNode.GetParameter("internalShell"):
            parameterNode.SetParameter("internalShell",str(4.0))
        if not parameterNode.GetParameter("planeEditMode"):
            parameterNode.SetParameter("planeEditMode","Points")
        if not parameterNode.GetParameter("updatePlanarCut"):
            parameterNode.SetParameter("updatePlanarCut",str(True))
        if not parameterNode.GetParameter("innerCylindersDiameter"):
            parameterNode.SetParameter("innerCylindersDiameter",str(4.0))
        if not parameterNode.GetParameter("extraCylindersDiameter"):
            parameterNode.SetParameter("extraCylindersDiameter",str(5.0))
        if not parameterNode.GetParameter("cylindersDepth"):
            parameterNode.SetParameter("cylindersDepth",str(10.0))
        if not parameterNode.GetParameter("diameterTolerance"):
            parameterNode.SetParameter("diameterTolerance",str(0.15))
        if not parameterNode.GetParameter("depthDiameterTolerance"):
            parameterNode.SetParameter("depthDiameterTolerance",str(0.15)) 
        if not parameterNode.GetParameter("cylindersVisibility"):
            parameterNode.SetParameter("cylindersVisibility",str(True))  
        if not parameterNode.GetParameter("lockDesign"):
            parameterNode.SetParameter("lockDesign",str(False))
    
    def getParentFolderItemID(self):
        shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
        sceneItemID = shNode.GetSceneItemID()
        folderSubjectHierarchyID = shNode.GetItemByName("AddMagnetsToModel")
        if folderSubjectHierarchyID:
            return folderSubjectHierarchyID
        else:
            return shNode.CreateFolderItem(sceneItemID,"AddMagnetsToModel")
    
    """
    def process(self,
                inputVolume: vtkMRMLScalarVolumeNode,
                outputVolume: vtkMRMLScalarVolumeNode,
                imageThreshold: float,
                invert: bool = False,
                showResult: bool = True) -> None:

        if not inputVolume or not outputVolume:
            raise ValueError("Input or output volume is invalid")

        import time

        startTime = time.time()
        logging.info("Processing started")

        # Compute the thresholded output volume using the "Threshold Scalar Volume" CLI module
        cliParams = {
            "InputVolume": inputVolume.GetID(),
            "OutputVolume": outputVolume.GetID(),
            "ThresholdValue": imageThreshold,
            "ThresholdType": "Above" if invert else "Below",
        }
        cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True, update_display=showResult)
        # We don't need the CLI module node anymore, remove it to not clutter the scene with it
        slicer.mrmlScene.RemoveNode(cliNode)

        stopTime = time.time()
        logging.info(f"Processing completed in {stopTime-startTime:.2f} seconds")
    """

    def createModel(self):
        parameterNode = self.getParameterNode()
        modelSegmentation = parameterNode.GetNodeReference("segmentation")
        modelNode = parameterNode.GetNodeReference("model")
        decimatedModelNode = parameterNode.GetNodeReference("decimatedModel")
        
        slicer.mrmlScene.RemoveNode(modelNode)
        slicer.mrmlScene.RemoveNode(decimatedModelNode)

        shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
        segmentationModelsFolder = shNode.GetItemByName("Segmentation Models")
        shNode.RemoveItem(segmentationModelsFolder)
        segmentationModelsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Segmentation Models")

        modelNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','model')
        decimatedModelNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLModelNode','decimatedModel')
        modelNode.CreateDefaultDisplayNodes()
        decimatedModelNode.CreateDefaultDisplayNodes()

        wasModified = parameterNode.StartModify()

        self.copyHollowed(modelSegmentation)
        
        seg = modelSegmentation.GetSegmentation()
        seg.CreateRepresentation(slicer.vtkSegmentationConverter.GetSegmentationClosedSurfaceRepresentationName())

        modelSegmentation.GetDisplayNode().SetVisibility(False)

        segmentID = seg.GetSegmentIdBySegmentName(self.HOLLOWED_SEGMENT_NAME)
        segment = seg.GetSegment(segmentID)
        logic = slicer.modules.segmentations.logic()
        logic.ExportSegmentToRepresentationNode(segment, modelNode)
        modelNode.SetName("model")

        modelDisplayNode = modelNode.GetDisplayNode()

        decimatedModelDisplayNode = decimatedModelNode.GetDisplayNode()
        decimatedModelDisplayNode.SetColor(modelNode.GetDisplayNode().GetColor())

        modelDisplayNode.SetVisibility(False)
        decimatedModelDisplayNode.SetVisibility(True)

        modelDisplayNode.SetVisibility2D(True)
        decimatedModelDisplayNode.SetVisibility2D(True)

        modelDisplayNode.SetSliceIntersectionThickness(3)
        decimatedModelDisplayNode.SetSliceIntersectionThickness(3)

        param = {
            "inputModel": modelNode,
            "outputModel": decimatedModelNode,
            "reductionFactor": 0.95,
            "method": "FastQuadric"
        }

        slicer.cli.runSync(slicer.modules.decimation, parameters=param)

        modelNodeItemID = shNode.GetItemByDataNode(modelNode)
        shNode.SetItemParent(modelNodeItemID, segmentationModelsFolder)
        decimatedModelNodeItemID = shNode.GetItemByDataNode(decimatedModelNode)
        shNode.SetItemParent(decimatedModelNodeItemID, segmentationModelsFolder)

        parameterNode.SetNodeReferenceID("model", modelNode.GetID())
        parameterNode.SetNodeReferenceID("decimatedModel", decimatedModelNode.GetID())

        layoutManager = slicer.app.layoutManager()
        layoutManager.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutDual3DView)
        viewLeft = layoutManager.threeDWidget(0).threeDView()
        viewRight = layoutManager.threeDWidget(1).threeDView()
        threeDLeftViewNode = viewLeft.mrmlViewNode()
        threeDRightViewNode = viewRight.mrmlViewNode()
        cameraLeftNode = slicer.modules.cameras.logic().GetViewActiveCameraNode(threeDLeftViewNode)
        cameraRightNode = slicer.modules.cameras.logic().GetViewActiveCameraNode(threeDRightViewNode)

        centroid = getCentroid(modelNode)
        viewUpDirection = np.array([0.,0.,1.])
        cameraDirection = np.array([0.,-1.,0.])
        cameraLeftNode.SetPosition(centroid-cameraDirection*300)
        cameraRightNode.SetPosition(centroid+cameraDirection*300)
        cameraLeftNode.SetFocalPoint(centroid)
        cameraRightNode.SetFocalPoint(centroid)
        cameraLeftNode.SetViewUp(viewUpDirection)
        cameraRightNode.SetViewUp(viewUpDirection)
        cameraLeftNode.ResetClippingRange()
        cameraRightNode.ResetClippingRange()

        parameterNode.EndModify(wasModified)

        if not slicer.app.commandOptions().noMainWindow:
            slicer.util.forceRenderAllViews()

    def getCutPlane(self, startPlacementMode = False):
        parameterNode = self.getParameterNode()
        cutPlane = parameterNode.GetNodeReference("cutPlane")
        if cutPlane is None:
            cutPlane = slicer.mrmlScene.CreateNodeByClass("vtkMRMLMarkupsPlaneNode")
            cutPlane.SetName("temp")
            slicer.mrmlScene.AddNode(cutPlane)
            slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(cutPlane)
            cutPlane.SetPlaneType(slicer.vtkMRMLMarkupsPlaneNode.PlaneTypePlaneFit)
            cutPlane.GetDisplayNode().SetHandlesInteractive(False)
            cutPlane.SetAttribute("isCutPlane","True")
            shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
            cutPlaneItemID = shNode.GetItemByDataNode(cutPlane)
            shNode.SetItemParent(cutPlaneItemID, self.getParentFolderItemID())
            cutPlane.SetName(slicer.mrmlScene.GetUniqueNameByString("cutPlane"))
            parameterNode.SetNodeReferenceID("cutPlane",cutPlane.GetID())

            #displayNode = cutPlane.GetDisplayNode()
            #displayNode.AddViewNodeID(slicer.MANDIBLE_VIEW_ID)

            self.addCutPlaneObserver()

        return cutPlane

    def getCylindersFiducial(self, startPlacementMode = False):
        parameterNode = self.getParameterNode()
        cylindersFiducial = parameterNode.GetNodeReference("cylindersFiducial")
        if cylindersFiducial is None:
            cylindersFiducial = slicer.mrmlScene.CreateNodeByClass("vtkMRMLMarkupsFiducialNode")
            cylindersFiducial.SetName("temp")
            slicer.mrmlScene.AddNode(cylindersFiducial)
            slicer.modules.markups.logic().AddNewDisplayNodeForMarkupsNode(cylindersFiducial)
            cylindersFiducial.SetAttribute("isCylindersFiducial","True")
            shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
            cylindersFiducialItemID = shNode.GetItemByDataNode(cylindersFiducial)
            shNode.SetItemParent(cylindersFiducialItemID, self.getParentFolderItemID())
            cylindersFiducial.SetName(slicer.mrmlScene.GetUniqueNameByString("cylindersFiducial"))
            parameterNode.SetNodeReferenceID("cylindersFiducial",cylindersFiducial.GetID())

            #displayNode = cylindersFiducial.GetDisplayNode()
            #displayNode.AddViewNodeID(slicer.MANDIBLE_VIEW_ID)
        
        return cylindersFiducial

    def onUpdatePointsTimerTimeout(self):
        cylindersFiducial = self.getCylindersFiducial()
        cutPlane = self.getCutPlane()

        if cylindersFiducial.GetNumberOfControlPoints() == 0:
            return
        
        if not cutPlane.GetIsPlaneValid():
            return
        
        # Get plane parameters
        plane_center = np.array(cutPlane.GetOrigin())
        plane_normal = np.array(cutPlane.GetNormal())

        # Project each control point
        for i in range(cylindersFiducial.GetNumberOfControlPoints()):
            point = np.array(cylindersFiducial.GetNthControlPointPosition(i))
            projected_point = project_point_to_plane(point, plane_center, plane_normal)
            #print(f"Original Point: {point}, Projected Point: {projected_point}")
            # Optionally, update the fiducial node's position
            cylindersFiducial.SetNthControlPointPosition(i, *projected_point)

        self.cutWithDynamicModeler()
    
    def cutWithDynamicModeler(self):
        parameterNode = self.getParameterNode()
        inputModel = parameterNode.GetNodeReference("model")
        decimatedInputModel = parameterNode.GetNodeReference("decimatedModel")
        planeCutTool = parameterNode.GetNodeReference("planeCutTool")
        cutPlane = self.getCutPlane()

        shNode = slicer.mrmlScene.GetSubjectHierarchyNode()
        cutModelsFolder = shNode.GetItemByName("Cut Models")

        if (cutModelsFolder == 0) or (planeCutTool is None):
            slicer.mrmlScene.RemoveNode(planeCutTool)

            shNode.RemoveItem(cutModelsFolder)
            cutModelsFolder = shNode.CreateFolderItem(self.getParentFolderItemID(),"Cut Models")

            inputModel.GetDisplayNode().SetVisibility(False)
            decimatedInputModel.GetDisplayNode().SetVisibility(False)

            modelANode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLModelNode")
            modelANode.SetName("Cut Model A")
            slicer.mrmlScene.AddNode(modelANode)
            modelANode.CreateDefaultDisplayNodes()
            modelADisplayNode = modelANode.GetDisplayNode()
            modelADisplayNode.SetVisibility2D(True)

            modelAViewNode = slicer.mrmlScene.GetSingletonNode("1", "vtkMRMLViewNode")
            modelADisplayNode.AddViewNodeID(modelAViewNode.GetID())

            modelBNode = slicer.mrmlScene.CreateNodeByClass("vtkMRMLModelNode")
            modelBNode.SetName("Cut Model B")
            slicer.mrmlScene.AddNode(modelBNode)
            modelBNode.CreateDefaultDisplayNodes()
            modelBDisplayNode = modelBNode.GetDisplayNode()
            modelBDisplayNode.SetVisibility2D(True)

            modelBViewNode = slicer.mrmlScene.GetSingletonNode("2", "vtkMRMLViewNode")
            modelBDisplayNode.AddViewNodeID(modelBViewNode.GetID())

            redViewNode = slicer.app.layoutManager().sliceWidget("Red").mrmlSliceNode()
            greenViewNode = slicer.app.layoutManager().sliceWidget("Green").mrmlSliceNode()
            yellowViewNode = slicer.app.layoutManager().sliceWidget("Yellow").mrmlSliceNode()

            modelADisplayNode.AddViewNodeID(redViewNode.GetID())
            modelADisplayNode.AddViewNodeID(greenViewNode.GetID())
            modelADisplayNode.AddViewNodeID(yellowViewNode.GetID())

            modelBDisplayNode.AddViewNodeID(redViewNode.GetID())
            modelBDisplayNode.AddViewNodeID(greenViewNode.GetID())
            modelBDisplayNode.AddViewNodeID(yellowViewNode.GetID())

            #Set color of the model
            aux = slicer.mrmlScene.GetNodeByID('vtkMRMLColorTableNodeFileMediumChartColors.txt')
            colorTable = aux.GetLookupTable()
            colorwithalpha = colorTable.GetTableValue(0)
            color = [colorwithalpha[0],colorwithalpha[1],colorwithalpha[2]]
            modelADisplayNode.SetColor(color)
            colorwithalpha = colorTable.GetTableValue(1)
            color = [colorwithalpha[0],colorwithalpha[1],colorwithalpha[2]]
            modelBDisplayNode.SetColor(color)

            planeCutTool = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLDynamicModelerNode")
            planeCutTool.SetToolName("Plane cut")
            planeCutTool.SetNodeReferenceID("PlaneCut.InputModel", inputModel.GetID())
            planeCutTool.AddNodeReferenceID("PlaneCut.InputPlane", cutPlane.GetID()) 
            planeCutTool.SetNodeReferenceID("PlaneCut.OutputNegativeModel", modelANode.GetID())
            planeCutTool.SetNodeReferenceID("PlaneCut.OutputPositiveModel", modelBNode.GetID())
            planeCutTool.SetAttribute("OperationType", "Difference")

            parameterNode.SetNodeReferenceID("planeCutTool", planeCutTool.GetID())

            modelANodeItemID = shNode.GetItemByDataNode(modelANode)
            shNode.SetItemParent(modelANodeItemID, cutModelsFolder)
            modelBNodeItemID = shNode.GetItemByDataNode(modelBNode)
            shNode.SetItemParent(modelBNodeItemID, cutModelsFolder)

        slicer.modules.dynamicmodeler.logic().RunDynamicModelerTool(planeCutTool)
    
    def addCutPlaneObserver(self):
        cutPlane = self.getCutPlane()
        #self.cutPlaneObserver = cutPlane.AddObserver(vtk.vtkCommand.ModifiedEvent, self.onCutPlaneModified)
        self.cutPlaneObserver = cutPlane.AddObserver(
            slicer.vtkMRMLMarkupsNode.PointModifiedEvent, 
            lambda arg1,arg2: self.updatePointsTimer.start()
        )

    def addCylindersFiducialObserver(self):
        cylindersFiducial = self.getCylindersFiducial()
        self.cylindersFiducialObserver = cylindersFiducial.AddObserver(
            slicer.vtkMRMLMarkupsNode.PointEndInteractionEvent,
            lambda arg1,arg2: self.updatePointsTimer.start()
        )

    def removeCutPlaneObserver(self):
        cutPlane = self.getCutPlane()
        cutPlane.RemoveObserver(self.cutPlaneObserver)
        self.cutPlaneObserver = 0

    def removeCylindersFiducialObserver(self):
        cylindersFiducial = self.getCylindersFiducial()
        cylindersFiducial.RemoveObserver(self.cylindersFiducialObserver)
        self.cylindersFiducialObserver = 0

    def setCutPlaneLocked(self, value):
        pass

    def setCylindersFiducialLocked(self, value):
        pass

    def setInteractionsOfCutPlane(self, value):
        pass

    def setInteractionsOfCylindersFiducial(self, value):
        pass

    def copyHollowed(self, segmentationNode):
        # Create a segment editor to get access to effects
        segmentEditorWidget = slicer.qMRMLSegmentEditorWidget()
        segmentEditorWidget.setMRMLScene(slicer.mrmlScene)
        segmentEditorNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentEditorNode")
        segmentEditorWidget.setMRMLSegmentEditorNode(segmentEditorNode)
        segmentEditorWidget.setSegmentationNode(segmentationNode)
        #segmentEditorWidget.setMasterVolumeNode(masterVolumeNode)
        segmentEditorNode.SetOverwriteMode(slicer.vtkMRMLSegmentEditorNode.OverwriteNone)
        segmentEditorNode.SetMaskMode(slicer.vtkMRMLSegmentationNode.EditAllowedEverywhere)


        # Select the first segment
        targetID = segmentationNode.GetSegmentation().GetNthSegmentID(0)
        #segmentEditorWidget.setCurrentSegmentID(segmentID)


        # Get the segment ID for the segment with name "hollowed" or create it if it does not exist
        segmentName = self.HOLLOWED_SEGMENT_NAME
        segmentation = segmentationNode.GetSegmentation()
        hollowedSegmentID = segmentation.GetSegmentIdBySegmentName(segmentName)

        if not hollowedSegmentID:
            # Create a new segment with the name "hollowed"
            hollowedSegmentID = segmentation.AddEmptySegment(segmentName)
            #hollowedSegmentID = segmentation.GetSegmentIdBySegmentName(segmentName)


        # Copy the target
        segmentEditorWidget.setCurrentSegmentID(hollowedSegmentID)
        segmentEditorWidget.setActiveEffectByName("Logical operators")
        effect = segmentEditorWidget.activeEffect()
        effect.setParameter("Operation", "COPY")
        effect.setParameter("ModifierSegmentID", targetID)
        effect.self().onApply()


        # Set the effect to "Hollow"
        segmentEditorWidget.setActiveEffectByName("Hollow")
        effect = segmentEditorWidget.activeEffect()

        # Set parameters for the hollow effect
        effect.setParameter("ShellThicknessMm", 3)  # Set shell thickness in mm
        #effect.setParameter("ShellMode", "OUTSIDE_SURFACE")  # Options: "MEDIAL_SURFACE", "INSIDE_SURFACE", "OUTSIDE_SURFACE"
        effect.setParameter("ShellMode", "INSIDE_SURFACE")

        # Apply the effect
        effect.self().onApply()


#
# AddMagnetsToModelTest
#


class AddMagnetsToModelTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """Do whatever is needed to reset the state - typically a scene clear will be enough."""
        slicer.mrmlScene.Clear()

    def runTest(self):
        """Run as few or as many tests as needed here."""
        self.setUp()
        self.test_AddMagnetsToModel1()

    def test_AddMagnetsToModel1(self):
        """Ideally you should have several levels of tests.  At the lowest level
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
        inputVolume = SampleData.downloadSample("AddMagnetsToModel1")
        self.delayDisplay("Loaded test data set")

        inputScalarRange = inputVolume.GetImageData().GetScalarRange()
        self.assertEqual(inputScalarRange[0], 0)
        self.assertEqual(inputScalarRange[1], 695)

        outputVolume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode")
        threshold = 100

        # Test the module logic

        logic = AddMagnetsToModelLogic()

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

        self.delayDisplay("Test passed")

def project_point_to_plane(point, plane_origin, plane_normal):
    """
    Projects a 3D point onto a plane.

    :param point: 3D coordinate of the point (list or numpy array)
    :param plane_origin: 3D coordinate of the plane origin (list or numpy array)
    :param plane_normal: Normal vector of the plane (list or numpy array)
    :return: Projected point on the plane
    """
    point = np.array(point)
    plane_origin = np.array(plane_origin)
    plane_normal = np.array(plane_normal)
    plane_normal = plane_normal / np.linalg.norm(plane_normal)  # Normalize the normal
    distance = np.dot(point - plane_origin, plane_normal)
    projected_point = point - distance * plane_normal
    return projected_point

def getCentroid(model):
    pd = model.GetPolyData().GetPoints().GetData()
    from vtk.util.numpy_support import vtk_to_numpy
    return np.average(vtk_to_numpy(pd), axis=0)