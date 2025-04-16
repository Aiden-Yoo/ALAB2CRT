# ALAB2CRT

ALAB2CRT is a tool that creates sessions from Arista Networks' various lab environments (ACT, ATD) into SecureCRT-compatible format.

## Features

- ACT (Arista Cloud Test) lab session creation
- ATD (Arista Test Drive) lab session creation
- Jump host connection support
- SecureCRT-compatible session file generation

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Aiden-Yoo/alab2crt.git
cd alab2crt
```

2. Install the package in development mode:
```bash
pip install -e .
```

## Configuration

### ACT Configuration

Modify the `src/alab2crt/config/act.yml` file to configure ACT settings:

```yaml
act:
  api_key: "your_act_api_key"
  act_username: "your_username"
```

### ATD Configuration

Modify the `src/alab2crt/config/atd.yml` file to configure ATD settings:

```yaml
atd:
  - topology: "topology_type"
    lab: "lab_name"
    username: "lab_username"
    password: "lab_password"
```

## Usage

After installation, you can run ALAB2CRT using the following command:

```bash
alab2crt
```

### Provider-specific Commands

Generate sessions for a specific provider:
```bash
alab2crt -p act    # Generate ACT sessions only
alab2crt -p atd    # Generate ATD sessions only
```

Generated session files will be saved in the `sessions` directory.

## Development

If you want to run the code directly without installation:

```bash
pip install -r requirments.txt
python src/alab2crt/main.py
```

## Directory Structure

```
alab2crt/
├── src/
│   └── alab2crt/
│       ├── config/
│       │   ├── act.yml
│       │   └── atd.yml
│       ├── providers/
│       │   ├── act.py
│       │   └── atd.py
│       └── core/
│           ├── session.py
│           └── config.py
├── sessions/
├── setup.py
├── requirements.txt
└── README.md
```

## License

This project is licensed under the MIT License.
