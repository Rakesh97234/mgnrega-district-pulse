#!/usr/bin/env python3
import os, time, json, logging, requests
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
from urllib.parse import urlencode

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mgnrega-etl")

PG_HOST = os.getenv('PG_HOST','postgres')
PG_DB = os.getenv('PG_DB','mgnrega')
PG_USER = os.getenv('PG_USER','postgres')
PG_PASS = os.getenv('PG_PASS','postgres')
API_BASE = os.getenv('MGNREGA_API_BASE','https://api.data.gov.in/resource/<RESOURCE_ID>')
API_KEY = os.getenv('MGNREGA_API_KEY','')
PER_PAGE = int(os.getenv('ETL_PER_PAGE','100'))

def get_conn():
    return psycopg2.connect(host=PG_HOST, dbname=PG_DB, user=PG_USER, password=PG_PASS)

def fetch_page(offset):
    params = {'limit': PER_PAGE, 'offset': offset}
    if API_KEY:
        params['api-key'] = API_KEY
    url = API_BASE + "?" + urlencode(params)
    logger.info("Fetching %s", url)
    resp = requests.get(url, timeout=30)
    if resp.status_code == 429:
        raise Exception("Rate limited")
    resp.raise_for_status()
    return resp.json()

def parse_record(rec):
    district_code = rec.get('districtid') or rec.get('district_code') or rec.get('district')
    period = rec.get('month') or rec.get('period') or rec.get('year_month') or rec.get('date') or ''
    year = None; month = None
    try:
        if '-' in period:
            y,m = period.split('-')[:2]; year=int(y); month=int(m)
        elif len(period)>=6:
            year=int(period[:4]); month=int(period[4:6])
    except:
        pass
    jobs = int(rec.get('jobs_generated') or rec.get('jobs_created') or 0)
    families = int(rec.get('workers') or rec.get('families_benefited') or 0)
    avg_days = float(rec.get('avg_work_days') or rec.get('avg_days') or 0)
    timely = float(rec.get('timely_payment_pct') or rec.get('timely_payments_pct') or 0)
    women_pct = float(rec.get('women_pct') or rec.get('women_participation_pct') or 0)
    raw = json.dumps(rec)
    source_ts = datetime.utcnow()
    return {
        'district_code': district_code,
        'year': year,
        'month': month,
        'jobs': jobs,
        'families': families,
        'avg_days': avg_days,
        'timely': timely,
        'women_pct': women_pct,
        'raw': raw,
        'source_ts': source_ts
    }

def upsert_rows(conn, rows):
    if not rows:
        return 0
    with conn.cursor() as cur:
        values = [(r['district_code'], r['year'], r['month'], r['jobs'], r['families'], r['avg_days'], r['timely'], r['women_pct'], r['raw'], r['source_ts']) for r in rows]
        sql = """
        WITH v(district_code, year, month, jobs_created, families_benefited, avg_days, timely_payments_pct, women_participation_pct, raw, source_ts) AS (VALUES %s)
        INSERT INTO metrics_monthly (district_id, year, month, jobs_created, families_benefited, avg_days, timely_payments_pct, women_participation_pct, raw, source_ts)
        SELECT d.id, v.year, v.month, v.jobs_created, v.families_benefited, v.avg_days, v.timely_payments_pct, v.women_participation_pct, v.raw, v.source_ts
        FROM v LEFT JOIN districts d ON d.district_code = v.district_code
        ON CONFLICT (district_id, year, month) DO UPDATE
        SET jobs_created = EXCLUDED.jobs_created,
          families_benefited = EXCLUDED.families_benefited,
          avg_days = EXCLUDED.avg_days,
          timely_payments_pct = EXCLUDED.timely_payments_pct,
          women_participation_pct = EXCLUDED.women_participation_pct,
          raw = EXCLUDED.raw,
          source_ts = EXCLUDED.source_ts,
          fetched_at = NOW();
        """
        execute_values(cur, sql, values, template=None, page_size=100)
    conn.commit()
    return len(rows)

def log_run(conn, status, rows_processed, notes=''):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO etl_runs (status, rows_processed, notes) VALUES (%s,%s,%s)", (status, rows_processed, notes))
    conn.commit()

def run_once():
    conn = get_conn()
    offset = 0
    total_rows = 0
    try:
        while True:
            data = fetch_page(offset)
            records = data.get('records') or data.get('data') or []
            if not records:
                break
            parsed=[]
            for rec in records:
                try:
                    p = parse_record(rec)
                    if p['district_code'] and p['year'] and p['month']:
                        parsed.append(p)
                except Exception as e:
                    logger.exception("parse error: %s", e)
            count = upsert_rows(conn, parsed)
            total_rows += count
            if len(records) < int(os.getenv('ETL_PER_PAGE',100)):
                break
            offset += int(os.getenv('ETL_PER_PAGE',100))
        log_run(conn, 'success', total_rows, 'OK')
        logger.info("ETL success, rows: %d", total_rows)
    except Exception as e:
        logger.exception("ETL failed: %s", e)
        log_run(conn, 'failed', total_rows, str(e))
    finally:
        conn.close()

if __name__ == '__main__':
    run_once()
