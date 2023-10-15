"""
My Service

Describe what your service does here
"""

from flask import jsonify, request, url_for, abort
from service.common import status  # HTTP Status Codes
from service.models import Product, Wishlist

# Import Flask application
from . import app


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        "Reminder: return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )


######################################################################
# CREATE A wishlist
######################################################################
@app.route('/wishlist/create', methods=['POST'])
def create_wishlist():
    """create an empty wishlist with post method"""
    new_list = Wishlist()
    new_list.deserialize(request.get_json())
    new_list.create()
    message = new_list.serialize()

    return jsonify(message), status.HTTP_201_CREATED

######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

# Place your REST API code here ...
