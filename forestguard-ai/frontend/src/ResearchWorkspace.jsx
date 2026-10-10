import React,{useEffect,useRef,useState} from 'react';
import L from 'leaflet';

function ResearchMap({report,revision,fit}){
  const host=useRef(null),map=useRef(null),overlay=useRef(null);
  const [error,setError]=useState('');
  useEffect(()=>{
    map.current=L.map(host.current,{crs:L.CRS.Simple,minZoom:-4,maxZoom:6,attributionControl:false});
    const resize=new ResizeObserver(()=>map.current?.invalidateSize());resize.observe(host.current);
    return()=>{resize.disconnect();map.current.remove();map.current=null;};
  },[]);
  useEffect(()=>{
    const bounds=[[0,0],[report.shape[0],report.shape[1]]];
    overlay.current?.remove();setError('');
    overlay.current=L.imageOverlay(`/api/research/proxy/image?v=${revision}`,bounds,{className:'change-raster'}).addTo(map.current);
    overlay.current.on('error',()=>setError('Map could not be loaded. Refresh the saved result.'));
    map.current.fitBounds(bounds,{padding:[15,15]});
  },[report.model_version,revision,fit]);
  return <><div ref={host} className="change-map research-map" role="region" aria-label="Compartment 279 unapproved research tree-cover proxy; pan and zoom"/>{error&&<p className="error-box" role="alert">{error}</p>}</>;
}

export default function ResearchWorkspace({api}){
  const [report,setReport]=useState(null),[busy,setBusy]=useState(false),[error,setError]=useState(''),[revision,setRevision]=useState(0),[fit,setFit]=useState(0);
  async function refresh(){setBusy(true);setError('');setReport(null);try{setReport(await api('/api/research/proxy'));setRevision(n=>n+1);}catch(e){setError(e.message);}finally{setBusy(false);}}
  useEffect(()=>{refresh();},[]);
  return <section aria-label="Research tree-cover map">
    <div className="sim-banner"><b>RESEARCH TREE-COVER PROXY</b><span>Real satellite image · model trained on a historical map · independent forest accuracy not established</span></div>
    <div className="change-intro"><div><h2>Inspect our saved model's map.</h2><p>Compartment 279 research polygon, not the full Joga beat. Crops and shrubs may be mistaken for tree cover.</p></div><button className="button secondary" onClick={refresh} disabled={busy}>{busy?'Checking saved result…':'Refresh saved result'}</button></div>
    {error&&<div className="error-box" role="alert">{error}</div>}
    {!report?<p className="empty-state" role="status">{busy?'Opening the verified research map…':error?'Restore the verified output and retry.':'No result loaded.'}</p>:!report.available?<p className="empty-state">{report.detail}</p>:<>
      <div className="change-period"><span>Observation: <strong>{report.acquisition_date.slice(0,10)}</strong></span><span>Stored data · no online map service</span></div>
      <div className="stats-grid">{[['Usable coverage',`${(report.usable_fraction*100).toFixed(2)}%`,'Image coverage, not accuracy'],['Tree-cover proxy',report.class_pixels['1'].toLocaleString(),'Predicted pixels, not forest hectares'],['Other-cover proxy',report.class_pixels['0'].toLocaleString(),'Predicted pixels'],['Model status','Research only','Independent forest validation missing']].map(([title,value,note])=><article className="stat-card" key={title}><div className="stat-top">{title}</div><strong>{value}</strong><small>{note}</small></article>)}</div>
      <div className="change-tools"><span>20 m analysis grid · pan and zoom</span><button className="button secondary" onClick={()=>setFit(n=>n+1)}>Fit map</button></div>
      <section className="panel"><ResearchMap report={report} revision={revision} fit={fit}/></section>
      <div className="change-legend"><span><i style={{background:'#25b86e'}}/>Tree-cover proxy</span><span><i style={{background:'#e9a345'}}/>Other-cover proxy</span><span>Unobserved pixels have no predicted class.</span></div>
      <section className="panel change-evidence"><h3>Traceable research output</h3><p>This model learned from an older land-cover map. Its predictions do not establish natural forest, legal forest status or deforestation. Model vote values are uncalibrated and must not be read as accuracy or canopy percentage.</p><dl><dt>Model version</dt><dd>{report.model_version}</dd><dt>Dataset version</dt><dd>{report.dataset_version}</dd><dt>Observed pixels</dt><dd>{report.predicted_pixels.toLocaleString()} / {report.study_mask_pixels.toLocaleString()}</dd><dt>Source image</dt><dd>{report.scene_id}</dd></dl><div className="change-actions">{[['classes','Class GeoTIFF'],['votes','Model vote GeoTIFF'],['json','Evidence JSON'],['html','Offline HTML report']].map(([format,title])=><a className="button secondary" key={format} href={`/api/research/proxy/download/${format}`}>{title} ↓</a>)}</div></section>
    </>}
  </section>;
}
