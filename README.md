# datahub (Redis version)

**NOTE** In early development!

## Background
A re-design of my previous project [datahub](https://github.com/fjaderboll/datahub)
with a Redis backend instead of SQLite. This has the benefits of greatly improved speed, parallelism and
less wear on your disk.

## File structure
This project consists of two parts:
* [app](app/README.md) - The application backend
* [web](web/README.md) - The web frontend (optional, but convenient for setup and viewing data)
