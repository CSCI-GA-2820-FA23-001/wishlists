# Copyright 2016, 2019 John J. Rofrano. All Rights Reserved.
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

"""
Test Factory to make fake objects for testing
"""
from datetime import date
import factory
from factory.fuzzy import FuzzyChoice, FuzzyDate
from service.models import Wishlist, Product


class WishlistFactory(factory.Factory):
    """Creates fake Wishlists"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Persistent class"""

        model = Wishlist

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("name")
    date_joined = FuzzyDate(date(2008, 1, 1))

    @factory.post_generation
    def addresses(
        self, create, extracted, **kwargs
    ):  # pylint: disable=method-hidden, unused-argument
        """Creates the addresses list"""
        if not create:
            return

        if extracted:
            self.addresses = extracted


class ProductFactory(factory.Factory):
    """Creates fake Products"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Persistent class"""

        model = Product

    id = factory.Sequence(lambda n: n)
    wishlist_id = None
    name = FuzzyChoice(choices=["home", "work", "other"])
    wishlist = factory.SubFactory(WishlistFactory)
