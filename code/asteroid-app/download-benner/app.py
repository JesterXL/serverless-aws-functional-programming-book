from urllib.request import urlopen
import re
import csv
from io import StringIO
import boto3

def parse_csv(lines):
    r = re.compile((
            '\s*(?P<rank>\d+)'
            '\s+(?P<percentile>\d+\.\d+)'
            '\s+(?P<name>\(\d+\)(\s+[-\w ]+)?)?'
            '\s+(?P<pdes1>\d+)'
            '\s+(?P<pdes2>[-\w]+)'
            '\s+(?P<deltav>\d+\.\d+)'
            '\s+(?P<h>\d+\.\d+)'
            '\s+(?P<a>\d+\.\d+)'
            '\s+(?P<e>\d+\.\d+)'
            '\s+(?P<i>\d+\.\d+)'))
    fields = ('pdes', 'dv', 'H', 'a', 'e', 'i')
    f = StringIO()

    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()

    c = 0
    for line in lines:
        c+=1
        if c < 4:
            continue

        m = r.match(line.decode("utf-8"))
        if not m:
            continue

        writer.writerow({
            'pdes': ('%s %s' % (m.group('pdes1'), m.group('pdes2'))).strip(),
            'dv': m.group('deltav'),
            'H': m.group('h'),
            'a': m.group('a'),
            'e': m.group('e'),
            'i': m.group('i')
            })
    return f.getvalue().encode('utf-8')

class HTTPFailure(Exception):
    pass

def lambda_handler(event, context):
    try:
        result = urlopen(event['benner']['url'])
    except Exception:
        raise HTTPFailure('Boom')

    data = result.read()
    lines = data.splitlines()
    csv = parse_csv(lines)
    result = boto3.client('s3').put_object(
        Bucket=event['bucketName'], 
        Key=event['benner']['filename'], 
        Body=csv
    )
    return result

if __name__ == "__main__":
    try:
        result = lambda_handler({}, {})
        print("result:", result)
    except HTTPFailure:
        print("HTTP failed.")
    except Exception as e:
        print("unknown error:", e)