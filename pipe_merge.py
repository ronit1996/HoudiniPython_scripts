import sys
from PySide2.QtWidgets import QApplication, QMainWindow
from PySide2 import QtWidgets, QtCore
import hou

class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # create the app window and set size and name #
        self.setGeometry(200,200,300,100)
        self.setWindowTitle("Pipe Merge")

        # create the label #
        self.label = QtWidgets.QLabel(self)
        self.label.setText("Node Name")
        
        # create the input field #
        self.entry = QtWidgets.QLineEdit(self)
        
        # layout both label and entry field #
        h_layout = QtWidgets.QHBoxLayout()
        h_layout.addWidget(self.label)
        h_layout.addWidget(self.entry)
        
        # create the button #
        self.button = QtWidgets.QPushButton(self, clicked = lambda: self.create_node())
        self.button.setText("Create Nodes")
        # close the existing window once the button is clicked #
        self.button.clicked.connect(self.close)
        self.button.setFocusPolicy(QtCore.Qt.NoFocus)

        # vertical layout #
        v_layout = QtWidgets.QVBoxLayout()
        v_layout.addLayout(h_layout)
        v_layout.addWidget(self.button)

        widget = QtWidgets.QWidget()
        widget.setLayout(v_layout)
        self.setCentralWidget(widget)
    
    # function to create nodes inside houdini, this will be called by the button #
    def create_node(self):
        selected_node = kwargs["node"]
        path = selected_node.path()
        l = path.split("/")
        l.pop(-1)
        parent_path = "/".join(l)
        node = hou.node(parent_path)

        # create the null node #
        null = node.createNode("null", "PIPE_{}".format(self.entry.text()))
        null.setInput(0, selected_node)
        null.moveToGoodPosition()
        null.setColor(hou.Color((0.95,0.55,0.66)))

        # create the obj merge node #
        obj_merge = node.createNode("object_merge", "MERGE_{}".format(self.entry.text()))
        obj_merge.moveToGoodPosition()
        obj_merge.parm("objpath1").set(null.path())
        obj_merge.setColor(hou.Color((0.65,0.89,0.63)))

window = MyApp()
window.show()
