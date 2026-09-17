// Optional scalable graph schema. The local prototype uses SQLite and NetworkX.
CREATE CONSTRAINT entity_id_unique IF NOT EXISTS
FOR (entity:Entity) REQUIRE entity.id IS UNIQUE;

CREATE INDEX entity_type_index IF NOT EXISTS
FOR (entity:Entity) ON (entity.type);

CREATE INDEX evidence_id_index IF NOT EXISTS
FOR (evidence:Evidence) ON (evidence.id);