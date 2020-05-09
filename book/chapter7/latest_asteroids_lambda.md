# Latest Asteroids Lambda

There is just one more Lambda to get weekly data: Latest Asteroids.

... however, there is a huge problem. The data is 500+ megs. Parsing it using Pandas and NumPy is over 4 gigs of RAM.

Risks of using Lambda for this include:

1. Lambda's have max of [250 megs deployment size](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html) when put on S3.
2. The max file you can store/access locally in the `/tmp` directory is 512 megs; I've seen the filesize exceed that sadly.
3. Lambda execution limit time is 15 minutes; can we download / upload the data in this time frame?
4. Lambda has about 3 gigs max RAM; using 500 megs of JSON while parsing in real-time usign Pandas and NumPy is over 4 gigs of RAM.

Your first reaction seeing "Pandas" and "NumPy" is probably to say "just use [EMR](https://aws.amazon.com/emr/)!" or even "just use [Batch](https://aws.amazon.com/batch/)!" EMR in particular is well suited to this use case of parsing larges amounts of data with powerful hardware, but then shutting down after use. Batch is similiar. Both, however, have 2 horrible problems in the Step Function integration and Enterprise context.

## Amazon Machine Images (AMI) Rehydration

EMR and Batch both have [AMI's](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AMIs.html), meaning an operting system. Whether your company utilizes custom AMI's or frequently updated, hand made ones... you have to update them. So while it's "serverless", the OS testing and maintenance is on you. For large companies that have locked down production access, this can be a royal pain, and a major timesink with an inability to quickly react and fix bugs that arise. Multiple this by 2 when you have two different regions with 2 different AMI versions for security reasons. While from a Cyber perspective rehydrations are good, from a developer perspective at large companies, they. Are. The. WORST. EMR/Batch is a no go if you can help it.

## Step Function Integration

While EMR and Batch have integration with Step Function, they don't support good return values. At the time of this writing, neither support the task token way of returning values (responding to an SQS message). Even ECS can do that, sadly, which makes these services a bit hard to treat like "functions"; they have to have some kind of side effect you can read like a file on S3, an SQS message, etc. Here's a table from Step Function Integrtions that gives you an idea:

<img src="./Screen Shot 2020-05-03 at 6.54.12 PM.png"></img>

You _can_ know if the Batch or EMR was successful or failed, but no details beyond that. The JSON they return is massive, but only 1 value tells you anything useful. We want useful return values.

## Solution: Streams

Streaming allows you to read and deal with parts of data vs. the whole thing. All the other Lambdas for the most part were:

> Read all the bytes into memory, then save to S3.

Streaming is different. Streaming is:

> Read some bytes, put some of them in memory, put some on S3, have S3 re-assemble at the end.

This solves our Lambda power issues:

1. Deployment size is just our code, no need to bake in the latest asteroids file from S3.
2. No need to store the whole file in RAM or locally; we'll get just a few bytes at a time.
3. Lambda 15 minute time limit? We'll see.
4. 3 gigs of RAM? Hell, we can do it with 128 megs!

There are 2 things required to make this work: a good streaming mechnism and [S3 multipart upload](https://docs.aws.amazon.com/AmazonS3/latest/dev/mpuoverview.html).

## S3 Multipart File Upload

While there are a lot of wonderful features for S3 multipart file uploads, we're not using any of it for concurrency. We're just doing it so we can read bits of data, upload to S3, and have AWS re-assemble it into a large file. Since our Lambda has a RAM and file size limit, this feature works out great. You _can_ upload multiple parts at once, but I want to show how you can write FP style code using streams. That, and it's easier to debug concurrency in a single place vs. sprawled out over many services. Don't worry, we'll create some fun sphghetti infra + code later, for now, enjoy the monolith pasta.

## Streams

Many languages have streams. [Python has streams](https://docs.python.org/3/library/asyncio-stream.html). I have no idea how they work.

[Node.js also has streams](https://www.freecodecamp.org/news/node-js-streams-everything-you-need-to-know-c9141306be93/). [I know](https://nodejs.dev/nodejs-streams) how they work.

So this Lambda will be in JavaScript soley to take advantage of their built-in streaming interface.

## Got Node.js?

I'll assume you have Node.js already, but unlike Python, Node.js doesn't come pre-installed everywhere. You can either download the latest from [their website](https://nodejs.org/en/) or install something like [nvm](https://github.com/nvm-sh/nvm) (Node Version Manager) to quickly play with versions (sort of like [PyEnv](https://github.com/pyenv/pyenv)). On a Terminal, run `node --version` and `npm --version` to verify Node and Node Package Manager are good to go.

## Creating the Lambda

Open up your `template.yaml`, and copy pasta a new Resource:

```yaml
LatestAsteroidsFunction:
  Type: AWS::Serverless::Function
  Properties:
    CodeUri: latest-asteroids/
    Handler: app.lambda_handler
    Runtime: nodejs12.x
    Timeout: 900
    Policies:
    - S3WritePolicy:
        BucketName:
          !Ref AsteroidFilesBucket
```

Take a note of the `Runtime` is now Node insted of Python, and `Timeout` is 900, the maximum you can do at the time of this writing (15 minutes). Normally, I'm a fan of shorter lambdas because waiting for slow running lambdas defeats the purpose of using quick to test dynamic languages. In this case, however, we want to create a benchmark first, an average of how long it may take and we'll adjust downwards. Better to wait 9 minutes for a failure than 15 when testing code manually or through end to end tests multiple times a day.

Also, create a new folder called `latest-asteroids` and `cd` into it. Run `npm init -y`. This'll create a default `package.json`. This holds many things, usually your libraries you need much like Python's `requirements.txt`. We don't need any libraries right now, the built in ones Node.js has are fine for now.

Finally, create an `app.js` file, with the following contents (remember dot jay ess, not dot pee why... it can happen when you switch languages often):

```javascript
const handler = async (event) => {
    return event
}

exports.handler = handler
```

Run `cd ..` to get back to the main folder and run `sam build` to ensure everything is good. Instead of seeing stuff like this:

```bash
Building resource 'ParseMassesFunction'
Running PythonPipBuilder:ResolveDependencies
Running PythonPipBuilder:CopySource
```

You should see stuff like this for your Latest Asteroids Lambda:

```bash
Building resource 'LatestAsteroidsFunction'
Running NodejsNpmBuilder:NpmPack
Running NodejsNpmBuilder:CopyNpmrc
Running NodejsNpmBuilder:CopySource
Running NodejsNpmBuilder:NpmInstall
Running NodejsNpmBuilder:CleanUpNpmrc
```

That mean SAM recognizes it as a JavaScript Lambda and is building it correctly, OH YEAH!

## Download Asteroids

The (read this slowly, lol) "Jet Propulsion Small-Body Database Search Engine" has a container ship ton of content, yo. The settings we're using, I have no idea what they mean beyond getting tons of CSV data. Even in Functional Programming, you can using abstraction programming technique to take complexitly and hide it behind a simple interface. Given the POST request has a gazillion form input values that aren't in _my_ English, we'll just expose a function `downloadLatestAsteroids` from a module called `downloads.js`. We're using [node-fetch](https://www.npmjs.com/package/node-fetch) to make REST calls because the `https` built-in Node module is too low-level and not as fun as `node-fetch`.

The code without the form parameters looks like:

```javascript
...
const downloadLatestAsteroids = () =>
    fetch(
        'https://ssd.jpl.nasa.gov/sbdb_query.cgi',
        {
            method: 'POST',
            body: params
        },
    )
    .then(
        res =>
        console.log("downloadLatestAsteroids fetch done, returning streaming body") ||
            res.body
    )

module.exports = downloadLatestAsteroids
```

If you don't know Promises, but do know [Python's async/await syntax](https://docs.python.org/3/library/asyncio.html), the JS version would be (without error handling):

```javascript
const downloadLatestAsteroids = async () => {
    const result = await fetch(
        'https://ssd.jpl.nasa.gov/sbdb_query.cgi',
        {
            method: 'POST',
            body: params
        }
    )
    return result.body
}
```

JavaScript Promises have built-in error handling, and chain much like our [PyMonad](https://pypi.org/project/PyMonad/) example from `Parse Masses`, so we'll stick with that syntax over async/await.

Both the `https` and `node-fetch` support treaing the body that is returned from an HTTP request as a stream. Given ours will be AT LEAST 500+ megs zip compressed, this is perfect for our low-powered Lambda (or even high powered 3 gig one). As soon as the JPL website starts sending data, our `Promise` will resolve, call the function in the `.then`, and we can snag the body off of the request, and send it back for others to start immediately reading from.

## Event Parameters

We'll start off on a good foot, and assume the bucket name and file name we're saving to S3 will be in our JSON event payload.

```javascript
const handler = async (event) => {
    const { bucket, latestAsteroids } = event
    return event
}

exports.handler = handler
```

To test that she works, we'll write some code to invoke our code locally only when it's run via `node app.js`, just like we do in Python. This code won't run when it's in your Lambda.

```javascript
if(require.main === module) {
    handler(
        {
            bucketName: 'asteroid-files', 
            latestAsteroids: { filename: 'lastest-asteroids.csv' } 
        }
    )
    .then(log)
    .catch(log)
}
```

## Logging

In Python, for normall debugging you use `print`. In JavaScript, you often use `console.log`. However, I'm lazy and like just typing `log` so I'll usually put it up top:

```javascript
const log = console.log
```

## Multipart Upload

First `cd` into your `latest-asteroids` folder, and run `npm install aws-sdk --save-dev`. This'll save the AWS SDK for Node.js in your `package.json` as a dev dependency, like `requirements-dev.txt` in Python. It'll also create a `node_modules` folder in there, and put the AWS SDK code and its dependencies in there. In Python, `pip install` will install globally by default, whereas if you want to install into a particular folder, you either tell `pip` to do that locally, or just use [virtualenv](https://virtualenv.pypa.io/en/latest/), [pipenv](https://github.com/pypa/pipenv), or some [Conda](https://docs.conda.io/en/latest/) derivative. Node on the other hand installs locally by default and only installs globally if you explicity tell it too.

Once the SDK is installed, we'll need to import it up top in our `app.js`:

```javascript
...
const AWS = require('aws-sdk')
...
```

That has a ton of awesome things in it. For now, let's use S3 in our Lambda Handler:

```javascript
...
const s3 = new AWS.S3()
```

To create our multipart upload, we have to ask AWS to create a unique one for us. Once successful, they'll give us a unique id back we can use to identify our upload. Here it is in async format:

```javascript
const { UploadId } = await s3.createMultipartUpload({
    Bucket: bucket,
    Key: latestAsteroids.filename
})
.promise()
```

## Currying in JavaScript with Crash Course on JavaScript Functions

... however, we don't want to do imperative style coding with all the error handling on us. We want to do it pipeline style just like in the `Parse Masses` PyMonad example, so we'll instead make this its own function:

```javascript
const createMultipartUpload = s3 => bucket => filename =>
    s3.createMultipartUpload({
        Bucket: bucket,
        Key: latestAsteroids.filename
    })
    .promise()
    .then(
        result =>
            result.UploadId
    )
```

There is a lot going on in that function, so let's break it down with a crash course in JavaScript functions and their varying styles.

### Arrow Functions vs the Rest

JavaScript used to use [function declarations](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/function):

```javascript
function createMultipartUpload(s3, bucket, filename) {
    ...
}
```

These have some special features, many of which are anti-functional programming. They can be used before they're defined since JavaScript, as opposed to F#, has a two-pass style parsing:

```javascript
// this is ok
createMultipartUpload(...)
function createMultipartUpload(s3, bucket, filename) {
    ...
}
```

However, they have a lot of Object Oriented and imperative baggage we want no part of. Examples include special keywords they support  like `this` (Python's `self`), `super`, and `arguments` amongst many others. Before JavaScript got the `class` keyword, you'd actually use the above as a constructor function for creating class instances:

```javascript
var instance = new createMultipartUpload(...)
``` 

JavaScript also supports [anonymous functions](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Functions), also called function expressions:

```javascript
const createMultipartUpload = function(s3, bucket, filename) {
    ...
}
```

Again, same problems with declarations with the OOP baggage.

Also, neither curry very well. Here's how you manually curry (i.e. without using a library) a declaration:

```javascript
function createMultipartUpload(s3) {
    return function(bucket) {
        return function(filename) {
            ...
        }
    }
}
```

Gross.

The rise of [jQuery](https://jquery.com/) created a style of code writing where you'd put functions as callbacks, i.e. "Call this function when the click happens":

```javascript
$('#button').click(function() {
  alert( "Handler for .click() called." );
})
```

That kind of mashing together, even with anonymous functions, is verbose and hard to read. For a variety of reasons, Arrow Functions (or Fat Arrow Functions, `=>` instead of `->`) were created, and make that look a lot nicer:

```javascript
$('#button').click(() => {
  alert( "Handler for .click() called." );
})
```

The arrow function intentionally removes a lot of the functionality from declarations such as `this`, and adds features such as no longer needing the `return` keyword if you remove the squiggly braces `{}`:

```javascript
const sup = () => {
    return 'sup'
}
// vs
const sup = () => 'sup'
```

Which brings us back to currying using Arrow Functions being A TON more readable (unlike my prose):

```javascript
const createMultipartUpload = s3 => bucket => filename =>
...
```

Yeah... exactly, vs:

```javascript
function createMultipartUpload(s3) {
    return function(bucket) {
        return function(filename) {
            ...
        }
    }
}
```

## Promise Crash Course

The JavaScript Promise has a variety of ways to use it. For Functional Programmers, we try to keep them with a single input, single output, so actively avoid all the multitude of optional parameters they have. Typically `then`'s will only have 1 function, and you'll only have 1 `catch` attached to the entire chain.

You can return whatever you want from a Promise, and as long as it's not a JavaScript `Error`, it'll resolve that for anyone to use:

```javascript
const sup = () =>
    Promise.resolve('sup')
```

... will resolve to `'sup'`:

```javascript
sup()
.then(log) // sup
```

And this will resolve to `'🐮'`:

```javascript
// notice I completely ignore the sup value in the first then
Promise.resolve('sup')
.then(
    () =>
        'cheese'
)
.then(
    yo => {
        if(yo === 'cheese') {
            return '🐮'
        }
        return Promise.resolve('no clue, bruh')
    }
)
```

Using `return value` or `Promise.resolve(value)` is the same except for super edge cases; both will give you `value` in the `.then`. If you return nothing, then the Promise will resolve, but have no value in the `.then`. That's ok for imperative/OOP developers. For FP, at a minimum return `true` or `false`.

You can even stop error handling if it's something you were expecting:

```javascript
const writeToDynamoDB = () =>
    Promise.resolve(true)
    .then(
        () =>
            dynamo.write('stuff')
    )
    .then(
        result =>
            log("result is:", result) ||
            result
    )
    .catch(
        error => {
            if(error.message === 'throttled') {
                return Promise.resolve(false)
            }
            return Promise.reject(error)
        }
    )
```

While the AWS SDK supports callbacks by default, that pattern is imperative, only supports chaining with a library, has a mistake prone imperative error handling model, and is hard to read nest. The `.promise` method of all JS SDK's supports getting a Promise back instead.

## Why No Async/Await

The async/await syntax is much more readable than Promises to those used to imperative programming. I use it still heavily in unit tests. We won't be using it here, though, as it doesn't support Functional Programming as it puts the error handling on you. There are ways around it by ensuring Promises never fail, but it's more pragmmatic to just use what Promises are good at: defining a `catch` in one place. We're trying to get you thinking in "pure pipes" for pipeline style programming. Functions, Lambdas, Step Functions... they're all just pure functions you pipe together and hopefully only have a few places for error handling. That philosphy is what we're going for across our stack and languages.

## Using createMultipartUpload

Let's implement our `createMultipartUpload` in our handler to showcase some conventions about her:

```javascript
const handler = async (event) => {
    const { bucket, latestAsteroids } = event
    const s3 = new AWS.S3()
    createMultipartUpload(s3)(bucket)(latestAsteroids.filename)
    .then(
        uploadID =>
            ...
    )
    .catch(
        error =>
            log("error:", error)
            || Promise.reject(error)
    )
}
```

Inside of `handler` is a bit of controlled bedlam. We've shown before it's the only place you should be intentionally raising Exceptions. This is so they're easily found during debugging, and so you the developer are aware of the "public interface" you're exposing to the Step Function in both retriable errors vs. automatic failure ones. For Functional Programming where you're not using the Effect pattern, and instead need to instantiate concrete objects, like our `S3` instance, this is where you do it as well. Anything functionally below it can just use it via the function closure. You may have other places that are lazy, and may `throw` or use the `new` keyword, and that's fine. If you're going to that level, then you've probably done your due dilligence and you're receiving `Result`'s or Errors there in a central place anyway.