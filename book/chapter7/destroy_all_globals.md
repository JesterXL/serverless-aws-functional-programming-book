# Destroy All Globals

Now while Lambdas may "feel" like infrastructure, they truly _are_ functions. Meaning, we can give them different inputs to have them produce different outputs. You can't reliably do that if they have global variables. The hardcoded globals I'm referring to are the bucket name the Lambdas are using, and the file names they are using when they upload files.

We have 2 options here. The first is the utilize the `template.yaml` to leverage CloudFormation, and have all our globals defined as environment variables. Then our Lambdas can use those.

The OTHER way is to treat them like true pure functions and only use data they got from their inputs. Screw environment varaibles. Screw globals. Let's keep things as stateless as possible, and continue to push the side effects/state as high as possible until AWS releases another product that solves that problem and we can then update this book to use that.

It'll also make the Lambdas easier to unit, integration, and end to end test later on since there is no globals to muck around with.

## Parallel State: Same Input, 3 Functions

Parallel's are interesting in that all the child states get the same input. However, each function needs differnet information. Step Function's JSON isnt' actually JSON, but something called JSONPath. It allows you to do queries in the JSON, and change inputs and outputs. We'll define all 3 of our Lambda's needed configuration data, and then tailor the input for each function so the Lambda code can remain dumb and work as it is.

## Global Variables to Remove

Let's get a list of global variables we have to remove from each function.

