# filepath: tests/features/keyword_listing.feature
Feature: Keyword Listing
  The optics CLI should allow users to list available keywords.

  Scenario: List all available keywords
    When I run "optics list"
    Then the command should succeed
    And the output should contain "Available Keywords"
    And the output should contain "AppManagement" # Example category
    And the output should contain "Launch App"    # Example keyword
    And the output should contain "ActionKeyword"
    And the output should contain "Press Element"
    And the output should contain "Verifier"
    And the output should contain "Assert Presence"
    And the output should not contain any word that starts with "_"

  Scenario: List keywords with a specific category
    When I run "optics list --category AppManagement"
    Then the command should succeed
    And the output should contain "Available Keywords"
    And the output should contain "AppManagement"
    And the output should contain "Launch App"
    And the output should not contain "ActionKeyword"
    And the output should not contain "Verifier"

  Scenario: List keywords with a specific keyword name failure
    When I run "optics list --keyword NonExistentKeyword"
    Then the command should fail
    And the output should contain "No keywords found matching 'NonExistentKeyword'"
    And the exit code should be non-zero
