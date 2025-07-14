from openLibrary.constants import (
    BASE_DOMAIN,
    SLASH,
    TIMEOUT_CONFIG
)


import httpx
from typing import Optional
from urllib.parse import urlencode 


class OLBase:
    _client = httpx.Client(timeout=TIMEOUT_CONFIG, follow_redirects=True)

    @classmethod
    def _get(cls, path, subdomain: str =  None, params: dict = {}) -> httpx.Response:

        url = f"https://{subdomain + '.' if subdomain is not None else ''}{BASE_DOMAIN}/{path}"

        resp = cls._client.get(urlencode(url), params=params)
        resp.raise_for_status()
        return resp
    
    def _post():
        # TODO: support this at some point, 
        pass

   
    @classmethod
    def flatten(cls, data: list | dict) -> list:
        '''
        flattens a list of compound data types into a list of the values from the children
        '''
        if cls.is_flat(data):
            return data
        
        flat = []
        
        for _, d in enumerate(data if isinstance(data, list) else data.values()):
            if isinstance(d, str) and SLASH in d:
                d = cls.clean_slash(d)
            
            flat.append(d)

        return flat

    @classmethod
    def is_flat(cls, val: list | dict) -> bool:
        
        return all(not isinstance(v, (list, dict, tuple, set)) \
                for _, v in enumerate(val if isinstance(val, list) \
                                      else val.values() if isinstance(val, dict) else val))

    @classmethod
    def clean_slash(cls, val: str) -> str:
        if val.count('/') >= 2:
            return val.split('/')[-2]
                        

