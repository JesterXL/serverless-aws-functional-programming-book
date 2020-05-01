# Are We Good?

Let's start creating predictable functions using the Golang style of error handling. First, we'll take our existing, imperative style and move it to a function:

```python
def download():
    try:
        result = urlopen(EXOPLANET_URL)
        data = result.read()
        return (result, None)
    except Exception as e:
        print("download failed:", e)
        return (None, e)
```

Let's break it down. First, we implement a try/except block around our `urlopen`. There are tons of things that can go wrong, and none of which are currently recoverable. Either it works, or throws errors for information purposes. Having long `except SomeTypeException` doesn't do anything beyond add more verbose logging with zero gain. More importantly, though, it ensures our function only has 2 things it can do: work or not.

Second, we capture the result and then read from it from the `urlopen` call vs. just returning it directly. This ensures we're explict about what we're returning. While the result is fine, the read operation could fail. You can just shove `urlopen(blah).read()` in there in the return tuple, but it makes things crowded and hard to read, and unclear which part failed. Python doesn't really supporte putting things on multiple lines and encourages short, 1 liners. While we're already well beyond [PEP compliant Python](https://pep8.org/), we still try to follow universal standards of easy to read code vs. mushed together code. Finally, it makes it easier to inject logs later for specific return values if we need to inspect further.

Third, we both log the error _locally_ in the function with a minimal amount of context (function name, what happened) plus the error itself. Then we return that instead.

## Consuming Golang Style

Using that function, our Lambda's handler now looks like:

```python
def lambda_handler(event, context):
    exoplanet_data, error = download()
    if error != None:
        raise error
    return event
```

## Upload

We'll take the upload code from `download-benner` and change it to Golang style:

```python
def upload(exoplanet_data):
    try:
        result = boto3.client('s3').put_object(
            Bucket="asteroid-files", 
            Key="exoplanet.csv", 
            Body=exoplanet_data
        )
        return (result, None)
    except Exception as e:
        print("Upload to S3 failed:", e)
        return (None, e)
```

The cooler part of this version is how the AWS SDK works for Python. If it doesn't throw, what you're doing probably worked. They ONLY throw errors for failtures. That means this try/except style is extremely predictable with their battle tested SDK's.

## Using Together

Now we can thread them together:

```python
def lambda_handler(event, context):
    exoplanet_data, error = download()
    if error != None:
        raise error

    result, error = upload(exoplanet_data)
    if error != None:
        raise error
    
    return event
```

Notice, though, I've used `raise` rather than return. Step Functions follow the model of "return value or throw an Exception" so we're abiding by that contract. However... could we do better?

## Retry or Broken?

As we mentioned earlier, most errors are extremely time bound what they mean:

1. It failed now, and won't work if you retry in the future.
2. It failed now, but _may_ work if you retry in the future.

We need to clearly differentiate between those. We're going to use simple Exception names for now for that intent. As your code base grows, you can either lump all failures into 1, just like you do with a try/except, or create different ones in case your Step Function needs to retry a different way.

For now, we KNOW we can retry if the NASA website is down since we don't control it, but if our S3 fails, it's 99% of the time a permission issue or code issue, and there is zero point retrying until we fix it.

Let's create 2 custom Exceptions in Python:

```python
class HTTPError(Exception):
    pass

class GeneralError(Exception):
    pass
```

HTTPError? Cool, we can retry.
GeneralError? We're screwed, give up because we'll have to fix the code.

## Wait, Why Raise?

In Golang, the docs aren't really clear about _why_ you don't want to use `panic`, which is basically other languages `throw` or `raise`. Basically if the error is horrible/fatal/unrecoverable, then you should just panic, but there is no clear definitions what horrible/fatal/unrecoverable actually is. So bottom line, avoid it if you can.

Functional Programmers when forced to use a non-functional language follow the same rule: avoid raising an Exceptions.

So why did we `raise`? Even those who encourage using `raise` in Python or other such languages prefer you do it from the highest level function possible. This prevents you from having to deep dive into many different files and functions to find the source of an error. Instead, it's right at the the top with hopefully enough context as to what went wrong.

Our case is that plus one additional reason: The Step Function can react to it.

Step Functions can retry. They can wait for 1 year. They can wait as long as you want between retries. They can even exponentionally back off, each retry waiting longer than the previous. They can even have their own try/catch/finally style.

Again, to FP and Golang error style affeciandos, this may seem abhorent, but this _is_ the interface they provide, so we'll make the most of it (I promise it gets a bit better later for you FP zealots).

Your next question is "Well, wait, why not let the Lambda retry? I mean, the code is right there, and doing synchronous retry is quite easy in that Python doesn't have weird async style like JavaScript if you don't want it to". True but, remember why we're doing microservices:
1. small, simple, focused code.
2. Retry is more code
3. Lambda's have a time limit, Step Function's have a huuuuge one
4. micro-servies usually aren't orchestrators (services that use multiple services together); that's what the Step Function was built for

So, we `raise` at the top to make errors clear where they are, what caused them, with enough context as to why. We use _custom_ Exceptions so the Step Function has a clear, binary interface on which to operate, answering "Can I retry or not?"

## Custom Exceptions

Let's use our custom exceptions:

```python
def lambda_handler(event, context):
    exoplanet_data, error = download()
    if error != None:
        raise HTTPError('Failed to download exoplanet data.')

    result, error = upload(exoplanet_data)
    if error != None:
        raise GeneralError('Failed to upload exoplanet data to S3.')

    return result
```

Great, and to test it out, we put our module check at the bottom:

```python
if __name__ == "__main__":
    try:
        result = lambda_handler({}, {})
        print("result:", result)
    except HTTPError:
        print("HTTP failed.")
    except GeneralError:
        print("General error.")
    except Exception as e:
        print("unknown error:", e)
```

## Caveats

The caveat to this is Python doesn't print out stack trace information along with Exceptions when you use custom ones like this. You have a couple options if you want to see them again, one of which is below.

Using the standard `traceback` Python 3 library, you can get access to, and format stack traces. Just import it, and put below your exception:

```python
import traceback

...
    except Exception as e:
            print("Upload to S3 failed:", e)
            traceback.print_exc()
            ...
```

## Deploy

Run `sam build && sam deploy` as we'll use her in our next section.