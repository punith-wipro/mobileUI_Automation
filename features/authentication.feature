Feature: Basic shopping app access
  As a shopper
  I want to sign in and manage a cart
  So that I can reach the products safely

  @smoke @regression
  Scenario: A valid user can sign in
    Given the app is on the login screen
    When I sign in with username "standard_user" and password "secret_sauce"
    Then the products screen is displayed

  @regression
  Scenario: Invalid credentials are rejected
    Given the app is on the login screen
    When I sign in with username "not_a_user" and password "wrong_password"
    Then a login error is displayed

  @smoke @regression
  Scenario: A signed-in user can log out
    Given the app is on the login screen
    When I sign in with username "standard_user" and password "secret_sauce"
    And I log out
    Then the app returns to the login screen

  @regression
  Scenario: A user can add a product to the cart
    Given the app is on the login screen
    When I sign in with username "standard_user" and password "secret_sauce"
    And I add the first product to the cart
    Then the first product can be removed from the cart
