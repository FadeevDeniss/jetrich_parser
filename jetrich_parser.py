import re
import time

from datetime import datetime
from logging import Logger
from typing import Type

from base_http_client import BaseHttpClient
from conf import Settings
from utils import configure_task_logger, write_to_file


class JetrichParser(BaseHttpClient):
    auth_token: str = None

    AUTHORIZED: bool = False

    def __init__(self, settings: Type[Settings], headers: dict[str, str] = None):
        super().__init__()

        self.settings = settings
        self.logger: Logger = configure_task_logger(__name__, settings.BASE_DIR)
        self.session.headers.update(headers)

    def login(self):

        start_time = time.time()
        self.logger.info(f'Calling {self.login}, Start time: {start_time}')
        self.perform_request('https://jetrich.xyz/ru', to_json=False)

        username, password = self.settings.username, self.settings.password
        request_json = {
            "returnSecureToken": True,
            'email': username,
            'password': password,
            "clientType": "CLIENT_TYPE_WEB"
        }
        key = 'AIzaSyAqeAbaOXgU4gCSTpvCysERS2X2DVgfzEo'
        identity_response = self.perform_request(
            'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword',
            params={'key': key}, json=request_json
        )
        if 'idToken' not in identity_response:
            self.logger.error(msg='Could not receive id token')
            raise Exception('Wrong response from Jetrich API')

        auth_response = self.perform_request(
            'https://cloudfire.app/api/v1/auth/firebase',
            json={"token": identity_response['idToken'], "language": "ru"}
        )
        if 'token' not in auth_response:
            self.logger.error(msg='Could not receive auth token')
            raise Exception(f'Wrong response body: {auth_response}')

        self.auth_token = auth_response['token']

        accounts = self.perform_request(url='https://identitytoolkit.googleapis.com/v1/accounts:lookup',
                                        params={'key': key}, json={"idToken": identity_response['idToken']})

        last_login_at = accounts['users'][0]['lastLoginAt']
        last_login_dt = datetime.fromtimestamp(int(last_login_at) / 1000)

        self.AUTHORIZED = True
        self.logger.info(f'Successfully logged in at {last_login_dt}')
        self.logger.info(f'{self.login} finished execution, end time: {start_time - time.time()}')

    def load_winners(self, game_uuid: str):
        start_time = time.time()
        self.logger.info(f'Calling {self.load_winners}, Start time: {start_time}')
        response = self.perform_request(
            f'https://cloudfire.app/api/v1/games/{game_uuid}/session?locale=ru&demo=false',
            method='POST', auth_header=True
        )

        response = self.perform_request(response['href'], method='GET', to_json=False)
        mgckey = re.search(r'mgckey":"(.*)","style', response).group(1)

        params = {
            'symbol': 'vs20olympx',
            'mgckey': mgckey
        }

        details = self.perform_request(
            'https://2de6b6b8be.fhciaglolw.net/gs2c/promo/race/details/',
            params=params
        )

        race_id = details['details'][0]['id']
        winners_response = self.perform_request('https://2de6b6b8be.fhciaglolw.net/gs2c/promo/race/v3/winners/',
                                                params=params, json={"raceIds": [race_id]})

        write_to_file(f'winners_data_{game_uuid}.txt', winners_response['winners'][0]['items'])

        self.logger.info(f'Data loaded')
        self.logger.info(f'{self.load_winners} finished execution, end time: {start_time - time.time()}')
