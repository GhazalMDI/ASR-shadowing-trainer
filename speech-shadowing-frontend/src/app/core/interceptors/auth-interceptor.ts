import { HttpInterceptorFn } from '@angular/common/http';

const SKIP_AUTH_REGEX = [
  ' /^.*\/episodes$/',
  ' /^.*\/accounts\/login$/',
  ' /^.*\/accounts\/register$/'
]

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  
  if (SKIP_AUTH_REGEX.some(url=> req.url.includes(url))){
    return next(req)
  }
  
  const token = localStorage.getItem('accessToken');
  console.log('INTERCEPTOR URL:', req.url);
  console.log('TOKEN:', token);

  if (token) {
    req = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });
  }

  return next(req);
};