# Deploying

To deploy, you typically build your code, then deploy.

Build. Then deploy.

You need to build when:

- You've changed non-unit test code in your Lambdas.
- You've changed something in `template.yaml`.

Running `sam build` will package up your code locally for deployment, and compile your `template.yaml` file to CloudFormation. If you see a `.aws-sam` folder in your code repo, that's what is in there. The build command does a few things, but one in particular you'll rely/hate on a lot is the validation of our `template.yaml`. You can do this by itself running `sam validate`. Sometimes the Python they use to call this doesn't handle exceptions so you'll have to search to find the YAML validation error. I highly encourage you to use <a href="https://dhall-lang.org/#">Dhall</a> or some other language that has types + yaml validation so you don't lose hours of your life for nothing. Thankfully, the SAM version of CloudFormation emits mostly CloudFormation errors, and Google is reasonably good providing solutions/reasons for those errors.

Once `sam build` is successful, you can then run `sam deploy`. This is so common a workflow, I'll often just run `sam build &amp;&amp; sam deploy`. This will upload all your packaged code Lambdas and other deployable items to an S3 bucket first, then attempt to run the CloudFormation template in AWS.

However, if this is your _first_ time deploying, you'll probably want to do `sam deploy --guided`. This'll create a `samconfig.toml` file. You only have to do this once. When you run `sam deploy`, she'll reference this file on how to configure things. It has things like what bucket is it uploading things to, if you want to confirm deployments, and `CAPABILITY_IAM` to default to using what IAM roles you define in your `template.yaml` vs. creating new ones for you; important for those of us in Enterprise AWS environments where we can't easily create our own IAM Roles. 

Run `sam build &amp;&amp; sam deploy` and we'll check out what she makes. Don't forget to name it (yes... again, lol) "asteroid-app". If you mess it up, no worries, just edit the `samconfig.toml` file with the correct name.