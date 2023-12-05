"""
TestYourResourceModel API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
# import os
import logging
from unittest import TestCase
from datetime import date
from service import app, routes
from service.models import db, Wishlist, Product
from service.common import status  # HTTP Status Codes
from tests.factories import WishlistFactory, ProductFactory


BASE_URL = "/api/wishlists"
CONTENT_TYPE_JSON = "application/json"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestWishlistServer(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        api_key = routes.generate_apikey()
        app.config["API_KEY"] = api_key
        app.logger.setLevel(logging.CRITICAL)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""

    def setUp(self):
        """This runs before each test"""
        self.app = app.test_client()
        self.headers = {"X-Api-Key": app.config["API_KEY"]}
        db.session.query(Wishlist).delete()  # clean up the last tests
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()
        self.client = app.test_client()

    def tearDown(self):
        """This runs after each test"""
        #resp = self.app.delete(BASE_URL, headers=self.headers)
        #self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        db.session.remove()

    ######################################################################
    #  HELPER FUNCTIONS
    ######################################################################
    def _create_wishlists(self, count):
        """create count number of test wishlists"""
        wishlists = []
        for _ in range(count):
            wishlist = WishlistFactory()
            resp = self.client.post(
                BASE_URL, 
                json=wishlist.serialize(),
                content_type=CONTENT_TYPE_JSON,
                headers=self.headers,
            )
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
                f"{BASE_URL}/{wishlist_id}/products", 
                json=product.serialize(),
                headers=self.headers,
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
    def test_health_check(self):
        """It should return"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_create_wishlist(self):
        """It should create a wishlist"""
        test_list = WishlistFactory()
        logging.debug("Test wishlist: %s", test_list.serialize())
        response = self.client.post(
            BASE_URL, 
            json=test_list.serialize(),
            content_type=CONTENT_TYPE_JSON,
            headers=self.headers,
            )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

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
        self.assertEqual(resp["quantity"], test_product.quantity)

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

    def test_list_product(self):
        """It should Get a list of Products"""
        # add two products to wishlist
        wishlist = self._create_wishlists(1)[0]
        product_list = ProductFactory.create_batch(2)
        # Create product 1
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/products", json=product_list[0].serialize()
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # Create product 2
        resp = self.client.post(
            f"{BASE_URL}/{wishlist.id}/products", json=product_list[1].serialize()
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # get the list back and make sure there are 2
        resp = self.client.get(f"{BASE_URL}/{wishlist.id}/products")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        self.assertEqual(len(data), 2)

        # test get products by name
        resp = self.client.get(
            f"{BASE_URL}/{wishlist.id}/products?name={wishlist.products[0].name}"
        )
        data = resp.get_json()[0]
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(data["name"], wishlist.products[0].name)

        # test wishlist not exist
        resp = self.client.get(f"{BASE_URL}/0/products")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_product(self):
        """It should Get an product from an wishlist"""
        # create a known address
        test_wishlist = self._create_wishlists(1)[0]
        test_product = ProductFactory()
        resp = self.client.post(
            f"{BASE_URL}/{test_wishlist.id}/products",
            json=test_product.serialize(),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        data = resp.get_json()
        logging.debug(data)
        product_id = data["id"]

        # retrieve it back
        resp = self.client.get(
            f"{BASE_URL}/{test_wishlist.id}/products/{product_id}",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        data = resp.get_json()
        logging.debug(data)
        self.assertEqual(data["wishlist_id"], test_wishlist.id)
        self.assertEqual(data["name"], test_product.name)

        # if product not exist
        resp = self.client.get(
            f"{BASE_URL}/{test_wishlist.id}/products/0",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_product(self):
        """It should update the name and quantity of a product"""
        test_wishlist = self._create_wishlists(1)[0]
        test_product = self._create_products(test_wishlist.id, 1)[0]
        info = test_product.serialize()
        info["name"] = "Test"
        info["quantity"] = 233
        resp = self.client.put(
            f"{BASE_URL}/{test_wishlist.id}/products/{test_product.id}",
            json=info,
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(test_product.name, data["name"])
        self.assertEqual(test_product.quantity, data["quantity"])

        # info not consistent
        info["wishlist_id"] = 0
        resp = self.client.put(
            f"{BASE_URL}/{test_wishlist.id}/products/{test_product.id}",
            json=info,
        )
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

    def test_update_product_not_contain(self):
        """It should update the product if not contained in given wishlist"""
        test_wishlists = self._create_wishlists(2)
        test_product = self._create_products(test_wishlists[0].id, 1)[0]
        info = test_product.serialize()
        info["name"] = "Test"
        info["quantity"] = 233
        resp = self.client.put(
            f"{BASE_URL}/{test_wishlists[1].id}/products/{test_product.id}",
            json=info,
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_product_not_exist(self):
        """It should update the product that not exist"""
        test_wishlists = self._create_wishlists(1)
        test_product = self._create_products(test_wishlists[0].id, 1)[0]
        info = test_product.serialize()
        info["name"] = "Test"
        info["quantity"] = 233
        resp = self.client.put(
            f"{BASE_URL}/{test_wishlists[0].id}/products/0",
            json=info,
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_product_wishlist_not_exist(self):
        """It should update the product that wishlist not exist"""
        test_wishlists = self._create_wishlists(1)
        test_product = self._create_products(test_wishlists[0].id, 1)[0]
        info = test_product.serialize()
        info["name"] = "Test"
        info["quantity"] = 233
        resp = self.client.put(
            f"{BASE_URL}/0/products/{test_product.id}",
            json=info,
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

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

    def test_list_wishlist_without_owner(self):
        """It should Get a list of wishlists"""
        self._create_wishlists(5)
        resp = self.client.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_list_wishlist_by_owner(self):
        """It should Get an wishlist by Owner"""
        wishlists = self._create_wishlists(3)
        resp = self.client.get(BASE_URL, query_string=f"owner={wishlists[1].owner}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data[0]["owner"], wishlists[1].owner)

    def test_list_wishlist_by_name(self):
        """It should Get an wishlist by Name"""
        wishlists = self._create_wishlists(3)
        resp = self.client.get(BASE_URL, query_string=f"name={wishlists[1].name}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data[0]["name"], wishlists[1].name)

    def test_list_wishlist_with_date_filter(self):
        """It should return filtered wishlists"""
        wishlists = self._create_wishlists(3)
        wishlists[0].date_joined = date(2000, 1, 1)
        wishlists[1].date_joined = date(2001, 1, 1)
        wishlists[2].date_joined = date(2002, 1, 1)
        wishlists[0].update()

        resp = self.client.get(f"{BASE_URL}?start=2000-12-30&end=2001-12-30")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data[0]["id"], wishlists[1].id)

        resp = self.client.get(f"{BASE_URL}?start=2000-12-30")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data[0]["id"], wishlists[1].id)
        self.assertEqual(data[1]["id"], wishlists[2].id)

        resp = self.client.get(f"{BASE_URL}?end=2001-12-30")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data[0]["id"], wishlists[0].id)
        self.assertEqual(data[1]["id"], wishlists[1].id)

    # def test_update_wishlist_by_name(self):
    #     """It should Update an existing Wishlist"""
    #     # create an Wishlist to update
    #     test_wishlist = WishlistFactory()
    #     resp = self.client.post(BASE_URL, json=test_wishlist.serialize())
    #     self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    #     # update the pet
    #     new_wishlist = resp.get_json()
    #     new_name = "Happy-Happy Joy-Joy"
    #     new_wishlist["name"] = "Happy-Happy Joy-Joy"
    #     new_wishlist_id = new_wishlist["id"]
    #     resp = self.client.put(
    #         f"{BASE_URL}/{new_wishlist_id}/{new_name}", json=new_wishlist
    #     )
    #     self.assertEqual(resp.status_code, status.HTTP_200_OK)
    #     updated_wishlist = resp.get_json()
    #     self.assertEqual(updated_wishlist["name"], "Happy-Happy Joy-Joy")
    def test_update_wishlist(self):
        """It should Update an existing Wishlist"""
        # create an Wishlist to update
        test_wishlist = WishlistFactory()
        resp = self.client.post(
            BASE_URL, 
            json=test_wishlist.serialize(),
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the pet
        new_wishlist = resp.get_json()
        new_wishlist["name"] = "nyu-wishlist"
        new_wishlist_id = new_wishlist["id"]
        resp = self.client.put(f"{BASE_URL}/{new_wishlist_id}", json=new_wishlist)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_wishlist = resp.get_json()
        self.assertEqual(updated_wishlist["name"], "nyu-wishlist")

        resp = self.client.put(f"{BASE_URL}/0", json=new_wishlist)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_copy_a_wishlist(self):
        """It should copy an existing Wishlist"""
        wishlists = self._create_wishlists(1)
        old_wishlist = wishlists[0]
        self._create_products(old_wishlist.id, 2)

        resp = self.client.post(f"{BASE_URL}/{old_wishlist.id}/copy")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        new_id = data["id"]
        # now get the new list
        resp = self.client.get(f"{BASE_URL}/{new_id}")
        data = resp.get_json()

        self.assertNotEqual(data["id"], old_wishlist.id)
        self.assertEqual(data["name"], old_wishlist.name + " COPY")
        self.assertEqual(len(data["products"]), 2)

        # if old wishlist does not exist
        resp = self.client.post(f"{BASE_URL}/0/copy")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    ######################################################################
    #  E R R O R    H A N D L E R   T E S T
    ######################################################################
    def test_bad_request(self):
        """It should not Create when sending the wrong data"""
        resp = self.client.post(
            BASE_URL, 
            json={"name": "not enough data"},
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsupported_media_type(self):
        """It should not Create when sending wrong media type"""
        wishlist = WishlistFactory()
        resp = self.client.post(
            BASE_URL, 
            json=wishlist.serialize(), 
            content_type="test/html",
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_method_not_allowed(self):
        """It should not allow an illegal method call"""
        resp = self.client.put(BASE_URL, json={"not": "today"})
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
