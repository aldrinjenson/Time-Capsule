# Time Capsule

Introducing Time Capsule

The open-source, self-hosted AI assistant that empowers you with perfect memory! 🧠💡

Time Capsule is a powerful tool that continuously captures and stores your digital activities, including screen recordings and typed text. It enables you to search and retrieve any information you've seen or typed on your device, providing you with a comprehensive digital memory.

## ✨ Key Features

- 🔒 Own your data with secure local storage
- 🖥️ Continuous capture of screen at 0.5 FPS & text
- 🔍 Search & find anything instantly
- 💻 Customize & extend with open source code
- 🔐 Encrypted storage for enhanced security
- ⚡ Optimized performance using OpenCV & Tesseract OCR
- 🐧🪟🍎 Cross-platform support for Windows, Linux, and macOS

## 🚧 Work in Progress 🚧

Time Capsule is currently under active development, with several exciting features in the pipeline.

### 🚀 Current Functionality

- **Screen recording**
  - Captures screenshots at a fixed interval of 2 seconds (0.5 FPS)
  - Performs OCR on captured screenshots to extract text
  - Saves extracted text along with timestamps and metadata

- **Typed text capture:**
  - Captures typed text across applications using the pynput library
  - Detects context switches based on mouse clicks, window focus changes, key presses, long pauses, and token limit reached
  - Saves captured text periodically to JSON files with timestamps and metadata
  - Provides configuration options for enabling/disabling text capture and specifying storage interval

### 📝 Features Awaiting Implementation

- 🔍 Search functionality to quickly find specific information based on keywords or timestamps
- 🔐 Data encryption to ensure the security of recorded data
- 🎨 Intuitive user interface for easy navigation and browsing of captured data

## 💻 Installation Instructions

Follow these steps to get the project running on your local machine:

1. Clone the repository
2. Create and activate a virtual environment
3. Install the required dependencies
4. Configure environment variables
5. Run the application

Refer to the [installation guide](docs/installation.md) for detailed instructions.

## 📂 Project Structure

The Time Capsule project follows a modular and organized structure:

- `src/`: Contains the main source code files
  - `screen_recording/`: Module for screen recording and OCR functionality
  - `text/`: Module for capturing typed text
  - `main.py`: Main entry point of the application
- `recordings/`: Directory for storing recorded data
  - `screenshots/`: Subdirectory for screen recordings
  - `text/`: Subdirectory for captured text data
- `tests/`: Contains unit tests for various modules
- `utils/`: Contains utility modules
  - `system_info.py`: Module for retrieving system information
  - `tokenization_utils.py`: Module for tokenizing and storing text data
- `docs/`: Documentation files
- `requirements.txt`: Lists the required Python dependencies
- `setup.py`: Setup script for the project

## 🤝 Contributing

We welcome contributions from the open-source community to help improve and expand the capabilities of Time Capsule. If you'd like to contribute, please refer to our [contribution guidelines](CONTRIBUTING.md) for more information.



## 📄 License

Time Capsule is released under the [MIT License](LICENSE).

## 📧 Contact

For any questions, suggestions, or feedback, please feel free to reach out to me on X at [@TheSethRose](https://www.x.com/TheSethRose)

## ❤️ Support

<a href="https://www.buymeacoffee.com/TheSethRose" target="_blank"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee!&emoji=&slug=TheSethRose&button_colour=000000&font_colour=ffffff&font_family=Cookie&outline_colour=ffffff&coffee_colour=FFDD00" alt="Buy Me A Coffee!"></a>

## 📚 Documentation

Detailed documentation for Time Capsule can be found in the [docs](docs/) directory. It includes:

- [Installation Guide](docs/installation.md)
- [Usage Instructions](docs/usage.md)
- [API Reference](docs/api_reference.md)


## 🛠️ Environment Setup

To set up the development environment for Time Capsule, follow these steps:

1. Install Python 3.9 or higher
2. Create a virtual environment
3. Install the required dependencies
4. Configure environment variables

Refer to the [environment setup guide](docs/environment_setup.md) for detailed instructions.

## 🚀 Deployment

Time Capsule can be deployed on various platforms, including:

- Local machine
- Cloud servers (e.g., AWS, Google Cloud, DigitalOcean)
- Containerized environments (e.g., Docker)

Refer to the [deployment guide](docs/deployment.md) for platform-specific instructions.

## 🗺️ Roadmap

The future roadmap for Time Capsule includes:

- Search functionality
- Data encryption
- User interface
- Integration with cloud storage services
- Mobile app for remote access

Stay tuned for updates and new feature releases!

## 📖 Table of Contents

- [Installation](docs/installation.md)
- [Usage](docs/usage.md)
- [API Reference](docs/api_reference.md)
- [Contributing](CONTRIBUTING.md)
- [License](LICENSE)

## 🖥️ Usage

To start using Time Capsule, follow these steps:

1. Ensure you have completed the installation and setup process
2. Open a terminal and navigate to the project directory
3. Run the command `python main.py`
4. Time Capsule will start capturing your screen and typed text
5. Access the captured data in the `recordings/` directory

Refer to the [usage guide](docs/usage.md) for more detailed instructions and advanced configuration options.

## 🧪 Tests

Time Capsule includes a suite of unit tests to ensure the reliability and stability of the codebase. To run the tests:

1. Make sure you have installed the required dependencies
2. Open a terminal and navigate to the project directory
3. Run the command `python -m unittest discover tests/`

The test results will be displayed in the terminal, indicating which tests passed or failed.