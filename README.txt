URL VALIDATOR APPLICATION
========================

Description
-----------
This application provides a graphical user interface for validating URLs. It checks if a URL:
- Has a valid format
- Uses a proper scheme (http or https)
- Is accessible (returns a successful HTTP status code)

The application displays the validation result both in the main window and in a popup message box.

Project Structure
----------------
The project follows Object-Oriented design principles with a focus on separation of concerns:

1. main.py
   - Entry point for the application
   - Minimal code that just initializes and runs the application

2. url_validator_app.py
   - Contains the URLValidatorApp class that handles the GUI
   - Manages the tkinter window, widgets, and user interactions
   - Delegates URL validation to the URLValidator class

3. url_validator.py
   - Contains the URLValidator class for URL validation logic
   - Provides methods to check URL format, scheme, and accessibility
   - Returns validation results with appropriate messages

4. config.py
   - Contains configuration constants
   - Centralizes settings for window dimensions, colors, fonts, etc.
   - Makes it easy to modify the application's appearance and behavior

Object-Oriented Design
---------------------
The code follows these Object-Oriented principles:

1. Separation of Concerns
   - UI logic is separated from validation logic
   - Configuration is separated from implementation

2. Single Responsibility Principle
   - Each class has a single, well-defined responsibility
   - URLValidator: Validates URLs
   - URLValidatorApp: Manages the GUI

3. Encapsulation
   - Related functionality is grouped together
   - Implementation details are hidden behind well-defined interfaces

4. DRY (Don't Repeat Yourself)
   - Constants are defined once in config.py
   - Common validation logic is centralized in the URLValidator class

Dependencies
-----------
- Python 3.x
- tkinter (standard library)
- validators
- requests

How to Run
---------
1. Ensure Python and the required packages are installed:
   ```
   pip install validators requests
   ```

2. Run the application:
   ```
   python main.py
   ```

Usage
-----
1. Enter a URL in the input field (default prefix is "https://")
2. Click the "Validate URL" button
3. View the validation result in both the main window and the popup message

Future Improvements
-----------------
1. Add support for more URL validation checks
2. Implement history of validated URLs
3. Add ability to save validation results
4. Create more detailed validation reports
5. Add support for batch validation of multiple URLs
6. Implement asynchronous validation for better UI responsiveness

Maintenance
----------
The modular structure makes the application easy to maintain and extend:
- To modify the UI, edit url_validator_app.py
- To change validation logic, edit url_validator.py
- To adjust appearance settings, edit config.py
- The main.py file should rarely need modification
