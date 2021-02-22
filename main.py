import importlib
import settings
import socket

role_module = importlib.import_module('roles.{}.{}'.format(settings.Roles.hosts[socket.gethostname()],'main'))
