# Tolerance and Slot Width
```
  It's easy to find out what good fit for the saw blade is by printing a few pockets with different widths. It depends on the printing technology. There is a summary at the end.

  The saw blade used on this example is 0.2mm. If I print using the SLA printer I make the pockets 0.3 mm. With the FDM printer the width needs to be 0.6 mm. And the default tolerance is 0.2mm

  These are the equations:

  Suggested sawBoxSlotWidths
  If SLA is used:
  sawBoxSlotWidth = sawBladeWidth + 0.1mm
  else if FDM is used:
  sawBoxSlotWidth = sawBladeWidth + 0.4mm

  realSawBoxWidth = sawBoxSlotWidth+2*clearanceFitPrintingTolerance

  So for this example we have:
  If SLA is used:
  realSawBoxWidth = sawBladeWidth + 0.1mm +2*clearanceFitPrintingTolerance = 0.2mm + 0.1mm + 2*0.2mm = 0.7mm
  else if FDM is used:
  realSawBoxWidth = sawBladeWidth + 0.4mm +2*clearanceFitPrintingTolerance = 0.2mm + 0.4mm + 2*0.2mm = 1.0mm

  From these we can find the realClearanceFitPrintingTolerance (that should be used with the realSawBoxWidth) as:
  If SLA is used:
  realClearanceFitPrintingTolerance = (realSawBoxWidth - sawBladeWidth)/2 = (0.7mm - 0.2mm)/2 = 0.25mm
  else if FDM is used:
  realClearanceFitPrintingTolerance = (realSawBoxWidth - sawBladeWidth)/2 = (1.0mm - 0.2mm)/2 = 0.4mm
```