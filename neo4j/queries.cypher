// Common queries for a future Neo4j-backed deployment.
MATCH (source:Entity {id: $source_id})-[relationship*1..5]-(target:Entity {id: $target_id})
RETURN relationship;

MATCH (entity:Entity)-[relationship]-(neighbor:Entity)
RETURN entity.id AS entity_id, count(relationship) AS degree
ORDER BY degree DESC;

MATCH (entity:Entity)-[relationship]-(neighbor:Entity)
RETURN entity, relationship, neighbor
LIMIT 500;