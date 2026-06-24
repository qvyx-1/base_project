// NeoPulse Timeline Editor
class TimelineEditor {
  static canvas = null;
  static ctx = null;
  static dragging = null;
  
  static init() {
    this.canvas = document.getElementById('timeline-canvas');
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    
    // Mouse events for dragging keyframes
    this.canvas.addEventListener('mousedown', (e) => this.onMouseDown(e));
    this.canvas.addEventListener('mousemove', (e) => this.onMouseMove(e));
    this.canvas.addEventListener('mouseup', () => this.onMouseUp());
  }
  
  static draw(scene, numPixels) {
    if (!this.ctx || !scene) return;
    
    const ctx = this.ctx;
    const w = this.canvas.width;
    const h = this.canvas.height;
    
    // Clear
    ctx.fillStyle = '#0a0a14';
    ctx.fillRect(0, 0, w, h);
    
    if (!scene.keyframes || scene.keyframes.length === 0) {
      ctx.fillStyle = '#333';
      ctx.font = '14px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText('Add keyframes to start editing', w / 2, h / 2);
      return;
    }
    
    const duration = scene.duration || 10;
    const padding = 40;
    const usableWidth = w - padding * 2;
    const pixelsPerSecond = usableWidth / Math.max(1, duration);
    
    // Draw time ruler
    ctx.fillStyle = '#333';
    ctx.font = '10px sans-serif';
    ctx.textAlign = 'center';
    
    for (let t = 0; t <= duration; t++) {
      const x = padding + t * pixelsPerSecond;
      ctx.fillRect(x, h - 20, 1, 10);
      ctx.fillText(`${t}s`, x, h - 5);
    }
    
    // Draw scene background
    const sceneY = 10;
    const sceneH = 30;
    ctx.fillStyle = '#1a1a3e';
    ctx.fillRect(padding, sceneY, usableWidth, sceneH);
    ctx.strokeStyle = '#7c6ff5';
    ctx.strokeRect(padding, sceneY, usableWidth, sceneH);
    
    // Draw keyframes
    scene.keyframes.forEach((kf, idx) => {
      const x = padding + kf.time * pixelsPerSecond;
      
      // Color swatch
      const colorHex = '#' + kf.colors[0].map(c => c.toString(16).padStart(2, '0')).join('');
      ctx.fillStyle = colorHex;
      ctx.fillRect(x - 8, sceneY + 2, 16, sceneH - 4);
      
      // Diamond marker
      ctx.fillStyle = '#fff';
      ctx.beginPath();
      ctx.moveTo(x, sceneY - 5);
      ctx.lineTo(x + 6, sceneY + 10);
      ctx.lineTo(x, sceneY + 25);
      ctx.lineTo(x - 6, sceneY + 10);
      ctx.closePath();
      ctx.fill();
      ctx.strokeStyle = '#7c6ff5';
      ctx.stroke();
      
      // Time label
      ctx.fillStyle = '#aaa';
      ctx.font = '9px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(`${kf.time.toFixed(1)}s`, x, sceneY + sceneH + 14);
    });
    
    // Draw interpolation lines between keyframes
    if (scene.keyframes.length > 1) {
      ctx.strokeStyle = '#7c6ff544';
      ctx.lineWidth = 2;
      ctx.setLineDash([4, 4]);
      ctx.beginPath();
      
      scene.keyframes.forEach((kf, idx) => {
        const x = padding + kf.time * pixelsPerSecond;
        const y = sceneY + sceneH / 2;
        if (idx === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      });
      ctx.stroke();
      ctx.setLineDash([]);
    }
    
    // Store keyframe positions for hit detection
    this._keyframePositions = scene.keyframes.map((kf, idx) => ({
      x: padding + kf.time * pixelsPerSecond,
      idx: idx
    }));
  }
  
  static onMouseDown(e) {
    if (!this._keyframePositions) return;
    
    const rect = this.canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    
    // Check if near a keyframe
    for (const kf of this._keyframePositions) {
      if (Math.abs(mx - kf.x) < 10) {
        this.dragging = kf.idx;
        break;
      }
    }
  }
  
  static onMouseMove(e) {
    if (this.dragging === null) return;
    
    const rect = this.canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    
    // Update the dragged keyframe's time
    if (window.app && window.app.currentScene) {
      const padding = 40;
      const duration = window.app.currentScene.duration || 10;
      const usableWidth = this.canvas.width - padding * 2;
      const pixelsPerSecond = usableWidth / Math.max(1, duration);
      
      let newTime = (mx - padding) / pixelsPerSecond;
      newTime = Math.max(0, Math.min(duration, newTime));
      
      window.app.currentScene.keyframes[this.dragging].time = newTime;
      this.draw(window.app.currentScene, window.app.numPixels || 64);
    }
  }
  
  static onMouseUp() {
    if (this.dragging !== null && window.app) {
      window.app.saveCurrentShow();
    }
    this.dragging = null;
  }
}

// Initialize timeline on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  TimelineEditor.init();
  window.TimelineEditor = TimelineEditor;
});
