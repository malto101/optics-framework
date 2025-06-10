# filepath: tests/features/framework_info.feature
Feature: Framework Information
    The optics CLI should provide information about the framework.

    Scenario: Display framework version
        When I run "optics version"
        Then the command should succeed
        And the output should match the version pattern "\d+\.\d+\.\d+"
        And the output should contain the current framework version
