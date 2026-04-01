import slicer
import qt
from DentalSegmentatorLib import PythonDependencyChecker
from SlicerNNUNetLib import Parameter, InstallLogic, SegmentationLogic
from typing import Optional
from pathlib import Path

class DentalSegmentatorHelper:
    def __init__(self, dentalSegmentatorAIModelDir = ""):
        # default values for the parameters, can be changed through code
        self.DENTAL_SEGMENTATOR_AI_MODEL_DIR = dentalSegmentatorAIModelDir or qt.QStandardPaths.writableLocation(qt.QStandardPaths.AppDataLocation) + "/DentalSegmentatorAIModel/"
        self.headCTCorticalBoneThreshold = 200
        self.islandMinimumSize = 1000 # in mm3, used in the wrapBigIslands function to determine which islands should be wrapped
        #self.growShrinkIterations = 5
        self.CORTICAL_MANDIBLE_SEGMENT_NAME = "Mandible"
        self.UPPER_SKULL_SEGMENT_NAME = "Upper Skull"
        self.MANDIBULAR_CANAL_SEGMENT_NAME = "Mandibular canal"
        self.UPPER_TEETH_SEGMENT_NAME = "Upper Teeth"
        self.LOWER_TEETH_SEGMENT_NAME = "Lower Teeth"
        self.segmentNamesToAdd = [
            self.MANDIBULAR_CANAL_SEGMENT_NAME,
            self.LOWER_TEETH_SEGMENT_NAME
        ]
        # install dependencies if needed
        # self.installAIDependenciesIfNeeded(forceReinstall=False)

    def doFullAIWorkflow(
        self
    ):
        #self.installAIDependenciesIfNeeded()
        self.runSegmentationAI()
        self.optimizeSegmentation()
        self.setVisibleSegments(
            [
                self.CORTICAL_MANDIBLE_SEGMENT_NAME,
                self.UPPER_SKULL_SEGMENT_NAME
            ]
        )

    def forceReinstallAIDependencies(self):
        self.installAIDependenciesIfNeeded(forceReinstall=True)
        print("If forced reinstall does not work please try reinstalling from pip yourself")

    def showProgressFunction(self, message: Optional[str] = None) -> None:
        """Display progress message to user."""
        print(message) # or use onProgressInfo from DentalSegmentator
        return

    def installAIDependenciesIfNeeded(self, forceReinstall=False):
        print("Installing AI dependencies, this may take a while...")
        NNUnetlogic = InstallLogic()
        if forceReinstall:
            NNUnetlogic._uninstallNNUnetIfNeeded()
        NNUnetlogic.progressInfo.connect(self.showProgressFunction)
        NNUnetlogic.setupPythonRequirements()

        modelDir = qt.QDir(self.DENTAL_SEGMENTATOR_AI_MODEL_DIR)
        if modelDir.exists() and forceReinstall:
            modelDir.removeRecursively()
        modelDir.mkpath(".")
        destWeightFolder = Path(modelDir.absolutePath())
        deps = PythonDependencyChecker(destWeightFolder=destWeightFolder)
        deps.downloadWeightsIfNeeded(self.showProgressFunction)

    # setters
    def setVolumeNode(self, volumeNode):
        self.volumeNode = volumeNode

    def setSegmentationNode(self, segmentationNode):
        self.segmentationNode = segmentationNode

    def setParameter(self, parameterName, parameterValue):
        if parameterName == "headCTCorticalBoneThreshold":
            self.headCTCorticalBoneThreshold = parameterValue
        elif parameterName == "segmentNamesToAdd":
            self.segmentNamesToAdd = parameterValue
        else:
            raise ValueError(f"Parameter {parameterName} not found")

    # the argument should be a dict with the keys "headCTCorticalBoneThreshold", "growShrinkIterations" and "segmentsNamesOfInterest"
    def setParameters(self, parameters: dict):
        self.headCTCorticalBoneThreshold = parameters.get("headCTCorticalBoneThreshold", self.headCTCorticalBoneThreshold)
        #self.growShrinkIterations = parameters.get("growShrinkIterations", self.growShrinkIterations)
        self.segmentNamesToAdd = parameters.get("segmentNamesToAdd", self.segmentNamesToAdd)

    # getters
    def getVolumeNode(self):
        return self.volumeNode

    def getSegmentationNode(self):
        return self.segmentationNode
    
    def getParameter(self, parameterName):
        if parameterName == "headCTCorticalBoneThreshold":
            return self.headCTCorticalBoneThreshold
        #elif parameterName == "growShrinkIterations":
        #    return self.growShrinkIterations
        elif parameterName == "segmentNamesToAdd":
            return self.segmentNamesToAdd
        else:
            raise ValueError(f"Parameter {parameterName} not found")

    def getParameters(self):
        return {
            "headCTCorticalBoneThreshold": self.headCTCorticalBoneThreshold,
            #"growShrinkIterations": self.growShrinkIterations,
            "segmentNamesToAdd": self.segmentNamesToAdd
        }

    def runSegmentationAI(self):
        inputVolume = self.getVolumeNode()

        destWeightFolder = Path(self.DENTAL_SEGMENTATOR_AI_MODEL_DIR)
        
        try:
            import torch
        except ImportError:
            print("torch module is not available. Please install it to use the AI segmentation features.")
            return
        
        parameter = Parameter(
            folds="0", 
            modelPath=destWeightFolder.resolve(), 
            device='cuda' if torch.cuda.is_available() else 'cpu'
        )
        
        dentalSegmentatorLogic = SegmentationLogic()
        #dentalSegmentatorLogic.inferenceFinished.connect(loadSegmentationAfterInference)
        dentalSegmentatorLogic.setParameter(parameter)
        dentalSegmentatorLogic.startSegmentation(inputVolume)
        dentalSegmentatorLogic.waitForSegmentationFinished()

        segmentation_node = slicer.util.loadSegmentation(dentalSegmentatorLogic._outFile)
        dentalSegmentatorLogic._renameSegments(segmentation_node)
        segmentation = segmentation_node.GetSegmentation()
        if self.getSegmentationNode():
            # copy content of the new segmentation to the existing one
            existingSegmentation = self.getSegmentationNode().GetSegmentation()
            existingSegmentation.RemoveAllSegments()
            for segmentIndex in range(segmentation.GetNumberOfSegments()):
                segmentID = segmentation.GetNthSegmentID(segmentIndex)
                segment = segmentation.GetSegment(segmentID)
                existingSegmentation.AddSegment(segment)
            slicer.mrmlScene.RemoveNode(segmentation_node)
        else:
            self.setSegmentationNode(segmentation_node)
            segmentation_node.SetName("HeadSegmentation")

    def loadSegmentation(self) -> "slicer.vtkMRMLSegmentationNode":
        try:
            segmentationNode = slicer.util.loadSegmentation(self._outFile)
            self._renameSegments(segmentationNode)
            return segmentationNode
        except StopIteration:
            raise RuntimeError(
                "Failed to load the segmentation.\n"
                "Something went wrong during the nnUNet processing.\n"
                "Please check the logs for potential errors and contact the library maintainers."
            )
        
    def stopSegmentationAI():
        print("Not possible to stop the AI segmentation once started because it runs on SlicerPython")

    def optimizeSegmentation(
        self
    ):
        self.addSegments(
            targetSegmentName = self.CORTICAL_MANDIBLE_SEGMENT_NAME, 
            segmentNamesToAddList = [
                self.MANDIBULAR_CANAL_SEGMENT_NAME,
                self.LOWER_TEETH_SEGMENT_NAME
            ]
        )
        self.addSegments(
            targetSegmentName = self.UPPER_SKULL_SEGMENT_NAME, 
            segmentNamesToAddList = [
                self.UPPER_TEETH_SEGMENT_NAME
            ]
        )
        targetSegmentsNamesList = [
            self.CORTICAL_MANDIBLE_SEGMENT_NAME,
            self.UPPER_SKULL_SEGMENT_NAME
        ]
        self.fillHolesAndGrowSegments(targetSegmentsNamesList)
        #return
        self.wrapBigIslands(targetSegmentsNamesList)

    def addSegments(
        self,
        targetSegmentName,
        segmentNamesToAddList
    ):
        volumeNode = self.getVolumeNode()
        segmentationNode = self.getSegmentationNode()

        # find the segment IDs to be edited
        segmentation_vtk = segmentationNode.GetSegmentation()

        targetSegmentID = None
        for i in range(segmentation_vtk.GetNumberOfSegments()):
            segmentID = segmentation_vtk.GetNthSegmentID(i)
            segment = segmentation_vtk.GetSegment(segmentID)
            if segment.GetName() == targetSegmentName:
                targetSegmentID = segmentID
                break

        segmentIDsToAddList = []
        for segmentName in segmentNamesToAddList:
            for i in range(segmentation_vtk.GetNumberOfSegments()):
                segmentID = segmentation_vtk.GetNthSegmentID(i)
                segment = segmentation_vtk.GetSegment(segmentID)
                if segment.GetName() == segmentName:
                    segmentIDsToAddList.append(segmentID)
                    break
                
        # set up segment editor and configure it
        segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
        segmentEditorNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentEditorNode")
        segmentEditorWidget.setMRMLSegmentEditorNode(segmentEditorNode)
        segmentEditorWidget.setSegmentationNode(segmentationNode)
        segmentEditorWidget.setSourceVolumeNode(volumeNode)

        segmentEditorNode.SetOverwriteMode(slicer.vtkMRMLSegmentEditorNode.OverwriteNone)
        segmentEditorNode.SetMaskMode(slicer.vtkMRMLSegmentationNode.EditAllowedEverywhere)
        segmentEditorNode.SetSourceVolumeIntensityMask(False)

        segmentEditorWidget.setCurrentSegmentID(targetSegmentID)
        for segmentID in segmentIDsToAddList:
            segmentEditorWidget.setActiveEffectByName("Logical operators")
            effect = segmentEditorWidget.activeEffect()
            effect.setParameter("Operation", "UNION")
            effect.setParameter("ModifierSegmentID", segmentID)
            effect.setParameter("BypassMasking", str(1))
            effect.self().onApply()

    def fillHolesAndGrowSegments(
            self,
            targetSegmentsNamesList
        ):
        volumeNode = self.getVolumeNode()
        segmentationNode = self.getSegmentationNode()
        segmentNamesList = targetSegmentsNamesList
        threshold = self.headCTCorticalBoneThreshold
        
        # find the segment IDs to be edited
        segmentation_vtk = segmentationNode.GetSegmentation()

        segmentIDsList = []
        for segmentName in segmentNamesList:
            for i in range(segmentation_vtk.GetNumberOfSegments()):
                segmentID = segmentation_vtk.GetNthSegmentID(i)
                segment = segmentation_vtk.GetSegment(segmentID)
                if segment.GetName() == segmentName:
                    segmentIDsList.append(segmentID)
                    break
                
        # set up segment editor and configure it
        segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
        segmentEditorNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentEditorNode")
        segmentEditorWidget.setMRMLSegmentEditorNode(segmentEditorNode)
        segmentEditorWidget.setSegmentationNode(segmentationNode)
        segmentEditorWidget.setSourceVolumeNode(volumeNode)

        segmentEditorNode.SetOverwriteMode(slicer.vtkMRMLSegmentEditorNode.OverwriteNone)
        segmentEditorNode.SetMaskMode(slicer.vtkMRMLSegmentationNode.EditAllowedEverywhere)
        segmentEditorNode.SetSourceVolumeIntensityMask(False)

        for segmentID in segmentIDsList:
            segmentEditorWidget.setCurrentSegmentID(segmentID)
            
            segmentEditorWidget.setActiveEffectByName("Smoothing")
            effect = segmentEditorWidget.activeEffect()
            effect.setParameter("SmoothingMethod", "MORPHOLOGICAL_CLOSING")
            effect.setParameter("KernelSizeMm", str(2.0))
            effect.self().onApply()


        segmentEditorNode.SetSourceVolumeIntensityMask(True)
        scalarRange = volumeNode.GetImageData().GetScalarRange()
        for segmentID in segmentIDsList:
            segmentEditorWidget.setCurrentSegmentID(segmentID)
            segmentEditorWidget.setActiveEffectByName("Margin")
            effect = segmentEditorWidget.activeEffect()

            marginMm = 1.0
            segmentEditorNode.SetSourceVolumeIntensityMaskRange(threshold, scalarRange[1])
            effect.setParameter("MarginSizeMm", str(marginMm))
            effect.self().onApply()
        
    def wrapBigIslands(
        self,
        targetSegmentsNamesList
    ):
        volumeNode = self.getVolumeNode()
        segmentationNode = self.getSegmentationNode()

        # find the segment IDs to be edited
        segmentation_vtk = segmentationNode.GetSegmentation()

        targetSegmentIDsList = []
        for segmentName in targetSegmentsNamesList:
            for i in range(segmentation_vtk.GetNumberOfSegments()):
                segmentID = segmentation_vtk.GetNthSegmentID(i)
                segment = segmentation_vtk.GetSegment(segmentID)
                if segment.GetName() == segmentName:
                    targetSegmentIDsList.append(segmentID)
                    break
                
        # set up segment editor and configure it
        segmentEditorWidget = slicer.modules.segmenteditor.widgetRepresentation().self().editor
        segmentEditorNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLSegmentEditorNode")
        segmentEditorWidget.setMRMLSegmentEditorNode(segmentEditorNode)
        segmentEditorWidget.setSegmentationNode(segmentationNode)
        segmentEditorWidget.setSourceVolumeNode(volumeNode)

        segmentEditorNode.SetOverwriteMode(slicer.vtkMRMLSegmentEditorNode.OverwriteNone)
        segmentEditorNode.SetMaskMode(slicer.vtkMRMLSegmentationNode.EditAllowedEverywhere)
        segmentEditorNode.SetSourceVolumeIntensityMask(False)

        for targetSegmentID in targetSegmentIDsList:
            segmentEditorWidget.setCurrentSegmentID(targetSegmentID)
            
            # Split islands dismissing small ones
            segmentEditorWidget.setActiveEffectByName("Islands")
            effect = segmentEditorWidget.activeEffect()
            effect.setParameter("Operation", "SPLIT_ISLANDS_TO_SEGMENTS")
            effect.setParameter("MinimumSize", str(self.islandMinimumSize))
            effect.self().onApply()

            # Find islands created by the split
            targetSegmentName = segmentation_vtk.GetSegment(targetSegmentID).GetName()
            segmentsToWrapIDs = [targetSegmentID]
            for i in range(segmentation_vtk.GetNumberOfSegments()):
                candidateSegmentID = segmentation_vtk.GetNthSegmentID(i)
                candidateSegment = segmentation_vtk.GetSegment(candidateSegmentID)
                if (
                    (targetSegmentName in candidateSegment.GetName()) and
                    (candidateSegmentID != targetSegmentID)
                ):
                    segmentsToWrapIDs.append(candidateSegmentID)
            
            # Wrap each island
            for wrapSegmentID in segmentsToWrapIDs:
                segmentEditorWidget.setCurrentSegmentID(wrapSegmentID)
                segmentEditorWidget.setActiveEffectByName("Wrap Solidify")
                effect = segmentEditorWidget.activeEffect()
                effect.setParameter("region", "outerSurface")
                effect.setParameter("remeshOversampling", str(1.5))
                effect.setParameter("smoothingFactor", str(0.2))
                effect.setParameter("shrinkwrapIterations", str(6))
                effect.setParameter("carveHolesInOuterSurface", str(True))
                #effect.setParameter("carveHolesInOuterSurfaceDiameter", str(50))
                effect.self().onApply()

            # Merge islands back together the wrapped segments
            segmentEditorWidget.setCurrentSegmentID(segmentsToWrapIDs[0])
            segmentsToDeleteIDs = []
            for i in range(1,len(segmentsToWrapIDs)):
                segmentToAddID = segmentsToWrapIDs[i]
                segmentEditorWidget.setActiveEffectByName("Logical operators")
                effect = segmentEditorWidget.activeEffect()
                effect.setParameter("Operation", "UNION")
                effect.setParameter("ModifierSegmentID", segmentToAddID)
                effect.setParameter("BypassMasking", str(1))
                effect.self().onApply()
                segmentsToDeleteIDs.append(segmentToAddID)
            
            for segmentToDeleteID in segmentsToDeleteIDs:
                segmentation_vtk.RemoveSegment(segmentToDeleteID)

    def setVisibleSegments(
            self,
            segmentNamesList = None
        ):
        segmentationNode = self.getSegmentationNode()
        # find the segment IDs to be set visible
        segmentation_vtk = segmentationNode.GetSegmentation()

        segmentIDsList = []
        for segmentName in segmentNamesList:
            for i in range(segmentation_vtk.GetNumberOfSegments()):
                segmentID = segmentation_vtk.GetNthSegmentID(i)
                segment = segmentation_vtk.GetSegment(segmentID)
                if segment.GetName() == segmentName:
                    segmentIDsList.append(segmentID)
                    break
                
        # set all segments invisible
        for i in range(segmentation_vtk.GetNumberOfSegments()):
            segmentID = segmentation_vtk.GetNthSegmentID(i)
            segmentationNode.GetDisplayNode().SetSegmentVisibility(segmentID, False)

        # set selected segments visible
        for segmentID in segmentIDsList:
            segmentationNode.GetDisplayNode().SetSegmentVisibility(segmentID, True)
        
        segmentationNode.CreateClosedSurfaceRepresentation()

    
    def loadSegmentationAfterInference(parameterNodeToModify, unused1 = None):
        try:
            segmentationNode = slicer.util.loadSegmentation(dentalSegmentatorLogic._outFile)
            renameDentalSegments(segmentationNode)
            parameterNodeToModify.SetNodeReferenceID("mandibleSegmentation", segmentationNode.GetID())
            return
        except StopIteration:
            raise RuntimeError(
                "Failed to load the segmentation.\n"
                "Something went wrong during the nnUNet processing.\n"
                "Please check the logs for potential errors and contact the library maintainers."
            )

    def renameDentalSegments(segmentationNode: "slicer.vtkMRMLSegmentationNode") -> None:
        """
        Rename loaded segments with dataset file labels dict.
        """
        labels = self._nnUNetParam.readSegmentIdsAndLabelsFromDatasetFile()
        if labels is None:
            return

        for segmentId, label in labels:
            segment = segmentationNode.GetSegmentation().GetSegment(segmentId)
            if segment is None:
                continue
            segment.SetName(label)

