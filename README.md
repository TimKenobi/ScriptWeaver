# Script Weaver

Script Weaver is a Python-based GUI application designed to create, edit, manage, and execute scripts by "weaving" together modular components. It supports languages like Python, Bash, and PowerShell, allowing users to build and run custom workflows efficiently. With features like in-app editing, grouping, tagging, and security options, it's perfect for developers, system administrators, and automation enthusiasts. This version is built and tested on the latest version of macOS 15.5, with support for other platforms in development.

Hint: Keep an eye out for possible Easter eggs, like references to classic movies—let the discovery be part of the fun!

## ✨ Features

- **Modular Script Building**: Combine pre-defined or custom script modules into cohesive workflows using the GUI.
- **Language Support**: Handles Python, Bash, PowerShell, and more with basic cross-language integration.
- **Script Management Grouping**: Organize scripts into groups that can be executed with a single command for streamlined workflows.
- **In-App Script Editing**: Built-in editor for uploading, modifying, and saving scripts directly within the application.
- **Tagging System**: Tag scripts for categories like tools, configurations, installs, and more to enhance organization and searchability.
- **Install/Uninstall Linking**: Tie installation scripts to corresponding uninstall scripts in the GUI for easy management.
- **Search Functionality**: Quickly search through scripts, groups, and tags to find what you need.
- **Built-in Security**: Includes security measures to protect script execution and data handling.
- **Sudo Specification**: Option to specify if a script requires sudo privileges, with appropriate prompts.
- **Hover Descriptions**: Detailed descriptions appear when hovering over scripts for quick insights.
- **Confirmation Dialogs**: "Are you sure?" dialog boxes for critical actions to prevent accidental executions or changes.
- **Branding Customization**: Customize the app's appearance and branding to fit your preferences.
- **Wiki and Resource Links**: Integrated links to wikis, documentation, and other resources for scripts.
- **Settings Panel**: Comprehensive settings for app behavior, including the ever important dark theme enabled by default.
- **Execution Monitoring**: Tracks runtime and errors via detailed logs.
- **File Management**: Handles script uploads, edits, inputs/outputs, and basic cleanup.

## ⚙️ How It Works

Script Weaver uses a configuration file to define modules and workflows, following this process:

1. **Configuration Parsing**: Loads the workflow configuration to identify modules, groups, tags, and execution details.
2. **Weaving Process**: Combines scripts into executable wrappers, managing flow, variables, and dependencies like sudo requirements.
3. **Editing and Management**: Use the GUI to edit scripts, create groups, add tags, link installs/uninstalls, and search.
4. **Security and Confirmation**: Applies built-in security checks, prompts for sudo if needed, and shows confirmation dialogs.
5. **Execution**: Runs the woven script or group, monitoring progress and capturing logs with included progress bars.
6. **Logging**: Records outcomes, errors, and metrics in logs, with hover descriptions and links available in the GUI.
7. **Cleanup**: Manages temporary files and resets the environment.

The app runs in a Python virtual environment, leveraging a GUI for interactive management, with dark theme and customization options accessible via settings.

## 📋 Requirements

### Operating System

* macOS (tested on M2 Pro with the latest version; other platforms in development)

### System Dependencies

* `python3`
* `python3-venv`
* `python3-pip`
* `bash` (for shell scripts)

### Python Dependencies

See `requirements.txt` for the full list.

## 🛠️ Installation

1. Clone the repository:
   ```
   git clone https://github.com/TimKenobi/Script_Weaver.git
   cd ScriptWeaver
   ```

2. Create and activate a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## 🚀 Usage

Launch the main script to open the GUI:

```
cd app
python main.py
```

From the GUI, you can:
- Load or create a configuration file (e.g., `settings.py`).
- Edit scripts in-app.
- Group and tag scripts.
- Search and manage installs/uninstalls.
- Execute with verbose logging and in app shell.


## 🔧 Configuration

- Place script modules in the `/scripts` directory.
- Use the settings panel for theme (dark by default), branding, and other customizations.
- Define groups, tags, descriptions, sudo flags, and links in the settings.py or via GUI.

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes. Ensure your code follows PEP8 standards and includes tests where applicable.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
