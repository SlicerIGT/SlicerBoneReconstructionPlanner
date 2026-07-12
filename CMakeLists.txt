cmake_minimum_required(VERSION 3.13.4)

project(BoneReconstructionPlanner)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner#bone-reconstruction-planner")
set(EXTENSION_CATEGORY "Planning")
set(EXTENSION_CONTRIBUTORS "MSc. Mauro I. Dominguez, PhD. Andras Lasso (PerkLab), Dr. Manjula Herath")
set(EXTENSION_DESCRIPTION "A extension for virtual surgical planning of mandibular reconstruction with vascularized fibula free flap and generation of patient-specific surgical guides.<br><img src=\"https://img.shields.io/badge/dynamic/json?label=Citations%20to%20date:&query=%24.citationCount&url=https%3A%2F%2Fapi.semanticscholar.org%2Fgraph%2Fv1%2Fpaper%2FDOI%3A10.1016%2Fj.stlm.2023.100109%3Ffields%3DcitationCount\" alt=\"Citations to date count\">")
set(EXTENSION_ICONURL "https://raw.githubusercontent.com/SlicerIGT/SlicerBoneReconstructionPlanner/main/BoneReconstructionPlanner.jpg")
set(EXTENSION_SCREENSHOTURLS "https://raw.githubusercontent.com/SlicerIGT/SlicerBoneReconstructionPlanner/main/BoneReconstructionPlanner/Resources/Pictures/screenshotPlanning.png https://raw.githubusercontent.com/SlicerIGT/SlicerBoneReconstructionPlanner/main/BoneReconstructionPlanner/Resources/Pictures/screenshotPatientSpecificSurgicalGuides.png")
set(EXTENSION_DEPENDS "SurfaceWrapSolidify MarkupsToModel Sandbox SlicerTelemetry") # Specified as a list or "NA" if no dependencies
set(EXTENSION_SCM "git")
set(EXTENSION_SCMURL "https://github.com/SlicerIGT/SlicerBoneReconstructionPlanner.git")
set(EXTENSION_SCMREVISION "main")
set(EXTENSION_ENABLED "1")
set(EXTENSION_STATUS "Beta")

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

find_package(SurfaceWrapSolidify REQUIRED)
find_package(MarkupsToModel REQUIRED)
find_package(Sandbox REQUIRED)

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(BoneReconstructionPlanner)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
