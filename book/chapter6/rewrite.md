# Rewrite To Result

Let's rewrite our Golang example using `Result` instead.

## Install

First, ensure you've got your virtual environment setup, then install the AWS Python SDK and PyMonad, and PyDash:

`pip install boto3 pydash pymonad`

Then copy [my Result.py](https://gist.github.com/JesterXL/c7cf86608c3d4cd04a1dc68894cc8a4d) into your `parse-masses/Result.py` file.

Import ya boiyz up top:

```python
import boto3
from Result import *
```

## Manual Return Result

Let's rewrite our `open_masses` which is in Golang style:

```python
def open_masses():
    try:
        mass_file = open('./masses.txt', 'r')
        return (mass_file, None)
    except Exception as e:
        print("Failed to open masses.txt:", e)
        return (None, e)
```

Changing it to a basic, manual return of a `Result` looks like this:

```python
def open_masses():
    try:
        mass_file = open('./masses.txt', 'r')
        return Ok(mass_file)
    except Exception as e:
        print("Failed to open masses.txt:", e)
        return Error(e)
```

We only changed 2 lines of code, the return values; an `Ok` with the `mass_file` or an `Error` with whatever `Exception` that happened.

Let's integrate her in the `lambda_handler` and see what she looks like. Our old one had:

```python
def lambda_handler(event, context):
    mass_file, error = open_masses()
```

Our new one looks like so:

```python
def lambda_handler(event, context):
    result = open_masses()
```

Thinking ahead, we'll probably make that result some value we can use. For now, though, we'll just change as we learn what the new output is as we attache new functions or "pipes" to the ever growing pipe.

## Bind Together

Now that we know how to rewrite, let's do it again with `read_mass_lines`:

```python
def read_mass_lines(mass_file):
    try:
        lines = mass_file.readlines()
        mass_file.close()
        return Ok(lines)
    except Exception as e:
        print("Failed to read the lines from the masses.txt:", e)
        return Error(e)
```

And now to bind them together and test her out:

```python

def lambda_handler(event, context):
    result = open_masses() \
    >> read_mass_lines
    print(result)

if __name__ == "__main__":
    lambda_handler({}, {})
```

The `result` contains all of the file, so your output may be large, but it hopefully starts with something like:

```shell
Ok: [' 1 Ceres 9.55E+20 4.38E+19\n', ' 1 Ceres 9
```

That bracket (`[`) is the giveaway that it's a Python `List` and our `readlines` worked. Rad, so we've piped together 2 functions now, let's keep going. That same `result` will change over time as we add more pipes (functions with single input, single output) to modify our data.

## Try

This try/except sequence is so common in non-functional languages (or even in hybrids like F#) where the `try` concept of "Try this, and if it works, gimme back an Ok, otherwise if it fails, give me back an Error" has an actual method. It's called `try`.

Let's refactor that cray mass parser method first; JUST the algorithm we're taking out.

```python
def unsafe_parse_mass_lines(lines):
    massd = {}
    for line in lines:
        parts = line.split(' ')
        massidx = len(parts) - 2
        mass = float(parts[massidx])
        name = ' '.join(parts[:massidx]).strip()

        if name not in massd:
            massd[name] = []
            massd[name].append(mass)

    for name, masses in massd.items():
        avg = sum(masses) / len(masses)
        massd[name] = avg
    del massd['']
    return massd
```

We gave it the prefix "unsafe" to indicate calling it is unsafe; meaning not pure, could blow up, no try/catch, etc. Python isn't like Java where they have keywords like `throwable` that are enforced by a compiler, so like Ruby we just follow strange conventions you have to learn to understand wtf is going on.

Now, instead of using it like this:

```python
def mass_lines_to_dictionary(lines):
    try:
        massd = unsafe_parse_mass_lines(lines)
        return Ok(massd)
    except Exception as e:
        return Error(e)
```

We'll instead using the `Result.try` static class method:

```python
def mass_lines_to_dictionary(lines):
    return Result.try_(lambda: unsafe_parse_mass_lines(lines))
```

Note the `try_` underscore at the end, not `try` since `try` is a reserved word.

Instead of calling the function, we give `Result.try` a function and say "call this; if it works, cool, gimme the result in an Ok, otherwise gimme the exception in an Error". There are ways to pre-package that `lines` parameter to further reduce typing, but we'll get that later.

Let's wire this new `mass_lines_to_dictionary` to our pipeline:

```python
def lambda_handler(event, context):
    result = open_masses() \
    >> read_mass_lines \
    >> mass_lines_to_dictionary
    print(result)
```

Now you're beast printout should be something like:

```shell
Ok: {'1 Ceres': 9.55e+20, '2 Pallas': 2.41e+20, 
```

😀

## JSON Parse

Let's do that again, this time with a built in Python method `dumps`. Let's this this opportunity to go the _other_ way. Instead of explicity marking functions as "unsafe", let's create safe ones.

```python
def safe_dumps(dictionary):
    return Result.try_(lambda: dumps(dictionary))
```

Now, instead of using our `massd_to_json` function:

```python
def massd_to_json(massd):
    try:
        press_x_for_jason = dumps(massd)
        return (press_x_for_jason, None)
    except Exception as e:
        print("Failed to convert massd to JSON:", e)
        return (None, e)
```

... we can just delete it, and integrate our `safe_dumps` to our pipeline:

```python
def lambda_handler(event, context):
    result = open_masses() \
    >> read_mass_lines \
    >> mass_lines_to_dictionary \
    >> safe_dumps
    print(result)
```

That'll give you:

```shell
Ok: {"1 Ceres": 9.55e+20, "2 Pallas": 2.41e+20,
```

DEM DOUBLE QUOTES!

## Safe Upload

Last rewrite is our `upload` function. Let's use `try_` there as well.

The old one:

```python
def upload(massd_json):
    try:
        result = boto3.client('s3').put_object(
            Bucket="asteroid-files", 
            Key="massd.json", 
            Body=massd_json
        )
        return (result, None)
    except Exception as e:
        print("Upload to S3 failed:", e)
        return (None, e)
```

The new one:

```python
def upload(massd_json):
    return Result.try_(
        lambda: boto3.client('s3').put_object(
            Bucket="asteroid-files", 
            Key="massd.json", 
            Body=massd_json
        )
    )
```

And to put in our last pipe:

```python
def lambda_handler(event, context):
    result = open_masses() \
    >> read_mass_lines \
    >> mass_lines_to_dictionary \
    >> safe_dumps \
    >> upload
    print(result)
```

Results in a longer version of:

```shell
Ok: {'ResponseMetadata': {'RequestId': 'DFB9FF
```

🤯🤘🏼

## Any Booms?

Let's break her twice JUST to show you it doesn't matter where the error occurs in a pipeline.

In `read_mass_lines` just return an `Error` on the first line.

```python
def read_mass_lines(mass_file):
    return Error('bleh')
    try:
        lines = mass_file.readlines()
        mass_file.close()
        return Ok(lines)
    except Exception as e:
        print("Failed to read the lines from the masses.txt:", e)
        return Error(e)
```

Then re-run:

```shell
Error: bleh
```

Sick.

Undo that, turn your intenet off, then re-run which'll make that `upload` function fail.

```shell
Error: Could not connect to the endpoint URL: "https://asteroid-files.s3.amazonaws.com/massd.json"
```

## Exiting the Matrix

Now that we're in FP world, that's great, but... the Step Function is either expecting JSON or an Exception... not a `Result` converted to JSON. The easiest way is to use functions to do this via `match`, but you can't use `raise` in Python lambda's, so... it's just easier to use `.value`.

```python
if isinstance(result.value, Exception):
    raise result.value
return result.value
```

Now that we have a value, we can `raise` it if its an `Exception`, otherwise return it.

## Wrapping Up

Save and so a `sam build && sam deploy`.

The final code:

```python
from json import dumps
import boto3
from Result import *

def open_masses():
    try:
        mass_file = open('./masses.txt', 'r')
        return Ok(mass_file)
    except Exception as e:
        print("Failed to open masses.txt:", e)
        return Error(e)

def read_mass_lines(mass_file):
    try:
        lines = mass_file.readlines()
        mass_file.close()
        return Ok(lines)
    except Exception as e:
        print("Failed to read the lines from the masses.txt:", e)
        return Error(e)

def unsafe_parse_mass_lines(lines):
    massd = {}
    for line in lines:
        parts = line.split(' ')
        massidx = len(parts) - 2
        mass = float(parts[massidx])
        name = ' '.join(parts[:massidx]).strip()

        if name not in massd:
            massd[name] = []
            massd[name].append(mass)

    for name, masses in massd.items():
        avg = sum(masses) / len(masses)
        massd[name] = avg
    del massd['']
    return massd
    
def mass_lines_to_dictionary(lines):
    return Result.try_(lambda: unsafe_parse_mass_lines(lines))

def safe_dumps(dictionary):
    return Result.try_(lambda: dumps(dictionary))

def upload(massd_json):
    return Result.try_(
        lambda: boto3.client('s3').put_object(
            Bucket="asteroid-files", 
            Key="massd.json", 
            Body=massd_json
        )
    )

def lambda_handler(event, context):
    result = open_masses() \
    >> read_mass_lines \
    >> mass_lines_to_dictionary \
    >> safe_dumps \
    >> upload
    if isinstance(result.value, Exception):
        raise result.value
    return result.value

if __name__ == "__main__":
    lambda_handler({}, {})
```


