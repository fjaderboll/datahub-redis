
# Datahub - Web frontend
This project was generated with [Angular CLI](https://github.com/angular/angular-cli) version 16.2.7.

## Development setup
```shell
npm install    # install dependencies

# update stuff
sudo npm uninstall -g @angular/cli
sudo npm install -g @angular/cli@latest
ng version

sudo npm install -g n
sudo n 20.8.1
node -v
```

## Run locally
Make sure `apiUrl` in `environments/environment.ts` points to your setup of the backend.

```shell
npm start      # start server at http://localhost:4200
ng serve
```

## Development cheat sheet
```shell
ng generate component components/InlineEdit    # create new component
ng generate component pages/SensorView         # create new page
ng generate component dialogs/CreateUserDialog # create new dialog
ng generate service services/Authentication    # create new service
ng add @angular/material                       # add Angular Material
ng build                                       # build for production
```

You can also use `ng generate directive|pipe|service|class|guard|interface|enum|module`.

* Material Components: https://material.angular.io/components/
* Icon library: https://fonts.google.com/icons?selected=Material+Icons
* Animated SVGs: https://www.svgbackgrounds.com/elements/animated-svg-preloaders/
