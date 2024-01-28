# QRcode

1. Download **zip file** or **clone** the repository.
2. Create a **venv** inside the project directory:
	> virtualenv venv
3. Start the venv:
	> source venv/bin/activate
5. Install the **requirements.txt**:
	> pip install -r requirements.txt
6. Create the local **database**:
	>python manage.py makemigrations
	>python manage.py migrate
7. Create a **SuperUser** to use the admin panel of Django:
	>python manage.py createsuperuser
8. Run the **server**:
	>python manage.py runserver
9. Go to this roat and enter the **username** and **password**:
	>127.0.0.1:8000/admin
