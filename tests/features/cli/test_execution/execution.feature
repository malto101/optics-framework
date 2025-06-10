# filepath: tests/features/test_execution.feature
Feature: Test Execution
    The optics CLI should allow users to execute tests and perform dry runs.
    (These scenarios assume a minimal valid project structure exists)

    Scenario: Perform a dry run of a valid project
        Given a minimal valid optics project exists at "sample_project_for_dry_run"
        When I run "optics dry_run sample_project_for_dry_run"
        Then the command should succeed
        And the output should indicate a dry run was performed

    Scenario: Execute tests for a valid project (mocked execution)
        Given a minimal valid optics project exists at "sample_project_for_execution"
        When I run "optics execute sample_project_for_execution"
        Then the command should succeed
        And the output should indicate tests were executed
        # Actual test execution would involve Appium, etc. and is complex for this scope.
        # We'd focus on the CLI invoking the execution engine.

    Scenario: Attempt to execute tests for a non-existent project
        When I run "optics execute non_existent_project"
        Then the command should fail
        And the output should indicate the project does not exist

    Scenario: Attempt to perform a dry run on a non-existent project
        When I run "optics dry_run non_existent_project"
        Then the command should fail
        And the output should indicate the project does not exist

    Scenario: Perform a dry run with an invalid project structure
        Given an invalid optics project structure exists at "invalid_project_structure"
        When I run "optics dry_run invalid_project_structure"
        Then the command should fail
        And the output should indicate the project structure is invalid
