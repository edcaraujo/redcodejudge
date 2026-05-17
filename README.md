# RedCodeJudge

## 🚀 Official automated testing tool for the RedCodeNinja Team

**RedCodeJudge** is a command-line tool designed to streamline the testing of competitive programming solutions. It automates the process of compiling, running, and validating your code against a set of test cases, providing clear and colorful feedback on its performance.

This tool is perfect for:
- Contestants of programming competitions (Marathons, OI, ICPC).
- Students and enthusiasts who want to test their algorithmic solutions locally.
- Coaches and teams who need a simple way to evaluate code.

## ✨ Features

- **Multiple Languages Supported**: Test solutions written in C, C++, Java, and Python with **automatic language detection**.
- **Rich Feedback**: Get status on each test case:
  - ✅ **AC (Accepted)**: Your program's output matches the expected output.
  - ⛔ **WA (Wrong Answer)**: Your program's output differs from the expected output.
  - 🐌 **TLE (Time Limit Exceeded)**: Your program took too long to execute (10s limit).
  - 💣 **RTE (Runtime Error)**: Your program crashed or returned a non-zero exit code.
- **Detailed Diff**: For **Wrong Answer** verdicts, a quick unified diff is displayed to help you spot the differences.
- **Performance Summary**: Get a final score with an accuracy percentage and a summary of the results.
- **Verbose Mode**: A verbose option `-v` to display the full I/O for each test case, making debugging easier.
- **Isolated Workspace**: Each execution creates a separate hidden directory (e.g., `.redcodejudge-2023...`) to store compilation artifacts and test results.

## 📋 Prerequisites

Before you begin, ensure you have Python 3 installed. Depending on the language you are testing, you may also need:

- **C**: `gcc`
- **C++**: `g++` (supports C++17)
- **Java**: `javac` and `java`

You can check your Python version by running:

```bash
python3 --version
```

## 📦 Installation

1. Clone the repository to your local machine.
   ```bash
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```bash
   cd redcodejudge
   ```
3. (Optional) Make the script executable:
   ```bash
   chmod +x redcodejudge.py
   ```

## 💡 Usage

Execute the script providing the path to your source code and the directories for input and output files.

```bash
python3 redcodejudge.py <source_file> -i <input_dir> -o <output_dir> [options]
```

### Arguments

- `source_file`: Path to your source code file (e.g., `problem.cpp`).
- `-i, --input-dir`: Directory containing input test files (e.g., `.in`, `.txt`).
- `-o, --output-dir`: Directory containing the corresponding expected output files (e.g., `.out`, `.sol`).
- `--lang` (Optional): The programming language. Choices: `c`, `cpp`, `java`, `python`. If omitted, it is auto-detected from the file extension.
- `-w, --workspace-dir` (Optional): Specific directory to store build artifacts and results.
- `-v, --verbose` (Optional): Enables verbose mode to show detailed I/O for each test case.

### Example

Imagine the following directory structure:

```
/my_contest
├── solutions
│   └── B.cpp
└── problems
    └── B
        ├── in
        │   ├── 01.in
        │   └── 02.in
        └── out
            ├── 01.out
            └── 02.out
```

To test the `B.cpp` solution, you would run:

```bash
python3 redcodejudge.py /my_contest/solutions/B.cpp -i /my_contest/problems/B/in -o /my_contest/problems/B/out
```

## 📝 License

This project is open-source, and you are free to use, modify, and distribute it. A `LICENSE` file with the MIT License is provided.
