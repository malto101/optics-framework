# Flow Control

The `FlowControl` class manages control flow operations including loops, conditions, and data management for test sessions.

### Read Data

The `read_data` method loads tabular data from a file path, an environment variable (using the `ENV:VAR_NAME` form), or a 2D list; applies optional query parts such as `select=col1,col2` and filter expressions; and stores the result in the session's elements. For full details on the `ENV:` prefix, query syntax (including variable resolution `${var}`), and all supported `file_path` forms, see [Read Data](../usage/keyword_usage.md#read-data) in Keyword Usage.

::: optics_framework.api.flow_control.FlowControl
    options:
      show_root_heading: true
      show_source: false
      heading_level: 2
