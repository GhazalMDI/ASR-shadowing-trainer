import { Component, OnInit } from '@angular/core';
import { DashboardService } from '../dashboard-service';
import { CommonModule } from '@angular/common';
import { last, Observable } from 'rxjs';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css',
})
export class Dashboard implements OnInit {

  performanceState: 'idle' | 'loading' | 'loaded' | 'error' = 'idle';

  activeTab: 'user' | 'performance' = 'user';
  user$!: Observable<any>;
  performances: any[] = []
  performanceLoaded = false
  loadingPerformance = false

  constructor(private dahshboardService: DashboardService) { }
  ngOnInit(): void {
    this.user$ = this.dahshboardService.getUserInfo();

  }

  loadPerformance() {
    this.activeTab = 'performance';
    if (this.performanceState === 'loaded') return;
    this.performanceState = 'loading';
    this.dahshboardService.getPerformance().subscribe({
      next: (response: any) => {
       
        this.performances = response.performances;
        this.performanceState = 'loaded';
      },
      error: () => {
        this.performanceState = 'error';
      }
    });
  }
}
