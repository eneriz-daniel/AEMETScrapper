Usage
=====

.. _requirements:

Requirements
------------

Only `tqdm` is requried. It is used to show progress bars in chunk-based downloads.

C
JSON format download
--------------------
.. code-block:: python

   from aemet_scrapper import AEMETScrapper

   api_key = 'YOUR_API_KEY'

   scrapper = AEMETScrapper(api_key)

   start_date = "1990-01-01T00:00:00UTC"
   end_date = "2020-12-31T23:59:59UTC"

   idema = "9294E" # BARDENAS REALES, BASE AÉREA

   scrapper.download_json(start_date, end_date, idema, "Bardenas1990-2020.json")

   [
      {
         "fecha": "1993-07-24",
         "indicativo": "9294E",
         "nombre": "BARDENAS REALES, BASE AÉREA",
         "provincia": "NAVARRA",
         "altitud": "295",
         "prec": "0,0",
         "dir": "19",
         "velmedia": "6,7",
         "racha": "23,1",
         "horaracha": "05:10"
      },
      ...
   ]


CSV format download
-------------------
::

   from aemet_scrapper import AEMETScrapper

   api_key = 'YOUR_API_KEY'

   scrapper = AEMETScrapper(api_key)

   start_date = "1990-01-01T00:00:00UTC"
   end_date = "2020-12-31T23:59:59UTC"

   idema = "9294E" # BARDENAS REALES, BASE AÉREA

   scrapper.download_csv(start_date, end_date, idema, "Bardenas1990-2020.csv")

   fecha,indicativo,nombre,provincia,altitud,tmed,prec,tmin,horatmin,tmax,horatmax,dir,velmedia,racha,horaracha,presMax,horaPresMax,presMin,horaPresMin
   1993-07-24,9294E,BARDENAS REALES, BASE AÉREA,NAVARRA,295,NaN,0,0,NaN,NaN,NaN,NaN,19,6,7,23,1,05:10,NaN,NaN,NaN,NaN
   1993-07-25,9294E,BARDENAS REALES, BASE AÉREA,NAVARRA,295,NaN,0,0,NaN,NaN,NaN,NaN,31,7,8,21,7,18:10,NaN,NaN,NaN,NaN
   1993-07-26,9294E,BARDENAS REALES, BASE AÉREA,NAVARRA,295,NaN,0,0,NaN,NaN,NaN,NaN,28,7,5,19,7,15:40,NaN,NaN,NaN,NaN
   1993-07-27,9294E,BARDENAS REALES, BASE AÉREA,NAVARRA,295,NaN,0,0,NaN,NaN,NaN,NaN,NaN,3,1,NaN,NaN,NaN,NaN,NaN,NaN

Note that as the keys of the last data entry are used as headers, some variables may not be included in all CSV file. This missing values are marked as NaN.


