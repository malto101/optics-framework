# filepath: tests/features/project/variable_resolution.feature
Feature: Project Variable Resolution
    As the test runner, I need to correctly resolve variables defined in element files
    when processing keywords and their parameters.

    Background:
    Given a test execution context for a project
    And an "elements.csv" file in the project with content:
        """
        Element_Name,Element_ID,Selector_Type
        login_button,com.example:id/login,id
        username_field,user_xpath,xpath
        api_key,ABC123XYZ,variable
        """

    Scenario: Successfully resolve an element variable
    When a keyword parameter is "${login_button}"
    Then the resolved value should be "com.example:id/login"

    Scenario: Attempt to resolve a non-existent variable
    When a keyword parameter is "${non_existent_var}"
    Then resolving the parameter should raise a "ValueError" or "VariableNotFound" error

    Scenario: Handle parameter that is not a variable
    When a keyword parameter is "literal_value"
    Then the resolved value should be "literal_value"

    Scenario: Handle malformed variable syntax
    When a keyword parameter is "${malformed_var"
    Then the resolved value should be "${malformed_var" # Or specific error handling
