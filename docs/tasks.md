# Tasks

[Tasks](https://discordpy.readthedocs.io/en/stable/ext/tasks/index.html) in discord.py are helpers
for [asyncio.Task](https://docs.python.org/3/library/asyncio-task.html#task-object)

They are used for having a loop run in the background at a specified interval/time.

## Creating a task

To create a task you need to make an `async` function that you want to run in the task and apply `tasks.loop` decorator on it.

You can read about its parameters in [discord.py documentation](https://discordpy.readthedocs.io/en/stable/ext/tasks/index.html#discord.ext.tasks.loop)

```python
from discord.ext import tasks


@tasks.loop(seconds=10)
async def my_task():
    print("Hello!")
```

Then you can start it by using it's `start` method. For example in `setup_hook`:

```python
@bot.event
async def setup_hook():
    my_task.start()
```

## Utility Decorators

### before_loop

A decorator that registers a coroutine to be called before the loop starts running.

```python
from discord.ext import tasks


@tasks.loop(seconds=10)
async def my_task():
    print("Hello!")


@my_task.before_loop
async def before_my_task():
    print("preparing!")
```

### after_loop

A decorator that registers a coroutine to be called after the loop finishes running.

```python
from discord.ext import tasks


@tasks.loop(seconds=10)
async def my_task():
    print("Hello!")


@my_task.after_loop
async def after_my_task():
    print("finished!")
```

### error

A decorator that registers a coroutine to be called if the task encounters an unhandled exception.

The coroutine must take only one argument the exception raised

```python
from discord.ext import tasks


@tasks.loop(seconds=10)
async def my_task():
    print(1 / 0)


@my_task.error
async def error_handler(error: Exception):
    print(error)
```

## Cancelling and Restarting

### cancel

Cancels the internal task, if it is running.

```python
my_task.cancel()
```

### stop

Gracefully stops the task from running.

Unlike [cancel](#cancel), this allows the task to finish its current iteration before gracefully exiting.

```python
my_task.stop()
```

### restart

A convenience method to restart the internal task.

```python
my_task.restart()
```

## Reconnect Exceptions Handling

### add_exception_type

Adds exception types to be handled during the reconnect logic.

By default the exception types handled are those handled by `Client.connect()`, which includes a lot of internet disconnection errors.

```python
my_task.add_exception_type(SomeCustomError, AnotherCustomError)
```

### clear_exception_types

Removes all exception types that are handled.

```python
my_task.clear_exception_types()
```

### remove_exception_type

Removes exception types from being handled during the reconnect logic.

```python
my_task.remove_exception_type(SomeCustomError, AnotherCustomError)
```

## Changing Interval

### change_interval

Changes the interval for the sleep time.

```python
from discord.ext import tasks


@tasks.loop(seconds=10)
async def my_task():
    print(1 / 0)


my_task.change_interval(seconds=15)
```

## Examples

Check out [discord.py tasks recipes](https://discordpy.readthedocs.io/en/stable/ext/tasks/index.html#recipes). There you can find a lot of examples