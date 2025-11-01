import React, {useEffect, useState} from 'react';
import DistrictSelector from './components/DistrictSelector';
import DistrictCard from './components/DistrictCard';
import {t} from './i18n';

export default function App(){
  const [district, setDistrict] = useState(null);
  const [banner, setBanner] = useState('');
  useEffect(()=>{
    if(!navigator.geolocation){
      setBanner(t('permissionDenied'));
      return;
    }
    setBanner(t('detecting'));
    navigator.geolocation.getCurrentPosition(async (pos)=>{
      try{
        const res = await fetch(`/api/v1/detect?lat=${pos.coords.latitude}&lon=${pos.coords.longitude}`);
        if(res.ok){ const data = await res.json(); setDistrict(data); setBanner(''); }
      }catch(e){
        setBanner(t('permissionDenied'));
      }
    }, (err)=>{
      setBanner(t('permissionDenied'));
    }, {timeout:10000});
  },[]);
  return (
    <div style={{padding:12,fontFamily:'sans-serif'}}>
      <h1>{t('app.title')}</h1>
      {banner && <div style={{background:'#fff3cd',padding:10,borderRadius:6}}>{banner}</div>}
      {!district && <DistrictSelector onSelect={d=>setDistrict(d)}/>}
      {district && <DistrictCard district={district} />}
    </div>
  );
}
