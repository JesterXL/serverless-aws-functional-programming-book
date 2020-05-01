# Creating & Testing the Step Function

We now have a working Lambda to download our Benner data. Lambdas on AWS are all about "who invokes it". They're typically tailored to that. CloudWatch Event running every day? Typically runs some code and returns no value. API Gateway or ALB? Return a JSON structure that looks like a REST call response. SNS/SQS/Kinesis? Nothing if it works, raise an exception intentionally or unintentionally to signal it didn't. Ours will be invoked by a Step Function... so what does that mean?

## WTF is a Step Function?

If you know, skip this part.

<a href="https://aws.amazon.com/step-functions/">Step Functions</a> are an AWS service that allows you to create a <a href="https://jessewarden.com/2012/07/finite-state-machines-in-game-development.html">state machine</a> and have it run various other AWS services, include other Step Functions. You use a more powerful JSON to define a flowchart of how your state machine works. You can visually see it being created, and when you run it, you can see each step work.

Step Functions were created because AWS lets you create a lot of stuff, but orchestrating all that stuff to work together is really hard... and involves <a href="https://www.youtube.com/watch?v=MvgN5gCuLac">more stuff</a>. The DevOps tooling exists now to make it much faster and easier to create a lot of your applications' pieces on AWS all at once. Step Functions can provide a way to BE the application when in reality it's calling Lambdas, Batch, sending messages to SQS queues, reading from DynamoDB, etc. 
The strength of Step Functions from an imperative and Functional Programming perspective, however, is AWS manages the state, and it's one big ole try/catch/finally with stateful retry. For all the things. That seems subtle, but has huge implications for saving you a lot of problems. A strength is that they can also run for a year. However, creating Tasks to ensure they don't run too long for asynchronous operations (a Promise / Future that can be cancelled) isn't doable yet.

Ok, back to Lambda invocations...

Step Functions usually have a lot of flexibility:

- Takes an input, returns an output. If it has side effects, it does its best to inform you in the JSON if it'll fit.
- Takes no input, returns no output, and is just all about that bass and side effects (like our Benner Lambda function above). This'll feel natural for imperative and Object Oriented Programmers.
-  Can't return a meaningful output beyond not crashing, so either no error == success, or you look elsewhere for the results of the side effects. <a href="https://aws.amazon.com/batch/">AWS Batch</a>, for example, doesn't support any meaningful return value beyond it ran or it crashed unlike it's non-serverless cousin <a href="https://aws.amazon.com/ecs/">ECS</a> which can.

As an ivory tower purist, I'm going to suggest you always do your best to do #1, #2 with SOME kind of return value, and only #3 if you're forced to use AWS Batch or some other system which returns no value but you still make an effort, perhaps in a subsequent Lambda, to go check if it _actually_ worked.

If you're familiar with <a href="https://jesterxl.github.io/real-world-functional-programming-book/part4/">Function Composition</a> / Composing Functions, Reactive style programming a la <a href="https://rxjs-dev.firebaseapp.com/">RxJS</a>, or a Functional Programming, #1 should feel quite natural. Instead of Lambdas having functions in them that are composed, you're composing the Lambdas together (or other things like queues and database tables). You don't have a lot of list/array comprehensions at your disposal in Step Functions beyond the default flow (<a href="https://returns.readthedocs.io/en/latest/pages/pipeline.html#flow">python</a> | <a href="https://lodash.com/docs/4.17.15#flow">javascript</a>) via a Step Function <a href="https://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-task-state.html">Task</a>, identity (<a href="https://pydash.readthedocs.io/en/latest/api.html#pydash.utilities.identity">python</a> | <a href="https://lodash.com/docs/4.17.15#identity">javascript</a>) via <a href="https://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-pass-state.html">Pass</a>, <a href="https://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-parallel-state.html">Parallel</a> which is kind of a Python async <a href="https://docs.python.org/3/library/asyncio-task.html#asyncio.gather">gather</a> | JavaScript <a href="https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/all">Promise.all</a>,  and <a href="https://docs.aws.amazon.com/step-functions/latest/dg/amazon-states-language-map-state.html">Map</a> which is a concurrent version of a normal map (<a href="https://www.geeksforgeeks.org/python-map-function/">python</a> | <a href="https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Map">javascript</a>). Sooooo adjust your thinking around offloading most of that list comprehension composing work to the Lambdas. The onus of supporting the Either (aka Result) pattern is on you. Aka, don't let your Lambdas explode. More on that later.

If you have no idea what any of that means, or you're from an Imperative / Object Oriented Programming, just know all the things you link together are wrapped in an implicit `try` with optional `except` / `catch` and optional `finally`.

> Did it fail? Do this instead.
> Did it fail? Retry... 3 times... and wait double the amount of time you did last time.. otherwise... give up and do this instead.

There's no variables for you to keep track off; the Step Function has it's own `this` or `self` that keeps all that state for you.
