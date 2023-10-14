"""
My Service

Describe what your service does here
"""

from flask import jsonify, request, url_for, abort
from service.common import status  # HTTP Status Codes
from service.models import Wishlist

# Import Flask application
from . import app


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    return (
        "Reminder: return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )

######################################################################
# CREATE A wishlist
######################################################################
@app.route( '/wishlist/create', methods=['POST'] )
def createWishlist():
    newList = Wishlist()
    newList.deserialize(request.get_json())
    newList.create()
    message = newList.serialize()

    return jsonify(message), status.HTTP_201_CREATED

######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

# Place your REST API code here ...
