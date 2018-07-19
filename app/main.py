from flask import Flask

app = Flask(__name__)

from ppc_optimization.coa_ppc_bidder.coabidder_trainer import coabidder_trainer
from celery import Celery
import logging
from json_helper import JsonHelper
from account_helper import AccountHelper

app.config.update(
    # CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_BROKER_URL='pyamqp://guest@localhost//',
    CELERY_RESULT_BACKEND='rpc://'
)


def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


celery = make_celery(app)


@celery.task(name='main.add_together')
def add_together(a, b):
    import time
    time.sleep(5)
    print 'Got add together: %s %s' % (a, b)
    return a + b


@celery.task(name='main.train_async')
def train_async(account_id):
    print 'Started training: %s' % account_id
    coabidder_trainer(config_id=0, config_path_template='ppc_optimization/clients/config/config_trainer_ot_m_0.yml',
                      account_id=account_id)


@app.route("/")
def hello():
    return JsonHelper.build_action_response(None, "Hello World from Flask")


@app.route("/accounts/<account_id>/train", methods=['GET'])
def train(account_id):
    message = "Started training for: %s" % account_id
    logging.info(message)
    train_async.delay(account_id)
    account = AccountHelper.get_account_object(account_id)
    account['is_training'] = True
    return JsonHelper.build_action_response(account, message)


@app.route("/accounts/<account_id>/generate", methods=['GET'])
def generate(account_id):
    message = "Started generating bids for: %s" % account_id
    logging.info(message)
    train_async.delay(account_id)
    account = AccountHelper.get_account_object(account_id)
    account['is_generating_bids'] = True
    return JsonHelper.build_action_response(account, message)


@app.route("/accounts/<account_id>", methods=['GET'])
def account(account_id):
    return AccountHelper.get_account_json(account_id)


@app.route("/accounts", methods=['GET'])
def accounts():
    return JsonHelper.to_json([])


if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=True, port=80)
