"""
Models for Wishlist

All of the models are stored in this module
"""
import logging
from datetime import date
from abc import abstractmethod
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


def init_db(app):
    """Initialize the SQLAlchemy app"""
    Wishlist.init_db(app)


######################################################################
#  P E R S I S T E N T   B A S E   M O D E L
######################################################################
class PersistentBase:
    """Base class added persistent methods"""

    def __init__(self):
        self.id = None  # pylint: disable=invalid-name

    @abstractmethod
    def serialize(self) -> dict:
        """Convert an object into a dictionary"""

    @abstractmethod
    def deserialize(self, data: dict) -> None:
        """Convert a dictionary into an object"""

    def create(self):
        """
        Creates a Wishlist to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()

    def update(self):
        """
        Updates a Wishlist to the database
        """
        logger.info("Updating %s", self.name)
        if not self.id:
            raise DataValidationError("Update called with empty ID field")
        db.session.commit()

    def delete(self):
        """Removes a Wishlist from the data store"""
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def init_db(cls, app):
        """Initializes the database session"""
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """Returns all of the records in the database"""
        logger.info("Processing all records")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a record by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)


######################################################################
#  P R O D U C T   M O D E L
######################################################################
class Product(db.Model, PersistentBase):
    """
    Class that represents an Product
    """

    __tablename__ = "product"

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    wishlist_id = db.Column(
        db.Integer, db.ForeignKey("wishlist.id", ondelete="CASCADE"), nullable=False
    )
    name = db.Column(db.String(64))

    def __repr__(self):
        return f"<Product {self.name} id=[{self.id}] wishlist[{self.wishlist_id}]>"

    def __str__(self):
        return f"{self.name}:"

    def serialize(self) -> dict:
        """Converts an Product into a dictionary"""
        return {
            "id": self.id,
            "wishlist_id": self.wishlist_id,
            "name": self.name,
        }

    def deserialize(self, data: dict) -> None:
        """
        Populates an Product from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.wishlist_id = data["wishlist_id"]
            self.name = data["name"]

        except KeyError as error:
            raise DataValidationError(
                "Invalid Product: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Product: body of request contained "
                "bad or no data " + error.args[0]
            ) from error
        return self


######################################################################
#  W I S H L I S T   M O D E L
######################################################################
class Wishlist(db.Model, PersistentBase):
    """
    Class that represents an Wishlist
    """    

    __tablename__ = "wishlist"

    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    date_joined = db.Column(db.Date(), nullable=False, default=date.today())
    products = db.relationship("Product", backref="wishlist", passive_deletes=True)
    owner = db.Column(db.String(64))

    def __repr__(self):
        return f"<Wishlist {self.name} id=[{self.id}]>"

    def serialize(self):
        """Converts an Wishlist into a dictionary"""
        wishlist = {
            "id": self.id,
            "name": self.name,
            "date_joined": self.date_joined.isoformat(),
            "products": [],
            "owner": self.owner,
        }
        for product in self.products:
            wishlist["products"].append(product.serialize())
        return wishlist

    def deserialize(self, data):
        """
        Populates an Wishlist from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            self.date_joined = date.fromisoformat(data["date_joined"])
            self.owner = data["owner"]
            # handle inner list of products
            product_list = data.get("products")
            for json_address in product_list:
                product = Product()
                product.deserialize(json_address)
                self.products.append(product)
        except KeyError as error:
            raise DataValidationError(
                "Invalid Wishlist: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Wishlist: body of request contained "
                "bad or no data - " + error.args[0]
            ) from error
        return self

    @classmethod
    def find_by_name(cls, name):
        """Returns all Wishlists with the given name

        Args:
            name (string): the name of the Wishlists you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)
