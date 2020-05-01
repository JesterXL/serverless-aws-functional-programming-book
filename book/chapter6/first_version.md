
## From Golang...

Let's create a Go style of this Lambda first, then we'll refactor to a stream one, and you'll start to see how much code you no longer have to write, yet still retain the simplicity of "only 2 paths".

First up, we gotta open up our masses text file. This open command could fail, as could the reading of it, so we'll make 'em 2 different functions.

```python
def open_masses():
    try:
        mass_file = open('./masses.txt', 'r')
        return (mass_file, None)
    except Exception as e:
        print("Failed to open masses.txt:", e)
        return (None, e)
```

This'll pass back the file object if it's successful, else why it failed to open it. Next up, we have to read the lines:

```python
def read_mass_lines(mass_file):
    try:
        lines = mass_file.readlines()
        mass_file.close()
        return (lines, None)
    except Exception as e:
        print("Failed to read the lines from the masses.txt:", e)
        return (None, e)
```

This one takes an input of the file, and attempts to read lines from it. Assuming that is successful, we'll then close the file handle.

Now that we have 2 functions, let's start wiring them up in our handler:

```python
def lambda_handler(event, context):
    mass_file, error = open_masses()
    if error != None:
        raise error

    lines, error = read_mass_lines(mass_file)
    if error != None:
        raise error

    return event
```

We open the masses file, and assuming that works, we attempt to read the lines from it. So far, so good.

The parsing is a bit dangerous. There are many type conversions, calling methods on items that might potentially be `None`, all of which is done in multiple loops that are not list comprehension loops, meaning they have their own state. For now, we'll assume the algorithm is sancrosanct, and just do our best to work around it, else risk breaking the core math.

```python
def mass_lines_to_dictionary(lines):
    try:
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
        return (massd, None)
    except Exception as e:
        print("Failed to parse the masses:", e)
        return (None, e)
```

Then using it in our handler:

```python
massd, error = mass_lines_to_dictionary(lines)
if error != None:
    raise error
```

Great, only 2 steps left: convert it to JSON and upload to S3.

```python
from json import dumps
...
def massd_to_json(massd):
    try:
        press_x_for_jason = dumps(massd)
        return (press_x_for_jason, None)
    except Exception as e:
        print("Failed to convert massd to JSON:", e)
        return (None, e)
```

Wiring her up in the Lambda's handler:

```python
jay_sawn, error = massd_to_json(massd)
if error != None:
    raise error
```

... and lastly uploading the JSON to S3:

```python
import boto3
...
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

Merging her into lambda handler as the last one gives us:

```python
def lambda_handler(event, context):
    mass_file, error = open_masses()
    if error != None:
        raise error

    lines, error = read_mass_lines(mass_file)
    if error != None:
        raise error

    massd, error = mass_lines_to_dictionary(lines)
    if error != None:
        raise error

    jay_sawn, error = massd_to_json(massd)
    if error != None:
        raise error

    result, error = upload(jay_sawn)
    if error != None:
        raise error

    return result
```

Ok, our 5 step process done as safely as possible without refactoring key algorithms:
1. opens a text file
2. attempts to read lines from it
3. attempts to create a Mass dictionary with data and avergages for all known mass data for asteroids
4. convert that Dictionary to a JSON String
5. upload it as a JSON file to S3 for use later
6. return S3 result for Step Function to see

Final Code:

```python
from json import dumps
import boto3

def open_masses():
    try:
        mass_file = open('./masses.txt', 'r')
        return (mass_file, None)
    except Exception as e:
        print("Failed to open masses.txt:", e)
        return (None, e)

def read_mass_lines(mass_file):
    try:
        lines = mass_file.readlines()
        mass_file.close()
        return (lines, None)
    except Exception as e:
        print("Failed to read the lines from the masses.txt:", e)
        return (None, e)

def mass_lines_to_dictionary(lines):
    try:
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
        return (massd, None)
    except Exception as e:
        print("Failed to parse the masses:", e)
        return (None, e)

def massd_to_json(massd):
    try:
        press_x_for_jason = dumps(massd)
        return (press_x_for_jason, None)
    except Exception as e:
        print("Failed to convert massd to JSON:", e)
        return (None, e)

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

def lambda_handler(event, context):
    mass_file, error = open_masses()
    if error != None:
        raise error

    lines, error = read_mass_lines(mass_file)
    if error != None:
        raise error

    massd, error = mass_lines_to_dictionary(lines)
    if error != None:
        raise error

    jay_sawn, error = massd_to_json(massd)
    if error != None:
        raise error

    result, error = upload(jay_sawn)
    if error != None:
        raise error

    return result
```