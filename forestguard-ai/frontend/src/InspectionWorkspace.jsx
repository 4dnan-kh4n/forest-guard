import React,{useEffect,useState} from 'react';
import {inspectionItems,inspectionCsv} from './inspectionPlan';

export default function InspectionWorkspace({api,onOpenYear,onOpenFire}) {
  const [items,setItems]=useState(null),[selected,setSelected]=useState([]),[fire,setFire]=useState(null),[error,setError]=useState('');
  useEffect(()=>{let active=true;
    api('/api/forest-history').then(report=>{if(active){const next=inspectionItems(report);setItems(next);setSelected(next.map(item=>item.id));}}).catch(e=>{if(active)setError(e.message);});
    api('/api/fire').then(report=>{if(active)setFire(report);}).catch(()=>{if(active)setFire({available:false});});
    return()=>{active=false;};
  },[]);
  function download(){
    const url=URL.createObjectURL(new Blob([inspectionCsv(items.filter(item=>selected.includes(item.id)))],{type:'text/csv;charset=utf-8'}));
    const link=document.createElement('a');link.href=url;link.download='joga-inspection-plan.csv';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  }
  return <section aria-label="Inspection planning">
    <section className="panel change-evidence inspection-fire"><h2>Before your next visit</h2>
      <p>{fire?.available?`${fire.inside_count} satellite fire signals in your mapped area; ${fire.nearby_count} nearby, in the saved seven-day feed.`:fire?'The fire feed needs an update.':'Checking saved fire observations…'}</p>
      {fire?.available&&<p>Last retrieved: {new Date(fire.fetched_at).toLocaleString('en-IN',{timeZone:'Asia/Kolkata'})} IST{fire.status==='partial'?' · one satellite source unavailable':''}.</p>}
      <button className="button secondary" onClick={onOpenFire}>Check current fire feed</button>
    </section>
    <div className="change-intro"><div><h2>Changes to review</h2><p>Largest possible loss first. Review these historical satellite estimates before planning a visit.</p></div>
      <button className="button primary" disabled={!items||!selected.length} onClick={download}>Download checklist ({selected.length})</button></div>
    {error&&<p className="error-box" role="alert">{error}</p>}
    {!items&&!error?<p role="status">Preparing your inspection plan…</p>:items?.length===0?<p>No possible-loss comparisons are available for review.</p>:items?.map((item,index)=><article className="panel change-evidence inspection-item" key={item.id}>
      <div className="inspection-heading"><h3>{index+1}. {item.title}</h3><label><input type="checkbox" checked={selected.includes(item.id)} onChange={e=>setSelected(ids=>e.target.checked?[...ids,item.id]:ids.filter(id=>id!==item.id))}/> Include in checklist</label></div>
      <p><b>{item.loss.toFixed(2)} ha</b> possible loss · <b>{item.gain.toFixed(2)} ha</b> possible gain. Compared {item.area.toFixed(2)} ha with clear images on both dates.</p>
      <button className="button secondary" onClick={()=>onOpenYear(item.year)}>View {item.year} image and change</button>
    </article>)}
    <details className="panel change-evidence"><summary>How priorities are chosen</summary><p>Items are ordered by estimated loss area, not a validated risk score. No exact inspection locations or causes have been inferred. The mapped area is compartment 279 in Joga. Checklist selection lasts while this section is open; download it to keep your choices.</p></details>
  </section>;
}
