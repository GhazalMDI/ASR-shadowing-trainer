import { Component, signal } from '@angular/core';
import { Router, RouterOutlet } from '@angular/router';
import { AuthService } from './authSevice';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  // protected readonly title = signal('speech-shadowing-frontend');
  constructor(private authService: AuthService, private router: Router, private http: HttpClient) { }


  logout() {
    const refreshToken = this.authService.getRefreshToken();
    const accessToken = this.authService.getAccessToken();
    console.log(refreshToken)
    console.log(accessToken)

    if (!refreshToken || !accessToken) {
      this.router.navigate(['/login']);
      return;
    }

    this.authService.logOut(refreshToken).subscribe({
      next: () => {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        this.router.navigate(['/login']);
      },
      error: (err) => {
        console.error('Logout failed', err);
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        this.router.navigate(['/login']);
      }
    });
  }
}
