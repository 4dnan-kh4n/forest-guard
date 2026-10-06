"""Reproducible five-year synthetic forest/fire series. No satellite inputs."""
import json
from pathlib import Path

MONTHS=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

def build_history():
    series=[]; canopy_ha=132.0
    for offset in range(60):
        year,month=2021+(10+offset)//12,(10+offset)%12+1
        seasonal_loss=[.12,.14,.16,.18,.2,.19,.17,.2,.22,.18,.15,.13][month-1]
        fires=(year*7+month*5)%4 if 4<=month<=9 else 0
        loss=round(seasonal_loss+fires*.085+offset*.0007,2)
        canopy_ha=round(max(0,canopy_ha-loss),2)
        heat={4:44,5:72,6:78,7:56,8:38,9:31}.get(month,10)
        risk=min(95,heat+fires*5+(year%3)*2)
        series.append({'month':f'{year}-{month:02d}','label':f'{MONTHS[month-1]} {year}',
            'simulated_canopy_ha':canopy_ha,'simulated_loss_ha':loss,
            'simulated_fire_detections':fires,'simulated_fire_risk_pct':risk,
            'data_kind':'SIMULATED · NOT SATELLITE MEASUREMENTS'})
    return {'schema':'forestguard-synthetic-history-v1','data_kind':'synthetic_demo',
        'period_months':60,'region':'Fictional demonstration area · not Joga or any official forest boundary',
        'created_by':'ForestGuard monthly demo formula v1','inputs':'Deterministic seasonal example values; no satellite images, fire records, weather or field measurements.',
        'interpretation':'Illustration only. Never cite these simulated values as observed forest loss or fires.',
        'starting_simulated_canopy_ha':132.0,'ending_simulated_canopy_ha':canopy_ha,
        'months':series}

def main():
    root=Path(__file__).resolve().parents[1]
    target=root/'data/demo/forest_fire_history_demo_v1.json'; target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(build_history(),indent=2)+'\n',encoding='utf-8')
    print(f'Created {target.name}: 60 simulated months; no imagery, fire detections or geographic boundary.')

if __name__=='__main__': main()
