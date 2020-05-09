const { set } = require('lodash/fp')

const createMultipartUpload = s3 => bucket => filename =>
    s3.createMultipartUpload({
        Bucket: bucket,
        Key: latestAsteroids.filename
    })
    .promise()
    .then(
        result =>
            result.UploadId
    )

const uploadPart = s3 => bucket => key => uploadID => counter => chunks => isLastPart =>
    s3.uploadPart({
        Bucket: bucket,
        Key: key,
        PartNumber: counter,
        UploadId: uploadID,
        Body: chunks.slice(0, chunks.length)
    })
    .promise()
    .then(
        set('PartNumber', counter)
    )
    .then(
        result =>
            ({
                part: result,
                isLastPart
            })
    )

const handler = async (event) => {
    const { bucket, latestAsteroids } = event
    const s3 = new AWS.S3()
    createMultipartUpload(s3)(bucket)(latestAsteroids.filename)
    .then(
        uploadID =>
            ...
    )
    .catch(
        error =>
            log("error:", error)
            || Promise.reject(error)
    )
}

exports.handler = handler

if(require.main === module) {
    handler(
        {
            bucketName: 'asteroid-files', 
            latestAsteroids: { filename: 'lastest-asteroids.csv' }  
        }
    )
    .then(log)
    .catch(log)
}