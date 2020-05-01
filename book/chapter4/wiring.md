# Wiring In Your Lambda

To have the Step Function use your Lambda, you'll need to modify 2 things in your Definition JSON. Feel free to edit it in the AWS Console first since it's better there helping you ensure you get the syntax correct and providing code hints. We'll have to change it's type from a `Pass` to a `Task`, and add a `Resource` property that is our Lambda Arn.  

So this:

```json
"Download Benner": {
  "Type": "Pass",
  "Result": "Hello",
```

Becomes this:

```json
"Download Benner": {
  "Type": "Task",
  "Resource": "arn:aws:lambda:us-east-1:089724945947:function:asteroid-app-DownloadBennerFunction-RRB3UVYDWLQ7",
```

The type `Task` is usually for Lambdas, but could be other things like <a href="https://docs.aws.amazon.com/step-functions/latest/dg/connect-batch.html">calling Batch</a>, <a href="https://docs.aws.amazon.com/step-functions/latest/dg/connect-ddb.html">putting an item in Dynamo</a>, or waiting for some rando piece of infra to <a href="https://docs.aws.amazon.com/step-functions/latest/dg/connect-sqs.html">respond to your SQS message</a>. The `Resource` is it's ARN. We've removed `Result` because that's up to the Lambda to decide what she returns, if anything.

... but that sucks. Having to hardcode the ARN isn't good for a few reasons. First, when you delete or redeploy, it's broken. Second, it's got the region hardcoded in there. Although I'm not covering a ton of best practices in this article, you should avoid EARLY in the project not hardcoding region if possible in case you need an active/passive or active/active scenario where you want the same code in east and west (for American deployments in the east, we usually fail over in the west in case the east breaks). Third, just like variables, you may want to change the name later and hardcoding the ARN prevents that.

We can instead use a the CloudFormation syntax to dynamically get the ARN, and SAM makes it a teency bit smaller. Let's change our Step Function definition to use it dynamically.

```yaml
DefinitionString:
  !Sub
  - |-
    {
      "Comment": "Loads asteroid data from various NASA sources, parses, and puts into a database.",
      "StartAt": "Download Benner",
      "States": {
        "Download Benner": {
          "Type": "Task",
          "Resource": "${downloadBennerLambda}",
          "End": true
        }
      }
    }
  - { downloadBennerLambda : !GetAtt DownloadBennerFunction.Arn }
```

Yaml, CloudFormation, and SAM's enhancements are a lot to take in, so let's break this snippet of the Step Function down. The `!Sub` is short form for <a href="https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-sub.html">Fn::Sub</a>, it's a function in CloudFormation to do string replacement with variables. In Python, you do that use `f'A var will be replaced {here}'` where the `here` is some variable in Python that it'll replace in the string. So if `here` is "cow" then after the Python code runs, the string will be "A var will be replaced cow". We want our `Resource` to be replaced with our Lambda arn. We don't know that, though, until the template is compiled, we create a variable to store it. You see that `downloadBennerLambda`? That's the variable; it equals whatever the Arn is of our Download Benner Lambda.

So... `!GetAtt`; he's another one. If you want to get an attribute / property / value of one of our resources in the template, `!GetAtt`, or <a href="https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getatt.html">Fn::GetAtt</a> is how you do it. You'll often see the Array / List syntax in a lot of documentation examples, which is fine, I just like the shorter version that feels more like code.

`!GetAtt DownloadBennerFunction.Arn`

vs.

`!GetAtt [ DownloadBennerFunction, Arn ]`

Ok, the squiggly braces / flower braces `{}`, we're creating a place to hold a bunch of variables. Right now, we only have 1, the `downloadBennerLambda`, but we'll add more Lambda functions as our code base grows to match our original architecture diagram.

Finally, we've used the Yaml `-` to indicate it's a list item. The first item in the list is the Step Function definition JSON, and the second is our variables. This is how the !Sub/Fn::Sub function works for Yaml, it prefers a list. The `-|` characters is one of the 9 (at the time of this writing) ways in which to do multiline strings in Yaml.

If you're curious, this is how you'd write the above in Python:

```python
from string import Template
download_benner_lambda_arn = "arn:aws:lambda:us-east-1:089724945947:function:asteroid-app-DownloadBennerFunction-RRB3UVYDWLQ7"
t = Template("""{
    "Comment": "Loads asteroid data from various NASA sources, parses, and puts into a database.",
    "StartAt": "Download Benner",
    "States": {
    "Download Benner": {
        "Type": "Task",
        "Resource": "$arn",
        "End": true
    }
}""")
definition = t.substitute(arn=download_benner_lambda_arn)
print(definition)
```

Cool? Save and run `sam build &amp;&amp; sam deploy`.