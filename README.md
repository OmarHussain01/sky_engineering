TO RUN THE PROJECT

# 1. Clone
git clone https://github.com/OmarHussain01/sky_engineering.git
cd sky_engineering

# 2. Create & activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate           # macOS/Linux
# .venv\Scripts\activate            # Windows (PowerShell)

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the server
python manage.py runserver

# 5. Open localhost
Go to your browser and write: localhost:8000
