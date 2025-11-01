package in.mgnrega.controller;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.*;
import java.util.*;
@RestController
@RequestMapping("/api/v1")
public class DistrictController {
    @Autowired
    private JdbcTemplate jdbc;

    @GetMapping("/districts")
    public List<Map<String,Object>> list(){
        return jdbc.queryForList("SELECT id, district_code, name_en, name_kn FROM districts ORDER BY name_en");
    }

    @GetMapping("/districts/{id}/summary")
    public Map<String,Object> summary(@PathVariable int id, @RequestParam(defaultValue="12") int months){
        String sql = "SELECT year, month, jobs_created, families_benefited, avg_days, timely_payments_pct FROM metrics_monthly WHERE district_id = ? ORDER BY year DESC, month DESC LIMIT ?";
        List<Map<String,Object>> rows = jdbc.queryForList(sql, id, months);
        double avgTimely = rows.stream().mapToDouble(r -> r.get("timely_payments_pct")==null?0:((Number)r.get("timely_payments_pct")).doubleValue()).average().orElse(0);
        String badge = avgTimely >= 85 ? "green" : (avgTimely >= 65 ? "yellow" : "red");
        Map<String,Object> resp = new HashMap<>();
        resp.put("district_id", id);
        resp.put("badge", badge);
        resp.put("trend", rows);
        resp.put("last_updated", jdbc.queryForObject("SELECT MAX(fetched_at) FROM metrics_monthly WHERE district_id = ?", Date.class, id));
        return resp;
    }

    @GetMapping("/detect")
    public Map<String,Object> detect(@RequestParam double lat, @RequestParam double lon){
        String sql = "SELECT id, name_kn FROM districts WHERE ST_Contains(geom, ST_SetSRID(ST_Point(? , ?),4326)) LIMIT 1";
        Map<String,Object> rec = jdbc.queryForMap(sql, lon, lat);
        return rec;
    }
}
