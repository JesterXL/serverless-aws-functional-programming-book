# Step Function Input

Now that we have parameterized Lambdas, this in turn makes our Step Function parameterized. There are no default values to reduce code paths SO we must now invoke our Step Function with this input.

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

Go into your AWS console, navigate to Services > Step Function, find yours, and when you click Start Execution, use the above JSON, and watch her execution go.

<img src="./Screen Shot 2020-05-03 at 12.04.50 PM.png"></img>

Notice that the 3 steps are grouped into this lighter, dotted green step that houses all 3. That's the `Parallel` and you can click it and see it's input. That same input is duplicated for all children it has. See here where I select the `Download Exoplanets` Lambda, and it has the same input.

<img src="./Screen Shot 2020-05-03 at 12.05.05 PM.png"></img>

## Output

All 3 of the Lambda functions return the S3 Put Object result directly. We can see the `Parallel` returns an Array, each item in the Array being what the Lambda at that index returned.  

<img src="./Screen Shot 2020-05-03 at 12.43.58 PM.png"></img>

## Output Path

That's a lot of JSON, no doubt. We only need the `etag`, the MD5 hash that AWS generates when you upload a file to S3. We can use that later as an extra check to ensure we're reading the file we think we are, AND to reduce how much JSON we're getting. Step Function 32kb JSON limit is a lurking shitshow we'll get to later. Let's snag off this `etag` since that's all we need, and there is no need to update a bunch of code again when we can just do it in the Step Function. This is also useful if you don't control / didn't write the downstream service.

You do this using `OutputPath`; it lets you filter what you want out of the output JSON. Let's update our `template.yaml` definition JSON to snag out the etags. We'll do it individually on each state.

Here's the updated Download Benner JSON state, check out the `OutputPath`, specifically the jQuery looking dollar sign in the `OutputPath` value:

```json
"Download Benner": {
    "Type": "Task",
    "Resource": "${downloadBennerLambda}",
    "OutputPath": "$.ResponseMetadata.HTTPHeaders.etag",
    "End": true
}
```

Do the same thing for the other 2 states, run `sam build && sam deploy`, then re-run your Step Function with the same JSON. Then, check out the simplified output:

<img src="./Screen Shot 2020-05-03 at 1.00.15 PM.png"></img>

... but ... what's up with the slashes `\` in front of the strings?

## JSON Parsing and JSON Path

The great about JSON is that everything can talk JSON. Dynamic languages, strongly typed compiled languages, Step Functions, Lambdas, Go... whatever. The downside is there are 2 types of JSON: A "JSON String" and a "JSON Object". Worse, you can put JSON Strings inside of JSON Objects. Your only clue there is the encoded strings via the back slashes `\` around the Strings.

While Step Functions and Lambdas are cool in that they all speak JSON, and even handle the parsing for you (which is why in Python / JavaScript, you just return a Dictionary / Object, and it convets it for you)...

... they sometimes have weird cases where you'll JSON Strings back in case of JSON Objects. Look for the back slashes `\` in the response. You'll see this a lot with nested Step Functions.

The good news is, the [JSON Path syntax](https://github.com/json-path/JsonPath), the syntax that Step Functions use to make JSON more dynamic, supports JSON Strings as well (mostly). Additionally, in the case of crytography, you'll sometimes get strings that aren't always Base64 encoded, and so it'll sometimes escape those values just in case so they'll work in JSON.

Nothing to worry about, just don't freak out when you see it. We won't be covering nested Step Functions in this book, but you'll get some weirdness when you get JSON inside of JSON in your Lambdas, so just know to look for it.