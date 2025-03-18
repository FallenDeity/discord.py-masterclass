# Tasks

One of the most common things you will often find yourself needing is some sort of background task. This could be anything from updating a counter every minute to updating some leaderboard every hour or posting daily reminders.
To handle these tasks, discord.py provides a `tasks` extension that makes it easy to create and manage background tasks.

The `tasks` extension is a wrapper around the [`asyncio.Task`](https://docs.python.org/3/library/asyncio-task.html#task-object) class that allows you to run a coroutine in the background at a specified interval, with a lot of additional features like error handling, reconnect logic, exponential backoff, and more.

## Creating a task

To create a task you need to make an `async` function that you want to run in the task and apply `tasks.loop` decorator on it.

It takes the following arguments:

- `seconds`: The number of seconds between each iteration.
- `minutes`: The number of minutes between each iteration.
- `hours`: The number of hours between each iteration.
- `time`: A `datetime.time` or a list of `datetime.time` objects representing the time(s) of day to run the task.
- `count`: The number of times to run the task. If `None`, the task will run indefinitely.
- `reconnect`: Whether to handle errors and restart the task using an exponential backoff strategy. Defaults to `True`. For more information see [here](https://github.com/Rapptz/discord.py/blob/ff638d393d0f5a83639ccc087bec9bf588b59a22/discord/backoff.py#L41-L108).
- `name`: The name of the task. If `None`, the function name will be used.

Then you can start it by using it's `start` method. This will schedule the task to run in the background.

=== "Using a Cog"
    ```python
    from discord.ext import commands, tasks

    class MyCog(commands.Cog):
        def __init__(self, bot):
            self.bot = bot

        # you can start the task when the cog is loaded
        async def cog_load(self):
            self.my_task.start()

        # you can stop the task when the cog is unloaded
        async def cog_unload(self):
            self.my_task.stop()

        @tasks.loop(seconds=10)
        async def my_task(self):
            print("Hello!")

    async def setup(bot):
        bot.add_cog(MyCog(bot))
    ```
=== "Standalone"
    ```python
    from discord.ext import tasks

    @tasks.loop(seconds=10)
    async def my_task():
        print("Hello!")

    class MyBot(commands.Bot):
        async def setup_hook(self):  # setup_hook is called before the bot starts
            my_task.start()

    bot = MyBot(command_prefix="!", intents=intents)

    @my_task.before_loop
    async def before_my_task():
        await bot.wait_until_ready()  # wait until the bot is ready
    ```
    !!! note "Note"
        The only requirement to schedule a task is to call the `start` method which you can call at an appropriate place in your code. A thing to note is that the task may start running before the bot is ready, so you may want to use `before_loop` to wait until the bot is ready if you are fetching any data from the discord API.

## Utility Decorators

---

### @before_loop

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

### @after_loop

A decorator that registers a coroutine to be called after the loop finishes running. You can use this to perform cleanup tasks.

```python
from discord.ext import tasks


@tasks.loop(seconds=10)
async def my_task():
    print("Hello!")


@my_task.after_loop
async def after_my_task():
    print("finished!")
```

### @error

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
This method is useful if you want to handle custom exceptions that are either raise by you or some third-party libraries.

```python
class SomeCustomError(Exception):
    pass

@tasks.loop(seconds=10)
async def my_task():
    connection = await some_third_party_library.connect()
    print(connection)
    if not connection:
        raise SomeCustomError("Connection failed!")
    # do something with connection
    connection.close()

my_task.add_exception_type(SomeCustomError) # now SomeCustomError will be handled during the reconnect logic
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

Check out [discord.py tasks recipes](https://discordpy.readthedocs.io/en/stable/ext/tasks/index.html#recipes) for some examples on how to use tasks in your bot.
