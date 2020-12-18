import requests
from typing import List, Dict, Union, Optional


class Request:
    proxies = None

    @staticmethod
    def post(url: str, data: List[Dict], params: Dict[str, Union[str, float]] = None) -> \
            Optional[requests.Response]:
        """
        Post request
        :param params:
        :param url:
        :param data:
        :return:
        """
        try:
            headers = {'content-type': 'application/json'}
            r = requests.post(url, verify=False, params=params, json=data, headers=headers,
                              proxies=Request.proxies)
            if r.status_code == 200:
                return r
            else:
                raise ValueError(f"Http Request had non-200 Status: {r.status_code}", r.status_code)
        except Exception as e:
            print("Post Error\n", e)
            raise

    @staticmethod
    def get(url: str, params: Dict[str, Union[str, float]], timeout: float = 1) -> Optional[requests.Response]:
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
