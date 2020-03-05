from google.cloud import bigquery

import pandas
import pandas_gbq
# import logging

# logger = logging.getLogger('pandas_gbq')
# logger.setLevel(logging.DEBUG)
# logger.addHandler(logging.StreamHandler())


def write_to_gbq(df, project_id, table_id):
    pandas_gbq.to_gbq(df, table_id, project_id=project_id, if_exists="append")

def run_query(query, project_id, table_id, client=None):
    """
    query like 'SELECT * FROM %s'
    project_id, table_id will be used to fill FROM

    Returns
    -------
    query_results
    """
    if client is None:
        client = bigquery.Client()
        
    query_job = client.query(query % f"`{project_id}.{table_id}`")
    results = query_job.result()
    
    return results