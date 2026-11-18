import {assets} from './shared/zack-assets.js';
import {passwordVerifier} from './shared/zack-verifier.js';

export const config = {path: ['/zack', '/zack/*']};
const privateHeaders = {'Cache-Control':'private, no-store','X-Robots-Tag':'noindex, nofollow, noarchive','Referrer-Policy':'no-referrer','X-Content-Type-Options':'nosniff'};
const encoder = new TextEncoder();
const hexBytes = hex => Uint8Array.from(hex.match(/../g), x => parseInt(x,16));
const hexString = bytes => Array.from(new Uint8Array(bytes), b => b.toString(16).padStart(2,'0')).join('');
const response = (body,status,headers={}) => new Response(body,{status,headers:{...privateHeaders,...headers}});
const types = {html:'text/html; charset=utf-8',mp4:'video/mp4',jpg:'image/jpeg',vtt:'text/vtt',zip:'application/zip'};

function login(wrong, method) {
  const html = `<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Zack’s walkthroughs | Samuel Ochoa</title><style>*{box-sizing:border-box}body{margin:0;color:#243428;background:#faf9f5;font:17px/1.5 system-ui}main{width:min(100% - 48px,400px);margin:clamp(72px,18vh,160px) auto}h1{font:normal 38px/1.12 Georgia,serif;margin-bottom:36px}label,input,button{display:block;width:100%}input,button{font:inherit;border-radius:8px;padding:11px 14px}input{border:1px solid #758372;background:white;margin:6px 0 14px}button{cursor:pointer;background:#334932;color:white;border:0;font-weight:600}p{color:#9b322b}</style><main><h1>Zack’s walkthroughs</h1><form action="/zack/" method="post"><label for="password">Password</label><input id="password" name="password" type="password" autocomplete="current-password" required>${wrong?'<p role="alert">That password didn’t match. Try again.</p>':''}<button>Open walkthroughs</button></form></main></html>`;
  return response(method==='HEAD'?null:html,401,{'Content-Type':'text/html; charset=utf-8'});
}

export default async function(request) {
  const url = new URL(request.url);
  if (url.pathname === '/zack') return response(null,308,{Location:'/zack/'});
  const secret = Netlify.env.get('ZACK_GATE_SECRET');
  if (!secret || !/^[0-9a-f]{64}$/.test(secret)) return response('Temporarily unavailable',503);
  const raw = hexBytes(secret);
  const signer = await crypto.subtle.importKey('raw',raw,{name:'HMAC',hash:'SHA-256'},false,['sign','verify']);
  const now = Math.floor(Date.now()/1000);
  if (request.method === 'POST' && url.pathname === '/zack/') {
    if (!request.headers.get('content-type')?.startsWith('application/x-www-form-urlencoded')) return response(null,415);
    const candidate = new URLSearchParams(await request.text()).get('password') || '';
    if (!await crypto.subtle.verify('HMAC',signer,hexBytes(passwordVerifier),encoder.encode('password:'+candidate))) return login(true);
    const until = now + 7*86400;
    const sig = hexString(await crypto.subtle.sign('HMAC',signer,encoder.encode('session:'+until)));
    return response(null,303,{Location:'/zack/','Set-Cookie':`zack_access=${until}.${sig}; Path=/zack/; Max-Age=604800; HttpOnly; Secure; SameSite=Lax`});
  }
  if (!['GET','HEAD'].includes(request.method)) return response(null,405,{Allow:'GET, HEAD'});
  const cookie = /(?:^|;\s*)zack_access=(\d{10})\.([a-f0-9]{64})(?:;|$)/.exec(request.headers.get('cookie')||'');
  if (!cookie || Number(cookie[1])<=now || !await crypto.subtle.verify('HMAC',signer,hexBytes(cookie[2]),encoder.encode('session:'+cookie[1]))) return login(false,request.method);
  const name = decodeURIComponent(url.pathname.slice('/zack/'.length)) || 'index.html';
  if (!Object.hasOwn(assets,name)) return response(null,404);
  const sealed = await fetch(new URL('/zack-files/'+assets[name]+'.bin',url.origin));
  if (!sealed.ok) return response(null,503);
  const bytes = new Uint8Array(await sealed.arrayBuffer());
  const key = await crypto.subtle.importKey('raw',raw,'AES-GCM',false,['decrypt']);
  const content = await crypto.subtle.decrypt({name:'AES-GCM',iv:bytes.subarray(0,12),additionalData:encoder.encode(name)},key,bytes.subarray(12));
  const size=content.byteLength,headers={'Content-Type':types[name.split('.').pop()], 'Accept-Ranges':'bytes'};
  if(name.endsWith('.zip'))headers['Content-Disposition']='attachment; filename="Queva walkthroughs for Zack.zip"';
  const range=request.headers.get('Range');
  let start=0,end=size-1;
  if(range){
    const match=/^bytes=(\d*)-(\d*)$/.exec(range);
    if(!match||(!match[1]&&!match[2]))return response(null,416,{'Content-Range':'bytes */'+size});
    if(match[1]){start=Number(match[1]);if(match[2])end=Math.min(Number(match[2]),end);}
    else start=Math.max(0,size-Number(match[2]));
    if(start>end)return response(null,416,{'Content-Range':'bytes */'+size});
    headers['Content-Range']=`bytes ${start}-${end}/${size}`;
  }
  headers['Content-Length']=String(end-start+1);
  return response(request.method==='HEAD'?null:new Uint8Array(content,start,end-start+1),range?206:200,headers);
}
