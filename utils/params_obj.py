# hide implementation details
from configparser import ConfigParser as _ConfigParser
import os.path

class ParamsParser(dict):
    """
    Uses ConfigParser to parse .ini files but has the following advantages:
    1) calls evals thus supporting both strings and numbers (and arrays etc)
    2) returns nested dict with dot (attribute) access, 
        one can pass subsection, which will have the same type


    Took code from https://stackoverflow.com/questions/13520421/recursive-dotdict
    """
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    @classmethod
    def from_file(cls, fname):
        if not os.path.exists(fname):
            raise FileNotFoundError(fname)

        config_parser = _ConfigParser()
        config_parser.read(fname)
        sections = config_parser._sections
        return cls(sections)


    def __init__(self, dct):
        """uses from_file constructor"""
        for key, value in dct.items():
            if isinstance(value, dict):
                value = ParamsParser(value)
            else:
                # means we reached the end
                try:
                    value = eval(value)
                except NameError as err:
                    raise NameError(f"Most probably you are mising quotes in your config: {err}")     
            self[key] = value