import httpx
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




class OLBase:

    def __init__(self, timeout_config):
        self._client = httpx.Client(timeout=timeout_config, follow_redirects=True)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(DEFAULT_LEVEL)
        self.logger.addHandler(CONSOLE_HANDLER)
        self.logger.addHandler(FILE_HANDLER) if FILE_HANDLER else None

    def _get(self, path, subdomain: str =  None, params: dict = {}) -> httpx.Response:

        url = f"https://{subdomain + '.' if subdomain is not None else ''}{BASE_DOMAIN}/{path}"

        self.logger.info(f"GET: {url}")
        self.logger.debug(F"pararms: {json.dumps(params, indent=2, sort_keys=True)}")

        resp = self._client.get(url, params=params)
        
        try:
            resp.raise_for_status()

        except Exception as e:
            self.logger.error(f"Error in GET", exc_info=True)
            raise e.with_traceback(e.__traceback__)
        
        finally:
            self.logger.info(f"GET: time elasped {resp.elapsed}")
            self.logger.debug(f"GET: recieved {resp.num_bytes_downloaded} bytes")
        
        return resp
    
    def _post():
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
                        

