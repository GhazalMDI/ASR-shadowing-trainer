import { Component } from '@angular/core';
import { AuthService } from '../../authSevice';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';

@Component({
  selector: 'app-login',
  imports: [CommonModule,FormsModule,RouterModule],
  templateUrl: './login.html',
  styleUrl: './login.css',
})
export class Login {
  email = ''
  password = ''
  constructor(private authService: AuthService, private router: Router, private http: HttpClient) { }
  login() {
    this.authService.login(this.email, this.password).subscribe(
      (response) => {
        console.log(response)
        this.authService.setToken(response.access_token,response.refresh_token);
        console.log("your login!")
        this.router.navigate([''])
      },
      (error)=>{
        console.log(error)
      }

    )
  }



}

