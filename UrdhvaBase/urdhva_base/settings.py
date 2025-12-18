import os
import sys
import enum
import json
import typing
import pydantic
import pydantic_settings

EnvConfigFile = ".alg_env"
Db_Urls_Base = {
        "mongo": [
        ],
        "elastic": [
        ],
        "postgres_async": [
        ],
        "mysql_async": [
        ],
        "redis": [
        ],
        "tibco": [
        ]
    }


class MultiTenancyMode(str, enum.Enum):
    SingleServerSingleDb = 'SingleServerSingleDb'
    SingleServerMultiDb = 'SingleServerMultiDb'
    MultiServerSingleDb = 'MultiServerSingleDb'
    MultiServerMultiDb = 'MultiServerMultiDb'


def configure_db_urls(db_urls):
    if not db_urls:
        db_urls = {}

    # Handling environmental variables like exposed from docker and kubernetes container
    for key, value in {"DB_URLS_POSTGRES_ASYNC": "postgres_async",
                       "DB_URLS_MYSQL_ASYNC": "mysql_async",
                       "DB_URLS_REDIS": "redis"}.items():
        if os.environ.get(key, None):
            db_urls[value] = os.environ[key].split(",")
    for key, value in Db_Urls_Base.items():
        if key not in db_urls:
            db_urls[key] = [pydantic.AnyUrl(url) for url in value]
    return db_urls


class Settings(pydantic_settings.BaseSettings):
    model_config = pydantic_settings.SettingsConfigDict(env_file=EnvConfigFile, extra='ignore')
    # Domain defaults
    app_name: str = "algo_fusion"
    entity_id: str = "algo_fusion"
    cookie_name: str = "algo_fusion"
    default_index: str = "algo_fusion"
    multi_tenant_support: bool = True
    password_salt: str = "algo_fusion_secret"
    max_redis_connections: int = 10
    origin_check_enabled: bool = False
    disable_api_extra_inputs: bool = False
    environment: str = ""
    api_prefix: str = "/api"
    docs_path: str = "/"

    # JWT
    jwt_secret_key: str = "12a34bc8d98e8f8g7h78i12j23k2l34m4n5o34p23q12r54s38tu9v2w12x7y2z3"
    jwt_algorithm: str = "HS256"

    # Header based authentication Enabled or Not
    enable_header_auth: bool = False

    # Keycloak Auth Server
    keycloak_external_url: pydantic.AnyHttpUrl = 'https://localhost:8443'
    keycloak_auth_default: str = "auth"
    keycloak_internal_url: pydantic.AnyHttpUrl = 'https://localhost:8443'
    keycloak_admin: str = 'admin'
    keycloak_password: str = 'password'
    keycloak_db_password: str = 'admin'
    fernet_key: str = 'NjY5N2IwOWM5ZjE0MjMzN2M3YzA5Y2Y4ZDE4NTA2Mjk='
    default_realm: str = 'algo_fusion'
    server_host: str = "localhost"
    keycloak_verify_ssl: bool = False

    # For RBAC
    roles_directories: typing.List[str] = []
    rbac_keys: typing.List[str] = ['sap_id', 'bu', 'state', 'city', 'district', 'zone']

    # For Logger
    log_base_dir: str = "/var/log/ceg_logs"
    log_max_size: int = 10000000
    log_max_count: int = 5

    # DB Multi-tenancy model
    db_multi_tenancy_model: MultiTenancyMode = MultiTenancyMode.SingleServerSingleDb
    login_count: int = 5
    base_path: str = "/opt/pipeline/algo"
    output_path: str = "/opt/pipeline/algo/orchestrator/pipeline/resources"
    module_base: str = "orchestrator"
    template_base: str = "/opt/pipeline/algo/orchestrator/flow_templates"
    results_path: str = "/opt/pipeline/algo/orchestrator/pipeline/resources"
    mft_path: str = "/opt/pipeline/mft_path/"
    ui_path: str = ""
    # settings.py
    ticketing_attachments: str = "C:/Users/Rakesh/OneDrive/Desktop/Ticketing_project/files"
    # ticketing_attachments: str = ""
    download_path: str = "/opt/pipeline/algo/orchestrator/masters"
    template_path: str = "/opt/pipeline/algo/orchestrator/notification_templates"
    engine_scripts_path: str = "/opt/pipeline/algo/orchestrator/pipeline"
    uploads: str = "/opt/pipeline/algo/orchestrator/pipeline/resources/upload_path"
    master_data_template_path: str = "/opt/pipeline/algo/utilities/master_data_template.xlsx"
    kibana_dashboard_header: str = 'osd-xsrf'
    default_creds: str = "secret"
    db_urls: typing.Dict[str, typing.List[pydantic.AnyUrl]] = Db_Urls_Base

    # Postgresql settings
    enable_echo: bool = True

    #---------------------------------
    #for minio
    minio_base_path: str = ""
    minio_endpoint: str = ""
    minio_access_key_id: str = ""
    minio_secret_access_key: str = ""
    #for spark
    spark_base_path: str = ""
    #for iceberg catalog
    catalog_db: str = ""
    catalog_user: str = ""
    catalog_password: str  = ""
    catalog_db_uri: str =""
    #---------------------------------
    
    # Session configuration settings
    session_same_site: str = 'Strict'
    session_secure: bool = True
    session_httponly: bool = True

    # This will give whether external authentication was enabled or not, If enabled will skip auth validation
    external_authentication: bool = False

    # Master cache time
    cache_gateway_port: int = 5920
    cache_gateway_host: str = "localhost"
    default_masters_cache_seconds: int = 15*60

    # For importing Urdhva framework packages
    import_paths: typing.Dict[str, str] = {}

    # No Auth Urls
    noauth_urls: typing.List[str] = []

    # Kafka
    kafka_enabled: bool = False
    kafka_bootstrap_servers: str = 'localhost:9092'

    # Superset
    superset_internal_url: str = 'http://localhost:8088'
    superset_external_url: str = 'http://localhost:8088'
    superset_user: str = ""
    superset_password: str = ''

    # SMTP
    smtp_host: str = ""
    smtp_port: int = 25
    smtp_from_url: str = ""
    smtp_reply_from: str = ""
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_tls_enabled: bool = False
    smtp_ssl_enabled: bool = False

    # Whatsapp
    whatsapp_creds: typing.Dict[str, str] = {}

    # SMS
    sms_creds: typing.Dict[str, str] = {}

    # LDAP Settings
    ldap_host: str = ""
    ldap_port: str = ""
    ldap_domain: str = ""
    ldap_auth_enabled: bool = False

    # camunda
    # Default Camunda
    camunda_url: str = ''
    open_ldap_url: str = ''
    cris_interlock_disable_url: str = ''
    camunda_default_config: typing.Dict[str, int] = {
        "maxTasks": 10,
        "lockDuration": 10000,
        "asyncResponseTimeout": 5000,
        "retries": 5,
        "retryTimeout": 5000,
        "sleepSeconds": 30
    }
    camunda_url_config: typing.Dict[str, typing.Dict] = {}
    camunda_url_va_config: typing.Dict[str, typing.Dict] = {}

    # For camunda configuration for non default one
    # Creating separate configuration for each bu and keep applicable rules for those
    # Sample {"TAS": [{"alert_section": "", "url": "", "sap_id": [],
    # "zone": [], "sales_area": [], "region": [], "rule": "odd/even"}]}
    camunda_configuration: typing.Dict[str, typing.List] = {}

    # For DB Connection Mapping
    db_connection_config: typing.Dict[str, str] = {}
    db_connection_mapping: typing.Dict[str, typing.Dict] = {}

    # RabbitMQ
    rabbitmq_enabled: bool = False
    rabbitmq_host: str = "localhost"
    rabbitmq_port: int = 5672
    rabbitmq_username: str = ""
    rabbitmq_password: str = ""
    rabbitmq_vhost: str = ""
    rabbitmq_queue: str = ""
    rabbitmq_auto_ack: bool = True
    pyrfc_docker: str = ""
    pyrfc_python: str = ""

    # openai api key
    openai_api_key: str = ""
    
    # ThingsBoard
    things_board_url: str = "http://localhost:8080"
    things_board_username: str = ""
    things_board_password: str = ""

    # Max user password retries
    max_password_retires: int = 3
    lockout_time: int = 60

    # Timezone settings
    time_zone: str = "Asia/Kolkata"

    def db_url(self, db):
        if self.db_multi_tenancy_model == MultiTenancyMode.SingleServerSingleDb or \
                self.db_multi_tenancy_model == MultiTenancyMode.SingleServerMultiDb:
            return self.db_urls.get(db, [])[0]

    class ConfigDict:
        env_file = EnvConfigFile
        case_sensitive = False


settings = Settings()

# Loading provided paths
if len(settings.import_paths) > 0:
    for _, path in settings.import_paths.items():
        if os.path.exists(path) and os.path.isdir(path):
            sys.path.append(path)

configure_db_urls(settings.db_urls)
