# Destroy All Globals

Now while Lambdas may "feel" like infrastructure, they truly _are_ functions. Meaning, we can give them different inputs to have them produce different outputs. You can't reliably do that if they have global variables. The hardcoded globals I'm referring to are the bucket name the Lambdas are using, and the file names they are using when they upload files. This becomes a problem when you need to put the same code in both regions (say `us-west-1` and `us-east-2` for the USA). This also includes different environments like QA, Staging, and Production.

We have 2 options here. The first is the utilize the `template.yaml` to leverage CloudFormation, and have all our globals defined as environment variables. Then our Lambdas can use those.

The OTHER way is to treat them like true pure functions and only use data they got from their inputs. Screw environment varaibles. Screw globals. Let's keep things as stateless, and thus portable, as possible, and continue to push the side effects/state as high as possible until AWS releases another product that solves that problem and we can then update this book to use that. 😎

It'll also make the Lambdas easier to unit, integration, and end to end test later on since there is no globals to muck around with.

## Parallel State: Same Input, 3 Functions

Parallel's are interesting in that all the child states get the same input. However, each function needs differnet information. Step Function's JSON isnt' actually JSON, but something called JSONPath. It allows you to do queries in the JSON, and change inputs and outputs. We'll define all 3 of our Lambda's needed configuration data, and then tailor the input for each function so the Lambda code can remain dumb and work as it is.

## Global Variables to Remove

Let's get a list of global variables we have to remove from each function.

- **Download Benner**
    - Benner Equation URL: "http://echo.jpl.nasa.gov/~lance/delta_v/delta_v.rendezvous.html"
    - S3 Bucket Name: "asteroid-files"
    - Equations Output Filename: "benner_deltav.csv"
- **Download Exoplanets**
    - Exoplanets URL: "http://exoplanetarchive.ipac.caltech.edu/cgi-bin/nstedAPI/nph-nstedAPI?table=cumulative&select=koi_sma,kepoi_name,koi_eccen,koi_incl,koi_longp,koi_period,koi_prad,koi_teq,koi_srad,koi_steff,koi_sage,koi_disposition,koi_pdisposition"
    - S3 Bucket Name: "asteroid-files"
    - Exoplanet Filename: "exoplanet.csv"
- **Parse Masses**
    - Masses Text File: "./masses.txt"
    - S3 Bucket Name: "asteroid-files"
    - Masses Data Output Filename: "massd.json"

## Event

Let's change our event to support the data needed for all JSON's. We can change it later if we don't like it, _with_ contract tests, but for now we're going to leverage JSON and Python's strengths as a dynamic language to play with ideas.

First up is the commonalities between all functions: The S3 Bucket Name. Let's add that to the root of the JSON so all can use it.

```json
{
    "bucketName": "asteroid-files"
}
```

Next up is Benner; she's got 2 that are specific for her, so let's give that Lambda her very own slot in the JSON:

```json
{
    "bucketName": "asteroid-files",
    "benner": {
        "url": "http://echo.jpl.nasa.gov/~lance/delta_v/delta_v.rendezvous.html",
        "filename": "benner_deltav.csv"
    }
}
```

Exoplanets Lambda has basically the same 2 requirements:

```json
{
    "bucketName": "asteroid-files",
    "benner": {
        "url": "http://echo.jpl.nasa.gov/~lance/delta_v/delta_v.rendezvous.html",
        "filename": "benner_deltav.csv"
    },
    "exoplanets": {
        "url": "http://exoplanetarchive.ipac.caltech.edu/cgi-bin/nstedAPI/nph-nstedAPI?table=cumulative&select=koi_sma,kepoi_name,koi_eccen,koi_incl,koi_longp,koi_period,koi_prad,koi_teq,koi_srad,koi_steff,koi_sage,koi_disposition,koi_pdisposition",
        "filename": "exoplanet.csv"
    }
}
```

Lastly, the Masses Lambda really only has 1; we'll keep the `masses.txt` file bundled with the Lambda for now. For the Lambda's tests which we'll write later, we can assume the `masses.txt` file will double as a test fixture.

```json
{
    "bucketName": "asteroid-files",
    "benner": {
        "url": "http://echo.jpl.nasa.gov/~lance/delta_v/delta_v.rendezvous.html",
        "filename": "benner_deltav.csv"
    },
    "exoplanets": {
        "url": "http://exoplanetarchive.ipac.caltech.edu/cgi-bin/nstedAPI/nph-nstedAPI?table=cumulative&select=koi_sma,kepoi_name,koi_eccen,koi_incl,koi_longp,koi_period,koi_prad,koi_teq,koi_srad,koi_steff,koi_sage,koi_disposition,koi_pdisposition",
        "filename": "exoplanet.csv"
    },
    "masses": {
        "filename": "massd.json"
    }
}
```

Cool, so that is our Step Function input. Let's go ~refactor~ change the Lambdas to utilize that input.

## Benner Change

The first is to replace the hardcoded URL with what's in the event. This:

```python
def lambda_handler(event, context):
    try:
        result = urlopen('http://echo.jpl.nasa.gov/~lance/delta_v/delta_v.rendezvous.html')
```

Becomes:

```python
def lambda_handler(event, context):
    try:
        result = urlopen(event['benner']['url'])
```

Notice in the above the `event` is already a Python dictionary for us, parsed from the Step Function, ready to be used, no need for `json.loads`.

Lastly, we need to replace the bucket name and file name in the `s3.put_object` call. Change the hardcoded values from:

```python
result = boto3.client('s3').put_object(
    Bucket="asteroid-files", 
    Key="benner_deltav.csv", 
    Body=csv
)
```

To this:

```python
result = boto3.client('s3').put_object(
    Bucket=event['bucketName'], 
    Key=event.benner['filename'], 
    Body=csv
)
```

## Exoplanets Change

The Exoplanets Lambda has the same changes, but they are parameterized in functions. So this call to `download`:

```python
def lambda_handler(event, context):
    exoplanet_data, error = download()
```

Becomes:

```python
def lambda_handler(event, context):
    exoplanet_data, error = download(event['exoplanets']['url'])
```
We have to modify the `download` function to take in that parameter and delete the `EXOPLANET_URL` variable up top:

```python
EXOPLANET_URL = 'http://exoplanetarchive.ipac.caltech.edu/cgi-bin/nstedAPI/nph-nstedAPI?table=cumulative&select=koi_sma,kepoi_name,koi_eccen,koi_incl,koi_longp,koi_period,koi_prad,koi_teq,koi_srad,koi_steff,koi_sage,koi_disposition,koi_pdisposition'

def download():
    try:
        result = urlopen(EXOPLANET_URL)
```

... becomes:

```python:
def download(url):
    try:
        result = urlopen(url)
```

And the `upload` actually needs 2 parameters, both the bucket name and new file name. From:

```python
result, error = upload(exoplanet_data)
```

To:

```python
result, error = upload(exoplanet_data, event['exoplanet']['bucketName'], event['exoplanet']['filename'])
```

Which means the upload function's function changes from:

```python
def upload(exoplanet_data):
    try:
        result = boto3.client('s3').put_object(
            Bucket="asteroid-files", 
            Key="exoplanet.csv", 
            Body=exoplanet_data
        )
```

To:

```python
def upload(exoplanet_data, bucketName, filename):
    try:
        result = boto3.client('s3').put_object(
            Bucket=bucketName,
            Key=filename, 
            Body=exoplanet_data
        )
```

## Parse Masses

Last up is refactoring the Masses Lambda. This one is weird because most of our bound (binded?) functions in the pipeline are single input, single output. You have 2 options here:

A: Using Closures to inject the extra arguments
B: Curried Function

The `upload` function takes 1 argument, but now we need her to take 2 additional ones. Let's first make `upload` the way we want from this:

```python
def upload(massd_json):
    return Result.try_(
        lambda: boto3.client('s3').put_object(
            Bucket="asteroid-files", 
            Key="massd.json", 
            Body=massd_json
        )
    )
```

To this:

```python
def upload(massd_json, bucketName, filename):
    return Result.try_(
        lambda: boto3.client('s3').put_object(
            Bucket=bucketName, 
            Key=filename, 
            Body=massd_json
        )
    )
```

### Closure Option

The closure option involves using Python's normal use of function closures; a function can access variables in the scope its defined in. So our `upload` can use anything defined in `lambda_handler`. We can wrap her with a function, or a smaller one called a `lambda` (Python Lambda is a different syntax for defining functions in Python, it has nothing to do with AWS Lambda).

We'll change the normal way of PyMonad's `bind` (i.e. the `>>` thing) where it'll automatically call `upload` with whatever it got from further up the pipeline to interjecting a new function. From this:

```python
>> upload
```

To this:

```python
>> (lambda massd_json: upload(massd_json, eventp['bucketName'], event['masses']['filename']))
```

The `massd_json` comes from the pipeline as the single and only parameter. However, we get the other 2, the `bucketName` and the `filename` off of the `event`. Since this function is inside the `lambda_handler`, he can access anything in there. If you're from JavaScript and know `Promises`, this should look familiar where you define anonymous functions in Promise chains a lot.

### Curry Option

The other option involves the use of curried functions; all functions take 1 argument. This allows you to create partial applications; a function with some arguments already given and stored in the closure.

We can make our `upload` function curried by putting `@curry` on top of it with `massd_json` placed as the last parameter instead, like so:

```python
from pymonad.Reader import curry
...
@curry
def upload(bucketName, filename, massd_json):
...
```

Then, we can give it 2 parameters, and let the pipeline give it the last one. From this:

```python
>> upload
```

To this:

```python
>> upload(eventp['bucketName'], event['masses']['filename'])
```

Note that `upload` above has its first 2 parameters applied, and will only actually run once its third, `massd_json` is given.

### Crash Course in Currying / Partial Applications

If you're new to currying, basically any function that takes over 1 parameter returns a function instead until the last parameter is provided.

This:

```python
def sup(firstName, lastName):
    return f"What's up {firstName} {lastName}!?"

sup('Jesse', 'Warden') # "What's up Jesse Warden!?
```

Becomes this:

```python
def sup(firstName):
    def last(lastName):
        return f"What's up {firstName} {lastName}!?"
    return last

sup('Jesse')('Warden')
```

At first that looks like a complicated way to call a function, but it allows you to do things like this:

```python
wat_is_this = sup('Jesse')
print(wat_is_this)
# <function sup.<locals>.last at 0x10dc48670>
```

That `wat_is_this` is a function. If you look at `def last`, it's that one. Notice how the `def last`, however, has a `firstName` in it's body, but nowhere does it have `firstName` in it's parameter list. THat's because it's using function closures to get it from the function its defined in, `sup`. So although `last` doesn't have a `firstName` function parameter, it has it stored as a value in the closure and will use it when you go `wat_is_this('Warden')`.

## Conclusions

Run `sam build && sam deploy`.