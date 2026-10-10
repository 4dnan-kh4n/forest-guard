import React,{useEffect,useState} from 'react';
import {annualChange} from './annualChange';

export default function ForestHistoryWorkspace({api,initialYear=2026}){
  const [report,setReport]=useState(null),[year,setYear]=useState(initialYear),[error,setError]=useState('');
  useEffect(()=>{let active=true;api('/api/forest-history').then(r=>{if(active)setReport(r);}).catch(e=>{if(active)setError(e.message);});return()=>{active=false;};},[]);
  const row=report?.observations?.find(item=>item.year===year);
  const change=report?.comparisons?.find(item=>item.after_year===year);
  const summary=annualChange(change);
  return <section aria-label="Annual forest observations">
    <div className="change-actions year-selector">{[2022,2023,2024,2025,2026].map(value=><button key={value} className={`button ${year===value?'primary':'secondary'}`} aria-pressed={year===value} onClick={()=>{setYear(value);setError('');}}>{value}</button>)}</div>
    {error&&<p className="error-box" role="alert">{error}</p>}
    {!report?<p role="status">Opening your forest history…</p>:!row?<section className="panel change-evidence"><h3>{year} image unavailable</h3><p>ForestGuard is preparing this image.</p></section>:<>
      <section className={`panel annual-summary ${summary?.direction||'baseline'}`} aria-live="polite">
        <span>{summary?`${change.before_year} → ${year}`:`${year} · reference year`}</span>
        <h2>{summary?`Estimated tree cover ${summary.direction==='unchanged'?'has no net change':summary.direction}`:'Starting point for yearly comparisons'}</h2>
        {summary?<><strong>{summary.netHa.toFixed(2)} ha {summary.direction==='decreased'?'net decrease':summary.direction==='increased'?'net increase':'net change'}</strong>
          <p>Tree-covered share of the same compared area: <b>{summary.beforePercent.toFixed(1)}% → {summary.afterPercent.toFixed(1)}%</b>.</p>
          <div className="annual-change-breakdown"><span>Possible loss: <b>{change.suspected_tree_proxy_loss_ha.toFixed(2)} ha</b></span><span>Possible gain: <b>{change.suspected_tree_proxy_gain_ha.toFixed(2)} ha</b></span></div>
          <p>Satellite estimate — inspect areas of possible loss before confirming deforestation.</p></>:<p>{year} is the earliest saved year. Select a later year to see its change from the previous year.</p>}
      </section>
      <div className="change-period"><span>Satellite image: <strong>{row.date}</strong></span>{year===2026&&<span>2026 · through this image date</span>}</div>
      <section className="panel annual-image"><img src={`/api/forest-history/${year}/image`} alt={`Joga mapped forest area, satellite image acquired ${row.date}`} onError={()=>setError('This satellite image could not be loaded.')}/></section>
      <details className="panel change-evidence"><summary>Image details and how to read the result</summary>
        <p><b>Mapped area:</b> compartment 279 in Joga. The available boundary does not cover the entire beat.</p>
        <p><b>Clear image coverage:</b> {(row.coverage_fraction*100).toFixed(1)}% of this area.{change&&` The yearly comparison covers ${change.common_area_ha.toFixed(2)} ha (${change.common_coverage_percent.toFixed(1)}%) visible in both images.`}</p>
        <p>Tree cover means the area the model assigns to the tree class. It does not measure how densely trees grow. Cloudy and missing pixels are excluded.</p>
        <p>{report.limits}</p><p>Source: {row.scene_id}. {row.attribution}</p>
      </details>
    </>}
  </section>;
}
