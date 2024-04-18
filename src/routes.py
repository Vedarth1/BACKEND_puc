from flask import Blueprint
from src.controllers.auth_controller import users
from src.controllers.puc_validation_controller import puc_validation
from src.controllers.image_processing import image_processing

# main blueprint to be registered with application
api = Blueprint('api', __name__)

# register user with api blueprint
api.register_blueprint(users, url_prefix="/users")
api.register_blueprint(puc_validation,url_prefix="/puc")
api.register_blueprint(image_processing,url_prefix="/puc")