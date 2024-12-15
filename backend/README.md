# Corneal Topography Backend

This is the optimized backend for processing corneal topography data. The system handles file uploads, data extraction, and patient examination records management.

## Project Structure

```
backend/
├── corneal_topography/
│   ├── models/
│   │   ├── __init__.py
│   │   └── examination.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── examination_service.py
│   │   └── file_service.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── validators.py
│   └── tests/
│       └── __init__.py
└── requirements.txt
```

## Features

- File upload handling with type and size validation
- Data extraction from corneal topography images
- Patient examination record management
- Automatic delta K calculation
- Transaction support for database operations
- Comprehensive error handling and logging
- Input validation for measurements

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

The main components are:

1. `ExaminationRecord`: Data class for storing examination data
2. `FileService`: Handles file uploads and validation
3. `ExaminationService`: Manages examination records
4. `validators`: Utility functions for data validation

## Error Handling

The system includes comprehensive error handling for:
- Invalid file types
- File size limits
- Data validation
- Database operations
- Image processing errors

## Logging

Proper logging is implemented throughout the system, replacing print statements with structured logging.
