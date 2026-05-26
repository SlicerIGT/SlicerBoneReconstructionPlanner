# Implementation Plan: Propagate transformVolume to All Fibula-Linked Nodes

## Problem Statement

When the user toggles the `transformVolume` button, `updateNormalizationFibulaLineTransform()` computes a rotation that aligns the fibula line with Z-axis (or resets it to identity). Currently, **only the `currentScalarVolume`** is placed under the `fibulaNormalizationTransformNode`. All other fibula-linked 3D nodes in the fibula view remain unaffected, causing a visual mismatch between the CT volume and the overlaid models/markups.

## Current Behavior (lines 5152–5197)

`updateNormalizationFibulaLineTransform(transformVolumeChecked)`:
1. Gets or creates `fibulaNormalizationTransformNode` (a `vtkMRMLLinearTransformNode`).
2. Attaches **only** `currentScalarVolume` to the transform via `SetAndObserveTransformNodeID`.
3. If checked → sets a rotation matrix; if unchecked → sets identity.

## Fibula-Linked Nodes That Need the Transform

These are the nodes **visible in the fibula 3D view** whose position, orientation, or pose should rotate together with the volume:

| # | Node(s) | Type | Container / Reference Key | Currently Transformed? |
|---|---------|------|---------------------------|------------------------|
| 1 | `fibulaModelNode` | `vtkMRMLModelNode` | parameterNode ref `"fibulaModelNode"` | No |
| 2 | `decimatedFibulaModelNode` | `vtkMRMLModelNode` | parameterNode ref `"decimatedFibulaModelNode"` | No |
| 3 | `fibulaLine` | `vtkMRMLMarkupsLineNode` | parameterNode ref `"fibulaLine"` | No |
| 4 | Fibula planes | `vtkMRMLMarkupsPlaneNode` | folder `"Fibula planes"` | No |
| 5 | Fibula segment length labels | text/model nodes | folder `"Fibula Segments Lengths"` | No |
| 6 | Cut bone pieces (fibula segments) | `vtkMRMLModelNode` | folder `"Cut Bones"` (all but last, which is resected mandible) | No |
| 7 | Transformed mandible pieces (shown in fibula view) | `vtkMRMLModelNode` | folder `"Transformed Mandible Pieces"` | No |
| 8 | Transformed full mandibles (shown in fibula view) | `vtkMRMLModelNode` | folder `"Transformed Full Mandible"` | No |
| 9 | Miter box models | `vtkMRMLModelNode` | folder `"miterBoxes Models"` | No |
| 10 | Bigger miter box models | `vtkMRMLModelNode` | folder `"biggerMiterBoxes Models"` | No |
| 11 | Preview miter box models | `vtkMRMLModelNode` | folder `"Preview Miter Boxes Models"` | No |
| 12 | Fibula cylinders models | `vtkMRMLModelNode` | folder `"Fibula Cylinders Models"` | No |
| 13 | Dental implant cylinders models | `vtkMRMLModelNode` | folder `"Dental Implants Cylinders Models"` | No |
| 14 | Fibula dental implant cylinders | `vtkMRMLModelNode` | folder `"Fibula Dental Implants Cylinders Models"` | No |
| 15 | Bigger fibula dental implant cylinders | `vtkMRMLModelNode` | folder `"Bigger Fibula Dental Implants Cylinders Models"` | No |
| 16 | Fibula surgical guide prototype | `vtkMRMLModelNode` | parameterNode ref `"fibulaSurgicalGuidePrototypeModel"` | No |
| 17 | `currentScalarVolume` | `vtkMRMLScalarVolumeNode` | parameterNode ref `"currentScalarVolume"` | **Yes** (the only one today) |

## Proposed Approach

### Strategy: apply `fibulaNormalizationTransformNode` to all fibula-linked nodes (live, not hardened)

Rather than hardening the transform into each node's geometry (which would require recomputing every time the button is toggled), we keep the transform **live** by calling `SetAndObserveTransformNodeID(fibulaNormalizationTransformNode.GetID())` on each node. When the transform matrix changes (identity ↔ rotation), all attached nodes update automatically via the MRML observer mechanism.

When detaching (e.g., before an operation that expects untransformed coordinates), we call `SetAndObserveTransformNodeID(None)`.

This is the same pattern already used for `currentScalarVolume`.

### Implementation Steps

#### Step 1: Add a helper method `getNodesLinkedToFibula()`

Create a new method in `BoneReconstructionPlannerLogic` that collects all the fibula-linked nodes that currently exist in the scene. The method should return a flat list of MRML nodes.

```python
def getNodesLinkedToFibula(self):
    parameterNode = self.getParameterNode()
    nodes = []

    # Individual node references
    for refKey in ["fibulaModelNode", "decimatedFibulaModelNode", "fibulaLine",
                   "fibulaSurgicalGuidePrototypeModel"]:
      node = parameterNode.GetNodeReference(refKey)
      if node is not None:
        nodes.append(node)

    # Folder-based lists (these may or may not exist at a given point in the workflow)
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
      "Preview Miter Boxes Models",
      "Fibula Cylinders Models",
      "Dental Implants Cylinders Models",
      "Fibula Dental Implants Cylinders Models",
      "Bigger Fibula Dental Implants Cylinders Models",
    ]
    for folderName in folderNames:
      nodesList = createListFromFolderName(folderName)
      nodes.extend(nodesList)

    return nodes
```

#### Step 2: Modify `updateNormalizationFibulaLineTransform()`

After the existing logic that sets the transform matrix, iterate over all fibula-linked nodes and attach them to `fibulaNormalizationTransformNode`:

```python
def updateNormalizationFibulaLineTransform(self, transformVolumeChecked):
    # ... existing code that creates/retrieves fibulaNormalizationTransformNode
    # ... existing code that applies transform to currentScalarVolume
    # ... existing code that sets identity or rotation matrix

    # NEW: Apply the same transform to all fibula-linked nodes
    fibulaLinkedNodes = self.getNodesLinkedToFibula()
    for node in fibulaLinkedNodes:
      node.SetAndObserveTransformNodeID(fibulaNormalizationTransformNode.GetID())
```

The key insight is that the transform node already has either the identity or the rotation matrix set by the time we reach this point, so all nodes will be in the correct position regardless of whether the checkbox is checked or unchecked. Identity transform means no visual change; rotation transform rotates all nodes together.

#### Step 3: Ensure newly-created fibula nodes also get the transform

Several methods create new nodes in the fibula view **after** `updateNormalizationFibulaLineTransform` has run. These methods must also attach new nodes to the transform:

1. **`generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandible()`** — At the end, after all sub-steps, call `self.updateNormalizationFibulaLineTransform(transformVolumeChecked)` to re-attach all nodes (including newly created ones). Since it already resets folders, the stale references are gone.

2. **`createMiterBoxesFromFibulaPlanes()`** — At the end, apply the normalization transform to the newly created miter box models.

3. **`makeBooleanOperationsToFibulaSurgicalGuideBase()`** — At the end, apply the normalization transform to the surgical guide prototype model.

4. **`createCylindersFromFiducialListAndNeomandiblePiecesButton`** (dental implants) — At the end of `onUpdateFibulaDentalImplantsTimerTimeout`, apply the normalization transform to the dental implant cylinders.

For each of these, the simplest pattern is:
```python
transformVolumeChecked = parameterNode.GetParameter("transformVolume") == "True"
self.updateNormalizationFibulaLineTransform(transformVolumeChecked)
```

This re-applies the transform to all existing fibula-linked nodes, including the just-created ones.

#### Step 4: Handle hardened-transform interactions

Some methods (like `tranformFibulaPiecesToMandible`, `tranformMandiblePiecesToFibula`) use `SetAndObserveTransformNodeID` followed by `HardenTransform()`. The fibula normalization transform must be handled carefully here:

- The normalization transform is a **view-only** rotation, not part of the surgical planning geometry.
- The `Cut Bones` and `Transformed Mandible Pieces` node geometries are computed in the **original** (non-normalized) coordinate frame.
- The normalization transform should be applied **after** all geometry operations are complete, purely for display.

Since `updateNormalizationFibulaLineTransform` already leaves transforms live (non-hardened), and we call it at the end of `generateFibulaPlanesFibulaBonePiecesAndTransformThemToMandible`, this is handled naturally. The key rule is: **never harden the normalization transform**.

### Verification

- Toggle `transformVolume` ON → All fibula-view nodes (model, line, planes, cut bones, mandible pieces, miter boxes, etc.) should rotate together with the CT volume.
- Toggle `transformVolume` OFF → All nodes return to their original orientation (identity transform).
- Create new fibula planes after toggling ON → New planes should also be rotated.
- Create miter boxes after toggling ON → Miter boxes should also be rotated.

### Risk Assessment

- **Low risk**: The approach uses `SetAndObserveTransformNodeID` with a live (non-hardened) transform. This is the exact same mechanism already used for `currentScalarVolume`. Toggling off sets identity, which has no visual effect.
- **Potential concern**: If any downstream method reads node positions with `GetNthControlPointPositionWorld` while the normalization transform is active, it will get the transformed (rotated) positions. This is **intentional** for `fibulaLine` since `createFibulaAxisFromFibulaLineAndRightSideLegChecked` already reads world positions and the fibula axis should be consistent with the visual display. However, we should verify that no method hardcodes the assumption that fibula-view nodes are in the un-normalized frame.
  - `centerFibulaLine()` reads `fibulaLine` positions → it calls `updateNormalizationFibulaLineTransform()` at the end, which is fine.
  - `createFibulaAxisFromFibulaLineAndRightSideLegChecked()` reads `fibulaLine` world positions → The normalization transform rotates the line but since the axis computation uses the line's world coordinates, the resulting fibula axis is correct in world space.
  - `transformFibulaPlanes()` reads mandible plane matrices and transforms fibula planes → Fibula planes get their positions from mandible→fibula registration transforms, then get hardened. The normalization transform is applied separately on top for display.

## Files Changed

Only one file is modified:
- `BoneReconstructionPlanner/BoneReconstructionPlanner.py`
