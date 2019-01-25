#   Copyright (c) 2018 Kurt Jacobson
#      <kurtcjacobson@gmail.com>
#
#   This file is part of QtPyVCP.
#
#   QtPyVCP is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 2 of the License, or
#   (at your option) any later version.
#
#   QtPyVCP is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with QtPyVCP.  If not, see <http://www.gnu.org/licenses/>.

import subprocess

from qtpy.QtWidgets import QPushButton, QVBoxLayout, QCheckBox

from qtpyvcp.widgets.dialogs.base_dialog import BaseDialog


from qtpyvcp.utilities.info import Info
from qtpyvcp.utilities import logger

Log = logger.getLogger(__name__)


class ProbeSim(BaseDialog):

    def __init__(self, parent=None):
        super(ProbeSim, self).__init__(parent=parent)

        self.info = Info()
        self.log = Log

        close_button = QPushButton("Touch")
        pulse_checkbox = QCheckBox()

        main_layout = QVBoxLayout()

        main_layout.addWidget(close_button)
        main_layout.addWidget(pulse_checkbox)

        self.setLayout(main_layout)
        self.setWindowTitle("Simulate touch probe")

        close_button.pressed.connect(self.touch_on)
        close_button.released.connect(self.touch_off)

    def touch_on(self):
        subprocess.Popen(['halcmd', 'setp', 'motion.probe-input', '1'])

    def touch_off(self):
        subprocess.Popen(['halcmd', 'setp', 'motion.probe-input', '0'])

    def close(self):
        self.hide()
