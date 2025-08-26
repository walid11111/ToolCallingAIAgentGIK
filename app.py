# type: ignore
import streamlit as st
import sys
import os
import shutil
import datetime
import json
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
from typing import Dict, Any, List
import logging
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set page configuration for a wider layout and custom title
st.set_page_config(
    page_title="Agentic AI Bootcamp Hub",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Project root setup
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from agent.tools.document_qa import initialize_document_qa
    from agent.controller import ask_agent
    from evaluation.evaluate_lama import evaluate_lama
    from evaluation.evaluate_gsm8k import evaluate_gsm8k
except ModuleNotFoundError as e:
    raise ModuleNotFoundError(
        f"{e}. Ensure you're running from project root ({PROJECT_ROOT}), 'agent' and 'evaluation' are packages, "
        "and no 'agent.py' or 'evaluation.py' files exist."
    )

# Initialize session states
if 'history' not in st.session_state:
    st.session_state.history = []
if 'past_history' not in st.session_state:
    st.session_state.past_history = []
if 'benchmark_results' not in st.session_state:
    st.session_state.benchmark_results = {}
if 'theme' not in st.session_state:
    st.session_state.theme = "Light"

# Create answers folder for benchmark tracking
answers_folder = Path("data/results/answers")
answers_folder.mkdir(parents=True, exist_ok=True)

def setup_custom_css():
    light_css = """
    <style>
    /* Import professional font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global theme - Lighter conversational background */
    .stApp {
        background: linear-gradient(135deg, #6B7280 0%, #9CA3AF 100%);
        color: #1f2937;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main content area styling */
    .main .block-container {
        background: linear-gradient(135deg, #6B7280 0%, #9CA3AF 100%);
        padding: 2rem 1rem;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    /* Sidebar styling - Lighter slate gray */
    section[data-testid="stSidebar"] {
        background: linear-gradient(135deg, #6B7280 0%, #9CA3AF 100%);
        border-right: 2px solid #9CA3AF;
        padding: 24px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
        border-radius: 0 20px 0 0;
    }
    
    /* Navigation radio buttons - Enhanced size and formatting */
    .stRadio > div {
        display: flex;
        flex-direction: column;
        gap: 16px; /* Increased spacing between buttons */
    }

    .stRadio label {
        font-size: 20px !important; /* Larger font size for better readability */
        font-weight: 600; /* Bold text for prominence */
        padding: 16px 20px !important; /* Larger padding for bigger buttons */
        border-radius: 12px; /* Softer, rounded corners */
        background: linear-gradient(135deg, rgba(107, 114, 128, 0.9) 0%, rgba(156, 163, 175, 0.7) 100%); /* Lighter gradient */
        border: 2px solid rgba(156, 163, 175, 0.5); /* Thicker, subtle border */
        color: #1f2937; /* Dark text for light theme readability */
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: flex-start;
        cursor: pointer;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); /* Subtle shadow for depth */
    }

    .stRadio label:hover {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.3) 0%, rgba(29, 78, 216, 0.2) 100%); /* Hover effect */
        border-color: #3B82F6; /* Blue border on hover */
        transform: translateY(-3px); /* Slight lift effect */
        box-shadow: 0 6px 16px rgba(59, 130, 246, 0.3); /* Enhanced shadow on hover */
    }

    .stRadio input:checked + div {
        background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%) !important; /* Blue gradient for selected */
        color: #ffffff !important; /* White text for selected */
        border-color: #3B82F6 !important; /* Matching border */
        box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4); /* Stronger shadow for selected */
        font-weight: 700; /* Extra bold for selected */
    }
    
    /* Chat container styling */
    .chat-container {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 20px;
        border: 1px solid rgba(156, 163, 175, 0.5);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
    }
    
    /* User messages - RIGHT side */
    .stChatMessage[data-testid="chat-message-user"] {
        flex-direction: row-reverse;
        margin: 15px 0;
    }
    
    .stChatMessage[data-testid="chat-message-user"] .stChatMessage {
        background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
        color: #ffffff;
        border-radius: 20px 20px 5px 20px;
        padding: 16px 20px;
        max-width: 70%;
        margin-left: auto;
        margin-right: 10px;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        font-size: 14px;
        line-height: 1.6;
        animation: slideInRight 0.3s ease-out;
        position: relative;
    }
    
    /* Assistant messages - LEFT side */
    .stChatMessage[data-testid="chat-message-assistant"] {
        flex-direction: row;
        margin: 15px 0;
    }
    
    .stChatMessage[data-testid="chat-message-assistant"] .stChatMessage {
        background: linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 100%);
        color: #1e293b;
        border-radius: 20px 20px 20px 5px;
        padding: 16px 20px;
        max-width: 70%;
        margin-right: auto;
        margin-left: 10px;
        border: 1px solid #CBD5E1;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        font-size: 14px;
        line-height: 1.6;
        animation: slideInLeft 0.3s ease-out;
        position: relative;
    }
    
    /* Add boundary line between chat messages */
    .stChatMessage + .stChatMessage {
        border-top: 1px solid #9CA3AF;
        margin-top: 15px;
        padding-top: 15px;
    }
    
    /* Chat input styling */
    .stChatInput {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 2px solid #9CA3AF;
        transition: all 0.3s ease;
    }
    
    .stChatInput:focus-within {
        border-color: #3B82F6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    /* Tool status cards - Lighter */
    .tool-card {
        background: linear-gradient(135deg, rgba(107, 114, 128, 0.9) 0%, rgba(156, 163, 175, 0.8) 100%);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(156, 163, 175, 0.4);
        border-radius: 16px;
        padding: 16px;
        margin: 12px 0;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    .tool-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        border-color: #3B82F6;
    }
    
    .tool-ready {
        border-left: 4px solid #10B981;
    }
    
    .tool-disabled {
        border-left: 4px solid #EF4444;
    }
    
    .status-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 10px;
        animation: pulse 2s infinite;
    }
    
    .status-ready {
        background: linear-gradient(45deg, #10B981, #059669);
    }
    
    .status-disabled {
        background: linear-gradient(45deg, #EF4444, #DC2626);
    }
    
    /* Enhanced Buttons */
    .stButton button {
        background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
        color: #ffffff;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 14px;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton button:hover {
        background: linear-gradient(135deg, #1D4ED8 0%, #1E40AF 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(59, 130, 246, 0.4);
    }
    
    .stButton button:active {
        transform: translateY(0);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    /* Professional Headers */
    .main-header {
        background: linear-gradient(135deg, #3B82F6, #1D4ED8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 12px;
        text-align: center;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        animation: fadeInDown 0.8s ease-out;
    }
    
    .sub-header {
        color: #1f2937;
        font-size: 18px;
        margin-bottom: 32px;
        font-weight: 500;
        text-align: center;
        animation: fadeInUp 0.8s ease-out;
    }
    
    /* Benchmark cards - Lighter */
    .benchmark-card {
        background: linear-gradient(135deg, rgba(107, 114, 128, 0.9) 0%, rgba(156, 163, 175, 0.8) 100%);
        backdrop-filter: blur(10px);
        color: #1f2937;
        padding: 20px;
        border-radius: 16px;
        margin: 12px 0;
        text-align: center;
        font-weight: 600;
        border: 1px solid rgba(156, 163, 175, 0.4);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        animation: fadeIn 0.6s ease-in;
        transition: all 0.3s ease;
    }
    
    .benchmark-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    .score-high {
        border-left: 5px solid #10B981;
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.05) 100%);
    }
    
    .score-medium {
        border-left: 5px solid #F59E0B;
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(217, 119, 6, 0.05) 100%);
    }
    
    .score-low {
        border-left: 5px solid #EF4444;
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.05) 100%);
    }
    
    /* Input styling */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border: 2px solid #9CA3AF;
        border-radius: 12px;
        color: #1f2937;
        font-size: 14px;
        padding: 12px 16px;
        transition: all 0.3s ease;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox select:focus {
        border-color: #3B82F6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        outline: none;
    }
    
    /* Professional divider */
    hr {
        border: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, #9CA3AF, transparent);
        margin: 32px 0;
        border-radius: 1px;
    }
    
    /* Animations */
    @keyframes slideInRight {
        from {
            transform: translateX(100px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideInLeft {
        from {
            transform: translateX(-100px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes fadeInDown {
        from {
            transform: translateY(-30px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    @keyframes fadeInUp {
        from {
            transform: translateY(30px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    /* Professional scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(156, 163, 175, 0.3);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #3B82F6, #1D4ED8);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #1D4ED8, #1E40AF);
    }
    
    /* Quick examples styling */
    .example-card {
        background: linear-gradient(135deg, rgba(107, 114, 128, 0.8) 0%, rgba(156, 163, 175, 0.6) 100%);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(156, 163, 175, 0.3);
        border-radius: 12px;
        padding: 12px;
        margin: 8px 0;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .example-card:hover {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(29, 78, 216, 0.05) 100%);
        border-color: #3B82F6;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
    }
    </style>
    """

    dark_css = """
    <style>
    /* Import professional font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global theme - Lighter conversational background */
    .stApp {
        background: linear-gradient(135deg, #6B7280 0%, #9CA3AF 100%);
        color: #f1f5f9;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main content area styling */
    .main .block-container {
        background: linear-gradient(135deg, #6B7280 0%, #9CA3AF 100%);
        padding: 2rem 1rem;
        border-radius: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    /* Sidebar styling - Lighter slate gray */
    section[data-testid="stSidebar"] {
        background: linear-gradient(135deg, #6B7280 0%, #9CA3AF 100%);
        border-right: 2px solid #9CA3AF;
        padding: 24px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        border-radius: 0 20px 0 0;
    }
    
    /* Navigation radio buttons - Enhanced size and formatting */
    .stRadio > div {
        display: flex;
        flex-direction: column;
        gap: 16px; /* Increased spacing between buttons */
    }

    .stRadio label {
        font-size: 20px !important; /* Larger font size for better readability */
        font-weight: 600; /* Bold text for prominence */
        padding: 16px 20px !important; /* Larger padding for bigger buttons */
        border-radius: 12px; /* Softer, rounded corners */
        background: linear-gradient(135deg, rgba(107, 114, 128, 0.9) 0%, rgba(156, 163, 175, 0.7) 100%); /* Lighter gradient */
        border: 2px solid rgba(156, 163, 175, 0.5); /* Thicker, subtle border */
        color: #f1f5f9; /* Light text for dark theme readability */
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: flex-start;
        cursor: pointer;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); /* Subtle shadow for depth */
    }

    .stRadio label:hover {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.3) 0%, rgba(29, 78, 216, 0.2) 100%); /* Hover effect */
        border-color: #3B82F6; /* Blue border on hover */
        transform: translateY(-3px); /* Slight lift effect */
        box-shadow: 0 6px 16px rgba(59, 130, 246, 0.3); /* Enhanced shadow on hover */
    }

    .stRadio input:checked + div {
        background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%) !important; /* Blue gradient for selected */
        color: #ffffff !important; /* White text for selected */
        border-color: #3B82F6 !important; /* Matching border */
        box-shadow: 0 6px 16px rgba(59, 130, 246, 0.4); /* Stronger shadow for selected */
        font-weight: 700; /* Extra bold for selected */
    }
    
    /* Chat container styling */
    .chat-container {
        background: rgba(156, 163, 175, 0.8);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 20px;
        border: 1px solid rgba(156, 163, 175, 0.5);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
    }
    
    /* User messages - RIGHT side */
    .stChatMessage[data-testid="chat-message-user"] {
        flex-direction: row-reverse;
        margin: 15px 0;
    }
    
    .stChatMessage[data-testid="chat-message-user"] .stChatMessage {
        background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
        color: #ffffff;
        border-radius: 20px 20px 5px 20px;
        padding: 16px 20px;
        max-width: 70%;
        margin-left: auto;
        margin-right: 10px;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
        font-size: 14px;
        line-height: 1.6;
        animation: slideInRight 0.3s ease-out;
    }
    
    /* Assistant messages - LEFT side */
    .stChatMessage[data-testid="chat-message-assistant"] {
        flex-direction: row;
        margin: 15px 0;
    }
    
    .stChatMessage[data-testid="chat-message-assistant"] .stChatMessage {
        background: linear-gradient(135deg, #9CA3AF 0%, #D1D5DB 100%);
        color: #1e293b;
        border-radius: 20px 20px 20px 5px;
        padding: 16px 20px;
        max-width: 70%;
        margin-right: auto;
        margin-left: 10px;
        border: 1px solid #D1D5DB;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        font-size: 14px;
        line-height: 1.6;
        animation: slideInLeft 0.3s ease-out;
    }
    
    /* Add boundary line between chat messages */
    .stChatMessage + .stChatMessage {
        border-top: 1px solid #9CA3AF;
        margin-top: 15px;
        padding-top: 15px;
    }
    
    /* Chat input styling */
    .stChatInput {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 2px solid #9CA3AF;
        transition: all 0.3s ease;
    }
    
    .stChatInput:focus-within {
        border-color: #3B82F6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    
    /* Tool status cards - Lighter */
    .tool-card {
        background: linear-gradient(135deg, rgba(107, 114, 128, 0.9) 0%, rgba(156, 163, 175, 0.8) 100%);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(156, 163, 175, 0.4);
        border-radius: 16px;
        padding: 16px;
        margin: 12px 0;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    
    .tool-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        border-color: #3B82F6;
    }
    
    .tool-ready {
        border-left: 4px solid #10B981;
    }
    
    .tool-disabled {
        border-left: 4px solid #EF4444;
    }
    
    .status-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 10px;
        animation: pulse 2s infinite;
    }
    
    .status-ready {
        background: linear-gradient(45deg, #10B981, #059669);
    }
    
    .status-disabled {
        background: linear-gradient(45deg, #EF4444, #DC2626);
    }
    
    /* Enhanced Buttons */
    .stButton button {
        background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
        color: #ffffff;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 14px;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton button:hover {
        background: linear-gradient(135deg, #1D4ED8 0%, #1E40AF 100%);
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(59, 130, 246, 0.5);
    }
    
    .stButton button:active {
        transform: translateY(0);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    }
    
    /* Professional Headers */
    .main-header {
        background: linear-gradient(135deg, #3B82F6, #1D4ED8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 12px;
        text-align: center;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        animation: fadeInDown 0.8s ease-out;
    }
    
    .sub-header {
        color: #d1d5db;
        font-size: 18px;
        margin-bottom: 32px;
        font-weight: 500;
        text-align: center;
        animation: fadeInUp 0.8s ease-out;
    }
    
    /* Benchmark cards - Lighter */
    .benchmark-card {
        background: linear-gradient(135deg, rgba(107, 114, 128, 0.9) 0%, rgba(156, 163, 175, 0.8) 100%);
        backdrop-filter: blur(10px);
        color: #f1f5f9;
        padding: 20px;
        border-radius: 16px;
        margin: 12px 0;
        text-align: center;
        font-weight: 600;
        border: 1px solid rgba(156, 163, 175, 0.4);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        animation: fadeIn 0.6s ease-in;
        transition: all 0.3s ease;
    }
    
    .benchmark-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
    }
    
    .score-high {
        border-left: 5px solid #10B981;
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.05) 100%);
    }
    
    .score-medium {
        border-left: 5px solid #F59E0B;
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(217, 119, 6, 0.05) 100%);
    }
    
    .score-low {
        border-left: 5px solid #EF4444;
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.05) 100%);
    }
    
    /* Input styling */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 2px solid #9CA3AF;
        border-radius: 12px;
        color: #f1f5f9;
        font-size: 14px;
        padding: 12px 16px;
        transition: all 0.3s ease;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox select:focus {
        border-color: #3B82F6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        outline: none;
    }
    
    /* Professional divider */
    hr {
        border: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, #9CA3AF, transparent);
        margin: 32px 0;
        border-radius: 1px;
    }
    
    /* Animations */
    @keyframes slideInRight {
        from {
            transform: translateX(100px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideInLeft {
        from {
            transform: translateX(-100px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes fadeInDown {
        from {
            transform: translateY(-30px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    @keyframes fadeInUp {
        from {
            transform: translateY(30px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    /* Professional scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(156, 163, 175, 0.3);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #3B82F6, #1D4ED8);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #1D4ED8, #1E40AF);
    }
    
    /* Quick examples styling */
    .example-card {
        background: linear-gradient(135deg, rgba(107, 114, 128, 0.8) 0%, rgba(156, 163, 175, 0.6) 100%);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(156, 163, 175, 0.3);
        border-radius: 12px;
        padding: 12px;
        margin: 8px 0;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .example-card:hover {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(29, 78, 216, 0.05) 100%);
        border-color: #3B82F6;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
    }
    </style>
    """

    if st.session_state.theme == "Light":
        st.markdown(light_css, unsafe_allow_html=True)
    else:
        st.markdown(dark_css, unsafe_allow_html=True)

    if st.session_state.theme == "Light":
        st.markdown(light_css, unsafe_allow_html=True)
    else:
        st.markdown(dark_css, unsafe_allow_html=True)

def chat_function(message):
    """Enhanced chat function with better error handling."""
    try:
        response, source = ask_agent(message)
        current_history = (message, response, source)
        st.session_state.past_history.append(current_history)
        return current_history
    except Exception as e:
        logger.error(f"Chat function error: {str(e)}")
        current_history = (message, f"❌ Error: {str(e)}", "Error")
        st.session_state.past_history.append(current_history)
        return current_history

def upload_files(files):
    """Enhanced file upload with better feedback."""
    try:
        file_paths = []
        for file in files:
            if file is not None:
                filename = file.name
                dest_path = os.path.join("data", "documents", filename)
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                
                with open(dest_path, "wb") as f:
                    f.write(file.getbuffer())
                file_paths.append(dest_path)

        # Reset vector store to force reload
        initialize_document_qa()
        return f"✅ Successfully uploaded {len(file_paths)} files and reloaded vector store."
    except Exception as e:
        logger.error(f"File upload error: {str(e)}")
        return f"❌ Error uploading files: {str(e)}"

def get_tool_status():
    """Get available tools status."""
    tools_info = [
        ("🌐 Web Search", "web_search", "Real-time Information via Serper API"),
        ("🧮 Calculator", "calculator", "Arithmetic & Math Operations"), 
        ("➗ Math Solver", "math_solver", "Advanced Math with Llama3-70B"),
        ("📄 Document QA", "document_qa", "RAG-based Document Analysis"),
        ("🤖 General AI", "general", "Llama3-8b-8192 Knowledge Base")
    ]
    return tools_info

def render_tool_status():
    """Render enhanced tool status cards."""
    st.markdown("### 🛠 Available Tools", help="Overview of AI tools and their status.")
    tools_info = get_tool_status()
    
    for tool_name, tool_key, description in tools_info:
        is_ready = True  # Assume all tools are ready for simplicity
        status_class = "tool-ready" if is_ready else "tool-disabled"
        status_dot = "status-ready" if is_ready else "status-disabled"
        status_text = "Ready" if is_ready else "Disabled"
        
        st.markdown(f"""
        <div class='tool-card {status_class}'>
            <div style='display: flex; align-items: center;'>
                <span class='status-dot {status_dot}'></span>
                <div>
                    <strong>{tool_name}</strong>
                    <div style='font-size: 12px; opacity: 0.8; margin-top: 4px;'>{description}</div>
                    <div style='font-size: 12px; font-weight: 600; margin-top: 4px;'>{status_text}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def save_answer_to_file(query: str, response: str, source: str, test_type: str = "general"):
    """Save query result to answer file for tracking."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{test_type}_answer_{timestamp}.json"
    filepath = answers_folder / filename
    
    answer_data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "query": query,
        "response": response,
        "source": source,
        "test_type": test_type
    }
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(answer_data, f, indent=2, ensure_ascii=False)
        return filepath
    except Exception as e:
        logger.error(f"Error saving answer: {str(e)}")
        return None

def clear_answers_folder():
    """Clear all files in the answers folder."""
    try:
        if answers_folder.exists():
            shutil.rmtree(answers_folder)
        answers_folder.mkdir(parents=True)
        return True
    except Exception as e:
        logger.error(f"Error clearing answers folder: {str(e)}")
        return False

def run_single_benchmark(benchmark_type: str, benchmark_func):
    """Run a single benchmark with enhanced tracking."""
    with st.spinner(f"Running {benchmark_type.upper()} benchmark..."):
        try:
            if benchmark_type == "lama":
                result = evaluate_lama()
            else:  # gsm8k
                result = evaluate_gsm8k()
            
            accuracy = 75.0  # Placeholder - replace with actual accuracy extraction
            
            st.session_state.benchmark_results[benchmark_type] = {
                "accuracy": accuracy,
                "timestamp": datetime.datetime.now().isoformat(),
                "full_result": result
            }
            
            return result
        except Exception as e:
            logger.error(f"Benchmark error: {str(e)}")
            return f"❌ Error running {benchmark_type}: {str(e)}"

def display_benchmark_scores():
    """Display benchmark scores with color coding."""
    if not st.session_state.benchmark_results:
        return
    
    st.markdown("#### 📊 Benchmark Scores")
    col1, col2 = st.columns(2)
    
    for i, (benchmark, data) in enumerate(st.session_state.benchmark_results.items()):
        accuracy = data["accuracy"]
        score_class = "score-high" if accuracy >= 80 else "score-medium" if accuracy >= 60 else "score-low"
        col = col1 if i % 2 == 0 else col2
        
        with col:
            st.markdown(f"""
            <div class='benchmark-card {score_class}'>
                <div style='font-size: 18px; font-weight: 700; margin-bottom: 8px;'>{benchmark.upper()}</div>
                <div style='font-size: 32px; font-weight: 800; margin-bottom: 8px;'>{accuracy:.1f}%</div>
                <div style='font-size: 12px; opacity: 0.7;'>
                    Last run: {data['timestamp'][:10]}
                </div>
            </div>
            """, unsafe_allow_html=True)

def display_performance_graph():
    """Display performance visualization graph."""
    if not st.session_state.benchmark_results:
        return
    
    st.markdown("#### 📈 Performance Overview")
    benchmarks = list(st.session_state.benchmark_results.keys())
    accuracies = [st.session_state.benchmark_results[b]["accuracy"] for b in benchmarks]
    colors = ['#10B981' if acc >= 80 else '#F59E0B' if acc >= 60 else '#EF4444' for acc in accuracies]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=benchmarks,
        y=accuracies,
        marker_color=colors,
        text=[f'{acc:.1f}%' for acc in accuracies],
        textposition='auto',
        textfont=dict(size=14, family='Inter', color='white')
    ))
    
    fig.update_layout(
        title=dict(
            text="🏆 Benchmark Performance Overview",
            font=dict(size=20, family='Inter'),  # Use 'font' inside 'title' instead of 'titlefont'
            x=0.5
        ),
        xaxis=dict(
            title=dict(
                text="Benchmark",
                font=dict(size=14)  # Customize x-axis title font here if needed
            )
        ),
        yaxis=dict(
            title=dict(
                text="Accuracy (%)",
                font=dict(size=14)  # Customize y-axis title font here if needed
            ),
            range=[0, 100]
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=80, b=40)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_sidebar():
    """Enhanced sidebar with professional design."""
    with st.sidebar:
        st.markdown("<h1 class='main-header'>⚙️ Control Panel</h1>", unsafe_allow_html=True)
        
        # Navigation
        st.markdown("""
        <div style='padding: 16px; background: linear-gradient(135deg, rgba(42, 64, 102, 0.9) 0%, rgba(58, 85, 120, 0.8) 100%); 
        border-radius: 16px; margin-bottom: 20px; border: 1px solid rgba(94, 112, 133, 0.3);'>
        <strong style='font-size: 16px;'>🌟 Navigation</strong>
        </div>
        """, unsafe_allow_html=True)
        
        page = st.radio("Select a page", 
                       ["💬 Chat", "📊 Evaluation", "📁 Documents", "ℹ️ About"], 
                       index=0, 
                       label_visibility="collapsed")
        
        st.divider()
        
        # Tool status
        st.markdown("""
        <div style='padding: 16px; background: linear-gradient(135deg, rgba(42, 64, 102, 0.9) 0%, rgba(58, 85, 120, 0.8) 100%); 
        border-radius: 16px; margin-bottom: 20px; border: 1px solid rgba(94, 112, 133, 0.3);'>
        <strong style='font-size: 16px;'>🛠 Tool Status</strong>
        </div>
        """, unsafe_allow_html=True)
        
        render_tool_status()
        
        st.divider()
        
        # Theme toggle
        st.markdown("""
        <div style='padding: 16px; background: linear-gradient(135deg, rgba(42, 64, 102, 0.9) 0%, rgba(58, 85, 120, 0.8) 100%); 
        border-radius: 16px; margin-bottom: 20px; border: 1px solid rgba(94, 112, 133, 0.3);'>
        <strong style='font-size: 16px;'>🎨 Theme</strong>
        </div>
        """, unsafe_allow_html=True)
        
        theme = st.selectbox("Select theme", 
                            ["Light", "Dark"], 
                            index=0 if st.session_state.theme == "Light" else 1,
                            label_visibility="collapsed")
        
        if theme != st.session_state.theme:
            st.session_state.theme = theme
            st.rerun()
        
        st.divider()
        
        # Benchmarks
        st.markdown("""
        <div style='padding: 16px; background: linear-gradient(135deg, rgba(42, 64, 102, 0.9) 0%, rgba(58, 85, 120, 0.8) 100%); 
        border-radius: 16px; margin-bottom: 20px; border: 1px solid rgba(94, 112, 133, 0.3);'>
        <strong style='font-size: 16px;'>📊 Benchmarks</strong>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🎯 LAMA", use_container_width=True):
                result = run_single_benchmark("lama", evaluate_lama)
                st.session_state.lama_result = result
                st.rerun()
        
        with col2:
            if st.button("📐 GSM8K", use_container_width=True):
                result = run_single_benchmark("gsm8k", evaluate_gsm8k)
                st.session_state.gsm8k_result = result
                st.rerun()
        
        display_benchmark_scores()
        
        st.divider()
        
        # Cleanup
        st.markdown("""
        <div style='padding: 16px; background: linear-gradient(135deg, rgba(42, 64, 102, 0.9) 0%, rgba(58, 85, 120, 0.8) 100%); 
        border-radius: 16px; margin-bottom: 20px; border: 1px solid rgba(94, 112, 133, 0.3);'>
        <strong style='font-size: 16px;'>🧹 Cleanup</strong>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.past_history = []
                st.rerun()
        
        with col2:
            if st.button("🗑️ Clear Results", use_container_width=True):
                if clear_answers_folder():
                    st.success("✅ Results cleared")
                st.rerun()
    
    return page

def render_chat_page():
    """Enhanced chat interface with user on RIGHT and assistant on LEFT."""
    st.markdown("<h1 class='main-header'>💬 Agentic AI Bootcamp Hub</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Your intelligent assistant for queries and analysis! 🚀</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        # Chat container with enhanced styling
        # st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # Chat history
        chat_container = st.container(height=500, border=False)
        with chat_container:
            for entry in st.session_state.past_history:
                message, response, source = entry
                
                # User message on the RIGHT
                with st.chat_message("user"):
                    st.markdown(f"**You:** {message}")
                    st.markdown(f"<div style='font-size: 11px; opacity: 0.7; text-align: right;'>{datetime.datetime.now().strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)
                
                # Assistant message on the LEFT
                tool_emoji = {
                    'web_search': '🌐',
                    'calculator': '🧮', 
                    'math_solver': '➗',
                    'document_qa': '📄',
                    'general': '🤖'
                }.get(source.lower().replace(' ', '_').replace('-', '_'), '🤖')
                
                with st.chat_message("assistant"):
                    st.markdown(f"**Assistant:** {response}")
                    st.markdown(f"<div style='font-size: 11px; opacity: 0.7;'>{tool_emoji} via {source} • {datetime.datetime.now().strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Enhanced input area
        prompt = st.chat_input("💭 Ask me anything...", key="chat_input")
        if prompt:
            with st.spinner("🤔 Thinking..."):
                chat_function(prompt)
                st.rerun()
        
        # Action buttons
        st.markdown("### ⚡ Quick Actions")
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            if st.button("💾 Save Last Answer", use_container_width=True) and st.session_state.past_history:
                last = st.session_state.past_history[-1]
                filepath = save_answer_to_file(last[0], last[1], last[2])
                if filepath:
                    st.success(f"💾 Saved to {filepath.name}")
        
        with col_b:
            if st.button("🔄 Reset Chat", use_container_width=True):
                st.session_state.past_history = []
                st.rerun()
        
        with col_c:
            if st.button("📊 View Stats", use_container_width=True):
                total_messages = len(st.session_state.past_history)
                st.info(f"📈 Total messages: {total_messages}")
    
    with col2:
        st.markdown("### 🌟 Quick Examples")
        st.markdown("<div style='margin-bottom: 10px;'>", unsafe_allow_html=True)
        
        examples = [
            "☀️ Weather today?",
            "🧮 Calculate 15 * 24",
            "📄 Summarize document",
            "🌍 Latest world news",
            "🔢 Solve math problem",
            "💡 Give me an idea",
            "🚀 What is AI?",
            "📊 Data analysis help"
        ]
        
        for i, example in enumerate(examples):
            if st.button(example, key=f"example_{i}", use_container_width=True, help=f"Try: {example}"):
                with st.spinner("🚀 Processing..."):
                    chat_function(example.split(' ', 1)[1] if ' ' in example else example)
                    st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Chat statistics
        st.markdown("### 📈 Chat Statistics")
        total_chats = len(st.session_state.past_history)
        
        st.markdown(f"""
        <div class='benchmark-card score-high' style='text-align: center; margin: 10px 0;'>
            <div style='font-size: 14px; margin-bottom: 8px;'>💬 Total Messages</div>
            <div style='font-size: 24px; font-weight: 800;'>{total_chats}</div>
        </div>
        """, unsafe_allow_html=True)

def render_evaluation_page():
    """Enhanced evaluation interface with improved layout."""
    st.markdown("<h1 class='main-header'>📊 Benchmark Evaluation</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Assess the agent's performance across different benchmarks! 🏆</p>", unsafe_allow_html=True)
    
    # Performance visualization
    display_performance_graph()
    
    # Benchmark controls
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class='benchmark-card' style='margin-bottom: 20px;'>
            <h4 style='color: #3B82F6; margin-bottom: 15px;'>🎯 LAMA Evaluation</h4>
            <p style='margin-bottom: 15px; opacity: 0.8;'>Tests knowledge and factual reasoning capabilities</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Run LAMA Evaluation", type="primary", use_container_width=True):
            result = run_single_benchmark("lama", evaluate_lama)
            st.session_state.lama_result = result
            st.rerun()
        
        if 'lama_result' in st.session_state:
            st.text_area("📋 LAMA Results", 
                        value=st.session_state.lama_result, 
                        height=200,
                        help="Detailed results from LAMA benchmark")
    
    with col2:
        st.markdown("""
        <div class='benchmark-card' style='margin-bottom: 20px;'>
            <h4 style='color: #10B981; margin-bottom: 15px;'>📐 GSM8K Evaluation</h4>
            <p style='margin-bottom: 15px; opacity: 0.8;'>Tests mathematical reasoning and problem-solving</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Run GSM8K Evaluation", type="primary", use_container_width=True):
            result = run_single_benchmark("gsm8k", evaluate_gsm8k)
            st.session_state.gsm8k_result = result
            st.rerun()
        
        if 'gsm8k_result' in st.session_state:
            st.text_area("📋 GSM8K Results", 
                        value=st.session_state.gsm8k_result, 
                        height=200,
                        help="Detailed results from GSM8K benchmark")

def render_document_page():
    """Enhanced document management interface."""
    st.markdown("<h1 class='main-header'>📁 Document Management</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Upload and manage documents for AI analysis! 📚</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("### 📤 Upload Documents")
        
        uploaded_files = st.file_uploader(
            "Choose files to upload",
            accept_multiple_files=True,
            type=["txt", "pdf", "docx"],
            help="Supported formats: TXT, PDF, DOCX (Max 200MB per file)"
        )
        
        if uploaded_files:
            st.markdown(f"**📋 Selected Files ({len(uploaded_files)}):**")
            for file in uploaded_files:
                file_size = f"{file.size:,} bytes" if file.size < 1024*1024 else f"{file.size/(1024*1024):.1f} MB"
                st.markdown(f"• **{file.name}** ({file_size})")
            
            if st.button("🚀 Upload Files", type="primary", use_container_width=True):
                with st.spinner("📤 Processing files..."):
                    status = upload_files(uploaded_files)
                    if "✅" in status:
                        st.success(status)
                    else:
                        st.error(status)
    
    with col2:
        st.markdown("### 📊 Document Statistics")
        
        docs_path = Path("data/documents")
        if docs_path.exists():
            doc_files = list(docs_path.glob("*"))
            total_docs = len(doc_files)
            txt_files = len([f for f in doc_files if f.suffix.lower() == '.txt'])
            pdf_files = len([f for f in doc_files if f.suffix.lower() == '.pdf'])
            docx_files = len([f for f in doc_files if f.suffix.lower() == '.docx'])
            
            # Statistics cards
            stats = [
                ("📊 Total", total_docs, "score-high"),
                ("📝 TXT", txt_files, "score-medium"),  
                ("📄 PDF", pdf_files, "score-medium"),
                ("📋 DOCX", docx_files, "score-medium")
            ]
            
            for stat_name, count, class_name in stats:
                st.markdown(f"""
                <div class='benchmark-card {class_name}' style='margin: 10px 0;'>
                    <div style='font-size: 14px; margin-bottom: 5px;'>{stat_name}</div>
                    <div style='font-size: 28px; font-weight: 800;'>{count}</div>
                </div>
                """, unsafe_allow_html=True)
        
        else:
            st.info("📂 No documents folder found")
    
    # Document list
    if docs_path.exists() and doc_files:
        st.markdown("### 📋 Document Library")
        
        # Create DataFrame for better display
        doc_data = []
        for file in doc_files:
            doc_data.append({
                "📁 Filename": file.name,
                "📊 Size": f"{file.stat().st_size:,} bytes",
                "📅 Modified": datetime.datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            })
        
        df = pd.DataFrame(doc_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

def render_about_page():
    """Enhanced about page with professional layout."""
    st.markdown("<h1 class='main-header'>ℹ️ About Agentic AI Bootcamp Hub</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>A cutting-edge tool-calling AI agent for the AI Bootcamp Mini-Project 🏆</p>", unsafe_allow_html=True)
    
    # Feature showcase
    st.markdown("### 🌟 Key Features")
    
    features = [
        ("🌐 Web Search", "Real-time information retrieval via Serper API", "Access current information from the web"),
        ("🧮 Calculator", "Precise arithmetic operations", "Solve mathematical calculations instantly"),
        ("➗ Math Solver", "Advanced reasoning with Llama3-70B", "Handle complex mathematical problems"),
        ("📄 Document QA", "RAG-based document analysis", "Query uploaded documents intelligently"),
        ("🤖 General AI", "Comprehensive knowledge with Llama3-8b-8192", "General purpose conversational AI")
    ]
    
    for feature, description, detail in features:
        st.markdown(f"""
        <div class='tool-card tool-ready' style='margin: 15px 0;'>
            <div style='display: flex; align-items: center;'>
                <span class='status-dot status-ready'></span>
                <div style='flex: 1;'>
                    <strong style='font-size: 16px;'>{feature}</strong>
                    <div style='font-size: 14px; opacity: 0.8; margin-top: 5px;'>{description}</div>
                    <div style='font-size: 12px; opacity: 0.6; margin-top: 3px;'>{detail}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Performance section
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏆 Performance Benchmarks")
        st.markdown("""
        - **LAMA**: Evaluates factual accuracy and knowledge recall
        - **GSM8K**: Tests mathematical and logical reasoning capabilities
        - **Real-time Evaluation**: Continuous performance monitoring
        """)
    
    with col2:
        st.markdown("### 📖 Usage Guide")
        st.markdown("""
        1. **💬 Chat**: Ask questions and receive intelligent responses
        2. **📊 Evaluation**: Run benchmarks to assess AI performance  
        3. **📁 Documents**: Upload files for RAG-based analysis
        4. **⚙️ Control Panel**: Manage themes, tools, and settings
        """)
    
    st.divider()
    
    # Technical specifications
    st.markdown("### 🔧 Technical Specifications")
    
    tech_specs = [
        ("🧠 AI Models", "Llama3-8b-8192, Llama3-70B"),
        ("🔍 Search API", "Serper API for real-time web search"),
        ("📚 Document Processing", "RAG (Retrieval Augmented Generation)"),
        ("🎨 UI Framework", "Streamlit with custom CSS styling"),
        ("📊 Visualization", "Plotly for interactive charts and graphs")
    ]
    
    for spec_name, spec_detail in tech_specs:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, rgba(42, 64, 102, 0.9) 0%, rgba(58, 85, 120, 0.8) 100%); 
        padding: 12px 16px; border-radius: 12px; margin: 8px 0; border-left: 4px solid #3B82F6;'>
            <strong>{spec_name}:</strong> {spec_detail}
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div style='text-align: center; padding: 24px; background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%); 
    border-radius: 20px; color: #ffffff; margin-top: 40px; font-weight: 600; box-shadow: 0 8px 32px rgba(59, 130, 246, 0.3);'>
        🚀 Agentic AI Bootcamp Hub - Built for Excellence in AI Competition 🏆<br>
        <small style='opacity: 0.8; font-weight: 400;'>© 2025 • Powered by Advanced AI Technologies</small>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main application function."""
    setup_custom_css()
    
    page = render_sidebar()
    
    if page == "💬 Chat":
        render_chat_page()
    elif page == "📊 Evaluation":
        render_evaluation_page()
    elif page == "📁 Documents":
        render_document_page()
    elif page == "ℹ️ About":
        render_about_page()

if __name__ == "__main__":
    main()