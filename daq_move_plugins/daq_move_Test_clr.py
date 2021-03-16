from pymodaq.daq_move.utility_classes import DAQ_Move_base  # base class
from pymodaq.daq_move.utility_classes import comon_parameters  # common set of parameters for all actuators
from pymodaq.daq_utils.daq_utils import ThreadCommand, getLineInfo  # object used to send info back to the main thread
from easydict import EasyDict as edict  # type of dict
import sys
import clr

class DAQ_Move_Test_clr(DAQ_Move_base):
    """
        Wrapper object to access the Mock fonctionnalities, similar wrapper for all controllers.

        =============== ==============
        **Attributes**    **Type**
        *params*          dictionnary
        =============== ==============
    """
    _controller_units = 'µm'
    # find available COM ports
    import serial.tools.list_ports
    ports = [str(port)[0:4] for port in list(serial.tools.list_ports.comports())]
    # if ports==[]:
    #    ports.append('')
    conex_path = 'C:\\Program Files\\New Focus\\New Focus Picomotor Application\\Samples'
    is_multiaxes = True  # set to True if this plugin is controlled for a multiaxis controller (with a unique communication link)
    stage_names = ['x', 'y']  # "list of strings of the multiaxes

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
        """
            Initialize the the class

            ============== ================================================ ==========================================================================================
            **Parameters**  **Type**                                         **Description**

            *parent*        Caller object of this plugin                    see DAQ_Move_main.DAQ_Move_stage
            *params_state*  list of dicts                                   saved state of the plugins parameters list
            ============== ================================================ ==========================================================================================

        """

        super().__init__(parent, params_state)
        self.settings.child(('epsilon')).setValue(0.0001)

        #to be adjusted on the different computers
        try:
            sys.path.append(self.settings.child(('conex_lib')).value())
            clr.AddReference("CmdLib")
            import Newport.CmdLib as CmdLib
            self.controller=CmdLib.CmdLib8742()
            self.settings.child('bounds','is_bounds').setValue(True)
            self.settings.child('bounds','min_bound').setValue(-0.02)
            self.settings.child('bounds','max_bound').setValue(0.02)

        except Exception as e:
            self.emit_status(ThreadCommand("Update_Status",[getLineInfo()+ str(e)]))
            raise Exception(getLineInfo()+ str(e))


    def check_position(self):
        """Get the current position from the hardware with scaling conversion.

        Returns
        -------
        float: The position obtained after scaling conversion.
        """
        ## TODO for your custom plugin
        pos = self.controller.get_value()
        ##

        pos = self.get_position_with_scaling(pos)
        self.emit_status(ThreadCommand('check_position',[pos]))
        return pos


    def close(self):
        """
        Terminate the communication protocol
        """
        ## TODO for your custom plugin
        self.controller.close_communication()
        ##

    def commit_settings(self, param):
        """
            | Activate any parameter changes on the PI_GCS2 hardware.
            |
            | Called after a param_tree_changed signal from DAQ_Move_main.

        """

        ### TODO for your custom plugin
        #if param.name() == "a_parameter_you've_added_in_self.params":
        #   self.controller.your_method_to_apply_this_param_change()
        #elif ...
        ###M


    def ini_stage(self, controller=None):
        """Actuator communication initialization

        Parameters
        ----------
        controller: (object) custom object of a PyMoDAQ plugin (Slave case). None if only one actuator by controller (Master case)

        Returns
        -------
        self.status (edict): with initialization status: three fields:
            * info (str)
            * controller (object) initialized controller
            *initialized: (bool): False if initialization failed otherwise True
        """


        try:
            # initialize the stage and its controller status
            # controller is an object that may be passed to other instances of DAQ_Move_Mock in case
            # of one controller controlling multiactuators (or detector)

            self.status.update(edict(info="", controller=None, initialized=False))

            # check whether this stage is controlled by a multiaxe controller (to be defined for each plugin)
            # if multiaxes then init the controller here if Master state otherwise use external controller
            if self.settings.child('multiaxes', 'ismultiaxes').value() and self.settings.child('multiaxes',
                                   'multi_status').value() == "Slave":
                if controller is None:
                    raise Exception('no controller has been defined externally while this axe is a slave one')
                else:
                    self.controller = controller
            else:  # Master stage

                ## TODO for your custom plugin
                self.controller = ActuatorWrapper()  
                self.controller.open_communication() # any object that will control the stages
                #####################################

            self.status.info = "Whatever info you want to log"
            self.status.controller = self.controller
            self.status.initialized = True
            return self.status

        except Exception as e:
            self.emit_status(ThreadCommand('Update_Status',[getLineInfo()+ str(e),'log']))
            self.status.info=getLineInfo()+ str(e)
            self.status.initialized=False
            return self.status


    def move_Abs(self, position):
        """ Move the actuator to the absolute target defined by position

        Parameters
        ----------
        position: (flaot) value of the absolute target positioning
        """

        position = self.check_bound(position)  #if user checked bounds, the defined bounds are applied here
        position = self.set_position_with_scaling(position)  # apply scaling if the user specified one

        ## TODO for your custom plugin
        self.controller.move_at(position)
        self.emit_status(ThreadCommand('Update_Status',['Some info you want to log']))
        ##############################



        self.target_position = position
        self.poll_moving()  #start a loop to poll the current actuator value and compare it with target position

    def move_Rel(self, position):
        """ Move the actuator to the relative target actuator value defined by position

        Parameters
        ----------
        position: (flaot) value of the relative target positioning
        """
        position = self.check_bound(self.current_position+position)-self.current_position
        self.target_position = position + self.current_position

        ## TODO for your custom plugin
        self.controller.move_at(self.target_position)
        self.emit_status(ThreadCommand('Update_Status',['Some info you want to log']))
        ##############################

        self.poll_moving()

    def move_Home(self):
        """
          Send the update status thread command.
            See Also
            --------
            daq_utils.ThreadCommand
        """

        ## TODO for your custom plugin
        self.controller.move_at(0)
        self.emit_status(ThreadCommand('Update_Status',['Some info you want to log']))
        ##############################


    def stop_motion(self):
      """
        Call the specific move_done function (depending on the hardware).

        See Also
        --------
        move_done
      """

      ## TODO for your custom plugin
      self.controller.stop()
      self.emit_status(ThreadCommand('Update_Status', ['Some info you want to log']))
      self.move_done() #to let the interface know the actuator stopped
      ##############################
