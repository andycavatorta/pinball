import importlib
import settings
import socket
import time

time.sleep(5) # trying to avoid mysterious device error when first using sockets
role_module = importlib.import_module('roles.{}.{}'.format(settings.Roles.hosts[socket.gethostname()],'main'))

# 31 birds
