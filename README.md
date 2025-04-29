## Overview
This FastAPI app extracts lab test names, values, and reference ranges from lab report images.

## Usage
1. Start the app:
```bash
uvicorn app.main:app --reload
```

2. Send a POST request to `/get-lab-tests` with an image.

## Dependencies
Install with:
```bash
pip install -r requirements.txt
```

## Example Output
```json
{
  "is_success": true,
  "lab_test_data": [
    {
      "lab_test_name": "Hemoglobin",
      "lab_test_value": 10.2,
      "bio_reference_range": "12.0 - 15.5",
      "lab_test_out_of_range": true
    }
  ]
}
```
