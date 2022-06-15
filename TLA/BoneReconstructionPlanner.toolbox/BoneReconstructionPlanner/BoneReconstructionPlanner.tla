--------------------- MODULE BoneReconstructionPlanner ---------------------

\*CONSTANT planeWidgets, fibulaBoxesWidgets,mandibleBoxesWidgets, segmentationWidgets, workflowSteps
CONSTANT workflowSteps

VARIABLE planeParametersState
VARIABLE planesCreated
VARIABLE fibulaBoxesParametersState
VARIABLE fibulaBoxesCreated
VARIABLE mandibleBoxesParametersState
VARIABLE segmentationParametersState
VARIABLE segmentationModelsCreated
VARIABLE workflowState

TypeOK == 
  (*************************************************************************)
  (* The type-correctness invariant                                        *)
  (*************************************************************************)
  /\ planeParametersState \in {"valid", "invalid"}
  /\ planesCreated \in {"valid", "invalid"}
  /\ fibulaBoxesParametersState \in {"valid", "invalid"}
  /\ fibulaBoxesCreated \in {"valid", "invalid"}
  /\ mandibleBoxesParametersState \in {"valid", "invalid"}
  /\ segmentationParametersState \in {"valid", "invalid"}
  /\ segmentationModelsCreated \in {"valid", "invalid"}
  /\ workflowState \in workflowSteps
  \* a workflowstate means it is not processing, it has already been achieved
  
BRPInit == /\ planeParametersState = "invalid"
           /\ planesCreated = "invalid"
           /\ fibulaBoxesParametersState = "invalid"
           /\ fibulaBoxesCreated = "invalid"
           /\ mandibleBoxesParametersState = "invalid"
           /\ segmentationParametersState = "invalid"
           /\ segmentationModelsCreated = "invalid"     
           /\ workflowState = "start"
           

\* WORKFLOW
inputSegmentations ==   /\ workflowState = "start"
                        /\ UNCHANGED planeParametersState
                        /\ UNCHANGED planesCreated
                        /\ UNCHANGED fibulaBoxesParametersState
                        /\ UNCHANGED fibulaBoxesCreated
                        /\ UNCHANGED mandibleBoxesParametersState
                        /\ UNCHANGED segmentationModelsCreated
                        /\ workflowState' = "i_segmentations"
                        /\ segmentationParametersState' = "valid"

createSegmentationModels ==  /\ workflowState = "i_segmentations"
                             /\ segmentationParametersState = "valid"
                             /\ UNCHANGED segmentationParametersState
                             /\ UNCHANGED planeParametersState
                             /\ UNCHANGED planesCreated
                             /\ UNCHANGED fibulaBoxesParametersState
                             /\ UNCHANGED fibulaBoxesCreated
                             /\ UNCHANGED mandibleBoxesParametersState
                             /\ UNCHANGED planesCreated
                             /\ workflowState' = "p_segmentations"
                             /\ segmentationModelsCreated' = "valid"

inputPlaneParameters == /\ workflowState = "p_segmentations"
                        /\ segmentationModelsCreated' = "valid"
                        /\ UNCHANGED planesCreated
                        /\ UNCHANGED segmentationParametersState
                        /\ UNCHANGED fibulaBoxesParametersState
                        /\ UNCHANGED fibulaBoxesCreated
                        /\ UNCHANGED mandibleBoxesParametersState
                        /\ UNCHANGED segmentationModelsCreated
                        /\ workflowState' = "i_planes"
                        /\ planeParametersState' = "valid"
                        
createPlanes ==         /\ workflowState = "i_planes"
                        /\ planeParametersState = "valid"
                        /\ UNCHANGED segmentationParametersState
                        /\ UNCHANGED fibulaBoxesParametersState
                        /\ UNCHANGED fibulaBoxesCreated
                        /\ UNCHANGED mandibleBoxesParametersState
                        /\ UNCHANGED planeParametersState
                        /\ UNCHANGED segmentationModelsCreated
                        /\ workflowState' = "p_planes"
                        /\ planesCreated' = "valid"

inputFibulaBoxesParameters ==   /\ workflowState = "p_planes"
                                /\ planesCreated = "valid"
                                /\ UNCHANGED segmentationParametersState
                                /\ UNCHANGED segmentationModelsCreated
                                /\ UNCHANGED planeParametersState
                                /\ UNCHANGED planesCreated
                                /\ UNCHANGED fibulaBoxesCreated
                                /\ UNCHANGED mandibleBoxesParametersState
                                /\ workflowState' = "i_fibulaB"
                                /\ fibulaBoxesParametersState' = "valid"

createFibulaBoxes ==        /\ workflowState = "i_fibulaB"
                            /\ fibulaBoxesParametersState = "valid"
                            /\ UNCHANGED segmentationParametersState
                            /\ UNCHANGED segmentationModelsCreated
                            /\ UNCHANGED fibulaBoxesParametersState
                            /\ UNCHANGED mandibleBoxesParametersState
                            /\ UNCHANGED planeParametersState
                            /\ UNCHANGED planesCreated
                            /\ UNCHANGED segmentationModelsCreated
                            /\ workflowState' = "p_fibulaB"
                            /\ fibulaBoxesCreated' = "valid"
                       

BRPInitNext ==    \/ inputSegmentations
                  \/ createSegmentationModels
                  \/ inputPlaneParameters
                  \/ createPlanes
                  \/ inputFibulaBoxesParameters
                  \/ createFibulaBoxes

FinishedWorkflow == workflowState # "p_fibulaB"
 
=============================================================================
\* Modification History
\* Last modified Wed Jun 15 18:48:03 ART 2022 by mau_i
\* Created Wed Jun 15 17:33:27 ART 2022 by mau_i
