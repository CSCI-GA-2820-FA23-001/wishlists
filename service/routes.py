"""
Wishlist Service

Wishlist service for shopping
"""
import secrets

# from functools import wraps
from datetime import date, datetime
from flask import jsonify, request, abort
from flask_restx import Resource, fields, reqparse  # , inputs
from service.common import status  # HTTP Status Codes
from service.models import Product, Wishlist


# Import Flask application
from . import app, api

BASE_URL = "/api/wishlists"


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
        "id": fields.Integer(
            readOnly=True,
            description="The unique id assigned to the product internally by service",
        ),
    },
)

create_wishlist_model = api.model(
    "Wishlist",
    {
        "name": fields.String(required=True, description="The name of the wishlist"),
        "owner": fields.String(required=True, description="The owner of the wishlist"),
        "date_joined": fields.Date(
            required=True,
            description="The date when the wishlist is created",
        ),
        "products": fields.List(
            fields.Nested(product_model),
            required=False,
            description="The products that belongs to the wishlist",
        ),
    },
)

wishlist_model = api.inherit(
    "WishlistModel",
    create_wishlist_model,
    {
        "id": fields.Integer(
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
    "name", type=str, location="args", required=False, help="List Products by name"
)


######################################################################
# Authorization Decorator
######################################################################
# def token_required(func):
#     """Decorator to require a token for this endpoint"""

#     @wraps(func)
#     def decorated(*args, **kwargs):
#         token = None
#         if "X-Api-Key" in request.headers:
#             token = request.headers["X-Api-Key"]

#         if app.config.get("API_KEY") and app.config["API_KEY"] == token:
#             return func(*args, **kwargs)

#         return {"message": "Invalid or missing token"}, 401

#     return decorated


######################################################################
# Function to generate a random API key (good for testing)
######################################################################
def generate_apikey():
    """Helper function used when testing API keys"""
    return secrets.token_hex(16)


######################################################################
#  PATH: /wishlists
######################################################################
@api.route("/wishlists", strict_slashes=False)
class WishlistCollection(Resource):
    """Handles all interactions with collections of Wishlists

    APIs:
    GET     /wishlists  List all wishlists
    POST    /wishlists  Create a wishlist
    """

    # ------------------------------------------------------------------
    # LIST ALL WISHLISTS
    # ------------------------------------------------------------------
    @api.doc("list_wishlists")
    @api.expect(wishlist_args, validate=True)
    @api.marshal_list_with(wishlist_model)
    def get(self):
        """Returns all of the wishlists. If there is a date filter, return filtered wishlists"""
        app.logger.info("Request for listing all wishlists")

        # Get query args
        args = wishlist_args.parse_args()
        owner = args["owner"]
        start = args["start"]
        end = args["end"]
        name = args["name"]

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
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # CREATE A NEW WISHLIST
    # ------------------------------------------------------------------
    @api.doc("create_wishlists", security="apikey")
    @api.response(400, "The posted data was not valid")
    @api.expect(create_wishlist_model)
    @api.marshal_with(wishlist_model, code=201)
    # @token_required
    def post(self):
        """create an empty wishlist with post method"""
        app.logger.info("Request for creating a wishlist")
        new_list = Wishlist()
        new_list.deserialize(api.payload)
        new_list.create()
        message = new_list.serialize()
        app.logger.info("Wishlist created with id: %d", message["id"])

        # needs to be updated after refactoring done
        location_url = api.url_for(
            WishlistResource, wishlist_id=new_list.id, _external=True
        )

        return message, status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
#  PATH: /wishlists/{wishlist_id}
######################################################################
@api.route("/wishlists/<wishlist_id>")
@api.param("wishlist_id", "The Wishlist identifier")
class WishlistResource(Resource):
    """
    WishlistResource class

    Allows the manipulation of a single Wishlist
    GET /wishlist{wishlist_id} - Returns a Wishlist based on it's id
    PUT /wishlist{wishlist_id} - Update a Wishlist with the id
    DELETE /wishlist{wishlist_id} -  Deletes a Wishlist with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE A WISHLIST
    # ------------------------------------------------------------------
    @api.doc("get_wishlists")
    @api.response(404, "Wishlist not found")
    @api.marshal_with(wishlist_model)
    def get(self, wishlist_id):
        """
        Retrieve a single wishlist

        This endpoint will return a Wishlist based on it's id
        """
        app.logger.info("Request to Retrieve a wishlist with id [%s]", wishlist_id)
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' could not be found.",
            )
        return wishlist.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING WISHLIST
    # ------------------------------------------------------------------
    @api.doc("update_wishlists", security="apikey")
    @api.response(404, "Wishlist not found")
    @api.response(400, "The posted Wishlist data was not valid")
    @api.expect(wishlist_model)
    @api.marshal_with(wishlist_model)
    # @token_required
    def put(self, wishlist_id):
        """
        Update a Wishlist

        This endpoint will update a Wishlist based the body that is posted
        """
        app.logger.info("Request to Update a wishlist with id [%s]", wishlist_id)
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' could not be found.",
            )
        app.logger.debug("Payload = %s", api.payload)
        data = api.payload
        wishlist.deserialize(data)
        wishlist.id = wishlist_id
        wishlist.update()
        return wishlist.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A WISHLIST
    # ------------------------------------------------------------------
    @api.doc("delete_wishlists", security="apikey")
    @api.response(204, "Wishlist deleted")
    # @token_required
    def delete(self, wishlist_id):
        """
        Delete a Wishlist

        This endpoint will delete a Wishlist based the id specified in the path
        """
        app.logger.info("Request to Update a wishlist with id [%s]", wishlist_id)
        wishlist = Wishlist.find(wishlist_id)
        if wishlist:
            wishlist.delete()
            app.logger.info("Wishlist with id [%s] was deleted", wishlist_id)

        return "", status.HTTP_204_NO_CONTENT


######################################################################
# PATH: /wishlists/<int:wishlist_id>/products
######################################################################
@api.route("/wishlists/<wishlist_id>/products", strict_slashes=False)
@api.param("wishlist_id", "The Wishlist id")
class ProductCollection(Resource):
    """
    ProductCollection class

    Allows the manipulation of the products in one wishlist
    GET /wishlists/<int:wishlist_id>/products - Returns a list of product in a Wishlist based on wishlist's id
    POST /wishlists/<int:wishlist_id>/products - create a product in a wishlist based the data posted
    """

    # ------------------------------------------------------------------
    # LIST ALL PRODUCTS IN A WISHLIST
    # ------------------------------------------------------------------
    @api.doc("list_products")
    @api.response(404, "products in wishlist not found")
    @api.marshal_list_with(product_model)
    def get(self, wishlist_id):
        """Returns all of the products for a wishlist"""
        app.logger.info(
            "Request for all Products for Wishlist with id: %s", wishlist_id
        )

        # See if the wishlist exists and abort if it doesn't
        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist with id '{wishlist_id}' could not be found.",
            )

        # Get query args
        args = product_args.parse_args()
        if args["name"]:
            products = wishlist.find_product_by_name(args["name"])
            results = [product.serialize() for product in products]
        else:
            results = [product.serialize() for product in wishlist.products]

        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    #  CREATE a product in the wishlist
    # ------------------------------------------------------------------
    @api.doc("create_product", security="apikey")
    @api.response(400, "The posted data was not valid")
    @api.expect(create_product_model)
    @api.marshal_with(product_model, code=201)
    # @token_required
    def post(self, wishlist_id):
        """
        Create a product

        This endpoint will create a product based the data in the body that is posted
        """
        app.logger.info("Request to create a product in wishlist %d", wishlist_id)

        wishlist = Wishlist.find(wishlist_id)
        if not wishlist:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist {wishlist_id} not exist",
            )
        # Create the product
        new_product = Product()
        info = api.payload
        if info["wishlist_id"] != wishlist.id:
            info["wishlist_id"] = wishlist.id  # Update wishlist_id if not consistent
        new_product.deserialize(info)
        new_product.wishlist = wishlist
        new_product.create()

        # wishlist.products.append(new_product)
        wishlist.update()

        # Return response
        message = new_product.serialize()

        # need to refactor after ProductResource created
        location_url = api.url_for(
            ProductResource,
            wishlist_id=wishlist.id,
            product_id=new_product.id,
            _external=True,
        )

        return message, status.HTTP_201_CREATED, {"Location": location_url}


@api.route(
    "/wishlists/<int:wishlist_id>/products/<int:product_id>", strict_slashes=False
)
@api.doc(params={"wishlist_id": "The Wishlist id", "product_id": "The Product id"})
class ProductResource(Resource):
    """
    ProductResource class

    Allows the manipulation of a single Product in one wishlist
    GET - RETRIEVE A PRODUCT in a wishlist
    PUT - UPDATE a product in the wishlist
    DELETE - DELETE a product in the wishlist
    """

    # ------------------------------------------------------------------
    # RETRIEVE A PRODUCT in a wishlist
    # ------------------------------------------------------------------
    @api.doc("get_product")
    @api.response(404, "product not found")
    @api.marshal_with(product_model)
    def get(self, wishlist_id, product_id):
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

        return product.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE a product in the wishlist
    # ------------------------------------------------------------------
    @api.doc("update_product")
    @api.response(404, "product not found")
    @api.marshal_with(product_model)
    def put(self, wishlist_id, product_id):
        """
        Update an product

        This endpoint will update the name and quantity of a product based given id
        """
        app.logger.info(
            "Request to update Product %d in Wishlist id: %d", product_id, wishlist_id
        )

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

        data = api.payload
        if str(data["wishlist_id"]) != str(wishlist_id):
            abort(
                status.HTTP_409_CONFLICT,
                "Should not change the wishlist a product belongs to",
            )
        product.deserialize(data)
        product.update()

        return product.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE a product in the wishlist
    # ------------------------------------------------------------------
    @api.doc("update_product")
    @api.response(204, "Wishlist deleted")
    def delete(self, wishlist_id, product_id):
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

        return "", status.HTTP_204_NO_CONTENT


######################################################################
# PATH: /wishlists/<int:wishlist_id>/copy
######################################################################
@api.route("/wishlists/<int:wishlist_id>/copy", strict_slashes=False)
@api.param("wishlist_id", "The Wishlist id")
class WishlistCopy(Resource):
    """
    WishlistCopy class

    Allows the action to copy one wishlist with its id
    POST - create a wishlist with diff id but same content
    """

    # ------------------------------------------------------------------
    # COPY AN EXISTING Wishlist
    # ------------------------------------------------------------------
    @api.doc("get_wishlists")
    @api.response(404, "Wishlist not found")
    @api.marshal_with(wishlist_model)
    def post(self, wishlist_id):
        """
        COPY AN EXISTING Wishlist with an id
        """
        old_wishlist = Wishlist.find(wishlist_id)
        if not old_wishlist:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Wishlist {wishlist_id} not exist",
            )
        old = old_wishlist.serialize()

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

        # location_url = url_for("get_wishlists", wishlist_id=new_list.id, _external=True)
        location_url = api.url_for(
            WishlistResource, wishlist_id=new_list.id, _external=True
        )

        return (
            new_list.serialize(),
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
