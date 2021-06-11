# NGINX ldap authentication proxy

Simple NGINX proxy to leverage LDAP authentication with user credentials binding 
through HTTP Basic Authentication.

## Usage:

Required environment variables:

* **LDAP_PROXY_URI**: URI for the ldap endpoint to use for the bind.
* **LDAP_PROXY_USERDN_TMPL**: Template to use for the user dn. The username provided 
  through basic auth is interpolated with the keyword `{user}`
* **LDAP_PROXY_UPSTREAM**: URI for the [default](/etc/nginx/conf.d/default.conf) proxy pass configuration

Example configuration values for usage with JumpCloud:

```
LDAP_PROXY_URI=ldaps://ldap.jumpcloud.com
LDAP_PROXY_USERDN_TMPL="uid={user},ou=Users,o=1bd358766be23330473e9d5124389083,dc=jumpcloud,dc=com"
LDAP_PROXY_UPSTREAM=http://www.google.com
```

## with Docker

```bash
docker run \
    -e LDAP_PROXY_URI=ldaps://ldap.jumpcloud.com \
    -e LDAP_PROXY_USERDN_TMPL="uid={user},ou=Users,o=1bd358766be23330473e9d5124389083,dc=jumpcloud,dc=com" \
    -e LDAP_PROXY_UPSTREAM="http://www.google.com" \
    -p 8080:80 \
    jrhuerta/nginx-ldap-proxy
```

## NGINX default configuration

[/etc/nginx/conf.d/default.tmpl](/etc/nginx/conf.d/default.tmpl)


## NGINX custom configuration

NGINX will load all `.conf` configuration files mounted in:
```
/etc/nginx/conf.d/
```

## Templates and environment variable interpolation

On startup any `.tmpl` files mounted in `/etc/nginx/conf.d/` will be interpolated 
using `envsubts` with only environment variables defined with the prefix `LDAP_PROXY` 
available. The resulting file will have the same file name as the template but with a 
`.conf` extension and will be loaded by NGINX on startup.

Example:

Template file:
`/etc/nginx/conf.d/default.tmpl`
```
server {
    listen *:80;
    server_name default;

    include /etc/nginx/auth.conf;

    location / {
        auth_request        /auth;
        proxy_pass          ${LDAP_PROXY_UPSTREAM};
    }
}
```

Docker command:
```bash
docker run --rm -ti \
    -e LDAP_PROXY_URI="<your_value>" \
    -e LDAP_PROXY_USERDN_TMPL="<your_value>" \
    -e LDAP_PROXY_UPSTREAM="<secure_content_uri>"
```

Generated on startup:
`/etc/nginx/conf.d/private_site.conf`
```
server {
    listen *:80;
    server_name default;

    include /etc/nginx/auth.conf;

    location / {
        auth_request        /auth;
        proxy_pass          http://upstream.local;
        proxy_set_header    Authorization "Bearer secret";
    }
}
```

## Kubernetes

* `.conf` and `.tmpl` files can be mounted as ConfigMaps
* secrets can be interpolated from environment variables.

