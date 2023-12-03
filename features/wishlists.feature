Feature: The wishlists service back-end
    As a Wishlists Service Owner
    I need a RESTful catalog service
    So that I can keep track of all my wishlists and items in them

    Background:
        Given the following wishlists
            | name   | user_name | date       |
            | wish_1 | user_3    | 2023-11-30 |
            | wish_2 | user_3    | 2022-11-30 |
            | wish_3 | user_4    | 2022-11-30 |
            | wish_4 | user_5    | 2021-11-30 |

        Given the following wishlist items
            | name   | wishlist_name | quantity |
            | item_1 | wish_1        | 5        |
            | item_2 | wish_1        | 2        |
            | item_3 | wish_2        | 3        |
            | item_4 | wish_4        | 1        |

    Scenario: The server is running
        When I visit the "Home Page"
        Then I should see "Wishlists RESTful Service" in the title
        And I should not see "404 Not Found"

    Scenario: Create a Wishlist
        When I visit the "Home Page"
        And I set the "Wishlist Name" to "wish_5"
        And I set the "User Name" to "5"
        And I press the "Create" button
        Then I should see the message "Success"
        When I copy the "Wishlist Id" field
        And I press the "Clear" button
        Then the "Wishlist Id" field should be empty
        And the "Wishlist Name" field should be empty
        And the "User Name" field should be empty
        When I paste the "Wishlist Id" field
        And I press the "Retrieve" button
        Then I should see the message "Success"
        And I should see "wish_5" in the "Wishlist Name" field
        And I should see "5" in the "User Name" field

    Scenario: Read a wishlist
        When I visit the "Home Page"
        And I set the "Wishlist Name" to "wish_1"
        And I press the "Search" button
        Then I should see the message "Success"
        When I copy the "Wishlist ID" field
        And I press the "Clear" button
        And I paste the "Wishlist ID" field
        And I press the "Retrieve" button
        Then I should see the message "Success"
        And I should see "wish_1" in the "Wishlist Name" field
        And I should see "user_3" in the "User Name" field

    Scenario: Delete a wishlist
        When I visit the "home page"
        And I press the "List" button
        And I copy the "first cell of wishlist table" field
        And I paste the "Wishlist ID" field
        And I press the "Delete" button
        Then I should see the message "Wishlist has been Deleted!"
        When I press the "List" button
        Then I should see the message "Success"
        And I should not see "wish_1" in the wishlist results
        And I should see "wish_2" in the wishlist results
        And I should see "wish_3" in the wishlist results
        And I should see "wish_4" in the wishlist results

    Scenario: Get all wishlists
        When I visit the "Home Page"
        And I press the "List" button
        Then I should see the message "Success"
        And I should see "wish_1" in the wishlist results
        And I should see "wish_2" in the wishlist results
        And I should see "wish_3" in the wishlist results
        And I should see "wish_4" in the wishlist results

    Scenario:  List all Wishlists Items in a Wishlist
        When I visit the "Home Page"
        And I set the "Wishlist Name" to "wish_1"
        And I press the "Search" button
        Then I should see the message "Success"
        When I copy the "Wishlist ID" field
        And I press the "Clear" button
        And I paste the "Product Wishlist Id" field
        And I press the "product-list" button
        Then I should see the message "Products retrieved successfully"
        And I should see "item_1" in the product results
        And I should see "item_2" in the product results
        And I should not see "item_3" in the product results


    Scenario:  Delete a product by name
        When I visit the "Home Page"
        And I set the "Wishlist Name" to "wish_12"
        And I press the "create" button
        Then I should see the message "Success"
        When I copy the "Wishlist ID" field
        And I press the "Clear" button
        And I paste the "Product Wishlist Id" field
        And I set the "Product Name" to "item_11"
        And I set the "Product Quantity" to "11"
        And I press the "product-create" button
        Then I should see the message "Product create Success"
        When I copy the "Product Id" field
        And I paste the "Product Id" field
        And I press the "product-delete" button
        Then I should see the message "Products has been Deleted!"

    Scenario: Retrieve a Product in a Wishlist
        When I visit the "home page"
        And I set the "Wishlist Name" to "wish_1"
        And I press the "Search" button
        Then I should see the message "Success"
        When I copy the "Wishlist ID" field
        And I paste the "Product Wishlist Id" field
        And I set the "Product Name" to "item_1"
        And I press the "Product Search" button
        Then I should see the message "Success"
        When I copy the "Product ID" field
        And I press the "Product Clear" button
        And I paste the "Product ID" field
        And I copy the "Wishlist ID" field
        And I paste the "Product Wishlist ID" field
        And I press the "Product Retrieve" button
        Then I should see "item_1" in the "Product Name" field
        And I should see "5" in the "Product Quantity" field


    Scenario: Copy a Wishlist
        When I visit the "Home Page"
        And I set the "Wishlist Name" to "wish_1"
        And I press the "Search" button
        Then I should see the message "Success"
        When I copy the "Wishlist ID" field
        And I press the "Clear" button
        And I paste the "Wishlist ID" field
        And I press the "Copy" button
        Then I should see the message "Success"
        When I press the "List" button
        Then I should see the message "Success"
        And I should see "wish_1 COPY" in the "Wishlist Name" field
        And I should see "user_3" in the "User Name" field
    
    Scenario: Update a Wishlist
        When I visit the "Home Page"
        And I set the "Wishlist Name" to "wish_1"
        And I press the "Search" button
        Then I should see the message "Success"
        When I copy the "Wishlist ID" field
        And I press the "Clear" button
        And I paste the "Wishlist ID" field
        And I press the "Retrieve" button
        Then I should see the message "Success"
        And I should see "wish_1" in the "Wishlist Name" field
        And I should see "user_3" in the "User Name" field
        When I set the "Wishlist Name" to "new_wish_name"
        And I set the "User Name" to "new_user"
        And I press the "Update" button
        Then I should see the message "Success" 
        When I press the "Clear" button
        And I paste the "Wishlist ID" field
        And I press the "Retrieve" button
        Then I should see the message "Success"
        And I should see "new_wish_name" in the "Wishlist Name" field
        And I should see "new_user" in the "User Name" field

    
    Scenario: Create a Product
        When I visit the "Home Page"
        And I press the "List" button
        And I copy the "first cell of wishlist table" field
        And I paste the "Product Wishlist ID" field
        And I set the "Product Name" to "item_5"
        And I set the "Product Quantity" to "5"
        And I press the "Product Create" button
        Then I should see the message "Product create Success"
        When I press the "Product List" button
        Then I should see "item_1" in the product results
        And I should see "item_2" in the product results
        And I should see "item_5" in the product results