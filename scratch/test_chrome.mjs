import { spawn } from 'child_process';
import http from 'http';

const chromePath = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const chrome = spawn(chromePath, [
  '--headless=new',
  '--remote-debugging-port=9222',
  '--user-data-dir=C:\\Users\\IMRD\\AppData\\Local\\Temp\\chrome-debug-profile',
  '--disable-gpu',
  '--no-sandbox'
]);

// Give Chrome a moment to start
setTimeout(async () => {
  try {
    const res = await fetch('http://localhost:9222/json/version');
    const data = await res.json();
    console.log('Chrome connected successfully! WebSocket URL:', data.webSocketDebuggerUrl);
  } catch (err) {
    console.error('Failed to connect to Chrome:', err);
  } finally {
    chrome.kill();
  }
}, 1500);
