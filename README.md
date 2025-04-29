# Dice Roller Telegram Bot

A simple dice roller Telegram bot. Currently works with two systems:
1. Basic _d6_, _d10_, _d20_, etc. dice rolls.
2. VtM d10 rolls. 1 on throw subtracts one success, 10 on throw adds two successes. _By default,
throw difficulty is 6_, but it can be set in the command argument.

## Commands
- `/roll` or `/r`. Makes a simple dice roll and gives a plain result. For the basic system, it's
the sum of all dices throws. For the VtM system, it's amount of successes.
- `/full` of `/f`. Makes a dice roll, gives a result, and prints a list of all throws.

### Command arguments
- For the basic system throw, it takes one `<number>d<number>` argument. For instance, `1d20`, `6d8`, `5d10`, etc.
- For the VtM throw, it takes one `<number>v[number]` argument. For instance, `1v8`, `5v`, `3v7`, etc.

### Usage examples
Input: `/r 6d6`  
Output: `6d6: 20`

Input: `/roll 7v`  
Output: `7v: 4 successes`

Input: `/f 6v`  
Output: `6v: 3 successes [5,10,7,3,5,4]`

Input: `/full 8v8`  
Output: `8v8: Botch! [9,1,3,2,2,7,1,6]`

## How to deploy
### Telegram bot creation

1. Address to the `@BotFather` in Telegram.
2. Start a creation of a new bot via `/new` command.
3. Type the bot name, the bot id and keep the token provided.

### Prerequisites

1. Copy this repository contents to your host.
2. Create `.env` file in the root directory of this project. Example is given here: [.env_example](.env_example).
3. Replace `TELEGRAM_TOKEN` field with token previously obtained from the `@BotFather`. No quote marks required.

There are two options to run this bot in your system: **Docker** container and **local runtime**.

#### Docker installation

1. Install [Docker Desktop](https://docs.docker.com/desktop/).
2. Run Docker Desktop. From Terminal (or Windows Powershell) build an image:
`docker build . -t <your image name>`.

For instance, `docker build . -t dice_bot`.

3. Run Docker container:
`docker run --env-file .env -d <your image name>`.

For instance, `docker run --env-file .env -d dice_bot`.

#### Local host installation

1. Install Python to your system. Python 3.12 or higher is required. [Releases page](https://www.python.org/downloads/). Add Python to your `PATH`, like specified during the installation.
2. Install Poetry package to your system. Run from the Terminal/Powershell: `pip install poetry`.
3. Install required Python packages with Poetry running the Terminal/Powershell in the project folder: `cd <your project folder> && poetry install`.
4. Run the bot with Poetry in the Terminal/Powershell: `poetry run python main.py`.
5. To stop the bot, press Ctrl-C in the Terminal/Powershell. To start it again, run `poetry run python main.py`.
