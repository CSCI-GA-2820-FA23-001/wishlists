"""
Wishlist Service

Wishlist service for shopping
"""
import secrets
from functools import wraps
from datetime import date, datetime
from flask import jsonify, request, url_for, abort, make_response
from flask_restx import Resource, fields, reqparse, inputs
from service.common import status  # HTTP Status Codes
from service.models import Product, Wishlist


# Import Flask application
from . import app, api

BASE_URL = "/wishlists"


############################################################
# Health Endpoint
############################################################
@app.route("/health")
def health():
    """Health Status"""
    return (jsonify(status="OK"), status.HTTP_200_OK)


######################################################################
# Configure the Root route before OpenAPI
######################################################################
@app.route("/")
def index():
    """Index page"""
    return app.send_static_file("index.html")

    # """Root URL response"""
    # return (
    #     jsonify(
    #         name="Wishlist Service",
    #         version="1.0",
    #         paths=url_for("list_wishlists", _external=True),
    #     ),
    #     status.HTTP_200_OK,
    # )


# Define the model so that the docs reflect what can be sent

create_product_model = api.model(
    "Product",
    {
        "name": fields.String(required=True, description="The name of the product"),
        "wishlist_id": fields.Integer(
            required=True, description="The wishlist ID that the product belongs to"
        ),
        "quantity": fields.Integer(
            required=True, description="The quantity of the product"
        ),
    },
)

product_model = api.inherit(
    "ProductModel",
    create_product_model,
    {
        "_id": fields.Integer(
            readOnly=True,
            description="The unique id assigned to the product internally by service",
        ),
    },
)

create_wishlist_model = api.model(
    "Wishlist",
    {
        "name": fields.String(required=True, description="The name of the wishlist"),
        "date_joined": fields.Date(
            required=True,
            description="The date the wishlist is created",
        ),
        "owner": fields.String(required=True, description="The owner of the wishlist"),
        "products": fields.List(
            fields.Raw(product_model),
            required=False,
            description="The products that belongs to the wishlist",
        ),
    },
)

wishlist_model = api.inherit(
    "WishlistModel",
    create_wishlist_model,
    {
        "_id": fields.Integer(
            readOnly=True,
            description="The unique id assigned to the wishlist internally by service",
        ),
    },
)

# query string arguments
wishlist_args = reqparse.RequestParser()
wishlist_args.add_argument(
    "name", type=str, location="args", required=False, help="List Wishlists by name"
)
wishlist_args.add_argument(
    "owner", type=str, location="args", required=False, help="List Wishlists by owner"
)
wishlist_args.add_argument(
    "start",
    type=str,
    location="args",
    required=False,
    help="List Pets by start-date filter",
)
wishlist_args.add_argument(
    "end",
    type=str,
    location="args",
    required=False,
    help="List Pets by end-date filter",
)

product_args = reqparse.RequestParser()
product_args.add_argument(
    "wishlist_id",
    type=int,
    location="args",
    required=True,
    help="List Products by wishlist_id",
)
product_args.add_argument(
    "name", type=str, location="args", required=True, help="List Products by name"
)


######################################################################
# Authorization Decorator
######################################################################
def token_required(func):
    """Decorator to require a token for this endpoint"""

    @wraps(func)
    def decorated(*args, **kwargs):
        token = None
        if "X-Api-Key" in request.headers:
            token = request.headers["X-Api-Key"]

        if app.config.get("API_KEY") and app.config["API_KEY"] == token:
            return func(*args, **kwargs)

        return {"message": "Invalid or missing token"}, 401

    return decorated


######################################################################
# Function to generate a random API key (good for testing)
######################################################################
def generate_apikey():
    """Helper function used when testing API keys"""
    return secrets.token_hex(16)


######################################################################
# LIST ALL wishlist
######################################################################
@app.route(BASE_URL, methods=["GET"])
def list_wishlists():
    """Returns all of the wishlists. If there is a date filter, return filtered wishlists"""
    app.logger.info("Request for listing all wishlists")

    # Get query args
    owner = request.args.get("owner")
    start = request.args.get("start")
    end = request.args.get("end")
    name = request.args.get("name")

    # Process the query string if any

    if owner:
        accounts = Wishlist.find_by_owner(owner)
    elif name:
        accounts = Wishlist.find_by_name(name)
    elif start or end:
        # filter by start and end date
        start_date = None
        end_date = None
        if start:
            start_date = datetime.strptime(start, "%Y-%m-%d").date()
        if end:
            end_date = datetime.strptime(end, "%Y-%m-%d").date()
        accounts = Wishlist.filter_by_date(start_date, end_date)
    else:
        accounts = Wishlist.all()

    results = [account.serialize() for account in accounts]
    return make_response(jsonify(results), status.HTTP_200_OK)


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

    location_url = url_for("get_wishlists", wishlist_id=new_list.id, _external=True)

    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


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
# UPDATE AN EXISTING Wishlist
######################################################################
@app.route("/wishlists/<int:wishlist_id>", methods=["PUT"])
def update_wishlists_by_name(wishlist_id):
    """
    Update an Wishlist
    This endpoint will update an Wishlist based the body that is posted
    """
    app.logger.info("Request to update wishlist with id: %s", wishlist_id)
    check_content_type("application/json")

    # See if the wishlist exists and abort if it doesn't
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' was not found.",
        )
    # Update from the json in the body of the request
    wishlist.deserialize(request.get_json())
    wishlist.id = wishlist_id
    # wishlist.name = newname
    wishlist.update()

    return make_response(jsonify(wishlist.serialize()), status.HTTP_200_OK)


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
# LIST PRODUCTS
######################################################################
@app.route(f"{BASE_URL}/<int:wishlist_id>/products", methods=["GET"])
def list_products(wishlist_id):
    """Returns all of the products for a wishlist"""
    app.logger.info("Request for all Products for Wishlist with id: %s", wishlist_id)

    # See if the wishlist exists and abort if it doesn't
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id '{wishlist_id}' could not be found.",
        )

    # Get query args
    name = request.args.get("name")
    if name:
        products = wishlist.find_product_by_name(name)
        results = [product.serialize() for product in products]
    else:
        results = [product.serialize() for product in wishlist.products]

    return make_response(jsonify(results), status.HTTP_200_OK)


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
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist {wishlist_id} not exist",
        )
    # Create the product
    new_product = Product()
    info = request.get_json()
    new_product.deserialize(info)
    new_product.wishlist = wishlist
    new_product.create()

    # Update wishlist_id if not consistent
    if new_product.wishlist_id and new_product.wishlist_id != wishlist_id:
        new_product.wishlist_id = wishlist_id
        new_product.update()

    # wishlist.products.append(new_product)
    wishlist.update()

    # Return response
    message = new_product.serialize()

    location_url = url_for(
        "get_product",
        wishlist_id=wishlist.id,
        product_id=new_product.id,
        _external=True,
    )

    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
# RETRIEVE a product in the wishlist
######################################################################
@app.route(f"{BASE_URL}/<int:wishlist_id>/products/<int:product_id>", methods=["GET"])
def get_product(wishlist_id, product_id):
    """
    Get an product

    This endpoint returns just an product
    """
    app.logger.info(
        "Request to update Product %d in Wishlist id: %d", product_id, wishlist_id
    )

    # See if the product exists and abort if it doesn't
    product = Product.find(product_id)
    if not product:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Product with id '{product_id}' could not be found.",
        )

    return make_response(jsonify(product.serialize()), status.HTTP_200_OK)


######################################################################
# UPDATE a product in the wishlist
######################################################################
@app.route(f"{BASE_URL}/<int:wishlist_id>/products/<int:product_id>", methods=["PUT"])
def update_product(wishlist_id, product_id):
    """
    Update an product

    This endpoint will update the name and quantity of a product based given id
    """
    app.logger.info(
        "Request to update Product %d in Wishlist id: %d", product_id, wishlist_id
    )
    check_content_type("application/json")

    # check the wishlist
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist with id {wishlist_id} not exist",
        )
    # check the product
    product = Product.find(product_id)
    if not product:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Product with id '{product_id}' not exist",
        )
    # check if the wishlist contains the product
    if product not in wishlist.products:
        abort(
            status.HTTP_400_BAD_REQUEST,
            f"Wishlist {wishlist_id} does not contain Product {product_id}",
        )

    data = request.get_json()
    if str(data["wishlist_id"]) != str(wishlist_id):
        abort(
            status.HTTP_409_CONFLICT,
            "Should not change the wishlist a product belongs to",
        )
    product.deserialize(request.get_json())
    product.update()

    return make_response(jsonify(product.serialize()), status.HTTP_200_OK)


######################################################################
#  DELETE a product in the wishlist
######################################################################
@app.route(
    f"{BASE_URL}/<int:wishlist_id>/products/<int:product_id>", methods=["DELETE"]
)
def delete_products(wishlist_id, product_id):
    """
    Delete a product

    This endpoint will delete a product based the id specified in the path
    """
    app.logger.info("Request to delete a product in wishlist %d", wishlist_id)
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist {wishlist_id} not exist",
        )
    product = Product.find(product_id)
    if product:
        product.delete()

    return make_response("", status.HTTP_204_NO_CONTENT)


######################################################################
# COPY AN EXISTING Wishlist
######################################################################
@app.route(f"{BASE_URL}/<int:wishlist_id>/copy", methods=["POST"])
def copy_wishlist_by_id(wishlist_id):
    """
    COPY AN EXISTING Wishlist with an id
    """
    old = Wishlist.find(wishlist_id).serialize()
    if not old:
        abort(
            status.HTTP_404_NOT_FOUND,
            f"Wishlist {wishlist_id} not exist",
        )

    new = {}
    for key, val in old.items():
        if key not in ["id", "name", "products"]:
            new[key] = val
    new["name"] = old["name"] + " COPY"
    new["products"] = []
    new["date_joined"] = str(date.today())
    new_list = Wishlist()
    new_list.deserialize(new)
    new_list.create()

    for product in old["products"]:
        product["wishlist_id"] = new_list.id
        new_product = Product()
        new_product.deserialize(product)
        new_product.create()

    location_url = url_for("get_wishlists", wishlist_id=new_list.id, _external=True)

    return make_response(
        jsonify(new_list.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


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
