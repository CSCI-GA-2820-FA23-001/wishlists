"""
Test cases for Wishlist Model

"""
import logging
import unittest
import os
from service import app
from service.models import Wishlist, Product, DataValidationError, db
from tests.factories import WishlistFactory, ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  Wishlist   M O D E L   T E S T   C A S E S
######################################################################
class TestWishlist(unittest.TestCase):
    """Test Cases for Wishlist Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Wishlist.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""

    def setUp(self):
        """This runs before each test"""
        db.session.query(Wishlist).delete()  # clean up the last tests
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_an_wishlist(self):
        """It should Create an Wishlist and assert that it exists"""
        fake_wishlist = WishlistFactory()
        # pylint: disable=unexpected-keyword-arg
        wishlist = Wishlist(
            name=fake_wishlist.name,
            date_joined=fake_wishlist.date_joined,
        )
        self.assertIsNotNone(wishlist)
        self.assertEqual(wishlist.id, None)
        self.assertEqual(wishlist.name, fake_wishlist.name)
        self.assertEqual(wishlist.date_joined, fake_wishlist.date_joined)

    # def test_add_a_wishlist(self):
    #     """It should Create an wishlist and add it to the database"""
    #     wishlists = Wishlist.all()
    #     self.assertEqual(wishlists, [])
    #     wishlist = WishlistFactory()
    #     wishlist.create()
    #     # Assert that it was assigned an id and shows up in the database
    #     self.assertIsNotNone(wishlist.id)
    #     wishlists = Wishlist.all()
    #     self.assertEqual(len(wishlists), 1)

    # def test_read_wishlist(self):
    #     """It should Read an wishlist"""
    #     wishlist = WishlistFactory()
    #     wishlist.create()

    #     # Read it back
    #     found_wishlist = Wishlist.find(wishlist.id)
    #     self.assertEqual(found_wishlist.id, wishlist.id)
    #     self.assertEqual(found_wishlist.name, wishlist.name)
    #     self.assertEqual(found_wishlist.email, wishlist.email)
    #     self.assertEqual(found_wishlist.phone_number, wishlist.phone_number)
    #     self.assertEqual(found_wishlist.date_joined, wishlist.date_joined)
    #     self.assertEqual(found_wishlist.products, [])

    # def test_update_wishlist(self):
    #     """It should Update an wishlist"""
    #     wishlist = WishlistFactory(email="advent@change.me")
    #     wishlist.create()
    #     # Assert that it was assigned an id and shows up in the database
    #     self.assertIsNotNone(wishlist.id)
    #     self.assertEqual(wishlist.email, "advent@change.me")

    #     # Fetch it back
    #     wishlist = Wishlist.find(wishlist.id)
    #     wishlist.email = "XYZZY@plugh.com"
    #     wishlist.update()

    #     # Fetch it back again
    #     wishlist = Wishlist.find(wishlist.id)
    #     self.assertEqual(wishlist.email, "XYZZY@plugh.com")

    # def test_delete_an_wishlist(self):
    #     """It should Delete an wishlist from the database"""
    #     wishlists = Wishlist.all()
    #     self.assertEqual(wishlists, [])
    #     wishlist = WishlistFactory()
    #     wishlist.create()
    #     # Assert that it was assigned an id and shows up in the database
    #     self.assertIsNotNone(wishlist.id)
    #     wishlists = Wishlist.all()
    #     self.assertEqual(len(wishlists), 1)
    #     wishlist = wishlists[0]
    #     wishlist.delete()
    #     wishlists = Wishlist.all()
    #     self.assertEqual(len(wishlists), 0)

    # def test_list_all_wishlists(self):
    #     """It should List all wishlists in the database"""
    #     wishlists = Wishlist.all()
    #     self.assertEqual(wishlists, [])
    #     for wishlist in WishlistFactory.create_batch(5):
    #         wishlist.create()
    #     # Assert that there are not 5 wishlists in the database
    #     wishlists = Wishlist.all()
    #     self.assertEqual(len(wishlists), 5)

    # def test_find_by_name(self):
    #     """It should Find an Wishlist by name"""
    #     wishlist = WishlistFactory()
    #     wishlist.create()

    #     # Fetch it back by name
    #     same_wishlist = Wishlist.find_by_name(wishlist.name)[0]
    #     self.assertEqual(same_wishlist.id, wishlist.id)
    #     self.assertEqual(same_wishlist.name, wishlist.name)

    # def test_serialize_an_wishlist(self):
    #     """It should Serialize an wishlist"""
    #     wishlist = WishlistFactory()
    #     product = ProductFactory()
    #     wishlist.products.append(product)
    #     serial_wishlist = wishlist.serialize()
    #     self.assertEqual(serial_wishlist["id"], wishlist.id)
    #     self.assertEqual(serial_wishlist["name"], wishlist.name)
    #     self.assertEqual(serial_wishlist["email"], wishlist.email)
    #     self.assertEqual(serial_wishlist["phone_number"], wishlist.phone_number)
    #     self.assertEqual(serial_wishlist["date_joined"], str(wishlist.date_joined))
    #     self.assertEqual(len(serial_wishlist["products"]), 1)
    #     products = serial_wishlist["products"]
    #     self.assertEqual(products[0]["id"], product.id)
    #     self.assertEqual(products[0]["wishlist_id"], product.wishlist_id)
    #     self.assertEqual(products[0]["name"], product.name)
    #     self.assertEqual(products[0]["street"], product.street)
    #     self.assertEqual(products[0]["city"], product.city)
    #     self.assertEqual(products[0]["state"], product.state)
    #     self.assertEqual(products[0]["postal_code"], product.postal_code)

    # def test_deserialize_an_wishlist(self):
    #     """It should Deserialize an wishlist"""
    #     wishlist = WishlistFactory()
    #     wishlist.products.append(ProductFactory())
    #     wishlist.create()
    #     serial_wishlist = wishlist.serialize()
    #     new_wishlist = Wishlist()
    #     new_wishlist.deserialize(serial_wishlist)
    #     self.assertEqual(new_wishlist.name, wishlist.name)
    #     self.assertEqual(new_wishlist.email, wishlist.email)
    #     self.assertEqual(new_wishlist.phone_number, wishlist.phone_number)
    #     self.assertEqual(new_wishlist.date_joined, wishlist.date_joined)

    # def test_deserialize_with_key_error(self):
    #     """It should not Deserialize an wishlist with a KeyError"""
    #     wishlist = Wishlist()
    #     self.assertRaises(DataValidationError, wishlist.deserialize, {})

    # def test_deserialize_with_type_error(self):
    #     """It should not Deserialize an wishlist with a TypeError"""
    #     wishlist = Wishlist()
    #     self.assertRaises(DataValidationError, wishlist.deserialize, [])

    # def test_deserialize_address_key_error(self):
    #     """It should not Deserialize an product with a KeyError"""
    #     product = Product()
    #     self.assertRaises(DataValidationError, product.deserialize, {})

    # def test_deserialize_address_type_error(self):
    #     """It should not Deserialize an product with a TypeError"""
    #     product = Product()
    #     self.assertRaises(DataValidationError, product.deserialize, [])

    # def test_add_wishlist_address(self):
    #     """It should Create an wishlist with an product and add it to the database"""
    #     wishlists = Wishlist.all()
    #     self.assertEqual(wishlists, [])
    #     wishlist = WishlistFactory()
    #     product = ProductFactory(wishlist=wishlist)
    #     wishlist.products.append(product)
    #     wishlist.create()
    #     # Assert that it was assigned an id and shows up in the database
    #     self.assertIsNotNone(wishlist.id)
    #     wishlists = Wishlist.all()
    #     self.assertEqual(len(wishlists), 1)

    #     new_wishlist = Wishlist.find(wishlist.id)
    #     self.assertEqual(new_wishlist.products[0].name, product.name)

    #     address2 = ProductFactory(wishlist=wishlist)
    #     wishlist.products.append(address2)
    #     wishlist.update()

    #     new_wishlist = Wishlist.find(wishlist.id)
    #     self.assertEqual(len(new_wishlist.products), 2)
    #     self.assertEqual(new_wishlist.products[1].name, address2.name)

    # def test_update_wishlist_address(self):
    #     """It should Update an wishlists product"""
    #     wishlists = Wishlist.all()
    #     self.assertEqual(wishlists, [])

    #     wishlist = WishlistFactory()
    #     product = ProductFactory(wishlist=wishlist)
    #     wishlist.create()
    #     # Assert that it was assigned an id and shows up in the database
    #     self.assertIsNotNone(wishlist.id)
    #     wishlists = Wishlist.all()
    #     self.assertEqual(len(wishlists), 1)

    #     # Fetch it back
    #     wishlist = Wishlist.find(wishlist.id)
    #     old_address = wishlist.products[0]
    #     print("%r", old_address)
    #     self.assertEqual(old_address.city, product.city)
    #     # Change the city
    #     old_address.city = "XX"
    #     wishlist.update()

    #     # Fetch it back again
    #     wishlist = Wishlist.find(wishlist.id)
    #     product = wishlist.products[0]
    #     self.assertEqual(product.city, "XX")

    # def test_delete_wishlist_address(self):
    #     """It should Delete an wishlists product"""
    #     wishlists = Wishlist.all()
    #     self.assertEqual(wishlists, [])

    #     wishlist = WishlistFactory()
    #     product = ProductFactory(wishlist=wishlist)
    #     wishlist.create()
    #     # Assert that it was assigned an id and shows up in the database
    #     self.assertIsNotNone(wishlist.id)
    #     wishlists = Wishlist.all()
    #     self.assertEqual(len(wishlists), 1)

    #     # Fetch it back
    #     wishlist = Wishlist.find(wishlist.id)
    #     product = wishlist.products[0]
    #     product.delete()
    #     wishlist.update()

    #     # Fetch it back again
    #     wishlist = Wishlist.find(wishlist.id)
    #     self.assertEqual(len(wishlist.products), 0)
