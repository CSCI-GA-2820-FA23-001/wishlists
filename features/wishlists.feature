Feature: The wishlists service back-end
    As a Wishlists Service Owner
    I need a RESTful catalog service
    So that I can keep track of all my wishlists and items in them

Background:
    Given the following wishlists
        | name      | user_name |
        | wish_1    | user_3    | 
        | wish_2    | user_3    | 
        | wish_3    | user_4    |
        | wish_4    | user_5    |

    Given the following wishlist items
        | name      | wishlist_id | product_id | quantity|
        | item_1    | wish_1    | 3 | 5 | 
        | item_2    | wish_1    | 4 | 2 | 
        | item_3    | wish_2    | 5 | 3 | 
        | item_4    | wish_4    | 6 | 1 | 

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Wishlists Demo REST API Service" in the title
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