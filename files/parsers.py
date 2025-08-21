import pandas as pd
import PyPDF2
import io
import json
from typing import Dict, Any, List
from django.conf import settings


class FileParser:
    """Base class for file parsing"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
    
    def parse(self) -> Dict[str, Any]:
        """Parse file and return structured data"""
        raise NotImplementedError("Subclasses must implement parse method")


class CSVParser(FileParser):
    """Parser for CSV files"""
    
    def parse(self) -> Dict[str, Any]:
        try:
            df = pd.read_csv(self.file_path)
            return {
                'type': 'csv',
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': df.columns.tolist(),
                'data': df.head(100).to_dict('records'),  # First 100 rows
                'summary': {
                    'total_rows': len(df),
                    'total_columns': len(df.columns),
                    'memory_usage': df.memory_usage(deep=True).sum(),
                }
            }
        except Exception as e:
            raise ValueError(f"Error parsing CSV file: {str(e)}")


class ExcelParser(FileParser):
    """Parser for Excel files"""
    
    def parse(self) -> Dict[str, Any]:
        try:
            # Read all sheets
            excel_file = pd.ExcelFile(self.file_path)
            sheets_data = {}
            
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(self.file_path, sheet_name=sheet_name)
                sheets_data[sheet_name] = {
                    'rows': len(df),
                    'columns': len(df.columns),
                    'column_names': df.columns.tolist(),
                    'data': df.head(50).to_dict('records'),  # First 50 rows per sheet
                }
            
            return {
                'type': 'excel',
                'sheets': list(excel_file.sheet_names),
                'sheets_data': sheets_data,
                'summary': {
                    'total_sheets': len(excel_file.sheet_names),
                    'total_rows': sum(sheet['rows'] for sheet in sheets_data.values()),
                }
            }
        except Exception as e:
            raise ValueError(f"Error parsing Excel file: {str(e)}")


class PDFParser(FileParser):
    """Parser for PDF files"""
    
    def parse(self) -> Dict[str, Any]:
        try:
            with open(self.file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                text_content = []
                page_count = len(pdf_reader.pages)
                
                # Extract text from first 10 pages to avoid memory issues
                for page_num in range(min(10, page_count)):
                    page = pdf_reader.pages[page_num]
                    text_content.append({
                        'page': page_num + 1,
                        'text': page.extract_text()[:1000]  # First 1000 characters per page
                    })
                
                return {
                    'type': 'pdf',
                    'total_pages': page_count,
                    'pages_parsed': len(text_content),
                    'text_content': text_content,
                    'summary': {
                        'total_pages': page_count,
                        'total_text_length': sum(len(page['text']) for page in text_content),
                    }
                }
        except Exception as e:
            raise ValueError(f"Error parsing PDF file: {str(e)}")


class TXTParser(FileParser):
    """Parser for TXT files"""
    
    def parse(self) -> Dict[str, Any]:
        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                lines = content.split('\n')
                
                return {
                    'type': 'txt',
                    'total_lines': len(lines),
                    'total_characters': len(content),
                    'content_preview': content[:2000],  # First 2000 characters
                    'lines_preview': lines[:100],  # First 100 lines
                    'summary': {
                        'total_lines': len(lines),
                        'total_characters': len(content),
                        'average_line_length': len(content) / len(lines) if lines else 0,
                    }
                }
        except Exception as e:
            raise ValueError(f"Error parsing TXT file: {str(e)}")


def get_parser(file_path: str, file_type: str) -> FileParser:
    """Factory function to get appropriate parser based on file type"""
    file_type = file_type.lower()
    
    if file_type in ['csv']:
        return CSVParser(file_path)
    elif file_type in ['xlsx', 'xls']:
        return ExcelParser(file_path)
    elif file_type in ['pdf']:
        return PDFParser(file_path)
    elif file_type in ['txt']:
        return TXTParser(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")


def parse_file(file_path: str, file_type: str) -> Dict[str, Any]:
    """Parse file and return structured data"""
    parser = get_parser(file_path, file_type)
    return parser.parse()
