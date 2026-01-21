"""
MAB AI Strategies - Shared Database Module
Handles Firestore, PostgreSQL, Redis, and Neo4j connections
"""

import os
import json
from typing import Any, Dict, List, Optional
from datetime import datetime
from contextlib import contextmanager

# Firestore
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

# PostgreSQL
import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import RealDictCursor, Json

# Redis
import redis

# Neo4j
from neo4j import GraphDatabase

# Configuration
FIRESTORE_DATABASE = os.getenv("FIRESTORE_DATABASE", "mab-production")
POSTGRES_CONN_STRING = os.getenv("POSTGRES_CONNECTION_STRING")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# Connection pools
_firestore_client = None
_postgres_pool = None
_redis_client = None
_neo4j_driver = None


def get_firestore_client() -> firestore.Client:
    """
    Get or create Firestore client (singleton)
    
    Returns:
        Firestore client instance
    """
    global _firestore_client
    
    if _firestore_client is None:
        _firestore_client = firestore.Client(database=FIRESTORE_DATABASE)
    
    return _firestore_client


def get_postgres_pool(min_conn: int = 2, max_conn: int = 10) -> ThreadedConnectionPool:
    """
    Get or create PostgreSQL connection pool
    
    Args:
        min_conn: Minimum connections in pool
        max_conn: Maximum connections in pool
        
    Returns:
        Connection pool instance
    """
    global _postgres_pool
    
    if _postgres_pool is None:
        _postgres_pool = ThreadedConnectionPool(
            min_conn, max_conn, POSTGRES_CONN_STRING
        )
    
    return _postgres_pool


@contextmanager
def get_postgres_connection():
    """
    Context manager for PostgreSQL connections
    
    Yields:
        Database connection from pool
    """
    pool = get_postgres_pool()
    conn = pool.getconn()
    
    try:
        yield conn
    finally:
        pool.putconn(conn)


def get_redis_client() -> redis.Redis:
    """
    Get or create Redis client
    
    Returns:
        Redis client instance
    """
    global _redis_client
    
    if _redis_client is None:
        _redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD if REDIS_PASSWORD else None,
            decode_responses=True
        )
    
    return _redis_client


def get_neo4j_driver() -> GraphDatabase.driver:
    """
    Get or create Neo4j driver
    
    Returns:
        Neo4j driver instance
    """
    global _neo4j_driver
    
    if _neo4j_driver is None:
        _neo4j_driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASSWORD)
        )
    
    return _neo4j_driver


class FirestoreRepository:
    """Base repository for Firestore operations"""
    
    def __init__(self, collection_name: str):
        self.db = get_firestore_client()
        self.collection = self.db.collection(collection_name)
    
    def create(self, document_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new document"""
        data['created_at'] = datetime.utcnow()
        data['updated_at'] = datetime.utcnow()
        
        doc_ref = self.collection.document(document_id)
        doc_ref.set(data)
        
        return {**data, 'id': document_id}
    
    def get(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID"""
        doc = self.collection.document(document_id).get()
        
        if not doc.exists:
            return None
        
        return {**doc.to_dict(), 'id': doc.id}
    
    def update(self, document_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing document"""
        data['updated_at'] = datetime.utcnow()
        
        doc_ref = self.collection.document(document_id)
        doc_ref.update(data)
        
        return self.get(document_id)
    
    def delete(self, document_id: str) -> None:
        """Delete a document"""
        self.collection.document(document_id).delete()
    
    def list(
        self,
        filters: List[tuple] = None,
        order_by: str = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List documents with optional filtering
        
        Args:
            filters: List of (field, operator, value) tuples
            order_by: Field to order by
            limit: Maximum results
            offset: Results to skip
            
        Returns:
            List of documents
        """
        query = self.collection
        
        # Apply filters
        if filters:
            for field, operator, value in filters:
                query = query.where(filter=FieldFilter(field, operator, value))
        
        # Apply ordering
        if order_by:
            direction = firestore.Query.DESCENDING if order_by.startswith('-') else firestore.Query.ASCENDING
            field = order_by.lstrip('-')
            query = query.order_by(field, direction=direction)
        
        # Apply pagination
        query = query.limit(limit).offset(offset)
        
        # Execute query
        docs = query.stream()
        
        return [{**doc.to_dict(), 'id': doc.id} for doc in docs]
    
    def batch_create(self, documents: List[Dict[str, Any]]) -> None:
        """Create multiple documents in a batch"""
        batch = self.db.batch()
        
        for doc_data in documents:
            doc_id = doc_data.pop('id', None)
            if not doc_id:
                doc_id = self.collection.document().id
            
            doc_data['created_at'] = datetime.utcnow()
            doc_data['updated_at'] = datetime.utcnow()
            
            doc_ref = self.collection.document(doc_id)
            batch.set(doc_ref, doc_data)
        
        batch.commit()


class PostgresRepository:
    """Base repository for PostgreSQL operations"""
    
    def __init__(self, table_name: str):
        self.table_name = table_name
    
    def execute_query(
        self,
        query: str,
        params: tuple = None,
        fetch_one: bool = False
    ) -> Any:
        """
        Execute a SQL query
        
        Args:
            query: SQL query string
            params: Query parameters
            fetch_one: Return single result
            
        Returns:
            Query results
        """
        with get_postgres_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                
                if query.strip().upper().startswith('SELECT'):
                    return cursor.fetchone() if fetch_one else cursor.fetchall()
                else:
                    conn.commit()
                    return cursor.rowcount
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a new record"""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        values = tuple(data.values())
        
        query = f"""
            INSERT INTO {self.table_name} ({columns})
            VALUES ({placeholders})
            RETURNING *
        """
        
        return self.execute_query(query, values, fetch_one=True)
    
    def get(self, record_id: int) -> Optional[Dict[str, Any]]:
        """Get a record by ID"""
        query = f"SELECT * FROM {self.table_name} WHERE id = %s"
        return self.execute_query(query, (record_id,), fetch_one=True)
    
    def update(self, record_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a record"""
        set_clause = ', '.join([f"{k} = %s" for k in data.keys()])
        values = tuple(data.values()) + (record_id,)
        
        query = f"""
            UPDATE {self.table_name}
            SET {set_clause}, updated_at = NOW()
            WHERE id = %s
            RETURNING *
        """
        
        return self.execute_query(query, values, fetch_one=True)
    
    def delete(self, record_id: int) -> int:
        """Delete a record"""
        query = f"DELETE FROM {self.table_name} WHERE id = %s"
        return self.execute_query(query, (record_id,))
    
    def list(
        self,
        filters: Dict[str, Any] = None,
        order_by: str = "id",
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List records with filtering"""
        where_clause = ""
        params = []
        
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(f"{key} = %s")
                params.append(value)
            where_clause = "WHERE " + " AND ".join(conditions)
        
        params.extend([limit, offset])
        
        query = f"""
            SELECT * FROM {self.table_name}
            {where_clause}
            ORDER BY {order_by}
            LIMIT %s OFFSET %s
        """
        
        return self.execute_query(query, tuple(params))


class CacheManager:
    """Manage Redis caching operations"""
    
    def __init__(self, prefix: str = "mab"):
        self.redis = get_redis_client()
        self.prefix = prefix
    
    def _make_key(self, key: str) -> str:
        """Create prefixed cache key"""
        return f"{self.prefix}:{key}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        value = self.redis.get(self._make_key(key))
        
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        
        return None
    
    def set(
        self,
        key: str,
        value: Any,
        expire_seconds: int = 3600
    ) -> bool:
        """Set cached value with expiration"""
        if not isinstance(value, str):
            value = json.dumps(value)
        
        return self.redis.setex(
            self._make_key(key),
            expire_seconds,
            value
        )
    
    def delete(self, key: str) -> bool:
        """Delete cached value"""
        return self.redis.delete(self._make_key(key)) > 0
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        return self.redis.exists(self._make_key(key)) > 0
    
    def increment(self, key: str, amount: int = 1) -> int:
        """Increment a counter"""
        return self.redis.incrby(self._make_key(key), amount)
    
    def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple keys at once"""
        prefixed_keys = [self._make_key(k) for k in keys]
        values = self.redis.mget(prefixed_keys)
        
        result = {}
        for key, value in zip(keys, values):
            if value:
                try:
                    result[key] = json.loads(value)
                except json.JSONDecodeError:
                    result[key] = value
        
        return result


class GraphRepository:
    """Base repository for Neo4j graph operations"""
    
    def __init__(self):
        self.driver = get_neo4j_driver()
    
    def execute_query(self, query: str, parameters: Dict[str, Any] = None):
        """Execute a Cypher query"""
        with self.driver.session() as session:
            return session.run(query, parameters).data()
    
    def create_node(
        self,
        label: str,
        properties: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a node"""
        query = f"""
            CREATE (n:{label} $properties)
            RETURN n
        """
        
        result = self.execute_query(query, {"properties": properties})
        return result[0]['n'] if result else None
    
    def create_relationship(
        self,
        from_id: str,
        to_id: str,
        relationship_type: str,
        properties: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create a relationship between nodes"""
        props_str = ", properties: $properties" if properties else ""
        
        query = f"""
            MATCH (a), (b)
            WHERE id(a) = $from_id AND id(b) = $to_id
            CREATE (a)-[r:{relationship_type} {{{props_str}}}]->(b)
            RETURN r
        """
        
        params = {"from_id": from_id, "to_id": to_id}
        if properties:
            params["properties"] = properties
        
        result = self.execute_query(query, params)
        return result[0]['r'] if result else None
    
    def find_path(
        self,
        from_id: str,
        to_id: str,
        max_depth: int = 5
    ) -> List[Dict[str, Any]]:
        """Find shortest path between nodes"""
        query = f"""
            MATCH path = shortestPath(
                (a)-[*..{max_depth}]-(b)
            )
            WHERE id(a) = $from_id AND id(b) = $to_id
            RETURN path
        """
        
        return self.execute_query(query, {"from_id": from_id, "to_id": to_id})


# Cleanup functions
def close_all_connections():
    """Close all database connections (call on shutdown)"""
    global _postgres_pool, _neo4j_driver
    
    if _postgres_pool:
        _postgres_pool.closeall()
    
    if _neo4j_driver:
        _neo4j_driver.close()
