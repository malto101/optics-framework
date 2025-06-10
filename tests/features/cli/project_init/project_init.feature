# filepath: tests/features/project_initialization.feature
Feature: Project Initialization
    The optics CLI should allow users to initialize new projects.

    Scenario: Initialize a new project with default settings
        When I run "optics init --name my_test_project" in a temporary directory
        Then the command should succeed
        And a directory named "my_test_project" should exist
        And the directory "my_test_project" should contain a "config.yaml" file
        And the directory "my_test_project" should contain a "test_cases.csv" file
        And the directory "my_test_project" should contain a "modules.csv" file
        And the directory "my_test_project" should contain a "elements.csv" file

    Scenario: Initialize a new project with a specific template
        When I run "optics init --name my_youtube_project --template youtube" in a temporary directory
        Then the command should succeed
        And a directory named "my_youtube_project" should exist
        And the directory "my_youtube_project" should contain files from the "youtube" template

    Scenario: Initialize a new project with git initialized
        When I run "optics init --name my_git_project --git-init" in a temporary directory
        Then the command should succeed
        And a directory named "my_git_project" should exist
        And the directory "my_git_project" should be a git repository

    Scenario: Attempt to initialize an existing project without force
        Given a project named "existing_project" already exists in a temporary directory
        When I run "optics init --name existing_project" in that temporary directory
        Then the command should fail or report an error
        And the directory "existing_project" should remain unchanged by this command

    Scenario: Initialize an existing project with force
        Given a project named "forced_project" already exists with some content in a temporary directory
        When I run "optics init --name forced_project --force" in that temporary directory
        Then the command should succeed
        And the directory "forced_project" should be re-initialized
