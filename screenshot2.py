#!/usr/bin/env python
# -*- coding: utf-8 -*-


from PyQt4 import QtCore, QtGui


class RubberBand(QtGui.QRubberBand):

    def __init__(self):
        super(RubberBand, self).__init__(QtGui.QRubberBand.Rectangle, None)
        self.setPalette(QtGui.QPalette(QtCore.Qt.transparent))
        self.pen = QtGui.QPen(QtCore.Qt.blue, 4)
        self.pen.setStyle(QtCore.Qt.SolidLine)
        self.painter = QtGui.QPainter()

    def paintEvent(self, event):

        self.painter.begin(self)
        self.painter.setPen(self.pen)
        self.painter.drawRect(event.rect())
        self.painter.end()


class ScreenShotWindow(QtGui.QWidget):

    def __init__(self, parent=None):
        super(ScreenShotWindow, self).__init__()

        self.setMouseTracking(True)
        self.setWindowFlags(self.windowFlags(
        ) | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.showFullScreen()
        self.setWindowOpacity(0.5)
        self.rubberband = RubberBand()
        self.setCursor(QtCore.Qt.CrossCursor)

    def closeEvent(self, *args):
        if self.parentWidget() and self.parent.isHidden():
            self.parentWidget().show()

    def mousePressEvent(self, event):
        self.origin = event.pos()
        self.rubberband.setGeometry(QtCore.QRect(self.origin, QtCore.QSize()))
        self.rubberband.show()
        QtGui.QWidget.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        if self.rubberband.isVisible():

            # self.rubberband.painter.drawText(self.rubberband.rect().x(),
            # self.rubberband.rect().y(), 'Help Me')
            size = self.rubberband.size()
            QtGui.QToolTip.showText(
                event.globalPos(),
                QtCore.QString('%1, %2 (Press Esc to Cancel)').arg(
                    size.width()).arg(size.height()),
                self)

            self.rubberband.setGeometry(QtCore.QRect(
                self.origin, event.pos()).normalized())
            left = QtGui.QRegion(QtCore.QRect(
                0, 0, self.rubberband.x(), self.height()))
            right = QtGui.QRegion(QtCore.QRect(
                self.rubberband.x() + self.rubberband.width(), 0, self.width(),
                self.height()))
            top = QtGui.QRegion(0, 0, self.width(), self.rubberband.y())
            bottom = QtGui.QRegion(0, self.rubberband.y(
            ) + self.rubberband.height(), self.width(), self.height())
            self.setMask(left + right + top + bottom)

    def mouseReleaseEvent(self, event):
        if self.rubberband.isVisible():
            self.rubberband.hide()
            rect = self.rubberband.geometry()
            if rect.width() and rect.height():
                p = QtGui.QPixmap.grabWindow(
                    QtGui.QApplication.desktop().winId(),
                    rect.x() + 4,
                    rect.y() + 4,
                    rect.width() - 8,
                    rect.height() - 8)
                p.save('/home/mahendra/workspace/falcon/test.jpg', 'jpg')
            self.close()

    def saveSnapShot(self):
        if self.rubberband.isHidden():
            return

        rect = self.rubberband.geometry()
        if rect.width() and rect.height():
            p = QtGui.QPixmap.grabWindow(
                QtGui.QApplication.desktop().winId(),
                rect.x() + 4,
                rect.y() + 4,
                rect.width() - 8,
                rect.height() - 8)
            p.save('/home/mahendra/workspace/falcon/test.jpg', 'jpg')

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.rubberband.setHidden(True)
            self.close()
        elif event.key() == QtCore.Qt.Key_Return:
            self.saveSnapShot()
            self.rubberband.setHidden(True)
            self.close()
        else:
            super(ScreenShotWindow, self).keyPressEvent(event)


if __name__ == '__main__':
    app = QtGui.QApplication([])
    ui = ScreenShotWindow()
    ui.show()
    app.exec_()
