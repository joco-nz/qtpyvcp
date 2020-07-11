"""
"""

from qtpyvcp.utilities.logger import getLogger
from qtpyvcp.plugins import DataPlugin

from qtpyvcp import hal
from qtpyvcp.actions.machine_actions import feed_override, rapid_override
from qtpyvcp.actions.spindle_actions import override as spindle_override


LOG = getLogger(__name__)
STATUS = getPlugin('status')

class EventActions(DataPlugin):
    def __init__(self, *args, **kwargs):
        super(EventActions, self).__init__()

    def initialise(self):
        LOG.debug('Initalizing Event Actions PlugIn')
        print "Initalizing Event Actions PlugIn"

    def terminate(self):
        pass
