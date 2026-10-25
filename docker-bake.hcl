# De vier images in één keer bouwen (docker buildx bake). De gedeelde stappen (installeren, bouwen van de
# monorepo) draaien één keer; daarna de vier eindimages naast elkaar. Gebruikt door .github/workflows/deploy.yml.
variable "REGISTRY" { default = "kleurhoek" }
variable "TAG" { default = "" }
variable "MARKETS" { default = "nl-nl" }

group "default" {
  targets = ["app"]
}

target "app" {
  name      = app
  matrix    = { app = ["api", "web", "admin", "login"] }
  context   = "."
  target    = app
  platforms = ["linux/amd64"]
  args      = { NEXT_PUBLIC_MARKETS = MARKETS, BUILD_SHA = TAG }
  # :<commit> rolt uit. :latest (wat Terraform gebruikt bij het (her)aanmaken van een container) zet de
  # deploy pas na een geslaagde test, zodat :latest altijd de laatste goede versie is om naar terug te gaan.
  tags       = TAG == "" ? ["${REGISTRY}/kleurhoek-${app}:latest"] : ["${REGISTRY}/kleurhoek-${app}:${TAG}"]
  cache-from = ["type=gha,scope=${app}"]
  cache-to   = ["type=gha,scope=${app},mode=max"]
}
