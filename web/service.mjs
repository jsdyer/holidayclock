import {validateCanadian} from './model.mjs';
export function canadianStore(seed, base, fetcher=fetch) {
  if(seed?.schema!=='coolcode.holidays.canada.v1'||!seed.years||!/^https:\/\/canada-holidays\.ca\//.test(base)) throw Error('The bundled calendar source is unavailable.');
  const cache=new Map(),pending=new Map();
  for(const [year,rows] of Object.entries(seed.years)) cache.set(Number(year),{rows:validateCanadian({holidays:rows},Number(year)),capturedAt:seed.retrievedAt,kind:'bundled'});
  return async year=>{
    if(!Number.isInteger(year)||year<2013||year>2038)throw Error('Canadian calendars support 2013–2038.');
    if(cache.has(year))return cache.get(year);
    if(pending.has(year))return pending.get(year);
    const task=(async()=>{
      const control=new AbortController(),timer=setTimeout(()=>control.abort(),15000);
      try{const url=new URL(base);url.searchParams.set('year',year);const response=await fetcher(url,{signal:control.signal,headers:{Accept:'application/json'},credentials:'omit',referrerPolicy:'no-referrer'});
        if(!response.ok)throw Error(`Canada Holidays returned HTTP ${response.status}.`);
        const text=await response.text();if(text.length>2_000_000)throw Error('The Canadian calendar response is too large.');
        const value={rows:validateCanadian(JSON.parse(text),year),capturedAt:new Date().toISOString(),kind:'fetched'};cache.set(year,value);return value;
      }catch(e){if(e.name==='AbortError')throw Error('Canada Holidays did not respond within 15 seconds.');if(e instanceof SyntaxError)throw Error('Canada Holidays did not return calendar JSON.');throw e;}finally{clearTimeout(timer);pending.delete(year);}
    })();pending.set(year,task);return task;
  };
}
