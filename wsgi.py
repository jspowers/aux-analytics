import os
from app import create_app

# Determine environment
config_name = os.getenv('FLASK_ENV', 'development')
if config_name == 'production':
    config_name = 'production'
elif config_name == 'testing':
    config_name = 'testing'
else:
    config_name = 'development'

app = create_app(config_name)

if __name__ == '__main__':
    app.run(debug=True)
