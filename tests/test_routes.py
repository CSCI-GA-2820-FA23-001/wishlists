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
            new_wishlist_id = resp.get_json()["id"]
            new_wishlist = Wishlist.find(new_wishlist_id)
            wishlists.append(new_wishlist)
        return wishlists

    def _create_products(self, wishlist_id, count):
        """create count number of product in a given wishlist"""
        products = []
        for _ in range(count):
            product = ProductFactory(wishlist_id=wishlist_id)
            resp = self.client.post(
                f"{BASE_URL}/{wishlist_id}/products", json=product.serialize()
            )
            self.assertEqual(
                resp.status_code,
                status.HTTP_201_CREATED,
                "Could not create test product",
            )
            new_product_id = resp.get_json()["id"]
            new_product = Product.find(new_product_id)
            products.append(new_product)
        return products

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
        # self.assertEqual(res["quantity"], test_product.quantity)

        # check if the product is in the wishlist
        product_id = resp["id"]
        product = Product.find(product_id)
        products = test_wishlist.products
        self.assertIn(product, products)

    def test_create_product_wishlist_not_exist(self):
        """It should report 404 error: wishlist not exist when creating products"""
        response = self.client.post(
            f"{BASE_URL}/0/products", json={"name": "Product", "wishlist_id": 0}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_product(self):
        """It should delete a product in a wishlist"""
        test_wishlist = self._create_wishlists(1)[0]
        test_product = self._create_products(test_wishlist.id, 1)[0]
        response = self.client.delete(
            f"{BASE_URL}/{test_wishlist.id}/products/{test_product.id}"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_product_wishlist_not_exist(self):
        """It should report 404 error: wishlist not exist when deleting a product"""
        test_wishlist = self._create_wishlists(1)[0]
        test_product = self._create_products(test_wishlist.id, 1)[0]
        response = self.client.delete(f"{BASE_URL}/0/products/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

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

