from json import dumps
import boto3
from Result import *
from pymonad.Reader import curry

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

@curry
def upload(bucketName, filename, massd_json):
    return Result.try_(
        lambda: boto3.client('s3').put_object(
            Bucket=bucketName, 
            Key=filename, 
            Body=massd_json
        )
    )


def lambda_handler(event, context):
    result = open_masses() \
    >> read_mass_lines \
    >> mass_lines_to_dictionary \
    >> safe_dumps \
    >> upload(event['bucketName'], event['masses']['filename'])
    if isinstance(result.value, Exception):
        raise result.value
    return result.value

if __name__ == "__main__":
    lambda_handler({'bucketName': 'asteroid-files', 'masses': {'filename': 'massd.json'}}, {})