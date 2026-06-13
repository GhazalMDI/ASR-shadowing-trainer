import { Routes } from '@angular/router';
import { Home } from './home/home';
import { Login } from './auth/login/login';
import { Register } from './auth/register/register';
import { Dashboard } from './dashboard/dashboard';
import { Episodes } from './episodes/episodes';
import { EpisodeDetail  } from './episode-detail/episode-detail';

export const routes: Routes = [
    {path:'',component:Home},
    {path:'login',component:Login},
    {path:'register',component:Register},
    {path:'dashboard',component:Dashboard},
    {path:'episodes',component:Episodes},
    {path:'episodes/:id',component:EpisodeDetail}
];

