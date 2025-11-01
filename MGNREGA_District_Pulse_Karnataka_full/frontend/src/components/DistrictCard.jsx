import React, {useEffect, useState} from 'react';
import {t} from '../i18n';

export default function DistrictCard({district}){
  const [summary, setSummary] = useState(null);
  useEffect(()=>{
    fetch(`/api/v1/districts/${district.id}/summary`).then(r=>r.json()).then(setSummary).catch(()=>setSummary(null));
  },[district]);
  if(!summary) return <div>Loading...</div>;
  const latest = summary.trend && summary.trend[0];
  const avgDays = latest ? latest.avg_days : '-';
  const timely = latest ? latest.timely_payments_pct : '-';
  const play = () => {
    const text = `${district.name_kn} — ${avgDays} ಸರಾಸರಿ ಕೆಲಸದ ದಿನಗಳು. ಪಾವತಿಗಳು ಶೇಕಡಾ ${timely} ಸಮಯಕ್ಕೆ ಆಗಿವೆ.`;
    const u = new SpeechSynthesisUtterance(text);
    u.lang = 'kn-IN';
    speechSynthesis.speak(u);
  };
  return (
    <div style={{marginTop:12}}>
      <h2>{district.name_kn || district.name_en}</h2>
      <div style={{display:'flex',gap:12}}>
        <div style={{padding:12,background:'#f5f5f5',borderRadius:8}}>
          <h3>{t('jobs')}</h3>
          <div style={{fontSize:20}}>{latest ? latest.jobs_created : '-'}</div>
        </div>
        <div style={{padding:12,background:'#f5f5f5',borderRadius:8}}>
          <h3>{t('families')}</h3>
          <div style={{fontSize:20}}>{latest ? latest.families_benefited : '-'}</div>
        </div>
      </div>
      <div style={{marginTop:10}}>
        <p>{t('avgDays')}: {avgDays}</p>
        <p>{t('timely')}: {timely}%</p>
        <button onClick={play} style={{padding:10,marginTop:8}}>{t('playSummary')}</button>
      </div>
    </div>
  );
}
