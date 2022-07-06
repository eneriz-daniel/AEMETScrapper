# Copyright (C) 2022 Daniel Enériz
# 
# This file is part of AEMET scrapper.
# 
# AEMET Scrapper is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# AEMET Scrapper is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with AEMET Scrapper.  If not, see <http://www.gnu.org/licenses/>.


import http.client
import os
import datetime
from tqdm import tqdm
import json

class AEMETScrapper:
    """Downloads data from AEMET using their API OpenData.
    Only daily climatological data is available at the moment.
    """


    def __init__(self, api_key):
        """Inizializes the scrapper. Needs an API key from AEMET.

        Args:
            api_key: API key from AEMET.
        
        Returns:
            AEMETScrapper: AEMETScrapper object.
        """
        self.api_key = api_key
        self.api_url_fmt = "/opendata/api/valores/climatologicos/diarios/datos/fechaini/{}/fechafin/{}/estacion/{}/?api_key={}" # Only the daily climatological data is available at the moment.
    
    def get_data_url(self, start_date, end_date, station_id):
        """Gets the URL to download the data.

        Args:
            start_date: Start date of the data. Must be a string in YYYY-MM-DDTHH:MM:SSUTC format.
            end_date: End date of the data. Must be a string in YYYY-MM-DDTHH:MM:SSUTC format.
            station_id: Station ID. You can check the station IDs in the [AEMET OpenData API](opendata.aemet.es).
        
        Returns:
            str: URL to download the data.
        
        Raises:
            Exception: If the data request is not successful.
        """

        # Check the dates are in YYYY-MM-DDTHH:MM:SSUTC format
        if not start_date.endswith("T00:00:00UTC"):
            start_date += "T00:00:00UTC"
        if not end_date.endswith("T23:59:59UTC"):
            end_date += "T00:00:00UTC"

        conn = http.client.HTTPSConnection("opendata.aemet.es")

        headers = {
            'cache-control': "no-cache"
        }

        conn.request("GET", self.api_url_fmt.format(start_date, end_date, station_id, self.api_key), headers=headers)

        res = conn.getresponse()
        data = res.read().decode("utf-8")

        # Read data as a dict
        data = eval(data)

        if data['estado'] != 200:
            raise Exception("Error while requesting AEMET data: {}".format(data['descripcion']))

        return data['datos']

    def download_json(self, start_date, end_date, station_id, data_filename = "data.json"):
        """Downloads the data and saves it in a json file. If the requested period is more than 5 years, it is split in 4-year chunks and a progress bar is shown.

        Args:
            start_date: Start date of the data. Must be a string in YYYY-MM-DDTHH:MM:SSUTC format.
            end_date: End date of the data. Must be a string in YYYY-MM-DDTHH:MM:SSUTC format.
            station_id: Station ID. You can check the station IDs in the [AEMET OpenData API](opendata.aemet.es).
            data_filename: Name of the json file to save the data.
        
        Returns:
            The data dict.
        """
        # Read dates as datetime objects
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%SUTC")
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%SUTC")

        # It the time difference is less than 5 years, download the data in one call
        if (end_date - start_date).days < 5*365.25:

            data_url = self.get_data_url(start_date.strftime("%Y-%m-%dT%H:%M:%SUTC"), end_date.strftime("%Y-%m-%dT%H:%M:%SUTC"), station_id)

            # Download data
            conn = http.client.HTTPSConnection("opendata.aemet.es")

            headers = {
                'cache-control': "no-cache"
            }

            conn.request("GET", data_url, headers=headers)

            res = conn.getresponse()
            data = res.read().decode("latin-1")

            # Save data in a json file
            with open(data_filename, "w") as f:
                f.write(data)
            
            return eval(data)
        
        else:
            # Create chunks of 4 years (5 is the limit of the OpenData AEMET API)
            chunks = []
            chunk_start = start_date
            chunk_end = chunk_start + datetime.timedelta(days=4*365.25)

            while chunk_end < end_date:
                chunks.append((chunk_start, chunk_end- datetime.timedelta(seconds=1))) # AEMET OpenData API likes 00:00:00 to 23:59:59 intervals
                chunk_start = chunk_end 
                chunk_end = chunk_start + datetime.timedelta(days=4*365.25)
                # If next chunk is after the end date, set it to the end date and stop the loop
                if chunk_end > end_date:
                    chunk_end = end_date
                    chunks.append((chunk_start, chunk_end- datetime.timedelta(seconds=1)))
                    break
            
            data = []
            # Iterate over the chunks
            for chunk_start, chunk_end in tqdm(chunks, 'Iterating over 4-year chunks'):
                data_tmp = self.download_json(chunk_start.strftime("%Y-%m-%dT%H:%M:%SUTC"), chunk_end.strftime("%Y-%m-%dT%H:%M:%SUTC"), station_id, "tmp.json")
                os.remove("tmp.json")
                
                # Append data to the final dict
                data += data_tmp

            # Save data in a json file
            with open(data_filename, "w") as f:
                json.dump(data, f)

            return data
    
    def json_to_csv(self, json_filename, csv_filename):
        """Converts a json file to a csv file using the last json entry keys as headers.

        Args:
            json_filename: Name of the json file to convert.
            csv_filename: Name of the csv file to save the data.
        
        Returns:
            None.
        """
        # Read data from json file
        with open(json_filename, "r") as f:
            data = eval(f.read())

        # Convert data to csv
        with open(csv_filename, "w") as f:
            # Use all the keys in the last entry as headers
            keys = data[-1].keys()
            f.write(";".join(keys) + "\n")
            for row in data:
                # Use NaN for missing values
                row = [row.get(k, "NaN") for k in keys]
                f.write(";".join(row) + "\n")
    
    def download_csv(self, start_date, end_date, station_id, csv_filename = "data.csv"):
        """Downloads the data and saves it in a csv file.

        Args:
            start_date: Start date of the data. Must be a string in YYYY-MM-DDTHH:MM:SSUTC format.
            end_date: End date of the data. Must be a string in YYYY-MM-DDTHH:MM:SSUTC format.
            station_id: Station ID. You can check the station IDs in the [AEMET OpenData API](opendata.aemet.es).
            csv_filename: Name of the csv file to save the data.
        
        Returns:
            None.
        """
        # Read dates as datetime objects
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%SUTC")
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%SUTC")

        # It the time difference is less than 5 years, download the data in one call
        self.download_json(start_date.strftime("%Y-%m-%dT%H:%M:%SUTC"), end_date.strftime("%Y-%m-%dT%H:%M:%SUTC"), station_id, "tmp.json")

        self.json_to_csv('tmp.json', csv_filename)

        os.remove('tmp.json')

# Example of usage
if __name__ == '__main__':

    # Load APIKEY from SECRETS json file
    with open('SECRETS') as f:
        secrets = json.load(f)
        api_key = secrets['APIKEY']

    scrapper = AEMETScrapper(api_key)

    start_date = "1990-01-01T00:00:00UTC"
    end_date = "2020-12-31T23:59:59UTC"

    idema = "9294E" # BARDENAS REALES, BASE AÉREA

    scrapper.download_csv(start_date, end_date, idema)



