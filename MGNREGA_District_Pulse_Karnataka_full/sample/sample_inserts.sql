-- Sample district entry (replace geom with real GeoJSON conversion)
INSERT INTO districts (state_code,district_code,name_en,name_kn) VALUES ('KA','KA_BLRR','Bengaluru Rural','ಬೆಂಗಳೂರು ಗ್ರಾಮೀಣ');
-- Sample metric row (replace district_id appropriately)
INSERT INTO metrics_monthly (district_id,year,month,jobs_created,families_benefited,avg_days,timely_payments_pct,raw,source_ts) VALUES (1,2025,10,12000,5400,12.3,92.0,'{}',now());
