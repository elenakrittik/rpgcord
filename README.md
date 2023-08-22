# RPGcord

To work on this Greatest Piece of Dogshit:tm: you'll need:

- [Git](https://git-scm.com/downloads)
- [Python](https://www.python.org/downloads)
- [Node.js](https://nodejs.org/en/download/current)

After installing all of that, [install pipx](https://pypa.github.io/pipx/installation/) and then run the following
commands inside
- `bash`/`fish`/etc. if you're on Linux or MacOS
- PowerShell 5+ if you're on Windows 10+

```sh
pipx install pdm
git clone https://github.com/elenakrittik/rpgcord.git
cd rpgcord
pdm run setup_env
```

To actually run the bot, you'll need a local MySQL instance set up and running.
[Install MariaDB](https://mariadb.org/download/?t=mariadb&p=mariadb&r=11.0.3),
a "better" version of MySQL, and choose root username as 'root' and set your
root password to whatever you wish. Then, run `mysql -u root -p`, enter password
when prompted and execute the following to setup database access for RPGcord:

```sql
CREATE USER 'rpgcord'@'localhost' IDENTIFIED BY 'mypassword';
CREATE DATABASE rpgcord;
GRANT ALL ON rpgcord.* TO 'rpgcord'@'locahost';
```

If you get an error similar to this:

```
ERROR 2002 (HY000): Can't connect to server on 'localhost' (10061)
```

That means that MySQL server is not currently running. We recommend setting up
MySQL to start/shutdown when your system starts/shutdowns. Select option
approritate for your system [here](https://dev.mysql.com/doc/refman/8.0/en/automatic-start.html), then restart your computer and repeat the above.

After you've setup the database, you need to copy `rpgcord/config.example.py` to `rpgcord/config.py` and edit database password and bot token. Then you should be able to start the bot using `pdm run rpgcord`.

## Working in Visual Studio Code

VS Code is recommended as your primary editor while working on this
project. When you first open this folder, VS Code will suggest a few
extensions to be installed. **DO NOT IGNORE THEM**. Installing all of
these will significantly improve your experience and will move most
warnings from CLI to the editor.

## Useful commands

`pdm run format` - format the code.
`pdm run lint` - lint the code.
`pdm run pyright` - type-check the code.
`pdm run docs` - run documentation server with live-reload.
`pdm run rpgcord` - run bot.
