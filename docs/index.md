# Creating a Discord Bot

## Introduction

This is a tutorial on how to create a Discord bot using the [discord.py](https://discordpy.readthedocs.io/en/latest/) library. This tutorial will cover the basics of creating a bot and how to use the library's commands and events. To follow this tutorial, you will need to have Python 3.11 installed on your computer.

### Installing Pyenv

=== "Windows"
    Open powershell in administrator mode. To do this right-click the windows icon and open the terminal (admin) mode.

    Installing [Chocolatey](https://chocolatey.org), this is a package manager for Windows. We will use this to install Pyenv.

    ```powershell
    Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
    ```

    Installing Pyenv.

    ```powershell
    choco install pyenv-win
    ```

    Adding Pyenv to PATH.

    ```powershell
    [System.Environment]::SetEnvironmentVariable('PYENV',$env:USERPROFILE + "\.pyenv\pyenv-win\","User")

    [System.Environment]::SetEnvironmentVariable('PYENV_ROOT',$env:USERPROFILE + "\.pyenv\pyenv-win\","User")

    [System.Environment]::SetEnvironmentVariable('PYENV_HOME',$env:USERPROFILE + "\.pyenv\pyenv-win\","User")

    [System.Environment]::SetEnvironmentVariable('path', $env:USERPROFILE + "\.pyenv\pyenv-win\bin;" + $env:USERPROFILE + "\.pyenv\pyenv-win\shims;" + [System.Environment]::GetEnvironmentVariable('path', "User"),"User")
    ```

    Set execution policy to always be able to run Pyenv.

    ```powershell
    Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Unrestricted
    ```

=== "Linux"
    Open the terminal.

    Install all required prerequisite dependencies.

    ```bash
    sudo apt-get update; sudo apt-get install make build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev wget curl git llvm \
    libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
    ```

    Download and execute installation script.

    ```bash
    curl https://pyenv.run | bash
    ```

    <hr>
    Optional steps but recommended.

    Add the following entries into your `~/.bashrc` file.

    ```sh
    # pyenv
    export PATH="$HOME/.pyenv/bin:$PATH"
    eval "$(pyenv init --path)"
    eval "$(pyenv virtualenv-init -)"
    ```

    Restart shell and test.

    ```bash
    exec $SHELL
    ```

=== "Mac"

    Install Brew (Install apple devtools first if you have never used the terminal, it will prompt you automatically)

    ```zsh
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    ```

    Installing Pyenv.

    ```zsh
    brew install pyenv
    ```


#### Installing Python

To verify that you have Penv installed, you can run the following command in your terminal:

```bash
pyenv --version
```

Install Python and setting it globally.

=== "Windows"

    ```bash
    pyenv install 3.10.5 && pyenv global 3.10.5 && python -V
    ```
=== "Mac & Linux"

    ```bash
    pyenv install 3.11 && pyenv global 3.11 && python -V
    ```

## Creating a Bot

To interact with the Discord API, we need to create a bot. To do this, we need to go to the [Discord Developer Portal](https://discord.com/developers/applications) and create a new application.

![Application](assets/application.png)

## Configuring the Bot

After creating the application, we need to configure the bot and get the bot token. To do this, we need to go to the `Bot` tab.

![Bot](assets/bot.png)

`Username`
:   This is the username of the bot. You can change this to whatever you want.

`Avatar`
:   This is the avatar of the bot. You can change this to whatever you want.

`Token`
:   This is the token of the bot. This is used to control the bot. You should keep this token private and not share it with anyone. Click on the `Copy` button to copy the token to your clipboard.

`Public Bot`
:   This is used to determine if the bot is public or not. If you want to make the bot public, you can enable this option.

## Configuring Intents

After configuring the bot, we need to configure intents. To do this, just scroll down to the `Privileged Gateway Intents` section and enable intents keeping in mind the following:

`Presence Intent`
:   This is used to determine if the bot can see the presence of users. For example, if this is enabled, the bot can see if a user is playing a game, streaming, listening to Spotify and statuses like online, idle, dnd and offline etc.

`Server Members Intent`
:   This is used to determine if the bot can see the members of a server. For example, if this is enabled, the bot can see if a user joins or leaves a server and related server member events.

`Message Content Intent`
:   This is used to determine if the bot can see the content of messages. For example, if this is enabled, the bot can see the content of messages and related message events.

!!! info "Tip"
    If you want to get contents of messages, embeds, attachments and use prefix commands, you will need to enable the `Message Content Intent`. As long as your bot is in less than 100 servers, you can enable all intents without any verification. If your bot is in more than 100 servers, you will need to verify your bot and get intents you need approved.

![Intents](assets/intents.png)

## Adding the Bot to a Server

After configuring intents, we need to add the bot to a server. To do this, we need to go to the `OAuth2` tab. Under the `OAuth2 URL Generator` section, go to select the `bot` scope, if you want slash commands for your bot as well check `applications.commands` scope also. Then, we need to select the permissions that we want the bot to have. After selecting the all the permissions, scroll down and copy the invite URL. You can use this URL to add the bot to a server.

![Permissions](assets/permissions.png)

!!! warning "Warning"
    For this tutorial, we will be using the `Administrator` permission. This is not recommended for production bots. You should only give your bot the permissions that it needs. If its a personal bot, you can give it the `Administrator` permission.

## In-App Authorization

![In-App Authorization](assets/tutorial_bot.png){: style="display: block; margin: 0 auto;"}

In order to add in-app authorization, you need to complete a few extra steps. Travel to `General` section under `OAuth2` tab and select `In-App Authorization` option. After that all steps are the same as above.

![In-App Authorization](assets/in_app_authorization.png)

## Conclusion

With that, we have created a Discord bot. In the next section, we will be creating a bot using the discord.py library. After completing this tutorial, you should have a basic understanding of how to create a Discord bot.
Before we move on to the next section, make sure to have the following ready:

- [x] Python 3.10 or higher installed on your computer.
- [x] A Discord bot created on the [Discord Developer Portal](https://discord.com/developers/applications).
- [x] The bot token copied to your clipboard or saved somewhere safe.
- [x] The bot added to a server.
