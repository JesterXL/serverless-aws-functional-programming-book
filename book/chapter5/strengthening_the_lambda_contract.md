# Strengthening the Lambda Contract

Like all things, we'll do our best.

What _is_ the best thing to do here, then? We can learn a lot from [Golang](https://golang.org/). It recognized that errors are just a way of life in programming. It also recognized that they can cause indirection, and exponentially increase how many possible paths your code can take. They also found Exceptions bubble on purpose, but by doing this it leaves the area of the code where the error happened, forcing you to find your way back. Sometimes this isn't as straightforward as following the stack trace. Often you want the error next to the piece of code that failed, called co-locating, since it's aware of its surroundings, and easier to reference nearby things.

```python
def get_with_this_or_that(this):
    if this == True:
        return "This"
    else:
        return "That"
```

In the above function, only 2 paths, and thus 2 things for you to keep in your head.

```python
def tick_tick(boom):
    if this == True:
        return "This"
    else if this == False:
        return "That"
    else:
        raise Exception("Boom")
```

In the above function, only 3 paths. However, once you start using this function with other functions, _they_ now have to worry about the exception. Python and other dynamic languages do not have any way of helping you know something deeply buried has an error, so you do one of the following:
- ignore it, focusing instead on the happy path
- ignore it, then fix it when it raises by wrapping with a try/except
- put try/excepts in places you're worried about

The first is brittle code. The second is how I see 90% of coders in non-FP, non-Go like languages, code. The third comes from a beneveloent place, but isn't thorough enough, nor very strategic in how to approach it. Worse, they're fighting a losing battle as more functions throw, many from libraries or from core Python, the amount of failure paths exponentially grows.

To simplify error handling like the above, they built into the language:

> Did the function work?
> No? Return the error and no data.
> Yes? Return the data and no error.

This means there are no `try` or `except` or `try` or `catch` in Go (ignore defer/panic for now).

A function either works, or it doesn't.

Most Go code looks like this:

```go
f, err := os.Open("filename.ext")
if err != nil {
    log.Fatal("Failed to open the filename.ext.")
    log.Fatal(err)
    return nil, err
}
// do stuff with the file
```

... repeated over and over. It's very imperative. Very easy to follow, very clear where failures occur and what probably caused them.

If another function CAN possibly recover from an error, it can. Except, instead of a separate place like an except/catch block, it's literally in the calling function, like normal code.

## Wait, why are we doing this?

The cool thing about having functions that only do 2 things means you can basically say "Either you worked or you didn't."

We're going to change that language in the Step Function based on her specific powers: Can we retry or are we screwed?

Most code failures can be boiled down to two paths:
1. It failed, and will fail if you try again unless you fix something.
2. It failed, but _may_ succeed if you try again.

Functional Programmers talk about "determinism" and "pure functions always working no matter how many times they're called". What they don't harp on too much, but which is equally important is deterministic failure. Meaning, if you write a function that fails, then it should always fail.

When you're dealing with side effects, in our case, loading data from 3rd party websites, you can never really guarentee what'll happen.

So, you ensure your function only has 2 responses, but _hints_ to those upstream on what type of error you're dealing with. We'll get more into that part later once we flesh out our Lambda more. Fow now, the tl;dr; is ensuring your code is extremely predictable: either it works, or it doesn't. If it doesn't, you know where exactly the error is, and no further code is run. This gives you massive confidence no matter how large your code base grows, and how many functions you need. Once you combine them, whether 2 or 2,000: they either all work, or all fail, there is NO in between.

Good feeling, ya?

## Golang Error Handling in Python

Python, Lua, and Golang have a cool feature in common: they can return multiple values. Now, Lua and Golang have it as an _actual_ feature, whereas with Python, you have to return a `Tuple` (read-only list/array) and destructure it. Go uses this feature as a language convention: Return your data and the error at the end. 

```go
f, err := os.Open("filename.ext")
```

That `err` may be `nil` (like Python's `None`). If so, then it's assumed `f` is good and what you want. If `err` is not `nil`, then you ignore `f`, print any helpful additional logs, log the error, and typically return it for functions further up the chain to know something deep inside failed, and they too should stop.

If you've never seen `Tuples` used in Python like that, here's an example:

```python
def sup():
    return ("one", 2, {'three': 'yo'})
```

When you call that function, you can set 3 variables to capature or "destructure" the Tuple; aka unpack the values in order to the 3 variables you define, like so:

```python
one_as_string, two_int, three_dictionary = sup()
```

We'll follow this same style in Python like so:

```python
def read_file(filename):
    try:
        result = open(filename, "r")
        return (result, None)
    except Exception as e:
        return (None, e)
```

Then you write the Go code that looks like this:

```go
f, err := os.Open("filename.ext")
```

To be similiar in Python:

```python
f, err = read_file("filename.ext")
```

Cool? Just remember, all functions should:
- either work or not
- return if they did with data, or not with error

That's it!