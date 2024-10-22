from qtpy.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, 
                            QSpinBox, QHBoxLayout, QPushButton, 
                            QFileDialog, QComboBox, QLabel, 
                            QSlider, QSpinBox, QFrame, QLineEdit)

from qtpy.QtCore import QThread, Qt

from PyQt5.QtGui import QFont, QDoubleValidator
from PyQt5.QtCore import pyqtSignal

import napari
from napari.utils.notifications import show_info
from napari.utils import progress

import open3d as o3d
import trimesh as tm
import numpy as np
import os

from astrocytes import AstrocytesContactState

class ProtoSwellingWidget(QWidget):

    traps_detected = pyqtSignal()
    traps_filtered = pyqtSignal()
    export_done    = pyqtSignal()
    labels_ready   = pyqtSignal()
    measures_ready = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.viewer        = napari.current_viewer()
        self.model         = AstrocytesContactState()
        self.mesh_path     = None

        self.layout = QVBoxLayout()
        self.init_ui()
        self.setLayout(self.layout)

    ####  >>  UI  <<  ####

    def init_ui(self):
        self.font = QFont()
        self.font.setFamily("Arial Unicode MS, Segoe UI Emoji, Apple Color Emoji, Noto Color Emoji")
        self.choose_file_ui()
        self.mesh_tools_ui()
    
    def choose_file_ui(self):
        pass

    def mesh_tools_ui(self):
        pass

    ####  >>  CALLBACKS  <<  ####

    def select_folder(self):
        pass

    def file_changed(self):
        pass

    def run_connected_components(self):
        """
        Creates a new shape layer for each connected component in the current labels layer.
        
        Settings:
            - Checkbox to remove the original the original layer.
        """
        pass

    def run_merge_by_distance(self):
        """
        In the current layer, merges the vertices together when they are closer than the distance specified.

        Settings:
            - Input box for the distance.
        """
        pass

    ####  >>  METHODS  <<  ####

    def load_mesh(self):
        pass
