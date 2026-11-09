// Cloudflare Worker: reads The Space Montesilvano showtimes for one day.
// GitHub runners get 403 from thespacecinema.it; this Worker fetches from Cloudflare instead.
// Call: GET https://<worker>/films?day=YYYY-MM-DD with header "x-key: <PROXY_KEY>".
// PROXY_KEY is a Worker secret (Settings -> Variables and Secrets), never in this file.
const BASE = 'https://www.thespacecinema.it';
const PAGE = BASE + '/cinema/montesilvano/al-cinema';
const UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36';

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
      headers: { 'Content-Type': 'application/json; charset=utf-8', 'X-Page-Status': String(page.status) },
    });
  },
};
