# Keyword Usage

This document outlines the available keywords for the Optics Framework, which can be used in the `test_modules.csv` file to define test steps. Keywords are derived from the framework's Python API, with method names converted to a space-separated format (e.g., `press_element` becomes `Press Element`). Each keyword corresponds to a specific action, verification, or control flow operation. Below, each keyword includes detailed parameter explanations to guide their usage.

## Action Keywords

These keywords handle interactions with the application, such as clicking, swiping, and text input.

- **Press Element**
  Presses a specified element on the screen.
  - **Parameters**:
    - `element`: The target to press. Can be:
      - *Text*: A string to locate via text detection (e.g., "Home", `${Home_text}`).
      - *XPath*: An XPath expression for Appium/Selenium (e.g., `//android.widget.Button[@resource-id="id"]`).
      - *Image*: A filename of an image in `input_templates/` (e.g., "home.png", `${Home_image}`).
    - `repeat` (optional, default=1): Number of times to press the element (integer).
    - `offset_x` (optional, default=0): Horizontal offset in pixels from the element's center (integer).
    - `offset_y` (optional, default=0): Vertical offset in pixels from the element's center (integer).
    - `index` (optional, default=0): Index of the element if multiple matches are found (integer, 0-based).
    - `aoi_x` (optional, default=0): X percentage of Area of Interest top-left corner (0-100, float).
    - `aoi_y` (optional, default=0): Y percentage of Area of Interest top-left corner (0-100, float).
    - `aoi_width` (optional, default=100): Width percentage of Area of Interest (0-100, float).
    - `aoi_height` (optional, default=100): Height percentage of Area of Interest (0-100, float).
    - `event_name` (optional): A string identifier for logging or triggering events (e.g., "click_home").
  - **Example**: `Press Element,${Subscriptions_text},2,10,20,0,0,0,100,100,click_event`

- **Press By Percentage**
  Presses at percentage-based coordinates on the screen.
  - **Parameters**:
    - `percent_x`: X-coordinate as a percentage of screen width (float, 0.0 to 1.0, e.g., 0.5 for 50%).
    - `percent_y`: Y-coordinate as a percentage of screen height (float, 0.0 to 1.0).
    - `repeat` (optional, default=1): Number of times to press (integer).
    - `event_name` (optional): A string identifier for the press event (e.g., "center_press").
  - **Example**: `Press By Percentage,0.5,0.5,,press_center`

- **Press By Coordinates**
  Presses at absolute coordinates on the screen.
  - **Parameters**:
    - `coor_x`: X-coordinate in pixels (integer, e.g., 500).
    - `coor_y`: Y-coordinate in pixels (integer, e.g., 800).
    - `repeat` (optional, default=1): Number of times to press (integer).
    - `event_name` (optional): A string identifier for the press event (e.g., "tap_event").
  - **Example**: `Press By Coordinates,500,800,,tap_event`


- **Detect And Press**
  Detects an element and presses it if found within a timeout.
  - **Parameters**:
    - `element`: The target to detect and press:
      - *Text*: A string (e.g., "Subscriptions").
      - *XPath*: An XPath expression (e.g., `//android.widget.TextView[@text="Home"]`).
      - *Image*: An image filename (e.g., "sub.jpeg").
    - `timeout`: Maximum time in seconds to wait for detection (integer, e.g., 10).
    - `event_name` (optional): A string identifier for the press event (e.g., "detect_click").
  - **Example**: `Detect And Press,${Subscriptions_image},10,detect_click`

- **Press Checkbox** *(Deprecated)*
  Presses a checkbox element (use `Press Element` instead).
  - **Parameters**:
    - `element`: The checkbox to press:
      - *Text*: A string (e.g., " Agree").
      - *XPath*: An XPath (e.g., `//android.widget.CheckBox`).
      - *Image*: An image filename (e.g., "checkbox.png").
    - `aoi_x` (optional, default=0): X percentage of Area of Interest top-left corner (0-100, float).
    - `aoi_y` (optional, default=0): Y percentage of Area of Interest top-left corner (0-100, float).
    - `aoi_width` (optional, default=100): Width percentage of Area of Interest (0-100, float).
    - `aoi_height` (optional, default=100): Height percentage of Area of Interest (0-100, float).
    - `event_name` (optional): A string identifier for the press event (e.g., "toggle").
  - **Example**: `Press Checkbox,${checkbox_xpath},0,0,100,100,toggle`

- **Press Radio Button** *(Deprecated)*
  Presses a radio button element (use `Press Element` instead).
  - **Parameters**:
    - `element`: The radio button to press:
      - *Text*: A string (e.g., "Option 1").
      - *XPath*: An XPath (e.g., `//android.widget.RadioButton`).
      - *Image*: An image filename (e.g., "radio.png").
    - `aoi_x` (optional, default=0): X percentage of Area of Interest top-left corner (0-100, float).
    - `aoi_y` (optional, default=0): Y percentage of Area of Interest top-left corner (0-100, float).
    - `aoi_width` (optional, default=100): Width percentage of Area of Interest (0-100, float).
    - `aoi_height` (optional, default=100): Height percentage of Area of Interest (0-100, float).
    - `event_name` (optional): A string identifier for the press event (e.g., "select").
  - **Example**: `Press Radio Button,${radio_xpath},0,0,100,100,select`

- **Select Dropdown Option**
  Selects an option from a dropdown (currently unimplemented).
  - **Parameters**:
    - `element`: The dropdown element:
      - *Text*: A string (e.g., "Dropdown").
      - *XPath*: An XPath (e.g., `//android.widget.Spinner`).
      - *Image*: An image filename (e.g., "dropdown.png").
    - `option`: The option to select (string, e.g., "Option 1").
    - `event_name` (optional): A string identifier for the selection event (e.g., "select_option").
  - **Example**: `Select Dropdown Option,${dropdown_xpath},Option 1,select_option`

- **Swipe**
  Performs a swipe action from specified coordinates in a direction.
  - **Parameters**:
    - `coor_x`: Starting X-coordinate in pixels (integer, e.g., 300).
    - `coor_y`: Starting Y-coordinate in pixels (integer, e.g., 400).
    - `direction` (optional, default="right"): Swipe direction ("up", "down", "left", "right").
    - `swipe_length` (optional, default=50): Distance of the swipe in pixels (integer).
    - `event_name` (optional): A string identifier for the swipe event (e.g., "swipe_up").
  - **Example**: `Swipe,300,400,up,100,swipe_up`

- **Swipe Seekbar To Right Android** *(Deprecated)*
  Swipes a seekbar to the right (Android-specific).
  - **Parameters**:
    - `element`: The seekbar element:
      - *Text*: A string (e.g., "Volume").
      - *XPath*: An XPath (e.g., `//android.widget.SeekBar`).
      - *Image*: An image filename (e.g., "seekbar.png").
    - `event_name` (optional): A string identifier for the swipe event (e.g., "adjust").
  - **Example**: `Swipe Seekbar To Right Android,${seekbar_xpath},adjust`

- **Swipe Until Element Appears**
  Swipes in a direction until an element appears or timeout is reached.
  - **Parameters**:
    - `element`: The target element:
      - *Text*: A string (e.g., "Home").
      - *XPath*: An XPath (e.g., `//android.widget.TextView[@text="Home"]`).
      - *Image*: An image filename (e.g., "home.png").
    - `direction`: Swipe direction ("up", "down", "left", "right").
    - `timeout`: Maximum time in seconds to swipe (integer, e.g., 15).
    - `event_name` (optional): A string identifier for the swipe event (e.g., "scroll_to_home").
  - **Example**: `Swipe Until Element Appears,${Home_image},down,15,scroll_to_home`

- **Swipe From Element**
  Swipes starting from a specified element.
  - **Parameters**:
    - `element`: The starting element:
      - *Text*: A string (e.g., "Subscriptions").
      - *XPath*: An XPath (e.g., `//android.widget.TextView[@text="Subscriptions"]`).
      - *Image*: An image filename (e.g., "sub.jpeg").
    - `direction`: Swipe direction ("up", "down", "left", "right").
    - `swipe_length`: Distance of the swipe in pixels (integer, e.g., 50).
    - `aoi_x` (optional, default=0): X percentage of Area of Interest top-left corner (0-100, float).
    - `aoi_y` (optional, default=0): Y percentage of Area of Interest top-left corner (0-100, float).
    - `aoi_width` (optional, default=100): Width percentage of Area of Interest (0-100, float).
    - `aoi_height` (optional, default=100): Height percentage of Area of Interest (0-100, float).
    - `event_name` (optional): A string identifier for the swipe event (e.g., "swipe_left").
  - **Example**: `Swipe From Element,${Subscriptions_text},left,50,0,0,100,100,swipe_left`

- **Scroll**
  Performs a scroll action in a specified direction.
  - **Parameters**:
    - `direction`: Scroll direction ("up", "down", "left", "right").
    - `event_name` (optional): A string identifier for the scroll event (e.g., "scroll_down").
  - **Example**: `Scroll,down,scroll_down`

- **Scroll Until Element Appears**
  Scrolls in a direction until an element appears or timeout is reached.
  - **Parameters**:
    - `element`: The target element:
      - *Text*: A string (e.g., "Home").
      - *XPath*: An XPath (e.g., `//android.widget.TextView[@text="Home"]`).
      - *Image*: An image filename (e.g., "home.png").
    - `direction`: Scroll direction ("up", "down", "left", "right").
    - `timeout`: Maximum time in seconds to scroll (integer, e.g., 20).
    - `event_name` (optional): A string identifier for the scroll event (e.g., "scroll_to_top").
  - **Example**: `Scroll Until Element Appears,${Home_xpath},up,20,scroll_to_top`

- **Scroll From Element**
  Scrolls starting from a specified element.
  - **Parameters**:
    - `element`: The starting element:
      - *Text*: A string (e.g., "Subscriptions").
      - *XPath*: An XPath (e.g., `//android.widget.TextView[@text="Subscriptions"]`).
      - *Image*: An image filename (e.g., "sub.jpeg").
    - `direction`: Scroll direction ("up", "down", "left", "right").
    - `scroll_length`: Distance of the scroll in pixels (integer, e.g., 100).
    - `aoi_x` (optional, default=0): X percentage of Area of Interest top-left corner (0-100, float).
    - `aoi_y` (optional, default=0): Y percentage of Area of Interest top-left corner (0-100, float).
    - `aoi_width` (optional, default=100): Width percentage of Area of Interest (0-100, float).
    - `aoi_height` (optional, default=100): Height percentage of Area of Interest (0-100, float).
    - `event_name` (optional): A string identifier for the scroll event (e.g., "scroll_right").
  - **Example**: `Scroll From Element,${Subscriptions_image},right,100,0,0,100,100,scroll_right`

- **Enter Text**
  Enters text into a specified element.
  - **Parameters**:
    - `element`: The input field:
      - *Text*: A string (e.g., "Search").
      - *XPath*: An XPath (e.g., `//android.widget.EditText`).
      - *Image*: An image filename (e.g., "search_field.png").
    - `text`: The text to enter (string, e.g., "Hello World").
    - `aoi_x` (optional, default=0): X percentage of Area of Interest top-left corner (0-100, float).
    - `aoi_y` (optional, default=0): Y percentage of Area of Interest top-left corner (0-100, float).
    - `aoi_width` (optional, default=100): Width percentage of Area of Interest (0-100, float).
    - `aoi_height` (optional, default=100): Height percentage of Area of Interest (0-100, float).
    - `event_name` (optional): A string identifier for the input event (e.g., "search_input").
  - **Example**: `Enter Text,${search_field_xpath},Hello World,0,0,100,100,search_input`

- **Enter Text Direct**
  Enters text without the need of a specified element or input field. Does not support special keys.
  - **Parameters**:
    - `text`: The text to enter (string, e.g., "Hello World").
    - `event_name` (optional): A string identifier for the input event (e.g., "search_input").
  - **Example**: `Enter Text Direct,Hello World,search_input`

- **Enter Text Using Keyboard**
  Enters text or special keys such as Enter, Tab, Space, Backspace using the keyboard, supported for appium and selenium.
  - **Parameters**:
    - `text or special key`: The text to enter (string, e.g., "Test Input") or special key in angle brackets (e.g., "<enter>", "<tab>").
    - `event_name` (optional): A string identifier for the input event (e.g., "keyboard_input").
  - **Example**: `Enter Text Using Keyboard,Test Input<enter>,keyboard_input`

- **Enter Number**
  Enters a number into a specified element.
  - **Parameters**:
    - `element`: The input field:
      - *Text*: A string (e.g., "Quantity").
      - *XPath*: An XPath (e.g., `//android.widget.EditText`).
      - *Image*: An image filename (e.g., "quantity_field.png").
    - `number`: The number to enter (float or integer, e.g., 42).
    - `aoi_x` (optional, default=0): X percentage of Area of Interest top-left corner (0-100, float).
    - `aoi_y` (optional, default=0): Y percentage of Area of Interest top-left corner (0-100, float).
    - `aoi_width` (optional, default=100): Width percentage of Area of Interest (0-100, float).
    - `aoi_height` (optional, default=100): Height percentage of Area of Interest (0-100, float).
    - `event_name` (optional): A string identifier for the input event (e.g., "number_input").
  - **Example**: `Enter Number,${quantity_field_xpath},42,0,0,100,100,number_input`

- **Press Keycode**
  Presses a specified keycode (e.g., Android keycodes).
  - **Parameters**:
    - `keycode`: The keycode to press (integer, e.g., 66 for Enter on Android).
    - `event_name`: A string identifier for the key press event (e.g., "enter_key").
  - **Example**: `Press Keycode,66,enter_key`

- **Clear Element Text**
  Clears text from a specified element.
  - **Parameters**:
    - `element`: The input field to clear:
      - *Text*: A string (e.g., "Search").
      - *XPath*: An XPath (e.g., `//android.widget.EditText`).
      - *Image*: An image filename (e.g., "search_field.png").
    - `aoi_x` (optional, default=0): X percentage of Area of Interest top-left corner (0-100, float).
    - `aoi_y` (optional, default=0): Y percentage of Area of Interest top-left corner (0-100, float).
    - `aoi_width` (optional, default=100): Width percentage of Area of Interest (0-100, float).
    - `aoi_height` (optional, default=100): Height percentage of Area of Interest (0-100, float).
    - `event_name` (optional): A string identifier for the clear event (e.g., "clear_input").
  - **Example**: `Clear Element Text,${input_field_xpath},0,0,100,100,clear_input`

- **Get Text**
  Retrieves text from a specified element (returns None if not supported).
  - **Parameters**:
    - `element`: The target element:
      - *Text*: A string (e.g., "Title").
      - *XPath*: An XPath (e.g., `//android.widget.TextView[@text="Title"]`).
      - *Image*: Not supported (use text/XPath only).
  - **Example**: `Get Text,${title_xpath}`

- **Sleep**
  Pauses execution for a specified duration.
  - **Parameters**:
    - `duration`: Time to sleep in seconds (integer, e.g., 5).
  - **Example**: `Sleep,5`

## App Management Keywords

These keywords manage application lifecycle operations.

- **Initialise Setup**
  Sets up the environment for the driver module.
  - **Parameters**: None
  - **Example**: `Initialise Setup`

- **Launch App**
  Launches the configured application (as defined in `config.yaml`).
  - **Parameters**:
    - `app_identifier` (optional): App package/bundle name (string, e.g., "com.example.app")
    - `app_activity` (optional): App activity name (string, e.g., "MainActivity")
    - `event_name` (optional): A string identifier for the launch event (e.g., "app_start")
  - **Example**: `Launch App,com.example.app,MainActivity,app_start`

- **Start Appium Session** *(Deprecated)*
  Starts an Appium session (same as `Launch App` for Appium).
  - **Parameters**:
    - `event_name` (optional): A string identifier for the session event (e.g., "session_start").
  - **Example**: `Start Appium Session,session_start`

- **Launch Other App**
  Starts another application by bundle ID.
  - **Parameters**:
    - `bundleid`: The bundle/package ID of the app (string, e.g., "com.example.app")
  - **Example**: `Launch Other App,com.example.app`

- **Close And Terminate App**
  Closes and terminates the current application.
  - **Parameters**: None
  - **Example**: `Close And Terminate App`

- **Force Terminate App**
  Forcefully terminates the specified application.
  - **Parameters**:
    - `app_name`: The name or package of the app to terminate (string, e.g., "com.example.app")
    - `event_name` (optional): A string identifier for the termination event (e.g., "force_stop")
  - **Example**: `Force Terminate App,com.example.app,force_stop`

- **Get App Version**
  Retrieves the version of the application (returns None if not available).
  - **Parameters**: None
  - **Example**: `Get App Version`

- **Get Driver Session Id**
  Returns the current driver session ID, if available (e.g., Appium session ID).
  - **Parameters**: None
  - **Example**: `Get Driver Session Id`

## Flow Control Keywords

These keywords manage test flow, such as loops and conditions.

- **Execute Module**
  Executes a named module from `test_modules.csv`.
  - **Parameters**:
    - `module_name`: The name of the module to execute (string, e.g., "Interact using text").
  - **Example**: `Execute Module,Interact using text`

- **Run Loop**
  Runs a loop over a target module, either by count or with variables.
  - **Parameters**:
    - `target`: The module to loop over (string, e.g., "Dynamic Launch").
    - For count-based:
      - `count`: Number of iterations (integer, e.g., 3).
    - For variable-based:
      - `var1`, `iterable1`, `var2`, `iterable2`, ...: Pairs of variable names (e.g., `${METHOD}`) and iterables. Iterables can be:
        - JSON string arrays: `"['text','xpath']"`
        - Pipe-separated values: `"text|xpath|image"`
        - Variables referencing lists: `${List}`
  - **Examples**:
    - Count-based: `Run Loop,Dynamic Launch,3`
    - Variable-based: `Run Loop,Dynamic Launch,${METHOD},"text|xpath|image"`
    - Variable-based with JSON: `Run Loop,Dynamic Launch,${METHOD},"['text','xpath']"`

- **Condition**
  Evaluates conditions and executes the corresponding target module. Supports both expression-based and module-based conditions.
  - **Parameters**:
    - `condition1`: A condition expression or module name:
      - Expression-based: A condition expression (string, e.g., `${METHOD} == 'text'`) using variables from `elements.csv`.
      - Module-based: A module name (string, e.g., "Check Element Present"). If the module executes successfully, the condition is true.
      - Inversion: Prefix with `!` to invert the condition (e.g., `!Check Element Present`).
    - `target1`: The module to execute if `condition1` is true (string, e.g., "Interact using text").
    - `condition2`, `target2`, ...: Additional condition-target pairs (optional).
    - `else_target` (optional): The module to execute if no conditions are true (string, e.g., "Interact using images").
  - **Examples**:
    - Expression-based: `Condition,${METHOD} == 'text',Interact using text,${METHOD} == 'xpath',Interact using xpath,Interact using images`
    - Module-based: `Condition,Check Element Present,Interact using text,Interact using images`
    - Inverted: `Condition,!Check Element Present,Handle Missing Element,Continue Flow`

- **Read Data**
  Reads data from a file, environment variable, list, or API, with optional query string for filtering/selection.

  - **Parameters**:
    - `input_element`: Variable to store the data (e.g., `${List}`)
    - `file_path`: Data source (CSV file, JSON file, ENV:VAR, list, or URL)
    - `query` (optional): Query string for filtering/selection (e.g., `status=active;columns=name`)
  - **Example**: `Read Data,${List},optics_framework/samples/contact/elements.csv,status=active;columns=name`
  - **Example**: `Read Data,${List},ENV:CONTACT_NAME`

- **Invoke API**
  Invokes an API call defined in the session's API config, with variable substitution and response extraction.
  - **Parameters**:
    - `api_name`: API to invoke (format: `collection.api_name`, e.g., `login.auth_token`)
  - **Example**: `Invoke API,login.auth_token`
  - **Example**: `Invoke API,login.send_otp`

- **Evaluate**
  Evaluates an expression and stores the result in a variable.
  - **Parameters**:
    - `param1`: The variable to store the result (string, e.g., `${result}`; typically in `${name}` format).
    - `param2`: The expression to evaluate (string, e.g., `${count} + 1`), using variables from `elements.csv`.
  - **Example**: `Evaluate,${result},${count} + 1`

- **Date Evaluate**
  Evaluates a date expression based on an input date and stores the result in a variable.
  - **Parameters**:
    - `param1`: The variable to store the result (string, e.g., `${tomorrow}`; typically in `${name}` format).
    - `param2`: The input date string (e.g., "04/25/2025" or "2025-04-25"). Format is auto-detected.
    - `param3`: The date expression to evaluate (e.g., "+1 day", "-2 days", or "today").
    - `param4` (optional, default="%d %B"): The output format for the evaluated date (e.g., "%d %B" produces "26 April").
  - **Examples**:
    - `Date Evaluate,${tomorrow},04/25/2025,+1 day`
    - `Date Evaluate,${yesterday},2025-04-25,-1 day,%Y-%m-%d`

## Verification Keywords

These keywords verify elements, screens, and data.

- **Validate Element**
  Verifies the presence of an element.
  - **Parameters**:
    - `element`: The element to verify:
      - *Text*: A string (e.g., "Home").
      - *XPath*: An XPath (e.g., `//android.widget.TextView[@text="Home"]`).
      - *Image*: An image filename (e.g., "home.png").
    - `timeout` (optional, default=10): Maximum time in seconds to wait (integer).
    - `rule` (optional, default="all"): Verification rule ("all" or "any"; "all" requires all elements if multiple, "any" requires at least one).
    - `event_name` (optional): A string identifier for the verification event (e.g., "check_home").
  - **Example**: `Validate Element,${Home_xpath},5,any,check_home`

- **Is Element**
  Checks if an element is in a specified state (unimplemented).
  - **Parameters**:
    - `element`: The element to check:
      - *Text*: A string (e.g., "Button").
      - *XPath*: An XPath (e.g., `//android.widget.Button`).
      - *Image*: An image filename (e.g., "button.png").
    - `element_state`: The state to verify (string: "visible", "invisible", "enabled", "disabled").
    - `timeout`: Maximum time in seconds to wait (integer, e.g., 10).
    - `event_name` (optional): A string identifier for the check event (e.g., "check_button").
  - **Example**: `Is Element,${button_xpath},visible,10,check_button`

- **Assert Equality**
  Compares two values for equality (unimplemented).
  - **Parameters**:
    - `output`: The first value to compare (string or variable, e.g., `${result}`).
    - `expression`: The second value to compare (string or expression, e.g., "42").
    - `event_name` (optional): A string identifier for the comparison event (e.g., "verify_result").
  - **Example**: `Assert Equality,${result},42,verify_result`

- **Assert Presence**
  Asserts the presence of one or more elements.
  - **Parameters**:
    - `elements`: Pipe-separated (`|`) elements to check:
      - *Text*: A string (e.g., "Home").
      - *XPath*: An XPath (e.g., `//android.widget.TextView[@text="Home"]`).
      - *Image*: An image filename (e.g., "home.png").
      - Example: `${Subscriptions_text}|${Home_xpath}`.
    - `timeout` (optional, default=30): Maximum time in seconds to wait (integer).
    - `rule` (optional, default="any"): Verification rule ("any" or "all").
    - `event_name` (optional): A string identifier for the assertion event (e.g., "verify_screen").
  - **Example**: `Assert Presence,${Subscriptions_text}|${Home_xpath},10,all,verify_screen`

- **Validate Screen**
  Verifies the screen by checking element presence (alias for `Assert Presence`, but does not fail on error).
  - **Parameters**:
    - `elements`: Pipe-separated (`|`) elements to verify:
      - *Text*: A string (e.g., "Home").
      - *XPath*: An XPath (e.g., `//android.widget.TextView[@text="Home"]`).
      - *Image*: An image filename (e.g., "home.png").
      - Example: `${Home_image}|${Subscriptions_image}`.
    - `timeout` (optional, default=30): Maximum time in seconds to wait (integer).
    - `rule` (optional, default="any"): Verification rule ("any" or "all").
    - `event_name` (optional): A string identifier for the verification event (e.g., "check_screen").
  - **Example**: `Validate Screen,${Home_image}|${Subscriptions_image},15,any,check_screen`

- **Capture Screenshot**
  Captures a screenshot of the current screen.
  - **Parameters**:
    - `event_name` (optional): A string identifier for the screenshot capture event (e.g., "screenshot_before_action").
  - **Returns**: Base64-encoded screenshot string.
  - **Example**: `Capture Screenshot,screenshot_before_action`

- **Capture Page Source**
  Captures the page source of the current screen.
  - **Parameters**:
    - `event_name` (optional): A string identifier for the page source capture event (e.g., "capture_source").
  - **Returns**: Page source as a string (XML for Appium, HTML for Selenium/Playwright).
  - **Example**: `Capture Page Source,capture_source`

- **Get Interactive Elements**
  Retrieves a list of interactive elements on the current screen.
  - **Parameters**:
    - `filter_config` (optional): List of filter types (e.g., `["buttons", "inputs"]`). Valid values:
      - `"all"`: Show all elements (default when None or empty)
      - `"interactive"`: Only interactive elements
      - `"buttons"`: Only button elements
      - `"inputs"`: Only input/text field elements
      - `"images"`: Only image elements
      - `"text"`: Only text elements
      - Can be combined: `["buttons", "inputs"]`
  - **Returns**: List of interactive elements with their properties.
  - **Example**: `Get Interactive Elements,["buttons","inputs"]`

- **Get Screen Elements**
  Captures a screenshot and retrieves interactive elements for API response.
  - **Parameters**: None
  - **Returns**: Dictionary with base64-encoded screenshot and list of elements.
  - **Example**: `Get Screen Elements`

## Additional Information

!!! info "Element Types"
    Many keywords accept `element` parameters that can be:
    - *Text*: A literal string or variable (e.g., "Home", `${Home_text}`) for OCR-based detection.
    - *XPath*: An XPath expression (e.g., `//android.widget.Button[@resource-id="id"]`) for Appium/Selenium.
    - *Image*: A filename from `input_templates/` (e.g., "home.png", `${Home_image}`) for image matching.
    Check each keyword’s description for supported types.

!!! tip "Parameters"
    Optional parameters can be left blank in the CSV (e.g., `Press Element,${Home_text},,,click_event` skips `repeat`, `offset_x`, and `offset_y`).

!!! info "Area of Interest (AOI) Parameters"
    Many keywords support AOI (Area of Interest) parameters (`aoi_x`, `aoi_y`, `aoi_width`, `aoi_height`) to limit element search to a specific region of the screen. These are specified as percentages (0-100):
    - `aoi_x`, `aoi_y`: Top-left corner coordinates (default: 0, 0)
    - `aoi_width`, `aoi_height`: Width and height of the region (default: 100, 100)
    - When AOI is used, the framework will annotate screenshots with the search region for debugging.

!!! warning "Deprecated Keywords"
    Keywords marked with *(Deprecated)* (e.g., `Press Checkbox`) should be avoided in new tests as they may be removed in future versions. Use alternatives like `Press Element` instead.

!!! note "Unimplemented Keywords"
    Some keywords (e.g., `Select Dropdown Option`) are placeholders and not yet functional. They are included for future compatibility.

!!! info "Usage in CSV"
    Keywords are used in the `module_step` column of `test_modules.csv`, with parameters in subsequent columns (e.g., `param_1`, `param_2`, ...). When using pipe-separated values (e.g., in `Assert Presence`), use the pipe character (`|`) to separate elements.

!!! tip "Variables"
    Parameters like `${Home_text}` reference values from `elements.csv`, allowing reusable element definitions.

Refer to the [User Workflow](../user_workflow.md) for examples of how to integrate these keywords into your test modules.
