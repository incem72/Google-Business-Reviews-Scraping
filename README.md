## Scraping Google Business Reviews

  Finds any business by search keywords that you provide(will be prompted when you run app) and then retrive all ewiews for found company.
  The proecss on run:
  1. App will ask you what business are you searching
  2. App will search your keywords and will ask you to confirm if result is satisfactory for you
  3. The etrieve reviews and save into csv file (located in "output" folder - you will find two files there:
      1)log.txt - For run time log reports
      2)data.csv - reviews if run is successfull


## Please install required packages first and run >python reviews.py
  pip install -r requirements.txt
  NOTE: App will download and install the required ChromeDriver on first run.
