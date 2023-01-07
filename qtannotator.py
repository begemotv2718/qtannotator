#!/usr/bin/python3
# Written with great assistance of chatGPT

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QRadioButton, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QColorDialog, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsTextItem, QGraphicsLineItem, QGraphicsPolygonItem, QGraphicsItemGroup, QFileDialog, QInputDialog
from PyQt5.QtGui import QPixmap, QImage, QColor, QBrush, QPen, QFont, QPainter, QVector2D, QPolygonF, QTransform
from PyQt5.QtCore import Qt, QRectF, QLineF, QPointF

class MainWindow(QMainWindow):
    def __init__(self, file_name, clipboard):
        super().__init__()
        self.clipboard = clipboard

        # Load the image
        self.image = QLabel()
        pixmap = QPixmap(file_name)
        self.image.setPixmap(pixmap)

        # Set up the graphics view and scene
        self.view = QGraphicsView()
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setRenderHint(QPainter.SmoothPixmapTransform)
        self.view.setDragMode(QGraphicsView.RubberBandDrag)
        self.view.setOptimizationFlag(QGraphicsView.DontAdjustForAntialiasing, True)
        self.view.setOptimizationFlag(QGraphicsView.DontSavePainterState, True)
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        pixmap_rect = pixmap.rect()
        self.scene.setSceneRect(pixmap_rect.x(),pixmap_rect.y(),pixmap_rect.width(),pixmap_rect.height())
        self.scene.addItem(QGraphicsPixmapItem(pixmap))
        self.view.fitInView(self.scene.sceneRect(),Qt.KeepAspectRatio)

        # Set up the radio buttons
        self.ellipse_button = QRadioButton("Ellipse")
        self.arrow_button = QRadioButton("Arrow")
        self.guideline_button = QRadioButton("Guideline")
        self.rectangle_button = QRadioButton("Rectangle")
        self.text_button = QRadioButton("Text")
        self.ellipse_button.setChecked(True)

        # Set up the color button
        self.color_button = QPushButton("Select Color")
        self.color_button.clicked.connect(self.select_color)
        self.selected_color = QColor(Qt.red)

        # Set up the save button
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_image)

        # Set up the layout
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.ellipse_button)
        h_layout.addWidget(self.arrow_button)
        h_layout.addWidget(self.guideline_button)
        h_layout.addWidget(self.rectangle_button)
        h_layout.addWidget(self.text_button)
        h_layout.addStretch()
        h_layout.addWidget(self.color_button)
        h_layout.addWidget(self.save_button)
        v_layout = QVBoxLayout()
        v_layout.addWidget(self.view)
        v_layout.addLayout(h_layout)
        central_widget = QWidget()
        central_widget.setLayout(v_layout)
        self.setCentralWidget(central_widget)

        # Set up the variables to keep track of the state
        self.current_tool = "ellipse"
        self.items = []
        self.undo_stack = []

        # Set up the signal/slot connections
        self.ellipse_button.toggled.connect(self.set_current_tool)
        self.arrow_button.toggled.connect(self.set_current_tool)
        self.guideline_button.toggled.connect(self.set_current_tool)
        self.rectangle_button.toggled.connect(self.set_current_tool)
        self.text_button.toggled.connect(self.set_current_tool)
        self.view.mousePressEvent = self.mouse_press_event
        self.view.mouseReleaseEvent = self.mouse_release_event
        self.view.mouseMoveEvent = self.mouse_move_event
        self.view.keyPressEvent = self.key_press_event
        self.mouse_key_down = False
        self.current_item = None

    def set_current_tool(self):
        if self.ellipse_button.isChecked():
            self.current_tool = "ellipse"
        elif self.arrow_button.isChecked():
            self.current_tool = "arrow"
        elif self.guideline_button.isChecked():
            self.current_tool = "guideline"
        elif self.rectangle_button.isChecked():
            self.current_tool = "rectangle"
        elif self.text_button.isChecked():
            self.current_tool = "text"

    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.selected_color = color

    def mouse_press_event(self, event):
        self.start_pos = self.view.mapToScene(event.pos())
        if self.current_tool == "text":
            text, ok = QInputDialog.getText(self, "Enter Text", "Text:")
            if ok:
                font = QFont()
                font.setPixelSize(30)
                text_item = QGraphicsTextItem(text)
                text_item.setFont(font)
                text_item.setDefaultTextColor(self.selected_color)
                text_item.setPos(self.start_pos.x(),self.start_pos.y())
                self.scene.addItem(text_item)
                self.items.append(text_item)
        else:
            self.mouse_key_down = True
            self.current_item = None
    
    def mouse_move_event(self,event):
        if(self.mouse_key_down):
            end_pos = self.view.mapToScene(event.pos())
            if(self.current_item is not None):
                self.scene.removeItem(self.current_item)
            if self.current_tool == "ellipse":
                ellipse_item = QGraphicsEllipseItem(QRectF(self.start_pos, end_pos))
                ellipse_item.setPen(QPen(self.selected_color,3))
                ellipse_item.setBrush(QBrush(Qt.transparent))
                self.current_item = ellipse_item
            elif self.current_tool == "arrow":
                line_item = QGraphicsLineItem(QLineF(self.start_pos, end_pos))
                line_item.setPen(QPen(self.selected_color, 3))
                line_arrow_vector = QVector2D(end_pos-self.start_pos)
                line_arrow_vector.normalize()
                line_arrow_vector *= 20
                line_arrow_point = line_arrow_vector.toPoint()
                arrow_head_vec1= QTransform().rotate(15).map(line_arrow_point)
                arrow_head_vec2= QTransform().rotate(-15).map(line_arrow_point)
                arrow_head_item = QGraphicsPolygonItem(QPolygonF([end_pos,end_pos-arrow_head_vec1,end_pos-arrow_head_vec2])) 
                arrow_head_item.setPen(QPen(self.selected_color, 3))
                arrow_item = QGraphicsItemGroup()
                arrow_item.addToGroup(arrow_head_item)
                arrow_item.addToGroup(line_item)
                self.current_item = arrow_item
            elif self.current_tool == "guideline":
                diff = end_pos - self.start_pos
                line_end_pos = None
                if(abs(diff.x())>abs(diff.y())):
                    line_end_pos= QPointF(end_pos.x(),self.start_pos.y())
                else:
                    line_end_pos= QPointF(self.start_pos.x(),end_pos.y())
                line_item = QGraphicsLineItem(QLineF(line_end_pos,self.start_pos))
                line_item.setPen(QPen(self.selected_color, 2, Qt.DashLine))
                self.current_item = line_item
            elif self.current_tool == "rectangle":
                rect_item = QGraphicsRectItem(QRectF(self.start_pos, end_pos))
                rect_item.setPen(QPen(self.selected_color))
                rect_item.setBrush(Qt.transparent)
                self.current_item = rect_item
            self.scene.addItem(self.current_item)


    def mouse_release_event(self, event):
        self.mouse_key_down = False
        if(self.current_item):
            self.items.append(self.current_item)
        self.current_item = None

    def key_press_event(self,event):
        if event.key() == Qt.Key_Z and event.modifiers() == Qt.ControlModifier:
            if(self.items):
                item = self.items.pop()
                self.scene.removeItem(item)
        elif event.key() == Qt.Key_S and event.modifiers() == Qt.ControlModifier:
            self.save_image()
        elif event.key() == Qt.Key_C and event.modifiers() == Qt.ControlModifier:
            self.save_image_to_clipboard()
    def make_image_for_export(self):
            # Create a new image with the same size as the original image
            image = QImage(self.image.pixmap().size(), QImage.Format_RGB32)
            # Set the background color to white
            image.fill(Qt.white)
            painter = QPainter(image)
            # Draw all the items onto the new image
            self.scene.render(painter)
            # Need to clean up painter, otherwise destroying painter before destroying image causes segfault
            painter.end()
            return(image)

    def save_image(self):
        #options = {}
        file_name,ok=QFileDialog.getSaveFileName(self, "Save Image", "", "Images (*.png *.xpm *.jpg .bmp);;All Files ()") #, options=options)
        if ok and file_name:
            image=self.make_image_for_export()
            image.save(file_name)
    def save_image_to_clipboard(self):
        image = self.make_image_for_export()
        self.clipboard.setImage(image)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(sys.argv[1],QApplication.clipboard())
    window.show()
    sys.exit(app.exec_())

