#!/usr/bin/env python3
"""
Warning suppression module to be imported before other modules.
This helps suppress syntax warnings from third-party libraries.
"""

import warnings
import os
import sys

# Set environment variables to suppress warnings at the Python interpreter level
os.environ['PYTHONWARNINGS'] = 'ignore::SyntaxWarning,ignore::DeprecationWarning,ignore::UserWarning'

# Configure warnings filter before any other imports
warnings.filterwarnings("ignore", category=SyntaxWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", message="invalid escape sequence")
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

# Specifically target the problematic modules
warnings.filterwarnings("ignore", module="stringcase")
warnings.filterwarnings("ignore", module="rauth")
warnings.filterwarnings("ignore", module="rauth.service")
warnings.filterwarnings("ignore", module="rauth.session")

# Set up logging suppression
import logging

# Suppress specific loggers
logging.getLogger('PIL').setLevel(logging.WARNING)
logging.getLogger('PIL.PngImagePlugin').setLevel(logging.WARNING) 
logging.getLogger('rauth').setLevel(logging.ERROR)
logging.getLogger('stringcase').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('requests').setLevel(logging.WARNING)

print("Warning suppression configured successfully")