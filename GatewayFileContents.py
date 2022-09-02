import os
logger = system.util.getLogger("GatewayFileContents")

'''
This script leverages a gateway message handler, called "executeInGatewayScope". The purpose of this message handler takes any calls made in the client scope, and moves them over to the gateway. That way when files are read, they come off the gateway file system and not the local development environment.

That message handler should take the following arguments: 
	func (REQ, str) - The fully qualified path of a function in the designated project
	kwargs (OPT, dict) - A dictionary containing the key-value pairs that match up to the functions keyword arguments

The definition of the "executeInGatewayScope" function is as follows:

def handleMessage(payload):
	"""
	This message handler will be called each time a message of this
	type is received.

	Arguments:
		payload: A dictionary that holds the objects passed to this
			 message handler. Retrieve them with a subscript, e.g.
			 myObject = payload['argumentName']
	"""
	
	"""
	Example call in project scope: 
		system.util.sendRequest(project, "executeInGatewayScope", {"func":"myScript.myFunction", 'kwargs':{"myParam1":123,"myParam2":456}}), 
	"""
	
	if payload.get('func') is None:
		raise TypeError("executeInGatewayScope expects a payload object named func")
	
	func_reference = eval(payload['func'])
	kwargs = payload.get('kwargs', {})
	
	return func_reference(**kwargs)

'''



# NOTE: Because this is using gateway scoped files, we want to make sure that we are aware if this is executed in gateway scope or not
from com.inductiveautomation.ignition.common.model import ApplicationScope
scope = ApplicationScope.getGlobalScope()
is_gateway = ApplicationScope.isGateway(scope)

ignition_globals = system.util.getGlobals()

# NOTE: This key is the key inside the globals that gateway-files are stored in
GATEWAY_FILES_KEY="gateway-files"
ignition_globals.setdefault(GATEWAY_FILES_KEY, {})

class GatewayFileException(Exception):
	pass

def readJsonFile(file_path):
	try:
		return system.util.jsonDecode(system.file.readFileAsString(file_path))
	except:
		# NOTE: I do not use an exception here, because the java exception is not raised in a way that is caught by it
		raise GatewayFileException("Error loading %s, not a valid JSON dictionary" % file_path)

file_readers = {
	".json": readJsonFile
}

def getGatewayFileContents(file_path, force_refresh=False, store_in_globals=True):
	# NOTE: If we ar enot executing in the gateway scope, then file paths will be relative to the client which we dont want. Sending a request to the gateway will allow it to read gateway files 
	if not is_gateway:
		project = system.util.getProjectName()
		return system.util.sendRequest(project, "executeInGatewayScope", {"func":"myScript.myFunction", 'kwargs':{"file_path":file_path, 'force_refresh':force_refresh, 'store_in_globals':store_in_globals }})
	
	
	if not os.path.exists(file_path):
		raise GatewayFileException("Unable to find gateway file at" % (file_path))
	
	# NOTE: Extract the file type to make sure we can load it correctly
	file_type = os.path.splitext(file_path)[-1]
	
	# NOTE: If at some point we failed to load the file and its blank, lets force it to reload
	if not ignition_globals.get(GATEWAY_FILES_KEY, {}).get(file_path, {}).get('data'):
		force_refresh = True
	
	# NOTE: Check if the last modification time is newer than the last time we imported the file
	if os.path.getmtime(file_path) > ignition_globals.get(GATEWAY_FILES_KEY, {}).get(file_path, {}).get('lastModifiedTime', 0) or force_refresh:
		file_reader = file_readers.get(file_type)
		
		if not file_reader:
			raise GatewayFileException("Unable to load file of type: %s, no reader defined")
		
		file_contents = file_reader(file_path)
		
		# NOTE: If we dont want to store this file in the globals for some reason, then we should just return it
		if not store_in_globals:
			return file_contents
			
		# NOTE: Set the reference in the globals to the new data
		ignition_globals[GATEWAY_FILES_KEY][file_path] = {
								'data': file_contents, 
								'lastModifiedTime': os.path.getmtime(file_path)
								}
															
		logger.info("Updating Gateway File in Cache: %s" % file_path)
	
	# NOTE: Regardless of if we updated the data, return it anyway
	return ignition_globals[GATEWAY_FILES_KEY][file_path]['data']
