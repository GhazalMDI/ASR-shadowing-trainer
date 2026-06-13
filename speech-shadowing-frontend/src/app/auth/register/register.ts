import { Component } from '@angular/core';
import { AuthService } from '../../authSevice';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-register',
  imports: [CommonModule,FormsModule],
  templateUrl: './register.html',
  styleUrl: './register.css',
})
export class Register {
 first_name = ''
  last_name = ''
  email = ''
  password = ''

  constructor(private authService: AuthService, private router: Router, private http: HttpClient) { }

  register() {
    this.authService.register(this.first_name, this.last_name, this.email, this.password).subscribe(
      (response) => {
        this.authService.setToken(response.tokens.access_token,response.tokens.refresh_token);
        console.log("account is created!")
        this.router.navigate(['']);
      },
      (error)=>{
        console.log(error)
      }

    )
  }
}
