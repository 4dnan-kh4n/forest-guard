import React, { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './style.css';
import Landing, {ForestLogo} from './Landing';
import FireWorkspace from './FireWorkspace';
import ForestHistoryWorkspace from './ForestHistoryWorkspace';
import InspectionWorkspace from './InspectionWorkspace';
import {startForestCursor} from './landingEffects';

const paths={leaf:'M12 21c-7-3-8-12 6-17 3 12-2 17-6 17Zm0 0c-2-5 0-9 4-13',grid:'M3 3h7v7H3zm11 0h7v7h-7zM3 14h7v7H3zm11 0h7v7h-7z',map:'m3 6 6-3 6 3 6-3v15l-6 3-6-3-6 3zm6-3v15m6-12v15',database:'M20 6c0 2-4 3-8 3S4 8 4 6s4-3 8-3 8 1 8 3ZM4 6v12c0 2 4 3 8 3s8-1 8-3V6M4 12c0 2 4 3 8 3s8-1 8-3',file:'M14 3H5v18h14V8zm0 0v5h5M8 12h8M8 16h6',arrow:'M5 12h14m-5-5 5 5-5 5',download:'M12 3v12m-5-5 5 5 5-5M4 17v4h16v-4',upload:'M12 16V4m-5 5 5-5 5 5M4 17v4h16v-4',check:'m5 12 4 4 10-10',search:'M10 18a8 8 0 1 0 0-16 8 8 0 0 0 0 16Zm6-2 6 6',focus:'M8 3H3v5m13-5h5v5M3 16v5h5m13-5v5h-5M12 8v8m-4-4h8',layers:'m12 3 10 6-10 6L2 9Zm-9 11 9 6 9-6',clock:'M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20Zm0-15v6l4 2'};
function Icon({name,size=20}) { return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d={paths[name]||paths.leaf}/></svg>; }
const percent=n=>`${((n||0)*100).toFixed(2)}%`;
const number=n=>Number(n||0).toLocaleString('en-IN');
const dateLabel=d=>new Date(d+'T12:00:00').toLocaleDateString('en-IN',{day:'numeric',month:'short',year:'numeric'});
async function api(url,options) { const response=await fetch(url,options); if(!response.headers.get('content-type')?.includes('application/json')) throw Error('The local ForestGuard API did not return JSON. Check that the local server is running.'); const result=await response.json(); if(response.status===401) window.dispatchEvent(new Event('forestguard-session-expired')); if(!response.ok) throw Error(result.detail||'Request failed'); return result; }

function MapPane({data,observation,layer,rings,fitSignal,index,maps,busy}) {
  const host=useRef(null),map=useRef(null),image=useRef(null),outline=useRef(null),fitted=useRef('');
  useEffect(()=>{
    const instance=L.map(host.current,{crs:L.CRS.Simple,scrollWheelZoom:false,minZoom:-2,maxZoom:5,zoomControl:false,attributionControl:false});
    L.control.zoom({position:'topleft'}).addTo(instance); map.current=instance; maps.current[index]=instance;
    instance.on('move',()=>{const peer=maps.current[1-index]; if(peer&&!busy.current){busy.current=true;peer.setView(instance.getCenter(),instance.getZoom(),{animate:false});busy.current=false;}});
    const resize=new ResizeObserver(()=>instance.invalidateSize());resize.observe(host.current);
    return ()=>{resize.disconnect();instance.off("move");maps.current[index]=null;instance.remove();map.current=null;};
  },[]);
  useEffect(()=>{
    if(!map.current||!data||!observation)return;
    const bounds=[[0,0],[data.height,data.width]];
    image.current?.remove();
    image.current=L.imageOverlay(`/api/datasets/${data.id}/${observation.id}/image/${layer}`,bounds).addTo(map.current);
    if(fitted.current!==data.id){map.current.fitBounds(bounds,{padding:[22,22]});fitted.current=data.id;}
    outline.current?.remove();
    outline.current=L.layerGroup(rings.map(ring=>L.polyline(ring.map(([x,y])=>[data.height-y,x]),{color:'#f3db82',weight:1.5,opacity:.95}))).addTo(map.current);
  },[data?.id,observation?.id,layer,rings]);
  useEffect(()=>{if(map.current&&data)map.current.fitBounds([[0,0],[data.height,data.width]],{padding:[22,22]});},[fitSignal]);
  return <div className="map-pane"><div ref={host} className="leaflet-host" role="img" aria-label={`${data.title}, ${observation.name}, ${layer} layer`}/><div className="map-date"><span className="map-dot"/>{dateLabel(observation.date)}{data.kind==='synthetic'&&<small>Simulated · {observation.name}</small>}</div><div className="map-scale">{data.resolution} m / pixel <span>Saved raster</span></div></div>;
}

function App({onLogout,hosted=false}){
  const [historyYear,setHistoryYear]=useState(2026);
  const [analysis,setAnalysis]=useState(null),[scenario]=useState(false);
  const [datasets,setDatasets]=useState([]),[selected,setSelected]=useState('compartment-279'),[section,setSection]=useState('Forest history'),[viewId,setViewId]=useState('1');
  const [layer,setLayer]=useState('imagery'),[compare,setCompare]=useState(false),[rings,setRings]=useState([]),[showBoundary,setShowBoundary]=useState(true),[menuOpen,setMenuOpen]=useState(false);
  const [activity,setActivity]=useState([]),[loading,setLoading]=useState(true),[checking,setChecking]=useState(false),[toast,setToast]=useState(''),[error,setError]=useState(''),[search,setSearch]=useState(''),[fit,setFit]=useState(0);
  const maps=useRef([]),syncBusy=useRef(false);
  const scopedDatasets=datasets.filter(d=>d.id===(scenario?'demo':'compartment-279'));
  const data=scopedDatasets.find(d=>d.id===selected)||scopedDatasets[0]; const observation=data?.views.find(v=>v.id===viewId)||data?.views[0];
  const isDemo=data?.kind==='synthetic'; const hasPair=!isDemo&&data?.views.length>1;
  async function refresh(){setDatasets((await api('/api/datasets')).filter(d=>d.id==='compartment-279'));setActivity(await api('/api/activity'));}
  useEffect(()=>{refresh().catch(e=>setError(e.message)).finally(()=>setLoading(false));},[]);
  useEffect(()=>{if(!data)return;let active=true;setViewId(data.views[0].id);setLayer('imagery');setCompare(false);setShowBoundary(true);setRings([]);api(`/api/datasets/${data.id}/outline`).then(r=>{if(active)setRings(r.rings);}).catch(e=>{if(active)setError(e.message);});return()=>{active=false;};},[data?.id]);
  useEffect(()=>{if(!toast)return;const id=setTimeout(()=>setToast(''),4500);return()=>clearTimeout(id);},[toast]);
  async function check(){setChecking(true);setError('');try{const r=await api(`/api/datasets/${data.id}/validate`,{method:'POST'});setToast(r.detail);setActivity(await api('/api/activity'));}catch(e){setError(e.message);}finally{setChecking(false);}}
  async function analyze(){if(!data)return;if(section==='Forest & fire'){setSection('Map workspace');return;}setChecking(true);setError('');try{const r=await api(`/api/datasets/${data.id}/analyze`,{method:'POST'});setAnalysis({...r,dataset:data.id});setSection('Map workspace');setLayer(data.layers.includes('ndvi')?'ndvi':'classes');setToast('Saved imagery analyzed');setActivity(await api('/api/activity'));}catch(e){setError(e.message);}finally{setChecking(false);}}
  useEffect(()=>{if(!data)return;let active=true;setAnalysis(null);api(`/api/datasets/${data.id}/analyze`,{method:'POST'}).then(r=>{if(active)setAnalysis({...r,dataset:data.id});}).catch(e=>{if(active)setError(e.message);});return()=>{active=false;};},[data?.id]);
  const sectionTitle={Overview:'Forest overview','Map workspace':'Satellite images','Research map':'Research map',Reports:'Reports','Forest history':'Forest change','Forest & fire':'Monthly scenario','Change detection':'Change detection'}[section]||section;
  const visible=scopedDatasets.filter(d=>(d.title+' '+d.subtitle).toLowerCase().includes(search.toLowerCase()));
  const relevantActivity=activity.filter(a=>a.dataset===(scenario?'demo':'compartment-279'));
  const compareView=data?.views.find(v=>v.id!==observation?.id);
  return <div className="app-shell">
    <aside className="sidebar"><div className="officer-brand-row"><div className="brand"><div className="brand-mark"><ForestLogo size={30}/></div><div>ForestGuard<span>AI MONITORING WORKSPACE</span></div></div><button className="officer-menu-toggle" aria-controls="officer-navigation" aria-expanded={menuOpen} onClick={()=>setMenuOpen(!menuOpen)}>{menuOpen?'Close menu':'Menu'} <span aria-hidden="true">{menuOpen?'×':'☰'}</span></button></div>
      <div className="workspace-label">WORKSPACE</div><nav id="officer-navigation" aria-label="Officer workspace" className={menuOpen?'is-open':''}>{([['Forest history','leaf'],['Fire detections','leaf'],['Inspection plan','check'],['Reports','file']]).map(([name,icon])=><button key={name} onClick={()=>{setSection(name);setMenuOpen(false);}} className={section===name?'active':''}><Icon name={icon}/><span>{name==='Overview'?'Forest overview':name==='Map workspace'?'Satellite images':name==='Forest history'?'Forest change':name}</span>{section===name&&<i/>}</button>)}</nav>
      <div className="sidebar-footer"><div className="avatar">FG</div><div>Joga<small>Forest officer</small></div></div>
    </aside>
    <div className="main-shell"><header className="topbar"><div className="breadcrumb">Workspace <span>/</span> <strong>{sectionTitle}</strong></div><div className="topbar-right"><span className="officer-label">Forest officer</span><button className="button secondary" onClick={onLogout}>Logout</button></div></header>
    <main><div className="page-heading"><div><div className="eyebrow">FORESTGUARD AI</div><h1>{sectionTitle}</h1><p>{section==='Change detection'?'Compare dated class maps, inspect usable coverage and export the evidence.':section==='Overview'?(scenario?'Synthetic scenario · generated images and known classes.':'Joga · your saved forest images.'):section==='Forest & fire'?'Generated monthly history for the synthetic scenario.':section==='Map workspace'?'View a saved satellite image and compare dates.':section==='Inspection plan'?'Joga · prepare a visit checklist from saved evidence.':section==='Fire detections'?'Monitor recent satellite thermal observations and inspect their timestamps.':section==='Forest history'?'Joga · yearly changes and the satellite images behind them.':section==='Estimated change'?'Compare real December images and inspect estimated tree-cover transitions.':section==='Research map'?'Inspect our stored tree-cover proxy and download its evidence.':section==='Datasets'?'Your saved imagery and simulated inputs.':'Export traceable, shareable snapshots of your saved data.'}</p></div>{section==='Map workspace'&&<button className="button secondary" onClick={analyze} disabled={checking}><Icon name={checking?"clock":"layers"}/> {checking?"Analyzing saved images…":section==='Forest & fire'?'Open satellite map':'Analyze saved images'}</button>}</div>
    {error&&<div className="error-box" role="alert">{error}<button aria-label="Dismiss error" onClick={()=>setError('')}>×</button></div>}
    {section==='Fire detections'?<FireWorkspace api={api}/>:section==='Forest history'?<ForestHistoryWorkspace api={api} initialYear={historyYear}/>:section==='Inspection plan'?<InspectionWorkspace api={api} onOpenYear={year=>{setHistoryYear(year);setSection('Forest history');window.scrollTo(0,0);}} onOpenFire={()=>{setSection('Fire detections');window.scrollTo(0,0);}}/>:loading?<div className="empty-state">Opening saved forest records…</div>:!data?<div className="empty-state"><Icon name="database" size={38}/><h2>Your workspace is ready.</h2><p>Joga satellite images are currently unavailable. The project team must restore the prepared data.</p><button className="button primary" onClick={()=>{setLoading(true);setError('');refresh().catch(e=>setError(e.message)).finally(()=>setLoading(false));}}>Retry saved observations</button></div>:<>
      {(section==='Overview'||section==='Map workspace')&&<>
        <div className={`workspace-grid ${section==='Map workspace'?'expanded':''}`}><section className="panel map-panel"><div className="panel-heading"><div><h2>Observation explorer</h2><span>Pan, zoom and compare stored layers</span></div><button className="icon-button" title="Fit image" aria-label="Fit image" onClick={()=>setFit(fit+1)}><Icon name="focus"/></button></div>
          <div className="map-toolbar"><div className="segments">{data.layers.filter(l=>l!=='ndvi').map(l=><button key={l} className={layer===l?'chosen':''} onClick={()=>setLayer(l)}>{l==='imagery'?'True colour':l==='classes'?'Simulated tree cover':l==='ndvi'?'Vegetation signal':data.common_mask?'Common clear pixels':'Clear pixels'}</button>)}</div><label className="compare-toggle"><input type="checkbox" checked={compare} disabled={data.views.length<2} onChange={e=>setCompare(e.target.checked)}/>Compare</label></div>
          <div className={`maps ${compare?'dual':''}`}><MapPane key={data.id+'-main'} data={data} observation={observation} layer={layer} rings={showBoundary?rings:[]} fitSignal={fit} index={0} maps={maps} busy={syncBusy}/>{compare&&compareView&&<MapPane key={data.id+'-compare'} data={data} observation={compareView} layer={layer} rings={showBoundary?rings:[]} fitSignal={fit} index={1} maps={maps} busy={syncBusy}/>}</div>
          <div className="map-footer"><label><input type="checkbox" checked={showBoundary} onChange={e=>setShowBoundary(e.target.checked)}/><span className="legend-outline"/>{isDemo?'Fictional study grid':data.id==='compartment-279'?'Mapped forest area':data.id==='sentinel'?'Candidate outline':'Outline'}</label><a href={`/api/datasets/${data.id}/report/html`}>Download report ↗</a></div>
          <div className="date-strip">{data.views.map(v=><button key={v.id} className={observation.id===v.id?'selected':''} onClick={()=>setViewId(v.id)}><span>{isDemo?v.name:dateLabel(v.date)}</span><small>{isDemo?'Simulated '+dateLabel(v.date):'Satellite image · leaf-growth signals'}</small></button>)}</div>
        </section></div>
      </>}
      {section==='Datasets'&&<><div className="library-toolbar"><div className="search-box"><Icon name="search"/><input aria-label="Search datasets" placeholder="Search your datasets…" value={search} onChange={e=>setSearch(e.target.value)}/></div><span>{visible.length} saved datasets</span></div><div className="dataset-cards">{visible.map(d=><article className="panel library-card" key={d.id}><div className="dataset-thumb" style={{backgroundImage:`url(/api/datasets/${d.id}/${d.views[0].id}/image/imagery)`}}><span className={`data-badge ${d.kind==='synthetic'?'demo':''}`}>{d.kind==='synthetic'?'Simulated data':'Real imagery'}</span></div><div><h2>{d.title}</h2><p>{d.subtitle}</p><dl><dt>Observations</dt><dd>{d.views.length}</dd><dt>Resolution</dt><dd>{d.resolution} m</dd><dt>Scope</dt><dd>{d.scope}</dd></dl><button className="button secondary full" onClick={()=>{setSelected(d.id);setSection('Map workspace');}}>Open workspace <Icon name="arrow" size={17}/></button></div></article>)}</div>{visible.length===0&&<p className="empty-state">No datasets match your search.</p>}</>}
      {section==='Reports'&&<section className="panel report-panel"><div className="report-row"><div><h3>Annual forest-change report</h3><p>2022–2026 · dated images and yearly comparisons</p></div><a className="button primary" href="/api/forest-history/report/pdf">Download PDF</a></div><div className="report-row"><div><h3>Satellite fire report</h3><p>Saved recent detections and observation time</p></div><a className="button primary" href="/api/fire/report/pdf">Download PDF</a></div><div className="panel-heading"><div><h2>Reports, ready to travel.</h2><span>Dated images, measured coverage and vegetation evidence prepared by ForestGuard.</span></div><Icon name="download"/></div>{scopedDatasets.map(d=><div className="report-row" key={d.id}><div className="report-icon"><Icon name="file"/></div><div><h3>Joga satellite report</h3><p>{d.views.length} observations · {d.kind==='synthetic'?'Simulated dates':'Acquisition dates'} · {d.resolution} m</p></div><a className="button secondary" href={`/api/datasets/${d.id}/report/csv`}>CSV <Icon name="download" size={16}/></a><a className="button primary" href={`/api/datasets/${d.id}/report/pdf`}>PDF report <Icon name="download" size={16}/></a></div>)}</section>}
      <footer className="page-footer"><span>ForestGuard AI · {isDemo?'Synthetic scenario':'Joga'}</span><span>{data.attribution}</span></footer>
    </>}
    </main></div>{toast&&<div className="toast" role="status"><Icon name="check"/>{toast}</div>}
  </div>;
}
function Stat({label,value,note,icon}){return <article className="stat-card"><div className="stat-top"><span>{label}</span><Icon name={icon}/></div><strong>{value}</strong><small>{note}</small></article>;}
function ForestGuard(){
  const [officer,setOfficer]=useState(null),cursor=useRef(null);
  useEffect(()=>startForestCursor(cursor.current),[]);
  useEffect(()=>{const expired=()=>setOfficer(null);window.addEventListener('forestguard-session-expired',expired);api('/api/session').then(result=>{if(result.authenticated)setOfficer(result);}).catch(()=>{});return()=>window.removeEventListener('forestguard-session-expired',expired);},[]);
  async function logout(){await api('/api/logout',{method:'POST'});window.location.reload();}
  return <><div ref={cursor} className="motion-cursor site-cursor page-cursor" aria-hidden="true"><div className="site-cursor-pill"/></div>{officer?<App onLogout={logout} hosted={officer.hosting==='vercel'}/>:<Landing onLogin={result=>{setOfficer(result);window.scrollTo(0,0);}}/>}</>;
}
createRoot(document.getElementById('root')).render(<ForestGuard/>);
