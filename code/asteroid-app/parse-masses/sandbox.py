from string import Template
download_benner_lambda_arn = "arn:aws:lambda:us-east-1:089724945947:function:asteroid-app-DownloadBennerFunction-RRB3UVYDWLQ7"
t = Template("""{
    "Comment": "Loads asteroid data from various NASA sources, parses, and puts into a database.",
    "StartAt": "Download Benner",
    "States": {
    "Download Benner": {
        "Type": "Task",
        "Resource": "$arn",
        "End": true
    }
}""")
definition = t.substitute(arn=download_benner_lambda_arn)
print(definition)