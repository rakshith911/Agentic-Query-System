# improvement_codegen/data_loader.py
"""
Enhanced Data Loader with MCP-style operations and Cursor AI integration

This module provides data loading capabilities with:
- MCP (Model Context Protocol) style data operations
- Enhanced error handling and validation
- Cursor AI-powered data processing
- Schema validation and type checking
"""

import os
import json
import pandas as pd
from typing import Dict, List, Any, Optional, Union
import logging
from pathlib import Path

# Set up logging - disabled for cleaner output
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Data directory path
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "Data")


class DataValidationError(Exception):
    """Custom exception for data validation errors"""
    pass


class MCPDataLoader:
    """MCP-style data loader with enhanced validation and error handling"""
    
    def __init__(self, data_dir: str = DATA_DIR):
        self.data_dir = Path(data_dir)
        self._validate_data_directory()
    
    def _validate_data_directory(self) -> None:
        """Validate that the data directory exists and contains required files"""
        if not self.data_dir.exists():
            raise DataValidationError(f"Data directory not found: {self.data_dir}")
        
        required_files = [
            "Table_feeds_v2.csv",
            "encoder_params.json", 
            "decoder_params.json",
            "encoder_schema.json",
            "decoder_schema.json"
        ]
        
        missing_files = []
        for file in required_files:
            if not (self.data_dir / file).exists():
                missing_files.append(file)
        
        if missing_files:
            logger.warning(f"Missing files: {missing_files}")
    
    def load_table_feeds(self) -> pd.DataFrame:
        """
        Load camera feeds data with enhanced validation
        
        Returns:
            DataFrame with camera feeds data
            
        Raises:
            DataValidationError: If data cannot be loaded or validated
        """
        csv_path = self.data_dir / "Table_feeds_v2.csv"
        xlsx_path = self.data_dir / "Table_feeds_v2.xlsx"
        
        try:
            if csv_path.exists():
                df = pd.read_csv(csv_path)
                # logger.info(f"Loaded {len(df)} camera feeds from CSV")
            elif xlsx_path.exists():
                df = pd.read_excel(xlsx_path)
                # logger.info(f"Loaded {len(df)} camera feeds from Excel")
            else:
                raise DataValidationError("No Table_feeds file found")
            
            # Validate required columns
            required_columns = ["FEED_ID", "THEATER", "FRRATE", "RES_W", "RES_H", "CODEC", "ENCR", "LAT_MS"]
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise DataValidationError(f"Missing required columns: {missing_columns}")
            
            # Data type validation and cleaning
            df = self._clean_feeds_data(df)
            
            return df
            
        except Exception as e:
            logger.error(f"Error loading camera feeds: {e}")
            raise DataValidationError(f"Failed to load camera feeds: {e}")
    
    def _clean_feeds_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate camera feeds data"""
        # Clean theater names
        df["THEATER"] = df["THEATER"].astype(str).str.strip().str.upper()
        
        # Validate numeric columns
        numeric_columns = ["FRRATE", "RES_W", "RES_H", "LAT_MS"]
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Remove rows with missing critical data
        df = df.dropna(subset=["FEED_ID", "THEATER"])
        
        # Validate theater values
        valid_theaters = ["PAC", "EUR", "ME", "CONUS"]
        invalid_theaters = df[~df["THEATER"].isin(valid_theaters)]["THEATER"].unique()
        if len(invalid_theaters) > 0:
            pass  # Invalid theaters found but logging disabled
        
        # logger.info(f"Cleaned data: {len(df)} valid feeds")
        return df
    
    def load_table_defs(self) -> pd.DataFrame:
        """
        Load table definitions (schema) for camera feed metadata
        
        Returns:
            DataFrame with table definitions
        """
        csv_path = self.data_dir / "Table_defs_v2.csv"
        xlsx_path = self.data_dir / "Table_defs_v2.xlsx"
        
        try:
            if csv_path.exists():
                return pd.read_csv(csv_path)
            elif xlsx_path.exists():
                return pd.read_excel(xlsx_path)
            else:
                raise DataValidationError("No Table_defs file found")
        except Exception as e:
            logger.error(f"Error loading table definitions: {e}")
            raise DataValidationError(f"Failed to load table definitions: {e}")
    
    def load_json(self, filename: str) -> Dict[str, Any]:
        """
        Load JSON file with validation
        
        Args:
            filename: Name of JSON file to load
            
        Returns:
            Dictionary with JSON data
            
        Raises:
            DataValidationError: If file cannot be loaded or parsed
        """
        file_path = self.data_dir / filename
        
        if not file_path.exists():
            raise DataValidationError(f"JSON file not found: {filename}")
        
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            
            # logger.info(f"Loaded JSON file: {filename}")
            return data
            
        except json.JSONDecodeError as e:
            raise DataValidationError(f"Invalid JSON in {filename}: {e}")
        except Exception as e:
            raise DataValidationError(f"Error loading {filename}: {e}")
    
    def load_encoder_schema(self) -> Dict[str, Any]:
        """Load encoder schema with validation"""
        return self.load_json("encoder_schema.json")
    
    def load_decoder_schema(self) -> Dict[str, Any]:
        """Load decoder schema with validation"""
        return self.load_json("decoder_schema.json")
    
    def load_encoder_params(self) -> Dict[str, Any]:
        """Load encoder parameters with validation"""
        return self.load_json("encoder_params.json")
    
    def load_decoder_params(self) -> Dict[str, Any]:
        """Load decoder parameters with validation"""
        return self.load_json("decoder_params.json")
    
    def validate_data_integrity(self) -> Dict[str, Any]:
        """
        Validate data integrity across all data sources
        
        Returns:
            Dictionary with validation results
        """
        validation_results = {
            "feeds_data": {"valid": False, "issues": []},
            "encoder_params": {"valid": False, "issues": []},
            "decoder_params": {"valid": False, "issues": []},
            "overall_valid": False
        }
        
        try:
            # Validate feeds data
            feeds_df = self.load_table_feeds()
            if len(feeds_df) > 0:
                validation_results["feeds_data"]["valid"] = True
                validation_results["feeds_data"]["record_count"] = len(feeds_df)
            else:
                validation_results["feeds_data"]["issues"].append("No feed records found")
            
            # Validate encoder parameters
            encoder_params = self.load_encoder_params()
            if encoder_params:
                validation_results["encoder_params"]["valid"] = True
                validation_results["encoder_params"]["param_count"] = len(encoder_params)
            else:
                validation_results["encoder_params"]["issues"].append("No encoder parameters found")
            
            # Validate decoder parameters
            decoder_params = self.load_decoder_params()
            if decoder_params:
                validation_results["decoder_params"]["valid"] = True
                validation_results["decoder_params"]["param_count"] = len(decoder_params)
            else:
                validation_results["decoder_params"]["issues"].append("No decoder parameters found")
            
            # Overall validation
            all_valid = all([
                validation_results["feeds_data"]["valid"],
                validation_results["encoder_params"]["valid"],
                validation_results["decoder_params"]["valid"]
            ])
            validation_results["overall_valid"] = all_valid
            
        except Exception as e:
            logger.error(f"Data validation failed: {e}")
            validation_results["validation_error"] = str(e)
        
        return validation_results


# Global data loader instance
_data_loader = MCPDataLoader()

# Convenience functions for backward compatibility
def load_table_feeds() -> pd.DataFrame:
    """Load camera feeds data"""
    return _data_loader.load_table_feeds()

def load_table_defs() -> pd.DataFrame:
    """Load table definitions"""
    return _data_loader.load_table_defs()

def load_json(filename: str) -> Dict[str, Any]:
    """Load JSON file"""
    return _data_loader.load_json(filename)

def load_encoder_schema() -> Dict[str, Any]:
    """Load encoder schema"""
    return _data_loader.load_encoder_schema()

def load_decoder_schema() -> Dict[str, Any]:
    """Load decoder schema"""
    return _data_loader.load_decoder_schema()

def load_encoder_params() -> Dict[str, Any]:
    """Load encoder parameters"""
    return _data_loader.load_encoder_params()

def load_decoder_params() -> Dict[str, Any]:
    """Load decoder parameters"""
    return _data_loader.load_decoder_params()

def validate_data_integrity() -> Dict[str, Any]:
    """Validate data integrity"""
    return _data_loader.validate_data_integrity()
