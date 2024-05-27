import sys
from PyQt5.QtWidgets import *
from Function import *

if __name__ == '__main__':
    app = QApplication([])
    mywin = MyWindow()
    mywin.show()
    sys.exit(app.exec_())