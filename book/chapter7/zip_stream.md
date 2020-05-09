# ZIP Stream

One nice thing about CSV data is that it has a lot of common patterns, making it zip pretty well. This helps shrink how much data we actually need to upload and download from S3. Let's take our download file Stream and zip it.

We'll import the zlib library built into Node.js:

```javascript
const { createGzip } = require('zlib')
const gzip = createGzip()
```

Instead of zipping the entire file, you feed it bytes, and it zips the bytes; it's meant to work wtihin streams.

## Pipelines

... before we get to that, though, just know Streams are insanely complicated. If you're an imperative developer, you'll be like "this is fine, looks like the beauty that is Unix". If you're an OOP head, you'll scoff and be like "Dude, you can just abstract all that nonsense to a wonderful class with 2 methods". If you're an FP'er, you'll long for F#'s way of handling streams.

Suffice to say, all the state and error handling is a lot of congnitive load so Node.js provides `pipeline` function. If you're from an FP or RxJS background, you may recognize that as like a `flow` or `compose` function, and you're right. It simplifies error handling and connections:

1. Put a bunch of streams in order.
2. We'll tell you if it worked or not.

Let's put our zip as the first step in the pipeline. We'll import `stream` first because we'll need her more later.

```javascript
const stream = require('stream')
const { pipeline } = stream
```

Then create our gigantor pipeline function:

```javascript
const zipCSVAndUploadToS3 = csvStream =>
    new Promise(
        (success, failure) =>
            pipeline(
                csvStream,
                error =>
                    error
                    ? failure(error)
                    : success(true)
            )
    )
```

There is the `promisify` function in Node to convert callbacks, but I always found its syntax + the examples verbose, and felt it was easier to just use a ternary if for the callback function. The above just has 1 item in the pipeline, the `csvStrea`. That's the HTTP Read stream we'll get when we initiate our file download. Although it may not have all the data from JPL's website yet, you can immediately handle reading off of it, and Node.js will handle all the data loading, back pressure, and various race conditions that could arise, all while keeping your memory usage extremly low regardless of file size.

Let's add the zipping to it:

```javascript
...
 pipeline(
    csvStream,
    gzip,
    error =>
    ...
```

Nice, now as we download the file, we'll zip it piece by piece. Let's implement our pipeline in our existing `handler`:

```javascript
...
return downloadLatestAsteroids()
    .then(
        zipCSVAndUploadToS3
    )
```