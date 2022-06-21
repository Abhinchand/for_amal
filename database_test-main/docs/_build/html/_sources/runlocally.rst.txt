==============================
Run Locally
==============================

To run Django locally.


You can run it via::


    pip install virtualenv
    virtualenv env source env/bin/activate

    git clone https://github.com/Amrithasuresh/BPPRC.git
    cd bpprc
    python manage.py makemigrations
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py loaddata example-data.json
    python manage.py runserver

Go to http://127.0.0.1:8000
