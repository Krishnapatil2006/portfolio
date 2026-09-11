import { spawn } from 'child_process';

const chromePath = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const chrome = spawn(chromePath, [
  '--headless=new',
  '--remote-debugging-port=9222',
  '--remote-debugging-address=127.0.0.1',
  '--user-data-dir=C:\\Users\\IMRD\\AppData\\Local\\Temp\\chrome-debug-profile',
  '--disable-gpu',
  '--no-sandbox'
]);

setTimeout(async () => {
  try {
    const res = await fetch('http://127.0.0.1:9222/json/version');
    const data = await res.json();
    console.log('SUCCESS! Connected to Chrome:', data.Browser);
  } catch (err) {
    console.error('Error:', err.message);
  } finally {
    chrome.kill();
  }
}, 2000);
