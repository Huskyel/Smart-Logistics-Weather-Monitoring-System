import boto3
import requests
import os
import pandas as pd
from io import StringIO
from dotenv import load_dotenv

load_dotenv()

def fetch_and_upload_to_s3(miasto):
    api_key = os.getenv('WEATHER_API_KEY')
    url = f"http://api.openweathermap.org/data/2.5/weather?q={miasto}&appid={api_key}&units=metric"
    data = requests.get(url).json()

    row = {
        'MIASTO': miasto,
        'TEMP': data['main']['temp'],
        'OPIS': data['weather'][0]['description'],
        'DATA_POBRANIA': pd.Timestamp.now()
    }
    df = pd.DataFrame([row])

    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False, header=False)

    s3 = boto3.client('s3', 
                      aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
                      aws_secret_access_key=os.getenv('AWS_SECRET_KEY'))
    
    bucket = 'logistykadanepogodowematkaz1'
    key = f"weather_{miasto}.csv"
    
    s3.put_object(Bucket=bucket, Key=key, Body=csv_buffer.getvalue())
    print(f"✅ Wysłano {miasto} do S3!")

if __name__ == "__main__":
    fetch_and_upload_to_s3("Poznan")