# Copy Pasta Coding

First, copy your `download-benner` (or `download_benner`) Lambda folder and paste it again inside the same folder. Rename it to `download-exoplanets`.

Second, go into your `template.yaml` and copy your `DownloadBennerFunction` resource, and paste a new one right below it and rename it. Don't forget to change the `CodeUri` as well; it should look like this:

Third, open up the `app.py` in there, a let's start from scratch:

```python
def lambda_handler(event, context):
    return event
```

Congrats, you've got yourself a new Lambda. Run `sam build && sam deploy`.

## Download Data

Like our Benner Lambda, we're going to be downloading a bunch of csv style data from some rando NASA/JPL website. Let's import our request lib:

```python
from urllib.request import urlopen
```

And implement the download with our pre-filled form submission:

```python
from urllib.request import urlopen

def lambda_handler(event, context):
    result = urlopen('http://exoplanetarchive.ipac.caltech.edu/cgi-bin/nstedAPI/nph-nstedAPI?table=cumulative&select=koi_sma,kepoi_name,koi_eccen,koi_incl,koi_longp,koi_period,koi_prad,koi_teq,koi_srad,koi_steff,koi_sage,koi_disposition,koi_pdisposition')
    return event
```

Ok, let's pause there, and see if we can do things better this time around.