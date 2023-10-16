"""
TestYourResourceModel API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
# import os
import logging
from unittest import TestCase
from service import app
from service.models import db, Wishlist, Product
from service.common import status  # HTTP Status Codes
from tests.factories import WishlistFactory, ProductFactory

BASE_URL = "/wishlists"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestWishlistServer(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""

    def setUp(self):
        """This runs before each test"""
        self.client = app.test_client()

    def tearDown(self):
        """This runs after each test"""

    ######################################################################
    #  HELPER FUNCTIONS
    ######################################################################
    def _create_wishlists(self, count):
        """create count number of test wishlists"""
        wishlists = []
        for _ in range(count):
            wishlist = WishlistFactory()
            resp = self.client.post(BASE_URL, json=wishlist.serialize())
            self.assertEqual(
                resp.status_code,
                status.HTTP_201_CREATED,
                "Could not create test wishlist",
            )
            new_account = resp.get_json()
            wishlist.id = new_account["id"]
            wishlists.append(wishlist)
        return wishlists

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_create_wishlist(self):
        """It should create a wishlist"""
        test_list = WishlistFactory()
        logging.debug("Test wishlist: %s", test_list.serialize())
        response = self.client.post(BASE_URL, json=test_list.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        res = response.get_json()
        self.assertEqual(res["owner"], test_list.owner)
        self.assertEqual(res["name"], test_list.name)
        self.assertEqual(res["products"], test_list.products)

    def test_delete_wishlist(self):
        """It should delete a selected wishlist"""
        wishlist = self._create_wishlists(1)[0]
        resp = self.client.delete(f"{BASE_URL}/{wishlist.id}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_create_product(self):
        """It should create a product in a wishlist"""
        test_wishlist = self._create_wishlists(1)[0]
        test_product = ProductFactory(wishlist_id=test_wishlist.id)
        response = self.client.post(
            f"{BASE_URL}/{test_wishlist.id}/products", json=test_product.serialize()
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        resp = response.get_json()
        self.assertEqual(resp["wishlist_id"], test_wishlist.id)
        self.assertEqual(resp["name"], test_product.name)
        # TBA
        # self.assertEqual(res["quanity"], test_product.quanity)
