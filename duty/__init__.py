from flask import Flask

import duty.routes.dashboard
import duty.routes.iris_cb_api
import duty.routes.datacenter_api
import duty.routes.longpoll_module_api
from duty.objects import db


def create_app():
    app = Flask(__name__)

    app.register_blueprint(duty.routes.dashboard.bp)
    app.register_blueprint(duty.routes.iris_cb_api.bp)
    app.register_blueprint(duty.routes.datacenter_api.bp)
    app.register_blueprint(duty.routes.longpoll_module_api.bp)

    @app.teardown_request
    def sync_db(_):
        db.sync()

    return app
