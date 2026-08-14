ALTER TABLE locations_sites
    DROP CONSTRAINT locations_sites_site_type_check;

ALTER TABLE locations_sites
    ADD CONSTRAINT locations_sites_site_type_check
    CHECK (site_type IN ('store','warehouse','processing_facility','property','office','farm'));
