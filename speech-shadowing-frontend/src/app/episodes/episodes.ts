import { ChangeDetectionStrategy, ChangeDetectorRef, Component, OnInit } from '@angular/core';
import { EpisodeService } from '../episode-service';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

@Component({
  selector: 'app-episodes',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './episodes.html',
  styleUrl: './episodes.css',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class Episodes implements OnInit {

  episodes: any[] = [];

  constructor(
    private episodeService: EpisodeService,
    private cdr: ChangeDetectorRef,
    private router:Router
  ) { }

  ngOnInit(): void {
    this.episodeService.getEpisodeList().subscribe({
      next: (response: any) => {
        console.log(response)
        this.episodes = response.episodes.map((ep: any) => ({
          ...ep,
          created_at: new Date(ep.created_at)
        }));
        
        this.cdr.markForCheck();
      },
      error: (err) => console.error(err)
    });
  }


  goToEpisode(episode_id:number) {
    this.router.navigate(['/episodes',episode_id])

  }
}


