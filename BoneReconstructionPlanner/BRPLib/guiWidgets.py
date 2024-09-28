from __main__ import ctk, qt

class checkablePushButtonWithIcon(ctk.ctkCheckablePushButton):
    def __init__(self, text="", icon=qt.QIcon(), parent=None):
        super().__init__(parent)
        self.text = text
        #
        self._mainLayout = qt.QHBoxLayout(self)
        self._mainLayout.setContentsMargins(0, 0, 0, 0)
        #self._mainLayout.setSpacing(15)
        #self._mainLayout.setSpacing(300)
        #
        self.icon = icon
        self._iconSize = qt.QSize(36, 36)
        pixmap = self.icon.pixmap(self._iconSize)
        self._iconLabel = qt.QLabel()
        self._iconLabel.setAlignment(qt.Qt.AlignCenter)
        self._iconLabel.setPixmap(pixmap)
        self._iconLabel.setFixedSize(self._iconSize)
        self._mainLayout.addSpacing(self.sizeHint.width())
        self._mainLayout.addWidget(self._iconLabel)
        self.setMinimumWidth(self.sizeHint.width() + self._iconSize.width())
        self.setSizePolicy(qt.QSizePolicy.Maximum, qt.QSizePolicy.Fixed)

# use it with ctk.ctkCheckBox.indicatorIcon = iconWithGreyOut(iconPath)
def iconWithGreyOut(iconPath, size = qt.QSize(24, 24)):
    iconPixmap = qt.QPixmap(iconPath)
    iconWithGreyOut = qt.QIcon()
    iconWithGreyOut.addPixmap(iconPixmap, qt.QIcon.Normal, qt.QIcon.On)
    grayed = iconWithGreyOut.pixmap(size, qt.QIcon.Disabled, qt.QIcon.On)
    iconWithGreyOut.addPixmap(grayed, qt.QIcon.Normal, qt.QIcon.Off)
    return iconWithGreyOut