CREATE TABLE "endpoints" (
    "id" serial primary key,
    "cloud" varchar,
    "region" varchar,
    "location" varchar,
    "protocol" varchar,
    "url" varchar
);

CREATE TABLE "pings" (
    "id" serial primary key,
    "date" timestamptz DEFAULT now(),
    "user" varchar,
    "type" varchar
);

CREATE TABLE "results" (
    "id" serial primary key,
    "ping_id" int4,
    "endpoint_id" int4,
    "duration" numeric
);

ALTER TABLE "results" ADD FOREIGN KEY ("endpoint_id") REFERENCES "endpoints"("id") ON DELETE CASCADE;
ALTER TABLE "results" ADD FOREIGN KEY ("ping_id") REFERENCES "pings"("id") ON DELETE CASCADE;

CREATE VIEW "all_pings" AS SELECT
    p.id,
    p.date,
    p.user,
    p.type,
    e.protocol,
    e.cloud,
    e.region,
    e.location,
    r.duration
   FROM results r
     JOIN endpoints e ON r.endpoint_id = e.id
     JOIN pings p ON r.ping_id = p.id
  ORDER BY p.date DESC;
