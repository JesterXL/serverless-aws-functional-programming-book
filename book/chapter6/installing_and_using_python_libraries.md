# Installing and Using Python Libraries

A quick note on installing and using Python libraries in AWS SAM. Each Python Lambda will have a `requirements.txt` file in it's folder. AWS SAM will install those libraries in the folder, then zip it up and upload to your Lambda function. Package management is a shit show in Python, so you're welcome to use whatever you want (Conad familiy, `pipenv`, etc). I'm going to use virtual environments.

1. install virtual environment library via `pip install virtualenv`.
2. then `cd` to your lambda folder; for now we're `parse-masses`
3. then `virtualenv parse-masses-env`
4. finally, `source parse-masses-env/bin/activate`
