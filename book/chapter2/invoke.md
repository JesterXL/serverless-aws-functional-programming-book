# Invoke & Test Locally

You already tested your function locally in the previous step, but now we're going to use SAM to invoke it locally. This requires Docker, so naturally is slower and more miserable, but bear with it for a bit. Install Docker first and ensure it's running. I do Docker Desktop for Mac.

Once installed and running, in your Terminal type `same local invoke`.

It'll run your `app.py` Lambda function in an environment that is mostly like what's up in AWS. While the Terminal will have more text, it's the same code returning the same thing:

```Fetching lambci/lambda:python3.8 Docker container image......
Mounting /Users/jessewarden/Documents/asteroid-app/hello_world as /var/task:ro,delegated inside runtime container
START RequestId: d0a81bb3-125d-1f7f-b676-2a3bfcf7c0b7 Version: $LATEST
END RequestId: d0a81bb3-125d-1f7f-b676-2a3bfcf7c0b7
REPORT RequestId: d0a81bb3-125d-1f7f-b676-2a3bfcf7c0b7  Init Duration: 101.78 ms        Duration: 3.54 ms   Billed Duration: 100 ms  Memory Size: 128 MB     Max Memory Used: 25 MB

{"statusCode":200,"body":"{\"message\": \"hello world\"}"}
```

If your Spidey Sense is tingling and you're like "why in the heck are we doing it this way?", don't fret. Compiled languages may have operating system dependencies, or even dynamic languages like JavaScript and Python that sometimes will use libraries that have to be compiled for a particular cpu and/or os architecture exist. That means, if I `pip install` or `npm install` locally, the `python_modules` or `node_modules` that are on my Mac won't work when I upload my Lambda to AWS. In my experience, most of the time you **DO NOT** need this functionality. The time it takes to run the test + integrate into your CI/CD pipeline has low returns.

Usually with Lambdas you invoke with a particular event, like "An API Gateway that does a GET with a query parameter" or "SQS will be sending a list of JSON objects I need to parse and put back on another queue". There are _a lot_ of these things. Run `sam local generate-event --help` to see a list. Basically `sam local generate-event` will create JSON fixtures so you can save it to a file, and test your functions. You can use this locally, for `sam local invoke` using them with the `-e` option, or even for unit tests. A quick way to generate 2, one for API Gateway and one for SQS:

`sam local generate-event apigateway aws-proxy &gt;&gt; events/api-event.json`

`sam local generate-event sqs receive-message &gt;&gt; events/sqs-event.json`

TODO: Running PyTest