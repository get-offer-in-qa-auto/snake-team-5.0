#!/bin/sh
set -eu

readonly jdbc_version="42.7.13"
readonly jdbc_sha256="6e0e4cc2d8cae902084f8a2b18728b073a6fd9d1f87c9d8bff8f298c18185b93"
readonly data_dir="/data/teamcity_server/datadir"
readonly jdbc_dir="${data_dir}/lib/jdbc"
readonly config_dir="${data_dir}/config"
readonly jdbc_file="${jdbc_dir}/postgresql-${jdbc_version}.jar"
readonly jdbc_temp="${jdbc_file}.tmp"

mkdir -p "${jdbc_dir}" "${config_dir}"

if [ ! -f "${jdbc_file}" ]; then
  curl \
    --fail \
    --location \
    --retry 3 \
    --silent \
    --show-error \
    "https://jdbc.postgresql.org/download/postgresql-${jdbc_version}.jar" \
    --output "${jdbc_temp}"
  echo "${jdbc_sha256}  ${jdbc_temp}" | sha256sum -c -
  mv "${jdbc_temp}" "${jdbc_file}"
fi

chmod 0644 "${jdbc_file}"

cat > "${config_dir}/database.properties" <<'EOF'
connectionUrl=jdbc:postgresql://teamcity-postgres:5432/teamcity
connectionProperties.user=teamcity
connectionProperties.password=overridden-by-TEAMCITY_DB_PASSWORD
maxConnections=50
testOnBorrow=false
EOF

chmod 0644 "${config_dir}/database.properties"
chown -R 1000:1000 "${data_dir}"
