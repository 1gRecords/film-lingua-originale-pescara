// Cloudflare Worker: The Space Montesilvano showtimes for the GitHub Pages build.
// thespacecinema.it challenges requests that start from GitHub runners, even through
// a Worker. So a Cron Trigger refreshes the next 7 days every hour inside a Durable
// Object pinned to Western Europe, and GitHub only reads the stored copy.
// GET /films?day=YYYY-MM-DD and GET /status, both with header "x-key: <PROXY_KEY>".
// PROXY_KEY is a Worker secret, never in this file. Deploy: cd cloudflare && npx wrangler deploy
import { DurableObject } from 'cloudflare:workers';

const BASE = 'https://www.thespacecinema.it';
const PAGE = BASE + '/cinema/montesilvano/al-cinema';
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36';
const DAYS = 7;
const FRESH_MS = 6 * 60 * 60 * 1000;

function romeDay(offset) {
  const when = new Date(Date.now() + offset * 86400000);
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'Europe/Rome' }).format(when);
}

async function colo() {
  try {
    const text = await (await fetch('https://www.cloudflare.com/cdn-cgi/trace')).text();
    return (text.match(/^colo=(\w+)/m) || [])[1] || '?';
  } catch {
    return '?';
  }
}

export class Fetcher extends DurableObject {
  async cookies(headers) {
    const page = await fetch(PAGE, { headers });
    const list = page.headers.getSetCookie ? page.headers.getSetCookie() : [];
    return { pageStatus: page.status, cookie: list.map(c => c.split(';')[0]).join('; ') };
  }

  async live(days) {
    const headers = { 'User-Agent': UA, 'Accept-Language': 'it-IT,it;q=0.9,en;q=0.8' };
    const { pageStatus, cookie } = await this.cookies(headers);
    const results = {};
    for (const day of days) {
      const api = `${BASE}/api/microservice/showings/cinemas/1026/films?showingDate=${day}T00:00:00`
        + '&minEmbargoLevel=3&includesSession=true&includeSessionAttributes=true';
      const res = await fetch(api, {
        headers: { ...headers, Accept: 'application/json', Referer: PAGE, Cookie: cookie },
      });
      results[day] = { status: res.status, body: await res.text() };
    }
    return { pageStatus, results };
  }

  async refresh() {
    const days = Array.from({ length: DAYS }, (_, i) => romeDay(i));
    const { pageStatus, results } = await this.live(days);
    const summary = [];
    for (const day of days) {
      const { status, body } = results[day];
      if (status === 200) await this.ctx.storage.put('films:' + day, { at: Date.now(), body });
      summary.push(`${day}:${status}`);
    }
    for (const key of (await this.ctx.storage.list({ prefix: 'films:' })).keys()) {
      if (key.slice(6) < days[0]) await this.ctx.storage.delete(key);
    }
    const last = { at: new Date().toISOString(), colo: await colo(), pageStatus, summary };
    await this.ctx.storage.put('last', last);
    return last;
  }

  async cached(day) {
    return (await this.ctx.storage.get('films:' + day)) || null;
  }

  async status() {
    return (await this.ctx.storage.get('last')) || {};
  }
}

function fetcher(env) {
  return env.FETCHER.get(env.FETCHER.idFromName('italy'), { locationHint: 'weur' });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (!env.PROXY_KEY || request.headers.get('x-key') !== env.PROXY_KEY) {
      return new Response('forbidden', { status: 403 });
    }
    const stub = fetcher(env);
    if (url.pathname === '/status') return Response.json(await stub.status());
    const day = url.searchParams.get('day') || '';
    if (url.pathname !== '/films' || !/^\d{4}-\d{2}-\d{2}$/.test(day)) {
      return new Response('use /films?day=YYYY-MM-DD or /status', { status: 400 });
    }
    const json = { 'Content-Type': 'application/json; charset=utf-8' };
    const stored = await stub.cached(day);
    if (stored && Date.now() - stored.at < FRESH_MS) {
      return new Response(stored.body, { headers: { ...json, 'X-Source': 'cache' } });
    }
    // Nothing fresh stored: try live (works when the caller is not blocked).
    const { results } = await stub.live([day]);
    const res = results[day];
    if (res.status === 200) return new Response(res.body, { headers: { ...json, 'X-Source': 'live' } });
    if (stored) return new Response(stored.body, { headers: { ...json, 'X-Source': 'stale' } });
    return new Response(res.body, { status: res.status, headers: json });
  },

  async scheduled(event, env, ctx) {
    ctx.waitUntil(fetcher(env).refresh());
  },
};
