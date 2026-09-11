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

async function runAudit() {
  await new Promise(r => setTimeout(r, 2000));
  
  const versionRes = await fetch('http://127.0.0.1:9222/json/version');
  const versionData = await versionRes.json();
  const wsUrl = versionData.webSocketDebuggerUrl;
  
  const ws = new WebSocket(wsUrl);
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
  
  await new Promise((resolve, reject) => {
    ws.onopen = resolve;
    ws.onerror = reject;
  });
  
  function send(method, params = {}) {
    return new Promise((resolve, reject) => {
      const msgId = id++;
      pending.set(msgId, { resolve, reject });
      ws.send(JSON.stringify({ id: msgId, method, params }));
    });
  }

  const targetRes = await send('Target.createTarget', { url: 'http://localhost:5173/' });
  const targetId = targetRes.targetId;
  const attachRes = await send('Target.attachToTarget', { targetId, flatten: true });
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
  await sendSession('DOM.enable');

  await new Promise(r => setTimeout(r, 3000));

  await sendSession('Emulation.setDeviceMetricsOverride', {
    width: 360,
    height: 800,
    deviceScaleFactor: 1,
    mobile: true,
  });
  
  await new Promise(r => setTimeout(r, 500));

  const evalRes = await sendSession('Runtime.evaluate', {
    expression: `
      (() => {
        const results = [];
        const all = document.querySelectorAll('*');
        for (const el of all) {
          const scrollW = el.scrollWidth;
          const clientW = el.clientWidth;
          const offsetW = el.offsetWidth;
          if (scrollW > 360 || offsetW > 360) {
            const tag = el.tagName.toLowerCase();
            const cls = el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\\s+/).join('.') : '';
            const idStr = el.id ? '#' + el.id : '';
            results.push({
              sel: tag + idStr + cls,
              scrollW,
              clientW,
              offsetW,
              styleWidth: el.style.width,
              computedWidth: window.getComputedStyle(el).width,
              computedPadding: window.getComputedStyle(el).padding
            });
          }
        }
        return results;
      })()
    `,
    returnByValue: true
  });

  console.log('Elements with scrollW > 360 or offsetW > 360 at 360px viewport:');
  console.log(JSON.stringify(evalRes.result.value, null, 2));

  ws.close();
  chrome.kill();
}

runAudit().catch(err => {
  console.error(err);
  try { chrome.kill(); } catch (e) {}
});
