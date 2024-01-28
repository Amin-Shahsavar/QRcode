# QRcode

1. Download zip file or clone the repository
2. create a venv inside the project directory
3. install the requirements.txt:
      pip install -r requirements.txt
5. create the local database:
      1. python manage.py makemigrations
      2. python manage.py migrate
6. create a SuperUser to use the admin panel of django:
      python manage.py createsuperuser
5. run the server:
      python manage.py runserver
6. go to this roat and enter the username and password:
      127.0.0.1:8000/admin
