import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { App } from './app/app';
import { authInterceptor } from './app/core/interceptors/auth-interceptor';
import { provideRouter } from '@angular/router';
import { routes } from './app/app.routes';
import { provideHttpClient, withInterceptors } from '@angular/common/http';


bootstrapApplication(App, {
providers:[
  provideRouter(routes),
  provideHttpClient(
    withInterceptors([authInterceptor])
  )
]
})
