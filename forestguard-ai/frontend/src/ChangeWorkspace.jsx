import React, {useEffect, useRef, useState} from 'react';
import L from 'leaflet';

const layers=[['change','All changes'],['loss','Loss only'],['gain','Gain only'],['coverage','Observable coverage']];
const legends=[['#d3ba90','Stable non-forest'],['#397d51','Stable forest'],['#cf4637','Suspected loss'],['#2295a4','Suspected gain']];
const hectare=n=>`${Number(n).toFixed(2)} ha`;

function ChangeMap({run,layer,title,fit}){
  const host=useRef(null),map=useRef(null),overlay=useRef(null);
  const [imageError,setImageError]=useState('');
  useEffect(()=>{
    map.current=L.map(host.current,{scrollWheelZoom:false,crs:L.CRS.Simple,minZoom:-4,maxZoom:6,attributionControl:false});
    const resize=new ResizeObserver(()=>map.current?.invalidateSize());resize.observe(host.current);
    return()=>{resize.disconnect();map.current.remove();map.current=null;};
  },[]);
  useEffect(()=>{
    const bounds=[[0,0],[run.height,run.width]];
    overlay.current?.remove();
    overlay.current=L.imageOverlay(`/api/change/runs/${run.run_id}/image/${layer}`,bounds,{className:'change-raster'}).addTo(map.current);
    setImageError('');
    const fail=()=>setImageError('Layer could not be loaded. Refresh the saved result.');
    overlay.current.on('error',fail);
    map.current.fitBounds(bounds,{padding:[15,15]});
  },[run.run_id,layer,fit]);
  return <article className="panel"><h3 className="change-map-title">{title}</h3><div ref={host} className="change-map" role="img" aria-label={title}/>{imageError&&<p className="error-box" role="alert">{imageError}</p>}<p className="change-map-note">20 m per pixel · fictional study grid · pan and zoom</p></article>;
}

export default function ChangeWorkspace({api,onRun}){
  const [status,setStatus]=useState(null),[report,setReport]=useState(null),[busy,setBusy]=useState(false),[error,setError]=useState(''),[layer,setLayer]=useState('change'),[fit,setFit]=useState(0);
  async function refresh(){setBusy(true);setError('');try{const result=await api('/api/change');setStatus(result);setReport(result.latest);}catch(e){setError(e.message);}finally{setBusy(false);}}
  useEffect(()=>{refresh();},[]);
  async function run(){setBusy(true);setError('');try{setReport(await api('/api/change/run',{method:'POST'}));onRun();}catch(e){setError(e.message);}finally{setBusy(false);}}
  return <section className="change-workspace" aria-label="Forest-cover change analysis">
    <div className="sim-banner"><b>SYNTHETIC SCENARIO</b><span>Generated class maps and dates · fictional study area.</span></div>
    <div className="change-intro"><div><h2>Compare cover. Keep the evidence.</h2><p>Detect suspected tree-cover loss and gain where both observations are clear.</p></div><div className="change-actions"><button className="button secondary" onClick={refresh} disabled={busy}>Refresh saved result</button><button className="button primary" onClick={run} disabled={busy||!status?.available}>{busy?'Processing…':'Run saved comparison'}</button></div></div>
    {error&&<div className="error-box" role="alert">{error}</div>}
    <p className="change-readiness">This comparison uses known synthetic classes. Real observation findings are shown separately when available.</p>
    {status&&!status.available&&<div className="error-box" role="alert">Comparison inputs are unavailable. Restore the saved fixture or run scripts/check_change.py locally.</div>}
    {!report?<div className="empty-state" role="status">{busy?'Opening saved comparison…':'Run the saved comparison to view its maps and reports.'}</div>:<>
      <div className="change-period"><span>Simulated dates: <strong>{report.before_date} → {report.after_date}</strong></span><span>Source: synthetic class maps</span></div>
      <div className="stats-grid">
        {[["Suspected loss",hectare(report.transition_area_ha.suspected_loss),'Synthetic forest → non-forest'],['Suspected gain',hectare(report.transition_area_ha.suspected_gain),'Synthetic non-forest → forest'],['Observable coverage',`${(report.common_coverage_fraction*100).toFixed(2)}%`,`${hectare(report.observable_area_ha)} valid on both dates`],['Study mask area',hectare(report.study_mask_area_ha),`${hectare(report.study_mask_area_ha-report.observable_area_ha)} unobservable`]].map(([label,value,note])=><article className="stat-card" key={label}><div className="stat-top">{label}</div><strong>{value}</strong><small>{note}</small></article>)}
      </div>
      <div className="change-tools"><div className="segments" role="group" aria-label="Change map layers">{layers.map(([id,name])=><button key={id} className={layer===id?'chosen':''} aria-pressed={layer===id} onClick={()=>setLayer(id)}>{name}</button>)}</div><button className="button secondary" onClick={()=>setFit(fit+1)}>Fit maps</button></div>
      <div className="change-maps"><ChangeMap run={report} layer="before" title={`Before · ${report.before_date}`} fit={fit}/><ChangeMap run={report} layer="after" title={`After · ${report.after_date}`} fit={fit}/><ChangeMap run={report} layer={layer} title={layers.find(([id])=>id===layer)[1]} fit={fit}/></div>
      <div className="change-legend">{legends.map(([color,text])=><span key={text}><i style={{background:color}}/>{text}</span>)}<span><i className="no-data"/>No data / outside study</span></div>
      <section className="panel change-evidence"><h3>Coverage and traceability</h3><p>Only {report.common_observable_pixels} of {report.study_mask_pixels} study pixels can be compared. Missing observations never count as loss or gain.</p><p>Net cover change over that common area: <strong>{hectare(report.net_cover_change_on_common_ha)}</strong>. Pixel-based hectares are not a surveyed boundary or tree-crown measurement.</p><dl><dt>Model</dt><dd>{report.model_version}</dd><dt>Study version</dt><dd>{report.study_area_version}</dd><dt>Definition</dt><dd>{report.forest_definition_version}</dd><dt>Run</dt><dd>{report.run_id}</dd></dl><p>Suspected cover transitions do not identify illegal logging, permanent deforestation or fire.</p><div className="change-actions">{[['csv','CSV report'],['html','HTML report'],['json','Evidence JSON'],['geotiff','Change GeoTIFF']].map(([format,label])=><a className="button secondary" key={format} href={`/api/change/runs/${report.run_id}/report/${format}`}>{label} ↓</a>)}</div></section>
    </>}
  </section>;
}
