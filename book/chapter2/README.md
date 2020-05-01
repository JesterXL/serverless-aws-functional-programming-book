# AWS SAM - Serverless Application Model


SAM is AWS's tooling to build, locally test, and deploy serverless applications. While AWS has a ton of ways to build and deploy stuff, SAM is specifically made for Serverless on AWS (<a href="https://serverless.com/">Serverlesss framework</a> is cloud agnostic). The pro's/con's:

- a single repo for all of your code vs many. This has positive implications for those of us in enterprises where our pipelines are slow and hard to modify.
- single template that defines your application 
- ability to nest applications
- ability to deploy with 1 command
- ability to deploy different environments (kind of of, not as easy as Serverless)
- You can see all your infra in AWS console linked via a single screen
- Open Source CLI

There are other things that it does that I don't use/care about, but others will rave over:

- ability to run Lambdas locally (and by "run", they mean in Docker with local API or CLI to invoke them with your own JSON... this, as opposed to.. you know, `node app.js` or `python main.py` which... you know... still work)
- ability to generate stub events which ... ok, is super awesome, I just am lazy to memorize the commands to do so, I instead google JSON examples and copy paste
- simplified version of CloudFormation for common serverless things like Lambda, API Gateway, and simpler Dynamo tables

## Setting Up SAM

Follow the instructions for <a href="https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html">setting up AWS SAM</a>, and then return here to follow along. We're going to start with their HelloWorld for Python, and continually modify.

I'm a follower of <a href="https://www.accenture.com/us-en/blogs/blogs-lessons-from-rocket-science-part-1-2">all up testing</a>. Meaning, get your whole system up and running vs building each indestructible piece and later wiring together. However, for this, we'll gradually get there as I want to take you through all the details of building and testing each component as well as seeing the "range" of Functional Programming purity you can choose to, or not to, apply. Normally, I highly encourage you to setup Lambda stubs that vaguely follow the interface so you can have your Step Function up and running with all pieces as quickly as possibly. At that point, you can iterate on each piece individually and continually re-run your Step Function to smoke test manually are your JSON contracts are working together like you think.