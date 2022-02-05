"""
Dynamic Status Widget.

Builts a grid of HAL status LEDs with associated label.
LEDs are linked dynamically to the correct signals.
-------------
"""
import sys, re
from subprocess import run as RUN

from qtpy.QtWidgets import QLabel, QWidget
from qtpy.QtCore import Property, Slot

from qtpyvcp.widgets import VCPWidget
from qtpyvcp.widgets.hal_widgets.hal_led import HalLedIndicator
from qtpyvcp.utilities.logger import getLogger

LOG = getLogger(__name__)

class HWStatusLeds(VCPWidget, QWidget):
    def __init__(self, parent=None):
        super(HWStatusLeds, self).__init__(parent)
        self.hal_data = {}
        self.card_types = []
        
        # build up the HAL environment info
        self.build_hal_data()

    def build_hal_data(self):
        #cmd_list = ['halcmd', 'show', 'pin', '-t', 'bit']
        cmd_list = ['cat', '/home/james/dev/pins.txt']
        cmd_result = RUN(cmd_list, capture_output=True)
        hal_lines = cmd_result.stdout.splitlines()
        #print(hal_lines)
        hw_lines = []
        cards = []
        for l in hal_lines:
            # split into fields
            line_fields = l.split()
            if len(line_fields) > 5:
                #built up key fields and test if should be added to master list
                type = line_fields[1].decode('UTF-8')
                direction = line_fields[2].decode('UTF-8')
                pin  = line_fields[4].decode('UTF-8')
                annotation = line_fields[5].decode('UTF-8')
                signal = line_fields[6].decode('UTF-8')
                #import pydevd;pydevd.settrace()
                #LOG.debug(f'type = {type}, direction = {direction}')
                is_hw_pin = re.search(r"hm2_|paraport", pin)
                if  type.lower() == 'bit' and \
                    direction.lower() != 'i/o' and \
                    is_hw_pin != None:
                    hw_lines.append({'type':type, 'direction':direction, 'pin':pin, 'annotation':annotation, 'signal':signal})
                    LOG.debug(f"{type} {direction} {pin} {annotation} {signal}")
                    # split the pin into its parts
                    pin_parts = pin.split('.')
                    LOG.debug(f"Pin parts:  {pin_parts}")
                    


        # now parse through the hw pins and segment into card types
        

    def initialize(self):
        pass
    

if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication

    app = QApplication(sys.argv)
    w = HWStatusLeds()
    w.show()
    sys.exit(app.exec_())
