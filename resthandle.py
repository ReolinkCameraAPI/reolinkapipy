import json

import requests


class Request:
    proxies = None

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
            r = requests.post(url, verify=False, params=params, json=data, headers=headers, proxies=Request.proxies)
            # if params is not None:
            #     r = requests.post(url, params=params, json=data, headers=headers, proxies=proxies)
            # else:
            #     r = requests.post(url, json=data)
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
            data = requests.get(url=url, verify=False, params=params, timeout=timeout, proxies=Request.proxies)
            
            return data
        except Exception as e:
            print("Get Error\n", e)
            raise
