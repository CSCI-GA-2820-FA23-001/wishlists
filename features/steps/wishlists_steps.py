######################################################################
# Copyright 2016, 2021 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Wishlist Steps

Steps file for Wishlists.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import requests
from behave import given
from compare import expect


@given("the following wishlists")
def step_impl(context):
    """Delete all Wishlists and load new ones"""
    # List all of the wishlists and delete them one by one
    headers = {"X-Api-Key": context.API_KEY}
    rest_endpoint = f"{context.BASE_URL}/api/wishlists"
    context.resp = requests.get(rest_endpoint)
    expect(context.resp.status_code).to_equal(200)
    for wishlist in context.resp.json():
        context.resp = requests.delete(
            f"{rest_endpoint}/{wishlist['id']}",
            headers=headers,
        )
        expect(context.resp.status_code).to_equal(204)

    # load the database with new wishlists
    for row in context.table:
        payload = {
            "name": row["name"],
            "owner": row["user_name"],
            "date_joined": row["date"],
            "products": [],
        }
        context.resp = requests.post(
            rest_endpoint, 
            json=payload,
            headers=headers,
        )
        expect(context.resp.status_code).to_equal(201)


@given("the following wishlist items")
def step_impl(context):
    """Load new wishlist items, delete wishlists already deleted all items"""
    # List all of the wishlist items and delete them one by one
    # load the database with new wishlist items
    headers = {"X-Api-Key": context.API_KEY}
    for row in context.table:
        wishlist_name = row["wishlist_name"]
        queryString = "name=" + wishlist_name
        rest_endpoint = f"{context.BASE_URL}/api/wishlists?{queryString}"
        context.resp = requests.get(rest_endpoint)
        print(context.resp.json())
        wishlist_id = context.resp.json()[0]["id"]
        # print(wishlist_id)
        payload = {
            "name": row["name"],
            "wishlist_id": wishlist_id,
            "quantity": int(row["quantity"]),
        }
        endpoint = f"{context.BASE_URL}/api/wishlists/{wishlist_id}/products"
        print(endpoint)
        context.resp = requests.post(
            endpoint, 
            json=payload,
            headers=headers,
        )
        print(context.resp.json())
        expect(context.resp.status_code).to_equal(201)
