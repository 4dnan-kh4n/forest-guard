import React,{useEffect,useRef,useState} from 'react';
import L from 'leaflet';

function FireMap({report}){
  const host=useRef(null);
  useEffect(()=>{
    const map=L.map(host.current,{scrollWheelZoom:false,attributionControl:false});
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
  return <section aria-label="Satellite fire monitoring"><div className="change-intro"><div><h2>Satellite fire detections</h2><p>Joga · satellite fire signals from the last seven days.</p></div><div className="change-actions"><button className="button primary" disabled={busy} onClick={refresh}>{busy?'Updating NASA observations…':'Update fire feed'}</button>{report?.available&&<a className="button secondary" href="/api/fire/report/pdf">Download fire report (PDF) ↓</a>}</div></div>
    {error&&<p className="error-box" role="alert">{error}</p>}
    {!report?<p role="status">Opening saved fire observations…</p>:!report.available?<p>No saved fire observations yet. Select Update fire feed.</p>:<>
      <div className="change-period"><span>Retrieved: <strong>{stamp(report.fetched_at)}</strong></span><span>{report.status==='complete'?'Both satellites checked':'Partial satellite feed'}</span></div>
      <div className="stats-grid">{[['Fire signals in your mapped area',report.inside_count,'Last seven days'],['Nearby fire signals',report.nearby_count,'Within 2 km']].map(([title,value,note])=><article className="stat-card" key={title}><div className="stat-top">{title}</div><strong>{value}</strong><small>{note}</small></article>)}</div>
      <section className="panel"><FireMap report={report}/></section><p className="change-map-note">Saved image: {report.background_date}. Red markers: inside your mapped area. Orange: nearby.</p>
      <details className="panel change-evidence"><summary>Detection details and satellite sources</summary><h3>{report.detections.length?'Recent thermal observations':'No detections reported in this area'}</h3><p>{report.limits}</p>{report.detections.map((event,index)=><div className="report-row" key={index}><div><h3>{event.sensor} · {event.scope==='inside'?'Inside mapped area':'Nearby'}</h3><p>{stamp(event.observed_at)} · {event.latitude.toFixed(5)}, {event.longitude.toFixed(5)} · {event.confidence} confidence · {event.frp_mw} MW radiant power</p></div></div>)}<h3>Feed evidence</h3>{report.sources.map(source=><p key={source.sensor}>{source.sensor}: {source.regional_rows.toLocaleString()} regional records checked. Latest regional detection: {source.latest_observation?stamp(source.latest_observation):'No records in feed'}.</p>)}{report.errors.length>0&&<p>Unavailable source: {report.errors.map(e=>e.sensor).join(', ')}.</p>}<div className="change-actions"><a className="button secondary" href={`https://firms.modaps.eosdis.nasa.gov/map/#d:7days;@${((report.boundary.bbox[0]+report.boundary.bbox[2])/2).toFixed(5)},${((report.boundary.bbox[1]+report.boundary.bbox[3])/2).toFixed(5)},14z`} target="_blank" rel="noreferrer">Open NASA fire map ↗</a></div><p>{report.attribution}</p><p>Mapped area: compartment 279 in Joga. No satellite signal does not prove that no fire occurred.</p></details>
      <details className="panel change-evidence"><summary>Previous years</summary><p>NASA is processing our request for 2022–2026 fire records. These will appear when the archive is available.</p></details>
    </>}
  </section>;
}
