# Configuration Guide

This document explains the configuration system for the framework.
Configurations are typically written in **YAML** and loaded into the framework using the `Config` model.

The system is **modular**: each functional area (drivers, element sources, text detection, image detection) is defined as a **list of dependencies with fallback priority**.

- **Priority:** The **first enabled dependency** in the list is attempted (`index 0`).
- **Fallback:** If that dependency fails, the framework will automatically attempt the next enabled dependency (`index 1`), and so on.

---

## Top-Level Structure

```yaml
console: true
driver_sources: [...]
elements_sources: [...]
text_detection: [...]
image_detection: [...]
file_log: false
json_log: true
json_path: ./logs/execution.json
log_level: INFO
log_path: ./logs/execution.log
project_path: ./tests/project
execution_output_path: ./output
include: [TC_001, TC_002]
exclude: [TC_999]
event_attributes_json: ./configs/event_attributes.json
halt_duration: 0.1
max_attempts: 3
```

---

## Dependency Configurations

All dependency definitions follow a common structure:

```yaml
- dependency_name:
    enabled: true | false
    url: "http://example.com"          # Optional, depends on dependency
    capabilities:                      # Optional, depends on dependency
      key1: value1
      key2: value2
```

### 1. `driver_sources`

Drivers control how tests interact with devices, browsers, or other systems.
Each entry represents a possible driver backend.

#### Example: Appium + Selenium

```yaml
driver_sources:
  - appium:
      enabled: true
      url: "http://localhost:4723"
      capabilities:
        platformName: Android
        deviceName: emulator-5554
        automationName: UiAutomator2
        appPackage: com.google.android.contacts
        appActivity: com.android.contacts.activities.PeopleActivity
  - selenium:
      enabled: false
      url: "http://localhost:4444/wd/hub"
      capabilities:
        browserName: chrome
        headless: true
```

- **url:** Remote server endpoint.
- **capabilities:** Driver-specific settings (e.g., [Appium Desired Capabilities](https://appium.io/docs/en/2.0/reference/caps/)).
- **priority:** Appium will be tried first. If disabled or fails, Selenium will be attempted.

---

### 2. `elements_sources`

Defines how elements are located during test execution.
Each source is a strategy for identifying elements.

#### Example

```yaml
elements_sources:
  - appium_find_element:
      enabled: true
  - appium_page_source:
      enabled: false
  - appium_screenshot:
      enabled: true
```

- **appium_find_element:** Uses Appium’s native find element API.
- **appium_page_source:** Uses parsed page source for lookup.
- **appium_screenshot:** Uses image-based matching on screenshots.

---

### 3. `text_detection`

Controls OCR/text recognition backends.
These are tried in order until one succeeds.

#### Example

```yaml
text_detection:
  - easyocr:
      enabled: true
  - tesseract:
      enabled: false
  - google-vision:
      enabled: false
```

- **easyocr:** Uses EasyOCR for text detection in screenshots.
- **tesseract:** Uses Tesseract OCR.
- **placeholder_future_ocr:** Reserved for future integrations.

---

### 4. `image_detection`

Controls computer vision/image matching backends.

#### Example

```yaml
image_detection:
  - templatematch:
      enabled: true
  - opencv_match:
      enabled: false
```

- **templatematch:** Uses template matching for locating UI components.
- **opencv_match:** Uses OpenCV feature matching.

---

## Logging

Logging is highly configurable:

```yaml
console: true
file_log: true
json_log: true
json_path: ./logs/results.json
log_level: INFO
log_path: ./logs/results.log
```

- **console:** Print logs to stdout.
- **file_log:** Write human-readable logs to `log_path`.
- **json_log:** Write structured JSON logs to `json_path`.
- **log_level:** Standard Python logging levels (`DEBUG`, `INFO`, `WARNING`, `ERROR`).

---

## Project Paths

```yaml
project_path: ./tests/project
execution_output_path: ./output
```

- **project_path:** Path to test artifacts and scripts.
- **execution_output_path:** Path where execution results (logs, screenshots, reports) will be stored.

---

## Filtering Test Execution

You can control which tests run using `include` and `exclude`.

```yaml
include:
  - smoke_tests.yaml
  - regression_suite.yaml
exclude:
  - experimental_features.yaml
```

- **include:** Only the listed tests will be executed.
- **exclude:** Exclude these tests even if included elsewhere.

---

## Event Attributes

```yaml
event_attributes_json: ./configs/event_attributes.json
```

- Points to a JSON file defining **custom event attributes** to be injected at runtime.
- Example `event_attributes.json`:

```json
{
  "env": "staging",
  "build_id": "2025.09.20",
  "run_by": "ci_pipeline"
}
```

---

## Retry & Stability Controls

```yaml
halt_duration: 0.1
max_attempts: 3
```

- **halt_duration:** Wait time (in seconds) before retrying after a failure.
- **max_attempts:** Maximum number of retries before failing an action.

---

## Best Practices

1. **Order matters** – place your most reliable driver/element/text/image source first.
2. **Use fallbacks wisely** – disable unused integrations to reduce startup time.
3. **Separate environments** – maintain different config files for `dev`, `staging`, and `production`.
4. **Structured logging** – enable `json_log` for CI/CD pipelines.
5. **Event attributes** – inject metadata like build IDs for traceability.

---

## Reference Table

| Field                   | Type                  | Description                                                                 |
|--------------------------|-----------------------|-----------------------------------------------------------------------------|
| `console`                | `bool`               | Enable/disable console logging.                                             |
| `driver_sources`         | `List[Dependency]`   | List of drivers with priority/fallback.                                     |
| `elements_sources`       | `List[Dependency]`   | List of element locator strategies.                                         |
| `text_detection`         | `List[Dependency]`   | OCR backends with fallback.                                                 |
| `image_detection`        | `List[Dependency]`   | Image detection backends with fallback.                                     |
| `file_log`               | `bool`               | Enable/disable file logging.                                                |
| `json_log`               | `bool`               | Enable/disable structured JSON logging.                                     |
| `json_path`              | `str \| null`        | Path to JSON log file (required if `json_log=true`).                        |
| `log_level`              | `str`                | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`).                        |
| `log_path`               | `str \| null`        | Path to text log file (required if `file_log=true`).                        |
| `project_path`           | `str \| null`        | Path to test artifacts and scripts.                                         |
| `execution_output_path`  | `str \| null`        | Path where execution results will be stored.                                |
| `include`                | `List[str] \| null`  | Only include these test files/cases.                                        |
| `exclude`                | `List[str] \| null`  | Exclude these test files/cases.                                             |
| `event_attributes_json`  | `str \| null`        | Path to JSON file with custom event attributes.                             |
| `halt_duration`          | `float`              | Wait duration (in seconds) before retrying.                                 |
| `max_attempts`           | `int`                | Maximum number of retries for an action.                                    |

---
