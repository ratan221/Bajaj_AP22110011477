import pytesseract
import cv2
import numpy as np
import tempfile
import re
from PIL import Image
import io
import os  # Add missing import

def process_lab_report(image_bytes):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp:
            temp.write(image_bytes)
            temp_path = temp.name

        if not os.path.exists(temp_path):
            raise Exception("Failed to save temporary image file")

        
        img = cv2.imread(temp_path)
        
        img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        
        
        denoised = cv2.fastNlMeansDenoising(thresh)
    
        
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(denoised, config=custom_config)
        
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
    
        results = []
        current_section = None
        
        for line in lines:
            #
            patterns = [
                
                r"([A-Za-z\s\(\).-]+?)\s*([-]?\d+\.?\d*)\s*([A-Za-z/%]+)?\s*([-]?\d+\.?\d*\s*-\s*[-]?\d+\.?\d*)?",
                
                r"([A-Za-z\s\(\).-]+?)\s*(POSITIVE|NEGATIVE)\s*([A-Za-z/%]+)?",
                
                r"([A-Za-z\s\(\).-]+?)\s*:\s*([-]?\d+\.?\d*)",
            ]
    
            for pattern in patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    test_name = match.group(1).strip()
                    value = match.group(2)
                    
                    
                    if any(word in test_name.lower() for word in ['date', 'no.', 'name', 'doctor', 'mobile']):
                        continue
                    
                    
                    unit = match.group(3) if len(match.groups()) > 2 and match.group(3) else "NA"
                    ref_range = match.group(4) if len(match.groups()) > 3 and match.group(4) else "NA"
                    
                   
                    out_of_range = False
                    # Fix indentation for this elif block
                    if ref_range != "NA" and ref_range:
                        try:
                            ref_low, ref_high = map(float, ref_range.replace(" ", "").split("-"))
                            value_float = float(value)
                            out_of_range = not (ref_low <= value_float <= ref_high)
                        except (ValueError, TypeError):
                            pass
                    elif value.upper() in ["POSITIVE"]:  # Fixed indentation
                        out_of_range = True
                    
                    result = {
                        "test_name": test_name.upper(),
                        "test_value": value,
                        "bio_reference_range": ref_range if ref_range != "NA" else "-",
                        "test_unit": unit if unit != "NA" else "-",
                        "lab_test_out_of_range": out_of_range
                    }
                    
                    if result not in results:
                        results.append(result)
                    break
    
        # Debug output
        print("Extracted text:", text)
        print("Processed results:", results)
        
        if not results:
            return {
                "is_success": True,
                "data": []
            }
    
        return {
            "is_success": True,
            "data": results
        }
    except Exception as e:
        print(f"Error in process_lab_report: {str(e)}")
        raise Exception(f"Failed to process lab report: {str(e)}")
    finally:
        # Cleanup temporary file
        if 'temp_path' in locals():
            try:
                os.remove(temp_path)
            except:
                pass


            