# Clean Up

Now that we're in a good place, let's clean some things up. Mainly technical debt we've been ignoring.

- in your `template.yaml`, change your `HelloWorldFunction` to `DownloadBennerFunction` 
- remove the entire `Events` section because we're not using API Gateway for this at all
- fix the very bottom, the output documentation, to use your new DownloadBennerFunction
- fix the very bottom to use your new implied role `DownloadBennerFunctionRole` (more about implied magic in your SAM template later)

Your cleaned template should now look like:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: >
  asteroid-app

  Sample SAM Template for asteroid-app

Globals:
  Function:
    Timeout: 3

Resources:
  DownloadBennerFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: download_benner/
      Handler: app.lambda_handler
      Runtime: python3.8
      Timeout: 60
  
  AsteroidFilesBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: asteroid-files

Outputs:
  DownloadBennerFunction:
    Description: "Downloads and parses delta velocity information and puts the new CSV file on S3."
    Value: !GetAtt DownloadBennerFunction.Arn
  HelloWorldFunctionIamRole:
    Description: "Implicit IAM Role created for Hello World function"
    Value: !GetAtt DownloadBennerFunctionRole.Arn
```

And once saved do a final `sam build && sam deploy`.