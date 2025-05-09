from flask import Blueprint

jobs = Blueprint('jobs', __name__)

from app.jobs import routes