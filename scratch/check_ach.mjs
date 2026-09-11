import { spawn } from 'child_process';

const chromePath = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const chrome = spawn(chromePath, [
  '--headless=new',
  '--remote-debugging-port=9222',
  '--remote-debugging-address=127.0.0.1',
  '--user-data-dir=C:\\Users\\IMRD\\AppData\\Local\\Temp\\chrome-debug-profile-' + Date.now(),
  '--disable-gpu',
  '--no-sandbox'
]);

async function run() {
  await new Promise(r => setTimeout(r, 2000));
  const versionRes = await fetch('http://127.0.0.1:9222/json/version');
  const versionData = await versionRes.json();
  const ws = new WebSocket(versionData.webSocketDebuggerUrl);
  let id = 1;
  const pending = new Map();
  ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    if (msg.id && pending.has(msg.id)) {
      const { resolve, reject } = pending.get(msg.id);
      pending.delete(msg.id);
      if (msg.error) reject(msg.error);
      else resolve(msg.result);
    }
  };
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  function send(method, params = {}) {
    return new Promise((resolve, reject) => {
      const msgId = id++;
      pending.set(msgId, { resolve, reject });
      ws.send(JSON.stringify({ id: msgId, method, params }));
    });
  }

  const targetRes = await send('Target.createTarget', { url: 'http://localhost:5173/' });
  const attachRes = await send('Target.attachToTarget', { targetId: targetRes.targetId, flatten: true });
  const sessionId = attachRes.sessionId;
  function sendSession(method, params = {}) {
    return new Promise((resolve, reject) => {
      const msgId = id++;
      pending.set(msgId, { resolve, reject });
      ws.send(JSON.stringify({ id: msgId, sessionId, method, params }));
    });
  }

  await sendSession('Page.enable');
  await sendSession('Runtime.enable');
  await new Promise(r => setTimeout(r, 3000));
  await sendSession('Emulation.setDeviceMetricsOverride', {
    width: 360, height: 800, deviceScaleFactor: 1, mobile: true,
  });
  await new Promise(r => setTimeout(r, 500));

  const evalRes = await sendSession('Runtime.evaluate', {
    expression: `
      (() => {
        const ach = document.querySelector('.achievement');
        if (!ach) return 'No .achievement found';
        const children = [];
        for (const el of ach.querySelectorAll('*')) {
          children.push({
            tag: el.tagName,
            cls: el.className,
            scrollW: el.scrollWidth,
            offsetW: el.offsetWidth,
            clientW: el.clientWidth,
            text: el.innerText ? el.innerText.substring(0, 30) : '',
            whiteSpace: window.getComputedStyle(el).whiteSpace
          });
        }
        return {
          achScrollW: ach.scrollWidth,
          achClientW: ach.clientWidth,
          children
        };
      })()
    `,
    returnByValue: true
  });

  console.log(JSON.stringify(evalRes.result.value, null, 2));
  ws.close();
  chrome.kill();
}
run().catch(e => { console.error(e); chrome.kill(); });
