class ActuatorWrapper:

	units = "nm"

	def __init__(self):

		self._com_port = ''
		self._current_value = 0
		self._target_value = None

	def open_communication(self):

		print("open_communication")
		return True

	def move_at(self, value):

		self._target_value = value
		self._current_value = value
		print("move_at, value = {} {}".format(self._target_value, self.units))		

	def stop(self):

		print("stop")
		pass

	def get_value(self):

		print("get_value, value = {} {}".format(self._current_value, self.units))
		return self._current_value

	def close_communication(self):

		print("close_communication")
		pass
	
if __name__ == "__main__" :
	
	actuator = ActuatorWrapper()
	actuator.move_at(100)
	actuator.get_value()
	
