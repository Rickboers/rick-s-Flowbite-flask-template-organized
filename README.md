![Project Screenshot](static\2024-12-30 06_41_57-Flowbite Flask - Brave.png)

commands to start:

1. Make new python virtual enviroment
2. pip install -r requirements.txt
3. npm install
4. npx tailwindcss -i ./static/src/input.css -o ./static/dist/css/output.css --watch
5. python run.py

Do flask db init once for the first time only and after you change the models.py only do flask db migrate and flask db upgrade:
flask db init
flask db migrate
flask db upgrade
