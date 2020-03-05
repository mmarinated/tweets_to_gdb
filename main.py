import os
from logging import DEBUG, ERROR, WARNING, info, debug, error, getLogger, warning, basicConfig
from time import sleep
from datetime import datetime

import pandas as pd
import twint
from importlib import reload

from utils.geo_utils      import parse_address_to_twint_config
from utils.params_obj     import ParamsParser
from utils                import gbq_utils, read_txt_utils
from paths                import PATH_TO_CONFIG, PATH_TO_JSON


def time_now():
    """returns time in format needed for twint"""
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def set_google_credential(path_to_json):
    """add Google Cloud credentials as environmental variable"""
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path_to_json


class TweetsGenerator:
    """A class that loads tweets based on config file and dumps to google database"""

    def __init__(self, *, config_fn=PATH_TO_CONFIG, use_cold_start=True, store_dataframe=False):
        """
        use_cold_start:
            if True uses time from config else loads 
            last time from path_to_time_logs file 
            (needed in case of program crash)
        """
        self.params = ParamsParser.from_file(config_fn)
        self.store_dataframe = store_dataframe
        set_google_credential(PATH_TO_JSON)

        if use_cold_start:
            since_time = self.params.twint_config.cold_start_since_time
        else:
            since_time = read_txt_utils.read_last_line(
                self.params.update_params.path_to_time_logs)
            print(f"Restarting program from {since_time}")
        
        self.twint_config = self.create_twint_config(self.params.twint_config, since_time)

        # logging
        basicConfig(filename=self.params.update_params.path_to_logs,level=DEBUG)
        

    def _delete_tmp_csv(self):
        if self.store_dataframe:
            raise NotImplementedError
            # pandas append tmp file to large db file

        # remove tmp file completely
        path_to_tmp_csv = self.params.twint_config.path_to_out_csv
        if os.path.exists(path_to_tmp_csv):
            os.remove(path_to_tmp_csv)

    def _update_and_log_since_time(self, time):
        self.twint_config = self.create_twint_config(self.params.twint_config, time)
        # a+ is "create if not exists and append to the end"
        with open(self.params.update_params.path_to_time_logs, "a+") as file:
            file.write("\n"+time)

    def try_run_twint_query(self):
        try:
            info(f"twint_config.Since {self.twint_config.Since}")
            twint.run.Search(self.twint_config)
            self._update_and_log_since_time(time_now())
            info(f"{time_now()}: Twint successfully ran.")
        except Exception as err: # should have better errors here
            error(f"{time_now()}: Twint failed. {err}")

    def try_upload_to_google_db(self):
        if os.path.exists(self.params.twint_config.path_to_out_csv):
            df = pd.read_csv(self.params.twint_config.path_to_out_csv)
            info(f"{df.shape[0]} tweets loaded.")
        else:
            warning(f"{time_now()} {self.params.twint_config.path_to_out_csv} does not exist. No tweets were found.")
            return
        
        try:
            gbq_utils.write_to_gbq(df, 
                                   self.params.google_db.project_id,
                                   self.params.google_db.table_id)
            info(f"{time_now()}: Successfully loaded to google database {df.shape[0]} tweets")

            # delete the previous dump as we have just uploaded it.
            # (if .csv file exists, twint appends new data there, so we need to delete it)
            self._delete_tmp_csv()
        except Exception as err: # should have better errors here v2
            error(f"{time_now()}: write_to_gbq failed. {err}")

    def run(self,):
        """load_tweets_and_dump_to_db"""
        while True:
            self.try_run_twint_query()
            self.try_upload_to_google_db()
            sleep(60 * self.params.update_params.frequency_in_min)

    @staticmethod
    def create_twint_config(params, since_time):
        """
        params correspond to twint_config section

        Returns
        -------
        initialized_twin_config
        """
        config = twint.Config()
        
        config.Search = params.query
        config.Geo = parse_address_to_twint_config(params.address, 
                                                num_km=params.num_km, 
                                                country_code=params.country_code)
        
        config.Custom["tweet"] = params.fields_to_load
        config.Custom["user"] = ["bio"]
        config.Store_csv = params.save_csv
        config.Output    = params.path_to_out_csv
        # # Number of Tweets to pull (Increments of 20).
        # config.Limit = 3
        config.Since  = since_time

        return config



if __name__ == "__main__":
    tweets_generator = TweetsGenerator()
    tweets_generator.run()




###
## Debug methods
###

def load_last_tweets_from_db(config_fn=PATH_TO_CONFIG, first_rows=5):
    """loads tweets we have loaded to google data base"""
    set_google_credential(PATH_TO_JSON)
    params = ParamsParser.from_file(config_fn)

    select_specifier = "" if first_rows is None else f"LIMIT {first_rows}"
    query = f"""SELECT * FROM %s {select_specifier}"""
    results = gbq_utils.run_query(query,
                                  params.google_db.project_id,
                                  params.google_db.table_id)

    return list(results)


# def clean_table(config_fn=PATH_TO_CONFIG):
#     """loads tweets we have loaded to google data base"""
#     set_google_credential(PATH_TO_JSON)
#     params = ParamsParser.from_file(config_fn)
#     query = f"""DELETE FROM %s WHERE TRUE"""
#     results = gbq_utils.run_query(query,
#                                   params.google_db.project_id,
#                                   params.google_db.table_id)

#     return results