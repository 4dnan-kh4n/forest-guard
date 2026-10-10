import React,{useEffect,useRef,useState} from 'react';
import L from 'leaflet';

function FireMap({report}){
  const host=useRef(null);
  useEffect(()=>{
    const map=L.map(host.current,{scrollWheelZoom:false,attributionControl:false});
    const bounds=L.latLngBounds(report.image_bounds);
    for(const event of report.detections)bounds.extend([event.latitude,event.longitude]);
    map.fitBounds(bounds,{padding:[20,20]});
    L.imageOverlay('/api/datasets/compartment-279/post_monsoon/image/imagery',report.image_bounds).addTo(map);
    L.geoJSON(report.boundary,{style:{color:'#f3d77c',weight:2,fillOpacity:0}}).addTo(map);
    for(const event of report.detections){
      const point=[event.latitude,event.longitude];
      const marker=L.circleMarker(point,{radius:7,color:event.scope==='inside'?'#dd482f':'#eaa63b',fillOpacity:.85}).addTo(map);
      const label=document.createElement('div');label.textContent=`${event.sensor} · ${event.confidence} confidence · ${new Date(event.observed_at).toLocaleString('en-IN',{timeZone:'Asia/Kolkata'})} IST · ${event.frp_mw} MW`;
      marker.bindPopup(label);
    }
    const resize=new ResizeObserver(()=>map.invalidateSize());resize.observe(host.current);
    return()=>{resize.disconnect();map.remove();};
  },[report.fetched_at,report.year]);
  return <div className="change-map" ref={host} role="region" aria-label="Satellite fire detections and compartment boundary"/>;
}

export default function FireWorkspace({api}){
  const [report,setReport]=useState(null),[archive,setArchive]=useState(null),[period,setPeriod]=useState('recent'),[busy,setBusy]=useState(false),[error,setError]=useState('');
  async function refresh(){setBusy(true);setError('');try{setReport(await api('/api/fire/refresh',{method:'POST'}));}catch(e){setError(e.message);}finally{setBusy(false);}}
  useEffect(()=>{
    let active=true;
    api('/api/fire/history').then(r=>{if(active)setArchive(r);}).catch(e=>{if(active)setError(e.message);});
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
  const selected=archive?.observations?.find(row=>String(row.year)===period);
  const current=period==='recent'?report:selected?{...archive,...selected,fetched_at:archive.imported_at,status:'archive',sources:[{sensor:archive.sensor,...archive.source}],errors:[],attribution:archive.attribution}:null;
  const stamp=s=>new Date(s).toLocaleString('en-IN',{timeZone:'Asia/Kolkata'})+' IST';
  return <section aria-label="Satellite fire monitoring"><div className="change-intro"><div><h2>Satellite fire detections</h2><p>Joga · recent and yearly satellite fire records.</p></div><div className="change-actions"><button className="button primary" disabled={busy} onClick={()=>{setPeriod('recent');refresh();}}>{busy?'Updating NASA observations…':'Update fire feed'}</button>{current?.available&&<a className="button secondary" href={period==='recent'?'/api/fire/report/pdf':'/api/fire/history/report/pdf'}>Download fire report (PDF) ↓</a>}</div></div>
    <div className="change-actions year-selector"><button className={`button ${period==='recent'?'primary':'secondary'}`} aria-pressed={period==='recent'} onClick={()=>setPeriod('recent')}>Last 7 days</button>{archive?.available&&archive.observations.map(row=><button className={`button ${period===String(row.year)?'primary':'secondary'}`} aria-pressed={period===String(row.year)} key={row.year} onClick={()=>setPeriod(String(row.year))}>{row.year}</button>)}</div>
    {error&&<p className="error-box" role="alert">{error}</p>}
    {!current?<p role="status">Opening saved fire observations…</p>:!current.available?<p>No saved fire observations yet. Select Update fire feed.</p>:<>
      <div className="change-period"><span>Retrieved: <strong>{stamp(current.fetched_at)}</strong></span><span>{period!=='recent'?(selected?.partial_year?'2026 · partial archive':'NASA historical archive'):current.status==='complete'?'Both satellites checked':'Partial satellite feed'}</span></div>
      <div className="stats-grid">{[['Fire signals in your mapped area',current.inside_count,period==='recent'?'Last seven days':`Recorded in ${period}`],['Nearby fire signals',current.nearby_count,'Within 2 km']].map(([title,value,note])=><article className="stat-card" key={title}><div className="stat-top">{title}</div><strong>{value}</strong><small>{note}</small></article>)}</div>
      <section className="panel"><FireMap report={current}/></section><p className="change-map-note">Saved image: {current.background_date}. Red markers: inside your mapped area. Orange: nearby.</p>
      <details className="panel change-evidence"><summary>Detection details and satellite sources</summary><h3>{current.detections.length?(period==='recent'?'Recent thermal observations':'Historical thermal observations'):'No detections reported in this area'}</h3><p>{current.limits}</p>{current.detections.map((event,index)=><div className="report-row" key={index}><div><h3>{event.sensor} · {event.scope==='inside'?'Inside mapped area':'Nearby'}</h3><p>{stamp(event.observed_at)} · {event.latitude.toFixed(5)}, {event.longitude.toFixed(5)} · {event.confidence} confidence · {event.frp_mw} MW radiant power</p></div></div>)}<h3>Feed evidence</h3>{current.sources.map(source=><p key={source.sensor}>{source.sensor}: {source.regional_rows.toLocaleString()} regional records checked. Latest regional detection: {source.latest_observation?stamp(source.latest_observation):'No records in feed'}.</p>)}{current.errors.length>0&&<p>Unavailable source: {current.errors.map(e=>e.sensor).join(', ')}.</p>}<div className="change-actions"><a className="button secondary" href={`https://firms.modaps.eosdis.nasa.gov/map/#d:7days;@${((current.boundary.bbox[0]+current.boundary.bbox[2])/2).toFixed(5)},${((current.boundary.bbox[1]+current.boundary.bbox[3])/2).toFixed(5)},14z`} target="_blank" rel="noreferrer">Open current NASA fire map ↗</a></div><p>{current.attribution}</p><p>Mapped area: compartment 279 in Joga. No satellite signal does not prove that no fire occurred.</p></details>
      {period!=='recent'&&<p className="change-map-note">Historical satellite signals, not confirmed fire incidents. The 2026 archive is partial.</p>}
    </>}
  </section>;
}
