"""
My Service

Describe what your service does here
"""

from flask import jsonify, request, url_for, abort, make_response
from service.common import status  # HTTP Status Codes
from service.models import Product, Wishlist

# Import Flask application
from . import app

BASE_URL = "/wishlists"


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        jsonify(
            name="Wishlist Service",
            version="1.0",
            # later change to list_wishlist
            paths=url_for("create_wishlist", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
# CREATE A wishlist
######################################################################
@app.route(BASE_URL, methods=["POST"])
def create_wishlist():
    """create an empty wishlist with post method"""
    new_list = Wishlist()
    new_list.deserialize(request.get_json())
    new_list.create()
    message = new_list.serialize()

    return make_response(jsonify(message), status.HTTP_201_CREATED)


######################################################################
# DELETE A wishlist
######################################################################
@app.route(f"{BASE_URL}/<int:wishlist_id>", methods=["DELETE"])
def delete_wishlists(wishlist_id):
    """
    Delete an Account

    This endpoint will delete an Account based the id specified in the path
    """
    app.logger.info("Request to delete wishlist with id: %s", wishlist_id)

    # Retrieve the account to delete and delete it if it exists
    wishlist = Wishlist.find(wishlist_id)
    if wishlist:
        wishlist.delete()

    return make_response("", status.HTTP_204_NO_CONTENT)


######################################################################
# RETRIEVE A wishlist by id
######################################################################
@app.route(f"{BASE_URL}/<int:wishlist_id>", methods=["GET"])
def get_wishlists(wishlist_id):
    """
    Retrieve a single Wishlist
    This endpoint will return an Wishlist based on it's id
    """
    app.logger.info("Request for Wishlist with id: %s", wishlist_id)
    # See if the wishlist exists and abort if it doesn't
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' could not be found.",
        )
    return wishlist.serialize(), status.HTTP_200_OK


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

# Place your REST API code here ...
