# datahub (Redis version)

**NOTE** In early development!

## Background
A re-design of [datahub](https://github.com/fjaderboll/datahub) with a Redis
backend instead of SQLite. This fills two purposes; greatly improved speed and
less wear on your disk.

## File structure
This project consists of two parts:
* [app](app/README.md) - The application backend
* [web](web/README.md) - The web frontend
