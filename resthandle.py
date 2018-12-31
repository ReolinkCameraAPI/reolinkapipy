import json

import requests


class Request:

    @staticmethod
    def post(url: str, data, params=None) -> requests.Response or None:
        """
        Post request
        :param params:
        :param url:
        :param data:
        :return:
        """
        try:
            headers = {'content-type': 'application/json'}
            if params is not None:
                r = requests.post(url, params=params, json=data, headers=headers)
            else:
                r = requests.post(url, json=data)
            if r.status_code == 200:
                return r
            else:
                raise ValueError("Status: ", r.status_code)
        except Exception as e:
            print("Post Error\n", e)
            raise

    @staticmethod
    def get(url, params, timeout=1) -> json or None:
        """
        Get request
        :param url:
        :param params:
        :param timeout:
        :return:
        """
        try:
            data = requests.get(url=url, params=params, timeout=timeout)
            return data
        except Exception as e:
            print("Get Error\n", e)
            raise
