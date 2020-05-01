# Learning About The Lambda Contract

When creating functions, microservices, or even Lambdaliths (all code in single Lambda vs many === Lambdalith), there is this unspoken contract in AWS in how Lambdas work with everything. It's called "The Lambda Contract™" and it goes like this:

> Did it throw an Exception?
> Yes? It failed.
> No? It worked.

If you've been programming long enough you know that statement is full of gray area. However, it's fundamental to how AWS works with Lambda functions. Despite being very Functional Programming styled (it has <a href="https://en.wikipedia.org/wiki/Lambda_calculus">Lambda calculus</a> in the name), not all languages are functional, and many embrace exceptions and runtime errors. Like the Erlang motto, AWS Lambda has wholly incorporated "let it crash" into their core architecture. Crashes are EXPECTED. They are part of the api expectations. You need to plan for them, expect them, and assume they a normal part of operations.

Exceptions are not exceptional in Serverless. They are just another return value that isn't an Either or Result from a Functional Programming perspective.

We're going to put this Lambda, and many others, in an AWS Step Function. The Step Function will invoke the Lambda function with some input, and receive the output. However, it's also a try/catch/finally style service. If they Lambda crashes, the Step Function will assume it failed. You have many options here how to interpret, and continue with that failure that can be acceptable. Anything that triggers/calls/invokes Lambdas follows the Lambda Contract. SQS: Did the Lambda handle my message without crashing? Cool, it's off the queue. Kinesis: Did the Lambda handle my message without crashing? No? Lemme try 2 more times. No? It did not handle my message, I'll send to a Dead Letter Queue instead. Lambda Invoke: Did the Lambda return a value? No? Am _I_ wrapped in a try/catch?

I want to be clear here: There were ONLY TWO options in the Lambda Contract, and ONLY ONE eventuality in the error scenario: It didn't work. This isn't like some Java or Python code where they handle 4 kinds of Exceptions with different code paths. No, this is the opposite: Either it worked, or it didn't. There IS no gray area. While you can do that type of exception handling in your code, that's not how Lambda works, nor how the various AWS services integrate with it.

What this means for our code, then, is we should endeavor to follow that contract. We do that by fulfilling the contract. "Yeah, if we don't throw an Exception, we're good, it worked". Oh rly? This is where things get fuzzy, and programming becomes hard again. Let's review just our 10 line function:

```python
def lambda_handler(event, context):
    data = urlopen('http://echo.jpl.nasa.gov/~lance/delta_v/delta_v.rendezvous.html').read()
    lines = data.splitlines()
    csv = parse_csv(lines)
    result = boto3.client('s3').put_object(
        Bucket="asteroid-files", 
        Key="benner_deltav.csv", 
        Body=csv
    )
    return result
```

Ready? Think about these answers and what they entail:

- What happens when there are too many Lambda invocations in my account?
- What happens when my Lambda when the IAM role/security groups don't allow internet access?
- What happens if the `urlopen` fails because the site is down?
- What happens if the data is too large for the Lambda memory size I chose and `splitlines` throws an Exception?
- What happens if `.read()` gets something other than a string? Does that mean `data.splitlines()` throws an Exception?
- When happens if `parse_csv` can't actually parse our data into CSV because the HTML has changed, breaking the regular expression or field names have changed?
- When happens if my IAM role doesn't allow `s3:put_object` permission?
- When happens when my bucket is deleted or has another name?`

That's just a few things that can go wrong. One approach is to wrap the whole thing in a try/except:

```python
def lambda_handler(event, context):
  try:
    data = urlopen('http://echo.jpl.nasa.gov/~lance/delta_v/delta_v.rendezvous.html').read()
    lines = data.splitlines()
    csv = parse_csv(lines)
    result = boto3.client('s3').put_object(
        Bucket="asteroid-files", 
        Key="benner_deltav.csv", 
        Body=csv
    )
    return result
  except Exception as e:
    print("Failed:", e)
```

... But then new, horrible questions are raised. It's ok if the site is down. I mean, we can retry. Step Functions can run for an entire year, what's a few minutes, hours, or days as long as the data is eventually updated that week, yah? How do we easily interpret that Exception amongst the many? That particular Exception isn't that exceptional.

That last question is the key as you'll start seeing more and more gray areas. Instead of following the path to madness, think of it like this:

> Can I retry?
> Yes? Cool, retry.
> No? We're screwed, here's why.

This allows you to follow the Lambda Contract, yet still have enough information to debug what went wrong, AND potentially retry for situations that warrant it. I'm simplifying it, no doubt, as you'll still find gray areas and edge cases where some Exceptions may be recoverable, and others, not so much.

Let's do a first attempt at this. This will allow our Step Function to have clear insight into success or failure of our function, and make it easier for us to test our service. You'll create 2 custom Exceptions in Python: one for overall failure, and one for http connection failure. Overall means we're screwed and something is broken that requires code to be fixed or infrastructure to be changed. The other, however, means there is still a chance of success, we just need time.

For you FP'ers following along, I want you to breathe slowly. Brace yourself: We're going to use the `class` and `raise` keywords in Python. Think of it like data, a return value from a function, not an Object Oriented / Imperative construct. We're creating 1 custom error, so it's basically a Union type: Our Data, Retry, or Error. We'll then pattern match in the Step Function against that. Also, F# has classes too. Feel better? No? Drink and workout, they helped me.

Here's our custom error, signaling to the Step Function, or anyone, that a retry is possible.

```python
class HTTPFailure(Exception):
    pass
```

Now, we can modify Lambda function to use it:

```python
def lambda_handler(event, context):
    try:
        result = urlopen('http://echo.jpl.nasa.gov/~lance/delta_v/delta_v.rendezvous.html')
    except Exception as e:
        raise HTTPFailure(str(e))

    data = result.read()
    lines = data.splitlines()
    csv = parse_csv(lines)
    result = boto3.client('s3').put_object(
        Bucket="asteroid-files", 
        Key="benner_deltav.csv", 
        Body=csv
    )
    return result
```

Cool, let's test it out right quick. We'll modify how we invoke it using old sk00l multi-exception handling:

```python
if __name__ == "__main__":
    try:
        result = lambda_handler({}, {})
        print("result:", result)
    except HTTPFailure:
        print("HTTP failed.")
    except Exception as e:
        print("unknown error:", e)
```

... and then turn our wireless off and run it.

`HTTP failed.`

Great! We can then wire up that Lambda in our Step Function with the ability to retry on something that can possibly be recovered from. All other errors can't, so there is zero point creating custom exceptions for them, and moving on (we'll ignore Lambda invocation throttling for now).