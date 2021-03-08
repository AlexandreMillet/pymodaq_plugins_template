from pymodaq.daq_move.utility_classes import DAQ_Move_base
from pymodaq.daq_move.utility_classes import comon_parameters

from pymodaq.daq_utils.daq_utils import ThreadCommand, getLineInfo
from easydict import EasyDict as edict
import sys
import clr


class DAQ_Move_Newport(DAQ_Move_base):
    """
        Wrapper object to access the conex fonctionnalities, similar wrapper for all controllers.

        =============== ==================
        **Attributes**   **Type**
        *ports*          list
        *conex_path*     string
        *params*         dictionnary list
        =============== ==================

        See Also
        --------
        daq_utils.ThreadCommand
    """

    _controller_units = 'µm'

    # find available COM ports
    # import serial.tools.list_ports
    # ports = [str(port)[0:4] for port in list(serial.tools.list_ports.comports())]
    # if ports==[]:
    #    ports.append('')
    ports = [] #Pas sur
    conex_path = 'C:\\Program Files\\New Focus\\New Focus Picomotor Application\\Samples'
    is_multiaxes = True
    stage_names = ['U', 'V']

    params = [{'title': 'controller library:', 'name': 'conex_lib', 'type': 'browsepath', 'value': conex_path},
              {'title': 'Controller Name:', 'name': 'controller_name', 'type': 'str', 'value': '', 'readonly': True},
              {'title': 'Motor ID:', 'name': 'motor_id', 'type': 'str', 'value': '', 'readonly': True},
              {'title': 'COM Port:', 'name': 'com_port', 'type': 'list', 'values': ports},
              {'title': 'Controller address:', 'name': 'controller_address', 'type': 'int', 'value': 1, 'default': 1,
               'min': 1},
              {'title': 'MultiAxes:', 'name': 'multiaxes', 'type': 'group', 'visible': is_multiaxes, 'children': [
                  {'title': 'is Multiaxes:', 'name': 'ismultiaxes', 'type': 'bool', 'value': is_multiaxes,
                   'default': False},
                  {'title': 'Status:', 'name': 'multi_status', 'type': 'list', 'value': 'Master',
                   'values': ['Master', 'Slave']},
                  {'title': 'Axis:', 'name': 'axis', 'type': 'list', 'values': stage_names},

              ]}] + comon_parameters

    def __init__(self, parent=None, params_state=None):
        super().__init__(parent, params_state)
        self.settings.child(('epsilon')).setValue(0.0001)

        # to be adjusted on the different computers
        try:
            sys.path.append(self.settings.child(('CmdLib8742')).value())
            clr.AddReference("CmdLib8742")
            import Newport.CmdLib8742 as CmdLib
            self.controller = CmdLib.Open()
            print("ok")
            # self.settings.child('bounds', 'is_bounds').setValue(True)
            # self.settings.child('bounds', 'min_bound').setValue(-0.02)
            # self.settings.child('bounds', 'max_bound').setValue(0.02)

        except Exception as e:
            self.emit_status(ThreadCommand("Update_Status", [getLineInfo() + str(e)]))
            raise Exception(getLineInfo() + str(e))
