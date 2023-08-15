from flask import Blueprint

blueprint = Blueprint("routes", __name__)

# Import the route modules here
from . import index
