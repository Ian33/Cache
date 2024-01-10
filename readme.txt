

To make requirements.txt
1. if requirements.txt exists delete it first (you may be able to update?)
2. run py -m pip freeze > requirements.txt

To create a virtual environment 
py -m venv venv 

activate venv 
.\venv\Scripts\activate 


this should install requirements.txt

pip install -r requirements.txt
 py -m pip install requirements.txt

 Note: you may have to use python, or python3 instead of py