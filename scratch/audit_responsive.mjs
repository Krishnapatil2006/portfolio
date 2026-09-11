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

  // Create a new target page
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

  // Wait for page to finish loading and rendering
  await new Promise(r => setTimeout(r, 3500));

  const viewports = [
    { w: 320, h: 800 },
    { w: 360, h: 800 },
    { w: 375, h: 812 },
    { w: 390, h: 844 },
    { w: 393, h: 852 },
    { w: 412, h: 915 },
    { w: 430, h: 932 },
    { w: 480, h: 900 },
    { w: 768, h: 1024 },
    { w: 820, h: 1180 },
    { w: 1024, h: 768 },
    { w: 1280, h: 800 },
    { w: 1440, h: 900 },
    { w: 1920, h: 1080 },
  ];

  console.log('=== RESPONSIVENESS AUDIT RESULTS ===\n');

  for (const vp of viewports) {
    await sendSession('Emulation.setDeviceMetricsOverride', {
      width: vp.w,
      height: vp.h,
      deviceScaleFactor: 1,
      mobile: vp.w <= 820,
    });
    
    // Allow layout reflow
    await new Promise(r => setTimeout(r, 300));

    const evalRes = await sendSession('Runtime.evaluate', {
      expression: `
        (() => {
          const scrollW = document.documentElement.scrollWidth;
          const clientW = document.documentElement.clientWidth;
          const innerW = window.innerWidth;
          
          const overflowing = [];
          const all = document.querySelectorAll('*');
          for (const el of all) {
            // Check bounding rect
            const rect = el.getBoundingClientRect();
            // Don't flag hidden or 0-size elements
            if (rect.width === 0 && rect.height === 0) continue;
            
            // Check if right edge exceeds viewport by more than 1px
            if (rect.right > innerW + 1) {
              const tag = el.tagName.toLowerCase();
              const cls = el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\\s+/).join('.') : '';
              const idStr = el.id ? '#' + el.id : '';
              overflowing.push({
                selector: tag + idStr + cls,
                rectRight: Math.round(rect.right),
                rectWidth: Math.round(rect.width),
                overflowPx: Math.round(rect.right - innerW)
              });
            }
          }
          
          return {
            scrollW,
            clientW,
            innerW,
            hasOverflow: scrollW > clientW,
            diff: scrollW - clientW,
            overflowCount: overflowing.length,
            topOverflowElements: overflowing.slice(0, 10)
          };
        })()
      `,
      returnByValue: true
    });

    const result = evalRes.result.value;
    const status = result.hasOverflow ? 'FAILED (OVERFLOW ' + result.diff + 'px)' : 'PASSED';
    console.log(`[${vp.w}x${vp.h}] -> ${status} (scrollWidth: ${result.scrollW}, clientWidth: ${result.clientW})`);
    if (result.hasOverflow) {
      console.log(`  Top overflowing elements (${result.overflowCount} total):`);
      for (const el of result.topOverflowElements) {
        console.log(`    - ${el.selector}: right=${el.rectRight}px (width=${el.rectWidth}px, overflow=+${el.overflowPx}px)`);
      }
    }
  }

  ws.close();
  chrome.kill();
}

runAudit().catch(err => {
  console.error('Audit failed:', err);
  try { chrome.kill(); } catch (e) {}
});
