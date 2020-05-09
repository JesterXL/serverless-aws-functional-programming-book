from urllib.request import urlopen
import boto3
import traceback
import sys

def download(url):
    try:
        result = urlopen(url)
        data = result.read()
        return (data, None)
    except Exception as e:
        print("download failed:", e)
        return (None, e)

def upload(exoplanet_data, bucketName, filename):
    try:
        result = boto3.client('s3').put_object(
            Bucket=bucketName, 
            Key=filename, 
            Body=exoplanet_data
        )
        return (result, None)
    except Exception as e:
        print("Upload to S3 failed:", e)
        print(sys.exc_info()[2])
        return (None, e)
        
class HTTPError(Exception):
    pass

class GeneralError(Exception):
    pass

def lambda_handler(event, context):
    exoplanet_data, error = download(event['exoplanets']['url'])
    if error != None:
        raise HTTPError('Failed to download exoplanet data.')

    result, error = upload(exoplanet_data, event['bucketName'], event['exoplanets']['filename'])
    if error != None:
        raise GeneralError('Failed to upload exoplanet data to S3.')

    return result

if __name__ == "__main__":
    try:
        result = lambda_handler({
            'bucketName': 'asteroid-files',
            'exoplanets': {
                'url': 'http://exoplanetarchive.ipac.caltech.edu/cgi-bin/nstedAPI/nph-nstedAPI?table=cumulative&select=koi_sma,kepoi_name,koi_eccen,koi_incl,koi_longp,koi_period,koi_prad,koi_teq,koi_srad,koi_steff,koi_sage,koi_disposition,koi_pdisposition',
                'filename': 'exoplanet.csv'
            }
        }, {})
        print("result:", result)
    except HTTPError:
        print("HTTP failed.")
    except GeneralError:
        print("General error.")
    except Exception as e:
        print("unknown error:", e)