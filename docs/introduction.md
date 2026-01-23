# :material-information: Introduction

**Optics Framework** is a powerful, extensible no-code test automation framework designed for **vision-powered**, **data-driven testing** and **production app synthetic monitoring**. It enables seamless integration with intrusive action & detection drivers such as Appium / WebDriver as well as non-intrusive action drivers such as BLE mouse / keyboard and detection drivers such as video capture card and external web cams.

## :material-target: Primary Use Cases

This framework was designed primarily for the following use cases:

1. **Production App Monitoring** :material-shield-check:
   Where access to USB debugging / developer mode and device screenshots is prohibited

2. **Resilient Self-Healing Test Automation** :material-auto-fix:
   That rely on more than one element identifier and multiple fallbacks to ensure maximum recovery

3. **Enable Non-Coders to Build Test Automation Scripts** :material-code-braces:
   No programming knowledge required to create and execute tests

## :material-check-circle: Supported Platforms

- :material-cellphone: **iOS** - Native iOS app testing
- :material-android: **Android** - Native Android app testing
- :material-web: **Browsers** - Web application testing
- :material-television: **Smart TVs** - BLE-enabled device testing

## :material-puzzle: Key Features

### :material-eye-outline: Vision Powered Detections

UI object detections are powered by computer vision and not just on XPath elements. This makes tests more resilient to UI changes.

### :material-code-braces: No Code Automation

No knowledge of programming languages or access to IDE needed to build automation scripts. Define tests using simple CSV files.

### :material-bluetooth: Non-Intrusive Action Drivers

Non-intrusive action drivers such as BLE mouse and keyboard are supported, enabling testing of production apps without developer mode.

### :material-database: Data-Driven Testing (DDT)

Execute test cases dynamically with multiple datasets, enabling parameterized testing and iterative execution.

### :material-puzzle: Extensible & Scalable

Easily add new keywords and modules without any hassle. The modular architecture allows for easy extension.

### :material-robot: AI Integration

Choose which AI models to use for object recognition and OCR. Support for multiple vision models and OCR engines.

### :material-auto-fix: Self-Healing Capability

Configure multiple drivers, screen capture methods, and detection techniques with priority-based execution. If a primary method fails, the system automatically switches to the next available method in the defined hierarchy.

## :material-cog: Architecture

Optics Framework offers a modular architecture paired with a command-line interface (CLI) that enables testers and developers to:

- Define test cases using CSV files
- Manage test data efficiently
- Execute tests with ease
- Extend functionality through plugins

## :material-school: Who Can Use It?

Whether you're:

- :material-account-circle: A **beginner** looking to automate your first test
- :material-account-tie: An **experienced developer** contributing new features
- :material-account-group: A **QA engineer** building comprehensive test suites
- :material-account-hard-hat: A **DevOps engineer** setting up CI/CD pipelines

The Optics Framework is designed to empower you.

## :material-file-document: License

The Optics Framework is licensed under the **Apache License 2.0**, which can be found [here](https://www.apache.org/licenses/LICENSE-2.0). This permissive license allows you to use, modify, and distribute the software freely, as long as you comply with its terms.

!!! info "License Key Points"

    - Redistributions of the code must include a copy of the license and any relevant notices
    - If you modify the code, you should also document your changes
    - The software is provided "as is" without any warranties
    - You can use, modify, distribute, and even sublicense the software with minimal restrictions

## :material-arrow-right: Next Steps

Ready to get started? Check out our [Quick Start Guide](quickstart.md) to create your first test in minutes!
