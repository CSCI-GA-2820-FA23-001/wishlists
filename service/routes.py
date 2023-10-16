"""
Wishlist Service

Implementation of CRUD wishlists and products in the wishlists
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
    message = """
    list_wishlists     GET      /wishlists
    create_wishlists   POST     /wishlists
    get_wishlists      GET      /wishlists/<wishlist_id>
    update_wishlists   PUT      /wishlists/<wishlist_id>
    delete_wishlists   DELETE   /wishlists/<wishlist_id>
    list_products    GET      /wishlists/<wishlist_id>/products
    create_products  POST     /wishlists/<wishlist_id>/products
    get_products     GET      /wishlists/<wishlist_id>/products/<product_id>
    update_products  PUT      /wishlists/<wishlist_id>/products/<product_id>
    delete_products  DELETE   /wishlists/<wishlist_id>/products/<product_id>
    """
    response = make_response(message)
    response.status = status.HTTP_200_OK
    response.headers["Content-Type"] = "text/plain"
    return response


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
def delete_accounts(wishlist_id):
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
#  CREATE a product in the wishlist
######################################################################
@app.route(f"{BASE_URL}/<int:wishlist_id>/products", methods=["POST"])
def create_products(wishlist_id):
    """
    Create a product

    This endpoint will create a product based the data in the body that is posted
    """
    app.logger.info("Request to create a product in wishlist %d", wishlist_id)
    check_content_type("application/json")

    wishlist = Wishlist.find(wishlist_id)
    if wishlist:
        # Create the product
        new_product = Product()
        info = request.get_json()
        new_product.deserialize(info)
        new_product.wishlist = wishlist
        new_product.create()

        # Update wishlist_id if not consistent
        if new_product.wishlist_id != wishlist_id:
            new_product.wishlist_id = wishlist_id
            new_product.update()

        # wishlist.products.append(new_product)
        wishlist.update()

        # Return response
        message = new_product.serialize()
        return make_response(jsonify(message), status.HTTP_201_CREATED)
    else:
        return make_response("Error: Wishlist not found", status.HTTP_404_NOT_FOUND)


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

# Place your REST API code here ...


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {media_type}",
    )
