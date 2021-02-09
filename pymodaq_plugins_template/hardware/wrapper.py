class ActuatorWrapper:

	units = "mm"

	def __init__(self):

		self._com_port = ''
		self._current_value = 0
		self._target_value = None

	def open_communication(self):

		return true

	def move_at(self, value):

		self._target_value = value
		self._current_value = value