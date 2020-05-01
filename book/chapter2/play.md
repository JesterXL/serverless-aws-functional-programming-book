# Play in the Sandbox

Let's play around with some things. First, let's run our Lambda function the normal way you run things in Python: `python hello_world/app.py`

If you do that, she won't print anything, though. Let's open up the code and learn about the basic Lambda function they generated for us (I've removed the comments):

```import json

def lambda_handler(event, context):
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "hello world",
            # "location": ip.text.replace("\n", "")
        }),
    }
```

Almost all Lambda functions share the same 3 characteristsics:

- a function
- it takes an event, sometimes a context
- it may or may not return something

Most people who explain Lambdas talk about what "triggered" it, or invoked it. If you look at that code, nothing is invoking it. It's just importing a module called `json` and defining a function called `lambda_handler`, but nothing else. Let's invoke it the Python way. We'll add this at the bottom of `app.py` and save it.

```if __name__ == "__main__":
    print("Testing...")
    lambda_handler({}, {})
```

This means when when Lambda runs, or we import the code in unit tests, the `print` and `lambda_handler({}, {})` we added doesn't run.  When we want to test our code locally, though, it does: `python hello_world/app.py`.

Let's change it to run and print the return value:

```if __name__ == "__main__":
    print(lambda_handler({}, {}))
```

Cool, now if run `python hello_world/app.py`:

```{'statusCode': 200, 'body': '{"message": "hello world"}'}
```

Nice. That's the JSON that would be returned if you called your Lambda in AWS via the API Gateway URL. It's also the exact same thing if you run your Lambda locally. It's just a function returning a dictionary.