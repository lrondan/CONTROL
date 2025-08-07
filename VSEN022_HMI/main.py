import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer    
import serial
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

class InterfazHMI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("HMI_V002.ui", self)

        # Fondo en frame_2
        self.frame_2.setStyleSheet(
            "QFrame { background-image: url('hmi.png'); background-repeat: no-repeat; background-position: center; }"
        )

        self.frame_3.setStyleSheet(
            "QFrame { background-image: url('hmi.png'); background-repeat: no-repeat; background-position: center; }"
        )

        self.frame_4.setStyleSheet(
            "QFrame { background-image: url('hmi.png'); background-repeat: no-repeat; background-position: center; }"
        )

app = QtWidgets.QApplication(sys.argv)
ventana = InterfazHMI()
ventana.show()
sys.exit(app.exec_())