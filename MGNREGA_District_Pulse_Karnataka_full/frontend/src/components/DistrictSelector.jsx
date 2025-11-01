import React, {useEffect, useState} from 'react';
import {t} from '../i18n';

export default function DistrictSelector({onSelect}){
  const [list,setList] = useState([]);
  useEffect(()=>{ fetch('/api/v1/districts').then(r=>r.json()).then(setList).catch(()=>setList([])); },[]);
  return (
    <div>
      <p>ದಯವಿಟ್ಟು ನಿಮ್ಮ ಜಿಲ್ಲೆ ಆಯ್ಕೆಮಾಡಿ:</p>
      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:8}}>
        {list.map(d=>(
          <button key={d.id} style={{padding:12,fontSize:16}} onClick={()=>onSelect(d)}>{d.name_kn || d.name_en}</button>
        ))}
      </div>
    </div>
  );
}
