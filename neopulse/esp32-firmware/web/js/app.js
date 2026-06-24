// NeoPulse Web Interface - Main Application
class NeoPulseApp {
  constructor() {
    this.currentScene = null;
    this.scenes = [];
    this.showId = 'show_' + Date.now();
    this.playing = false;
    this.numPixels = 64;
    this.brightness = 100;
    
    // DOM elements
    this.pixelPreview = document.getElementById('pixel-preview');
    this.colorPicker = document.getElementById('color-picker');
    this.rSlider = document.getElementById('r-slider');
    this.gSlider = document.getElementById('g-slider');
    this.bSlider = document.getElementById('b-slider');
    this.brightnessSlider = document.getElementById('brightness-slider');
    this.brightnessVal = document.getElementById('brightness-val');
    this.sceneSelect = document.getElementById('scene-select');
    this.keyframeUl = document.getElementById('keyframe-ul');
    this.showsList = document.getElementById('shows-list');
    this.playStatus = document.getElementById('play-status');
    
    // Initialize
    this.initPixelPreview();
    this.bindEvents();
    this.loadState();
    this.loadShows();
    this.startPolling();
  }

  initPixelPreview() {
    this.pixelPreview.innerHTML = '';
    for (let i = 0; i < this.numPixels; i++) {
      const pixel = document.createElement('div');
      pixel.className = 'pixel';
      pixel.style.background = '#000';
      this.pixelPreview.appendChild(pixel);
    }
  }

  bindEvents() {
    // Color picker sync
    this.colorPicker.addEventListener('input', (e) => this.onColorPick(e.target.value));
    
    this.rSlider.addEventListener('input', () => this.syncColorFromSliders());
    this.gSlider.addEventListener('input', () => this.syncColorFromSliders());
    this.bSlider.addEventListener('input', () => this.syncColorFromSliders());
    
    // Brightness
    this.brightnessSlider.addEventListener('input', (e) => {
      this.brightness = parseInt(e.target.value);
      this.brightnessVal.textContent = this.brightness;
      this.setBrightness(this.brightness);
    });
    
    // Buttons
    document.getElementById('btn-new-scene').addEventListener('click', () => this.newScene());
    document.getElementById('btn-add-keyframe').addEventListener('click', () => this.addKeyframe());
    document.getElementById('btn-play').addEventListener('click', () => this.playShow());
    document.getElementById('btn-stop').addEventListener('click', () => this.stopAnimation());
    
    // Scene select
    this.sceneSelect.addEventListener('change', (e) => {
      const idx = parseInt(e.target.value);
      if (idx >= 0 && idx < this.scenes.length) {
        this.currentScene = this.scenes[idx];
        this.renderKeyframes();
      }
    });
    
    // Effect select
    document.getElementById('effect-select').addEventListener('change', (e) => {
      if (e.target.value) {
        this.showEffectParams(e.target.value);
      }
    });
  }

  onColorPick(hex) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    this.rSlider.value = r;
    this.gSlider.value = g;
    this.bSlider.value = b;
  }

  syncColorFromSliders() {
    const r = this.rSlider.value;
    const g = this.gSlider.value;
    const b = this.bSlider.value;
    const hex = '#' + [r, g, b].map(x => parseInt(x).toString(16).padStart(2, '0')).join('');
    this.colorPicker.value = hex;
  }

  getCurrentColor() {
    return [parseInt(this.rSlider.value), parseInt(this.gSlider.value), parseInt(this.bSlider.value)];
  }

  async loadState() {
    try {
      const resp = await fetch('/api/state');
      const data = await resp.json();
      if (data.status === 'ok') {
        this.numPixels = data.num_pixels || 64;
        this.initPixelPreview();
        document.getElementById('pixel-count').textContent = `Pixels: ${this.numPixels}`;
        
        // Update WiFi status
        const wifi = data.wifi;
        let wifiText = 'WiFi: ';
        if (wifi.sta_connected) {
          wifiText += `${wifi.sta_ssid} (${wifi.sta_ip})`;
        } else if (wifi.ap_active) {
          wifiText += `AP Mode (${wifi.ap_ssid})`;
        } else {
          wifiText += 'Disconnected';
        }
        document.getElementById('wifi-status').textContent = wifiText;
      }
    } catch (e) {
      console.error('Failed to load state:', e);
    }
  }

  async loadShows() {
    try {
      const resp = await fetch('/api/shows');
      const data = await resp.json();
      if (data.status === 'ok') {
        this.scenes = data.shows || [];
        this.renderSceneSelect();
        this.renderShowsList();
      }
    } catch (e) {
      console.error('Failed to load shows:', e);
    }
  }

  renderSceneSelect() {
    this.sceneSelect.innerHTML = '<option value="-1">No scene selected</option>';
    this.scenes.forEach((scene, idx) => {
      const opt = document.createElement('option');
      opt.value = idx;
      opt.textContent = scene.name || `Scene ${idx + 1}`;
      this.sceneSelect.appendChild(opt);
    });
  }

  renderShowsList() {
    this.showsList.innerHTML = '';
    this.scenes.forEach((show, idx) => {
      const div = document.createElement('div');
      div.className = 'show-item';
      div.innerHTML = `
        <span>${show.name || 'Untitled'}</span>
        <button class="play-btn" data-idx="${idx}">▶</button>
        <button class="delete-btn" data-idx="${idx}">✕</button>
      `;
      
      div.querySelector('.play-btn').addEventListener('click', () => this.playShowById(idx));
      div.querySelector('.delete-btn').addEventListener('click', () => this.deleteShow(idx));
      
      this.showsList.appendChild(div);
    });
  }

  newScene() {
    const scene = {
      id: 'scene_' + Date.now(),
      name: `Scene ${this.scenes.length + 1}`,
      keyframes: [],
      interpolation: 'linear',
      loop_mode: 'single',
      duration: 10,
      brightness: 100,
    };
    this.scenes.push(scene);
    this.currentScene = scene;
    this.renderSceneSelect();
    this.sceneSelect.value = this.scenes.length - 1;
    this.renderKeyframes();
    this.saveCurrentShow();
  }

  addKeyframe() {
    if (!this.currentScene) {
      // Create a default scene first
      this.newScene();
    }
    
    const color = this.getCurrentColor();
    const time = this.currentScene.keyframes.length > 0 
      ? this.currentScene.keyframes[this.currentScene.keyframes.length - 1].time + 2
      : 0;
    
    // Generate gradient colors for all pixels
    const colors = [];
    for (let i = 0; i < this.numPixels; i++) {
      colors.push(color);
    }
    
    this.currentScene.keyframes.push({ time, colors });
    this.renderKeyframes();
    this.saveCurrentShow();
  }

  renderKeyframes() {
    this.keyframeUl.innerHTML = '';
    if (!this.currentScene) return;
    
    this.currentScene.keyframes.forEach((kf, idx) => {
      const li = document.createElement('li');
      li.className = 'keyframe-item';
      
      const colorHex = '#' + kf.colors[0].map(c => c.toString(16).padStart(2, '0')).join('');
      li.innerHTML = `
        <span class="color-swatch" style="background: ${colorHex}"></span>
        <span>${kf.time.toFixed(1)}s</span>
        <button data-idx="${idx}">✕</button>
      `;
      
      li.querySelector('button').addEventListener('click', () => {
        this.currentScene.keyframes.splice(idx, 1);
        this.renderKeyframes();
        this.saveCurrentShow();
      });
      
      this.keyframeUl.appendChild(li);
    });
    
    // Update timeline
    if (window.TimelineEditor) {
      window.TimelineEditor.draw(this.currentScene, this.numPixels);
    }
  }

  async playShow() {
    if (!this.currentScene) return;
    
    // Save current scene as a show
    await this.saveCurrentShow();
    
    try {
      const resp = await fetch('/api/play', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ show_id: this.currentScene.id })
      });
      const data = await resp.json();
      if (data.status === 'ok') {
        this.playStatus.textContent = `Playing: ${data.show}`;
        this.playing = true;
      }
    } catch (e) {
      console.error('Play failed:', e);
    }
  }

  async playShowById(idx) {
    const show = this.scenes[idx];
    if (!show) return;
    
    try {
      const resp = await fetch('/api/play', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ show_id: show.id })
      });
      const data = await resp.json();
      if (data.status === 'ok') {
        this.playStatus.textContent = `Playing: ${data.show}`;
        this.playing = true;
      }
    } catch (e) {
      console.error('Play failed:', e);
    }
  }

  async stopAnimation() {
    try {
      await fetch('/api/play', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ show_id: null })
      });
      this.playStatus.textContent = 'Status: Stopped';
      this.playing = false;
    } catch (e) {
      console.error('Stop failed:', e);
    }
  }

  async setBrightness(value) {
    try {
      await fetch('/api/config/brightness', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ brightness: value })
      });
    } catch (e) {
      console.error('Brightness update failed:', e);
    }
  }

  async saveCurrentShow() {
    if (!this.currentScene) return;
    
    try {
      await fetch('/api/shows', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(this.currentScene)
      });
      this.loadShows();
    } catch (e) {
      console.error('Save failed:', e);
    }
  }

  async deleteShow(idx) {
    const show = this.scenes[idx];
    if (!show) return;
    
    try {
      await fetch(`/api/shows/${show.id}`, { method: 'DELETE' });
      this.scenes.splice(idx, 1);
      this.loadShows();
    } catch (e) {
      console.error('Delete failed:', e);
    }
  }

  showEffectParams(effectType) {
    const section = document.getElementById('params-section');
    const container = document.getElementById('params-container');
    section.style.display = 'block';
    
    // Fetch effect schema
    fetch('/api/effects')
      .then(r => r.json())
      .then(data => {
        const effect = data.effects[effectType];
        if (!effect) return;
        
        container.innerHTML = `<p>${effect.description}</p>`;
        
        effect.params.forEach(paramName => {
          const row = document.createElement('div');
          row.className = 'param-row';
          
          let inputHtml = '';
          if (paramName === 'color' || paramName === 'color_red' || paramName === 'color_blue') {
            inputHtml = `<input type="color" data-param="${paramName}" value="#ff0000">`;
          } else {
            inputHtml = `<input type="number" data-param="${paramName}" step="0.1" min="0" max="255" value="${effect.default_params?.[paramName] || 1}">`;
          }
          
          row.innerHTML = `<label>${paramName}</label>${inputHtml}`;
          container.appendChild(row);
        });
        
        // Add run button
        const btn = document.createElement('button');
        btn.textContent = '▶ Run Effect';
        btn.style.marginTop = '8px';
        btn.style.padding = '8px 16px';
        btn.style.background = '#7c6ff5';
        btn.style.color = 'white';
        btn.style.border = 'none';
        btn.style.borderRadius = '6px';
        btn.style.cursor = 'pointer';
        
        btn.addEventListener('click', () => this.runEffect(effectType));
        container.appendChild(btn);
      });
  }

  async runEffect(effectType) {
    const params = {};
    document.querySelectorAll('#params-container input').forEach(input => {
      const name = input.dataset.param;
      if (input.type === 'color') {
        const hex = input.value.slice(1);
        params[name] = [
          parseInt(hex.slice(0, 2), 16),
          parseInt(hex.slice(2, 4), 16),
          parseInt(hex.slice(4, 6), 16)
        ];
      } else {
        params[name] = parseFloat(input.value);
      }
    });
    
    try {
      await fetch('/api/effect/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: effectType, params, duration_ms: 10000 })
      });
    } catch (e) {
      console.error('Effect run failed:', e);
    }
  }

  startPolling() {
    // Update pixel preview every second
    setInterval(async () => {
      try {
        const resp = await fetch('/api/state');
        const data = await resp.json();
        if (data.status === 'ok' && data.playing) {
          this.playStatus.textContent = `Playing: ${data.current_scene || '...'}`;
          
          // Update pixel preview with current colors
          const pixels = this.pixelPreview.children;
          for (let i = 0; i < Math.min(pixels.length, data.colors?.length || 0); i++) {
            const c = data.colors[i];
            if (c) {
              pixels[i].style.background = `rgb(${c[0]},${c[1]},${c[2]})`;
            }
          }
        }
      } catch (e) {
        // Silently ignore polling errors
      }
    }, 1000);
  }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  window.app = new NeoPulseApp();
});
