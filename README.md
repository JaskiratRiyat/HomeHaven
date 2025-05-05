HomeHaven 🏠

A web application built with Flask (Python) that connects users with trusted household service providers, including plumbing, electrical work, cleaning, and more.

Features
•	🔍 Browse Services: Search and filter a variety of household services.
•	📝 Book Appointments: Schedule and manage service bookings.
•	👤 User Authentication: Sign up, log in, and manage your profile.
•	⭐ Service Provider Ratings: Rate and review service providers.
•	📱 Responsive Design: Works seamlessly on desktop and mobile devices.

Installation
1.	Clone the repository
git clone https://github.com/yourusername/household-services-app.git

cd household-services-app

2.	Create and activate a virtual environment (recommended):

python -m venv venv

source venv/bin/activate  # On Windows: venv\Scripts\activate

3.	Install dependencies
pip install -r requirements.txt

4.	Set up environment variables
Create a .env file in the root directory and add:

FLASK_DEBUG=true

FLASK_APP=app.py

SQLALCHEMY_DATABASE_URI=sqlite:///db.sqlite3

SQLALCHEMY-TRACK-MODIFICATION=False

SECRET_KEY="your key :)"

6.	Run the app
python app.py

7.	Visit
http://127.0.0.1:5000/

Also attached a project report containing all other necessary facts about the project and a demonstration video :)



