# Deployment Diagram

```mermaid
graph TD;
  classDef prod fill:#30803075;
  classDef test fill:#30303075;
  classDef cloudflare fill:#30308075;
  classDef firewall fill:#cc700075;

  subgraph "GithubPages"
    Frontend[Frontend]
  end

  subgraph Firewall[Amazon Firewall]
    subgraph Amazon[Amazon EC2 Free Instance]

      subgraph Prod["Prod container"]
          ProdApp[Chat App]
      end
      class Prod prod

      subgraph Test["Test container"]
          TestApp[Chat App]
      end
      class Test test

      Traefik[Traefik] --> Prod
      Traefik --> Test

      ProdApp-->ProdDB[(sqlite)]
      TestApp-->TestDB[(sqlite)]

      %%Prod --> Test
    end
  end

  Frontend -->|HTTPS / WebSocket| Cloudflare[[Cloudflare Proxy / WAF]]

  Traefik -->|ACME| LetsEncrypt
  Cloudflare --> Traefik

  %%Hacker --> Firewall

  class Cloudflare cloudflare
  class Firewall firewall
```

-   Github Pages: https://pages.github.com/
-   WAF: https://developers.cloudflare.com/waf/
-   AWS Free Tier: https://aws.amazon.com/free/
-   Traefik & Let’s Encrypt: https://doc.traefik.io/traefik/https/acme/
-   Docker: https://docs.docker.com/get-started/overview/
