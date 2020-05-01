# Inline Template

Keep that step function we created above around, it's super convenient to have a simple one quickly available to play with step function JSON so you can learn and test syntax. In AWS SAM, you define your stuff in `template.yaml`, so that's where we'll define ours. Since it's starting small, we'll do it inline in YAML as well. You'll add a new Resource, which means "text aligned with 'DownloadBennerFunction' and 'AsteroidFilesBucket'".

When in doubt, SAM mostly follows CloudFormation syntax, so refer to the main <a href="https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-stepfunctions-statemachine.html">CloudFormation docs</a> if you don't know a property.

It looks like this:

```yaml
GetAsteroidsDataStepFunction:
    Type: AWS::StepFunctions::StateMachine
    Properties:
      StateMachineName: get-asteroid-data
      RoleArn:
        !Sub
          - |-
            arn:aws:iam::${AWS::AccountId}:role/service-role/StatesExecutionRole-us-east-1
          - accountID: !Ref AWS::AccountId
      DefinitionString: !Sub |-
        {
          "Comment": "Loads asteroid data from various NASA sources, parses, and puts into a database.",
          "StartAt": "Download Benner",
          "States": {
            "Download Benner": {
              "Type": "Pass",
              "Result": "Hello",
              "End": true
            }
          }
        }
```

The `GetAsteroidsDataStepFunction` is what we're calling our Step Function resource. The `Type` let's SAM/CloudFormation know what type of resource, in this case, we're creating an AWS Step Function. For now we'll hardcode our `RoleArn` / IAM role the default one provided by AWS. You create your own, this is just easier to do basic executions. SAM DOES have intelligence to know who is using who and adjust that for you but for now we'll start with a basic one. We use whack YAML + SAM syntax to dynamically inject your account id in there so you don't have to hardcode it. Yes, I know we still hardcoded us-east-1...

Finally, our `DefinitionString` is your Step Function's JSON. This is the same JSON you put in the AWS Console to create your Step Functions. Since it's small, we'll keep in the template.yaml for now.

In your outputs at the bottom, add your Step Function:

```yaml
GetAsteroidsDataStepFunction:
    Description: "Gets asteroid data from Nasa, parses, and puts into Dynamo."
    Value: !Ref GetAsteroidsDataStepFunction
```

Save and run `sam build &amp;&amp; sam deploy`. You should see your Step Function created. 