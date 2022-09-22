class Logger(object):
  """
  DESCRIPTION: Logger is a class that provides a simple interface for logging messages. It reuses the built-in system.util.getLogger function to create a logger that uses the built-in Ignition functionality.
  Logger also implements the custom_print method that allows for logs to also be printed into the Script Console and the Perspective Console if possible.
  At the end of each method, before executing custom_print it will check if the logger is enabled (i.e. logger.isDebugEnabled()) so that it works in concert with the builtin logging settings.
  
  EXAMPLE USAGE:
  logger = Logging.Logger("MyLogger")
  logger.info("Hello World!")
  """
  
	def __init__(self, logger_name):
		"""
		DESCRIPTION: instantiates object
		PARAMETERS: logger_name (REQ, string) - name of the logger
    """
		self.logger = system.util.getLogger(self._logger_name)

		
	def get_logging_method(self, level):
		logging_levels = {
			"info": (self.logger.info, self.logger.isInfoEnabled),
			"trace": (self.logger.trace, lambda: True),
			"debug": (self.logger.debug, self.logger.isDebugEnabled),
			"warn": (self.logger.warn, lambda: True),
			"error": (self.logger.error, lambda: True)
			}
		
		return logging_levels.get(level, "info")


	def get_name(self):
		"""
		DESCRIPTION: gets the name of the logger
		"""
		return self.logger.getName()
		
	def generic_log(self, logger_message, logging_level):
		"""
		DESCRIPTION: calls the method which makes the log, repeats using parent log if necessary.
		PARAMETERS: logger_message(REQ, string) The message to be logged
					logging_level (REQ, string) - the Ignition specific level the gateway will be logged to
		"""
		custom_message = "%s.%s: %s" % (self.get_name(), logging_level, logger_message)

    # NOTE: get needed method and information based on the logging level then log it using the detailed_log method
    logging_method, logger_enabled = self.get_logging_method(logging_level)
    self.detailed_log(logging_method, logger_message)
	
	def info(self, logger_message):
		"""
		DESCRIPTION: Logs to the gateway with the logging level set to INFO, valuable for general details that we would want to show up in any logs for historical troubleshooting.
		PARAMETERS: logger_message (REQ, string) - the message to be recorded in log
        """
		self.generic_log(logger_message, "info")

	def error(self, logger_message):
		"""
		DESCRIPTION: Logs to the gateway with the logging level set to ERROR, valuable for calling out errors that happened in the application, for historical and real time troubleshooting.
		PARAMETERS: logger_message (REQ, string) - the message to be recorded in log
        """
		self.generic_log(logger_message, "error")

	def trace(self, logger_message):
		"""
		DESCRIPTION: Logs to the gateway with the logging level set to TRACE, valuable for finer level details that normally are not logged.
		PARAMETERS: logger_message (REQ, string) - the message to be recorded in log
		"""
		self.generic_log(logger_message, "trace")

	def debug(self, logger_message):
		"""
		DESCRIPTION: Logs to the gateway with the logging level set to DEBUG, valuable for adding troubleshooting information into the logs, that shouldn't always be present.
		PARAMETERS: logger_message (REQ, string) - the message to be recorded in log
        """
		self.generic_log(logger_message, "debug")
		
	def warn(self, logger_message):
		"""
		DESCRIPTION: Logs to the gateway with the logging level set to WARN, valuable for displaying warnings to a user in the logs that should likely be resolved.
		PARAMETERS: logger_message (REQ, string) - the message to be recorded in log
					logger_details (OPT, object) - the object to be converted to a throwable for printing in the logs
        """
		custom_message = "%s.warn: %s" % (self._logger_name, logger_message)

    self.logger.warn(logger_message)

    # isWarnEnabled does not exist, so we will just print
    self.custom_print(custom_message)


	def custom_print(self, custom_message):
		"""
		DESCRIPTION: Allows for printing to console in the python, client, and perspective scopes. Catch all for above functions.
		PARAMETERS: custom_message (REQ, string) - the message to be recorded in the console
    """

    try:
      system.perspective.print(custom_message)
    except:
      print(custom_message)
