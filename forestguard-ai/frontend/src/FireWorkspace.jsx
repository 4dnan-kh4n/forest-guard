import React,{useEffect,useRef,useState} from 'react';
import L from 'leaflet';

function FireMap({report}){
  const host=useRef(null);
  useEffect(()=>{
    const map=L.map(host.current,{attributionControl:false});
    const bounds=L.latLngBounds(report.image_bounds);
    L.imageOverlay('/api/datasets/compartment-279/post_monsoon/image/imagery',report.image_bounds).addTo(map);
    L.geoJSON(report.boundary,{style:{color:'#f3d77c',weight:2,fillOpacity:0}}).addTo(map);
    for(const event of report.detections){
      const point=[event.latitude,event.longitude];bounds.extend(point);
      const marker=L.circleMarker(point,{radius:7,color:event.scope==='inside'?'#dd482f':'#eaa63b',fillOpacity:.85}).addTo(map);
      const label=document.createElement('div');label.textContent=`${event.sensor} · ${event.confidence} confidence · ${new Date(event.observed_at).toLocaleString('en-IN',{timeZone:'Asia/Kolkata'})} IST · ${event.frp_mw} MW`;
      marker.bindPopup(label);
    }
    map.fitBounds(bounds,{padding:[20,20]});
    const resize=new ResizeObserver(()=>map.invalidateSize());resize.observe(host.current);
    return()=>{resize.disconnect();map.remove();};
  },[report.fetched_at]);
  return <div className="change-map" ref={host} role="region" aria-label="Satellite fire detections and compartment boundary"/>;
}

export default function FireWorkspace({api}){
  const [report,setReport]=useState(null),[busy,setBusy]=useState(false),[error,setError]=useState('');
  async function refresh(){setBusy(true);setError('');try{setReport(await api('/api/fire/refresh',{method:'POST'}));}catch(e){setError(e.message);}finally{setBusy(false);}}
  useEffect(()=>{
    let active=true;
    api('/api/fire').then(async r=>{
      if(!active)return;
      setReport(r);
      if(navigator.onLine&&(!r.available||Date.now()-Date.parse(r.fetched_at)>600000)){
        setBusy(true);
        try{const fresh=await api('/api/fire/refresh',{method:'POST'});if(active)setReport(fresh);}
        catch(e){if(active)setError(e.message);}
        finally{if(active)setBusy(false);}
      }
    }).catch(e=>{if(active)setError(e.message);});
    const timer=setInterval(()=>{if(navigator.onLine)refresh();},15*60*1000);
    return()=>{active=false;clearInterval(timer);};
  },[]);
  const stamp=s=>new Date(s).toLocaleString('en-IN',{timeZone:'Asia/Kolkata'})+' IST';
  return <section aria-label="Satellite fire monitoring"><div className="change-intro"><div><h2>Satellite fire detections</h2><p>NASA thermal observations · compartment 279 and its 2 km surroundings · last seven days.</p></div><button className="button primary" disabled={busy} onClick={refresh}>{busy?'Updating NASA observations…':'Update fire feed'}</button></div>
    {error&&<p className="error-box" role="alert">{error}</p>}
    {!report?<p role="status">Opening saved fire observations…</p>:!report.available?<p>No saved fire observations yet. Select Update fire feed.</p>:<>
      <div className="change-period"><span>Retrieved: <strong>{stamp(report.fetched_at)}</strong></span><span>{report.status==='complete'?'Both satellites checked':'Partial satellite feed'}</span></div>
      <div className="stats-grid">{[['Detection centres inside',report.inside_count,'Thermal signals, not confirmed incidents'],['Nearby detections',report.nearby_count,'Within approximately 2 km of the boundary'],['Satellites checked',report.sources.length,'NOAA-20 / NOAA-21 · VIIRS'],['Refresh interval','15 min','While this view is open; internet required']].map(([title,value,note])=><article className="stat-card" key={title}><div className="stat-top">{title}</div><strong>{value}</strong><small>{note}</small></article>)}</div>
      <section className="panel"><FireMap report={report}/></section><p className="change-map-note">Background image: {report.background_date}. Yellow outline: compartment 279. Red: centre inside; orange: nearby. The background is saved context, not a live photograph of a fire.</p>
      <section className="panel change-evidence"><h3>{report.detections.length?'Recent thermal observations':'No detections reported in this area'}</h3><p>{report.limits}</p>{report.detections.map((event,index)=><div className="report-row" key={index}><div><h3>{event.sensor} · {event.scope==='inside'?'Centre inside compartment':'Nearby'}</h3><p>{stamp(event.observed_at)} · {event.latitude.toFixed(5)}, {event.longitude.toFixed(5)} · {event.confidence} confidence · {event.frp_mw} MW radiant power</p></div></div>)}<h3>Feed evidence</h3>{report.sources.map(source=><p key={source.sensor}>{source.sensor}: {source.regional_rows.toLocaleString()} regional records checked. Latest regional detection: {source.latest_observation?stamp(source.latest_observation):'No records in feed'}.</p>)}{report.errors.length>0&&<p>Unavailable source: {report.errors.map(e=>e.sensor).join(', ')}.</p>}<div className="change-actions"><a className="button secondary" href="/api/fire/report/json">Download fire evidence ↓</a><a className="button secondary" href="https://firms.modaps.eosdis.nasa.gov/map/" target="_blank" rel="noreferrer">Open NASA fire map ↗</a></div><p>{report.attribution}</p></section>
      <section className="panel change-evidence"><h3>Annual fire history</h3><p>2022–2026 historical detections require archived satellite records. The recent seven-day feed cannot reconstruct five years. Historical totals are not substituted with generated values.</p></section>
    </>}
  </section>;
}
