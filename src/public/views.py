"""
Logic for dashboard related routes
"""
from flask import Blueprint, render_template
from flask_login import current_user
blueprint = Blueprint('public', __name__)

@blueprint.route('/', methods=['GET'])
def index():
    if not current_user:
        user=[]
    else:
        user=current_user
    return render_template('public/index.tmpl',user=user)



