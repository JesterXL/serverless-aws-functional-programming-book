
## What's a Result?

Before we do, let's get our nomenclature right.

This pattern Golang uses and we're using in Python is also used in Lua. It's so common to have these focused functions that mathematicians created an Algebriac Data Type for it called `Result`. Basically "the result of the function". Results typically are either "Ok" or "Error". If you need more then 2 return values, there are types for that too. For our example, though, we're pretty clear:
- either you can open a file, or you can't
- either you can read lines from it, or you can't
- either that data is good enough to parse, or it isn't
- either you can convert that data to JSON, or you can't
- either it successfully uploads to S3, or it doesn't

... now Functional Programmers are going to correct me and point out the original ADT is actually called "Either", just like our bullet points illustrate. However, while `Either` is an ok name, it usese "Left" or "Right". Those are the worst possible terms to give a programmer in the trenches writing code. They use both hands if they're able, so those terms don't mean anything programmer specific. Names can mean literly anything in code. They have mathematical definitions, sure, but sadly their names make them confusing.

Therefore, we're not going to use it. Instead, we'll use `Result` and a result is either `Ok`: the function workd, or it's an `Error`. We'll often refer to a Result as a "type". Even though Python isn't a typed language, it still supports and enforces basic types at runtime so think of it like that kind of a type. You can return Strings, Numbers, Dictionaries, Tuples, and Results from functions; make sense?

## Creating Results

Many types have special ways of creating them. For `Dictionaries`, you use squiggly / flower brackets:

```python
person = { 'firstName': 'Jesse' }
```

For `Lists`, you'll use square brackets:

```python
family = ['Her Majesty', 'Albus', 'Sydney', 'Rowan']
``` 

For a JSON string, you'll use the `dumps` function:

```python
json_string = dumps(person)
```

For a `Result`, you'll use the `Ok` function:

```python
person_result = Ok(person)
```

or a `Error` function:

```python
function_error = Error('b00m b00m, shake the r00m')
```

Don't confuse `Error` with an Exception; they're not the same thing.

## Comparing to Golang

Using our Go return value, this indicats a function worked:

```python
json_str, error = parse(stuff)
print(json_str, error)
# '{"firstName": "Jesse"}`, None
```

And this indicates it failed

```python
json_str, error = parse(stuff)
print(json_str, error)
# None, failed
```

Note:

1. they look the exact same
2. you have to check one before you check the other
3. you define both despite only using 1 in one path and 1 in the other

Ok, let's compare to a successful Result:

```python
result = parse(stuff)
print(result)
# Ok: {"firstName": "Jesse"}
```

And a failed one:

```python
result = parse(stuff)
print(result)
# Error: b00m
```

Nothing huge here at first beyond 1 value instead of 2, you only have to check 1 value, and only need 1 variable.

## Pipeline

The _real_ key is that you can bind them together. Changing this Golang version:

```python
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
```

To this Result version:

```python
result = open_masses()
>> read_mass_lines \
>> mass_lines_to_dictionary \
>> massd_to_json \
>> upload \
```

Rad, eh!? The `>>` operator is a function called `bind` that "binds things together". If you re-read the Golang version, each function takes 1 input and produces 1 output. The `\` is because Python, like Bash, doesn't really like things on multiple lines by default, so you have to be explicit about what is part of the same set of code. Those `\` say, "Yo, this is the same code, I'm just continuing it on a new line so I have room, ok?". The "room" is the dead giveaway as most Python likes to be single line statements, but we'll live.

However, each time we call that function, we have to:

1. verify it's not an error
2. if it is, stop control flow and return the error (or make a new one if need be)
3. otherwise use that new variable we created and manually call the next function with it
4. ... while making room for 2 new variables, re-using the `error` variable

Using `bind`, all that is handled for you. No need for error verification, stopping if error, manually calling functions with previous result, nor creating many variables.

## Getting Values Out

Eventually, you'll want to get values OUT of the Result. The magic box is cool, but like... if we need the raw values for some other function call that doesn't take a Result, or perhaps outside our Lambda function in JSON, we'll need that raw value. This includes debugging for ourselves.

There are variety of ways, I'll cover the 2 most common.

### Dot Value

The quickest, and most anti-FP, is dot value:

```python
print(Ok('{"firstName": "Jesse"}').value)
# {"firstName": "Jesse"}
```

If you're learning FP, dude, seriously, it's completely fine to do that. I encourage you to practice the `getOrElse` and then `match`.

### get_or_else

Sounds threatening, but read it like this: "If it's an `Ok`, get the value, otherwise if it's an `Error`, I'll give you a default instead.

```python
value_or_error = Ok('{"firstName": "Jesse"}').get_or_else('it broke')
print(value_or_error)
# {"firstName": "Jesse"}
```

For an `Erorr`, however, it'll just give you the default you pass instead of whatever is inside the `Error`:

```python
value_or_error = Error('b00m').get_or_else('it broke')
print(value_or_error)
# it broke
```

Normally, `Error`'s house `Exceptions`, but if you want to put just Strings in there, that's fine too; Python is dynamic, do whatever you want. However, for people using `Results`, they sometimes don't entirely crash without a value as they can provide defaults. This `get_or_else` gives you that option to just provide defaults for code that can keep going.

### Match

The `match` method uses functions. They do **NOT** have to be Python `lambda`'s, I just put 'em here for brevity:

Here's an `Ok`:

```python
value_or_error = Ok('{"firstName": "Jesse"}').match({
    Ok: lambda value: value,
    Error: lambda error: error,
})
print(value_or_error)
# {"firstName": "Jesse"}
```

Here's an `Error`:
```python
value_or_error = Error('b00m').match({
    Ok: lambda value: value,
    Error: lambda error: error,
})
print(value_or_error)
# b00m
```

You'll use `match` when you want to react or transform the data without using `map` at the very end of a long pipeline.

## Conclusion

Using Result gives you a single value, you can return them from functions, they can be chained together, and they significantly reduce the amount of code you have to write. Let's now convert our Golang style Lambda to a Result oriented one.