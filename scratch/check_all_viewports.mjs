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
  await new Promise((resolve, reject) => { ws.onopen = resolve; ws.onerror = reject; });
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
  await new Promise(r => setTimeout(r, 3000));

  for (const width of [320, 360, 375, 390, 412, 430, 480, 768, 820, 1024]) {
    await sendSession('Emulation.setDeviceMetricsOverride', {
      width, height: 800, deviceScaleFactor: 1, mobile: true,
    });
    await new Promise(r => setTimeout(r, 400));

    const evalRes = await sendSession('Runtime.evaluate', {
      expression: `
        (() => {
          const docScroll = document.documentElement.scrollWidth;
          const bodyScroll = document.body.scrollWidth;
          const rootScroll = document.getElementById('root').scrollWidth;
          const cw = document.documentElement.clientWidth;
          
          const exceeding = [];
          for (const el of document.querySelectorAll('*')) {
            const rect = el.getBoundingClientRect();
            if (rect.right > cw + 0.5) {
              const tag = el.tagName.toLowerCase();
              const cls = el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\\s+/).join('.') : '';
              exceeding.push({
                tag: tag + cls,
                right: Math.round(rect.right * 10) / 10,
                width: Math.round(rect.width * 10) / 10,
                excess: Math.round((rect.right - cw) * 10) / 10
              });
            }
          }
          return {
            width: ${width},
            cw,
            docScroll,
            bodyScroll,
            rootScroll,
            hasOverflow: docScroll > cw || bodyScroll > cw || rootScroll > cw || exceeding.length > 0,
            exceedingCount: exceeding.length,
            topExceeding: exceeding.slice(0, 8)
          };
        })()
      `,
      returnByValue: true
    });

    const res = evalRes.result.value;
    console.log('Viewport ' + res.width + 'px: clientWidth=' + res.cw + ', docScroll=' + res.docScroll + ', bodyScroll=' + res.bodyScroll + ', rootScroll=' + res.rootScroll);
    if (res.hasOverflow) {
      console.log('  -> OVERFLOW! Exceeding elements (' + res.exceedingCount + '):', res.topExceeding);
    }
  }

  ws.close();
  chrome.kill();
}

runAudit().catch(err => {
  console.error(err);
  try { chrome.kill(); } catch (e) {}
});
