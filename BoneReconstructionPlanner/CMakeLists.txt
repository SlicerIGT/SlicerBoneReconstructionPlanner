#-----------------------------------------------------------------------------
set(MODULE_NAME BoneReconstructionPlanner)

#-----------------------------------------------------------------------------
set(MODULE_PYTHON_SCRIPTS
  ${MODULE_NAME}.py
  BRPLib/guiWidgets.py
  BRPLib/helperFunctions.py
  BRPLib/MOOSEHelper.py
  BRPLib/DentalSegmentatorHelper.py
  BRPLib/VSPAnimation.py
  )

set(MODULE_PYTHON_RESOURCES
  Resources/defaultParameters.json
  Resources/Fonts/OpenSans-Bold.ttf
  Resources/Fonts/OpenSans-Bold_LICENSE.txt
  Resources/UI/${MODULE_NAME}.ui
  Resources/Icons/${MODULE_NAME}.png
  Resources/Icons/add_48.svg
  Resources/Icons/axes.svg
  Resources/Icons/bone_48.svg
  Resources/Icons/construction_48.svg
  Resources/Icons/experiment_48.svg
  Resources/Icons/fibula_normalization_transform.png
  Resources/Icons/iconCTFibula.png
  Resources/Icons/iconCTFibulaCropped.png
  Resources/Icons/iconCTMandible.png
  Resources/Icons/iconFibulaSegmentation.png
  Resources/Icons/iconMandibleSegmentation.png
  Resources/Icons/iconTestPlanBRP.png
  Resources/Icons/linked_camera_48.svg
  Resources/Icons/lock_48.svg
  Resources/Icons/mail_48.svg
  Resources/Icons/MarkupsDelete.png
  Resources/Icons/MarkupsPlaneMouseModePlaceAdd.png
  Resources/Icons/quick_reference_48.svg
  Resources/Icons/recycle_48.svg
  Resources/Icons/remove_48.svg
  Resources/Icons/target_48.svg
  Resources/Icons/update_48.svg
  Resources/Icons/visibility_48.svg
  )

#-----------------------------------------------------------------------------
slicerMacroBuildScriptedModule(
  NAME ${MODULE_NAME}
  SCRIPTS ${MODULE_PYTHON_SCRIPTS}
  RESOURCES ${MODULE_PYTHON_RESOURCES}
  WITH_GENERIC_TESTS
  )

#-----------------------------------------------------------------------------
if(BUILD_TESTING)

  # Modules of the extensions we depend on are not loaded by default during testing,
  # but the test scene needs them (e.g. MarkupsToModel nodes)
  set(_dependency_module_paths)
  foreach(_dependency SurfaceWrapSolidify MarkupsToModel Sandbox Telemetry)
    foreach(_modules_dir ${Slicer_QTLOADABLEMODULES_LIB_DIR} ${Slicer_QTSCRIPTEDMODULES_LIB_DIR})
      if(EXISTS ${${_dependency}_DIR}/${_modules_dir})
        list(APPEND _dependency_module_paths ${${_dependency}_DIR}/${_modules_dir})
      endif()
    endforeach()
  endforeach()

  # Register the unittest subclass in the main script as a ctest.
  # Note that the test will also be available at runtime.
  slicer_add_python_unittest(SCRIPT ${MODULE_NAME}.py
    SLICER_ARGS --additional-module-paths ${_dependency_module_paths}
    )

  # Additional build-time testing
  add_subdirectory(Testing)
endif()
