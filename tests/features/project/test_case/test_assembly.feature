# filepath: tests/features/project/test_assembly.feature
Feature: Project Test Assembly and Filtering
    As the framework, I need to correctly filter test cases based on configuration
    and assemble them into an executable structure.

    Background:
        Given a temporary project directory
        And a "modules.csv" file exists in the project directory defining "MOD_A", "MOD_B", "MOD_C"
        And an "elements.csv" file exists in the project directory

    Scenario: Include specific test cases from config
        Given a "config.yaml" file in the project directory with:
        """
        include:
            - TC001
            - TC003
        # other necessary config...
        driver_sources: [{'appium': {'enabled': True}}]
        elements_sources: [{'appium_find_element': {'enabled': True}}]
        """
        And a "test_cases.csv" file in the project directory with:
        """
        test_case,test_step
        TC001,MOD_A
        TC002,MOD_B
        TC003,MOD_C
        """
        When the project's test execution queue is built
        Then the execution queue should contain "TC001"
        And the execution queue should not contain "TC002"
        And the execution queue should contain "TC003"

    Scenario: Exclude specific test cases from config
        Given a "config.yaml" file in the project directory with:
        """
        exclude:
            - TC002
        # other necessary config...
        driver_sources: [{'appium': {'enabled': True}}]
        elements_sources: [{'appium_find_element': {'enabled': True}}]
        """
        And a "test_cases.csv" file in the project directory with:
        """
        test_case,test_step
        TC001,MOD_A
        TC002,MOD_B
        TC003,MOD_C
        """
        When the project's test execution queue is built
        Then the execution queue should contain "TC001"
        And the execution queue should not contain "TC002"
        And the execution queue should contain "TC003"

    Scenario: Build correct linked list structure for test execution
        Given a "config.yaml" file in the project directory with minimal valid settings
        And a "test_cases.csv" file in the project directory with:
        """
        test_case,test_step
        TC_Main,MOD_Main
        """
        And a "modules.csv" file in the project directory with:
        """
        module_name,module_step,param_1,param_2
        MOD_Main,Keyword1,elem1,,
        MOD_Main,Keyword2,elem2,val2,arg2
        """
        When the project's test execution queue is built for "TC_Main"
        Then the "TC_Main" node in the queue should exist
        And its first module should be "MOD_Main"
        And the "MOD_Main" node should have "Keyword1" followed by "Keyword2"
        And "Keyword1" should reference "elem1"
        And "Keyword2" should reference "elem2" with value "val2" and args "arg2"
