# Snippets for Chapter 11

## <em>Quick links to the recipes</em>
* [Granting additional privileges ](#granting-additional-privileges)
* [Managing access with API key ](#managing-access-with-api-key)
* [Configuring Single Sign-On ](#configuring-single-sign-on)


## Granting additional privileges

### Dev tools command to return Kubernetes logs
```
GET /logs-*/_search 
{ 
  "query": { 
    "bool": { 
      "must": { 
        "exists": { 
          "field": "kubernetes.namespace"
        } 
      } 
    } 
  } 
} 
```

### Granted read privileges to specific documents
```json
{
    "bool": {
        "must": {
          "exists": {
            "field": "kubernetes.namespace"
          }
        }
    }
}
```

## Managing access with API key
### Dev Tools command to create API key
```
POST /_security/api_key 
{ 
  "name": "rennes_traffic_writer_key",  
  "role_descriptors": { 
    "rennes_traffic_writer": {  
      "cluster": ["monitor", "read_ilm"], 
      "index": [ 
        { 
          "names": ["metric-rennes_traffic-*"], 
          "privileges": ["view_index_metadata", "create_doc"] 
        } 
      ] 
    } 
  } 
} 
```

Restart Logstash service
```console
sudo systemctl stop logstash.service 
```
```console
sudo systemctl start logstash.service 
```

## Configuring Single Sign-On

### Elasticsearch user setting for oidc
```yaml
xpack.security.authc.realms.oidc:  
    oidc-okta:  
        order: 3  
        rp.client_id: <CLIENT_ID>  
        rp.response_type: code  
        rp.redirect_uri: "<KIBANA_URL>/api/security/oidc/callback"
        op.issuer: "https://dev-<ACCOUNT_ID>.okta.com"
        op.authorization_endpoint: "https://dev-<ACCOUNT_ID>.okta.com/oauth2/v1/authorize"
        op.token_endpoint: "https://dev-<ACCOUNT_ID>.okta.com/oauth2/v1/token"
        op.jwkset_path: "https://dev-<ACCOUNT_ID>.okta.com/oauth2/v1/keys"
        op.userinfo_endpoint: "https://dev-<ACCOUNT_ID>.okta.com/oauth2/v1/userinfo"
        rp.post_logout_redirect_uri: "<KIBANA_URL>/security/logged_out"
        rp.requested_scopes: ["openid", "groups", "profile", "email"]
        claims.principal: email
        claims.name: name 
        claims.mail: email
        claims.groups: groups
```

### Kibana user settings for oidc provider
```yaml
xpack.security.authc.providers:  
   oidc:  
       oidc1:   
           order: 2  
           realm: oidc-okta  
           description: SSO with Okta via OIDC  
   basic:  
       basic1:  
           order: 3 
```

### Kibana user settings for oidc provider with icon and hint
```yaml
xpack.security.authc.providers:
    oidc: 
        oidc1:  
            order: 2 
            realm: oidc-okta 
            description: SSO with Okta via OIDC 
            hint: "For business and observability users" 
            icon: "logoKibana" 
    basic: 
        basic1: 
            order: 3 
```

