import re
import json
import time
import regex
import typing
import asyncio
import pydantic
import datetime
import traceback
import collections
import urdhva_base
import urdhva_base.settings
import urdhva_base.redispool
import urdhva_base.queryparams
import urdhva_base.utilities as utils
from sqlalchemy.pool import NullPool
from starlette.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.pool import NullPool

from sqlalchemy import (
    BigInteger,
    TIMESTAMP,
    DateTime,
    func,
    Identity,
    select,
    String,
    text
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    mapped_column,
    undefer
)


# Define Base class for declarative base
class Base(MappedAsDataclass, DeclarativeBase, dataclass_callable=pydantic.dataclasses.dataclass):
    class Config:
        orm_mode = True


# Define base model for Postgresql
class UrdhvaPostgresBase(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column("id", BigInteger, autoincrement=True, primary_key=True,
                                                     init=False, server_default=Identity(minvalue=1), unique=True)
    created_at: Mapped[typing.Optional[datetime.datetime]] = mapped_column("created_at", TIMESTAMP,
                                                                           server_default=func.now(), init=False)
    updated_at: Mapped[typing.Optional[datetime.datetime]] = mapped_column("updated_at", TIMESTAMP,
                                                                           server_default=func.now(),
                                                                           onupdate=func.now(), init=False)
    entity_id: Mapped[typing.Optional[str]] = mapped_column("entity_id", String, index=True)


class DatabaseManager:
    def __init__(self, database_url):
        self.engine = create_async_engine(database_url, poolclass=NullPool)
        self.async_session = async_sessionmaker(self.engine)

    async def get_session(self):
        return self.async_session()

    async def create_all(self):
        async with self.engine.begin() as conn:
            # Sorting all tables to make sure non-dependent one should configure first
            tables = Base.metadata.sorted_tables
            await conn.run_sync(Base.metadata.create_all, tables=tables)


manager = DatabaseManager(str(urdhva_base.settings.db_urls["postgres_async"][0]))


# --------------------------------------------------------------------------------------
# Create tables (once per application)
# --------------------------------------------------------------------------------------
async def create_tables():
    await manager.create_all()


# Define base model for Pydantic
class BasePostgresModel(pydantic.BaseModel):
    __tablename__ = ""

    @classmethod
    async def cleanup_session(cls, session):
        try:
            session.rollback()
        except Exception as e:
            print(e)
        try:
            session.close()
        except Exception as e:
            print(e)

    @classmethod
    async def _apply_acls(cls):
        ...

    @classmethod
    async def get_clause_conditions(cls, formated=False, extra_key_mapping=None, default_mapping=None):
        if not (urdhva_base.ctx.exists() and hasattr(cls.Config, "access_key_mapping")):
            return []

        rpt = urdhva_base.context.context.get('rpt', {})
        key_mapping = await cls.Config.access_key_mapping
        mapped_data = await cls._get_mapped_data(key_mapping)
        or_condition_keys = await cls._get_or_conditions(mapped_data)

        mapped_data = await cls._clean_mapped_data(mapped_data, or_condition_keys)
        mapped_data = await cls._remove_bu_if_sap_id_exists(mapped_data, rpt)

        return await cls._build_where_clause(mapped_data, rpt, or_condition_keys, formated, extra_key_mapping, default_mapping)

    @staticmethod
    async def _get_mapped_data(key_mapping):
        return {
            key.split(":")[0].strip(): key.split(":")[1].strip() if ":" in key else key.split(":")[0].strip()
            for key in key_mapping
        }

    @staticmethod
    async def _get_or_conditions(mapped_data):
        or_keys = {}
        duplicates = [item for item, count in collections.Counter(mapped_data.values()).items() if count > 1]
        for dup in duplicates:
            or_keys[dup] = [k for k, v in mapped_data.items() if v == dup]
        return or_keys

    @staticmethod
    async def _clean_mapped_data(mapped_data, or_condition_keys):
        for base_key, mapped_keys in or_condition_keys.items():
            for mapped_key in mapped_keys:
                if mapped_key != base_key:
                    mapped_data.pop(mapped_key, None)
        return mapped_data

    @staticmethod
    async def _remove_bu_if_sap_id_exists(mapped_data, rpt):
        if 'bu' in mapped_data and 'sap_id' in mapped_data:
            if rpt.get('bu') and rpt.get('sap_id'):
                mapped_data.pop('bu', None)
        return mapped_data

    @staticmethod
    async def _build_where_clause(mapped_data, rpt, or_condition_keys, formated, extra_key_mapping, default_mapping):
        where_clause = []
        for key, value in mapped_data.items():
            key = extra_key_mapping.get(key, key) if extra_key_mapping else key
            value = default_mapping.get(key, value) if default_mapping else value
            rpt_val = rpt.get(value)

            if rpt_val:
                clause = await BasePostgresModel._format_clause(key, rpt_val, or_condition_keys, formated)
                where_clause.append(clause)
        return where_clause

    @staticmethod
    async def _format_clause(key, val, or_conditions, formated):
        if isinstance(val, list):
            return await BasePostgresModel._format_list_clause(key, val, or_conditions, formated)
        return {'key': key, "cond": 'equals', "value": val} if formated else f"{key}='{val}'"

    @staticmethod
    async def _format_list_clause(key, val_list, or_conditions, formated):
        if len(val_list) == 1:
            single_val = val_list[0]
            if formated:
                return {'key': key, "cond": 'equals', "value": single_val}
            if key in or_conditions:
                return "(" + " OR ".join([f"{k}='{single_val}'" for k in or_conditions[key]]) + ")"
            return f"{key}='{single_val}'"
        else:
            if formated:
                return {'key': key, "cond": ' ', "value": val_list}
            if key in or_conditions:
                return f"({' OR '.join(f'{k} in {tuple(val_list)}' for k in or_conditions[key])})"
            return f"{key} in {tuple(val_list)}"

    @classmethod
    async def _get_entity_id(cls, entity_id=None):
        if urdhva_base.ctx.exists():
            return urdhva_base.ctx['entity_id']
        return entity_id

    @classmethod
    async def get(cls, row_id, entity_id=None, skip_secrets=False):
        """
        For Getting specific record
        :param row_id: record id
        :param entity_id: entity id
        :return: record if exists else null
        """
        session = await manager.get_session()
        result = await session.execute(
            select(cls.Config.schema_class).where(cls.Config.schema_class.id == int(row_id))
        )
        resp = result.scalars().first()
        await asyncio.shield(session.close())
        return resp

    @classmethod
    async def count(cls, params: urdhva_base.queryparams.QueryParams = None, entity_id=None, count_query=None):
        query = [f"select count('*') from {cls.__tablename__}"]

        if count_query and isinstance(count_query, list):
            query.extend(count_query[1:])
        else:
            query_params = await cls._build_entity_clause(entity_id)
            query_params += await cls._get_access_restrictions()
            query_params += await cls._get_standard_query()
            query_params += await cls.get_clause_conditions()
            if params and params.q:
                query_params.append(params.q)
            if query_params:
                query.append("where " + " AND ".join(query_params))

        session = await manager.get_session()
        total = await session.scalar(text(" ".join(query)))
        await asyncio.shield(session.close())
        return total

    @classmethod
    async def _build_entity_clause(cls, entity_id):
        if entity_id:
            return [f"{cls.__tablename__}.entity_id = '{entity_id}'"]
        return []

    @classmethod
    async def _get_access_restrictions(cls):
        if not (urdhva_base.ctx.exists() and urdhva_base.context.context.get('rpt', {})):
            return []

        rpt = urdhva_base.context.context['rpt']
        redis_client = await urdhva_base.redispool.get_redis_connection()
        key = f"access_restrictions_{urdhva_base.ctx['entity_id']}"
        if not await redis_client.hexists(key, rpt['email']):
            return []

        data = json.loads(await redis_client.hget(key, rpt['email']))
        if not data.get("organizations_permitted"):
            return []

        permitted_org = data['organizations_permitted'].split(",")
        permitted_org_str = f"('{permitted_org[0]}')" if len(permitted_org) == 1 else str(tuple(permitted_org))
        if cls.__tablename__ == "organization":
            return [f"id in {permitted_org_str}"]
        return [f"organization_id in {permitted_org_str}"]

    @classmethod
    async def _get_standard_query(cls):
        return [cls.Config.standard_query] if hasattr(cls.Config, 'standard_query') else []

    @classmethod
    async def update_by_query(cls, query, entity_id=None):
        session = await manager.get_session()
        try:
            result = await session.execute(text(query))
            print(f"Rows committed {result.rowcount}")
            await session.commit()
        except Exception as e:
            print(f"Exception while running update by query {e}")
            raise RuntimeError(f"Exception while running update by query {e}")
        finally:
            await asyncio.shield(session.close())

    @classmethod
    async def get_aggr_data(cls, query, limit=100, skip=0, skip_total=True):
        """
        @Description: For getting aggregated data, Join queries
        :param query: Query string to execute
        :param limit:
        :param skip:
        :return:
        """
        # Generating Postgres query from given query
        session = await manager.get_session()
        try:
            if limit:
                query_ = f"{query} LIMIT {limit} OFFSET {limit * skip}"
            else:
                query_ = f"{query}"
            if not query_.upper().startswith("WITH ") and not query_.upper().startswith("SELECT "):
                query_ = f"select {query_}"
            result = await session.execute(text(query_))
            resp = result.all()
            # Getting key columns from reults
            columns = [key for key in result.keys()]
            results = [{columns[index]: value for index, value in enumerate(row)} for row in resp]
            # Fetching total available records for the given query
            total = len(results)
            if not skip_total:
                try:
                    total = await session.scalar(text(f"select COUNT(*) FROM(SELECT {query}) AS subquery"))
                except Exception as e:
                    print(e)
            results_data = {"data": results, "count": len(results), "total": total}
            return results_data
        except Exception as e:
            print(f"Exception while running aggregation query {e}")
            raise RuntimeError(f"Exception while running aggregation query {e}")
        finally:
            await asyncio.shield(session.close())

    @classmethod
    async def get_all(cls, params=None, entity_id=None, resp_type="encoded", skip_secrets=False):

        ### uncomment the below lines to create tables in your database####
        # await manager.create_all()
        # return
        ### uncomment the below lines to create tables in your database####
        params = await cls._get_default_params(params)
        fields = await cls._prepare_fields(params)
        query = [f"select {','.join(fields)} from {cls.__tablename__}"]
        query_params = await cls._build_query_params(params, entity_id)
        search_conditions = await cls._build_search_conditions(params)
        if search_conditions:
            query_params.extend(search_conditions)
        if query_params:
            query.append("where " + " AND ".join(query_params))
        count_query = list(query)
        await cls._add_sorting(query, params)
        await cls._add_pagination(query, params)
        return await cls._execute_query(query, count_query, params, entity_id, resp_type)

    @staticmethod
    async def _get_default_params(params):
        return params or urdhva_base.queryparams.QueryParams(q="", fields='["*"]', skip=0, limit=100)

    @classmethod
    async def _prepare_fields(cls, params):
        fields = params.fields if params and params.fields else '["*"]'
        if isinstance(fields, str):
            fields = json.loads(fields)
        if fields and "*" not in fields and "id" not in fields:
            fields.append("id")
        return fields

    @classmethod
    async def _build_query_params(cls, params, entity_id):
        query_params = [f"{cls.__tablename__}.entity_id = '{entity_id}'"] if entity_id else []
        query_params.extend(await cls._get_acl_conditions())
        if hasattr(cls.Config, 'standard_query'):
            query_params.append(cls.Config.standard_query)
        if params.q:
            query_params.append(params.q)
        query_params.extend(await cls._build_search_conditions(params))
        query_params.extend(await cls._get_cleaned_clause_conditions())
        return query_params

    @classmethod
    async def _get_acl_conditions(cls):
        conditions = []
        if not (urdhva_base.ctx.exists() and urdhva_base.context.context.get('rpt', {})):
            return conditions
        rpt = urdhva_base.context.context['rpt']
        redis_client = await urdhva_base.redispool.get_redis_connection()
        key = f"access_restrictions_{urdhva_base.ctx['entity_id']}"
        if await redis_client.hexists(key, rpt['email']):
            data = json.loads(await redis_client.hget(key, rpt['email']))
            permitted_org = data.get("organizations_permitted", "").split(",")
            if len(permitted_org) == 1:
                permitted_org = f"('{permitted_org[0]}')"
            if cls.__tablename__ == "organization":
                conditions.append(f"id in {permitted_org}")
            else:
                conditions.append(f"organization_id in {permitted_org}")
        return conditions

    @classmethod
    async def _build_search_conditions(cls, params):
        if not params.search_text or not hasattr(cls.Config, 'search_fields'):
            return []
        search_text = params.search_text.strip()
        if not search_text:
            return []
        conditions = [f"{cls.__tablename__}.{field} ILIKE '%{search_text}%'" for field in cls.Config.search_fields]
        return [f"({' OR '.join(conditions)})"] if conditions else []

    @classmethod
    async def _get_cleaned_clause_conditions(cls):
        raw_conditions = await cls.get_clause_conditions()
        pattern = regex.compile(r"\s*bu\s*=\s*(?>'[^'\n]{1,100}')\s*")
        return [re.sub(pattern, '', cond).strip().rstrip("AND").rstrip("and") for cond in raw_conditions if
                cond.strip()]

    @staticmethod
    async def _add_sorting(query, params):
        try:
            order_by = json.loads(params.sort) if isinstance(params.sort, str) else params.sort
            if order_by:
                for key, value in order_by.items():
                    order = 'ASC' if 'asc' in value.lower() else 'DESC'
                    query.append(f"ORDER BY {key} {order}")
                    break
        except Exception as e:
            print(f"Exception in order by {e}")
            query.append("ORDER BY updated_at DESC")

    @staticmethod
    async def _add_pagination(query, params):
        if params.limit:
            query.append(f"LIMIT {params.limit}")
        if params.skip:
            query.append(f"OFFSET {params.skip * params.limit}")

    @classmethod
    async def _execute_query(cls, query, count_query, params, entity_id, resp_type):
        session = await manager.get_session()
        try:
            result = await session.scalars(select(cls.Config.schema_class).from_statement(text(" ".join(query))))
            rows = result.all()
            results = [{k: v for k, v in row.__dict__.items() if not k.startswith("_")} for row in rows]
            total = await cls.count(params, entity_id, count_query) if results else 0
            response = {"data": results, "count": len(results), "total": total}
            return JSONResponse(content=jsonable_encoder(response)) if resp_type == "encoded" else response
        except Exception as e:
            raise RuntimeError(f"Exception while running get_all query: {e}")
        finally:
            await asyncio.shield(session.close())

    @classmethod
    def convert_to_dict(cls, input_data):
        return {key: value for key, value in input_data.__dict__.items() if not key.startswith("_")}

    @classmethod
    async def delete(cls, row_id, entity_id=None):
        """

        :param row_id:
        :param entity_id:
        :return:
        """
        session = await manager.get_session()
        result = await session.execute(
            select(cls.Config.schema_class).where(cls.Config.schema_class.id == int(row_id))
        )

        if result.scalars().first() is not None:
            await session.execute(
                cls.Config.schema_class.__table__.delete().where(cls.Config.schema_class.id == int(row_id))
            )
            
            await session.commit()
            await asyncio.shield(session.close())
            return {"status": True, "message": "Deleted", "data": []}
        return {"status": False, "message": "Failed to delete.", "data": []}

    async def create(self, entity_id=None, upsert=False, upsert_skip_keys=[]):
        """

        :param entity_id:
        :param upsert:
        :return:
        """
        if not upsert_skip_keys:
            upsert_skip_keys = ["id", "entity_id", "created_at", "updated_at"]
        else:
            upsert_skip_keys = list(set(upsert_skip_keys + ["id", "entity_id", "created_at", "updated_at"]))

        await manager.create_all()
        session = await manager.get_session()
        try:
            if not upsert:
                schema_class = self.Config.schema_class(**{**json.loads(self.model_dump_json()), "entity_id": entity_id})
                session.add(schema_class)
                await session.commit()
                await session.refresh(schema_class)
                return {"id": schema_class.id, **{key: value for key, value in schema_class.__dict__.items() if not key.startswith("_")}}
            else:
                schema_dict = {**json.loads(self.model_dump_json()), "entity_id": entity_id}
                schema_class = self.Config.schema_class(**schema_dict)

                ins_resp = insert(self.Config.schema_class).values([schema_dict])

                conflict_dict = {
                    exc.key: exc for exc in ins_resp.excluded if exc.key not in upsert_skip_keys
                }

                ins_resp = ins_resp.on_conflict_do_update(
                    index_elements=self.Config.upsert_keys,
                    set_=conflict_dict
                ).returning(self.Config.schema_class.id)

                resp = await session.execute(ins_resp)
                await session.commit()
                row = resp.fetchone()
                if row:
                    result = await self.get(row[0])
                    return result.__dict__
                return None
        except Exception as e:
            print(f"Exception in {'create' if not upsert else 'upsert'} {e}")
            return None
        finally:
            await asyncio.shield(session.close())
        return None

    async def modify(self, entity_id=None):
        """

        :param entity_id:
        :return:
        """
        session = await manager.get_session()
        result = await session.execute(
            select(self.Config.schema_class).where(self.Config.schema_class.id == int(self.id))
        )
        record = result.one()
        if len(record):
            for key, value in self.model_dump(exclude_none=True, exclude_unset=True).items():
                if key == 'updated_at':
                    continue
                setattr(record[0], key, value)
            await session.commit()
            await asyncio.shield(session.close())
            return True, "updated"
        return False, "Record Not Found"

    @classmethod
    async def bulk_update(cls, records, entity_id=None, upsert=False, upsert_skip_keys = []):
        """

        :param records: list of records to insert as bulk into database
        :param entity_id:
        :param upsert:
        :return:
        """
        if not upsert_skip_keys:
            upsert_skip_keys = ["id", "entity_id", "created_at", "updated_at"]
        else:
            upsert_skip_keys = list(set(upsert_skip_keys + ["id", "entity_id", "created_at", "updated_at"]))

        await manager.create_all()
        session = await manager.get_session()
        try:
            if not upsert:
                tasks = [cls.Config.schema_class(**{**json.loads(json.dumps(rec,
                                                                            default=utils.datetime_serializer)),
                                                    "entity_id": entity_id}) for rec in records]
                session.add_all(tasks)
                await session.commit()  # Commit the transaction
                try:
                    await session.refresh(tasks[0])
                except Exception as e:
                    print(e)
                await session.close()
            else:
                # Calculating max records to send for upsert operation by considering max columns limit 32767
                max_limit = int(32767 / (len(records[0]) + 1)) - 1
                for index in range(0, len(records), max_limit):
                    ins_resp = insert(cls.Config.schema_class).values([{**rec, "entity_id": entity_id}
                                                                       for rec in records[index:index+max_limit]])
                    conflict_dict = {exc.key: exc for exc in ins_resp.excluded if exc.key not in upsert_skip_keys}
                    ins_resp = ins_resp.on_conflict_do_update(
                        index_elements=cls.Config.upsert_keys, set_=conflict_dict
                    )
                    await session.execute(ins_resp)
                    await session.commit()  # Commit the transaction
                    try:
                        schema_class = cls.Config.schema_class(**{**records[0],
                                                                  "entity_id": entity_id})
                        await session.refresh(schema_class)
                    except Exception as e:
                        print(e)
                    await session.close()
        except Exception as e:
            print(f"Exception in bulk update {e}")
            print(f"Traceback {traceback.format_exc()}")
        finally:
            try:
                await session.commit()  # Commit the transaction
            except Exception as e:
                print(e)
            try:
                await asyncio.shield(session.close())
            except Exception as e:
                print(e)
        return True, "Data inserted"

    class Config:
        populate_by_name = True
        json_encoders = {
        }
        from_attributes = True
        collection_name: urdhva_base.settings.default_index
        schema_class: Base
        search_fields: []
        upsert_keys: []


# Define concrete model
class PostgresModel(BasePostgresModel):
    id: typing.Optional[int]
    created_at: typing.Optional[datetime.datetime] | None = None
    updated_at: typing.Optional[datetime.datetime] | None = None
    entity_id: typing.Optional[str] | None = None
