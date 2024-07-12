import os

# Define the project structure
project_structure = {
    "app": {
        "__init__.py": """
from flask import Flask
from .routes import main

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    app.register_blueprint(main)

    return app
""",
        "config.py": """
import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'mysecretkey')
""",
        "routes.py": """
from flask import Blueprint, jsonify
from .services.line_service import get_line_id

main = Blueprint('main', __name__)

@main.route('/env')
def get_env_variable():
    line_id = get_line_id()
    return jsonify({"lineId": line_id})
""",
        "services": {
            "__init__.py": "",
            "line_service.py": """
import os

def get_line_id():
    return os.getenv('lineId', 'Environment variable lineId not set')
"""
        },
        "templates": {
            "index.html": """
<!DOCTYPE html>
<html>
<head>
    <title>Flask App</title>
</head>
<body>
    <h1>Welcome to the Flask App!</h1>
</body>
</html>
"""
        }
    },
    "tests": {
        "__init__.py": "",
        "test_app.py": """
import unittest
from app import create_app

class BasicTests(unittest.TestCase):

    def setUp(self):
        self.app = create_app().test_client()
        self.app.testing = True

    def test_env_variable(self):
        response = self.app.get('/env')
        self.assertEqual(response.status_code, 200)
        self.assertIn('lineId', response.json)

if __name__ == "__main__":
    unittest.main()
"""
    },
    "run.py": """
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run()
""",
    ".env": "lineId=your_line_id_value\n",
    ".flaskenv": """
FLASK_APP=run.py
FLASK_ENV=development
"""
}

def create_project_structure(base_path, structure):
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_project_structure(path, content)
        else:
            with open(path, 'w') as file:
                file.write(content.strip() + '\n')

if __name__ == "__main__":
    project_base_path = os.getcwd()
    create_project_structure(project_base_path, project_structure)
    print(f"Project structure created successfully at {project_base_path}.")
