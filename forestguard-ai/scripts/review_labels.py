"""Build an offline proposal form and validate its export; never approve training splits."""
import argparse
import hashlib
import html
import json
import math
import tempfile
from pathlib import Path

from audit_labels import audit

ROOT=Path(__file__).resolve().parents[1]
PACK=ROOT/'data/labels/compartment_279_blind_review_v1'
TEMPLATE=PACK/'reviewer_cases.geojson'
EDITABLE={'class','reviewer','review_date','confidence','uncertainty_notes','review_status',
          'height_evidence','canopy_cover_percent','qualifying_stand_area_ha','forest_use_evidence','origin'}


def validate(document,template=TEMPLATE):
    template=Path(template)
    original=json.loads(template.read_bytes())
    if document.get('review_template_sha256')!=hashlib.sha256(template.read_bytes()).hexdigest():
        raise ValueError('Export does not match the preserved review template.')
    if len(document.get('features',[]))!=len(original['features']):raise ValueError('Review case count changed.')
    for proposed,source in zip(document['features'],original['features']):
        p=proposed['properties'];q=source['properties']
        if proposed.get('type')!=source['type'] or proposed['geometry']!=source['geometry'] or set(p)!=set(q) or any(p[k]!=q[k] for k in set(q)-EDITABLE):
            raise ValueError('Case geometry, source/date, independence or split was changed.')
        if p['review_status'] not in {'unreviewed','reviewed'}:raise ValueError('Invalid proposal review status.')
        if p['review_status']=='unreviewed' and p!=q:raise ValueError('Changed cases need an explicit reviewer record.')
        if p['review_status']=='reviewed':
            if not isinstance(p['uncertainty_notes'],str) or not p['uncertainty_notes'].strip():
                raise ValueError('Record the evidence assessment and uncertainty.')
            if p['origin'] not in {'unknown','natural_forest','forestry_plantation','agricultural_orchard_or_crop','scrub','other'}:
                raise ValueError('Invalid proposed land-use origin.')
            if p['class']=='forest':
                for key,minimum,maximum in [('canopy_cover_percent',10,100),('qualifying_stand_area_ha',.5,float('inf'))]:
                    value=p[key]
                    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or not minimum<value<=maximum:
                        raise ValueError('Forest proposal needs supported canopy above 10% and stand extent above 0.5 ha.')
                if any(not isinstance(p[k],str) or not p[k].strip() for k in ['height_evidence','forest_use_evidence']):
                    raise ValueError('Forest proposal needs height/height-potential and forest-use evidence citations.')
                if p['origin'] in {'agricultural_orchard_or_crop','scrub'}:
                    raise ValueError('Agricultural crops/orchards and scrub cannot be proposed as forest.')
    result=audit(document)
    assert not result['training_eligible'] and not result['split_checks_complete']
    return dict(result,proposal_only=True,source_truth_verified=False)


def build(output,pack=PACK):
    output=Path(output)
    if output.exists():raise ValueError('Keep the existing review form; choose a new output folder.')
    pack=Path(pack);template=pack/'reviewer_cases.geojson'
    document=json.loads(template.read_bytes())
    document['review_template_sha256']=hashlib.sha256(template.read_bytes()).hexdigest()
    validate(document,template)
    cards=[]
    for index,feature in enumerate(document['features']):
        p=feature['properties']
        cards.append(f'''<fieldset data-case="{index}"><legend>Case {index+1}: {html.escape(p['label_id'])}</legend>
<p>Observation: {html.escape(p['observation_date'])}. Reference: {html.escape(p['reference_date'])}. Inspect the matching numbered images above.</p>
<label><input type="checkbox" name="reviewed"> I have reviewed this case</label>
<label>Proposed class <select name="class"><option value="unknown">Unknown / insufficient evidence</option><option value="non_forest">Non-forest</option><option value="forest">Forest</option></select></label>
<label>Confidence <select name="confidence"><option value="">Choose after review</option><option>low</option><option>medium</option><option>high</option></select></label>
<label>Land use / origin <select name="origin"><option value="unknown">Unknown</option><option value="natural_forest">Natural forest</option><option value="forestry_plantation">Forestry plantation</option><option value="agricultural_orchard_or_crop">Agricultural orchard / crop</option><option value="scrub">Scrub</option><option value="other">Other</option></select></label>
<label>Evidence assessment and uncertainty <textarea name="uncertainty_notes" rows="3"></textarea></label>
<label>Supported canopy cover (%) <input name="canopy_cover_percent" type="number" min="0" max="100" step="any"></label>
<label>Supported stand extent (ha) <input name="qualifying_stand_area_ha" type="number" min="0" step="any"></label>
<label>Height above 5 m, or height potential: cite dated evidence and method <textarea name="height_evidence" rows="2"></textarea></label>
<label>Forest rather than agricultural use: cite evidence and method <textarea name="forest_use_evidence" rows="2"></textarea></label></fieldset>''')
    encoded=json.dumps(document).replace('<','\\u003c')
    form='''<section id="review-form"><h2>Record your review</h2><p>These are proposed interpretations, not approved ground truth. Source evidence, geometry and dates remain fixed. All evaluation splits stay unassigned and independence stays false pending assessment. No field photos are requested.</p>
<label>Reviewer name / identifier <input id="reviewer" autocomplete="off"></label><label>Actual review date <input id="review-date" type="date"></label>'''+''.join(cards)+'''
<button id="export-review" type="button">Download proposed labels</button><p id="review-status" role="status"></p></section>
<style>#review-form{max-width:950px;margin:30px auto}fieldset{margin:20px 0;padding:18px;border:1px solid #77998a}label{display:block;margin:12px 0}input:not([type=checkbox]),select,textarea{display:block;width:100%;box-sizing:border-box;padding:10px;font:inherit}button{padding:14px;background:#235540;color:white;border:0;font:inherit}#review-status{font-weight:bold}</style>
<script>
const template='''+encoded+''';
document.getElementById('export-review').addEventListener('click',()=>{
 const result=JSON.parse(JSON.stringify(template)),reviewer=document.getElementById('reviewer').value.trim(),date=document.getElementById('review-date').value;
 try{
  for(const card of document.querySelectorAll('[data-case]')){
   if(!card.querySelector('[name=reviewed]').checked)continue;
   if(!reviewer||!date)throw Error('Enter the actual reviewer and review date.');
   const p=result.features[Number(card.dataset.case)].properties;
   p.reviewer=reviewer;p.review_date=date;p.review_status='reviewed';
   for(const name of ['class','confidence','origin','uncertainty_notes','height_evidence','forest_use_evidence'])p[name]=card.querySelector('[name='+name+']').value.trim()||null;
   for(const name of ['canopy_cover_percent','qualifying_stand_area_ha']){const value=card.querySelector('[name='+name+']').value;p[name]=value===''?null:Number(value);}
   if(!p.confidence||!p.uncertainty_notes)throw Error('Each reviewed case needs confidence and an evidence/uncertainty assessment.');
   if(p.class==='forest'&&(!(p.canopy_cover_percent>10&&p.canopy_cover_percent<=100)||!(p.qualifying_stand_area_ha>.5)||!p.height_evidence||!p.forest_use_evidence||['agricultural_orchard_or_crop','scrub'].includes(p.origin)))throw Error('Forest proposals need supported canopy, stand extent, height/height-potential and forest-use evidence; exclude agricultural crops/orchards and scrub.');
  }
  const url=URL.createObjectURL(new Blob([JSON.stringify(result,null,2)+'\\n'],{type:'application/geo+json'}));
  const link=document.createElement('a');link.href=url;link.download='compartment_279_review_proposals.geojson';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  document.getElementById('review-status').textContent='Proposal exported. Originals unchanged; run the Python validation before accepting any review.';
 }catch(error){document.getElementById('review-status').textContent=error.message;}
});
</script>'''
    page=(pack/'comparison.html').read_text(encoding='utf-8').replace('</html>',form+'</html>')
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='review_form_',dir=output.parent) as temporary:
        folder=Path(temporary)
        (folder/'review.html').write_text(page,encoding='utf-8')
        (folder/'reviewer_cases.geojson').write_text(json.dumps(document,indent=2)+'\n')
        folder.rename(output)
    return {'status':'PASS','cases':len(document['features']),'classes_generated':0,'training_approved':False}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['build','validate'])
    parser.add_argument('path',type=Path)
    parser.add_argument('--pack',type=Path,default=PACK,help='Preserved comparison pack containing reviewer_cases.geojson.')
    args=parser.parse_args()
    if args.action=='validate' and args.path.stat().st_size>2*1024**2:parser.error('Export exceeds 2 MiB.')
    try:
        result=build(args.path,args.pack) if args.action=='build' else validate(json.loads(args.path.read_bytes()),args.pack/'reviewer_cases.geojson')
        print(json.dumps(result,indent=2))
    except (ValueError,OSError,KeyError,TypeError) as error:parser.exit(1,f'Review failed: {error}\n')
