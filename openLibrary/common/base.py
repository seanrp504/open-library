import httpx
from urllib.parse import urlencode
import logging
import json

from openLibrary.constants import (
    BASE_DOMAIN,
    SLASH,
    TIMEOUT_CONFIG,
    DEFAULT_LEVEL,
    CONSOLE_HANDLER,
    FILE_HANDLER
)



logger = logging.getLogger(__name__)
logger.setLevel(DEFAULT_LEVEL)
logger.addHandler(CONSOLE_HANDLER)
logger.addHandler(FILE_HANDLER) if FILE_HANDLER else None


class OLBase:
    _client = httpx.Client(timeout=TIMEOUT_CONFIG, follow_redirects=True)

    @classmethod
    def __get(cls, path, subdomain: str =  None, params: dict = {}) -> httpx.Response:

        url = f"https://{subdomain + '.' if subdomain is not None else ''}{BASE_DOMAIN}/{path}"

        logger.info(f"GET: {urlencode(url)}")
        logger.debug(F"pararms: {json.dumps(params, indent=2, sort_keys=True)}")

        resp = cls._client.get(urlencode(url), params=params)
        
        try:
            resp.raise_for_status()

        except Exception as e:
            logger.error(f"Error in GET: {e.with_traceback()}")
            raise e
        
        finally:
            logger.info(f"GET: time elasped {resp.elapsed}")
            logger.debug(f"GET: recieved {resp.num_bytes_downloaded} bytes")
        
        return resp
    
    def __post():
        # TODO: support this at some point, 
        raise NotImplementedError()

   
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
            return val.split('/')[-1]
                        

