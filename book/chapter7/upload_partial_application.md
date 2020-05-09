# Upload Partial Application

Before we start reading from our download, we need a pure way to upload a part of the file. If it's pure, and we're using a Lambda with enough juice + bandwidth, we could spawn many of these at the same time. Since they're pure, they wouldn't have any globals, and could safely run together. We're not going to be doing that now for simplicity, but this focus on purity allows you to get that safer concurrency so it's a good habit to start.

The `s3.uploadPart` takes a few parameters:

```javascript
 s3.uploadPart({
    Bucket,
    Key,
    PartNumber,
    UploadId,
    Body
})
```

Our bucket we already know; we get that from our `event`. The key as well, it's the filename of the asteroids csv. The `UploadId`, that's what we'll get from `createMultipartUpload`.

The `PartNumber` has 3 important rules:
1. Starts with `1`
2. Every piece of the file you upload must have a different number.
3. You have 1 to 10,000.

There's no state in functional programming, so we have a few options here to increment the number (recursion, etc). The only issue we'll fix later is you do not get the `PartNumber` back in the response. Most requests in JavaScript are done in stateful Promises, so typically you can just read from the closure, and this is what we'll do so those downstream can use that `PartNumber`.

Finally the `Body` is the piece of our file. The rules here are complicated:

1. It has to be minimum 5 megs
2. If it's less than 5 megs, it has to be the last part you upload.

It's ok if you upload the parts out of order, but we'll be doing it in order for now.

## Binary vs Objects

Most streams in Node.js default to binary, called `Buffer` in Node.js. It's a class that allows you to play with raw bytes. The type of pipeline we're building is mostly around `Objects` (like Python's `Dictionray`) so we'll be doing that mode instead. You tell a `Stream` what its input type and output is. A lot of our methods, too, will take in bytes, but return Objects.

Our `uploadPart` function is no different. Let's expound on the above function to see what her function signature should look like:

```javascript
const uploadPart = s3 => bucket => key => uploadID => counter => chunks => isLastPart
    s3.uploadPart({
        Bucket: bucket,
        Key: key,
        PartNumber: counter,
        UploadId: uploadID,
        Body: chunks.slice(0, chunks.length)
    })
    .promise()
```

This is a good start. Our `s3` is brought in the through the arguments to make her more pure and testable (easy to stub vs. mig-i-dy mocks). The `bucket` and `key` we know. The `uploadID` is so we know what multipart upload to associate it with. The `counter` is our `PartNumber` that we've conveniently made incrementing it someone else's problem (Functional Programming is good at that). The `Body`, notice we're using `slice` on the entire Buffer. That's the quick way to get a clone of the bytes and be as immutable as possible. Given our rules that special things happen on the last part, we need a way to know about it, so the last parameter is `isLastPart`.

However, others downstream will need to know about that `PartNumber` as well, so we'll enhance the result that comes out of S3. We _could_ do that this way:

```javascript
.then(
    s3Result => {
        const newResult = s3Result
        newResult.PartNumber = counter
        return newResult
    }
)
```

However, that has mutation, and while it looks like it's making a copy, it's just a reference. No harm, but a bad habit in FP. On that note, we could use destructuring:

```javascript
.then(
    s3Result => {
        return {
            ...s3Result,
            PartNumber: counter
        }
    }
)
```

But all functions in FP return values, so using the `return` keyword is redundant.

```javascript
.then(
    s3Result =>
        ({
            ...s3Result,
            PartNumber: counter
        })
)
```

And while that's fine, there is a more terse way using the `set` function from Lodash. It's one of the many Lens style functions it has.

```javascript
const { set } = require('lodash/fp')
...
.then(
    s3Result =>
        set('PartNumber', counter, s3Result)
)
```

But all `lodash/fp` libraries are curried by default, so we can partially apply it instead:

```javascript
.then(
    set('PartNumber', counter)
)
```

WHile this is ok, we're still missing the `isLastPart`. Let's add 1 more pipe to this function to move some data around:

```javascript
.then(
    result =>
        ({
            part: result,
            isLastPart: isLastPart
        })
)
```

Those are the only 2 properties we care about for those downstream: A file part, and if it's the last one. We can shorten it further since the property name `isLastPart` has the same name as the value:

```javascript
.then(
    result =>
        ({
            part: result,
            isLastPart
        })
)
```

That gives us:

```javascript
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
```

## Dependency Injection and Partial Application

We need to call `uploadPart` many times, but the only things that'll change between each time we call it is the `counter`, `chunks`, and `isLastPart`. The `s3` instance we only create once for use throughout our app, forever. The `bucket` name is also the same throughout the entire app's lifetime. The `key`, same. The `uploadID` is HOPEFULLY the same, else we have larger issues. That's why we put those 3 parameters at the end; the first 4 can be added or "partially applied". Let's implement and show you in our `handler`:

```javascript
...
.then(
    uploadID => {
        const uploadPartPartial = uploadPart(s3)(bucket)(latestAsteroids.filename)(uploadID)
    }
)
```

That `uploadPartPartial` takes 3 parameters: `counter`, `chunks`, and `isLastPart`. We'll know those once we start processing the bytes in our pipeline. The other 4 never change. She may be half-cocked, but she's fully ready to rock. Let's start downloading our file:

```javascript
.then(
    uploadID => {
        const uploadPartPartial = uploadPart(s3)(bucket)(latestAsteroids.filename)(uploadID)
        return downloadLatestAsteroids()
        .then(

        )
    }
)
```


