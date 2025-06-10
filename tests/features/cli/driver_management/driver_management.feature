# filepath: tests/features/driver_management.feature
Feature: Driver Management
    The optics CLI should allow users to list and install drivers.

    Scenario: List available drivers
        When I run "optics setup --list"
        Then the command should succeed
        And the output should contain "Available Drivers"
        And the output should contain "Action Drivers"
        And the output should contain "Appium"
        And the output should contain "Text Drivers"
        And the output should contain "EasyOCR"

    Scenario: Install a specific driver (mocked installation)
        When I run "optics setup --install Appium"
        Then the command should succeed
        And the output should indicate "Appium" driver installation was attempted or successful
        # Actual installation is hard to verify in a unit/integration test without external dependencies
        # and permissions. We'd typically mock the subprocess call for 'pip install'.

    Scenario: Install a driver that does not exist
        When I run "optics setup --install NonExistentDriver"
        Then the command should fail
        And the output should contain "Driver 'NonExistentDriver' not found"
        And the exit code should be non-zero
