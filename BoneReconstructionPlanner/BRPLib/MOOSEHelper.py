import slicer

bone_names = {
    "carpal_left": "Left Carpal",
    "carpal_right": "Right Carpal",
    "clavicle_left": "Left Clavicle",
    "clavicle_right": "Right Clavicle",
    "femur_left": "Left Femur",
    "femur_right": "Right Femur",
    "fibula_left": "Left Fibula",
    "fibula_right": "Right Fibula",
    "fingers_left": "Left Fingers",
    "fingers_right": "Right Fingers",
    "humerus_left": "Left Humerus",
    "humerus_right": "Right Humerus",
    "metacarpal_left": "Left Metacarpal",
    "metacarpal_right": "Right Metacarpal",
    "metatarsal_left": "Left Metatarsal",
    "metatarsal_right": "Right Metatarsal",
    "patella_left": "Left Patella",
    "patella_right": "Right Patella",
    "radius_left": "Left Radius",
    "radius_right": "Right Radius",
    "scapula_left": "Left Scapula",
    "scapula_right": "Right Scapula",
    "skull": "Skull",
    "tarsal_left": "Left Tarsal",
    "tarsal_right": "Right Tarsal",
    "tibia_left": "Left Tibia",
    "tibia_right": "Right Tibia",
    "toes_left": "Left Toes",
    "toes_right": "Right Toes",
    "ulna_left": "Left Ulna",
    "ulna_right": "Right Ulna",
}

class MOOSEHelper:
    def __init__(self):
        # default values for the parameters, can be changed through code
        self.AI_MODEL_NAME = "clin_ct_peripheral_bones"
        self.limitBoneHUValueMoose = 200
        self.growShrinkIterations = 5
        self.LEFT_FIBULA_SEGMENT_NAME = "Left Fibula"
        self.RIGHT_FIBULA_SEGMENT_NAME = "Right Fibula"
        self.segmentsNamesOfInterest = [
            self.LEFT_FIBULA_SEGMENT_NAME,
            self.RIGHT_FIBULA_SEGMENT_NAME
        ]
        # install dependencies if needed
        # self.installAIDependenciesIfNeeded(forceReinstall=False)

    def doFullAIWorkflow(
        self
    ):
        #self.installAIDependenciesIfNeeded()
        self.runSegmentationAI()
        self.renameSegments(bone_names)
        self.optimizeSegmentation()
        self.setVisibleSegments(self.segmentsNamesOfInterest)

    def installAIDependenciesIfNeeded(self, forceReinstall=False):
        from MOOSE import DependencyManager
        dependencyManager = DependencyManager()
        if forceReinstall or (dependencyManager.get_dependencies_install_status() is False):
            print("Installing AI dependencies, this may take a while...")
            dependencyManager.install_all_dependencies()
            # After installing/upgrading packages (e.g., pydicom 2.x → 3.x),
            # stale modules remain cached in sys.modules from the old version.
            # Clear them so the newly installed versions are imported correctly
            # without requiring a Slicer restart.
            self._clearStaleModules()

    @staticmethod
    def _clearStaleModules():
        """Remove cached modules that may be stale after dependency installation."""
        import sys
        prefixes_to_clear = ["pydicom", "dicom2nifti", "moosez"]
        stale_keys = [
            key for key in sys.modules
            if any(key == prefix or key.startswith(prefix + ".")
                   for prefix in prefixes_to_clear)
        ]
        for key in stale_keys:
            del sys.modules[key]

    def forceReinstallAIDependencies(self):
        self.installAIDependenciesIfNeeded(forceReinstall=True)
        print("If forced reinstall does not work please try reinstalling from pip yourself")

    # setters
    def setVolumeNode(self, volumeNode):
        self.volumeNode = volumeNode

    def setSegmentationNode(self, segmentationNode):
        self.segmentationNode = segmentationNode

    def setParameter(self, parameterName, parameterValue):
        if parameterName == "limitBoneHUValueMoose":
            self.limitBoneHUValueMoose = parameterValue
        elif parameterName == "growShrinkIterations":
            self.growShrinkIterations = parameterValue
        elif parameterName == "segmentsNamesOfInterest":
            self.segmentsNamesOfInterest = parameterValue
        else:
            raise ValueError(f"Parameter {parameterName} not found")
    
    # the argument should be a dict with the keys "limitBoneHUValueMoose", "growShrinkIterations" and "segmentsNamesOfInterest"
    def setParameters(self, parameters: dict):
        self.limitBoneHUValueMoose = parameters.get("limitBoneHUValueMoose", self.limitBoneHUValueMoose)
        self.growShrinkIterations = parameters.get("growShrinkIterations", self.growShrinkIterations)
        self.segmentsNamesOfInterest = parameters.get("segmentsNamesOfInterest", self.segmentsNamesOfInterest)

    # getters
    def getVolumeNode(self):
        return self.volumeNode

    def getSegmentationNode(self):
        return self.segmentationNode
    
    def getParameter(self, parameterName):
        if parameterName == "limitBoneHUValueMoose":
            return self.limitBoneHUValueMoose
        elif parameterName == "growShrinkIterations":
            return self.growShrinkIterations
        elif parameterName == "segmentsNamesOfInterest":
            return self.segmentsNamesOfInterest
        else:
            raise ValueError(f"Parameter {parameterName} not found")

    def getParameters(self):
        return {
            "limitBoneHUValueMoose": self.limitBoneHUValueMoose,
            "growShrinkIterations": self.growShrinkIterations,
            "segmentsNamesOfInterest": self.segmentsNamesOfInterest
        }
    
    def runSegmentationAI(
        self
    ):
        inputVolume = self.getVolumeNode()
        segmentationNode = self.getSegmentationNode()
        AIModelName = self.AI_MODEL_NAME

        # now segment using AI
        if not inputVolume or not AIModelName:
            raise RuntimeError("Please select an input volume and model.")

        from MOOSE import MOOSELogic
        mooseLogic = MOOSELogic()
        moose_folder, subject_folder = mooseLogic.prepare_data(inputVolume)
        segmentation_file, label_indices = mooseLogic.run_segmentation(moose_folder, subject_folder, AIModelName)

        if not segmentation_file:
            raise RuntimeError("Could not infer segmentation from provided dataset. Check the FOV.")

        properties = {"name": f"{inputVolume.GetName()}_{AIModelName}_segmentation"}
        segmentation_node = slicer.util.loadSegmentation(segmentation_file, properties=properties)
        segmentation = segmentation_node.GetSegmentation()
        for segmentIndex in range(segmentation.GetNumberOfSegments()):
            segmentID = segmentation.GetNthSegmentID(segmentIndex)
            segmentID_numeric = int(segmentID.replace("Segment_", ""))
            segment = segmentation.GetSegment(segmentID)
            newName = label_indices[segmentID_numeric]
            segment.SetName(newName)

        import shutil
        shutil.rmtree(moose_folder)

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
            segmentation_node.SetName("LegsSegmentation")

    def stopSegmentationAI():
        print("Not possible to stop the AI segmentation once started because it runs on SlicerPython")

    def optimizeSegmentation(
        self
    ):
        self.improveSegmentsQualityWithMorphologicalOperations()
        self.fillHolesOfSegments()
    
    # replace the arguments with the ones set in the class attributes, and use the class attributes instead of the arguments
    def improveSegmentsQualityWithMorphologicalOperations(
        self
    ):        
        volumeNode = self.getVolumeNode()
        segmentationNode = self.getSegmentationNode()
        threshold = self.limitBoneHUValueMoose
        algorithmIterations = self.growShrinkIterations
        segmentNamesList = self.segmentsNamesOfInterest
        
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
        segmentEditorNode.SetSourceVolumeIntensityMask(True)


        scalarRange = volumeNode.GetImageData().GetScalarRange()
        for segmentID in segmentIDsList:
            segmentEditorWidget.setCurrentSegmentID(segmentID)
            segmentEditorWidget.setActiveEffectByName("Margin")
            effect = segmentEditorWidget.activeEffect()

            marginMm = 1.0
            for i in range(algorithmIterations):
                # grow
                segmentEditorNode.SetSourceVolumeIntensityMaskRange(threshold, scalarRange[1])
                effect.setParameter("MarginSizeMm", str(marginMm))
                effect.self().onApply()
                # shrink
                segmentEditorNode.SetSourceVolumeIntensityMaskRange(scalarRange[0], threshold)
                effect.setParameter("MarginSizeMm", str(-marginMm))
                effect.self().onApply()

    def fillHolesOfSegments(
        self
        ):

        volumeNode = self.getVolumeNode()
        segmentationNode = self.getSegmentationNode()
        segmentNamesList = self.segmentsNamesOfInterest

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
            
            segmentEditorWidget.setActiveEffectByName("Islands")
            effect = segmentEditorWidget.activeEffect()
            effect.setParameter("Operation", "KEEP_LARGEST_ISLAND")
            effect.setParameter("MinimumSize", str(1000))
            effect.self().onApply()

            segmentEditorWidget.setActiveEffectByName("Smoothing")
            effect = segmentEditorWidget.activeEffect()
            effect.setParameter("SmoothingMethod", "MORPHOLOGICAL_CLOSING")
            effect.setParameter("KernelSizeMm", str(2.0))
            effect.self().onApply() # this line could be optional

            segmentEditorWidget.setActiveEffectByName("Wrap Solidify")
            effect = segmentEditorWidget.activeEffect()
            effect.setParameter("region", "outerSurface")
            effect.setParameter("remeshOversampling", str(1.5))
            effect.setParameter("smoothingFactor", str(0.2))
            effect.setParameter("shrinkwrapIterations", str(6))
            effect.self().onApply()

    def setVisibleSegments(
            self,
            segmentNamesList = None
        ):
        # use given or default segment names list
        segmentNamesList = segmentNamesList or self.segmentsNamesOfInterest
        
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

    def renameSegments(self, renameDict: dict):
        segmentationNode = self.getSegmentationNode()
        segmentation_vtk = segmentationNode.GetSegmentation()
        for segmentIndex in range(segmentation_vtk.GetNumberOfSegments()):
            segmentID = segmentation_vtk.GetNthSegmentID(segmentIndex)
            segment = segmentation_vtk.GetSegment(segmentID)
            oldName = segment.GetName()
            if oldName in renameDict:
                newName = renameDict[oldName]
                segment.SetName(newName)