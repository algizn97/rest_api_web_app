from sanic import Sanic, json
from sanic.log import logger
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.absolute()
sys.path.insert(0, str(BASE_DIR))

from database import init_db, create_test_data, dispose_db
from api.auth import auth_bp
from api.users import users_bp
from api.admin import admin_bp
from api.webhook import webhook_bp
from middleware import auth_middleware

app = Sanic("REST_API")

# Routes
app.blueprint(auth_bp, url_prefix='/api/auth')
app.blueprint(users_bp, url_prefix='/api/users')
app.blueprint(admin_bp, url_prefix='/api/admin')
app.blueprint(webhook_bp, url_prefix='/api/webhook')


@app.middleware("request")
async def apply_auth(request):
    await auth_middleware(request)


@app.get("/")
async def health_check(request):
    return json({"status": "OK", "message": "REST API ready!"})


@app.listener("before_server_start")
async def setup_db(app, loop):
    logger.info("Creating database...")
    await init_db()
    logger.info("Creating test database...")
    await create_test_data()
    logger.info("Database created successfully!")


@app.listener("after_server_stop")
async def teardown_db(app, loop):
    await dispose_db()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
