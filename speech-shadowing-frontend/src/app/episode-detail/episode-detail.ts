import { ChangeDetectorRef, Component, HostListener, OnDestroy, OnInit } from '@angular/core';
import { EpisodeService } from '../episode-service';
import { ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../authSevice';
import { environment } from '../environments/environment';

@Component({
  selector: 'app-episode-detail',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './episode-detail.html',
  styleUrls: ['./episode-detail.css'],
})
export class EpisodeDetail implements OnInit, OnDestroy {

  episodeId!: string;
  episode: any;
  isCompleted = false;
  isFinished = false;

  audio: HTMLAudioElement = new Audio();
  current_time = 0;
  duration = 0;
  playing = false;

  chunks: { start: number; end: number }[] = [];
  currentChunkIndex = 0;

  private ws!: WebSocket;
  private recorder!: MediaRecorder;
  private mediaStream!: MediaStream;

  score = 0;

  constructor(
    private cdr: ChangeDetectorRef,
    private episodeService: EpisodeService,
    private route: ActivatedRoute,
    private auth: AuthService
  ) { }

  ngOnInit(): void {
    this.episodeId = this.route.snapshot.paramMap.get('id')!;
    const token = this.auth.getAccessToken();
    if (!token) return;

    this.ws = new WebSocket(`${environment.wsUrl}/episodes/audio?token=${token}`);

    this.ws.onopen = () => {
      console.log("WebSocket Connected!");
      this.ws.send(JSON.stringify({
        action: 'start',
        episode_id: this.episodeId
      }));
    };

    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log("WS MESSAGE:", data);

      if (data.action === 'ready') {
        this.chunks = data.chunks;
        console.log("Chunks received:", this.chunks.length);
        return;
      }

      if (data.error) {
        console.error("WS Error:", data.error);
        return;
      }

      if (data.message) {
        console.log("WS:", data.message);
        return;
      }

      this.score = data.score;
      this.cdr.detectChanges();
    };

    this.ws.onclose = () => console.log('WebSocket disconnected');

    this.episodeService.getEpisodeById(this.episodeId).subscribe({
      next: (res: any) => {
        this.episode = res;
        this.isCompleted = res.is_completed;
        this.episode.created_at = new Date(this.episode.created_at);

        this.audio.src = `${environment.apiUrl}/${this.episode.sound}`;

        this.audio.load();

        this.audio.onloadedmetadata = () => {
          this.duration = this.audio.duration;
        };

        this.audio.ontimeupdate = () => {
          this.current_time = this.audio.currentTime;
          this.cdr.detectChanges();
        };
      },
      error: (err) => console.error(err)
    });
  }

  start() {
    if (this.isCompleted) return;
    if (this.chunks.length === 0) {
      console.error("Chunks not loaded yet!");
      return;
    }
    this.isFinished = false;
    this.currentChunkIndex = 0;
    this.playSegment();
  }

  playSegment() {
    if (this.currentChunkIndex >= this.chunks.length) return;

    const chunk = this.chunks[this.currentChunkIndex];
    console.log(`Playing chunk ${this.currentChunkIndex}/${this.chunks.length}: ${chunk.start}s → ${chunk.end}s`);

    this.audio.currentTime = chunk.start;
    const playPromise = this.audio.play();
    if (playPromise) {
      playPromise.catch(err => console.error("Play error:", err));
    }
    this.playing = true;

    const interval = setInterval(() => {
      if (this.audio.currentTime >= chunk.end || this.audio.ended || this.audio.paused) {
        this.audio.pause();
        clearInterval(interval);
        console.log(`Chunk ${this.currentChunkIndex} finished playing`);
        this.startRecording();
      }
    }, 100);
  }

  startRecording() {
    console.log('Recording...');

    const chunk = this.chunks[this.currentChunkIndex];
    const chunkDuration = chunk.end - chunk.start;
    const recordTime = (chunkDuration + 3) * 1000;

    console.log(`Record duration: ${chunkDuration + 3}s`);

    this.startMicStreaming(recordTime);
  }

  startMicStreaming(recordTime: number) {
    navigator.mediaDevices.getUserMedia({
      audio: {
        echoCancellation: false,
        noiseSuppression: false,
        autoGainControl: false
      }
    }).then(stream => {
      this.mediaStream = stream;
      let audioChunks: Blob[] = [];

      this.recorder = new MediaRecorder(stream);

      this.recorder.ondataavailable = (event) => {
        if (event.data.size > 0) audioChunks.push(event.data);
      };

      this.recorder.onstop = () => {
        if (this.isFinished) return;

        const blob = new Blob(audioChunks, { type: 'audio/webm' });
        if (this.ws.readyState === WebSocket.OPEN) {
          this.ws.send(blob);
        }
        audioChunks = [];
        this.nextStep();
      };

      this.recorder.start();

      setTimeout(() => {
        console.log("TIMEOUT FIRED, stopping recorder");
        if (this.recorder && this.recorder.state !== 'inactive') {
          this.recorder.stop();
        }
        if (this.mediaStream) {
          this.mediaStream.getTracks().forEach(track => track.stop());
        }
      }, recordTime);
    });
  }

  nextStep() {
    if (this.isFinished) return;

    this.currentChunkIndex++;
    console.log(`nextStep: ${this.currentChunkIndex}/${this.chunks.length}`);

    if (this.currentChunkIndex >= this.chunks.length) {
      this.isFinished = true;
      console.log("Finished all chunks");

      if (this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ action: "finish" }));
        console.log("FINISH SENT");
      }

      this.audio.pause();
      this.audio.currentTime = 0;
      this.playing = false;
      return;
    }

    this.playSegment();
  }

  stopAll() {
    this.audio.pause();
    this.audio.currentTime = 0;
    this.playing = false;

    if (this.recorder && this.recorder.state !== 'inactive') {
      this.recorder.stop();
    }
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach(track => track.stop());
    }
  }

  formatTime(sec: number): string {
    if (!sec) return '00:00';
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  }

  goBack() {
    window.history.back();
  }

  ngOnDestroy(): void {
    this.stopAll();
    if (this.ws) this.ws.close();
  }

  @HostListener("window:beforeunload")
  handleUnload() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ action: "finish" }));
    }
    this.stopAll();
  }
}