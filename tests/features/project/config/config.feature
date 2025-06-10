# filepath: tests/features/common/configuration_handling.feature
Feature: Configuration Management
    As a developer, I want to reliably load and access configuration data
    so that the framework components can be configured correctly.

    Background:
        Given a temporary project directory for configuration files

    Scenario: Load a valid YAML configuration file
        Given a YAML file named "valid_config.yaml" exists in the temporary directory with content:
        """
        setting1: value1
        setting2:
            nested_setting: nested_value
        """
        When I load the configuration from "valid_config.yaml"
        Then the configuration should be loaded successfully
        And the configuration value for "setting1" should be "value1"
        And the configuration value for "setting2.nested_setting" should be "nested_value"

    Scenario: Attempt to load a non-existent YAML file
        When I attempt to load the configuration from "non_existent_config.yaml"
        Then loading the configuration should fail with a "FileNotFoundError" or similar error

    Scenario: Attempt to load a malformed YAML file
        Given a YAML file named "malformed_config.yaml" exists in the temporary directory with content:
        """
        setting1: value1
        setting2: value2: invalid_yaml
        """
        When I attempt to load the configuration from "malformed_config.yaml"
        Then loading the configuration should fail with a "YAMLParseError" or similar error

    Scenario: Get a configuration value with a default
        Given a YAML file named "partial_config.yaml" exists in the temporary directory with content:
        """
        present_key: present_value
        """
        And I load the configuration from "partial_config.yaml"
        When I get the configuration value for "missing_key" with default "default_value"
        Then the retrieved value should be "default_value"
        When I get the configuration value for "present_key" with default "default_value"
        Then the retrieved value should be "present_value"

    Scenario: Handle DependencyConfig objects
        Given a YAML file named "dependency_config.yaml" exists in the temporary directory with content:
        """
        drivers:
            - appium:
                enabled: true
                url: "http://localhost:4723"
                capabilities:
                    platformName: "Android"
                    deviceName: "Pixel_5"
            - template_match:
                enabled: false

        """
        And I load the configuration from "dependency_config.yaml"
        When I access the "drivers" configuration as a list of DependencyConfig objects
        Then the first dependency for "appium" should be enabled
        And its "url" attribute should be "http://localhost:4723"
        And its "capabilities.platformName" attribute should be "Android"
        And its "capabilities.deviceName" attribute should be "Pixel_5"
        When I access the second dependency for "template_match"
        Then it should be disabled
        And it should not have any capabilities defined

    Scenario: Validate configuration schema
        Given a YAML file named "schema_config.yaml" exists in the temporary directory with content:
        """
        setting1: value1
        setting2: value2
        """
        And I load the configuration from "schema_config.yaml"
        When I validate the configuration against the schema:
        """
        type: object
        properties:
            setting1:
                type: string
            setting2:
                type: string
        required: [setting1, setting2]
        """
        Then the configuration should be valid according to the schema

    Scenario: Handle missing required configuration keys
        Given a YAML file named "incomplete_config.yaml" exists in the temporary directory with content:
        """
        setting1: value1
        """
        And I load the configuration from "incomplete_config.yaml"
        When I validate the configuration against the schema:
        """
        type: object
        properties:
            setting1:
                type: string
            setting2:
                type: string
        required: [setting1, setting2]
        """
        Then the validation should fail with a "MissingRequiredKeyError" or similar error
