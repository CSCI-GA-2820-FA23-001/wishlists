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
from service.models import db, Wishlist
from service.common import status  # HTTP Status Codes
from tests.factories import WishlistFactory

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
            new_wishlist_id = resp.get_json()["id"]
            new_wishlist = Wishlist.find(new_wishlist_id)
            wishlists.append(new_wishlist)
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

    def test_get_wishlist_id(self):
        """It should Get an Wishlist by id"""
        wishlists = self._create_wishlists(3)
        # print(wishlists)
        resp = self.client.get(f"{BASE_URL}/{wishlists[1].id}")

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], wishlists[1].name)

    def test_get_wishlist(self):
        """It should Read a single Wishlist"""
        # get the id of an wishlist
        wishlists = self._create_wishlists(1)
        wishlist = wishlists[0]
        resp = self.client.get(
            f"{BASE_URL}/{wishlist.id}", content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["id"], wishlist.id)

    def test_get_wishlist_not_found(self):
        """It should not Read an Wishlist that is not found"""
        resp = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
