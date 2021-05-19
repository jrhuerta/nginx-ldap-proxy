#!/bin/bash
if [ -z ${LDAP_PROXY_URI+x} ]
then
  echo "LDAP_PROXY_URI env var required."; exit;
fi;

if [ -z ${LDAP_PROXY_USERDN_TMPL+x} ]
then
  echo "LDAP_PROXY_USERDN_TMPL env var required."; exit;
fi;

envsubst '${LDAP_PROXY_URI} ${LDAP_PROXY_USERDN_TMPL}' \
  < /etc/nginx/auth.tmpl \
  > /etc/nginx/auth.conf

for f in /etc/nginx/conf.d/*.tmpl; do
  envsubst "`printf '${%s} ' $(bash -c "compgen -A variable | grep -i ldap_proxy")`" \
    < "${f}" \
    > "${f%.*}.conf"
done;

exec "$@"