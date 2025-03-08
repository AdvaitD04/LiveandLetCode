// Recorder.js - MIT License (https://github.com/mattdiamond/Recorderjs)

export default class Recorder {
    constructor(source, config) {
      this.context = source.context;
      this.node = (
        this.context.createScriptProcessor || this.context.createJavaScriptNode
      ).call(this.context, config.bufferLen || 4096, config.numChannels || 2, config.numChannels || 2);
      this.node.onaudioprocess = (e) => {
        if (!this.recording) return;
  
        const buffer = [];
        for (let channel = 0; channel < this.config.numChannels; channel++) {
          buffer.push(e.inputBuffer.getChannelData(channel));
        }
        this.worker.postMessage({
          command: "record",
          buffer: buffer,
        });
      };
  
      this.worker = new Worker(config.workerPath || "recorderWorker.js");
      this.worker.onmessage = (e) => {
        const blob = e.data;
        this.callback(blob);
      };
  
      this.worker.postMessage({
        command: "init",
        config: {
          sampleRate: this.context.sampleRate,
          numChannels: this.config.numChannels,
        },
      });
  
      this.recording = false;
      this.callback = config.callback || function () {};
    }
  
    record() {
      this.recording = true;
    }
  
    stop() {
      this.recording = false;
    }
  
    clear() {
      this.worker.postMessage({ command: "clear" });
    }
  
    getBuffer(cb) {
      this.callback = cb || this.callback;
      this.worker.postMessage({ command: "getBuffer" });
    }
  
    exportWAV(cb, mimeType) {
      this.callback = cb || this.callback;
      this.worker.postMessage({
        command: "exportWAV",
        type: mimeType || "audio/wav",
      });
    }
  
    static forceDownload(blob, filename) {
      const url = (window.URL || window.webkitURL).createObjectURL(blob);
      const link = window.document.createElement("a");
      link.href = url;
      link.download = filename || "output.wav";
      link.click();
    }
  }