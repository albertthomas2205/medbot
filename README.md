OPEN-DROID

This project provides an ASGI-based server using Uvicorn, running on 0.0.0.0, and supporting WebSockets + background workers with Redis.

📥 Clone the Repository
git clone https://github.com/albertthomas2205/OPEN-DROID
cd OPEN-DROID/asgi_uk_medical_bot-main

🐍 Create & Activate Virtual Environment
Windows
python -m venv venv
venv\Scripts\activate

Linux / WSL
python3 -m venv venv
source venv/bin/activate

📦 Install Dependencies
pip install -r requirements.txt

🚀 Run ASGI Server
uvicorn asgi_uk_medical_bot.asgi:application --host 0.0.0.0 --port 8001


🧰 Redis Setup
If you are using WSL / Linux

Install Redis:

sudo apt update
sudo apt install redis-server


Start Redis:

redis-server

❗ If Redis is already installed

Just start the server:

redis-server --port 6380

🌐 Access the Application

Open this in browser:

http://localhost:8000


or access from your LAN:

http://<your-ip>:8000

✔ Summary
Step	Description
1	Clone repository
2	Create / activate virtual environment
3	Install dependencies
4	Run Uvicorn server
5	Install & start Redis
6	Access server from browser
