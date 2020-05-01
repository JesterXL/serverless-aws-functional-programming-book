# IAM Role Permissions

Ok, so back to why our Lambda failed with an access denied with a put object. Thankfully our service is a micro-service so it (hopefully, unless you have kids like me and yo brain don't work) doesn't take long to guess where in our code it could possibly throw something like that:

```python
result = boto3.client('s3').put_object(
        Bucket="asteroid-files", 
        Key="benner_deltav.csv", 
        Body=csv
    )
```

So why isn't it allowed? Well, all of AWS for the most part is allowed to work via IAM Permissions, or "Identity Access Permissions". ALL of AWS' services use the same thing. The good news is if you have a permission's issue, 90% of the time, that's why. The bad news is, there are 50 billion permissions for you to memorize, but at least they're named well.

AWS SAM helps a lot here if you're not in an Enterprise environment.

## IAM Role and Permission Types

We're not going to cover a lot here, because again this stuff is boring and software is all about having fun, SO here's the short version.

IAM Roles typically go like this:

- Role ARN: You create a Role, and it has various things people using that role can do. "Full Access? You can do everything! Read this bucket? That's all you can do."
- AWS Managed Policy: AWS knows most services do reasonably common things, so they created policies to do those bais things. Example is the basic lambda role that allows you to execute it and sends logs to CloudWatch.
- Custom Policies: Only do this 1 thing.

Cyber loves custom policies. This ensures your Lambdas, Step Functions, etc. can ONLY do 1 teency thing, and it significantly reduces the attack surface area. It also is a royal pain to manage, debug, update, and test... but hey, we're safe, right? `<rant>` As programmers age, I feel most of us get more pragmmatic in a good way. Why do Cyber people seem to get more of a pain in my ass as _I_ get older?`</rant>`

One other piece of good news, our Step Function already has a good enough default IAM Role so most of our drama will be with various resources that the Step Function uses, not the Step Function itself.

## Enabling SAM Resources to Do Things

SAM helps a little bit by inferring these policies and doing it for you. For example, if you're Lambda is triggered by an S3 event, it updates/creates an IAM Role to allow those things and you don't have to worry about it in your `template.yaml`.

For non-reactive things, though, like our Lambda needing to write a file from an S3 bucket, we have to explictly state that.

We'll add policy to our Lambda stating this using an AWS Managed Policy `S3WritePolicy` which you may have guessed "Allows those who use this policy to write things to an S3 bucket... just give me the name of it".

```yaml
Policies:
- S3WritePolicy:
    BucketName:
    !Ref AsteroidFilesBucket
```

Also, let's take this opportunity to make fun of CloudFormation for a mintue. You'd think that'd be written like you'd write it in code:

```yaml
S3WritePolicy:
    BucketName:
    !GetAtt AsteroidFilesBucket.BucketName
```

Yeah, getting the attribute of the bucket, [BucketName](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3-bucket.html#cfn-s3-bucket-name) since that's what the [S3WritePolicy](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-policy-template-list.html#s3-write-policy) says it needs in the documentation, right?

Well, yeah, but... no. The above doesn't work using get attribute, you need the bucket reference. Of COURSE it needs a reference. * face palm *

## To Learn More

To learn more about various policies in SAM, [this is a good article](https://aws.amazon.com/premiumsupport/knowledge-center/lambda-sam-template-permissions/).

The managed policies you can use in SAM are [here](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-policy-template-list.html).

For those in an Enterprise environment where you don't create/modify IAM Roles yourself, you'll probably end up just using `RoleArn`'s. You'll just need more integration tests in your code to ensure role changes don't affect your code, and adding new code works with your existing role.

## Fixing Our Step Function

Save that first YAML in your template next to your Lambda function:

```yaml
DownloadBennerFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: download_benner/
      Handler: app.lambda_handler
      Runtime: python3.8
      Timeout: 60
      Policies:
      - S3WritePolicy:
          BucketName:
            !Ref AsteroidFilesBucket
```

... then `sam build && sam deploy`. Once done, run your Step Function again.

<img src="./Screen Shot 2020-04-25 at 11.15.11 AM.png"></img>