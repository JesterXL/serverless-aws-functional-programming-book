# Error Types

Let's learn about errors as they are a fundamental concept of Step Functions and how they interact with other services. They're also a pragmmatism Functional Programmers will just have to learn how to work with (think how F# isn't Haskell, lol). Seriously, FP people, I promise this isn't all there is to errors. We'll tackle it slowly over chapters, hang in there.

<img src="./Screen Shot 2020-04-25 at 10.22.05 AM.png"></img>

There are unofficially 3 types of errors you'll encounter in Step Functions.

1. service blew up
2. step function blew up
3. aws blew up

## Service Blew Up

Most of what you'll probably be dealing with is when a service done broke; specifically, when a service doesn't work as expected by raising/throwing an Exception. The JSON that coes to a Step Function isn't always obvious of source, but typically you'll find a few clues it was your Lambda. One is the stack trace has Python code in it:

<img src="./Screen Shot 2020-04-25 at 10.44.10 AM.png"></img>

Specifically our `app.py`. In this case the AWS Python SDK, called `boto3` which uses a lot of stuff from `botocore`, got an access denied when attempting to put an object. Like most exceptions, you start to memorize them + how you fixed them after you do it a few times. We'll fix that in the next section.

## Step Function Blew Up

Sometimes your JSON syntax is correct, but the dynamic things you do it in, such as using its [JSON Path](https://github.com/json-path/JsonPath) powers only fail at runtime; when you're actually executing your Step Function. These errors usually require you to just fix your Step Function's JSON, redeploy, and re-test.

## AWS Blew Up

These are weird, hard to track down, and sometimes they even have 2 different names... BUT you _can_ react to them positively. Examples include when your AWS Lambda is throttled, either because your account ran out of Lambda concurrency or for permission reasons. Sometimes network errors can occur, and not just for Lambda.

Bottom line, the Step Function is a big ole try/catch/finally, so rest assured even the ones you don't know about yet can be caught and reacted to vs. "I'll fix it when it happens".
