# QRcode

1. Download **zip file** or **clone** the repository
2. Create a **venv** inside the project directory
3. Install the **requirements.txt**:
        >pip install -r requirements.txt
5. Create the local database:
        >python manage.py makemigrations
        >python manage.py migrate
6. Create a SuperUser to use the admin panel of django:
        >python manage.py createsuperuser
5. Run the server:
        >python manage.py runserver
6. Go to this roat and enter the username and password:
        >127.0.0.1:8000/admin
