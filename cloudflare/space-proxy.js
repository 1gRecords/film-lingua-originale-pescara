// Cloudflare Worker: reads The Space Montesilvano showtimes for one day.
// GitHub runners get 403 from thespacecinema.it, and so does a Worker running in a
// US data centre (Cloudflare challenge). The fetch therefore runs inside a Durable
// Object pinned to Western Europe (locationHint 'weur').
// Call: GET https://<worker>/films?day=YYYY-MM-DD with header "x-key: <PROXY_KEY>".
// PROXY_KEY is a Worker secret, never in this file. Deploy: cd cloudflare && npx wrangler deploy
import { DurableObject } from 'cloudflare:workers';

const BASE = 'https://www.thespacecinema.it';
const PAGE = BASE + '/cinema/montesilvano/al-cinema';
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36';

async function colo() {
  try {
    const text = await (await fetch('https://www.cloudflare.com/cdn-cgi/trace')).text();
    return (text.match(/^colo=(\w+)/m) || [])[1] || '?';
  } catch {
    return '?';
  }
}

export class Fetcher extends DurableObject {
  async fetch(request) {
    const day = new URL(request.url).searchParams.get('day');
    const headers = { 'User-Agent': UA, 'Accept-Language': 'it-IT,it;q=0.9,en;q=0.8' };
    const page = await fetch(PAGE, { headers });
    const cookies = (page.headers.getSetCookie ? page.headers.getSetCookie() : [])
      .map(c => c.split(';')[0]).join('; ');
    const api = `${BASE}/api/microservice/showings/cinemas/1026/films?showingDate=${day}T00:00:00`
      + '&minEmbargoLevel=3&includesSession=true&includeSessionAttributes=true';
    const res = await fetch(api, {
      headers: { ...headers, Accept: 'application/json', Referer: PAGE, Cookie: cookies },
    });
    return new Response(res.body, {
      status: res.status,
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
        'X-Page-Status': String(page.status),
        'X-Fetch-Colo': await colo(),
      },
    });
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (!env.PROXY_KEY || request.headers.get('x-key') !== env.PROXY_KEY) {
      return new Response('forbidden', { status: 403 });
    }
    const day = url.searchParams.get('day') || '';
    if (url.pathname !== '/films' || !/^\d{4}-\d{2}-\d{2}$/.test(day)) {
      return new Response('use /films?day=YYYY-MM-DD', { status: 400 });
    }
    const stub = env.FETCHER.get(env.FETCHER.idFromName('italy'), { locationHint: 'weur' });
    return stub.fetch(`https://do/films?day=${day}`);
  },
};
