# Project Setup

This document provides instructions for setting up the PowerCV project locally.

## Prerequisites
- Python 3.10 or higher
- Virtual environment tool (e.g., venv, poetry, or pipenv)
- Docker (optional, for containerized development)

## Steps
1. Clone the repository:
 bash
 git clone https://github.com/AnalyticAce/PowerCV.git
 cd PowerCV
 

2. Create and activate a virtual environment:
 bash
 python -m venv venv
 source venv/bin/activate # On Windows: venv\Scripts\activate
 

3. Install dependencies:
 bash
 pip install -r requirements.txt
 

4. Run the development server:
 bash
 python app/main.py
 

5. Access the application at http://127.0.0.1:8000.

For Docker setup, refer to the Dockerfile and docker-compose documentation.