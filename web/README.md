# Datahub - Web frontend
An [Angular](https://angular.dev/) 22 application using [Angular Material](https://material.angular.dev/)
and [Highcharts](https://www.highcharts.com/).

## Development setup
Requires Node.js 22.22 or newer (or 24.15 or newer), the Docker image builds with Node.js 22.

```shell
sudo npm install -g n
sudo n 24      # install Node.js 24 LTS
node -v

npm install    # install dependencies
```

The Angular CLI is installed as a dependency, use it with `npx ng` (or `npm run ng --`).

## Run locally
Make sure `apiUrl` in `src/environments/environment.ts` points to your setup of the backend.

```shell
npm start      # start server at http://localhost:4200
```

## Build and test
```shell
npm run build  # production build to dist/web, served by the backend
npm test       # unit tests with Vitest
```

## Upgrading
```shell
npx ng update                                              # list available updates
npx ng update @angular/core @angular/cli @angular/material # update Angular, runs migrations
npm outdated                                               # other dependencies
npm audit
```

`package.json` overrides the version of `vite` (only used by the development server) to get
security fixes before `@angular/build` updates it, remove the override when it does.

## Development cheat sheet
```shell
npx ng generate component components/InlineEdit    # create new component
npx ng generate component pages/SensorView         # create new page (and add it to app.routes.ts)
npx ng generate component dialogs/CreateUserDialog # create new dialog
npx ng generate service services/Authentication    # create new service
```

You can also use `ng generate directive|pipe|service|class|guard|interface|enum`.

### Layout
* Pages are loaded on demand, see `src/app/app.routes.ts`.
* All REST calls are in `ServerService`. Use the `` api`...` `` helper for URLs, it encodes names taken from the page URL.
* Narrow screens: tables go in a `.table-container` (scrolls sideways), button rows in `.actions` (wraps).
  The header switches to a menu below 840 pixels.

### Links
* Material Components: https://material.angular.dev/components/
* Icon library: https://fonts.google.com/icons?selected=Material+Icons (self hosted via `@fontsource/material-icons`)
* Animated SVGs: https://www.svgbackgrounds.com/elements/animated-svg-preloaders/
